-- Volatility-adaptive exits, risk-based sizing, scale-out ladder, and circuit breakers.
--
-- Background: the mechanical stop compared against margin ROI, so a "3%" stop at 10x
-- leverage was a 0.3% price move and fired on noise. These columns let the stop, the
-- target, the position size, and the entry filters all be tuned from the dashboard
-- instead of requiring an agent redeploy.

ALTER TABLE trading_settings
  -- Volatility-adaptive exits
  ADD COLUMN IF NOT EXISTS exit_mode text DEFAULT 'atr',
  ADD COLUMN IF NOT EXISTS sl_atr_mult numeric DEFAULT 2.5,
  ADD COLUMN IF NOT EXISTS tp_rr_ratio numeric DEFAULT 2.0,
  ADD COLUMN IF NOT EXISTS atr_period integer DEFAULT 14,
  ADD COLUMN IF NOT EXISTS min_stop_price_pct numeric DEFAULT 0.8,
  ADD COLUMN IF NOT EXISTS max_stop_price_pct numeric DEFAULT 5.0,

  -- Risk-based position sizing
  ADD COLUMN IF NOT EXISTS risk_per_trade_usd numeric,
  ADD COLUMN IF NOT EXISTS risk_per_trade_pct numeric DEFAULT 0.5,
  ADD COLUMN IF NOT EXISTS max_notional_per_position numeric,
  ADD COLUMN IF NOT EXISTS min_notional_per_position numeric DEFAULT 100,

  -- Partial take-profit ladder, "R:percent_of_size" pairs
  ADD COLUMN IF NOT EXISTS enable_profit_ladder boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS profit_ladder text DEFAULT '1.0:50,2.0:30',
  ADD COLUMN IF NOT EXISTS breakeven_after_first_fill boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS enable_breakeven_stop boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS breakeven_trigger_r numeric DEFAULT 1.0,
  ADD COLUMN IF NOT EXISTS trailing_stop_activation_r numeric DEFAULT 1.5,
  ADD COLUMN IF NOT EXISTS trailing_stop_distance_r numeric DEFAULT 1.0,

  -- Re-entry control (anti-chop)
  ADD COLUMN IF NOT EXISTS reentry_cooldown_minutes numeric DEFAULT 45,
  ADD COLUMN IF NOT EXISTS loss_reentry_cooldown_minutes numeric DEFAULT 90,
  ADD COLUMN IF NOT EXISTS block_direction_flip boolean DEFAULT true,

  -- Account-level circuit breakers
  ADD COLUMN IF NOT EXISTS max_daily_loss_usd numeric,
  ADD COLUMN IF NOT EXISTS max_daily_loss_pct numeric DEFAULT 3.0,
  ADD COLUMN IF NOT EXISTS max_consecutive_losses integer DEFAULT 4,
  ADD COLUMN IF NOT EXISTS loss_streak_pause_minutes numeric DEFAULT 120,

  -- Higher-timeframe trend agreement
  ADD COLUMN IF NOT EXISTS enable_htf_trend_filter boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS htf_trend_timeframe text DEFAULT '1h',
  ADD COLUMN IF NOT EXISTS htf_trend_fast_ema integer DEFAULT 20,
  ADD COLUMN IF NOT EXISTS htf_trend_slow_ema integer DEFAULT 50,
  ADD COLUMN IF NOT EXISTS htf_trend_min_separation_pct numeric DEFAULT 0.15,
  ADD COLUMN IF NOT EXISTS htf_block_when_flat boolean DEFAULT true,

  -- Analysis timeframes (previously hardcoded in the agent)
  ADD COLUMN IF NOT EXISTS intraday_timeframe text DEFAULT '15m',
  ADD COLUMN IF NOT EXISTS longterm_timeframe text DEFAULT '4h',

  -- Pair hunter tuning
  ADD COLUMN IF NOT EXISTS pair_hunter_min_volatility numeric DEFAULT 1.0,
  ADD COLUMN IF NOT EXISTS pair_hunter_ideal_volatility numeric DEFAULT 2.0,
  ADD COLUMN IF NOT EXISTS pair_hunter_max_volatility numeric DEFAULT 3.5,
  ADD COLUMN IF NOT EXISTS pair_hunter_min_volume_24h numeric DEFAULT 50000000,
  ADD COLUMN IF NOT EXISTS pair_hunter_min_trend_strength numeric DEFAULT 25,
  ADD COLUMN IF NOT EXISTS pair_hunter_min_price numeric DEFAULT 0.01,
  ADD COLUMN IF NOT EXISTS pair_hunter_max_spread_pct numeric DEFAULT 0.5,
  ADD COLUMN IF NOT EXISTS pair_hunter_timeframe text DEFAULT '15m',
  ADD COLUMN IF NOT EXISTS pair_hunter_blacklist text DEFAULT 'SHIB PEPE FLOKI BONK WIF MEME DOGE 1000SATS LUNA FTT',
  ADD COLUMN IF NOT EXISTS pair_hunter_weight_volatility numeric DEFAULT 0.25,
  ADD COLUMN IF NOT EXISTS pair_hunter_weight_trend numeric DEFAULT 0.40,
  ADD COLUMN IF NOT EXISTS pair_hunter_weight_setup numeric DEFAULT 0.35;

COMMENT ON COLUMN trading_settings.exit_mode IS
  'atr = stop derived from sl_atr_mult x ATR% of price; fixed = legacy take_profit_percent/stop_loss_percent as margin ROI.';
COMMENT ON COLUMN trading_settings.profit_ladder IS
  'Scale-out plan as comma separated R:size_pct pairs, e.g. "1.0:50,2.0:30". Remainder rides the trailing stop.';
COMMENT ON COLUMN trading_settings.risk_per_trade_usd IS
  'Fixed USD risked per trade. Takes precedence over risk_per_trade_pct. Notional is solved from the stop distance.';
COMMENT ON COLUMN trading_settings.min_notional_per_position IS
  'Floor so a very tight stop cannot size an order below the exchange minimum.';
COMMENT ON COLUMN trading_settings.max_consecutive_losses IS
  'Pause new entries after this many consecutive losing closes. 0 disables the breaker.';
COMMENT ON COLUMN trading_settings.htf_trend_min_separation_pct IS
  'Minimum EMA separation on the confirmation timeframe. Below this the market is treated as a range.';

-- Move the existing row onto the new profile. Legacy TP/SL stay as the fixed-mode fallback,
-- expressed as margin ROI, and are only consulted when ATR data is unavailable.
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
