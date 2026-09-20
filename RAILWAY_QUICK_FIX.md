# ⚡ Railway Quick Fix: Missing Environment Variables

## 🚨 Error You're Seeing

```
RuntimeError: Missing required environment variable: DEEPSEEK_API_KEY
```

## ✅ Quick Fix (2 Minutes)

### Step 1: Go to Railway Variables

1. Open Railway dashboard: https://railway.app/dashboard
2. Click on your service/project
3. Click **"Variables"** tab (left sidebar)

### Step 2: Add Required Variables

Click **"New Variable"** and add these **ONE BY ONE**:

#### 1. DeepSeek API Key (REQUIRED)
```
Name: DEEPSEEK_API_KEY
Value: sk-your-actual-deepseek-key-here
```

#### 2. DeepSeek Base URL
```
Name: DEEPSEEK_BASE_URL
Value: https://api.deepseek.com
```

#### 3. Exchange Selection
```
Name: EXCHANGE
Value: binance
```
(Or `aster` if using Aster DEX)

#### 4. Exchange Credentials

**If using Binance:**
```
Name: BINANCE_API_KEY
Value: your_binance_api_key

Name: BINANCE_API_SECRET
Value: your_binance_api_secret
```

**OR if using Aster:**
```
Name: ASTER_USER_ADDRESS
Value: your_aster_user_address

Name: ASTER_SIGNER_ADDRESS
Value: your_aster_signer_address

Name: ASTER_PRIVATE_KEY
Value: your_aster_private_key
```

### Step 3: Wait for Auto-Redeploy

- Railway automatically redeploys when you add variables
- Wait 1-2 minutes
- Check **"Deployments"** tab for build status

### Step 4: Verify It Works

1. Go to **"Deployments"** tab
2. Click latest deployment
3. Check logs - should see:
   ```
   🌐 HTTP API server started on 0.0.0.0:3000
   ```
4. No more `RuntimeError` messages!

---

## 📋 Minimum Required Variables

**Must have these 3 minimum:**

1. ✅ `DEEPSEEK_API_KEY` (your DeepSeek API key)
2. ✅ `EXCHANGE` (`binance` or `aster`)
3. ✅ Exchange credentials:
   - Binance: `BINANCE_API_KEY` + `BINANCE_API_SECRET`
   - OR Aster: `ASTER_USER_ADDRESS` + `ASTER_SIGNER_ADDRESS` + `ASTER_PRIVATE_KEY`

## 📋 Optional Variables (Recommended)

**These are NOT required for the agent to start, but recommended:**

- `TAAPI_API_KEY` - Optional (for technical indicators, can use TA-Lib + Binance instead)
- `SUPABASE_URL` + `SUPABASE_KEY` - Optional (only needed if you want trades synced to Supabase database)
- `SUPABASE_SERVICE_KEY` - Optional (recommended over SUPABASE_KEY for server-side operations)

---

## 🎯 Pro Tip: Bulk Import

Instead of adding one-by-one, use Railway's **"Raw Editor"**:

1. Click **"Variables"** tab
2. Click **"Raw Editor"** button (top right)
3. Paste all variables at once:

```env
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
EXCHANGE=binance
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
ASSETS=BTC ETH SOL
INTERVAL=5m
API_PORT=3000
PORT=3000
```

4. Click **"Save"**
5. Railway auto-redeploys!

---

## 🆘 Still Not Working?

### Check Build Logs:
1. Go to **"Deployments"** tab
2. Click latest deployment
3. Click **"View Logs"**
4. Look for specific error messages

### Common Issues:

**"Still getting DEEPSEEK_API_KEY error"**
- Make sure variable name is exactly `DEEPSEEK_API_KEY` (case-sensitive)
- Check there are no extra spaces
- Wait for redeploy to finish (check deployment status)

**"Getting BINANCE_API_KEY error"**
- Make sure `EXCHANGE=binance` is set
- Add both `BINANCE_API_KEY` and `BINANCE_API_SECRET`

**"Build succeeds but agent crashes"**
- Check logs for other missing variables
- See `ENV_DEPLOYMENT_TEMPLATE.md` for complete list

---

## 📚 Full Guide

See `RAILWAY_DEPLOYMENT.md` for complete deployment guide.

---

**Quick Checklist:**
- [ ] Added `DEEPSEEK_API_KEY`
- [ ] Added `EXCHANGE` (binance or aster)
- [ ] Added exchange credentials (Binance OR Aster)
- [ ] Waited for redeploy
- [ ] Checked logs - no errors
- [ ] Agent URL working
