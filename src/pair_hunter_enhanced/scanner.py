"""
🔍 Binance Scanner - Fetches all futures pairs and market data
"""
import requests
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    symbol: str
    price: float
    volume_24h_usd: float
    price_change_1h_pct: float
    price_change_24h_pct: float
    high_24h: float
    low_24h: float
    bid_ask_spread_pct: float
    funding_rate: Optional[float] = None
    open_interest_usd: Optional[float] = None

class BinanceScanner:
    """Scans Binance USD-M Futures for all active pairs"""
    
    BASE_URL = "https://fapi.binance.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AYO-Trading-Agent/1.0'
        })
    
    def get_all_symbols(self) -> List[str]:
        """Fetch all active USD-M futures symbols"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/fapi/v1/exchangeInfo",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            symbols = []
            for symbol_info in data.get('symbols', []):
                if (symbol_info.get('contractType') == 'PERPETUAL' and
                    symbol_info.get('status') == 'TRADING' and
                    symbol_info.get('quoteAsset') == 'USDT'):
                    symbols.append(symbol_info['symbol'])
            
            logger.info(f"Found {len(symbols)} active USD-M perpetual futures")
            return symbols
            
        except Exception as e:
            logger.error(f"Failed to fetch symbols: {e}")
            return []
    
    def get_24h_ticker_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Fetch 24h ticker data for all symbols"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/fapi/v1/ticker/24hr",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            market_data = {}
            for ticker in data:
                symbol = ticker.get('symbol')
                if symbol not in symbols:
                    continue
                
                price = float(ticker.get('lastPrice', 0))
                quote_volume = float(ticker.get('quoteVolume', 0))
                
                bid = float(ticker.get('bidPrice', price))
                ask = float(ticker.get('askPrice', price))
                spread_pct = ((ask - bid) / price * 100) if price > 0 else 0
                
                market_data[symbol] = MarketData(
                    symbol=symbol,
                    price=price,
                    volume_24h_usd=quote_volume,
                    price_change_1h_pct=self._calc_1h_change(ticker),
                    price_change_24h_pct=float(ticker.get('priceChangePercent', 0)),
                    high_24h=float(ticker.get('highPrice', 0)),
                    low_24h=float(ticker.get('lowPrice', 0)),
                    bid_ask_spread_pct=spread_pct
                )
            
            logger.info(f"Fetched 24h data for {len(market_data)} symbols")
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to fetch ticker data: {e}")
            return {}
    
    def _calc_1h_change(self, ticker: dict) -> float:
        change_24h = float(ticker.get('priceChangePercent', 0))
        return change_24h / 24
    
    def get_klines_for_atr(self, symbol: str, period: str = "1h", limit: int = 24) -> pd.DataFrame:
        """Fetch klines for ATR calculation"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/fapi/v1/klines",
                params={'symbol': symbol, 'interval': period, 'limit': limit},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_volume',
                'taker_buy_quote_volume', 'ignore'
            ])
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range percentage"""
        if df.empty or len(df) < period:
            return 0.0
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        current_price = close.iloc[-1]
        atr_pct = (atr / current_price * 100) if current_price > 0 else 0
        
        return atr_pct
