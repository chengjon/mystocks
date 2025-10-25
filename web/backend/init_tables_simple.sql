-- ========================================
-- MyStocks 股票数据扩展功能 - 简化版数据库初始化脚本
-- 版本: 1.0.0 (Apache License Compatible)
-- 日期: 2025-10-14
-- 说明: 创建7个PostgreSQL+TimescaleDB表(移除压缩策略)
-- ========================================

-- 1. 个股资金流向表
CREATE TABLE IF NOT EXISTS stock_fund_flow (
    id BIGSERIAL,
    symbol VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    main_net_inflow DECIMAL(20, 2),
    main_net_inflow_rate DECIMAL(10, 4),
    super_large_net_inflow DECIMAL(20, 2),
    large_net_inflow DECIMAL(20, 2),
    medium_net_inflow DECIMAL(20, 2),
    small_net_inflow DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date),
    UNIQUE(symbol, trade_date, timeframe)
);

SELECT create_hypertable('stock_fund_flow', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_stock_fund_flow_symbol_date
    ON stock_fund_flow(symbol, trade_date DESC);

CREATE INDEX IF NOT EXISTS idx_stock_fund_flow_timeframe
    ON stock_fund_flow(timeframe, trade_date DESC);

-- 2. ETF实时数据表
CREATE TABLE IF NOT EXISTS etf_spot_data (
    id BIGSERIAL,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date),
    UNIQUE(symbol, trade_date)
);

SELECT create_hypertable('etf_spot_data', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_etf_spot_symbol
    ON etf_spot_data(symbol, trade_date DESC);

-- 3. 竞价抢筹数据表
CREATE TABLE IF NOT EXISTS chip_race_data (
    id BIGSERIAL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    trade_date DATE NOT NULL,
    race_type VARCHAR(10) NOT NULL,
    latest_price DECIMAL(10, 3),
    change_percent DECIMAL(10, 4),
    prev_close DECIMAL(10, 3),
    open_price DECIMAL(10, 3),
    race_amount DECIMAL(20, 2),
    race_amplitude DECIMAL(10, 4),
    race_commission DECIMAL(20, 2),
    race_transaction DECIMAL(20, 2),
    race_ratio DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date),
    UNIQUE(symbol, trade_date, race_type)
);

SELECT create_hypertable('chip_race_data', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_chip_race_symbol
    ON chip_race_data(symbol, trade_date DESC);

-- 4. 龙虎榜详细数据表
CREATE TABLE IF NOT EXISTS stock_lhb_detail (
    id BIGSERIAL,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, trade_date),
    UNIQUE(symbol, trade_date)
);

SELECT create_hypertable('stock_lhb_detail', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_stock_lhb_symbol
    ON stock_lhb_detail(symbol, trade_date DESC);

-- 5. 策略信号表
CREATE TABLE IF NOT EXISTS strategy_signals (
    id BIGSERIAL,
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_date TIMESTAMP NOT NULL,
    signal_type INT NOT NULL,
    price DECIMAL(10, 3),
    reason TEXT,
    confidence DECIMAL(5, 4),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, signal_date)
);

SELECT create_hypertable('strategy_signals', 'signal_date',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_strategy_signals_strategy
    ON strategy_signals(strategy_id, signal_date DESC);

CREATE INDEX IF NOT EXISTS idx_strategy_signals_symbol
    ON strategy_signals(symbol, signal_date DESC);

-- 6. 回测交易明细表
CREATE TABLE IF NOT EXISTS backtest_trades (
    id BIGSERIAL,
    backtest_id VARCHAR(50) NOT NULL,
    trade_date TIMESTAMP NOT NULL,
    action VARCHAR(10) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(10, 3),
    shares INT,
    amount DECIMAL(20, 2),
    commission DECIMAL(20, 2),
    profit DECIMAL(20, 2),
    return_rate DECIMAL(10, 4),
    PRIMARY KEY (id, trade_date)
);

SELECT create_hypertable('backtest_trades', 'trade_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_backtest_trades_backtest
    ON backtest_trades(backtest_id, trade_date);

-- 7. 回测结果汇总表 (非hypertable)
CREATE TABLE IF NOT EXISTS backtest_results (
    id BIGSERIAL PRIMARY KEY,
    backtest_id VARCHAR(50) NOT NULL UNIQUE,
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20, 2),
    final_capital DECIMAL(20, 2),
    total_return DECIMAL(10, 4),
    annual_return DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    win_rate DECIMAL(5, 4),
    total_trades INT,
    profit_factor DECIMAL(10, 4),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_backtest_results_strategy
    ON backtest_results(strategy_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_backtest_results_symbol
    ON backtest_results(symbol, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_backtest_results_backtest_id
    ON backtest_results(backtest_id);

-- 完成提示
\echo '✅ PostgreSQL+TimescaleDB tables created successfully (Apache License version)!'
\echo '   - stock_fund_flow (hypertable)'
\echo '   - etf_spot_data (hypertable)'
\echo '   - chip_race_data (hypertable)'
\echo '   - stock_lhb_detail (hypertable)'
\echo '   - strategy_signals (hypertable)'
\echo '   - backtest_trades (hypertable)'
\echo '   - backtest_results (standard table)'
