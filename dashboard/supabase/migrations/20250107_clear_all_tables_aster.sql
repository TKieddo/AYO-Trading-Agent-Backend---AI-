-- Clear all tables for fresh start (safe on empty / missing tables)
DO $$ BEGIN
  TRUNCATE TABLE orders CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE trades CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE positions CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE account_metrics CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE decisions CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE prices CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE trading_logs CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE pnl_series CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE performance_series CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE wallet_balance_history CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  TRUNCATE TABLE order_metrics_summary CASCADE;
EXCEPTION WHEN undefined_table THEN NULL; END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_matviews WHERE matviewname = 'wins_losses_stats') THEN
    REFRESH MATERIALIZED VIEW wins_losses_stats;
  END IF;
EXCEPTION WHEN others THEN NULL; END $$;
