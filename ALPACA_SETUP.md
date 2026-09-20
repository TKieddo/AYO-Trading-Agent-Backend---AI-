# Alpaca Setup (Stocks + Crypto)

Wire the AYO bot to Alpaca **paper** trading for US stocks and crypto.

## 1. Get API keys

1. Log in at [app.alpaca.markets](https://app.alpaca.markets/)
2. Open **Paper Trading**
3. **API Keys** → Generate
4. Copy **Key ID** and **Secret** (shown once)

Use **Trading API** keys — not Broker API.

## 2. `.env` settings

```bash
EXCHANGE=alpaca
ALPACA_API_KEY=your_key_id
ALPACA_API_SECRET=your_secret
ALPACA_PAPER=true

# Stocks + crypto the bot will trade
STOCK_ASSETS=AAPL TSLA NVDA MSFT
CRYPTO_ASSETS=BTC ETH SOL
INTERVAL=15m

# Alpaca is not crypto-futures leverage — keep this low
DEFAULT_LEVERAGE=1
ALPACA_LEVERAGE=1
MARGIN_PER_POSITION=100
POSITION_SIZING_MODE=margin
MAX_POSITIONS=4

# Keep exits on (your close-path fixes)
AGENT_MANAGE_EXITS=true
ENABLE_STOP_LOSS_ORDERS=true
TRADING_ENABLED=true

# Still required for the LLM
DEEPSEEK_API_KEY=your_deepseek_key
```

Optional: put everything in one list:

```bash
ASSETS=AAPL TSLA BTC ETH
```

## 3. Run

```bash
cd "AYO-Trading-Agent-Backend---AI--main"
# install deps if needed
poetry install   # or: pip install -e .
python -m src.main
```

You should see:

```text
✅ Using Alpaca (paper) for stocks + crypto
💰 Account Balance / Buying Power: $...
```

## 4. Notes

| Topic | Detail |
|--------|--------|
| Paper vs live | Keep `ALPACA_PAPER=true` until exits look solid |
| Leverage | Spot/margin buying power — not 10x perps |
| Market hours | US stocks: regular session; crypto: 24/7 on Alpaca |
| PDT | Live accounts under $25k have day-trade limits |
| Data | Stock bars use Alpaca IEX feed (free); crypto can use Alpaca or Binance public data |

## 5. Multi-exchange (optional)

To keep Binance/Aster for crypto futures and Alpaca for stocks:

```bash
MULTI_EXCHANGE_MODE=true
# set Binance/Aster keys AND Alpaca keys
STOCK_ASSETS=AAPL TSLA
CRYPTO_ASSETS=BTC ETH
```

Stocks route to Alpaca; crypto prefers Aster/Binance when configured.
