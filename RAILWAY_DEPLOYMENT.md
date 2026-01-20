# 🚂 Railway Deployment Guide

Complete guide to deploy your Python trading agent to Railway.

## 📋 Prerequisites

- Railway account ([Sign up here](https://railway.app))
- GitHub repository with your code
- API keys ready (DeepSeek, Binance/Aster)

---

## 🚀 Step-by-Step Deployment

### Step 1: Create New Project on Railway

1. Go to: https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `AYO-Trading-Agent-Backend---AI-`
5. Railway will detect it's a Python project

### Step 2: Configure Service

Railway should auto-detect your Python project. If not:

1. Click on your service
2. Go to **Settings** tab
3. Set:
   - **Root Directory:** `/` (root)
   - **Build Command:** `pip install poetry && poetry install --no-interaction --no-ansi --no-root`
   - **Start Command:** `poetry run python -m src.main`
   - **Port:** `3000` (or leave as `PORT` env var)

### Step 3: Add Environment Variables (CRITICAL!)

This is the most important step! The agent **requires** these variables to start.

1. In Railway dashboard, go to your service
2. Click **"Variables"** tab
3. Click **"New Variable"** for each one below

#### Required Variables (Must Have):

```env
# DeepSeek API (REQUIRED - agent won't start without this!)
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-reasoner
DEEPSEEK_MAX_TOKENS=20000

# Exchange Selection (choose ONE: Binance OR Aster)
EXCHANGE=binance

# Binance Futures API (if using Binance - REQUIRED if EXCHANGE=binance)
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
BINANCE_TESTNET=false
BINANCE_LEVERAGE=10

# OR Aster DEX API (if using Aster - REQUIRED if EXCHANGE=aster)
ASTER_USER_ADDRESS=your_aster_user_address
ASTER_SIGNER_ADDRESS=your_aster_signer_address
ASTER_PRIVATE_KEY=your_aster_private_key
ASTER_API_BASE=https://fapi.asterdex.com
```

#### Optional but Recommended Variables:

```env
# TAAPI API (OPTIONAL - for technical indicators, replaced by TA-Lib + Binance)
TAAPI_API_KEY=your_taapi_key_here

# Supabase (OPTIONAL - for trade syncing to database)
# Only needed if you want trades automatically saved to Supabase
# NOTE: Dashboard (Vercel) needs Supabase for settings page, but agent doesn't need it directly
# Agent fetches settings from dashboard API, which reads from Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
# OR use SUPABASE_SERVICE_KEY (recommended for server-side, bypasses RLS)
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Trading Configuration (can be changed via dashboard later)
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

# API Server
API_HOST=0.0.0.0
API_PORT=3000
APP_PORT=3000
PORT=3000
```

**Note:** Railway automatically sets `PORT` environment variable. Your agent will use it automatically.

### Step 4: Deploy

1. After adding all environment variables, Railway will automatically redeploy
2. Wait 2-5 minutes for the build to complete
3. Check the **"Deployments"** tab for build logs

### Step 5: Get Your Agent URL

1. Go to **Settings** tab
2. Under **"Networking"**, you'll see your public URL:
   - Example: `https://your-app-name.up.railway.app`
3. Copy this URL - you'll need it for your Vercel dashboard

---

## 🔧 Configuration Tips

### Using Railway's Environment Variables UI

Railway makes it easy to add variables:

1. **Bulk Import:** Click **"Raw Editor"** to paste multiple variables at once
2. **Reference Variables:** Use `${{OTHER_VAR}}` to reference other variables
3. **Environment-Specific:** Set different values for Production vs Preview

### Port Configuration

Railway automatically sets `PORT` environment variable. Your agent's `config_loader.py` will:
1. First check `PORT` (Railway sets this)
2. Fall back to `APP_PORT` or `API_PORT`
3. Default to `3000` if none set

**You don't need to manually set PORT** - Railway handles it!

---

## 🧪 Testing Your Deployment

### 1. Check Build Logs

In Railway dashboard → **Deployments** → Click latest deployment → **View Logs**

Look for:
- ✅ `🌐 HTTP API server started on 0.0.0.0:3000`
- ✅ No `RuntimeError: Missing required environment variable` errors

### 2. Test Agent Status

Once deployed, test the status endpoint:

```bash
curl https://your-app-name.up.railway.app/status
```

Should return JSON with agent status.

### 3. Test from Vercel Dashboard

1. Go to Vercel dashboard
2. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-app-name.up.railway.app`
3. Redeploy Vercel
4. Check connection status in dashboard

---

## 🆘 Troubleshooting

### Error: "Missing required environment variable: DEEPSEEK_API_KEY"

**Solution:**
1. Go to Railway → Your Service → **Variables** tab
2. Add `DEEPSEEK_API_KEY` with your actual API key
3. Railway will auto-redeploy

### Error: "Missing required environment variable: BINANCE_API_KEY"

**Solution:**
- If using Binance: Add `BINANCE_API_KEY` and `BINANCE_API_SECRET`
- If using Aster: Add `ASTER_USER_ADDRESS`, `ASTER_SIGNER_ADDRESS`, `ASTER_PRIVATE_KEY`
- Make sure `EXCHANGE=binance` or `EXCHANGE=aster` is set

### Build Fails: "poetry: command not found"

**Solution:**
- Railway should auto-install Poetry, but if not:
- Update build command: `pip install poetry && poetry install --no-interaction --no-ansi --no-root`

### Agent Starts But Can't Connect from Vercel

**Solution:**
1. Check Railway logs - agent should show: `HTTP API server started`
2. Test directly: `curl https://your-railway-url/status`
3. Verify CORS is working (should be automatic)
4. Check Vercel's `NEXT_PUBLIC_API_URL` is correct

### Port Issues

**Solution:**
- Railway sets `PORT` automatically - don't override it
- Your agent will use `PORT` if set, otherwise falls back to `API_PORT` or `3000`
- Check Railway logs to see which port it's using

---

## 📝 Quick Checklist

- [ ] Railway project created
- [ ] GitHub repo connected
- [ ] Service configured (build/start commands)
- [ ] **`DEEPSEEK_API_KEY` added** (REQUIRED)
- [ ] **Exchange credentials added** (Binance OR Aster - REQUIRED)
- [ ] Trading configuration variables added (optional but recommended)
- [ ] Deployment successful (check logs)
- [ ] Agent URL copied
- [ ] Tested `/status` endpoint
- [ ] Updated Vercel with agent URL

---

## 💰 Railway Pricing

- **Hobby Plan:** $5/month (512MB RAM, 1GB storage)
- **Pro Plan:** $20/month (8GB RAM, 100GB storage)
- **Free Trial:** $5 credit to start

**Recommended:** Hobby plan is sufficient for trading agent.

---

## 🔄 Updating Your Deployment

### Update Code:
1. Push to GitHub
2. Railway auto-deploys (if enabled)
3. Or manually click **"Redeploy"** in Railway dashboard

### Update Environment Variables:
1. Go to **Variables** tab
2. Edit or add variables
3. Railway auto-redeploys

---

## 🎉 You're Live!

Your trading agent is now running 24/7 on Railway! 

- **Monitor:** Railway dashboard → Logs
- **Update:** Push to GitHub → Auto-deploys
- **Settings:** Change via Vercel dashboard (if using Supabase)

---

## 📚 Additional Resources

- **Environment Variables:** See `ENV_DEPLOYMENT_TEMPLATE.md` for complete list
- **Vercel Setup:** See `VERCEL_DASHBOARD_SETUP.md` to connect dashboard
- **DigitalOcean Alternative:** See `QUICK_DEPLOY_DIGITALOCEAN.md`

---

**Need help?** Check Railway logs in the dashboard for specific errors.
