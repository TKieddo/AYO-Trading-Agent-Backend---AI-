-- Extended Trading Settings Migration
-- Adds all .env configuration options to database for real-time management
-- Run this in your Supabase SQL editor

-- Add new columns to trading_settings table
ALTER TABLE trading_settings
ADD COLUMN IF NOT EXISTS multi_exchange_mode boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS assets text DEFAULT 'BTC ETH SOL',
ADD COLUMN IF NOT EXISTS interval text DEFAULT '5m',
ADD COLUMN IF NOT EXISTS strategy text DEFAULT 'auto',
ADD COLUMN IF NOT EXISTS exchange text DEFAULT 'binance',
ADD COLUMN IF NOT EXISTS alert_service_enabled boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS alert_risk_per_trade numeric(10,2) DEFAULT 30.0,
ADD COLUMN IF NOT EXISTS alert_check_interval integer DEFAULT 5,
ADD COLUMN IF NOT EXISTS alert_agent_endpoint text DEFAULT 'http://localhost:5000/api/alert/signal',
ADD COLUMN IF NOT EXISTS alert_assets text DEFAULT 'ZEC,BTC,ETH,SOL,BNB',
ADD COLUMN IF NOT EXISTS alert_timeframe text DEFAULT '15m',
ADD COLUMN IF NOT EXISTS enable_trailing_stop boolean DEFAULT true,
ADD COLUMN IF NOT EXISTS trailing_stop_activation_pct numeric(5,2) DEFAULT 5.0,
ADD COLUMN IF NOT EXISTS trailing_stop_distance_pct numeric(5,2) DEFAULT 3.0,
ADD COLUMN IF NOT EXISTS max_position_hold_hours numeric(10,2) DEFAULT 48.0,
ADD COLUMN IF NOT EXISTS enable_drawdown_protection boolean DEFAULT true,
ADD COLUMN IF NOT EXISTS max_drawdown_from_peak_pct numeric(5,2) DEFAULT 5.0,
ADD COLUMN IF NOT EXISTS scalping_tp_percent numeric(5,2) DEFAULT 5.0,
ADD COLUMN IF NOT EXISTS scalping_sl_percent numeric(5,2) DEFAULT 5.0,
ADD COLUMN IF NOT EXISTS auto_strategy_cache_minutes integer DEFAULT 0,
ADD COLUMN IF NOT EXISTS asset_leverage_overrides jsonb DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS asset_timeframes jsonb DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS llm_model text DEFAULT 'deepseek-reasoner',
ADD COLUMN IF NOT EXISTS deepseek_max_tokens integer DEFAULT 20000,
ADD COLUMN IF NOT EXISTS next_public_base_url text DEFAULT 'http://localhost:3001';

-- Update default settings with current .env values
UPDATE trading_settings
SET 
  multi_exchange_mode = false,
  assets = 'BTC ETH SOL BNB ZEC DOGE AVAX XLM XMR',
  interval = '5m',
  strategy = 'auto',
  exchange = 'binance',
  alert_service_enabled = true,
  alert_risk_per_trade = 30.0,
  alert_check_interval = 5,
  alert_agent_endpoint = 'http://localhost:5000/api/alert/signal',
  alert_assets = 'ZEC,BTC,ETH,SOL,BNB',
  alert_timeframe = '15m',
  enable_trailing_stop = true,
  trailing_stop_activation_pct = 5.0,
  trailing_stop_distance_pct = 3.0,
  max_position_hold_hours = 48.0,
  enable_drawdown_protection = true,
  max_drawdown_from_peak_pct = 5.0,
  scalping_tp_percent = 5.0,
  scalping_sl_percent = 5.0,
  auto_strategy_cache_minutes = 0,
  asset_leverage_overrides = '{"ZEC": 5, "BTC": 25, "ETH": 25, "BNB": 25, "DOGE": 25, "SOL": 25}'::jsonb,
  asset_timeframes = '{"BTC": "15m", "ETH": "15m", "SOL": "15m", "BNB": "15m", "ZEC": "5m"}'::jsonb,
  llm_model = 'deepseek-reasoner',
  deepseek_max_tokens = 20000,
  next_public_base_url = 'http://localhost:3001'
WHERE id = 'default';

-- Insert default if not exists
INSERT INTO trading_settings (
  id, 
  multi_exchange_mode, 
  assets, 
  interval, 
  strategy, 
  exchange,
  alert_service_enabled,
  alert_risk_per_trade,
  alert_check_interval,
  alert_agent_endpoint,
  alert_assets,
  alert_timeframe,
  enable_trailing_stop,
  trailing_stop_activation_pct,
  trailing_stop_distance_pct,
  max_position_hold_hours,
  enable_drawdown_protection,
  max_drawdown_from_peak_pct,
  scalping_tp_percent,
  scalping_sl_percent,
  auto_strategy_cache_minutes,
  asset_leverage_overrides,
  asset_timeframes,
  llm_model,
  deepseek_max_tokens,
  next_public_base_url
)
VALUES (
  'default',
  false,
  'BTC ETH SOL BNB ZEC DOGE AVAX XLM XMR',
  '5m',
  'auto',
  'binance',
  true,
  30.0,
  5,
  'http://localhost:5000/api/alert/signal',
  'ZEC,BTC,ETH,SOL,BNB',
  '15m',
  true,
  5.0,
  3.0,
  48.0,
  true,
  5.0,
  5.0,
  5.0,
  0,
  '{"ZEC": 5, "BTC": 25, "ETH": 25, "BNB": 25, "DOGE": 25, "SOL": 25}'::jsonb,
  '{"BTC": "15m", "ETH": "15m", "SOL": "15m", "BNB": "15m", "ZEC": "5m"}'::jsonb,
  'deepseek-reasoner',
  20000,
  'http://localhost:3001'
)
ON CONFLICT (id) DO NOTHING;

-- Add comments for documentation
COMMENT ON COLUMN trading_settings.multi_exchange_mode IS 'Enable trading on multiple exchanges simultaneously';
COMMENT ON COLUMN trading_settings.assets IS 'Space-separated list of assets to trade (e.g., "BTC ETH SOL")';
COMMENT ON COLUMN trading_settings.interval IS 'Trading interval (e.g., "5m", "1h")';
COMMENT ON COLUMN trading_settings.strategy IS 'Trading strategy: auto, scalping, llm_trend, or empty for default';
COMMENT ON COLUMN trading_settings.exchange IS 'Exchange to use: binance or aster';
COMMENT ON COLUMN trading_settings.alert_service_enabled IS 'Enable PineScript alert monitoring service';
COMMENT ON COLUMN trading_settings.alert_risk_per_trade IS 'Default risk per trade for alerts (USD)';
COMMENT ON COLUMN trading_settings.alert_check_interval IS 'Alert check interval in seconds';
COMMENT ON COLUMN trading_settings.alert_agent_endpoint IS 'Agent endpoint URL for alert signals';
COMMENT ON COLUMN trading_settings.alert_assets IS 'Comma-separated list of assets to monitor for alerts';
COMMENT ON COLUMN trading_settings.alert_timeframe IS 'Default timeframe for alert monitoring';
COMMENT ON COLUMN trading_settings.enable_trailing_stop IS 'Enable trailing stop loss';
COMMENT ON COLUMN trading_settings.trailing_stop_activation_pct IS 'Start trailing after X% profit';
COMMENT ON COLUMN trading_settings.trailing_stop_distance_pct IS 'Keep SL X% below peak profit';
COMMENT ON COLUMN trading_settings.max_position_hold_hours IS 'Maximum hours to hold a position';
COMMENT ON COLUMN trading_settings.enable_drawdown_protection IS 'Enable drawdown protection';
COMMENT ON COLUMN trading_settings.max_drawdown_from_peak_pct IS 'Maximum drawdown from peak (percentage)';
COMMENT ON COLUMN trading_settings.scalping_tp_percent IS 'Take profit percentage for scalping strategy';
COMMENT ON COLUMN trading_settings.scalping_sl_percent IS 'Stop loss percentage for scalping strategy';
COMMENT ON COLUMN trading_settings.auto_strategy_cache_minutes IS 'Cache auto strategy selection for X minutes (0 = re-evaluate every cycle)';
COMMENT ON COLUMN trading_settings.asset_leverage_overrides IS 'JSON object with per-asset leverage overrides (e.g., {"BTC": 25, "ZEC": 5})';
COMMENT ON COLUMN trading_settings.asset_timeframes IS 'JSON object with per-asset timeframe overrides (e.g., {"BTC": "15m", "ZEC": "5m"})';
COMMENT ON COLUMN trading_settings.llm_model IS 'LLM model to use (e.g., deepseek-reasoner, deepseek-chat)';
COMMENT ON COLUMN trading_settings.deepseek_max_tokens IS 'Maximum tokens for DeepSeek API';
COMMENT ON COLUMN trading_settings.next_public_base_url IS 'Base URL for the dashboard/API';
