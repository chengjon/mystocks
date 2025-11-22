-- Phase 4 Day 4-5: 策略管理表结构
-- 创建策略相关的PostgreSQL表

-- 1. 策略表
CREATE TABLE IF NOT EXISTS user_strategies (
    strategy_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    description TEXT,

    -- 策略参数 (JSON格式)
    parameters JSONB DEFAULT '[]',

    -- 风险控制参数
    max_position_size DECIMAL(5,4) NOT NULL DEFAULT 0.1,
    stop_loss_percent DECIMAL(5,2),
    take_profit_percent DECIMAL(5,2),

    -- 状态和元数据
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT chk_strategy_type CHECK (strategy_type IN ('momentum', 'mean_reversion', 'breakout', 'grid', 'custom')),
    CONSTRAINT chk_status CHECK (status IN ('draft', 'active', 'paused', 'archived')),
    CONSTRAINT chk_position_size CHECK (max_position_size > 0 AND max_position_size <= 1)
);

-- 索引
CREATE INDEX idx_user_strategies_user_id ON user_strategies(user_id);
CREATE INDEX idx_user_strategies_status ON user_strategies(status);
CREATE INDEX idx_user_strategies_type ON user_strategies(strategy_type);
CREATE INDEX idx_user_strategies_created_at ON user_strategies(created_at DESC);

-- 自动更新updated_at触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_strategies_updated_at
    BEFORE UPDATE ON user_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 注释
COMMENT ON TABLE user_strategies IS 'Phase 4: 用户策略配置表';
COMMENT ON COLUMN user_strategies.strategy_id IS '策略ID (主键)';
COMMENT ON COLUMN user_strategies.user_id IS '用户ID';
COMMENT ON COLUMN user_strategies.strategy_name IS '策略名称';
COMMENT ON COLUMN user_strategies.strategy_type IS '策略类型: momentum/mean_reversion/breakout/grid/custom';
COMMENT ON COLUMN user_strategies.parameters IS '策略参数 (JSON格式)';
COMMENT ON COLUMN user_strategies.max_position_size IS '最大仓位比例 (0-1)';
COMMENT ON COLUMN user_strategies.status IS '状态: draft/active/paused/archived';

-- 2. 回测结果表
CREATE TABLE IF NOT EXISTS backtest_results (
    backtest_id SERIAL PRIMARY KEY,
    strategy_id INTEGER NOT NULL REFERENCES user_strategies(strategy_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,

    -- 回测配置
    symbols TEXT[] NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15,2) NOT NULL,
    commission_rate DECIMAL(6,4) NOT NULL DEFAULT 0.0003,
    slippage_rate DECIMAL(6,4) NOT NULL DEFAULT 0.001,
    benchmark VARCHAR(20),

    -- 回测结果
    final_capital DECIMAL(15,2),

    -- 绩效指标 (JSON格式)
    performance_metrics JSONB,

    -- 回测状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- 约束
    CONSTRAINT chk_backtest_status CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    CONSTRAINT chk_date_range CHECK (end_date >= start_date)
);

-- 索引
CREATE INDEX idx_backtest_results_strategy_id ON backtest_results(strategy_id);
CREATE INDEX idx_backtest_results_user_id ON backtest_results(user_id);
CREATE INDEX idx_backtest_results_status ON backtest_results(status);
CREATE INDEX idx_backtest_results_created_at ON backtest_results(created_at DESC);

-- 注释
COMMENT ON TABLE backtest_results IS 'Phase 4: 回测结果表';
COMMENT ON COLUMN backtest_results.backtest_id IS '回测ID (主键)';
COMMENT ON COLUMN backtest_results.strategy_id IS '关联的策略ID';
COMMENT ON COLUMN backtest_results.performance_metrics IS '绩效指标 (JSON): total_return, sharpe_ratio, max_drawdown等';
COMMENT ON COLUMN backtest_results.status IS '回测状态: pending/running/completed/failed';

-- 3. 权益曲线表
CREATE TABLE IF NOT EXISTS backtest_equity_curves (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER NOT NULL REFERENCES backtest_results(backtest_id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    equity DECIMAL(15,2) NOT NULL,
    drawdown DECIMAL(5,2) NOT NULL,
    benchmark_equity DECIMAL(15,2),

    UNIQUE(backtest_id, trade_date)
);

-- 索引
CREATE INDEX idx_equity_curves_backtest_id ON backtest_equity_curves(backtest_id);
CREATE INDEX idx_equity_curves_trade_date ON backtest_equity_curves(trade_date);

-- 注释
COMMENT ON TABLE backtest_equity_curves IS 'Phase 4: 回测权益曲线数据';

-- 4. 交易记录表
CREATE TABLE IF NOT EXISTS backtest_trades (
    trade_id SERIAL PRIMARY KEY,
    backtest_id INTEGER NOT NULL REFERENCES backtest_results(backtest_id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    action VARCHAR(10) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    commission DECIMAL(10,2) NOT NULL,
    profit_loss DECIMAL(15,2),

    CONSTRAINT chk_action CHECK (action IN ('buy', 'sell'))
);

-- 索引
CREATE INDEX idx_backtest_trades_backtest_id ON backtest_trades(backtest_id);
CREATE INDEX idx_backtest_trades_symbol ON backtest_trades(symbol);
CREATE INDEX idx_backtest_trades_date ON backtest_trades(trade_date);

-- 注释
COMMENT ON TABLE backtest_trades IS 'Phase 4: 回测交易记录';
COMMENT ON COLUMN backtest_trades.action IS '操作类型: buy/sell';

-- 插入示例数据 (可选)
INSERT INTO user_strategies (user_id, strategy_name, strategy_type, description, parameters, max_position_size, status, tags)
VALUES
(1001, '双均线策略', 'momentum', '基于5日和20日均线的金叉死叉策略',
 '[{"name": "short_period", "value": 5, "data_type": "int"}, {"name": "long_period", "value": 20, "data_type": "int"}]'::jsonb,
 0.2, 'draft', ARRAY['均线', '趋势跟踪']);

-- 验证表创建
SELECT
    'user_strategies' as table_name,
    COUNT(*) as row_count
FROM user_strategies
UNION ALL
SELECT
    'backtest_results',
    COUNT(*)
FROM backtest_results
UNION ALL
SELECT
    'backtest_equity_curves',
    COUNT(*)
FROM backtest_equity_curves
UNION ALL
SELECT
    'backtest_trades',
    COUNT(*)
FROM backtest_trades;
