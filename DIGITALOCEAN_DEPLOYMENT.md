# 🚀 DigitalOcean Deployment Guide

Complete guide to deploy your AI Trading Agent to DigitalOcean.

## 📋 Prerequisites

- DigitalOcean account ([Sign up here](https://www.digitalocean.com))
- GitHub repository with your code
- Supabase project (for database)
- API keys ready (Binance/Aster, DeepSeek, etc.)

---

## 🎯 Option 1: DigitalOcean App Platform (Recommended - Easiest)

**Cost:** ~$5-12/month  
**Best for:** Quick deployment, zero infrastructure management

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Prepare for DigitalOcean deployment"
   git push origin main
   ```

### Step 2: Create App on DigitalOcean

1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Connect your GitHub repository
4. Select your repository and branch (`main`)

### Step 3: Configure Python Trading Agent Service

**Service 1: Trading Agent**

1. Click **"Edit"** or **"Add Component"** → **"Service"**
2. Configure:
   - **Name:** `trading-agent`
   - **Source Directory:** `/` (root)
   - **Build Command:** 
     ```bash
     pip install poetry && poetry install --no-interaction --no-ansi --no-root
     ```
   - **Run Command:**
     ```bash
     poetry run python -m src.main
     ```
   - **HTTP Port:** `3000`
   - **Instance Size:** Basic ($5/month) or Professional ($12/month)
   - **Instance Count:** 1

3. **Environment Variables** (Add all from your `.env`):
   ```env
   # API Keys (REQUIRED)
   DEEPSEEK_API_KEY=your_deepseek_key
   BINANCE_API_KEY=your_binance_key
   BINANCE_API_SECRET=your_binance_secret
   
   # OR Aster DEX
   ASTER_USER_ADDRESS=your_address
   ASTER_SIGNER_ADDRESS=your_signer
   ASTER_PRIVATE_KEY=your_private_key
   
   # Trading Configuration (can be changed via dashboard)
   EXCHANGE=binance
   ASSETS=BTC ETH SOL BNB ZEC DOGE AVAX XLM XMR
   INTERVAL=5m
   STRATEGY=auto
   
   # Position Sizing
   MARGIN_PER_POSITION=40.0
   DEFAULT_LEVERAGE=30
   POSITION_SIZING_MODE=margin
   MAX_POSITIONS=5
   
   # Per-asset leverage
   ZEC_LEVERAGE=5
   BTC_LEVERAGE=25
   ETH_LEVERAGE=25
   BNB_LEVERAGE=25
   DOGE_LEVERAGE=25
   SOL_LEVERAGE=25
   
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
   
   # Risk Management
   ENABLE_TRAILING_STOP=true
   TRAILING_STOP_ACTIVATION_PCT=5.0
   TRAILING_STOP_DISTANCE_PCT=3.0
   MAX_POSITION_HOLD_HOURS=48.0
   ENABLE_DRAWDOWN_PROTECTION=true
   MAX_DRAWDOWN_FROM_PEAK_PCT=5.0
   
   # Scalping
   SCALPING_TP_PERCENT=5.0
   SCALPING_SL_PERCENT=5.0
   
   # LLM
   LLM_MODEL=deepseek-reasoner
   DEEPSEEK_MAX_TOKENS=20000
   
   # API Server
   API_HOST=0.0.0.0
   API_PORT=3000
   APP_PORT=3000
   ```

### Step 4: Configure Next.js Dashboard Service

**Service 2: Dashboard**

1. Click **"Add Component"** → **"Service"**
2. Configure:
   - **Name:** `dashboard`
   - **Source Directory:** `/dashboard`
   - **Build Command:**
     ```bash
     npm install && npm run build
     ```
   - **Run Command:**
     ```bash
     npm start
     ```
   - **HTTP Port:** `3001`
   - **Instance Size:** Basic ($5/month)
   - **Instance Count:** 1

3. **Environment Variables:**
   ```env
   NODE_ENV=production
   PORT=3001
   
   # Supabase (REQUIRED for database)
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   
   # Python Agent URL (update after agent deploys)
   NEXT_PUBLIC_API_URL=https://trading-agent-xxxx.ondigitalocean.app
   NEXT_PUBLIC_BASE_URL=https://dashboard-xxxx.ondigitalocean.app
   ```

### Step 5: Deploy

1. Click **"Create Resources"** or **"Deploy"**
2. Wait 5-10 minutes for deployment
3. Copy the URLs:
   - Trading Agent: `https://trading-agent-xxxx.ondigitalocean.app`
   - Dashboard: `https://dashboard-xxxx.ondigitalocean.app`

### Step 6: Update Environment Variables

After first deployment:

1. Go to **Settings** → **App-Level Environment Variables**
2. Update `NEXT_PUBLIC_API_URL` with your trading agent URL
3. Click **"Save"** → App will auto-redeploy

### Step 7: Run Database Migration

1. Go to your Supabase SQL Editor
2. Run: `dashboard/supabase/migrations/20250115_extended_trading_settings.sql`
3. This creates all the settings tables

---

## 🐳 Option 2: DigitalOcean Droplets + Dokploy (More Control)

**Cost:** ~$6-12/month (Droplet) + Free (Dokploy)  
**Best for:** Full control, custom configurations

### Step 1: Create Droplet

1. Go to [DigitalOcean Droplets](https://cloud.digitalocean.com/droplets)
2. Click **"Create Droplet"**
3. Configure:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($6/month - 1GB RAM) or Regular ($12/month - 2GB RAM)
   - **Region:** Choose closest to you
   - **Authentication:** SSH keys (recommended) or password
4. Click **"Create Droplet"**

### Step 2: Install Dokploy

SSH into your droplet:
```bash
ssh root@your_droplet_ip
```

Install Dokploy:
```bash
curl -sSL https://dokploy.com/install.sh | sh
```

Follow the installation prompts. Dokploy will give you:
- Web UI URL: `http://your_droplet_ip:3000`
- Default credentials (save these!)

### Step 3: Configure Dokploy

1. Open Dokploy web UI in browser
2. Login with default credentials
3. Change password immediately

### Step 4: Deploy Trading Agent

1. In Dokploy, click **"New Application"**
2. **Source:** GitHub (connect your repo)
3. **Build Method:** Dockerfile
4. **Dockerfile Path:** `Dockerfile`
5. **Port:** `3000`
6. **Environment Variables:** Add all from your `.env` file (same as Option 1)

### Step 5: Deploy Dashboard

1. Click **"New Application"**
2. **Source:** GitHub
3. **Build Method:** Dockerfile
4. **Dockerfile Path:** `dashboard/Dockerfile`
5. **Port:** `3001`
6. **Environment Variables:** Add dashboard env vars

### Step 6: Configure Networking

In Dokploy:
1. Go to **Traefik** settings
2. Add domain names:
   - `trading-agent.yourdomain.com` → Trading Agent
   - `dashboard.yourdomain.com` → Dashboard
3. Dokploy will automatically:
   - Get SSL certificates (Let's Encrypt)
   - Configure reverse proxy
   - Enable HTTPS

---

## 🔧 Post-Deployment Setup

### 1. Update Dashboard Settings

1. Go to your dashboard: `https://dashboard-xxxx.ondigitalocean.app/settings`
2. Configure all trading settings via UI
3. Settings are saved to Supabase and applied immediately

### 2. Verify Agent is Running

Check agent status:
```bash
curl https://trading-agent-xxxx.ondigitalocean.app/status
```

Check agent logs:
- **App Platform:** Dashboard → Runtime Logs
- **Dokploy:** Applications → Your App → Logs

### 3. Monitor Trading

- **Dashboard:** View positions, trades, decisions
- **Logs:** Monitor agent activity
- **Settings:** Change parameters in real-time

---

## 🔄 Updating Your Deployment

### App Platform:
- Push to GitHub → Auto-deploys
- Or: Dashboard → Settings → Force Rebuild

### Dokploy:
- Push to GitHub → Click "Redeploy" in Dokploy UI
- Or: Dokploy auto-detects changes (if enabled)

---

## 💰 Cost Breakdown

### Option 1: App Platform
- Trading Agent: $5-12/month
- Dashboard: $5/month
- **Total: ~$10-17/month**

### Option 2: Droplets + Dokploy
- Droplet: $6-12/month
- Dokploy: FREE (open source)
- **Total: ~$6-12/month**

---

## 🆘 Troubleshooting

### Agent Not Starting
- Check logs in DigitalOcean dashboard
- Verify all environment variables are set
- Check API keys are valid

### Dashboard Can't Connect to Agent
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check agent is running: `curl https://agent-url/status`
- Ensure both services are in same network (App Platform) or use public URLs

### Database Connection Issues
- Verify Supabase credentials
- Check Supabase project is active
- Run migrations in Supabase SQL Editor

---

## 📝 Environment Variables Reference

See `.env.example` for complete list. Key variables:

**Trading Agent:**
- `DEEPSEEK_API_KEY` (required)
- `BINANCE_API_KEY` / `BINANCE_API_SECRET` OR `ASTER_*` (required)
- `EXCHANGE` (binance or aster)
- `ASSETS` (space-separated list)
- `INTERVAL` (5m, 15m, 1h, etc.)

**Dashboard:**
- `NEXT_PUBLIC_SUPABASE_URL` (required)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (required)
- `NEXT_PUBLIC_API_URL` (agent URL)
- `SUPABASE_SERVICE_ROLE_KEY` (for server-side operations)

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Supabase project created
- [ ] Database migrations run
- [ ] API keys ready (Binance/Aster, DeepSeek)
- [ ] App Platform or Droplet created
- [ ] Environment variables configured
- [ ] Services deployed
- [ ] URLs updated in environment variables
- [ ] Agent status check passes
- [ ] Dashboard loads correctly
- [ ] Settings page accessible
- [ ] Trading agent making decisions

---

## 🎉 You're Live!

Your trading agent is now running 24/7 on DigitalOcean! 

- **Change settings:** Dashboard → Settings (instant updates)
- **Monitor:** Dashboard → Portfolio, Risk, etc.
- **Update code:** Push to GitHub → Auto-deploys

**Need help?** Check logs in DigitalOcean dashboard or Dokploy UI.
