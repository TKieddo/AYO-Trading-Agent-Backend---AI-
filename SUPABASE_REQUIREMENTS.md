# 🗄️ Supabase Requirements Explained

Clear breakdown of when Supabase is needed and where.

---

## 📊 Two Different Uses of Supabase

### 1. **Dashboard Settings Storage** (REQUIRED for Settings Page)

**Where:** Dashboard (Vercel)  
**Purpose:** Store trading settings that you change via the dashboard UI

**Required Variables (Vercel):**
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

**How it works:**
```
User changes settings in Dashboard
    ↓
Dashboard saves to Supabase (trading_settings table)
    ↓
Python Agent fetches from Dashboard API
    ↓
Dashboard API reads from Supabase
    ↓
Returns settings to Python Agent
```

**Without it:**
- ❌ Dashboard settings page won't work
- ❌ Can't save/load settings from dashboard
- ⚠️ Agent falls back to `.env` defaults
- ✅ Agent still runs, but settings are static

---

### 2. **Trade Syncing** (OPTIONAL)

**Where:** Python Agent (Railway/DigitalOcean)  
**Purpose:** Automatically sync completed trades to Supabase database

**Optional Variables (Railway/DigitalOcean):**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
# OR (recommended)
SUPABASE_SERVICE_KEY=your_service_role_key
```

**How it works:**
```
Python Agent executes trade
    ↓
Trade completed
    ↓
Agent syncs trade data to Supabase (trades table)
    ↓
Dashboard can display trade history
```

**Without it:**
- ✅ Agent runs fine
- ✅ Trading works normally
- ⚠️ Trades not saved to database
- ⚠️ Dashboard won't show trade history
- ✅ Agent logs: "Supabase not configured - skipping trade sync"

---

## 🎯 Summary

| Component | Supabase Needed? | What For | Required? |
|-----------|------------------|----------|-----------|
| **Dashboard (Vercel)** | ✅ YES | Settings storage | ✅ **REQUIRED** for settings page |
| **Python Agent** | ❌ NO (directly) | Settings fetching | ❌ No - fetches from dashboard API |
| **Python Agent** | ⚠️ Optional | Trade syncing | ❌ No - optional feature |

---

## 🔧 Setup Checklist

### For Dashboard Settings to Work:

**Vercel Environment Variables:**
- [ ] `NEXT_PUBLIC_SUPABASE_URL`
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- [ ] `SUPABASE_SERVICE_ROLE_KEY`
- [ ] Run database migration: `dashboard/supabase/migrations/20250115_extended_trading_settings.sql`

### For Trade Syncing (Optional):

**Railway/DigitalOcean Environment Variables:**
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_SERVICE_KEY` (recommended) or `SUPABASE_KEY`

---

## 💡 Important Notes

1. **Dashboard MUST have Supabase** - Otherwise settings page won't work
2. **Agent doesn't need Supabase directly** - It fetches settings from dashboard API
3. **Trade syncing is separate** - Optional feature, doesn't affect settings
4. **Same Supabase project** - Both dashboard and agent can use the same Supabase project

---

## 🆘 Troubleshooting

**"Dashboard settings page shows error"**
- ✅ Check Vercel has Supabase environment variables
- ✅ Run database migration in Supabase SQL Editor
- ✅ Verify Supabase project is active

**"Agent can't fetch settings from dashboard"**
- ✅ Check `NEXT_PUBLIC_API_URL` in Vercel points to your agent
- ✅ Check dashboard has Supabase configured
- ✅ Agent will fall back to `.env` defaults if dashboard unavailable

**"Trades not syncing to database"**
- ⚠️ This is OK - trade syncing is optional
- ✅ Add Supabase variables to Railway/DigitalOcean if you want it
- ✅ Only works with Binance exchange (not Aster)

---

**Bottom Line:** 
- **Dashboard needs Supabase** for settings page to work
- **Agent doesn't need Supabase** directly (fetches from dashboard)
- **Trade syncing is optional** - add Supabase to agent only if you want it
