"""OKX REST API client (demo/live USDT-margined SWAP) with the AYO exchange interface."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

from src.config_loader import CONFIG

logger = logging.getLogger(__name__)

# Public instrument universe cache (no auth required).
_USDT_SWAP_BASES_CACHE: Dict[str, Any] = {"ts": 0.0, "bases": set()}
_USDT_SWAP_BASES_TTL_SEC = 900


def fetch_okx_usdt_swap_bases(
    base_url: Optional[str] = None,
    ttl_sec: int = _USDT_SWAP_BASES_TTL_SEC,
) -> set:
    """
    Return live OKX USDT-margined SWAP base assets (e.g. {'BTC','ETH',...}).
    Uses the public instruments endpoint — no API keys required.
    """
    now = time.time()
    cached = _USDT_SWAP_BASES_CACHE.get("bases") or set()
    if cached and (now - float(_USDT_SWAP_BASES_CACHE.get("ts") or 0)) < ttl_sec:
        return set(cached)

    url = (base_url or CONFIG.get("okx_base_url") or "https://www.okx.com").rstrip("/")
    try:
        resp = requests.get(
            f"{url}/api/v5/public/instruments",
            params={"instType": "SWAP"},
            timeout=20,
        )
        resp.raise_for_status()
        payload = resp.json() or {}
        rows = payload.get("data") if isinstance(payload, dict) else payload
        bases = set()
        for row in rows if isinstance(rows, list) else []:
            if not isinstance(row, dict):
                continue
            state = str(row.get("state") or "").lower()
            if state and state != "live":
                continue
            settle = (row.get("settleCcy") or row.get("quoteCcy") or "").upper()
            inst_id = (row.get("instId") or "").upper()
            if settle and settle != "USDT":
                continue
            if not inst_id.endswith("-USDT-SWAP"):
                continue
            base = inst_id.replace("-USDT-SWAP", "").split("-")[0]
            if base:
                bases.add(base)
        if bases:
            _USDT_SWAP_BASES_CACHE["ts"] = now
            _USDT_SWAP_BASES_CACHE["bases"] = bases
            logger.info(f"OKX USDT-SWAP universe: {len(bases)} live bases")
            return bases
        logger.warning("OKX instruments returned no USDT-SWAP bases")
    except Exception as e:
        logger.warning(f"Failed to fetch OKX USDT-SWAP instruments: {e}")
    return set(cached) if cached else set()


class OKXAPI:
    """Client for OKX perpetual SWAP (crypto) — demo via x-simulated-trading header."""

    def __init__(self):
        api_key = CONFIG.get("okx_api_key")
        api_secret = CONFIG.get("okx_api_secret")
        passphrase = CONFIG.get("okx_passphrase")
        demo = bool(CONFIG.get("okx_demo", True))

        if not api_key or not api_secret or not passphrase:
            raise ValueError(
                "OKX_API_KEY, OKX_API_SECRET, and OKX_PASSPHRASE must be set in .env "
                "(Demo Trading → Personal Center → Demo Trading API)"
            )

        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.demo = demo
        self.base = CONFIG.get("okx_base_url", "https://www.okx.com").rstrip("/")
        self.td_mode = (CONFIG.get("okx_td_mode") or "cross").lower()  # cross | isolated
        self.pos_mode = (CONFIG.get("okx_pos_mode") or "net_mode").lower()  # net_mode | long_short_mode
        self.default_leverage = int(
            CONFIG.get("okx_leverage", CONFIG.get("default_leverage", 10)) or 10
        )
        self._inst_cache: Dict[str, Dict[str, Any]] = {}

        # Validate credentials early
        bal = self._request("GET", "/api/v5/account/balance")
        avail = self._extract_usdt_equity(bal)
        logger.info(
            f"OKX client initialized (demo={demo}, equity≈{avail}, "
            f"leverage={self.default_leverage}x, tdMode={self.td_mode})"
        )

    # ------------------------------------------------------------------ auth
    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def _sign(self, timestamp: str, method: str, path_with_query: str, body: str) -> str:
        message = f"{timestamp}{method.upper()}{path_with_query}{body}"
        mac = hmac.new(
            self.api_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        )
        return base64.b64encode(mac.digest()).decode("utf-8")

    def _headers(self, method: str, path_with_query: str, body: str = "") -> Dict[str, str]:
        ts = self._timestamp()
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": self._sign(ts, method, path_with_query, body),
            "OK-ACCESS-TIMESTAMP": ts,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.demo:
            headers["x-simulated-trading"] = "1"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
        auth: bool = True,
        max_attempts: int = 3,
    ) -> Any:
        query = ""
        if params:
            query = "?" + urlencode({k: v for k, v in params.items() if v is not None})
        path_with_query = f"{path}{query}"
        body_str = json.dumps(json_body) if json_body is not None else ""
        url = f"{self.base}{path_with_query}"

        last_err: Optional[Exception] = None
        for attempt in range(max_attempts):
            try:
                headers = (
                    self._headers(method, path_with_query, body_str if method.upper() != "GET" else "")
                    if auth
                    else {"Content-Type": "application/json", "Accept": "application/json"}
                )
                if self.demo and not auth:
                    headers["x-simulated-trading"] = "1"

                resp = requests.request(
                    method,
                    url,
                    headers=headers,
                    data=body_str if json_body is not None else None,
                    timeout=30,
                )
                if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_attempts - 1:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                if resp.status_code >= 400:
                    raise RuntimeError(
                        f"OKX {method} {path} HTTP {resp.status_code}: {resp.text[:400]}"
                    )
                data = resp.json() if resp.content else {}
                code = str(data.get("code", "0"))
                if code != "0":
                    raise RuntimeError(
                        f"OKX {method} {path} failed code={code}: {data.get('msg')} {str(data)[:300]}"
                    )
                return data.get("data", data)
            except Exception as e:
                last_err = e
                if attempt < max_attempts - 1 and "failed code=" not in str(e):
                    time.sleep(0.4 * (2 ** attempt))
                    continue
                raise
        raise last_err or RuntimeError("OKX request failed")

    async def _retry(self, fn, *args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)

    # --------------------------------------------------------------- symbols
    def _normalize_asset(self, asset: str) -> str:
        a = (asset or "").strip().upper()
        for suf in ("-USDT-SWAP", "-USDT", "/USDT", "USDT", "-USD-SWAP", "-USD"):
            if a.endswith(suf.replace("-", "")) or a.endswith(suf):
                a = a[: -len(suf)] if a.endswith(suf) else a
                break
        a = a.replace("-USDT-SWAP", "").replace("-USDT", "").replace("/USDT", "")
        a = a.replace("USDT", "").replace("-", "").replace("/", "")
        return a

    def _to_inst_id(self, asset: str) -> str:
        raw = (asset or "").strip().upper()
        if raw.endswith("-SWAP") or "-SWAP" in raw:
            return raw
        base = self._normalize_asset(asset)
        return f"{base}-USDT-SWAP"

    def _from_inst_id(self, inst_id: str) -> str:
        s = (inst_id or "").upper()
        return s.replace("-USDT-SWAP", "").replace("-USDT", "").split("-")[0]

    def _get_instrument(self, inst_id: str) -> Dict[str, Any]:
        if inst_id in self._inst_cache:
            return self._inst_cache[inst_id]
        data = self._request(
            "GET",
            "/api/v5/public/instruments",
            params={"instType": "SWAP", "instId": inst_id},
            auth=False,
        )
        items = data if isinstance(data, list) else []
        info = items[0] if items else {}
        self._inst_cache[inst_id] = info
        return info

    def list_usdt_swap_bases(self) -> set:
        """Cached set of base assets tradeable as USDT-SWAP on this OKX account/venue."""
        return fetch_okx_usdt_swap_bases(base_url=self.base)

    def is_usdt_swap_tradable(self, asset: str) -> bool:
        base = self._normalize_asset(asset)
        if not base:
            return False
        bases = self.list_usdt_swap_bases()
        if not bases:
            # Fail open only when the public catalog is unreachable (avoid total halt).
            info = self._get_instrument(self._to_inst_id(base))
            return bool(info.get("instId"))
        return base in bases

    def _contracts_from_coins(self, asset: str, coin_qty: float) -> str:
        """Convert coin quantity to OKX contract size string."""
        inst_id = self._to_inst_id(asset)
        info = self._get_instrument(inst_id)
        ct_val = float(info.get("ctVal") or 1)
        lot_sz = float(info.get("lotSz") or 1)
        min_sz = float(info.get("minSz") or lot_sz)
        if ct_val <= 0:
            ct_val = 1.0
        contracts = abs(float(coin_qty or 0)) / ct_val
        # Round down to lot size
        if lot_sz > 0:
            contracts = (contracts // lot_sz) * lot_sz
        if contracts < min_sz:
            contracts = min_sz
        # Format cleanly
        if contracts >= 1:
            return str(int(contracts)) if abs(contracts - int(contracts)) < 1e-9 else f"{contracts:.4f}".rstrip("0").rstrip(".")
        return f"{contracts:.8f}".rstrip("0").rstrip(".")

    def _extract_usdt_equity(self, balance_data: Any) -> float:
        rows = balance_data if isinstance(balance_data, list) else []
        if not rows:
            return 0.0
        details = rows[0].get("details") or []
        for d in details:
            if (d.get("ccy") or "").upper() == "USDT":
                for key in ("eq", "cashBal", "availBal", "availEq"):
                    try:
                        if d.get(key) is not None:
                            return float(d[key])
                    except (TypeError, ValueError):
                        continue
        try:
            return float(rows[0].get("totalEq") or 0)
        except (TypeError, ValueError):
            return 0.0

    # --------------------------------------------------------------- trading
    async def set_leverage(self, asset: str, leverage: int):
        inst_id = self._to_inst_id(asset)
        lev = str(int(leverage or self.default_leverage))
        body: Dict[str, Any] = {
            "instId": inst_id,
            "lever": lev,
            "mgnMode": self.td_mode,
        }
        try:
            await self._retry(
                lambda: self._request("POST", "/api/v5/account/set-leverage", json_body=body)
            )
            logger.info(f"OKX set leverage {inst_id} → {lev}x ({self.td_mode})")
        except Exception as e:
            logger.warning(f"OKX set_leverage {inst_id} failed: {e}")

    def _pos_side_for(self, side: str, reduce_only: bool) -> Optional[str]:
        if self.pos_mode in ("net", "net_mode"):
            return "net"
        # hedge / long_short_mode
        side = side.lower()
        if reduce_only:
            return "long" if side == "sell" else "short"
        return "long" if side == "buy" else "short"

    async def place_buy_order(
        self,
        asset: str,
        amount: float,
        leverage: Optional[int] = None,
        slippage: float = 0.01,
        reduce_only: bool = False,
    ):
        _ = slippage
        await self.set_leverage(asset, leverage or self.default_leverage)
        return await self._place_market(asset, "buy", amount, reduce_only=reduce_only)

    async def place_sell_order(
        self,
        asset: str,
        amount: float,
        leverage: Optional[int] = None,
        slippage: float = 0.01,
        reduce_only: bool = False,
    ):
        _ = slippage
        await self.set_leverage(asset, leverage or self.default_leverage)
        return await self._place_market(asset, "sell", amount, reduce_only=reduce_only)

    async def _place_market(
        self, asset: str, side: str, amount: float, reduce_only: bool = False
    ) -> Dict[str, Any]:
        inst_id = self._to_inst_id(asset)
        sz = self._contracts_from_coins(asset, amount)
        body: Dict[str, Any] = {
            "instId": inst_id,
            "tdMode": self.td_mode,
            "side": side.lower(),
            "ordType": "market",
            "sz": sz,
        }
        pos_side = self._pos_side_for(side, reduce_only)
        if pos_side:
            body["posSide"] = pos_side
        if reduce_only:
            body["reduceOnly"] = True

        result = await self._retry(
            lambda: self._request("POST", "/api/v5/trade/order", json_body=body)
        )
        row = result[0] if isinstance(result, list) and result else (result or {})
        logger.info(
            f"OKX {side.upper()} {inst_id} sz={sz} reduceOnly={reduce_only} "
            f"ordId={row.get('ordId')} clOrdId={row.get('clOrdId')}"
        )
        return row if isinstance(row, dict) else {"raw": result}

    async def place_take_profit(self, asset: str, is_long: bool, quantity: float, tp_price: float):
        """Algo take-profit (market on trigger)."""
        return await self._place_algo(
            asset, is_long=is_long, quantity=quantity, trigger_px=tp_price, kind="tp"
        )

    async def place_stop_loss(self, asset: str, is_long: bool, quantity: float, sl_price: float):
        """Algo stop-loss (market on trigger)."""
        return await self._place_algo(
            asset, is_long=is_long, quantity=quantity, trigger_px=sl_price, kind="sl"
        )

    async def _place_algo(
        self,
        asset: str,
        is_long: bool,
        quantity: float,
        trigger_px: float,
        kind: str,
    ) -> Dict[str, Any]:
        inst_id = self._to_inst_id(asset)
        sz = self._contracts_from_coins(asset, quantity)
        side = "sell" if is_long else "buy"
        body: Dict[str, Any] = {
            "instId": inst_id,
            "tdMode": self.td_mode,
            "side": side,
            "ordType": "conditional",
            "sz": sz,
            "reduceOnly": True,
        }
        pos_side = self._pos_side_for(side, reduce_only=True)
        if pos_side:
            body["posSide"] = pos_side

        px = str(round(float(trigger_px), 8))
        if kind == "tp":
            body["tpTriggerPx"] = px
            body["tpOrdPx"] = "-1"  # market
            body["tpTriggerPxType"] = "last"
        else:
            body["slTriggerPx"] = px
            body["slOrdPx"] = "-1"
            body["slTriggerPxType"] = "last"

        result = await self._retry(
            lambda: self._request("POST", "/api/v5/trade/order-algo", json_body=body)
        )
        row = result[0] if isinstance(result, list) and result else (result or {})
        logger.info(f"OKX {kind.upper()} {inst_id} trigger={px} algoId={row.get('algoId')}")
        return row if isinstance(row, dict) else {"raw": result}

    def extract_oids(self, order_result: Dict) -> List[str]:
        if not order_result:
            return []
        for key in ("ordId", "algoId", "clOrdId", "id"):
            if order_result.get(key):
                return [str(order_result[key])]
        return []

    async def get_current_price(self, asset: str) -> float:
        inst_id = self._to_inst_id(asset)
        try:
            data = await self._retry(
                lambda: self._request(
                    "GET",
                    "/api/v5/market/ticker",
                    params={"instId": inst_id},
                    auth=False,
                )
            )
            row = data[0] if isinstance(data, list) and data else {}
            for key in ("last", "askPx", "bidPx"):
                if row.get(key) is not None:
                    return float(row[key])
        except Exception as e:
            logger.error(f"OKX price error for {asset}: {e}")
        return 0.0

    async def get_user_state(self) -> Dict[str, Any]:
        try:
            bal = await self._retry(lambda: self._request("GET", "/api/v5/account/balance"))
            positions_raw = await self._retry(
                lambda: self._request(
                    "GET", "/api/v5/account/positions", params={"instType": "SWAP"}
                )
            )
            equity = self._extract_usdt_equity(bal)
            rows = bal if isinstance(bal, list) else []
            avail = equity
            if rows:
                details = rows[0].get("details") or []
                for d in details:
                    if (d.get("ccy") or "").upper() == "USDT":
                        try:
                            avail = float(d.get("availEq") or d.get("availBal") or equity)
                        except (TypeError, ValueError):
                            pass

            enriched = []
            for pos in positions_raw if isinstance(positions_raw, list) else []:
                try:
                    pos_sz = float(pos.get("pos") or 0)
                except (TypeError, ValueError):
                    pos_sz = 0.0
                if abs(pos_sz) <= 0:
                    continue
                inst_id = pos.get("instId") or ""
                asset = self._from_inst_id(inst_id)
                info = self._get_instrument(inst_id)
                ct_val = float(info.get("ctVal") or 1)
                # Convert contracts → coin qty
                coin_qty = abs(pos_sz) * ct_val
                side = (pos.get("posSide") or "").lower()
                if side == "short" or (side in ("", "net") and pos_sz < 0):
                    signed = -coin_qty
                else:
                    signed = coin_qty
                entry = float(pos.get("avgPx") or 0)
                mark = float(pos.get("markPx") or entry)
                upl = float(pos.get("upl") or 0)
                margin = float(pos.get("margin") or pos.get("imr") or 0)
                lev = float(pos.get("lever") or self.default_leverage)
                notional = abs(coin_qty * mark)
                if margin <= 0 and lev > 0:
                    margin = notional / lev
                roi = (upl / margin * 100.0) if margin > 0 else None

                enriched.append({
                    "coin": asset,
                    "symbol": asset,
                    "szi": signed,
                    "quantity": signed,
                    "entryPx": entry,
                    "entry_price": entry,
                    "entryPrice": entry,
                    "markPrice": mark,
                    "current_price": mark,
                    "pnl": upl,
                    "unrealized_pnl": upl,
                    "unRealizedProfit": upl,
                    "roiPercent": roi,
                    "roi": roi,
                    "notional": notional,
                    "initialMargin": margin,
                    "positionInitialMargin": margin,
                    "initial_margin": margin,
                    "leverage": lev,
                    "liquidationPx": pos.get("liqPx"),
                    "okx_inst_id": inst_id,
                    "okx_pos": pos_sz,
                })

            return {
                "balance": avail,
                "total_value": equity,
                "positions": enriched,
                "asset_balances": [
                    {
                        "asset": "USDT",
                        "walletBalance": equity,
                        "availableBalance": avail,
                        "crossWalletBalance": equity,
                        "crossUnPnl": sum(p.get("pnl", 0) for p in enriched),
                        "positionValue": equity,
                    }
                ],
                "okx_account": {"demo": self.demo, "td_mode": self.td_mode},
            }
        except Exception as e:
            logger.error(f"OKX get_user_state error: {e}", exc_info=True)
            return {"balance": 0, "total_value": 0, "positions": [], "asset_balances": []}

    async def get_open_orders(self) -> List[Dict]:
        out: List[Dict] = []
        try:
            pending = await self._retry(
                lambda: self._request(
                    "GET",
                    "/api/v5/trade/orders-pending",
                    params={"instType": "SWAP"},
                )
            )
            for o in pending if isinstance(pending, list) else []:
                asset = self._from_inst_id(o.get("instId", ""))
                otype = (o.get("ordType") or "").upper()
                mapped = "TAKE_PROFIT" if "LIMIT" in otype else otype
                out.append({
                    "coin": asset,
                    "symbol": asset,
                    "oid": o.get("ordId"),
                    "orderId": o.get("ordId"),
                    "type": mapped,
                    "side": o.get("side"),
                    "trigger": o.get("px") or o.get("avgPx") or 0,
                    "raw": o,
                })
        except Exception as e:
            logger.debug(f"OKX pending orders: {e}")

        try:
            algos = await self._retry(
                lambda: self._request(
                    "GET",
                    "/api/v5/trade/orders-algo-pending",
                    params={"instType": "SWAP", "ordType": "conditional"},
                )
            )
            for o in algos if isinstance(algos, list) else []:
                asset = self._from_inst_id(o.get("instId", ""))
                has_tp = o.get("tpTriggerPx") not in (None, "", "0")
                mapped = "TAKE_PROFIT" if has_tp else "STOP"
                trigger = o.get("tpTriggerPx") or o.get("slTriggerPx") or 0
                out.append({
                    "coin": asset,
                    "symbol": asset,
                    "oid": o.get("algoId"),
                    "orderId": o.get("algoId"),
                    "type": mapped,
                    "side": o.get("side"),
                    "trigger": trigger,
                    "raw": o,
                })
        except Exception as e:
            logger.debug(f"OKX algo orders: {e}")
        return out

    async def get_recent_fills(self, limit: int = 50) -> List[Dict]:
        try:
            data = await self._retry(
                lambda: self._request(
                    "GET",
                    "/api/v5/trade/fills-history",
                    params={"instType": "SWAP", "limit": str(min(limit, 100))},
                )
            )
            out = []
            for f in data if isinstance(data, list) else []:
                asset = self._from_inst_id(f.get("instId", ""))
                out.append({
                    "coin": asset,
                    "symbol": asset,
                    "side": f.get("side"),
                    "px": float(f.get("fillPx") or 0),
                    "price": float(f.get("fillPx") or 0),
                    "sz": float(f.get("fillSz") or 0),
                    "size": float(f.get("fillSz") or 0),
                    "fee": float(f.get("fee") or 0),
                    "realizedPnl": f.get("fillPnl"),
                    "pnl": f.get("fillPnl"),
                    "time": f.get("ts"),
                    "id": f.get("tradeId") or f.get("billId"),
                    "raw": f,
                })
            return out
        except Exception as e:
            logger.debug(f"OKX fills: {e}")
            return []

    async def get_open_interest(self, asset: str) -> Optional[float]:
        try:
            inst_id = self._to_inst_id(asset)
            data = await self._retry(
                lambda: self._request(
                    "GET",
                    "/api/v5/public/open-interest",
                    params={"instId": inst_id},
                    auth=False,
                )
            )
            row = data[0] if isinstance(data, list) and data else {}
            return float(row["oi"]) if row.get("oi") is not None else None
        except Exception:
            return None

    async def get_funding_rate(self, asset: str) -> Optional[float]:
        try:
            inst_id = self._to_inst_id(asset)
            data = await self._retry(
                lambda: self._request(
                    "GET",
                    "/api/v5/public/funding-rate",
                    params={"instId": inst_id},
                    auth=False,
                )
            )
            row = data[0] if isinstance(data, list) and data else {}
            return float(row["fundingRate"]) if row.get("fundingRate") is not None else None
        except Exception:
            return None

    def fetch_candles(self, symbol: str, interval: str = "15m", limit: int = 100) -> List[List[Any]]:
        """Sync OHLCV rows as ``[ts_ms, open, high, low, close, volume]`` for the TA client."""
        inst_id = self._to_inst_id(symbol)
        bar_map = {
            "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1H", "2h": "2H", "4h": "4H", "6h": "6H", "12h": "12H",
            "1d": "1D", "1w": "1W",
        }
        bar = bar_map.get((interval or "15m").lower(), "15m")
        try:
            data = self._request(
                "GET",
                "/api/v5/market/candles",
                params={"instId": inst_id, "bar": bar, "limit": str(min(int(limit), 300))},
                auth=False,
            )
        except Exception as e:
            logger.error(f"OKX candles error for {symbol} {interval}: {e}")
            return []

        rows: List[List[Any]] = []
        for raw in reversed(data if isinstance(data, list) else []):
            try:
                rows.append([
                    int(raw[0]),
                    float(raw[1]),
                    float(raw[2]),
                    float(raw[3]),
                    float(raw[4]),
                    float(raw[5] if len(raw) > 5 else 0),
                ])
            except (IndexError, TypeError, ValueError):
                continue
        return rows

    async def get_klines(self, symbol: str, interval: str = "15m", limit: int = 100) -> List[List[Any]]:
        return self.fetch_candles(symbol, interval, limit)

    async def cancel_order(self, asset: str, oid: str):
        inst_id = self._to_inst_id(asset)
        try:
            await self._retry(
                lambda: self._request(
                    "POST",
                    "/api/v5/trade/cancel-order",
                    json_body={"instId": inst_id, "ordId": str(oid)},
                )
            )
            return
        except Exception:
            pass
        try:
            await self._retry(
                lambda: self._request(
                    "POST",
                    "/api/v5/trade/cancel-algos",
                    json_body=[{"instId": inst_id, "algoId": str(oid)}],
                )
            )
        except Exception as e:
            logger.error(f"OKX cancel_order {oid} {asset}: {e}")

    async def cancel_all_orders(self, asset: str):
        try:
            target = self._normalize_asset(asset)
            pending = await self.get_open_orders()
            for o in pending:
                if self._normalize_asset(o.get("coin") or o.get("symbol") or "") != target:
                    continue
                oid = o.get("oid") or o.get("orderId")
                if oid:
                    await self.cancel_order(asset, str(oid))
        except Exception as e:
            logger.error(f"OKX cancel_all_orders {asset}: {e}")

    async def round_size(self, asset: str, amount: float) -> float:
        try:
            inst_id = self._to_inst_id(asset)
            info = self._get_instrument(inst_id)
            ct_val = float(info.get("ctVal") or 1)
            contracts = float(self._contracts_from_coins(asset, amount))
            return contracts * ct_val
        except Exception:
            return abs(float(amount or 0))
