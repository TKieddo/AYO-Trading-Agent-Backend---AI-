"""
📊 Scalping Scorer - Ranks pairs by scalping potential
"""
from typing import Dict, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ScoredPair:
    symbol: str
    scalping_score: float
    volatility_score: float
    volume_score: float
    trend_score: float
    momentum_score: float
    atr_pct: float
    rank: int = 0

class ScalpingScorer:
    """Scores pairs for scalping suitability"""
    
    def __init__(self):
        self.ideal_atr = 5.5
    
    def score_pairs(self, market_data: Dict, atr_data: Dict[str, float]) -> List[ScoredPair]:
        """Score all pairs and return ranked list"""
        scored = []
        
        for symbol, data in market_data.items():
            atr_pct = atr_data.get(symbol, 0)
            
            vol_score = self._calc_volatility_score(atr_pct)
            volume_score = self._calc_volume_score(data.volume_24h_usd)
            trend_score = self._calc_trend_score(data)
            momentum_score = self._calc_momentum_score(data.price_change_1h_pct)
            
            total_score = (
                vol_score * 0.40 +
                volume_score * 0.30 +
                trend_score * 0.20 +
                momentum_score * 0.10
            )
            
            scored.append(ScoredPair(
                symbol=symbol,
                scalping_score=round(total_score, 4),
                volatility_score=round(vol_score, 4),
                volume_score=round(volume_score, 4),
                trend_score=round(trend_score, 4),
                momentum_score=round(momentum_score, 4),
                atr_pct=round(atr_pct, 2)
            ))
        
        scored.sort(key=lambda x: x.scalping_score, reverse=True)
        
        for i, pair in enumerate(scored):
            pair.rank = i + 1
        
        return scored
    
    def _calc_volatility_score(self, atr_pct: float) -> float:
        if atr_pct < 1.0:
            return 0.1
        elif atr_pct < 3.0:
            return 0.3 + (atr_pct - 1.0) / 2.0 * 0.5
        elif atr_pct <= 8.0:
            distance_from_ideal = abs(atr_pct - self.ideal_atr)
            return max(0.8, 1.0 - distance_from_ideal / 5.0)
        elif atr_pct <= 12.0:
            return 0.6 - (atr_pct - 8.0) / 4.0 * 0.4
        else:
            return 0.2
    
    def _calc_volume_score(self, volume_24h: float) -> float:
        target_volume = 100_000_000
        return min(volume_24h / target_volume, 1.0)
    
    def _calc_trend_score(self, data) -> float:
        price_range_pct = ((data.high_24h - data.low_24h) / data.price * 100) if data.price > 0 else 0
        
        if price_range_pct < 2:
            return 0.3
        elif price_range_pct < 15:
            return 0.6 + (price_range_pct / 15) * 0.4
        else:
            return 0.7
    
    def _calc_momentum_score(self, change_1h_pct: float) -> float:
        abs_change = abs(change_1h_pct)
        
        if abs_change < 0.5:
            return 0.3
        elif abs_change <= 3.0:
            return 0.5 + (abs_change / 3.0) * 0.5
        elif abs_change <= 8.0:
            return 1.0 - (abs_change - 3.0) / 5.0 * 0.5
        else:
            return 0.3
    
    def get_top_pairs(self, scored: List[ScoredPair], n: int = 7, min_score: float = 0.3) -> List[ScoredPair]:
        valid = [p for p in scored if p.scalping_score >= min_score]
        return valid[:n]
    
    def format_leaderboard(self, top_pairs: List[ScoredPair]) -> str:
        lines = ["\n🏆 PAIR HUNTER LEADERBOARD"]
        lines.append("-" * 60)
        for p in top_pairs:
            lines.append(f"#{p.rank} {p.symbol}: {p.scalping_score:.3f} (ATR: {p.atr_pct}%)")
        return "\n".join(lines)
