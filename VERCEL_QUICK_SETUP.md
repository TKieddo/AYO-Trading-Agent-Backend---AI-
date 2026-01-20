# ⚡ Quick Setup: Vercel Dashboard + Python Agent

## 🎯 What You Have Now

✅ **Dashboard:** Deployed on Vercel  
✅ **Agent Code:** On GitHub  
✅ **CORS:** Configured to allow Vercel requests  
❌ **Agent Running:** Needs to be deployed

---

## 🚀 3-Step Setup

### Step 1: Deploy Python Agent (Choose One)

**Option A: DigitalOcean (Easiest)**
- Follow: `QUICK_DEPLOY_DIGITALOCEAN.md`
- Cost: ~$5-12/month
- Time: 5 minutes

**Option B: Railway**
- Visit: https://railway.app
- Connect GitHub repo
- Deploy Python service
- **Important:** Add environment variables (see `RAILWAY_QUICK_FIX.md`)
- Cost: ~$5-10/month

**Option C: Render**
- Visit: https://render.com
- Connect GitHub repo
- Deploy Python Web Service
- Cost: ~$7-15/month

### Step 2: Get Agent URL

After deployment, you'll get a URL like:
- `https://trading-agent-xxxx.ondigitalocean.app`
- `https://your-app.railway.app`
- `https://your-app.onrender.com`

### Step 3: Configure Vercel

1. Go to: https://vercel.com/dashboard
2. Select your dashboard project
3. Go to **Settings** → **Environment Variables**
4. Add:

```env
NEXT_PUBLIC_API_URL=https://your-agent-url.com
NEXT_PUBLIC_BASE_URL=https://your-vercel-dashboard.vercel.app
```

5. Click **"Redeploy"**

---

## ✅ Done!

Your dashboard will now connect to your Python agent automatically.

---

## 🧪 Test It

1. Visit your Vercel dashboard
2. Check the connection status indicator
3. Should show "Connected" if agent is running

---

## 🆘 Troubleshooting

**"Agent Offline"**
- Verify `NEXT_PUBLIC_API_URL` is correct in Vercel
- Test agent directly: `curl https://your-agent-url.com/status`
- Check agent logs in your hosting platform

**CORS Errors**
- Already fixed! CORS now allows all `*.vercel.app` domains automatically

---

**Need more details?** See `VERCEL_DASHBOARD_SETUP.md`
