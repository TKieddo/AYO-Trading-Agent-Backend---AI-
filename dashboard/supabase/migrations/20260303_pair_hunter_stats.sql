-- Pair Hunter performance stats persistence
-- Stores per-asset hit rate + expectancy so hunting quality survives restarts/redeploys

CREATE TABLE IF NOT EXISTS pair_hunter_stats (
  asset VARCHAR(16) PRIMARY KEY,
  total_trades INTEGER NOT NULL DEFAULT 0,
  wins INTEGER NOT NULL DEFAULT 0,
  losses INTEGER NOT NULL DEFAULT 0,
  win_rate NUMERIC(7, 3) NOT NULL DEFAULT 0,
  total_pnl_usd NUMERIC(20, 8) NOT NULL DEFAULT 0,
  total_pnl_percent NUMERIC(20, 8) NOT NULL DEFAULT 0,
  expectancy_usd NUMERIC(20, 8) NOT NULL DEFAULT 0,
  expectancy_percent NUMERIC(20, 8) NOT NULL DEFAULT 0,
  last_close_reason TEXT,
  last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pair_hunter_stats_updated_at
  ON pair_hunter_stats(updated_at DESC);

ALTER TABLE pair_hunter_stats ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = 'pair_hunter_stats'
      AND policyname = 'Allow public read access'
  ) THEN
    CREATE POLICY "Allow public read access"
      ON pair_hunter_stats
      FOR SELECT
      USING (true);
  END IF;
END
$$;
