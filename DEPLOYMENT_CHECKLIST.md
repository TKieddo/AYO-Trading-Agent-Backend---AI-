# ✅ DigitalOcean Deployment Checklist

Use this checklist to ensure everything is ready for deployment.

## 📋 Pre-Deployment

### Code Preparation
- [ ] All code committed to GitHub
- [ ] `.gitignore` excludes `.env` files
- [ ] No sensitive data in code
- [ ] Database migrations ready (`dashboard/supabase/migrations/20250115_extended_trading_settings.sql`)

### Environment Setup
- [ ] Supabase project created
- [ ] Database migrations run in Supabase
- [ ] API keys ready:
  - [ ] DeepSeek API key
  - [ ] Binance API key & secret (OR Aster credentials)
  - [ ] Supabase URL & keys

### DigitalOcean Account
- [ ] Account created at [digitalocean.com](https://www.digitalocean.com)
- [ ] Payment method added
- [ ] GitHub account connected (for App Platform)

---

## 🚀 Deployment Steps

### Option A: App Platform (Recommended)

- [ ] Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
- [ ] Click "Create App"
- [ ] Connect GitHub repository
- [ ] **Trading Agent Service:**
  - [ ] Source directory: `/` (root)
  - [ ] Build command: `pip install poetry && poetry install --no-interaction --no-ansi --no-root`
  - [ ] Run command: `poetry run python -m src.main`
  - [ ] Port: `3000` (or use PORT env var)
  - [ ] Instance size: Basic ($5/month)
  - [ ] All environment variables added (see `ENV_DEPLOYMENT_TEMPLATE.md`)
- [ ] **Dashboard Service:**
  - [ ] Source directory: `/dashboard`
  - [ ] Build command: `npm install && npm run build`
  - [ ] Run command: `npm start`
  - [ ] Port: `3001`
  - [ ] Instance size: Basic ($5/month)
  - [ ] All environment variables added
- [ ] Click "Create Resources"
- [ ] Wait for deployment (5-10 minutes)
- [ ] Copy deployment URLs

### Option B: Droplets + Dokploy

- [ ] Create Droplet (Ubuntu 22.04, $6-12/month)
- [ ] SSH into droplet
- [ ] Install Dokploy: `curl -sSL https://dokploy.com/install.sh | sh`
- [ ] Access Dokploy UI
- [ ] Deploy Trading Agent:
  - [ ] Connect GitHub repo
  - [ ] Use Dockerfile
  - [ ] Port: 3000
  - [ ] Add environment variables
- [ ] Deploy Dashboard:
  - [ ] Use `dashboard/Dockerfile`
  - [ ] Port: 3001
  - [ ] Add environment variables
- [ ] Configure domains (optional)

---

## 🔧 Post-Deployment

### Environment Variables
- [ ] Update `NEXT_PUBLIC_API_URL` with trading agent URL
- [ ] Update `NEXT_PUBLIC_BASE_URL` with dashboard URL
- [ ] Verify all API keys are set correctly

### Database
- [ ] Run migration: `20250115_extended_trading_settings.sql` in Supabase
- [ ] Verify `trading_settings` table exists
- [ ] Check default settings are populated

### Testing
- [ ] Check agent status: `curl https://agent-url/status`
- [ ] Check dashboard loads: `https://dashboard-url`
- [ ] Test settings page: `https://dashboard-url/settings`
- [ ] Verify agent is fetching settings from database
- [ ] Check logs for errors

### Monitoring
- [ ] Set up DigitalOcean monitoring alerts
- [ ] Bookmark dashboard URL
- [ ] Test changing settings via UI
- [ ] Verify changes apply immediately

---

## 🎯 Quick Start Commands

### Check Agent Status
```bash
curl https://your-agent-url.ondigitalocean.app/status
```

### View Agent Logs
- **App Platform:** Dashboard → Runtime Logs
- **Dokploy:** Applications → Your App → Logs

### Update Settings
1. Go to: `https://your-dashboard-url/settings`
2. Change any values
3. Click "Save"
4. Changes apply immediately (no redeploy needed)

---

## 📞 Support

If you encounter issues:
1. Check deployment logs
2. Verify environment variables
3. Check Supabase connection
4. Review `DIGITALOCEAN_DEPLOYMENT.md` for detailed steps

---

## 💡 Pro Tips

- **Start with App Platform** - It's easier and auto-deploys from GitHub
- **Use environment variables** - Never commit `.env` files
- **Test locally first** - Make sure everything works before deploying
- **Monitor costs** - App Platform shows usage in dashboard
- **Backup settings** - Export from Supabase if needed

---

**Ready to deploy?** Follow `DIGITALOCEAN_DEPLOYMENT.md` for detailed instructions!
