#!/usr/bin/env python3
"""Quick IG demo connectivity + optional tiny market order smoke test."""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


async def main():
    parser = argparse.ArgumentParser(description="IG demo smoke test")
    parser.add_argument("--trade", action="store_true", help="Place a tiny BUY then close (demo only)")
    parser.add_argument("--asset", default="EURUSD")
    args = parser.parse_args()

    from src.trading.ig_api import IGAPI
    ig = IGAPI()
    state = await ig.get_user_state()
    print("✅ Login OK")
    print(f"   balance/available: {state.get('balance')}")
    print(f"   equity: {state.get('total_value')}")
    print(f"   open positions: {len(state.get('positions') or [])}")
    print(f"   account: {state.get('ig_account')}")

    px = await ig.get_current_price(args.asset)
    print(f"✅ {args.asset} mid≈ {px}")

    if not args.trade:
        print("\nNo trade placed (pass --trade to open+close a tiny demo position).")
        return

    if not ig.demo:
        print("❌ Refusing --trade on LIVE. Set IG_DEMO=true.")
        return

    print(f"\nPlacing tiny BUY {args.asset} ...")
    # amount is converted via ig sizing; with IG_FIXED_SIZE this is ignored for size
    try:
        order = await ig.place_buy_order(args.asset, amount=1.0)
    except Exception as e:
        print("   open error:", e)
        return
    print("   open result:", order.get("dealReference") or order)
    conf = order.get("confirm") or {}
    if conf:
        print(
            f"   confirm: status={conf.get('dealStatus')} reason={conf.get('reason')} "
            f"dealId={conf.get('dealId')}"
        )
    await asyncio.sleep(2)
    state2 = await ig.get_user_state()
    print(f"   positions now: {len(state2.get('positions') or [])}")
    for p in state2.get("positions") or []:
        print(f"   - {p.get('symbol')} qty={p.get('quantity')} pnl={p.get('pnl')}")

    if not (state2.get("positions") or []):
        print("\nNo open position to close (deal likely rejected — check confirm above).")
        print("Done.")
        return

    print(f"Closing {args.asset} ...")
    try:
        close = await ig.place_sell_order(args.asset, amount=1.0, reduce_only=True)
        print("   close result:", close)
        for c in close.get("closed") or []:
            cref = c.get("dealReference")
            if cref:
                try:
                    cconf = ig._request("GET", f"/confirms/{cref}", version="1")
                    print(
                        f"   close confirm: status={cconf.get('dealStatus')} "
                        f"reason={cconf.get('reason')}"
                    )
                except Exception as e:
                    print("   close confirm error:", e)
    except Exception as e:
        print("   close error:", e)

    state3 = await ig.get_user_state()
    print(f"   positions after close: {len(state3.get('positions') or [])}")
    print("\nDone. Confirm in IG demo UI as well.")


if __name__ == "__main__":
    asyncio.run(main())
