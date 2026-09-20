# AI-Trading Agent Supabase dump

- **Project:** AI-Trading Agent (`rwcamygafesbuwvwbqrz`)
- **URL:** https://rwcamygafesbuwvwbqrz.supabase.co
- **Region:** eu-north-1
- **Data:** all public tables were **empty (0 rows)** at export — this is a **schema-only** dump

## Restore on self-hosted Supabase / Coolify

1. Stand up Supabase (or Postgres + PostgREST if you only need SQL).
2. In SQL editor / `psql`, run `RESTORE_ALL.sql` (schema + migrations).
3. Then run `02_live_extras.sql` (functions + `wins_losses_stats` matview).
4. Point the agent at the new URL:

```bash
SUPABASE_URL=https://<your-coolify-host>
SUPABASE_KEY=<anon-or-service-key>
SUPABASE_SERVICE_KEY=<service-role-key>
```

## Files

| File | Purpose |
|------|---------|
| `RESTORE_ALL.sql` | Combined schema + repo migrations |
| `01_schema.sql` | Base schema |
| `migrations/` | Incremental migrations |
| `02_live_extras.sql` | Live functions / matview from cloud |
| `INVENTORY.json` | Table list + export metadata |
| `live_columns.json` | Live column catalog for verify |
