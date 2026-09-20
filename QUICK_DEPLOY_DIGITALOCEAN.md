# ⚡ Quick Deploy to DigitalOcean - 5 Minutes

Fastest way to get your trading agent live on DigitalOcean App Platform.

## 🚀 Step-by-Step (5 Minutes)

### 1. Push to GitHub (1 min)
```bash
git add .
git commit -m "Ready for DigitalOcean deployment"
git push origin main
```

### 2. Create App on DigitalOcean (2 min)

1. Go to: https://cloud.digitalocean.com/apps
2. Click **"Create App"**
3. **Connect GitHub** → Select your repo → Branch: `main`

### 3. Configure Trading Agent (1 min)

**Add Component** → **Service**:

- **Name:** `trading-agent`
- **Source Directory:** `/` (leave empty or type `/`)
- **Build Command:** 
  ```bash
  pip install poetry && poetry install --no-interaction --no-ansi --no-root
  ```
- **Run Command:**
  ```bash
  poetry run python -m src.main
  ```
- **HTTP Port:** `3000`
- **Instance Size:** Basic ($5/month)

**Environment Variables** (Click "Edit" → Add all from `ENV_DEPLOYMENT_TEMPLATE.md`):
- `DEEPSEEK_API_KEY` (required)
- `BINANCE_API_KEY` + `BINANCE_API_SECRET` (or Aster credentials)
- `EXCHANGE=binance`
- `ASSETS=BTC ETH SOL BNB ZEC DOGE AVAX XLM XMR`
- `INTERVAL=5m`
- All other variables from template

### 4. Configure Dashboard (1 min)

**Add Component** → **Service**:

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

**Environment Variables:**
- `NEXT_PUBLIC_SUPABASE_URL` (required)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (required)
- `SUPABASE_SERVICE_ROLE_KEY` (required)
- `NEXT_PUBLIC_API_URL` (update after deployment)
- `NEXT_PUBLIC_BASE_URL` (update after deployment)
- `NODE_ENV=production`
- `PORT=3001`

### 5. Deploy! (1 min)

1. Click **"Create Resources"**
2. Wait 5-10 minutes
3. Copy URLs:
   - Agent: `https://trading-agent-xxxx.ondigitalocean.app`
   - Dashboard: `https://dashboard-xxxx.ondigitalocean.app`

### 6. Final Setup (1 min)

1. **Update Dashboard Environment Variables:**
   - Go to Dashboard → Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` = your agent URL
   - Update `NEXT_PUBLIC_BASE_URL` = your dashboard URL
   - Click "Save" → Auto-redeploys

2. **Run Database Migration:**
   - Go to Supabase SQL Editor
   - Run: `dashboard/supabase/migrations/20250115_extended_trading_settings.sql`

3. **Test:**
   - Visit: `https://dashboard-url/settings`
   - Change a setting → Click "Save"
   - Verify it works!

---

## ✅ Done!

Your trading agent is now running 24/7! 🎉

- **Change settings:** Dashboard → Settings (instant updates)
- **Monitor:** Dashboard → Portfolio, Risk, etc.
- **Update code:** Push to GitHub → Auto-deploys

**Total Cost:** ~$10/month (both services)

---

## 🆘 Troubleshooting

**Agent not starting?**
- Check logs: Dashboard → Runtime Logs
- Verify all environment variables are set
- Check API keys are valid

**Dashboard can't connect?**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check agent is running: `curl https://agent-url/status`

**Need more help?** See `DIGITALOCEAN_DEPLOYMENT.md` for detailed guide.
