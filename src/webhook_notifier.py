"""
Webhook notifier for sending trade alerts to external services (WhatsApp, Discord, Telegram).
"""

from __future__ import annotations

import html
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


def _esc(value: Any) -> str:
    """Escape text for Telegram HTML parse mode."""
    return html.escape("" if value is None else str(value), quote=False)


def _short(text: Any, limit: int = 140) -> str:
    s = " ".join(str(text or "").split())
    if len(s) <= limit:
        return s
    return s[: max(0, limit - 1)].rstrip() + "…"


def _action_label(action: Any) -> str:
    a = str(action or "").strip().lower()
    if a == "buy":
        return "OPEN LONG"
    if a == "sell":
        return "OPEN SHORT"
    if a == "hold":
        return "HOLD"
    return (a or "UNKNOWN").upper()


def _action_emoji(action: Any) -> str:
    a = str(action or "").strip().lower()
    if a == "buy":
        return "🟢"
    if a == "sell":
        return "🔴"
    if a == "hold":
        return "⚪"
    return "•"


class WebhookNotifier:
    """Sends trade notifications via generic webhook and/or native Telegram."""

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
    ):
        self.webhook_url = webhook_url
        self.enabled_webhook = bool(webhook_url)
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.enabled_telegram = bool(telegram_bot_token and telegram_chat_id)

        if self.enabled_webhook:
            logger.info(f"🔔 Webhook notifier enabled: {webhook_url}")
        else:
            logger.info("🔕 Webhook notifier disabled (no WEBHOOK_URL configured)")
        if self.enabled_telegram:
            logger.info("📨 Native Telegram notifier enabled")
        elif telegram_bot_token or telegram_chat_id:
            logger.warning(
                "⚠️ Native Telegram partially configured (need both TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)"
            )

    @staticmethod
    def _is_telegram_send_message_url(url: str) -> bool:
        lower = (url or "").lower()
        return "api.telegram.org" in lower and "/sendmessage" in lower

    def _format_telegram_message(self, event_type: str, data: Dict[str, Any]) -> str:
        """Create a structured Telegram HTML message."""
        event = (event_type or "EVENT").upper()
        if event == "ENTRY":
            return (
                f"🟢 <b>ENTRY</b>  {_esc(data.get('asset', ''))}\n"
                f"Side: <b>{_esc(data.get('side', ''))}</b>\n"
                f"Price: {_esc(data.get('price', ''))}\n"
                f"Size: {_esc(data.get('size', ''))}\n"
                f"Leverage: {_esc(data.get('leverage', ''))}x\n"
                f"Reason: {_esc(_short(data.get('reason', ''), 180))}"
            )
        if event == "EXIT":
            return (
                f"🔴 <b>EXIT</b>  {_esc(data.get('asset', ''))}\n"
                f"Side: <b>{_esc(data.get('side', ''))}</b>\n"
                f"Entry: {_esc(data.get('entry_price', ''))}\n"
                f"Exit: {_esc(data.get('exit_price', ''))}\n"
                f"PnL: {_esc(data.get('pnl_percent', ''))}%  /  ${_esc(data.get('pnl_usd', ''))}\n"
                f"Reason: {_esc(_short(data.get('reason', ''), 180))}"
            )
        if event == "PAIR_HUNTER":
            pairs = data.get("top_pairs") or []
            positions = data.get("current_positions") or []
            pair_lines = "\n".join(f"  • <code>{_esc(p)}</code>" for p in pairs) or "  • none"
            pos_lines = "\n".join(f"  • <code>{_esc(p)}</code>" for p in positions) or "  • none"
            return (
                f"🎯 <b>PAIR HUNTER</b>\n"
                f"<i>Watchlist for this cycle</i>\n\n"
                f"<b>Top pairs</b>\n{pair_lines}\n\n"
                f"<b>Open positions</b>\n{pos_lines}"
            )
        if event == "POSITION_UPDATE":
            return (
                f"📊 <b>POSITION UPDATE</b>\n"
                f"Open: <b>{_esc(data.get('count', 0))}</b>\n"
                f"Total PnL: ${_esc(data.get('total_pnl_usd', 0))} "
                f"({_esc(data.get('total_pnl_pct', 0))}%)"
            )
        if event in ("DECISION_SUMMARY", "AGENT_PROPOSAL"):
            return self._format_agent_proposal(data)
        if event in ("CYCLE_OUTCOME", "SYSTEM_DECISION"):
            return self._format_system_decision(data)
        if event == "MILESTONE":
            return (
                f"🏁 <b>MILESTONE</b>  {_esc(data.get('asset', ''))}\n"
                f"PnL: {_esc(data.get('pnl_percent', ''))}%  /  ${_esc(data.get('pnl_usd', ''))}\n"
                f"{_esc(data.get('milestone', ''))}"
            )
        if event == "ERROR":
            return (
                f"⚠️ <b>ERROR</b>  {_esc(data.get('error_type', ''))}\n"
                f"Asset: {_esc(data.get('asset', '') or '—')}\n"
                f"{_esc(_short(data.get('message', ''), 220))}"
            )
        return f"ℹ️ <b>{_esc(event)}</b>\n{_esc(_short(data, 400))}"

    def _format_agent_proposal(self, data: Dict[str, Any]) -> str:
        """LLM intent only — not yet filtered by risk / HTF / cooldowns."""
        proposals = data.get("proposals") or []
        analyzed = data.get("analyzed_assets") or []
        ts = _esc(_short(data.get("timestamp") or "", 32))
        lines = [
            "🧠 <b>AGENT PROPOSAL</b>",
            "<i>DeepSeek intent for this cycle (before system filters)</i>",
            "",
        ]
        if ts:
            lines.append(f"Time: <code>{ts}</code>")
        lines.append(f"Assets analyzed: <b>{len(analyzed) or len(proposals)}</b>")
        lines.append("")

        if not proposals:
            # Fallback for older callers that only send action_counts
            counts = data.get("action_counts") or {}
            if counts:
                pretty = " · ".join(f"{_esc(k)} {_esc(v)}" for k, v in counts.items())
                lines.append(f"Counts: {pretty}")
            else:
                lines.append("No proposals this cycle.")
            return "\n".join(lines)

        for p in proposals:
            asset = _esc(p.get("asset", "?"))
            action = p.get("action", "hold")
            label = _esc(_action_label(action))
            emoji = _action_emoji(action)
            alloc = p.get("allocation_usd")
            rationale = _esc(_short(p.get("rationale", ""), 120))
            lines.append(f"{emoji} <b>{asset}</b>  →  <b>{label}</b>")
            if action in ("buy", "sell") and alloc not in (None, "", 0, 0.0):
                try:
                    lines.append(f"   Margin: ${_esc(f'{float(alloc):.2f}')}")
                except (TypeError, ValueError):
                    pass
            if rationale:
                lines.append(f"   {_esc('↳')} {rationale}")
            lines.append("")

        # Compact tally with human labels
        tally = {"OPEN LONG": 0, "OPEN SHORT": 0, "HOLD": 0, "OTHER": 0}
        for p in proposals:
            lab = _action_label(p.get("action"))
            if lab in tally:
                tally[lab] += 1
            else:
                tally["OTHER"] += 1
        tally_bits = [f"{v} {k.lower()}" for k, v in tally.items() if v]
        lines.append("Summary: " + " · ".join(_esc(b) for b in tally_bits))
        lines.append("")
        lines.append("<i>Final fills appear next in SYSTEM DECISION (filters may block entries).</i>")
        return "\n".join(lines).rstrip()

    def _format_system_decision(self, data: Dict[str, Any]) -> str:
        """Post-filter outcomes — what the bot actually did."""
        outcomes = data.get("outcomes") or []
        lines = [
            "⚙️ <b>SYSTEM DECISION</b>",
            "<i>After risk / trend / cooldown filters</i>",
            "",
        ]
        if not outcomes:
            lines.append("No actionable outcomes this cycle.")
            return "\n".join(lines)

        filled = blocked = held = closed = skipped = 0
        for o in outcomes:
            asset = _esc(o.get("asset", "?"))
            status = str(o.get("final_status") or "").lower()
            proposed = _action_label(o.get("proposed_action"))
            detail = _esc(_short(o.get("detail", ""), 140))

            if status in ("filled", "executed", "opened"):
                filled += 1
                icon, title = "✅", "FILLED"
            elif status in ("blocked", "rejected", "paused"):
                blocked += 1
                icon, title = "🚫", "BLOCKED"
            elif status in ("closed", "exited"):
                closed += 1
                icon, title = "🏁", "CLOSED"
            elif status in ("held", "hold"):
                held += 1
                icon, title = "⚪", "HOLD"
            else:
                skipped += 1
                icon, title = "⏸️", status.upper() or "SKIPPED"

            lines.append(f"{icon} <b>{asset}</b>  ·  {title}")
            lines.append(f"   Agent wanted: <b>{_esc(proposed)}</b>")
            if detail:
                lines.append(f"   {_esc('↳')} {detail}")
            lines.append("")

        bits = []
        if filled:
            bits.append(f"{filled} filled")
        if blocked:
            bits.append(f"{blocked} blocked")
        if held:
            bits.append(f"{held} held")
        if closed:
            bits.append(f"{closed} closed")
        if skipped:
            bits.append(f"{skipped} skipped")
        lines.append("Totals: " + " · ".join(_esc(b) for b in bits))
        return "\n".join(lines).rstrip()

    async def _post_telegram_payload(self, url: str, text: str, chat_id: str) -> bool:
        payload = {
            "chat_id": str(chat_id),
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    return True
                body = await response.text()
                logger.warning(f"⚠️ Telegram failed: {response.status} - {body[:200]}")
                return False

    async def _send_webhook_notification(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Send event to generic webhook; if it's Telegram endpoint, send Telegram-compatible payload."""
        if not self.enabled_webhook or not self.webhook_url:
            return False

        try:
            if self._is_telegram_send_message_url(self.webhook_url):
                chat_id = self.telegram_chat_id or data.get("chat_id")
                if not chat_id:
                    logger.warning("⚠️ TELEGRAM_CHAT_ID is missing; cannot send to Telegram sendMessage URL")
                    return False
                ok = await self._post_telegram_payload(
                    self.webhook_url,
                    self._format_telegram_message(event_type, data),
                    str(chat_id),
                )
                if ok:
                    logger.debug(f"✅ Webhook sent: {event_type}")
                return ok

            payload = {
                "event": event_type,
                "timestamp": data.get("timestamp", ""),
                "data": data,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        logger.debug(f"✅ Webhook sent: {event_type}")
                        return True
                    body = await response.text()
                    logger.warning(f"⚠️ Webhook failed: {response.status} for {event_type} - {body[:200]}")
                    return False
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
            return False

    async def _send_telegram_notification(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Send event directly to Telegram Bot API using token + chat id."""
        if not self.enabled_telegram:
            return False
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        try:
            ok = await self._post_telegram_payload(
                url,
                self._format_telegram_message(event_type, data),
                str(self.telegram_chat_id),
            )
            if ok:
                logger.debug(f"✅ Telegram sent: {event_type}")
            return ok
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
            return False

    async def send_notification(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Send notification to all enabled channels."""
        webhook_ok = await self._send_webhook_notification(event_type, data)
        telegram_ok = await self._send_telegram_notification(event_type, data)
        return webhook_ok or telegram_ok

    async def notify_entry(
        self, asset: str, side: str, price: float, size: float, leverage: int, reason: str = ""
    ):
        await self.send_notification(
            "ENTRY",
            {
                "asset": asset,
                "side": side,
                "price": price,
                "size": size,
                "leverage": leverage,
                "reason": reason,
                "timestamp": str(datetime.now(timezone.utc)),
            },
        )

    async def notify_exit(
        self,
        asset: str,
        side: str,
        entry_price: float,
        exit_price: float,
        pnl_percent: float,
        pnl_usd: float,
        reason: str,
        size: float,
    ):
        await self.send_notification(
            "EXIT",
            {
                "asset": asset,
                "side": side,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl_percent": pnl_percent,
                "pnl_usd": pnl_usd,
                "reason": reason,
                "size": size,
                "timestamp": str(datetime.now(timezone.utc)),
            },
        )

    async def notify_pair_hunter(self, top_pairs: list, positions: list):
        await self.send_notification(
            "PAIR_HUNTER",
            {
                "top_pairs": top_pairs,
                "current_positions": positions,
                "timestamp": str(datetime.now(timezone.utc)),
            },
        )

    async def notify_agent_proposal(
        self,
        analyzed_assets: List[str],
        proposals: List[Dict[str, Any]],
        action_counts: Optional[Dict[str, int]] = None,
    ):
        """LLM intent bubble — clearly labeled as proposal, not a fill."""
        await self.send_notification(
            "AGENT_PROPOSAL",
            {
                "analyzed_assets": analyzed_assets,
                "proposals": proposals,
                "action_counts": action_counts or {},
                "decision_count": len(proposals),
                "timestamp": str(datetime.now(timezone.utc)),
            },
        )

    async def notify_system_decision(self, outcomes: List[Dict[str, Any]]):
        """Final post-filter outcomes for the cycle."""
        await self.send_notification(
            "SYSTEM_DECISION",
            {
                "outcomes": outcomes,
                "timestamp": str(datetime.now(timezone.utc)),
            },
        )

    async def notify_position_update(self, positions: list, total_pnl_usd: float, total_pnl_pct: float):
        await self.send_notification(
            "POSITION_UPDATE",
            {
                "positions": positions,
                "total_pnl_usd": total_pnl_usd,
                "total_pnl_pct": total_pnl_pct,
                "count": len(positions),
                "timestamp": str(datetime.now(timezone.utc)),
            },
        )

    async def notify_profit_milestone(
        self, asset: str, pnl_percent: float, pnl_usd: float, milestone: str
    ):
        await self.send_notification(
            "MILESTONE",
            {
                "asset": asset,
                "pnl_percent": pnl_percent,
                "pnl_usd": pnl_usd,
                "milestone": milestone,
                "timestamp": str(datetime.now(timezone.utc)),
            },
        )

    async def notify_error(self, error_type: str, message: str, asset: str = ""):
        await self.send_notification(
            "ERROR",
            {
                "error_type": error_type,
                "message": message,
                "asset": asset,
                "timestamp": str(datetime.now(timezone.utc)),
            },
        )
