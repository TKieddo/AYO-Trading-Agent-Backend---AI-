-- Pair Hunter exclusions for repeatedly invalid symbols
-- Safe to run on existing deployments

ALTER TABLE pair_hunter_stats
ADD COLUMN IF NOT EXISTS data_fail_count INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS excluded_until TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS exclusion_reason TEXT,
ADD COLUMN IF NOT EXISTS last_data_error TEXT;
