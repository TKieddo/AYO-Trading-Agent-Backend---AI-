"""
🛡️ Pair Filter - Removes scams and low-quality pairs
"""
import logging
from typing import List, Dict, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FilterConfig:
    min_volume_24h_usd: float = 10_000_000
    max_spread_pct: float = 0.3
    max_price_change_1h_pct: float = 50.0
    min_price_usd: float = 0.0001
    max_price_usd: float = 100000
    exclude_patterns: tuple = ('DOWN', 'UP', 'BEAR', 'BULL')
    max_funding_rate_abs: float = 0.01

class PairFilter:
    """Filters out scammy, illiquid, or unsuitable pairs"""
    
    BLACKLIST: Set[str] = set()
    
    def __init__(self, config: FilterConfig = None):
        self.config = config or FilterConfig()
    
    def apply_all_filters(self, market_data: Dict) -> Dict:
        """Apply all filters and return only valid pairs"""
        filtered = {}
        rejected = []
        
        for symbol, data in market_data.items():
            is_valid, reason = self._check_pair(data)
            if is_valid:
                filtered[symbol] = data
            else:
                rejected.append((symbol, reason))
        
        if rejected:
            logger.info(f"Rejected {len(rejected)} pairs (showing first 5):")
            for sym, reason in rejected[:5]:
                logger.info(f"  - {sym}: {reason}")
        
        logger.info(f"✅ {len(filtered)} pairs passed all filters")
        return filtered
    
    def _check_pair(self, data) -> tuple:
        """Check if a single pair passes all filters"""
        symbol = data.symbol
        cfg = self.config
        
        if symbol in self.BLACKLIST:
            return False, "Manual blacklist"
        
        if any(pattern in symbol for pattern in cfg.exclude_patterns):
            return False, "Leveraged token"
        
        if data.volume_24h_usd < cfg.min_volume_24h_usd:
            return False, f"Low volume"
        
        if data.bid_ask_spread_pct > cfg.max_spread_pct:
            return False, f"High spread"
        
        if data.price < cfg.min_price_usd or data.price > cfg.max_price_usd:
            return False, f"Price out of range"
        
        if abs(data.price_change_1h_pct) > cfg.max_price_change_1h_pct:
            return False, f"Extreme 1h move"
        
        return True, "OK"
    
    def add_to_blacklist(self, symbols: List[str]):
        for sym in symbols:
            self.BLACKLIST.add(sym)
        logger.info(f"Added {len(symbols)} symbols to blacklist")
