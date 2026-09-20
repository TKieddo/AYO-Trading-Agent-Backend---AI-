"""Multi-exchange manager for trading on multiple exchanges simultaneously.

This module allows trading crypto on Aster and Binance exchanges.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from src.config_loader import CONFIG


class MultiExchangeManager:
    """Manages multiple exchanges simultaneously for multi-asset trading."""
    
    def __init__(self):
        """Initialize exchanges based on configuration."""
        self.exchanges: Dict[str, Any] = {}
        self.asset_to_exchange: Dict[str, str] = {}
        self.exchange_configs: Dict[str, Dict[str, Any]] = {}
        
        # Load exchange configurations
        self._load_exchanges()
        self._map_assets_to_exchanges()
    
    def _load_exchanges(self):
        """Load and initialize all configured exchanges."""
        # Check for Aster (crypto)
        aster_user = CONFIG.get("aster_user_address")
        aster_signer = CONFIG.get("aster_signer_address")
        aster_key = CONFIG.get("aster_private_key")
        
        if aster_user and aster_signer and aster_key:
            try:
                from src.trading.aster_api import AsterAPI
                self.exchanges["aster"] = AsterAPI()
                self.exchange_configs["aster"] = {
                    "type": "crypto",
                    "name": "Aster DEX"
                }
                logging.info("✅ Initialized Aster DEX for crypto trading")
            except Exception as e:
                logging.error(f"❌ Failed to initialize Aster: {e}")
        
        # Check for Binance (crypto)
        binance_key = CONFIG.get("binance_api_key")
        binance_secret = CONFIG.get("binance_api_secret")
        if binance_key and binance_secret:
            try:
                from src.trading.binance_api import BinanceAPI
                self.exchanges["binance"] = BinanceAPI()
                testnet = CONFIG.get("binance_testnet", False)
                self.exchange_configs["binance"] = {
                    "type": "crypto",
                    "name": "Binance Futures",
                    "testnet": testnet
                }
                logging.info(f"✅ Initialized Binance Futures ({'testnet' if testnet else 'mainnet'}) for crypto trading")
            except Exception as e:
                logging.error(f"❌ Failed to initialize Binance: {e}")

        # Check for Alpaca (stocks + crypto)
        alpaca_key = CONFIG.get("alpaca_api_key")
        alpaca_secret = CONFIG.get("alpaca_api_secret")
        if alpaca_key and alpaca_secret:
            try:
                from src.trading.alpaca_api import AlpacaAPI
                self.exchanges["alpaca"] = AlpacaAPI()
                paper = CONFIG.get("alpaca_paper", True)
                self.exchange_configs["alpaca"] = {
                    "type": "multi",
                    "name": f"Alpaca ({'paper' if paper else 'live'})",
                    "paper": paper,
                }
                logging.info(f"✅ Initialized Alpaca ({'paper' if paper else 'live'}) for stocks + crypto")
            except Exception as e:
                logging.error(f"❌ Failed to initialize Alpaca: {e}")

        # Check for IG Markets (forex / CFDs)
        ig_key = CONFIG.get("ig_api_key")
        ig_user = CONFIG.get("ig_username")
        ig_pass = CONFIG.get("ig_password")
        if ig_key and ig_user and ig_pass:
            try:
                from src.trading.ig_api import IGAPI
                self.exchanges["ig"] = IGAPI()
                demo = CONFIG.get("ig_demo", True)
                self.exchange_configs["ig"] = {
                    "type": "forex",
                    "name": f"IG Markets ({'demo' if demo else 'live'})",
                    "demo": demo,
                }
                logging.info(f"✅ Initialized IG Markets ({'demo' if demo else 'live'}) for forex/CFDs")
            except Exception as e:
                logging.error(f"❌ Failed to initialize IG: {e}")

        # Check for OKX (crypto SWAP)
        okx_key = CONFIG.get("okx_api_key")
        okx_secret = CONFIG.get("okx_api_secret")
        okx_pass = CONFIG.get("okx_passphrase")
        if okx_key and okx_secret and okx_pass:
            try:
                from src.trading.okx_api import OKXAPI
                self.exchanges["okx"] = OKXAPI()
                demo = CONFIG.get("okx_demo", True)
                self.exchange_configs["okx"] = {
                    "type": "crypto",
                    "name": f"OKX ({'demo' if demo else 'live'})",
                    "demo": demo,
                }
                logging.info(f"✅ Initialized OKX ({'demo' if demo else 'live'}) for crypto SWAP")
            except Exception as e:
                logging.error(f"❌ Failed to initialize OKX: {e}")
        
        if not self.exchanges:
            raise ValueError("No exchanges configured! Please set up at least one exchange.")
        
        logging.info(f"📊 Multi-exchange manager initialized with {len(self.exchanges)} exchange(s)")
        for name, config in self.exchange_configs.items():
            logging.info(f"   - {config['name']} ({config['type']})")
    
    def _map_assets_to_exchanges(self):
        """Map assets to their appropriate exchanges.
        
        Stocks -> Alpaca when available.
        Crypto -> Aster/Binance preferred, else Alpaca.
        """
        def _split(raw: str) -> list:
            if not raw:
                return []
            sep = "," if "," in raw else " "
            return [a.strip().upper() for a in raw.split(sep) if a.strip()]

        crypto_assets = _split(CONFIG.get("crypto_assets") or "")
        stock_assets = _split(CONFIG.get("stock_assets") or "")
        forex_assets = _split(CONFIG.get("forex_assets") or "")
        legacy = _split(CONFIG.get("assets") or "")
        assets_list = []
        seen = set()
        for a in crypto_assets + stock_assets + forex_assets + legacy:
            if a not in seen:
                seen.add(a)
                assets_list.append(a)

        stock_set = set(stock_assets)
        crypto_set = set(crypto_assets)

        for asset_upper in assets_list:
            # Explicit stocks always prefer Alpaca
            if asset_upper in stock_set and "alpaca" in self.exchanges:
                self.asset_to_exchange[asset_upper] = "alpaca"
                continue

            # Forex pairs (6+ char currency codes) -> IG
            forex_ccy = ("USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD")
            looks_forex = (
                asset_upper in set(forex_assets)
                or (len(asset_upper) >= 6 and any(c in asset_upper for c in forex_ccy)
                    and asset_upper[:3] in forex_ccy and asset_upper[3:6] in forex_ccy)
            )
            if looks_forex and "ig" in self.exchanges:
                self.asset_to_exchange[asset_upper] = "ig"
                continue

            # Crypto: prefer the configured EXCHANGE, then other futures venues, then Alpaca/IG
            if asset_upper in crypto_set or asset_upper not in stock_set:
                preferred = str(CONFIG.get("exchange") or "").lower()
                crypto_order = []
                for name in (preferred, "okx", "binance", "aster", "alpaca", "ig"):
                    if name and name not in crypto_order:
                        crypto_order.append(name)
                routed = False
                for name in crypto_order:
                    if name in self.exchanges:
                        self.asset_to_exchange[asset_upper] = name
                        routed = True
                        break
                if not routed:
                    logging.warning(f"⚠️  No exchange available for {asset_upper}")
                continue

            if "alpaca" in self.exchanges:
                self.asset_to_exchange[asset_upper] = "alpaca"
            elif "ig" in self.exchanges:
                self.asset_to_exchange[asset_upper] = "ig"
            else:
                logging.warning(f"⚠️  No exchange available for {asset_upper}")

        if assets_list:
            logging.info(f"✅ Asset mapping complete: {len(assets_list)} assets -> {self.asset_to_exchange}")
        else:
            logging.warning("⚠️  No assets configured in ASSETS / STOCK_ASSETS / CRYPTO_ASSETS")
    
    def get_exchange_for_asset(self, asset: str) -> Optional[Any]:
        """Get the appropriate exchange for an asset.
        
        Args:
            asset: Asset symbol (e.g., 'BTC', 'EURUSD')
            
        Returns:
            Exchange instance or None
        """
        asset_upper = asset.upper()
        
        # Check explicit mapping first
        if asset_upper in self.asset_to_exchange:
            exchange_name = self.asset_to_exchange[asset_upper]
            exchange = self.exchanges.get(exchange_name)
            if exchange:
                return exchange
            else:
                logging.warning(f"⚠️  Exchange '{exchange_name}' not found for asset {asset_upper}")
        
        # Default to available crypto exchange
        if "aster" in self.exchanges:
            logging.debug(f"🔍 Auto-detected {asset_upper} -> Aster")
            return self.exchanges["aster"]
        elif "binance" in self.exchanges:
            logging.debug(f"🔍 Auto-detected {asset_upper} -> Binance")
            return self.exchanges["binance"]
        elif "okx" in self.exchanges:
            logging.debug(f"🔍 Auto-detected {asset_upper} -> OKX")
            return self.exchanges["okx"]
        elif "alpaca" in self.exchanges:
            logging.debug(f"🔍 Auto-detected {asset_upper} -> Alpaca")
            return self.exchanges["alpaca"]
        elif "ig" in self.exchanges:
            logging.debug(f"🔍 Auto-detected {asset_upper} -> IG")
            return self.exchanges["ig"]
        
        logging.error(f"❌ No exchange found for asset {asset_upper}")
        return None
    
    def get_exchange_name_for_asset(self, asset: str) -> Optional[str]:
        """Get the exchange name for an asset.
        
        Args:
            asset: Asset symbol
            
        Returns:
            Exchange name or None
        """
        asset_upper = asset.upper()
        
        if asset_upper in self.asset_to_exchange:
            return self.asset_to_exchange[asset_upper]
        
        # Auto-detect
        forex_indicators = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]
        if len(asset_upper) >= 6 and any(fx in asset_upper for fx in forex_indicators):
            if "ig" in self.exchanges:
                return "ig"
            return "pepperstone" if "pepperstone" in self.exchanges else None
        
        if "aster" in self.exchanges:
            return "aster"
        elif "binance" in self.exchanges:
            return "binance"
        elif "okx" in self.exchanges:
            return "okx"
        elif "hyperliquid" in self.exchanges:
            return "hyperliquid"
        return None
    
    async def get_all_positions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get positions from all exchanges.
        
        Returns:
            Dictionary mapping exchange names to their positions
        """
        all_positions = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                state = await exchange.get_user_state()
                positions = state.get("positions", [])
                
                # Add exchange info to each position
                for pos in positions:
                    pos["exchange"] = exchange_name
                    pos["exchange_type"] = self.exchange_configs[exchange_name]["type"]
                
                all_positions[exchange_name] = positions
            except Exception as e:
                logging.error(f"Error getting positions from {exchange_name}: {e}")
                all_positions[exchange_name] = []
        
        return all_positions
    
    async def get_all_balances(self) -> Dict[str, Dict[str, float]]:
        """Get balances from all exchanges.
        
        Returns:
            Dictionary mapping exchange names to their balance info
        """
        all_balances = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                state = await exchange.get_user_state()
                all_balances[exchange_name] = {
                    "balance": state.get("balance", 0.0),
                    "total_value": state.get("total_value", 0.0),
                    "exchange_type": self.exchange_configs[exchange_name]["type"]
                }
            except Exception as e:
                logging.error(f"Error getting balance from {exchange_name}: {e}")
                all_balances[exchange_name] = {
                    "balance": 0.0,
                    "total_value": 0.0,
                    "exchange_type": self.exchange_configs[exchange_name]["type"]
                }
        
        return all_balances
    
    async def get_merged_user_state(self) -> Dict[str, Any]:
        """Combine balances and positions from every live exchange into one state dict."""
        positions: List[Dict[str, Any]] = []
        balance = 0.0
        total_value = 0.0
        for exchange_name, exchange in self.exchanges.items():
            try:
                state = await exchange.get_user_state()
                balance += float(state.get("balance") or 0)
                total_value += float(state.get("total_value") or state.get("balance") or 0)
                for pos in state.get("positions") or []:
                    pos = dict(pos)
                    pos["exchange"] = exchange_name
                    pos["exchange_type"] = self.exchange_configs.get(exchange_name, {}).get("type")
                    positions.append(pos)
            except Exception as e:
                logging.error(f"Error merging state from {exchange_name}: {e}")
        return {"balance": balance, "total_value": total_value, "positions": positions}

    def get_exchanges_by_type(self, exchange_type: str) -> Dict[str, Any]:
        """Get all exchanges of a specific type.
        
        Args:
            exchange_type: "crypto" (only crypto exchanges are supported)
            
        Returns:
            Dictionary of exchange name -> exchange instance
        """
        return {
            name: exchange
            for name, exchange in self.exchanges.items()
            if self.exchange_configs[name]["type"] == exchange_type
        }
    
    def list_exchanges(self) -> List[str]:
        """List all active exchange names.
        
        Returns:
            List of exchange names
        """
        return list(self.exchanges.keys())
    
    def has_exchange(self, exchange_name: str) -> bool:
        """Check if an exchange is available.
        
        Args:
            exchange_name: Exchange name to check
            
        Returns:
            True if exchange is available
        """
        return exchange_name in self.exchanges
