"""Test script to execute a small trade on Pepperstone and verify it appears."""

import asyncio
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent))

from src.trading.pepperstone_api import PepperstoneAPI
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def test_trade():
    """Execute a small test trade and verify position."""
    
    print("=" * 60)
    print("PEPPERSTONE CTRADER TRADE TEST")
    print("=" * 60)
    print()
    
    try:
        # Initialize Pepperstone client
        pepperstone = PepperstoneAPI()
        environment = pepperstone.environment
        
        print(f"📍 Environment: {environment.upper()}")
        if environment == "demo":
            print(f"🔗 View on cTrader Demo: https://ct.pepperstone.com/")
        else:
            print(f"🔗 View on cTrader Live: https://ct.pepperstone.com/")
        print()
        
        # Get initial account state
        print("📊 Fetching account state...")
        state = await pepperstone.get_user_state()
        balance = state.get('balance', 0)
        total_value = state.get('total_value', 0)
        positions = state.get('positions', [])
        
        print(f"💰 Balance: ${balance:.2f}")
        print(f"💵 Total Value: ${total_value:.2f}")
        print(f"📈 Current Positions: {len(positions)}")
        
        if positions:
            print("\nCurrent Positions:")
            for pos in positions:
                coin = pos.get('coin', 'N/A')
                size = pos.get('quantity', 0)
                entry = pos.get('entryPrice', 0)
                pnl = pos.get('unrealized_pnl', 0)
                current_price = pos.get('current_price', 0)
                print(f"  • {coin}: Size={size:.2f}, Entry=${entry:.5f}, Current=${current_price:.5f}, PnL=${pnl:.4f}")
        print()
        
        # Check if we have enough balance
        if balance < 10:
            print("⚠️  WARNING: Balance is very low. You need at least $10-20 for a test trade.")
            print("   Make sure you have funds in your Pepperstone account.")
            if environment == "demo":
                print("   Demo accounts usually come with virtual funds.")
            return
        
        # Test parameters
        TEST_ASSET = "EURUSD"  # Major forex pair - you can change to GBPUSD, USDJPY, etc.
        TEST_SIZE_LOTS = 0.01  # 0.01 lots = micro lot (smallest size)
        
        print(f"🎯 Test Trade Parameters:")
        print(f"   Asset: {TEST_ASSET}")
        print(f"   Size: {TEST_SIZE_LOTS} lots (micro lot)")
        print(f"   Note: 1 lot = 100,000 units, 0.01 lots = 1,000 units")
        print()
        
        # Get current price
        print(f"📈 Fetching current price for {TEST_ASSET}...")
        current_price = await pepperstone.get_current_price(TEST_ASSET)
        if current_price <= 0:
            print(f"❌ Failed to get price for {TEST_ASSET}")
            return
        
        print(f"   Current {TEST_ASSET} Price: {current_price:.5f}")
        print()
        
        # Confirm
        print("⚠️  READY TO EXECUTE TEST TRADE")
        print(f"   This will place a BUY order for {TEST_SIZE_LOTS} lots of {TEST_ASSET}")
        print(f"   This is a very small position (micro lot)")
        if environment == "demo":
            print("   ✅ This is DEMO - no real money at risk")
        else:
            print("   ⚠️  This is LIVE trading - real money!")
        print()
        response = input("   Continue? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("❌ Trade cancelled.")
            return
        
        print()
        print("🚀 Executing BUY order...")
        
        # Place buy order
        try:
            # For forex, size is in lots
            order_result = await pepperstone.place_buy_order(TEST_ASSET, TEST_SIZE_LOTS)
            print("✅ Order placed successfully!")
            print()
            print("Order Result:")
            print(f"   {order_result}")
            print()
            
            # Extract order IDs if available
            oids = pepperstone.extract_oids(order_result)
            if oids:
                print(f"📝 Order IDs: {oids}")
            
            # Wait a moment for order to fill
            print()
            print("⏳ Waiting 3 seconds for order to fill...")
            await asyncio.sleep(3)
            
            # Check for new position
            print()
            print("🔍 Checking for new position...")
            new_state = await pepperstone.get_user_state()
            new_positions = new_state.get('positions', [])
            
            test_asset_position = None
            for pos in new_positions:
                if pos.get('coin') == TEST_ASSET or pos.get('symbol') == TEST_ASSET:
                    test_asset_position = pos
                    break
            
            if test_asset_position:
                print("✅ POSITION FOUND!")
                print()
                print(f"📊 {TEST_ASSET} Position Details:")
                print(f"   Symbol: {test_asset_position.get('coin')}")
                print(f"   Size: {test_asset_position.get('quantity', 0):.2f} lots")
                print(f"   Entry Price: {test_asset_position.get('entryPrice', 0):.5f}")
                print(f"   Current Price: {test_asset_position.get('current_price', 0):.5f}")
                print(f"   Unrealized PnL: ${test_asset_position.get('unrealized_pnl', 0):.4f}")
                print()
                print("=" * 60)
                print("✅ SUCCESS! Position is open and visible.")
                print()
                print(f"🌐 View on cTrader:")
                print(f"   https://ct.pepperstone.com/")
                print()
                print("💡 Tips:")
                print("   • The position should appear in your cTrader platform immediately")
                print("   • You can manually close it via the cTrader UI")
                print("   • Or let the agent manage it with TP/SL orders")
                print("=" * 60)
            else:
                print("⚠️  Position not found yet. It may still be processing.")
                print("   Check recent fills:")
                fills = await pepperstone.get_recent_fills(limit=5)
                if fills:
                    print("   Recent fills:")
                    for fill in fills[-3:]:
                        coin = fill.get('coin') or fill.get('asset', 'N/A')
                        side = "BUY" if fill.get('isBuy') else "SELL"
                        print(f"     • {side} {coin}: {fill.get('sz', 0)} @ {fill.get('px', 0)}")
                
        except Exception as e:
            print(f"❌ Error executing trade: {e}")
            import traceback
            traceback.print_exc()
            return
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print()
        print("💡 Make sure you have set in your .env file:")
        print("   • PEPPERSTONE_CLIENT_ID")
        print("   • PEPPERSTONE_CLIENT_SECRET")
        print("   • PEPPERSTONE_ACCOUNT_ID")
        print("   • PEPPERSTONE_ENVIRONMENT=demo (for testing)")
        print()
        print("   Get credentials from: cTrader Open API Portal")
        return
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print()
    asyncio.run(test_trade())
