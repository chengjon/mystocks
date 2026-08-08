-- ============================================================================
-- create_test_schema.sql
-- Consolidated DDL for mystocks_test database
-- Auto-generated from SQLAlchemy ORM models in web/backend/app/
-- 39 tables + indexes across 11 declarative bases
-- ============================================================================

SET client_min_messages TO WARNING;
SET statement_timeout = '30s';

BEGIN;

-- ============================================================================
-- Module: app.models.announcement
-- ============================================================================

-- Table: announcement

CREATE TABLE IF NOT EXISTS announcement (
	id SERIAL NOT NULL,
	stock_code VARCHAR(20) NOT NULL,
	stock_name VARCHAR(100),
	announcement_title TEXT NOT NULL,
	announcement_type VARCHAR(100),
	publish_date DATE NOT NULL,
	publish_time TIMESTAMP WITHOUT TIME ZONE,
	url TEXT,
	content TEXT,
	summary TEXT,
	keywords JSONB,
	importance_level INTEGER,
	data_source VARCHAR(50) NOT NULL,
	source_id VARCHAR(200),
	is_analyzed BOOLEAN,
	sentiment VARCHAR(20),
	impact_score DECIMAL(5, 2),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	updated_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	CONSTRAINT uq_announcement_source UNIQUE (stock_code, source_id, data_source)
)
;

-- Table: announcement_monitor_record

CREATE TABLE IF NOT EXISTS announcement_monitor_record (
	id SERIAL NOT NULL,
	rule_id INTEGER,
	announcement_id INTEGER,
	matched_keywords JSONB,
	triggered_at TIMESTAMP WITHOUT TIME ZONE,
	notified BOOLEAN,
	notified_at TIMESTAMP WITHOUT TIME ZONE,
	notification_result TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(rule_id) REFERENCES announcement_monitor_rule (id) ON DELETE CASCADE,
	FOREIGN KEY(announcement_id) REFERENCES announcement (id) ON DELETE CASCADE
)
;

-- Table: announcement_monitor_rule

CREATE TABLE IF NOT EXISTS announcement_monitor_rule (
	id SERIAL NOT NULL,
	rule_name VARCHAR(100) NOT NULL,
	keywords JSONB,
	announcement_types JSONB,
	stock_codes JSONB,
	min_importance_level INTEGER,
	notify_enabled BOOLEAN,
	notify_channels JSONB,
	is_active BOOLEAN,
	created_by INTEGER,
	created_at TIMESTAMP WITHOUT TIME ZONE,
	updated_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	UNIQUE (rule_name)
)
;

-- ============================================================================
-- Module: app.models.indicator_config
-- ============================================================================

-- Table: indicator_configurations

CREATE TABLE IF NOT EXISTS indicator_configurations (
	id SERIAL NOT NULL,
	user_id INTEGER NOT NULL,
	name VARCHAR(100) NOT NULL,
	indicators JSON NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
	last_used_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id)
)
;

-- ============================================================================
-- Module: app.models.indicator_data
-- ============================================================================

-- Table: indicator_data

CREATE TABLE IF NOT EXISTS indicator_data (
	timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
	stock_code VARCHAR(20) NOT NULL,
	indicator_code VARCHAR(50) NOT NULL,
	value FLOAT,
	complex_value JSON,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	PRIMARY KEY (timestamp, stock_code, indicator_code)
)
;

-- Table: indicator_tasks

CREATE TABLE IF NOT EXISTS indicator_tasks (
	id SERIAL NOT NULL,
	task_id VARCHAR(50) NOT NULL,
	task_type VARCHAR(50) NOT NULL,
	status VARCHAR(20),
	progress FLOAT,
	params JSON,
	result_summary JSON,
	error_message TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	completed_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id)
)
;

-- ============================================================================
-- Module: app.models.market_data
-- ============================================================================

-- Table: cn_stock_chip_race_end

CREATE TABLE IF NOT EXISTS cn_stock_chip_race_end (
	id BIGSERIAL NOT NULL,
	date DATE NOT NULL,
	code VARCHAR(20) NOT NULL,
	name VARCHAR(100),
	new_price DECIMAL(10, 3),
	change_rate DECIMAL(10, 4),
	pre_close_price DECIMAL(10, 3),
	open_price DECIMAL(10, 3),
	deal_amount DECIMAL(20, 2),
	bid_rate DECIMAL(10, 4),
	bid_trust_amount DECIMAL(20, 2),
	bid_deal_amount DECIMAL(20, 2),
	bid_ratio DECIMAL(10, 4),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id)
)
;

-- Table: cn_stock_chip_race_open

CREATE TABLE IF NOT EXISTS cn_stock_chip_race_open (
	id BIGSERIAL NOT NULL,
	date DATE NOT NULL,
	code VARCHAR(20) NOT NULL,
	name VARCHAR(100),
	new_price DECIMAL(10, 3),
	change_rate DECIMAL(10, 4),
	pre_close_price DECIMAL(10, 3),
	open_price DECIMAL(10, 3),
	deal_amount DECIMAL(20, 2),
	bid_rate DECIMAL(10, 4),
	bid_trust_amount DECIMAL(20, 2),
	bid_deal_amount DECIMAL(20, 2),
	bid_ratio DECIMAL(10, 4),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id)
)
;

-- Table: etf_spot_data

CREATE TABLE IF NOT EXISTS etf_spot_data (
	id BIGSERIAL NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	name VARCHAR(100),
	trade_date DATE NOT NULL,
	latest_price DECIMAL(10, 3),
	change_percent DECIMAL(10, 4),
	change_amount DECIMAL(10, 3),
	volume BIGINT,
	amount DECIMAL(20, 2),
	open_price DECIMAL(10, 3),
	high_price DECIMAL(10, 3),
	low_price DECIMAL(10, 3),
	prev_close DECIMAL(10, 3),
	turnover_rate DECIMAL(10, 4),
	total_market_cap DECIMAL(20, 2),
	circulating_market_cap DECIMAL(20, 2),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id, trade_date)
)
;

-- Table: sector_fund_flow

CREATE TABLE IF NOT EXISTS sector_fund_flow (
	id BIGSERIAL NOT NULL,
	sector_code VARCHAR(50) NOT NULL,
	sector_name VARCHAR(100) NOT NULL,
	sector_type VARCHAR(20) NOT NULL,
	trade_date DATE NOT NULL,
	timeframe VARCHAR(10) NOT NULL,
	latest_price DECIMAL(10, 3),
	change_percent DECIMAL(10, 4),
	main_net_inflow DECIMAL(20, 2),
	main_net_inflow_rate DECIMAL(10, 4),
	super_large_net_inflow DECIMAL(20, 2),
	super_large_net_inflow_rate DECIMAL(10, 4),
	large_net_inflow DECIMAL(20, 2),
	large_net_inflow_rate DECIMAL(10, 4),
	medium_net_inflow DECIMAL(20, 2),
	medium_net_inflow_rate DECIMAL(10, 4),
	small_net_inflow DECIMAL(20, 2),
	small_net_inflow_rate DECIMAL(10, 4),
	leading_stock VARCHAR(100),
	leading_stock_change_percent DECIMAL(10, 4),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id, trade_date)
)
;

-- Table: stock_blocktrade

CREATE TABLE IF NOT EXISTS stock_blocktrade (
	id BIGSERIAL NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	stock_name VARCHAR(100),
	trade_date DATE NOT NULL,
	deal_price DECIMAL(10, 3),
	close_price DECIMAL(10, 3),
	premium_ratio DECIMAL(10, 4),
	deal_amount DECIMAL(20, 2),
	deal_volume BIGINT,
	turnover_rate DECIMAL(10, 4),
	buyer_name VARCHAR(200),
	seller_name VARCHAR(200),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id, trade_date)
)
;

-- Table: stock_dividend

CREATE TABLE IF NOT EXISTS stock_dividend (
	id BIGSERIAL NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	stock_name VARCHAR(100),
	announce_date DATE,
	ex_dividend_date DATE,
	record_date DATE,
	payment_date DATE,
	dividend_year VARCHAR(10),
	plan_profile VARCHAR(200),
	dividend_ratio DECIMAL(10, 4),
	bonus_share_ratio DECIMAL(10, 4),
	transfer_ratio DECIMAL(10, 4),
	allotment_ratio DECIMAL(10, 4),
	allotment_price DECIMAL(10, 3),
	plan_progress VARCHAR(50),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id)
)
;

-- Table: stock_fund_flow

CREATE TABLE IF NOT EXISTS stock_fund_flow (
	id BIGSERIAL NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	trade_date DATE NOT NULL,
	timeframe VARCHAR(10) NOT NULL,
	main_net_inflow DECIMAL(20, 2),
	main_net_inflow_rate DECIMAL(10, 4),
	super_large_net_inflow DECIMAL(20, 2),
	large_net_inflow DECIMAL(20, 2),
	medium_net_inflow DECIMAL(20, 2),
	small_net_inflow DECIMAL(20, 2),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id, trade_date)
)
;

-- Table: stock_lhb_detail

CREATE TABLE IF NOT EXISTS stock_lhb_detail (
	id BIGSERIAL NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	name VARCHAR(100),
	trade_date DATE NOT NULL,
	reason VARCHAR(200),
	buy_amount DECIMAL(20, 2),
	sell_amount DECIMAL(20, 2),
	net_amount DECIMAL(20, 2),
	turnover_rate DECIMAL(10, 4),
	institution_buy DECIMAL(20, 2),
	institution_sell DECIMAL(20, 2),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id, trade_date)
)
;

-- ============================================================================
-- Module: app.models.monitoring
-- ============================================================================

-- Table: alert_record

CREATE TABLE IF NOT EXISTS alert_record (
	id SERIAL NOT NULL,
	rule_id INTEGER,
	rule_name VARCHAR(100),
	symbol VARCHAR(20) NOT NULL,
	stock_name VARCHAR(100),
	alert_time TIMESTAMP WITHOUT TIME ZONE,
	alert_type VARCHAR(50) NOT NULL,
	alert_level VARCHAR(20),
	alert_title VARCHAR(200),
	alert_message TEXT,
	alert_details JSONB,
	snapshot_data JSONB,
	is_read BOOLEAN,
	is_handled BOOLEAN,
	handled_by VARCHAR(50),
	handled_at TIMESTAMP WITHOUT TIME ZONE,
	handle_note TEXT,
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	FOREIGN KEY(rule_id) REFERENCES alert_rule (id) ON DELETE SET NULL
)
;

-- Table: alert_rule

CREATE TABLE IF NOT EXISTS alert_rule (
	id SERIAL NOT NULL,
	rule_name VARCHAR(100) NOT NULL,
	rule_type VARCHAR(50) NOT NULL,
	description TEXT,
	symbol VARCHAR(20),
	stock_name VARCHAR(100),
	parameters JSONB,
	trigger_conditions JSONB,
	notification_config JSONB,
	is_active BOOLEAN,
	priority INTEGER,
	created_by VARCHAR(50),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	updated_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	UNIQUE (rule_name)
)
;

-- Table: dragon_tiger_list

CREATE TABLE IF NOT EXISTS dragon_tiger_list (
	id SERIAL NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	stock_name VARCHAR(100),
	trade_date DATE NOT NULL,
	reason VARCHAR(200),
	reason_code VARCHAR(50),
	total_buy_amount DECIMAL(20, 2),
	total_sell_amount DECIMAL(20, 2),
	net_amount DECIMAL(20, 2),
	institution_buy_count INTEGER,
	institution_sell_count INTEGER,
	institution_net_amount DECIMAL(20, 2),
	detail_data JSONB,
	impact_score INTEGER,
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	CONSTRAINT uq_dragon_tiger_symbol_date UNIQUE (symbol, trade_date)
)
;

-- Table: monitoring_statistics

CREATE TABLE IF NOT EXISTS monitoring_statistics (
	id SERIAL NOT NULL,
	stat_date DATE NOT NULL,
	stat_hour INTEGER,
	total_monitored_stocks INTEGER,
	active_alerts INTEGER,
	total_alerts_triggered INTEGER,
	alerts_by_type JSONB,
	alerts_by_level JSONB,
	limit_up_count INTEGER,
	limit_down_count INTEGER,
	dragon_tiger_count INTEGER,
	avg_response_time_ms INTEGER,
	data_update_frequency INTEGER,
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	CONSTRAINT uq_monitoring_stat_date_hour UNIQUE (stat_date, stat_hour)
)
;

-- Table: realtime_monitoring

CREATE TABLE IF NOT EXISTS realtime_monitoring (
	id SERIAL NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	stock_name VARCHAR(100),
	timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	trade_date DATE NOT NULL,
	price DECIMAL(10, 2),
	open_price DECIMAL(10, 2),
	high_price DECIMAL(10, 2),
	low_price DECIMAL(10, 2),
	pre_close DECIMAL(10, 2),
	change_amount DECIMAL(10, 2),
	change_percent DECIMAL(10, 2),
	volume BIGINT,
	amount DECIMAL(20, 2),
	turnover_rate DECIMAL(10, 2),
	indicators JSONB,
	market_strength VARCHAR(20),
	is_limit_up BOOLEAN,
	is_limit_down BOOLEAN,
	is_st BOOLEAN,
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id)
)
;

-- ============================================================================
-- Module: app.models.rbac
-- ============================================================================

-- Table: audit_logs

CREATE TABLE IF NOT EXISTS audit_logs (
	id UUID NOT NULL,
	user_id UUID,
	action VARCHAR(100) NOT NULL,
	resource_type VARCHAR(50) NOT NULL,
	resource_id VARCHAR(255),
	ip_address VARCHAR(45) NOT NULL,
	user_agent TEXT,
	request_method VARCHAR(10),
	request_path VARCHAR(500),
	status VARCHAR(20) NOT NULL,
	error_message TEXT,
	additional_data TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
)
;

-- Table: permissions

CREATE TABLE IF NOT EXISTS permissions (
	id UUID NOT NULL,
	name VARCHAR(100) NOT NULL,
	display_name VARCHAR(100) NOT NULL,
	description TEXT,
	resource VARCHAR(50) NOT NULL,
	action VARCHAR(50) NOT NULL,
	is_active BOOLEAN NOT NULL,
	is_system BOOLEAN NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
)
;

-- Table: role_permissions

CREATE TABLE IF NOT EXISTS role_permissions (
	id UUID NOT NULL,
	role_id UUID NOT NULL,
	permission_id UUID NOT NULL,
	assigned_by UUID,
	assigned_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	is_active BOOLEAN NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id),
	FOREIGN KEY(role_id) REFERENCES roles (id),
	FOREIGN KEY(permission_id) REFERENCES permissions (id),
	FOREIGN KEY(assigned_by) REFERENCES users (id)
)
;

-- Table: roles

CREATE TABLE IF NOT EXISTS roles (
	id UUID NOT NULL,
	name VARCHAR(50) NOT NULL,
	display_name VARCHAR(100) NOT NULL,
	description TEXT,
	parent_role_id UUID,
	is_active BOOLEAN NOT NULL,
	is_system BOOLEAN NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(parent_role_id) REFERENCES roles (id)
)
;

-- Table: security_events

CREATE TABLE IF NOT EXISTS security_events (
	id UUID NOT NULL,
	user_id UUID,
	event_type VARCHAR(50) NOT NULL,
	severity VARCHAR(20) NOT NULL,
	title VARCHAR(200) NOT NULL,
	description TEXT,
	ip_address VARCHAR(45) NOT NULL,
	user_agent TEXT,
	request_method VARCHAR(10),
	request_path VARCHAR(500),
	event_data TEXT,
	resolved BOOLEAN NOT NULL,
	resolved_by UUID,
	resolved_at TIMESTAMP WITH TIME ZONE,
	resolution_notes TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id),
	FOREIGN KEY(resolved_by) REFERENCES users (id)
)
;

-- Table: user_roles

CREATE TABLE IF NOT EXISTS user_roles (
	id UUID NOT NULL,
	user_id UUID NOT NULL,
	role_id UUID NOT NULL,
	assigned_by UUID,
	assigned_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	expires_at TIMESTAMP WITH TIME ZONE,
	is_active BOOLEAN NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_user_role UNIQUE (user_id, role_id),
	FOREIGN KEY(user_id) REFERENCES users (id),
	FOREIGN KEY(role_id) REFERENCES roles (id),
	FOREIGN KEY(assigned_by) REFERENCES users (id)
)
;

-- Table: user_sessions

CREATE TABLE IF NOT EXISTS user_sessions (
	id UUID NOT NULL,
	user_id UUID NOT NULL,
	session_token VARCHAR(255) NOT NULL,
	refresh_token VARCHAR(255),
	ip_address VARCHAR(45) NOT NULL,
	user_agent TEXT,
	is_active BOOLEAN NOT NULL,
	last_activity TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
)
;

-- Table: users

CREATE TABLE IF NOT EXISTS users (
	id UUID NOT NULL,
	username VARCHAR(50) NOT NULL,
	email VARCHAR(255) NOT NULL,
	full_name VARCHAR(100),
	password_hash VARCHAR(255) NOT NULL,
	avatar_url VARCHAR(500),
	oauth_provider VARCHAR(50),
	oauth_user_id VARCHAR(255),
	oauth_token_data TEXT,
	is_active BOOLEAN NOT NULL,
	is_verified BOOLEAN NOT NULL,
	is_superuser BOOLEAN NOT NULL,
	last_login TIMESTAMP WITH TIME ZONE,
	login_count INTEGER NOT NULL,
	failed_login_attempts INTEGER NOT NULL,
	locked_until TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id)
)
;

-- ============================================================================
-- Module: app.models.stock
-- ============================================================================

-- Table: stock_info

CREATE TABLE IF NOT EXISTS stock_info (
	symbol VARCHAR(20) NOT NULL,
	name VARCHAR(100) NOT NULL,
	exchange VARCHAR(20),
	security_type VARCHAR(50),
	list_date DATE,
	status VARCHAR(20),
	listing_board VARCHAR(50),
	market_cap DECIMAL(25, 2),
	circulating_market_cap DECIMAL(25, 2),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	updated_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (symbol)
)
;

-- ============================================================================
-- Module: app.models.strategy
-- ============================================================================

-- Table: strategy_backtest

CREATE TABLE IF NOT EXISTS strategy_backtest (
	id BIGSERIAL NOT NULL,
	strategy_code VARCHAR(50) NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	stock_name VARCHAR(100),
	signal_date DATE NOT NULL,
	entry_price VARCHAR(20),
	exit_price VARCHAR(20),
	exit_date DATE,
	holding_days INTEGER,
	return_rate VARCHAR(20),
	max_drawdown VARCHAR(20),
	backtest_period VARCHAR(50),
	parameters JSON,
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id)
)
;

-- Table: strategy_definition

CREATE TABLE IF NOT EXISTS strategy_definition (
	id SERIAL NOT NULL,
	strategy_code VARCHAR(50) NOT NULL,
	strategy_name_cn VARCHAR(100) NOT NULL,
	strategy_name_en VARCHAR(100) NOT NULL,
	description TEXT,
	parameters JSON,
	is_active BOOLEAN,
	created_at TIMESTAMP WITHOUT TIME ZONE,
	updated_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	UNIQUE (strategy_code)
)
;

-- Table: strategy_result

CREATE TABLE IF NOT EXISTS strategy_result (
	id BIGSERIAL NOT NULL,
	strategy_code VARCHAR(50) NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	stock_name VARCHAR(100),
	check_date DATE NOT NULL,
	match_result BOOLEAN NOT NULL,
	match_score INTEGER,
	match_details JSON,
	latest_price VARCHAR(20),
	change_percent VARCHAR(20),
	created_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id)
)
;

-- ============================================================================
-- Module: app.models.sync_message
-- ============================================================================

-- Table: sync_message

CREATE TABLE IF NOT EXISTS sync_message (
	id SERIAL NOT NULL,
	operation_type operationtype NOT NULL,
	sync_direction syncdirection NOT NULL,
	source_database VARCHAR(100) NOT NULL,
	target_database VARCHAR(100) NOT NULL,
	source_table VARCHAR(100) NOT NULL,
	target_table VARCHAR(100) NOT NULL,
	record_identifier JSONB NOT NULL,
	payload JSONB NOT NULL,
	status messagestatus NOT NULL,
	priority INTEGER NOT NULL,
	retry_count INTEGER NOT NULL,
	max_retries INTEGER NOT NULL,
	next_retry_at TIMESTAMP WITHOUT TIME ZONE,
	error_message TEXT,
	error_details JSONB,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	started_at TIMESTAMP WITHOUT TIME ZONE,
	completed_at TIMESTAMP WITHOUT TIME ZONE,
	sync_latency_ms DECIMAL(10, 2),
	processing_duration_ms DECIMAL(10, 2),
	processed_by VARCHAR(100),
	extra_metadata JSONB,
	PRIMARY KEY (id),
	CONSTRAINT check_priority_range CHECK (priority >= 1 AND priority <= 10),
	CONSTRAINT check_retry_count_non_negative CHECK (retry_count >= 0),
	CONSTRAINT check_max_retries_non_negative CHECK (max_retries >= 0),
	CONSTRAINT check_retry_count_le_max CHECK (retry_count <= max_retries)
)
;

-- Table: sync_statistics

CREATE TABLE IF NOT EXISTS sync_statistics (
	id SERIAL NOT NULL,
	window_start TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	window_end TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	window_size_minutes INTEGER NOT NULL,
	source_table VARCHAR(100),
	target_table VARCHAR(100),
	total_messages INTEGER NOT NULL,
	success_count INTEGER NOT NULL,
	failed_count INTEGER NOT NULL,
	retry_count INTEGER NOT NULL,
	dead_letter_count INTEGER NOT NULL,
	avg_sync_latency_ms DECIMAL(10, 2),
	p50_sync_latency_ms DECIMAL(10, 2),
	p95_sync_latency_ms DECIMAL(10, 2),
	p99_sync_latency_ms DECIMAL(10, 2),
	max_sync_latency_ms DECIMAL(10, 2),
	avg_processing_duration_ms DECIMAL(10, 2),
	success_rate DECIMAL(5, 2),
	failure_rate DECIMAL(5, 2),
	calculated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (id)
)
;

-- ============================================================================
-- Module: app.models.user
-- ============================================================================

-- Table: user_tokens

CREATE TABLE IF NOT EXISTS user_tokens (
	id SERIAL NOT NULL,
	user_id INTEGER NOT NULL,
	token VARCHAR(200) NOT NULL,
	token_type VARCHAR(20) NOT NULL,
	expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (id)
)
;

-- ============================================================================
-- Module: app.models.wencai_data
-- ============================================================================

-- Table: wencai_queries

CREATE TABLE IF NOT EXISTS wencai_queries (
	id SERIAL NOT NULL,
	query_name VARCHAR(20) NOT NULL,
	query_text TEXT NOT NULL,
	description VARCHAR(255),
	is_active BOOLEAN NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (id)
)
;

-- ============================================================================
-- Module: app.repositories.backtest_repository
-- ============================================================================

-- Table: backtest_equity_curves

CREATE TABLE IF NOT EXISTS backtest_equity_curves (
	id SERIAL NOT NULL,
	backtest_id INTEGER NOT NULL,
	trade_date DATE NOT NULL,
	equity NUMERIC(15, 2) NOT NULL,
	drawdown NUMERIC(5, 2) NOT NULL,
	benchmark_equity NUMERIC(15, 2),
	PRIMARY KEY (id),
	CONSTRAINT uq_backtest_trade_date UNIQUE (backtest_id, trade_date),
	FOREIGN KEY(backtest_id) REFERENCES backtest_results (backtest_id) ON DELETE CASCADE
)
;

-- Table: backtest_results

CREATE TABLE IF NOT EXISTS backtest_results (
	backtest_id SERIAL NOT NULL,
	strategy_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	symbols TEXT[] NOT NULL,
	start_date DATE NOT NULL,
	end_date DATE NOT NULL,
	initial_capital NUMERIC(15, 2) NOT NULL,
	commission_rate NUMERIC(6, 4) NOT NULL,
	slippage_rate NUMERIC(6, 4) NOT NULL,
	benchmark VARCHAR(20),
	final_capital NUMERIC(15, 2),
	performance_metrics JSON,
	status VARCHAR(20) NOT NULL,
	error_message TEXT,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	started_at TIMESTAMP WITHOUT TIME ZONE,
	completed_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (backtest_id),
	CONSTRAINT chk_backtest_status CHECK (status IN ('pending', 'running', 'completed', 'failed')),
	CONSTRAINT chk_date_range CHECK (end_date >= start_date)
)
;

-- Table: backtest_trades

CREATE TABLE IF NOT EXISTS backtest_trades (
	trade_id SERIAL NOT NULL,
	backtest_id INTEGER NOT NULL,
	symbol VARCHAR(20) NOT NULL,
	trade_date DATE NOT NULL,
	action VARCHAR(10) NOT NULL,
	price NUMERIC(10, 2) NOT NULL,
	quantity INTEGER NOT NULL,
	amount NUMERIC(15, 2) NOT NULL,
	commission NUMERIC(10, 2) NOT NULL,
	profit_loss NUMERIC(15, 2),
	PRIMARY KEY (trade_id),
	CONSTRAINT chk_action CHECK (action IN ('buy', 'sell')),
	FOREIGN KEY(backtest_id) REFERENCES backtest_results (backtest_id) ON DELETE CASCADE
)
;

-- ============================================================================
-- Module: app.repositories.strategy_repository
-- ============================================================================

-- Table: user_strategies

CREATE TABLE IF NOT EXISTS user_strategies (
	strategy_id SERIAL NOT NULL,
	user_id INTEGER NOT NULL,
	strategy_name VARCHAR(100) NOT NULL,
	strategy_type VARCHAR(50) NOT NULL,
	description TEXT,
	parameters JSON,
	max_position_size NUMERIC(5, 4) NOT NULL,
	stop_loss_percent NUMERIC(5, 2),
	take_profit_percent NUMERIC(5, 2),
	status VARCHAR(20) NOT NULL,
	tags TEXT[],
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (strategy_id),
	CONSTRAINT chk_strategy_type CHECK (strategy_type IN ('momentum', 'mean_reversion', 'breakout', 'grid', 'custom')),
	CONSTRAINT chk_status CHECK (status IN ('draft', 'active', 'paused', 'archived')),
	CONSTRAINT chk_position_size CHECK (max_position_size > 0 AND max_position_size <= 1)
)
;

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs (created_at);
CREATE INDEX IF NOT EXISTS idx_audit_ip ON audit_logs (ip_address);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_status ON audit_logs (status);
CREATE INDEX IF NOT EXISTS idx_audit_user_action ON audit_logs (user_id, action);
CREATE INDEX IF NOT EXISTS idx_backtest_code_date ON strategy_backtest (strategy_code, signal_date);
CREATE INDEX IF NOT EXISTS idx_backtest_results_created_at ON backtest_results (created_at);
CREATE INDEX IF NOT EXISTS idx_backtest_results_status ON backtest_results (status);
CREATE INDEX IF NOT EXISTS idx_backtest_results_strategy_id ON backtest_results (strategy_id);
CREATE INDEX IF NOT EXISTS idx_backtest_results_user_id ON backtest_results (user_id);
CREATE INDEX IF NOT EXISTS idx_backtest_symbol ON strategy_backtest (symbol, signal_date);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_backtest_id ON backtest_trades (backtest_id);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_date ON backtest_trades (trade_date);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_symbol ON backtest_trades (symbol);
CREATE INDEX IF NOT EXISTS idx_chip_race_end_code ON cn_stock_chip_race_end (code, date);
CREATE INDEX IF NOT EXISTS idx_chip_race_open_code ON cn_stock_chip_race_open (code, date);
CREATE INDEX IF NOT EXISTS idx_created_completed ON sync_message (created_at, completed_at);
CREATE INDEX IF NOT EXISTS idx_equity_curves_backtest_id ON backtest_equity_curves (backtest_id);
CREATE INDEX IF NOT EXISTS idx_equity_curves_trade_date ON backtest_equity_curves (trade_date);
CREATE INDEX IF NOT EXISTS idx_etf_spot_symbol ON etf_spot_data (symbol, trade_date);
CREATE INDEX IF NOT EXISTS idx_is_active ON wencai_queries (is_active);
CREATE INDEX IF NOT EXISTS idx_last_used ON indicator_configurations (last_used_at);
CREATE INDEX IF NOT EXISTS idx_permission_active ON permissions (is_active);
CREATE INDEX IF NOT EXISTS idx_permission_resource_action ON permissions (resource, action);
CREATE INDEX IF NOT EXISTS idx_query_name ON wencai_queries (query_name);
CREATE INDEX IF NOT EXISTS idx_realtime_symbol_time ON realtime_monitoring (symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_role_active ON roles (is_active);
CREATE INDEX IF NOT EXISTS idx_role_permission_active ON role_permissions (is_active);
CREATE INDEX IF NOT EXISTS idx_role_system ON roles (is_system);
CREATE INDEX IF NOT EXISTS idx_sector_fund_flow_code ON sector_fund_flow (sector_code, trade_date);
CREATE INDEX IF NOT EXISTS idx_sector_fund_flow_type ON sector_fund_flow (sector_type, timeframe, trade_date);
CREATE INDEX IF NOT EXISTS idx_security_created ON security_events (created_at);
CREATE INDEX IF NOT EXISTS idx_security_event_type ON security_events (event_type);
CREATE INDEX IF NOT EXISTS idx_security_ip ON security_events (ip_address);
CREATE INDEX IF NOT EXISTS idx_security_resolved ON security_events (resolved);
CREATE INDEX IF NOT EXISTS idx_security_severity ON security_events (severity);
CREATE INDEX IF NOT EXISTS idx_session_expires ON user_sessions (expires_at);
CREATE INDEX IF NOT EXISTS idx_session_last_activity ON user_sessions (last_activity);
CREATE INDEX IF NOT EXISTS idx_session_token ON user_sessions (session_token);
CREATE INDEX IF NOT EXISTS idx_session_user_active ON user_sessions (user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_source_target_status ON sync_message (source_table, target_table, status);
CREATE INDEX IF NOT EXISTS idx_status_priority_created ON sync_message (status, priority, created_at);
CREATE INDEX IF NOT EXISTS idx_status_retry_next_retry ON sync_message (status, retry_count, next_retry_at);
CREATE INDEX IF NOT EXISTS idx_stock_blocktrade_date ON stock_blocktrade (trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_blocktrade_symbol ON stock_blocktrade (symbol, trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_dividend_ex_date ON stock_dividend (ex_dividend_date);
CREATE INDEX IF NOT EXISTS idx_stock_dividend_symbol ON stock_dividend (symbol, announce_date);
CREATE INDEX IF NOT EXISTS idx_stock_fund_flow_symbol_date ON stock_fund_flow (symbol, trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_fund_flow_timeframe ON stock_fund_flow (timeframe, trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_info_exchange ON stock_info (exchange);
CREATE INDEX IF NOT EXISTS idx_stock_info_name ON stock_info (name);
CREATE INDEX IF NOT EXISTS idx_stock_info_security_type ON stock_info (security_type);
CREATE INDEX IF NOT EXISTS idx_stock_lhb_symbol ON stock_lhb_detail (symbol, trade_date);
CREATE INDEX IF NOT EXISTS idx_strategy_code ON strategy_definition (strategy_code);
CREATE INDEX IF NOT EXISTS idx_strategy_result_code_date ON strategy_result (strategy_code, check_date);
CREATE INDEX IF NOT EXISTS idx_strategy_result_match ON strategy_result (match_result, check_date);
CREATE INDEX IF NOT EXISTS idx_strategy_result_symbol_date ON strategy_result (symbol, check_date);
CREATE INDEX IF NOT EXISTS idx_user_active ON users (is_active);
CREATE INDEX IF NOT EXISTS idx_user_created ON users (created_at);
CREATE INDEX IF NOT EXISTS idx_user_id ON indicator_configurations (user_id);
CREATE INDEX IF NOT EXISTS idx_user_oauth ON users (oauth_provider, oauth_user_id);
CREATE INDEX IF NOT EXISTS idx_user_role_active ON user_roles (is_active);
CREATE INDEX IF NOT EXISTS idx_user_role_expires ON user_roles (expires_at);
CREATE INDEX IF NOT EXISTS idx_user_strategies_created_at ON user_strategies (created_at);
CREATE INDEX IF NOT EXISTS idx_user_strategies_status ON user_strategies (status);
CREATE INDEX IF NOT EXISTS idx_user_strategies_type ON user_strategies (strategy_type);
CREATE INDEX IF NOT EXISTS idx_user_strategies_user_id ON user_strategies (user_id);
CREATE INDEX IF NOT EXISTS idx_window_calculated ON sync_statistics (window_start, calculated_at);
CREATE INDEX IF NOT EXISTS idx_window_table ON sync_statistics (window_start, window_end, source_table, target_table);
CREATE INDEX IF NOT EXISTS ix_alert_record_alert_level ON alert_record (alert_level);
CREATE INDEX IF NOT EXISTS ix_alert_record_alert_time ON alert_record (alert_time);
CREATE INDEX IF NOT EXISTS ix_alert_record_alert_type ON alert_record (alert_type);
CREATE INDEX IF NOT EXISTS ix_alert_record_is_read ON alert_record (is_read);
CREATE INDEX IF NOT EXISTS ix_alert_record_symbol ON alert_record (symbol);
CREATE INDEX IF NOT EXISTS ix_alert_rule_is_active ON alert_rule (is_active);
CREATE INDEX IF NOT EXISTS ix_alert_rule_symbol ON alert_rule (symbol);
CREATE INDEX IF NOT EXISTS ix_announcement_announcement_type ON announcement (announcement_type);
CREATE INDEX IF NOT EXISTS ix_announcement_data_source ON announcement (data_source);
CREATE INDEX IF NOT EXISTS ix_announcement_importance_level ON announcement (importance_level);
CREATE INDEX IF NOT EXISTS ix_announcement_monitor_record_announcement_id ON announcement_monitor_record (announcement_id);
CREATE INDEX IF NOT EXISTS ix_announcement_monitor_record_rule_id ON announcement_monitor_record (rule_id);
CREATE INDEX IF NOT EXISTS ix_announcement_monitor_record_triggered_at ON announcement_monitor_record (triggered_at);
CREATE INDEX IF NOT EXISTS ix_announcement_monitor_rule_is_active ON announcement_monitor_rule (is_active);
CREATE INDEX IF NOT EXISTS ix_announcement_publish_date ON announcement (publish_date);
CREATE INDEX IF NOT EXISTS ix_announcement_stock_code ON announcement (stock_code);
CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs (action);
CREATE INDEX IF NOT EXISTS ix_audit_logs_ip_address ON audit_logs (ip_address);
CREATE INDEX IF NOT EXISTS ix_audit_logs_resource_type ON audit_logs (resource_type);
CREATE INDEX IF NOT EXISTS ix_audit_logs_status ON audit_logs (status);
CREATE INDEX IF NOT EXISTS ix_backtest_results_strategy_id ON backtest_results (strategy_id);
CREATE INDEX IF NOT EXISTS ix_backtest_results_user_id ON backtest_results (user_id);
CREATE INDEX IF NOT EXISTS ix_dragon_tiger_list_net_amount ON dragon_tiger_list (net_amount);
CREATE INDEX IF NOT EXISTS ix_dragon_tiger_list_symbol ON dragon_tiger_list (symbol);
CREATE INDEX IF NOT EXISTS ix_dragon_tiger_list_trade_date ON dragon_tiger_list (trade_date);
CREATE INDEX IF NOT EXISTS ix_indicator_data_timestamp ON indicator_data (timestamp);
CREATE INDEX IF NOT EXISTS ix_indicator_tasks_status ON indicator_tasks (status);
CREATE INDEX IF NOT EXISTS ix_monitoring_statistics_stat_date ON monitoring_statistics (stat_date);
CREATE INDEX IF NOT EXISTS ix_permissions_action ON permissions (action);
CREATE INDEX IF NOT EXISTS ix_permissions_resource ON permissions (resource);
CREATE INDEX IF NOT EXISTS ix_realtime_monitoring_is_limit_down ON realtime_monitoring (is_limit_down);
CREATE INDEX IF NOT EXISTS ix_realtime_monitoring_is_limit_up ON realtime_monitoring (is_limit_up);
CREATE INDEX IF NOT EXISTS ix_realtime_monitoring_symbol ON realtime_monitoring (symbol);
CREATE INDEX IF NOT EXISTS ix_realtime_monitoring_timestamp ON realtime_monitoring (timestamp);
CREATE INDEX IF NOT EXISTS ix_realtime_monitoring_trade_date ON realtime_monitoring (trade_date);
CREATE INDEX IF NOT EXISTS ix_security_events_event_type ON security_events (event_type);
CREATE INDEX IF NOT EXISTS ix_security_events_ip_address ON security_events (ip_address);
CREATE INDEX IF NOT EXISTS ix_security_events_severity ON security_events (severity);
CREATE INDEX IF NOT EXISTS ix_sync_message_completed_at ON sync_message (completed_at);
CREATE INDEX IF NOT EXISTS ix_sync_message_created_at ON sync_message (created_at);
CREATE INDEX IF NOT EXISTS ix_sync_message_next_retry_at ON sync_message (next_retry_at);
CREATE INDEX IF NOT EXISTS ix_sync_message_operation_type ON sync_message (operation_type);
CREATE INDEX IF NOT EXISTS ix_sync_message_priority ON sync_message (priority);
CREATE INDEX IF NOT EXISTS ix_sync_message_source_table ON sync_message (source_table);
CREATE INDEX IF NOT EXISTS ix_sync_message_status ON sync_message (status);
CREATE INDEX IF NOT EXISTS ix_sync_message_sync_direction ON sync_message (sync_direction);
CREATE INDEX IF NOT EXISTS ix_sync_message_target_table ON sync_message (target_table);
CREATE INDEX IF NOT EXISTS ix_sync_statistics_source_table ON sync_statistics (source_table);
CREATE INDEX IF NOT EXISTS ix_sync_statistics_target_table ON sync_statistics (target_table);
CREATE INDEX IF NOT EXISTS ix_sync_statistics_window_end ON sync_statistics (window_end);
CREATE INDEX IF NOT EXISTS ix_sync_statistics_window_start ON sync_statistics (window_start);
CREATE INDEX IF NOT EXISTS ix_user_sessions_ip_address ON user_sessions (ip_address);
CREATE INDEX IF NOT EXISTS ix_user_strategies_user_id ON user_strategies (user_id);
CREATE INDEX IF NOT EXISTS ix_user_tokens_id ON user_tokens (id);
CREATE INDEX IF NOT EXISTS ix_user_tokens_user_id ON user_tokens (user_id);
CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE INDEX IF NOT EXISTS ix_wencai_queries_id ON wencai_queries (id);
CREATE INDEX IF NOT EXISTS ix_wencai_queries_is_active ON wencai_queries (is_active);
CREATE UNIQUE INDEX IF NOT EXISTS ix_indicator_tasks_task_id ON indicator_tasks (task_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_permissions_name ON permissions (name);
CREATE UNIQUE INDEX IF NOT EXISTS ix_roles_name ON roles (name);
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_sessions_refresh_token ON user_sessions (refresh_token);
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_sessions_session_token ON user_sessions (session_token);
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_tokens_token ON user_tokens (token);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);
CREATE UNIQUE INDEX IF NOT EXISTS ix_wencai_queries_query_name ON wencai_queries (query_name);
CREATE UNIQUE INDEX IF NOT EXISTS uk_user_name ON indicator_configurations (user_id, name);

COMMIT;

-- ============================================================================
-- Schema initialization complete
-- ============================================================================
