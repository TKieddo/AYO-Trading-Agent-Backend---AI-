# Environment Variables for DigitalOcean Deployment

Copy these variables to your DigitalOcean App Platform or Dokploy environment variables section.

## Python Trading Agent Variables

```env
# DeepSeek API (REQUIRED)
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-reasoner
DEEPSEEK_MAX_TOKENS=20000

# Exchange Selection (choose ONE: Binance OR Aster)
EXCHANGE=binance

# Binance Futures API (if using Binance)
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
BINANCE_TESTNET=false
BINANCE_LEVERAGE=10

# OR Aster DEX API (if using Aster)
ASTER_USER_ADDRESS=your_aster_user_address
ASTER_SIGNER_ADDRESS=your_aster_signer_address
ASTER_PRIVATE_KEY=your_aster_private_key
ASTER_API_BASE=https://fapi.asterdex.com

# Trading Configuration (Can be changed via Dashboard Settings)
ASSETS=BTC ETH SOL BNB ZEC DOGE AVAX XLM XMR
INTERVAL=5m
STRATEGY=auto
MULTI_EXCHANGE_MODE=false

# Position Sizing
MARGIN_PER_POSITION=40.0
DEFAULT_LEVERAGE=30
POSITION_SIZING_MODE=margin
MAX_POSITIONS=5

# Per-Asset Leverage Overrides
ZEC_LEVERAGE=5
BTC_LEVERAGE=25
ETH_LEVERAGE=25
BNB_LEVERAGE=25
DOGE_LEVERAGE=25
SOL_LEVERAGE=25

# Risk Management
ENABLE_TRAILING_STOP=true
TRAILING_STOP_ACTIVATION_PCT=5.0
TRAILING_STOP_DISTANCE_PCT=3.0
MAX_POSITION_HOLD_HOURS=48.0
ENABLE_DRAWDOWN_PROTECTION=true
MAX_DRAWDOWN_FROM_PEAK_PCT=5.0

# Scalping Strategy
SCALPING_TP_PERCENT=5.0
SCALPING_SL_PERCENT=5.0
AUTO_STRATEGY_CACHE_MINUTES=0

# Alert Service
ALERT_SERVICE_ENABLED=true
ALERT_RISK_PER_TRADE=30.0
ALERT_CHECK_INTERVAL=5
ALERT_AGENT_ENDPOINT=http://localhost:5000/api/alert/signal
ALERT_ASSETS=ZEC,BTC,ETH,SOL,BNB
ALERT_TIMEFRAME=15m
BTC_TIMEFRAME=15m
ETH_TIMEFRAME=15m
SOL_TIMEFRAME=15m
BNB_TIMEFRAME=15m
ZEC_TIMEFRAME=5m

# API Server
API_HOST=0.0.0.0
API_PORT=3000
APP_PORT=3000
```

## Next.js Dashboard Variables

```env
# Supabase (REQUIRED for database)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Python Agent URL (update after deployment)
NEXT_PUBLIC_API_URL=https://trading-agent-xxxx.ondigitalocean.app
NEXT_PUBLIC_BASE_URL=https://dashboard-xxxx.ondigitalocean.app

# Node Environment
NODE_ENV=production
PORT=3001
```
