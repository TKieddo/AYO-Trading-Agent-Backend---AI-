"""IG Markets REST API client (demo/live CFDs: forex, indices, stock CFDs)."""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from src.config_loader import CONFIG

logger = logging.getLogger(__name__)

# Common demo epics (resolved via market search when possible).
DEFAULT_EPIC_HINTS = {
    "EURUSD": "CS.D.EURUSD.MINI.IP",
    "GBPUSD": "CS.D.GBPUSD.MINI.IP",
    "USDJPY": "CS.D.USDJPY.MINI.IP",
    "AUDUSD": "CS.D.AUDUSD.MINI.IP",
    "USDCAD": "CS.D.USDCAD.MINI.IP",
    "USDCHF": "CS.D.USDCHF.MINI.IP",
    # Inverted aliases still resolve to the standard IG quote (same epic).
    "CADUSD": "CS.D.USDCAD.MINI.IP",
    "CHFUSD": "CS.D.USDCHF.MINI.IP",
    "NZDUSD": "CS.D.NZDUSD.MINI.IP",
    "EURGBP": "CS.D.EURGBP.MINI.IP",
    "EURJPY": "CS.D.EURJPY.MINI.IP",
    "GBPJPY": "CS.D.GBPJPY.MINI.IP",
    # Gold/silver epics vary by account region; search falls back if these 404.
    "XAUUSD": "CS.D.USCGC.TODAY.IP",
    "GOLD": "CS.D.USCGC.TODAY.IP",
    "XAGUSD": "CS.D.USCSI.TODAY.IP",
    "SILVER": "CS.D.USCSI.TODAY.IP",
}


class IGAPI:
    """Client for IG demo/live CFD trading with the same interface as Binance/Alpaca."""

    def __init__(self):
        api_key = CONFIG.get("ig_api_key")
        username = CONFIG.get("ig_username")
        password = CONFIG.get("ig_password")
        demo = bool(CONFIG.get("ig_demo", True))

        if not api_key or not username or not password:
            raise ValueError(
                "IG_API_KEY, IG_USERNAME, and IG_PASSWORD must be set in .env "
                "(My IG → Settings → API keys; use demo login for paper)"
            )

        self.api_key = api_key
        self.username = username
        self.password = password
        self.demo = demo
        self.base = (
            CONFIG.get("ig_demo_url", "https://demo-api.ig.com/gateway/deal")
            if demo
            else CONFIG.get("ig_live_url", "https://api.ig.com/gateway/deal")
        )
        self.account_id = CONFIG.get("ig_account_id")  # optional preferred account
        self.currency = CONFIG.get("ig_currency", "USD")
        self.default_leverage = int(CONFIG.get("ig_leverage", CONFIG.get("default_leverage", 20)) or 20)
        self._cst: Optional[str] = None
        self._security_token: Optional[str] = None
        self._epic_cache: Dict[str, str] = {}
        self._deal_id_by_asset: Dict[str, str] = {}
        self._load_epic_overrides()

        self._login()
        bal = self._accounts_balance()
        logger.info(
            f"IG client initialized (demo={demo}, account={self.account_id}, "
            f"balance≈{bal}, leverage_hint={self.default_leverage}x)"
        )

    def _load_epic_overrides(self):
        raw = CONFIG.get("ig_epic_map") or ""
        # Format: EURUSD:CS.D.EURUSD.MINI.IP,GBPUSD:CS.D.GBPUSD.MINI.IP
        for part in raw.split(","):
            part = part.strip()
            if ":" in part:
                k, v = part.split(":", 1)
                self._epic_cache[k.strip().upper().replace("/", "")] = v.strip()

    def _encrypt_password(self) -> str:
        """RSA-encrypt password the same way as IG Labs sample apps (Java / JS).

        GET /session/encryptionKey → encrypt base64(password|timestamp) with PKCS1 v1.5.
        See: https://github.com/IG-Group/ig-webapi-java-sample
        """
        headers = {
            "X-IG-API-KEY": self.api_key,
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json; charset=UTF-8",
        }
        key_resp = requests.get(
            f"{self.base}/session/encryptionKey", headers=headers, timeout=30
        )
        if key_resp.status_code >= 400:
            raise RuntimeError(
                f"IG encryptionKey failed ({key_resp.status_code}): {key_resp.text[:300]}"
            )
        key_data = key_resp.json()
        encryption_key = key_data.get("encryptionKey")
        timestamp = key_data.get("timeStamp")
        if not encryption_key or timestamp is None:
            raise RuntimeError("IG encryptionKey response missing encryptionKey/timeStamp")

        # Match Java AuthenticationService.encryptPassword:
        # base64(password|timestamp) → RSA PKCS1 → base64
        plain = f"{self.password}|{timestamp}".encode("utf-8")
        to_encrypt = base64.b64encode(plain)
        public_key = serialization.load_der_public_key(base64.b64decode(encryption_key))
        encrypted = public_key.encrypt(to_encrypt, padding.PKCS1v15())
        return base64.b64encode(encrypted).decode("utf-8")

    def _login(self):
        # Same flow as IG Labs JS/Java samples: Version 2 + encryptedPassword
        headers = {
            "X-IG-API-KEY": self.api_key,
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json; charset=UTF-8",
            "Version": "2",
        }
        try:
            password = self._encrypt_password()
            body = {
                "identifier": self.username,
                "password": password,
                "encryptedPassword": True,
            }
            resp = requests.post(
                f"{self.base}/session", headers=headers, json=body, timeout=30
            )
        except Exception as enc_err:
            logger.warning(f"IG encrypted login unavailable ({enc_err}); trying plaintext")
            body = {
                "identifier": self.username,
                "password": self.password,
                "encryptedPassword": False,
            }
            resp = requests.post(
                f"{self.base}/session", headers=headers, json=body, timeout=30
            )

        if resp.status_code >= 400 and body.get("encryptedPassword"):
            # Fallback: some environments accept plaintext
            logger.warning(
                f"IG encrypted login failed ({resp.status_code}); retrying plaintext"
            )
            body = {
                "identifier": self.username,
                "password": self.password,
                "encryptedPassword": False,
            }
            resp = requests.post(
                f"{self.base}/session", headers=headers, json=body, timeout=30
            )

        if resp.status_code >= 400:
            raise RuntimeError(f"IG login failed ({resp.status_code}): {resp.text[:400]}")

        self._cst = resp.headers.get("CST")
        self._security_token = resp.headers.get("X-SECURITY-TOKEN")
        if not self._cst or not self._security_token:
            raise RuntimeError("IG login succeeded but CST / X-SECURITY-TOKEN missing")

        data = resp.json() if resp.content else {}
        accounts = data.get("accounts") or []
        current = data.get("currentAccountId")
        if not self.account_id:
            # Prefer CFD / spread demo account if present
            preferred = None
            for acc in accounts:
                acc_id = acc.get("accountId")
                acc_type = (acc.get("accountType") or "").upper()
                name = (acc.get("accountName") or "").lower()
                if acc.get("preferred") or "cfd" in name or acc_type in ("CFD", "SPREADBET"):
                    preferred = acc_id
                    break
            self.account_id = preferred or current or (accounts[0].get("accountId") if accounts else None)

        if self.account_id and self.account_id != current:
            try:
                self._request("PUT", "/session", json_body={"accountId": self.account_id}, version="1")
                logger.info(f"IG switched to account {self.account_id}")
            except Exception as e:
                logger.warning(f"Could not switch IG account to {self.account_id}: {e}")

        logger.info(f"IG session OK (demo={self.demo}, accounts={len(accounts)})")

    def _auth_headers(self, version: str = "2") -> Dict[str, str]:
        if not self._cst or not self._security_token:
            self._login()
        return {
            "X-IG-API-KEY": self.api_key,
            "CST": self._cst or "",
            "X-SECURITY-TOKEN": self._security_token or "",
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json; charset=UTF-8",
            "Version": str(version),
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
        version: str = "2",
        max_attempts: int = 3,
    ) -> Any:
        url = f"{self.base.rstrip('/')}{path}"
        last_err: Optional[Exception] = None
        for attempt in range(max_attempts):
            try:
                headers = self._auth_headers(version=version)
                # IG closes (DELETE with body) must be POST + _method=DELETE
                # (same as official Java sample HttpDeleteWithBody).
                req_method = method
                if method.upper() == "DELETE" and json_body is not None:
                    req_method = "POST"
                    headers["_method"] = "DELETE"
                resp = requests.request(
                    req_method, url, headers=headers, params=params, json=json_body, timeout=30
                )
                if resp.status_code in (401, 403) and attempt < max_attempts - 1:
                    logger.warning("IG auth expired — re-login")
                    self._login()
                    continue
                if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_attempts - 1:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                if resp.status_code >= 400:
                    raise RuntimeError(f"IG {method} {path} failed ({resp.status_code}): {resp.text[:500]}")
                if resp.status_code == 204 or not resp.content:
                    return {}
                return resp.json()
            except Exception as e:
                last_err = e
                if attempt < max_attempts - 1 and "failed (" not in str(e):
                    time.sleep(0.4 * (2 ** attempt))
                    continue
                raise
        raise last_err or RuntimeError("IG request failed")

    async def _retry(self, fn, *args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)

    def _normalize_asset(self, asset: str) -> str:
        a = (asset or "").strip().upper().replace("/", "").replace("_", "").replace("-", "")
        return a

    def resolve_epic(self, asset: str) -> str:
        key = self._normalize_asset(asset)
        if key in self._epic_cache:
            return self._epic_cache[key]

        # Prefer live market search first for metals / odd aliases; hints are regional.
        search_first = key in ("XAUUSD", "XAGUSD", "GOLD", "SILVER", "CADUSD", "CHFUSD")
        if not search_first and key in DEFAULT_EPIC_HINTS:
            self._epic_cache[key] = DEFAULT_EPIC_HINTS[key]
            return self._epic_cache[key]

        # Search IG markets
        try:
            search_term = (
                "Gold" if key in ("XAUUSD", "GOLD") else
                "Silver" if key in ("XAGUSD", "SILVER") else
                asset.replace("/", "")
            )
            data = self._request("GET", "/markets", params={"searchTerm": search_term}, version="1")
            markets = data.get("markets") or []
            # Prefer FX / CFD mini epics
            ranked = []
            for m in markets:
                epic = m.get("epic") or ""
                name = (m.get("instrumentName") or "").upper()
                itype = (m.get("instrumentType") or "").upper()
                score = 0
                if key in epic.replace(".", "").upper() or key in name.replace("/", "").replace(" ", ""):
                    score += 5
                if key in ("XAUUSD", "GOLD") and "GOLD" in name:
                    score += 6
                if key in ("XAGUSD", "SILVER") and "SILVER" in name:
                    score += 6
                if "MINI" in epic.upper() or "TODAY" in epic.upper():
                    score += 3
                if itype in ("CURRENCIES", "FX", "SHARES", "INDICES", "COMMODITIES"):
                    score += 2
                if m.get("marketStatus") == "TRADEABLE":
                    score += 2
                ranked.append((score, epic, m))
            ranked.sort(key=lambda x: x[0], reverse=True)
            if ranked and ranked[0][0] > 0 and ranked[0][1]:
                epic = ranked[0][1]
                self._epic_cache[key] = epic
                logger.info(f"IG resolved {asset} -> {epic}")
                return epic
        except Exception as e:
            logger.warning(f"IG market search failed for {asset}: {e}")

        if key in DEFAULT_EPIC_HINTS:
            self._epic_cache[key] = DEFAULT_EPIC_HINTS[key]
            return self._epic_cache[key]

        raise ValueError(
            f"Could not resolve IG epic for {asset}. "
            f"Set IG_EPIC_MAP e.g. {key}:CS.D.{key}.MINI.IP"
        )

    def _accounts_balance(self) -> float:
        try:
            data = self._request("GET", "/accounts", version="1")
            for acc in data.get("accounts") or []:
                if not self.account_id or acc.get("accountId") == self.account_id:
                    bal = acc.get("balance") or {}
                    return float(bal.get("available") or bal.get("balance") or 0)
        except Exception:
            pass
        return 0.0

    def _market_snapshot(self, epic: str) -> Dict[str, Any]:
        data = self._request("GET", f"/markets/{epic}", version="3")
        return data if isinstance(data, dict) else {}

    def _mid_price(self, snapshot: Dict[str, Any]) -> float:
        instrument = snapshot.get("instrument") or {}
        snapshot_node = snapshot.get("snapshot") or {}
        for key in ("bid", "offer", "netChange"):
            pass
        bid = snapshot_node.get("bid")
        offer = snapshot_node.get("offer")
        try:
            if bid is not None and offer is not None:
                return (float(bid) + float(offer)) / 2.0
            if bid is not None:
                return float(bid)
            if offer is not None:
                return float(offer)
        except (TypeError, ValueError):
            pass
        return float(instrument.get("valueOfOnePip") or 0) or 0.0

    def _to_ig_size(self, asset: str, amount: float, price: float) -> float:
        """Convert bot quantity (margin*lev/price style) into IG contract size."""
        qty = abs(float(amount or 0))
        px = float(price or 0) or 1.0
        notional = qty * px
        # Configurable knobs
        divisor = float(CONFIG.get("ig_size_divisor", 5000) or 5000)
        min_size = float(CONFIG.get("ig_min_size", 0.5) or 0.5)
        max_size = float(CONFIG.get("ig_max_size", 25) or 25)
        fixed = CONFIG.get("ig_fixed_size")
        if fixed is not None and str(fixed).strip() != "":
            try:
                return float(fixed)
            except (TypeError, ValueError):
                pass
        size = round(max(min_size, min(max_size, notional / divisor)), 2)
        return size

    async def set_leverage(self, asset: str, leverage: int):
        logger.info(
            f"IG set_leverage({asset}, {leverage}x): ignored "
            "(IG CFD leverage is account/product defined)"
        )

    async def get_current_price(self, asset: str) -> float:
        try:
            epic = self.resolve_epic(asset)
            snap = await self._retry(lambda: self._market_snapshot(epic))
            return self._mid_price(snap)
        except Exception as e:
            logger.error(f"IG price error for {asset}: {e}")
            return 0.0

    async def place_buy_order(
        self,
        asset: str,
        amount: float,
        leverage: Optional[int] = None,
        slippage: float = 0.01,
        reduce_only: bool = False,
    ):
        _ = leverage, slippage
        if reduce_only:
            return await self._close_direction(asset, close_long=False, amount=amount)
        return await self._open_position(asset, direction="BUY", amount=amount)

    async def place_sell_order(
        self,
        asset: str,
        amount: float,
        leverage: Optional[int] = None,
        slippage: float = 0.01,
        reduce_only: bool = False,
    ):
        _ = leverage, slippage
        if reduce_only:
            return await self._close_direction(asset, close_long=True, amount=amount)
        return await self._open_position(asset, direction="SELL", amount=amount)

    async def _open_position(self, asset: str, direction: str, amount: float) -> Dict[str, Any]:
        epic = self.resolve_epic(asset)
        snap = await self._retry(lambda: self._market_snapshot(epic))
        price = self._mid_price(snap)
        size = self._to_ig_size(asset, amount, price)
        status = ((snap.get("snapshot") or {}).get("marketStatus") or "").upper()
        if status and status not in ("TRADEABLE",):
            logger.warning(f"IG {asset} marketStatus={status} (opens may reject until TRADEABLE)")

        currencies = (snap.get("instrument") or {}).get("currencies") or []
        currency = self.currency
        if currencies:
            currency = currencies[0].get("code") or currency

        # Prefer MARKET; if preference says not available, send LIMIT at offer/bid
        rules = snap.get("dealingRules") or {}
        mkt_pref = (rules.get("marketOrderPreference") or "").upper()
        snapshot = snap.get("snapshot") or {}
        order_type = "MARKET"
        level = None
        if "NOT_AVAILABLE" in mkt_pref:
            order_type = "LIMIT"
            if direction == "BUY":
                level = snapshot.get("offer") or price
            else:
                level = snapshot.get("bid") or price

        body: Dict[str, Any] = {
            "epic": epic,
            "expiry": "-",
            "direction": direction,
            "size": size,
            "orderType": order_type,
            "currencyCode": currency,
            "forceOpen": True,
            "guaranteedStop": False,
        }
        if level is not None:
            body["level"] = float(level)

        result = await self._retry(
            lambda: self._request("POST", "/positions/otc", json_body=body, version="2")
        )
        deal_ref = result.get("dealReference")
        logger.info(
            f"IG {direction} {asset} ({epic}) size={size} orderType={order_type} ref={deal_ref}"
        )
        if deal_ref:
            # Poll confirm — deals are async
            conf: Dict[str, Any] = {}
            for _ in range(8):
                try:
                    conf = await self._retry(
                        lambda: self._request("GET", f"/confirms/{deal_ref}", version="1")
                    )
                    if conf.get("dealStatus") or conf.get("dealId"):
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.4)
            result["confirm"] = conf
            deal_id = conf.get("dealId")
            deal_status = (conf.get("dealStatus") or "").upper()
            reason = conf.get("reason")
            if deal_id:
                self._deal_id_by_asset[self._normalize_asset(asset)] = str(deal_id)
            if deal_status and deal_status not in ("ACCEPTED", "OPEN"):
                raise RuntimeError(
                    f"IG deal rejected: status={deal_status} reason={reason} "
                    f"marketStatus={status} confirm={conf}"
                )
        return result

    async def _close_direction(self, asset: str, close_long: bool, amount: float) -> Dict[str, Any]:
        """Close existing position(s) for asset. close_long=True means flatten a BUY/long."""
        positions = await self._retry(lambda: self._request("GET", "/positions", version="2"))
        epic = self.resolve_epic(asset)
        closed = []
        for pos_wrap in positions.get("positions") or []:
            pos = pos_wrap.get("position") or {}
            mkt = pos_wrap.get("market") or {}
            pos_epic = mkt.get("epic") or ""
            if pos_epic != epic:
                continue
            direction = (pos.get("direction") or "").upper()
            is_long = direction == "BUY"
            if close_long and not is_long:
                continue
            if not close_long and is_long:
                continue
            size = float(pos.get("size") or 0)
            deal_id = pos.get("dealId")
            if size <= 0 or not deal_id:
                continue
            close_dir = "SELL" if is_long else "BUY"
            body = {
                "dealId": deal_id,
                "direction": close_dir,
                "size": size,
                "orderType": "MARKET",
            }
            res = await self._retry(
                lambda b=body: self._request("DELETE", "/positions/otc", json_body=b, version="1")
            )
            closed.append(res)
            logger.info(f"IG closed {asset} dealId={deal_id} via {close_dir} size={size}")
        if not closed:
            # Fallback: try cached deal id
            deal_id = self._deal_id_by_asset.get(self._normalize_asset(asset))
            if deal_id:
                close_dir = "SELL" if close_long else "BUY"
                price = await self.get_current_price(asset)
                size = self._to_ig_size(asset, amount, price)
                body = {
                    "dealId": deal_id,
                    "direction": close_dir,
                    "size": size,
                    "orderType": "MARKET",
                }
                res = await self._retry(
                    lambda: self._request("DELETE", "/positions/otc", json_body=body, version="1")
                )
                closed.append(res)
        if not closed:
            raise RuntimeError(f"No IG position found to close for {asset}")
        return {"closed": closed}

    async def place_take_profit(self, asset: str, is_long: bool, quantity: float, tp_price: float):
        """Attach/update limit (TP) via position update when possible; else working order."""
        return await self._update_stops_limits(asset, is_long, quantity, limit_level=tp_price)

    async def place_stop_loss(self, asset: str, is_long: bool, quantity: float, sl_price: float):
        return await self._update_stops_limits(asset, is_long, quantity, stop_level=sl_price)

    async def _update_stops_limits(
        self,
        asset: str,
        is_long: bool,
        quantity: float,
        stop_level: Optional[float] = None,
        limit_level: Optional[float] = None,
    ) -> Dict[str, Any]:
        _ = quantity
        positions = await self._retry(lambda: self._request("GET", "/positions", version="2"))
        epic = self.resolve_epic(asset)
        for pos_wrap in positions.get("positions") or []:
            pos = pos_wrap.get("position") or {}
            mkt = pos_wrap.get("market") or {}
            if mkt.get("epic") != epic:
                continue
            direction = (pos.get("direction") or "").upper()
            if is_long and direction != "BUY":
                continue
            if not is_long and direction != "SELL":
                continue
            deal_id = pos.get("dealId")
            body: Dict[str, Any] = {}
            if stop_level is not None:
                body["stopLevel"] = float(stop_level)
            if limit_level is not None:
                body["limitLevel"] = float(limit_level)
            if not body or not deal_id:
                continue
            try:
                res = await self._retry(
                    lambda: self._request("PUT", f"/positions/otc/{deal_id}", json_body=body, version="2")
                )
                logger.info(f"IG updated stops/limits on {asset} dealId={deal_id}: {body}")
                return {"id": deal_id, "dealId": deal_id, **(res or {}), **body}
            except Exception as e:
                logger.warning(f"IG position update failed, trying working order: {e}")

        # Fallback: working order at level
        epic = self.resolve_epic(asset)
        price = await self.get_current_price(asset)
        size = self._to_ig_size(asset, quantity or 1, price)
        level = limit_level if limit_level is not None else stop_level
        direction = "SELL" if is_long else "BUY"
        order_type = "LIMIT" if limit_level is not None else "STOP"
        body = {
            "epic": epic,
            "expiry": "-",
            "direction": direction,
            "size": size,
            "level": float(level),
            "type": order_type,
            "currencyCode": self.currency,
            "timeInForce": "GOOD_TILL_CANCELLED",
            "guaranteedStop": False,
        }
        res = await self._retry(
            lambda: self._request("POST", "/workingorders/otc", json_body=body, version="2")
        )
        logger.info(f"IG working {order_type} {direction} {asset} @ {level}")
        return res

    def extract_oids(self, order_result: Dict) -> List[str]:
        if not order_result:
            return []
        for key in ("dealId", "dealReference", "id"):
            if order_result.get(key):
                return [str(order_result[key])]
        if order_result.get("confirm", {}).get("dealId"):
            return [str(order_result["confirm"]["dealId"])]
        closed = order_result.get("closed")
        if isinstance(closed, list) and closed:
            ref = closed[0].get("dealReference") or closed[0].get("dealId")
            if ref:
                return [str(ref)]
        return []

    async def get_user_state(self) -> Dict[str, Any]:
        try:
            accounts = await self._retry(lambda: self._request("GET", "/accounts", version="1"))
            positions_raw = await self._retry(lambda: self._request("GET", "/positions", version="2"))

            cash = 0.0
            equity = 0.0
            for acc in accounts.get("accounts") or []:
                if self.account_id and acc.get("accountId") != self.account_id:
                    continue
                bal = acc.get("balance") or {}
                cash = float(bal.get("available") or 0)
                equity = float(bal.get("balance") or cash)
                break

            enriched = []
            for pos_wrap in positions_raw.get("positions") or []:
                pos = pos_wrap.get("position") or {}
                mkt = pos_wrap.get("market") or {}
                epic = mkt.get("epic") or ""
                direction = (pos.get("direction") or "").upper()
                size = float(pos.get("size") or 0)
                if size <= 0:
                    continue
                entry = float(pos.get("openLevel") or 0)
                bid = mkt.get("bid")
                offer = mkt.get("offer")
                try:
                    current = (float(bid) + float(offer)) / 2.0 if bid is not None and offer is not None else float(bid or offer or entry)
                except (TypeError, ValueError):
                    current = entry
                upl = float(pos.get("upl") or 0)
                # Approximate ROI on margin: IG doesn't always give margin per position cleanly
                margin = abs(float(pos.get("contractSize") or 0) * size * entry / max(self.default_leverage, 1))
                if margin <= 0:
                    margin = abs(size * entry) / max(self.default_leverage, 1)
                roi = (upl / margin * 100.0) if margin > 0 else 0.0
                signed = size if direction == "BUY" else -size
                # Human asset name
                asset = None
                for k, v in {**DEFAULT_EPIC_HINTS, **self._epic_cache}.items():
                    if v == epic:
                        asset = k
                        break
                if not asset:
                    name = (mkt.get("instrumentName") or epic).upper().replace("/", "")
                    asset = name.replace(" ", "")[:12] or epic
                self._deal_id_by_asset[self._normalize_asset(asset)] = str(pos.get("dealId") or "")

                enriched.append({
                    "coin": asset,
                    "symbol": asset,
                    "szi": signed,
                    "quantity": signed,
                    "entryPx": entry,
                    "entry_price": entry,
                    "entryPrice": entry,
                    "markPrice": current,
                    "current_price": current,
                    "pnl": upl,
                    "unrealized_pnl": upl,
                    "unRealizedProfit": upl,
                    "roiPercent": roi,
                    "roi": roi,
                    "notional": abs(size * current),
                    "initialMargin": margin,
                    "positionInitialMargin": margin,
                    "initial_margin": margin,
                    "leverage": float(self.default_leverage),
                    "liquidationPx": None,
                    "ig_epic": epic,
                    "ig_deal_id": pos.get("dealId"),
                })

            return {
                "balance": cash,
                "total_value": equity,
                "positions": enriched,
                "asset_balances": [{
                    "asset": self.currency,
                    "walletBalance": equity,
                    "availableBalance": cash,
                    "crossWalletBalance": equity,
                    "crossUnPnl": sum(p.get("pnl", 0) for p in enriched),
                    "positionValue": equity,
                }],
                "ig_account": {"account_id": self.account_id, "demo": self.demo},
            }
        except Exception as e:
            logger.error(f"IG get_user_state error: {e}", exc_info=True)
            return {"balance": 0, "total_value": 0, "positions": [], "asset_balances": []}

    async def get_open_orders(self) -> List[Dict]:
        try:
            data = await self._retry(lambda: self._request("GET", "/workingorders", version="2"))
            out = []
            for wrap in data.get("workingOrders") or []:
                wo = wrap.get("workingOrderData") or {}
                mkt = wrap.get("marketData") or {}
                epic = wo.get("epic") or mkt.get("epic") or ""
                asset = epic
                for k, v in {**DEFAULT_EPIC_HINTS, **self._epic_cache}.items():
                    if v == epic:
                        asset = k
                        break
                otype = (wo.get("orderType") or "").upper()
                mapped = "TAKE_PROFIT" if otype == "LIMIT" else ("STOP" if "STOP" in otype else otype)
                level = float(wo.get("orderLevel") or wo.get("level") or 0)
                out.append({
                    "coin": asset,
                    "asset": asset,
                    "symbol": asset,
                    "oid": str(wo.get("dealId") or ""),
                    "isBuy": (wo.get("direction") or "").upper() == "BUY",
                    "sz": float(wo.get("orderSize") or wo.get("size") or 0),
                    "px": level,
                    "triggerPx": level,
                    "orderType": mapped,
                    "type": mapped,
                })
            return out
        except Exception as e:
            logger.error(f"IG get_open_orders error: {e}")
            return []

    async def get_recent_fills(self, limit: int = 50) -> List[Dict]:
        try:
            # Transaction history — best-effort
            data = await self._retry(
                lambda: self._request(
                    "GET",
                    "/history/transactions",
                    params={"type": "ALL_DEAL", "pageSize": min(limit, 50)},
                    version="2",
                )
            )
            fills = []
            for t in data.get("transactions") or []:
                fills.append({
                    "coin": t.get("instrumentName") or t.get("marketName"),
                    "asset": t.get("instrumentName"),
                    "symbol": t.get("instrumentName"),
                    "side": t.get("transactionType"),
                    "sz": float(t.get("size") or 0) if str(t.get("size", "")).replace(".", "", 1).isdigit() else 0,
                    "size": 0,
                    "px": float(t.get("openLevel") or t.get("closeLevel") or 0 or 0),
                    "price": float(t.get("openLevel") or 0 or 0),
                    "id": t.get("reference"),
                })
            return fills[:limit]
        except Exception as e:
            logger.debug(f"IG get_recent_fills: {e}")
            return []

    async def cancel_order(self, asset: str, oid: str):
        await self._retry(
            lambda: self._request("DELETE", f"/workingorders/otc/{oid}", version="2")
        )
        logger.info(f"IG cancelled working order {oid} ({asset})")

    async def cancel_all_orders(self, asset: str):
        orders = await self.get_open_orders()
        key = self._normalize_asset(asset)
        for o in orders:
            if self._normalize_asset(str(o.get("coin") or "")) == key or key in str(o.get("coin") or "").upper():
                try:
                    await self.cancel_order(asset, o.get("oid"))
                except Exception as e:
                    logger.warning(f"IG cancel failed for {o.get('oid')}: {e}")

    async def round_size(self, asset: str, amount: float) -> float:
        price = await self.get_current_price(asset)
        return self._to_ig_size(asset, amount, price)

    async def get_open_interest(self, asset: str) -> Optional[float]:
        return None

    async def get_funding_rate(self, asset: str) -> Optional[float]:
        return None

    def fetch_price_history(self, asset: str, resolution: str = "MINUTE_15", num_points: int = 100) -> List[Dict]:
        """Sync helper for indicators (OHLC from IG)."""
        epic = self.resolve_epic(asset)
        # GET /prices/{epic}/{resolution}/{numPoints}
        data = self._request("GET", f"/prices/{epic}/{resolution}/{int(num_points)}", version="3")
        return data.get("prices") or []
