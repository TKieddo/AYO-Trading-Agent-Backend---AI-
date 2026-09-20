# OKX Demo Setup (Crypto SWAP / Perps)

Wire AYO to **OKX Demo Trading** for crypto perpetuals.

## 1. Create demo API keys

1. Log in at [okx.com](https://www.okx.com/)
2. **Trade → Demo Trading**
3. **Personal Center → Demo Trading API → Create**
4. Copy **API Key**, **Secret Key**, and **Passphrase** (you set the passphrase)

Docs: [OKX API](https://www.okx.com/docs-v5/en/#overview-demo-trading-services)

Demo uses the same REST host with header `x-simulated-trading: 1` (the bot sets this when `OKX_DEMO=true`).

**Do not use a VPN to bypass geo blocks** — that can violate OKX terms. If the site/API works from your network, you’re fine.

## 2. `.env` settings

```bash
EXCHANGE=okx
OKX_DEMO=true
OKX_API_KEY=your_demo_api_key
OKX_API_SECRET=your_demo_secret
OKX_PASSPHRASE=your_passphrase

# Crypto the bot will trade (mapped to BTC-USDT-SWAP, etc.)
CRYPTO_ASSETS=BTC ETH SOL
ASSETS=BTC ETH SOL
INTERVAL=15m

OKX_LEVERAGE=10
DEFAULT_LEVERAGE=10
MARGIN_PER_POSITION=100
POSITION_SIZING_MODE=margin
MAX_POSITIONS=4

AGENT_MANAGE_EXITS=false
ENABLE_STOP_LOSS_ORDERS=true
TRADING_ENABLED=true

DEEPSEEK_API_KEY=your_deepseek_key

# Keep calmer hunter if enabled
PAIR_HUNTER_MIN_VOLATILITY=1.5
PAIR_HUNTER_IDEAL_VOLATILITY=3.0
PAIR_HUNTER_MAX_VOLATILITY=6.0
```

Optional:

```bash
OKX_TD_MODE=cross          # cross | isolated
OKX_POS_MODE=net_mode      # net_mode | long_short_mode
OKX_BASE_URL=https://www.okx.com
```

## 3. Smoke-test login (no full bot)

```bash
cd "AYO-Trading-Agent-Backend---AI--main"
.venv/bin/python test_okx_demo.py
# optional tiny open+close:
.venv/bin/python test_okx_demo.py --trade --asset BTC
```

## 4. Run the bot

```bash
.venv/bin/python -m src.main
```

Look for:

```text
✅ Using OKX (DEMO) for crypto SWAP
💰 Account Balance / Buying Power: ...
```

## 5. Notes

| Topic | Detail |
|--------|--------|
| Instrument | `BTC` → `BTC-USDT-SWAP` |
| Size | Coin qty converted via contract `ctVal` |
| TP/SL | Algo conditional orders + mechanical UI % |
| Live | Set `OKX_DEMO=false` and use **live** API keys only when ready |

## 6. Multi-exchange (optional)

```bash
MULTI_EXCHANGE_MODE=true
# OKX for crypto, IG for forex, etc.
FOREX_ASSETS=EURUSD GBPUSD
CRYPTO_ASSETS=BTC ETH SOL
```
