# 🚀 Vercel Dashboard + Python Agent Setup Guide

Your dashboard is deployed on Vercel, but it needs to connect to your Python trading agent. Here's how to make them communicate.

## 📋 Current Situation

✅ **Dashboard:** Deployed on Vercel  
✅ **Agent Code:** On GitHub  
❌ **Agent Running:** Not deployed yet (needs hosting)

## 🔗 How They Communicate

The dashboard uses the `NEXT_PUBLIC_API_URL` environment variable to connect to your Python agent:

```
Vercel Dashboard → NEXT_PUBLIC_API_URL → Python Agent (needs hosting)
```

## 🎯 Step 1: Deploy Your Python Agent

You need to host your Python agent somewhere. Here are the best options:

### Option A: DigitalOcean App Platform (Recommended)
- **Cost:** ~$5-12/month
- **Easiest:** Zero infrastructure management
- **Guide:** See `QUICK_DEPLOY_DIGITALOCEAN.md`

### Option B: Railway
- **Cost:** ~$5-10/month
- **Very Easy:** Great for Python apps
- **URL:** https://railway.app

### Option C: Render
- **Cost:** ~$7-15/month
- **Easy:** Good Python support
- **URL:** https://render.com

### Option D: Fly.io
- **Cost:** Free tier available
- **Good for:** Small projects
- **URL:** https://fly.io

---

## 🔧 Step 2: Configure Vercel Environment Variables

Once your Python agent is deployed and you have its URL (e.g., `https://trading-agent-xxxx.ondigitalocean.app`):

### 1. Go to Vercel Dashboard
- Visit: https://vercel.com/dashboard
- Select your dashboard project

### 2. Add Environment Variables
Go to **Settings** → **Environment Variables** and add:

```env
# Python Trading Agent URL (REQUIRED)
NEXT_PUBLIC_API_URL=https://your-agent-url.com

# Your Dashboard URL (for settings)
NEXT_PUBLIC_BASE_URL=https://your-vercel-dashboard.vercel.app

# Supabase (if you're using it)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 3. Redeploy
After adding environment variables:
- Click **"Redeploy"** or push a new commit
- Vercel will rebuild with the new variables

---

## 🧪 Step 3: Test the Connection

### 1. Check Agent Status
Visit your dashboard and check the connection status indicator.

### 2. Test API Endpoints
Your dashboard should now be able to:
- ✅ Fetch trading decisions from agent
- ✅ View agent status
- ✅ Get trading logs
- ✅ Update trading settings (if using Supabase)

### 3. Verify in Browser Console
Open browser DevTools (F12) → Console:
- Should see successful API calls to your agent URL
- No CORS errors (if agent is configured correctly)

---

## 🔒 Important: CORS Configuration

Your Python agent now has CORS support built-in! It automatically allows:
- ✅ All `*.vercel.app` domains (production and preview deployments)
- ✅ Localhost for development
- ✅ Custom origins via environment variable

### Optional: Configure Specific Origins

If you want to restrict to specific domains, add this to your Python agent's environment variables:

```env
# In your agent's hosting platform (DigitalOcean/Railway/etc.)
CORS_ALLOWED_ORIGINS=https://your-dashboard.vercel.app,https://your-custom-domain.com
```

**Note:** If not set, it defaults to allowing all Vercel domains (`*.vercel.app`) and localhost.

---

## 📝 Quick Setup Checklist

- [ ] Deploy Python agent to hosting platform (DigitalOcean/Railway/Render)
- [ ] Get agent's public URL (e.g., `https://agent-xxx.com`)
- [ ] Add `NEXT_PUBLIC_API_URL` to Vercel environment variables
- [ ] Add `NEXT_PUBLIC_BASE_URL` to Vercel (your Vercel dashboard URL)
- [ ] Configure CORS on Python agent to allow Vercel domain
- [ ] Redeploy Vercel dashboard
- [ ] Test connection in dashboard
- [ ] Verify agent status shows "connected"

---

## 🆘 Troubleshooting

### Dashboard shows "Agent Offline"
1. **Check agent URL:** Verify `NEXT_PUBLIC_API_URL` is correct in Vercel
2. **Test agent directly:** `curl https://your-agent-url.com/status`
3. **Check CORS:** Agent must allow Vercel domain
4. **Check agent logs:** Agent might be crashing on startup

### CORS Errors in Browser
- CORS is now automatically configured to allow all `*.vercel.app` domains
- If you still see CORS errors, check that your agent is deployed and running
- For custom domains, add `CORS_ALLOWED_ORIGINS` environment variable to your agent

### Environment Variables Not Working
- Vercel requires redeploy after adding env vars
- Make sure variable names start with `NEXT_PUBLIC_` for client-side access
- Check Vercel build logs for errors

---

## 💡 Recommended Architecture

```
┌─────────────────┐
│  Vercel         │  Dashboard (Frontend)
│  Dashboard      │  └─ NEXT_PUBLIC_API_URL
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  DigitalOcean   │  Python Trading Agent
│  / Railway      │  └─ API Server (Port 3000/8080)
│  / Render       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Supabase       │  Database (Settings, Trades)
└─────────────────┘
```

---

## 🚀 Next Steps

1. **Deploy Python Agent:**
   - Follow `QUICK_DEPLOY_DIGITALOCEAN.md` for easiest option
   - Or choose Railway/Render for similar ease

2. **Configure Vercel:**
   - Add environment variables as shown above
   - Redeploy dashboard

3. **Test Everything:**
   - Verify agent connection
   - Test trading settings updates
   - Monitor trading activity

---

## 📚 Additional Resources

- **DigitalOcean Deployment:** `DIGITALOCEAN_DEPLOYMENT.md`
- **Environment Variables:** `ENV_DEPLOYMENT_TEMPLATE.md`
- **Quick Deploy:** `QUICK_DEPLOY_DIGITALOCEAN.md`

---

**Need help?** Check your agent logs and Vercel deployment logs for specific errors.
