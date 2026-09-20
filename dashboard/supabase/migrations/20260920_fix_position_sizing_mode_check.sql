-- Paste this alone into Supabase SQL Editor first.
-- Your DB still has the old position_sizing_mode check (without 'risk'),
-- possibly under a different constraint name than we were dropping.

DO $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN
    SELECT con.conname
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
    WHERE rel.relname = 'trading_settings'
      AND nsp.nspname = 'public'
      AND con.contype = 'c'
      AND pg_get_constraintdef(con.oid) ILIKE '%position_sizing_mode%'
  LOOP
    EXECUTE format('ALTER TABLE trading_settings DROP CONSTRAINT IF EXISTS %I', r.conname);
  END LOOP;
END $$;

ALTER TABLE trading_settings
ADD CONSTRAINT trading_settings_position_sizing_mode_check
CHECK (position_sizing_mode IN ('auto', 'fixed', 'target_profit', 'margin', 'risk'));

UPDATE trading_settings
SET
  exit_mode = COALESCE(exit_mode, 'atr'),
  position_sizing_mode = 'risk',
  take_profit_percent = 20,
  stop_loss_percent = 12,
  leverage = 10,
  max_positions = 3,
  margin_per_position = COALESCE(margin_per_position, 30),
  interval = '15m',
  exchange = 'okx',
  updated_at = now()
WHERE id = 'default';

-- Confirm
SELECT position_sizing_mode, exit_mode, sl_atr_mult, tp_rr_ratio, interval, exchange
FROM trading_settings
WHERE id = 'default';
