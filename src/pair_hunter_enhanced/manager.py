"""
🎯 Pair Hunter Manager - Main interface
"""
import os
import logging
from typing import List, Optional, Dict
from .scanner import BinanceScanner
from .filters import PairFilter, FilterConfig
from .scorer import ScalpingScorer, ScoredPair
from .cache import PairCache

logger = logging.getLogger(__name__)

class PairHunterManager:
    """
    Main manager - hunts top pairs every 15 minutes
    Falls back to ASSETS if Binance API fails
    """
    
    def __init__(self, 
                 top_n: int = 7,
                 min_volume_usd: float = 10_000_000,
                 max_spread_pct: float = 0.3,
                 cache_ttl_minutes: int = 15,
                 fallback_pairs: Optional[List[str]] = None):
        
        self.top_n = top_n
        
        # Use ASSETS from env if no fallback provided
        if fallback_pairs is None:
            assets_str = os.getenv('ASSETS', 'BTC ETH SOL BNB ZEC')
            fallback_pairs = [f"{a.strip()}USDT" for a in assets_str.split() if a.strip()]
        
        self.fallback_pairs = fallback_pairs
        
        self.scanner = BinanceScanner()
        self.filter = PairFilter(FilterConfig(
            min_volume_24h_usd=min_volume_usd,
            max_spread_pct=max_spread_pct
        ))
        self.scorer = ScalpingScorer()
        self.cache = PairCache(ttl_seconds=cache_ttl_minutes * 60)
        
        logger.info(f"Pair Hunter initialized (top_n={top_n})")
    
    def get_top_pairs(self, force_refresh: bool = False, with_scores: bool = False) -> List[str]:
        """Get top N pairs for scalping"""
        
        # Check cache first
        if not force_refresh and self.cache.is_valid():
            cached = self.cache.get()
            if cached:
                symbols = [p['symbol'] for p in cached]
                logger.info(f"Using cached pairs: {symbols}")
                return symbols
        
        # Fetch fresh data
        try:
            logger.info("🔍 Hunting for best scalping pairs...")
            
            all_symbols = self.scanner.get_all_symbols()
            if not all_symbols:
                raise Exception("Failed to fetch symbols")
            
            market_data = self.scanner.get_24h_ticker_data(all_symbols)
            if not market_data:
                raise Exception("Failed to fetch market data")
            
            filtered = self.filter.apply_all_filters(market_data)
            
            atr_data = self._get_atr_for_pairs(filtered)
            scored = self.scorer.score_pairs(filtered, atr_data)
            top_pairs = self.scorer.get_top_pairs(scored, n=self.top_n, min_score=0.25)
            
            if not top_pairs:
                logger.error("No pairs met threshold, using fallback")
                return self._get_fallback()
            
            # Cache results
            cache_data = [{'symbol': p.symbol, 'score': p.scalping_score} for p in top_pairs]
            self.cache.set(cache_data)
            
            symbols = [p.symbol for p in top_pairs]
            logger.info(f"🎯 Top {len(symbols)} pairs: {symbols}")
            
            return symbols
            
        except Exception as e:
            logger.error(f"Pair Hunter failed: {e}")
            return self._get_fallback()
    
    def _get_atr_for_pairs(self, market_data: Dict) -> Dict[str, float]:
        """Calculate ATR for top 50 by volume"""
        sorted_pairs = sorted(
            market_data.items(),
            key=lambda x: x[1].volume_24h_usd,
            reverse=True
        )[:50]
        
        atr_data = {}
        for symbol, _ in sorted_pairs:
            try:
                df = self.scanner.get_klines_for_atr(symbol, period="1h", limit=24)
                if not df.empty:
                    atr_pct = self.scanner.calculate_atr(df)
                    atr_data[symbol] = atr_pct
            except Exception:
                atr_data[symbol] = 0
        
        return atr_data
    
    def _get_fallback(self):
        """Return fallback pairs"""
        logger.info(f"Using fallback pairs: {self.fallback_pairs}")
        return self.fallback_pairs.copy()
    
    def clear_cache(self):
        self.cache.clear()
