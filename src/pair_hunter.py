"""
🎯 Pair Hunter - Dynamically discovers best trading pairs for scalping
Enhanced version with sophisticated scoring and Binance integration
Falls back to ASSETS if hunting fails
"""

import asyncio
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

# Import the sophisticated scanner/scorer if available
try:
    from src.pair_hunter_enhanced.scanner import BinanceScanner
    from src.pair_hunter_enhanced.scorer import ScalpingScorer
    ENHANCED_AVAILABLE = True
except ImportError:
    try:
        from pair_hunter_enhanced.scanner import BinanceScanner
        from pair_hunter_enhanced.scorer import ScalpingScorer
        ENHANCED_AVAILABLE = True
    except ImportError:
        ENHANCED_AVAILABLE = False
        logger.warning("Enhanced Pair Hunter not available, using basic implementation")

# Fallbacks only — the live values come from CONFIG so they stay tunable without a redeploy.
DEFAULT_BLACKLIST = "SHIB PEPE FLOKI BONK WIF MEME DOGE 1000SATS LUNA FTT"
MIN_VOLUME_24H = 10_000_000  # $10M daily volume
MIN_PRICE = 0.01  # Avoid sub-penny coins
MAX_SPREAD_PCT = 0.5  # Max 0.5% bid-ask spread


def get_blacklist() -> set:
    """Assets never to trade, from PAIR_HUNTER_BLACKLIST (space or comma separated)."""
    from src.config_loader import CONFIG

    raw = CONFIG.get("pair_hunter_blacklist") or DEFAULT_BLACKLIST
    return {token.strip().upper() for token in str(raw).replace(",", " ").split() if token.strip()}


class PairHunter:
    """Discovers optimal trading pairs based on volatility and setup quality"""
    
    def __init__(self, exchange_client=None, top_n: int = 7):
        self.exchange = exchange_client
        self.top_n = top_n
        self._last_hunt_time = None
        self._cached_pairs = []
        
        # Try to use enhanced scanner if no exchange client provided
        if not exchange_client and ENHANCED_AVAILABLE:
            self._scanner = BinanceScanner()
            self._scorer = ScalpingScorer()
            self._use_enhanced = True
            logger.info(f"Pair Hunter initialized with ENHANCED mode (top_n={top_n})")
        else:
            self._use_enhanced = False
            logger.info(f"Pair Hunter initialized with BASIC mode (top_n={top_n})")
    
    async def hunt_pairs(self, min_volatility: float = None, timeframe: str = None) -> List[str]:
        """
        Hunt for best trading pairs
        
        Args:
            min_volatility: Minimum ATR% (too quiet = skip)
            timeframe: Analysis timeframe
            
        Returns:
            List of asset symbols (e.g., ['BTC', 'ETH', 'SOL'])
        """
        from src.config_loader import CONFIG

        if min_volatility is None:
            min_volatility = float(CONFIG.get("pair_hunter_min_volatility", 1.0) or 1.0)
        if timeframe is None:
            timeframe = str(CONFIG.get("pair_hunter_timeframe", "15m") or "15m")

        # Check if we should use enhanced version
        if self._use_enhanced and not self.exchange:
            return await self._hunt_enhanced()
        
        # Use basic implementation with exchange client
        return await self._hunt_basic(min_volatility, timeframe)
    
    async def _hunt_enhanced(self) -> List[str]:
        """Use enhanced Binance-based hunting, then keep only venue-tradable symbols."""
        try:
            logger.info(f"🔍 PAIR HUNTER (ENHANCED): Scanning for top {self.top_n} opportunities...")
            
            # Import here to avoid circular imports
            try:
                from src.pair_hunter_enhanced.manager import PairHunterManager
            except ImportError:
                from pair_hunter_enhanced.manager import PairHunterManager
            
            # Over-fetch from Binance — many hot names are not listed on OKX.
            overfetch_n = max(self.top_n * 5, self.top_n + 20)
            hunter = PairHunterManager(
                top_n=overfetch_n,
                fallback_pairs=[]
            )
            
            # Get top pairs
            pairs = hunter.get_top_pairs(force_refresh=True)
            if not pairs:
                logger.warning("Enhanced Pair Hunter found no pairs (empty fallback by design)")
                return []
            
            # Convert from BTCUSDT to BTC format
            assets = [p.replace('USDT', '') for p in pairs]
            assets = filter_assets_to_trading_venue(assets, limit=self.top_n)
            
            logger.info(f"🏆 ENHANCED PAIR HUNTER discovered (venue-filtered): {assets}")
            self._cached_pairs = assets
            self._last_hunt_time = datetime.now()
            
            return assets
            
        except Exception as e:
            logger.error(f"Enhanced hunting failed: {e}, not using hardcoded fallback")
            return []
    
    async def _hunt_basic(self, min_volatility: float, timeframe: str) -> List[str]:
        """Original basic implementation"""
        logger.info(f"🔍 PAIR HUNTER (BASIC): Scanning for top {self.top_n} opportunities...")
        
        try:
            # Step 1: Get all futures pairs with volume
            all_pairs = await self._get_futures_pairs()
            logger.info(f"Found {len(all_pairs)} total futures pairs")
            
            # Step 2: Filter by basic criteria
            qualified = await self._filter_basic_criteria(all_pairs)
            logger.info(f"{len(qualified)} pairs passed basic filters")
            
            # Step 3: Calculate volatility and trend strength
            scored = await self._score_pairs(qualified, timeframe)
            
            # Step 4: Sort by score and return top N
            top_pairs = sorted(scored, key=lambda x: x['score'], reverse=True)[:self.top_n]
            
            assets = [p['asset'] for p in top_pairs]
            
            # Log results
            logger.info("🏆 TOP PAIRS DISCOVERED:")
            for i, p in enumerate(top_pairs, 1):
                logger.info(f"  {i}. {p['asset']}: Score {p['score']:.1f} | "
                           f"Vol: {p['volatility']:.1f}% | "
                           f"Trend: {p['trend_strength']:.1f}")
            
            self._cached_pairs = assets
            self._last_hunt_time = datetime.now()
            
            return assets
            
        except Exception as e:
            logger.error(f"Pair hunting failed: {e}, falling back to ASSETS")
            return self._get_assets_fallback()
    
    def _get_assets_fallback(self) -> List[str]:
        """Get ASSETS from environment as fallback"""
        from src.config_loader import CONFIG

        assets_str = CONFIG.get('assets') or os.getenv('ASSETS', '')
        assets = [a.strip() for a in str(assets_str).replace(',', ' ').split() if a.strip()]
        logger.info(f"Using ASSETS fallback: {assets}")
        return assets
    
    async def _get_futures_pairs(self) -> List[Dict]:
        """Get all USDT perpetual futures with 24h volume"""
        try:
            exchange_info = await self.exchange.get_exchange_info()
            tickers = await self.exchange.get_24h_tickers()
            
            # Create volume lookup
            volume_map = {t['symbol']: float(t.get('volume', 0)) * float(t.get('weightedAvgPrice', 0)) 
                         for t in tickers}
            
            blacklist = get_blacklist()
            pairs = []
            for symbol_info in exchange_info.get('symbols', []):
                symbol = symbol_info['symbol']
                
                # Only USDT perpetual futures
                if not symbol.endswith('USDT'):
                    continue
                    
                asset = symbol.replace('USDT', '')
                
                # Skip blacklisted
                if asset in blacklist:
                    continue
                
                volume = volume_map.get(symbol, 0)
                
                pairs.append({
                    'asset': asset,
                    'symbol': symbol,
                    'volume_24h': volume,
                    'price': float(tickers.get(symbol, {}).get('lastPrice', 0))
                })
            
            return pairs
            
        except Exception as e:
            logger.error(f"Failed to get futures pairs: {e}")
            return []
    
    async def _filter_basic_criteria(self, pairs: List[Dict]) -> List[Dict]:
        """Filter by volume, price, blacklist"""
        from src.config_loader import CONFIG

        qualified = []
        min_volume = float(CONFIG.get("pair_hunter_min_volume_24h", MIN_VOLUME_24H) or MIN_VOLUME_24H)
        min_price = float(CONFIG.get("pair_hunter_min_price", MIN_PRICE) or MIN_PRICE)

        for pair in pairs:
            # Volume check — thin books cost more in spread than the edge is worth
            if pair['volume_24h'] < min_volume:
                continue
            
            # Price check (avoid sub-penny)
            if pair['price'] < min_price:
                continue
            
            qualified.append(pair)
        
        return qualified
    
    async def _score_pairs(self, pairs: List[Dict], timeframe: str) -> List[Dict]:
        """Score pairs preferring medium volatility (tradable, not whip-saw)."""
        from src.config_loader import CONFIG

        scored = []
        min_vol = float(CONFIG.get("pair_hunter_min_volatility", 1.5) or 1.5)
        max_vol = float(CONFIG.get("pair_hunter_max_volatility", 6.0) or 6.0)
        ideal_vol = float(CONFIG.get("pair_hunter_ideal_volatility", 3.0) or 3.0)
        min_trend = float(CONFIG.get("pair_hunter_min_trend_strength", 25.0) or 25.0)
        w_vol = float(CONFIG.get("pair_hunter_weight_volatility", 0.25) or 0.25)
        w_trend = float(CONFIG.get("pair_hunter_weight_trend", 0.40) or 0.40)
        w_setup = float(CONFIG.get("pair_hunter_weight_setup", 0.35) or 0.35)
        
        for pair in pairs:
            try:
                # Get OHLCV data
                ohlcv = await self.exchange.get_klines(
                    symbol=pair['symbol'],
                    interval=timeframe,
                    limit=50
                )
                
                if len(ohlcv) < 20:
                    continue
                
                # Calculate metrics
                volatility = self._calculate_volatility(ohlcv)
                if volatility < min_vol or volatility > max_vol:
                    logger.debug(
                        f"Skip {pair.get('asset')}: vol={volatility:.2f}% "
                        f"outside [{min_vol}, {max_vol}]"
                    )
                    continue

                trend_strength = self._calculate_trend(ohlcv)
                if trend_strength < min_trend:
                    logger.debug(
                        f"Skip {pair.get('asset')}: trend={trend_strength:.1f} below {min_trend} (chop)"
                    )
                    continue

                setup_quality = self._evaluate_setup(ohlcv)
                # Sweet-spot vol: peak at ideal_vol, fade toward min/max (0-100 scale)
                span = max(ideal_vol - min_vol, max_vol - ideal_vol, 0.5)
                vol_score = max(0.0, 100.0 * (1.0 - abs(volatility - ideal_vol) / span))
                
                # Prefer trend + setup over raw heat
                score = (
                    vol_score * w_vol +
                    trend_strength * w_trend +
                    setup_quality * w_setup
                )
                
                scored.append({
                    'asset': pair['asset'],
                    'symbol': pair['symbol'],
                    'score': score,
                    'volatility': volatility,
                    'trend_strength': trend_strength,
                    'setup_quality': setup_quality,
                    'volume': pair['volume_24h']
                })
                
            except Exception as e:
                logger.debug(f"Failed to score {pair['symbol']}: {e}")
                continue
        
        return scored
    
    def _calculate_volatility(self, ohlcv: List) -> float:
        """Calculate recent volatility (ATR-based)"""
        if len(ohlcv) < 14:
            return 0
        
        # Calculate ATR
        atr_sum = 0
        for i in range(1, min(15, len(ohlcv))):
            high = float(ohlcv[i][2])
            low = float(ohlcv[i][3])
            prev_close = float(ohlcv[i-1][4])
            
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            atr_sum += max(tr1, tr2, tr3)
        
        atr = atr_sum / 14
        current_price = float(ohlcv[-1][4])
        
        # Return as percentage
        return (atr / current_price) * 100 if current_price > 0 else 0
    
    def _calculate_trend(self, ohlcv: List) -> float:
        """Calculate trend strength (ADX-like)"""
        if len(ohlcv) < 20:
            return 0
        
        closes = [float(c[4]) for c in ohlcv[-20:]]
        
        # Simple directional movement
        up_moves = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i-1])
        down_moves = sum(1 for i in range(1, len(closes)) if closes[i] < closes[i-1])
        
        total_moves = up_moves + down_moves
        if total_moves == 0:
            return 0
        
        # Trend strength (0-100)
        return (abs(up_moves - down_moves) / total_moves) * 100
    
    def _evaluate_setup(self, ohlcv: List) -> float:
        """Evaluate current setup quality"""
        if len(ohlcv) < 10:
            return 0
        
        # Get recent candles
        recent = ohlcv[-10:]
        highs = [float(c[2]) for c in recent]
        lows = [float(c[3]) for c in recent]
        closes = [float(c[4]) for c in recent]
        volumes = [float(c[5]) for c in recent]
        
        # Check for consolidation breakout potential
        price_range = max(highs) - min(lows)
        avg_volume = sum(volumes) / len(volumes)
        
        # Higher volume + reasonable range = better setup
        volume_score = min(avg_volume / 1000000, 1.0) * 50  # Max 50 points
        range_score = min(price_range / min(lows) * 100, 5.0) * 10  # Max 50 points
        
        return volume_score + range_score


# ═══════════════════════════════════════════════════════════
# SIMPLIFIED FUNCTION API (for main.py integration)
# ═══════════════════════════════════════════════════════════

def filter_assets_to_trading_venue(assets: List[str], limit: Optional[int] = None) -> List[str]:
    """
    Keep only symbols the configured crypto venue can actually trade.
    When EXCHANGE=okx (default), intersect with live OKX USDT-SWAP instruments.
    """
    from src.config_loader import CONFIG

    if not assets:
        return []

    venue = str(CONFIG.get("exchange") or "okx").lower().strip()
    cleaned = []
    seen = set()
    for raw in assets:
        base = str(raw or "").strip().upper().replace("USDT", "").replace("-SWAP", "").replace("-", "")
        if not base or base in seen:
            continue
        seen.add(base)
        cleaned.append(base)

    if venue != "okx":
        return cleaned[:limit] if limit else cleaned

    try:
        from src.trading.okx_api import fetch_okx_usdt_swap_bases
        okx_bases = fetch_okx_usdt_swap_bases()
    except Exception as e:
        logger.warning(f"OKX venue filter unavailable ({e}); returning unfiltered hunt list")
        return cleaned[:limit] if limit else cleaned

    if not okx_bases:
        logger.warning("OKX venue filter empty; returning unfiltered hunt list")
        return cleaned[:limit] if limit else cleaned

    kept = [a for a in cleaned if a in okx_bases]
    dropped = [a for a in cleaned if a not in okx_bases]
    if dropped:
        logger.info(
            f"Pair Hunter dropped {len(dropped)} non-OKX symbols: {', '.join(dropped[:12])}"
            + ("…" if len(dropped) > 12 else "")
        )
    if limit is not None:
        kept = kept[:limit]
    return kept


async def get_best_pairs(
    exchange_client=None,
    top_n: int = 7,
    min_volatility: float = None,
    use_enhanced: bool = True
) -> List[str]:
    """
    Simple function to get best trading pairs
    
    Args:
        exchange_client: Exchange client (Hyperliquid/Aster/Binance/OKX)
        top_n: Number of pairs to return
        min_volatility: Minimum volatility filter for basic hunting mode
        use_enhanced: Use Binance-based enhanced hunting if no exchange client
        
    Returns:
        List of asset symbols tradeable on the configured venue
    """
    from src.config_loader import CONFIG

    if min_volatility is None:
        min_volatility = float(CONFIG.get('pair_hunter_min_volatility', 1.0) or 1.0)

    # Check if enhanced hunting is enabled via environment
    if CONFIG.get('enable_pair_hunter', False) and use_enhanced:
        # Use enhanced mode (Binance scan → OKX venue filter)
        hunter = PairHunter(exchange_client=None, top_n=top_n)
        assets = await hunter.hunt_pairs(min_volatility=min_volatility)
    elif exchange_client:
        # Use basic mode with exchange client
        hunter = PairHunter(exchange_client, top_n=top_n)
        assets = await hunter.hunt_pairs(min_volatility=min_volatility)
        assets = filter_assets_to_trading_venue(assets, limit=top_n)
    else:
        # Fallback to ASSETS
        assets_str = CONFIG.get('assets') or os.getenv('ASSETS', '')
        assets = [a.strip() for a in str(assets_str).replace(',', ' ').split() if a.strip()][:top_n]
        assets = filter_assets_to_trading_venue(assets, limit=top_n)

    return filter_assets_to_trading_venue(assets or [], limit=top_n)
