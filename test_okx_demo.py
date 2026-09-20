#!/usr/bin/env python3
"""OKX demo smoke test using Pair Hunter pairs (not hardcoded BTC/ETH/SOL)."""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv(override=True)


def _okx_swap_bases(okx) -> set:
    """Return set of base assets that have a USDT-SWAP on OKX."""
    try:
        data = okx._request(
            "GET",
            "/api/v5/public/instruments",
            params={"instType": "SWAP"},
            auth=False,
        )
    except Exception as e:
        print(f"⚠️  Could not list OKX instruments: {e}")
        return set()
    bases = set()
    for row in data if isinstance(data, list) else []:
        inst = (row.get("instId") or "").upper()
        if inst.endswith("-USDT-SWAP") and (row.get("state") or "").lower() == "live":
            bases.add(inst.replace("-USDT-SWAP", ""))
    return bases


async def main():
    parser = argparse.ArgumentParser(description="OKX demo smoke test (hunted pairs)")
    parser.add_argument("--trade", action="store_true", help="Place a tiny BUY then close (demo only)")
    parser.add_argument(
        "--asset",
        default="",
        help="Optional override asset. Default: first Pair Hunter result listed on OKX.",
    )
    parser.add_argument("--top-n", type=int, default=8)
    args = parser.parse_args()

    print("🔍 Pair Hunter scanning (medium-vol filter)...")
    from src.pair_hunter import get_best_pairs

    hunted = await get_best_pairs(
        exchange_client=None,
        top_n=args.top_n,
        min_volatility=float(os.getenv("PAIR_HUNTER_MIN_VOLATILITY", "1.5") or 1.5),
        use_enhanced=True,
    )
    if not hunted:
        print("❌ Pair Hunter returned no pairs — aborting (will not fall back to hardcoded list).")
        return

    print(f"🏆 Hunted pairs (Binance scan): {hunted}")

    from src.trading.okx_api import OKXAPI

    try:
        okx = OKXAPI()
    except Exception as e:
        print(f"❌ OKX login failed: {e}")
        print("   Fill OKX_API_KEY / OKX_API_SECRET / OKX_PASSPHRASE in .env (Demo Trading API).")
        print(f"   Set EXCHANGE=okx — hunted pairs ready: {hunted}")
        return

    okx_bases = _okx_swap_bases(okx)
    tradeable = [a for a in hunted if a.upper().replace("USDT", "") in okx_bases]
    skipped = [a for a in hunted if a.upper().replace("USDT", "") not in okx_bases]
    if skipped:
        print(f"⏭️  Not on OKX SWAP (skipped): {skipped}")
    if not tradeable and not args.asset:
        print("❌ No hunted pairs are listed as live USDT-SWAP on OKX.")
        return

    asset = (args.asset or tradeable[0]).upper().replace("USDT", "").replace("-", "")
    print(f"✅ Trading OKX-listed hunted pair: {asset}")

    state = await okx.get_user_state()
    print("✅ Login OK")
    print(f"   balance/available: {state.get('balance')}")
    print(f"   equity: {state.get('total_value')}")
    print(f"   open positions: {len(state.get('positions') or [])}")
    print(f"   account: {state.get('okx_account')}")

    px = await okx.get_current_price(asset)
    print(f"✅ {asset}-USDT-SWAP last≈ {px}")

    if not args.trade:
        print("\nNo trade placed (pass --trade to open+close on the hunted pair).")
        return

    if not okx.demo:
        print("❌ Refusing --trade on LIVE. Set OKX_DEMO=true.")
        return

    amount = 0.01 if asset in ("BTC",) else (0.1 if asset in ("ETH", "BCH", "LTC") else 1.0)
    print(f"\nPlacing tiny BUY {asset} amount≈{amount} (hunted) ...")
    try:
        order = await okx.place_buy_order(asset, amount=amount)
    except Exception as e:
        print("   open error:", e)
        return
    print("   open result:", order)
    await asyncio.sleep(2)
    state2 = await okx.get_user_state()
    print(f"   positions now: {len(state2.get('positions') or [])}")
    for p in state2.get("positions") or []:
        print(f"   - {p.get('symbol')} qty={p.get('quantity')} pnl={p.get('pnl')}")

    if not (state2.get("positions") or []):
        print("\nNo open position to close (check OKX demo UI / order reject).")
        return

    print(f"Closing {asset} ...")
    try:
        close = await okx.place_sell_order(asset, amount=amount, reduce_only=True)
        print("   close result:", close)
    except Exception as e:
        print("   close error:", e)

    state3 = await okx.get_user_state()
    print(f"   positions after close: {len(state3.get('positions') or [])}")
    print("\nDone. Confirm in OKX Demo Trading UI.")


if __name__ == "__main__":
    asyncio.run(main())
