-- MyStocks Web端数据库迁移脚本
-- Version: 1.0.0
-- Date: 2025-10-24
-- Description: 创建Web端所需的所有表

-- ============ 策略管理表 ============

-- 1. 策略表
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_type VARCHAR(50),  -- 'model_based', 'rule_based', 'hybrid'
    model_id INTEGER,
    parameters JSONB,  -- 策略参数（JSON格式）
    status VARCHAR(20) DEFAULT 'draft',  -- 'draft', 'active', 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_strategies_status ON strategies(status);
CREATE INDEX IF NOT EXISTS idx_strategies_user ON strategies(user_id);

COMMENT ON TABLE strategies IS '交易策略表';
COMMENT ON COLUMN strategies.strategy_type IS '策略类型';
COMMENT ON COLUMN strategies.parameters IS '策略参数（JSON格式）';
COMMENT ON COLUMN strategies.status IS '状态：draft草稿/active活跃/archived归档';

-- 2. 模型表
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50),  -- 'random_forest', 'lightgbm'
    version VARCHAR(20),
    hyperparameters JSONB,  -- 超参数
    training_config JSONB,  -- 训练配置
    performance_metrics JSONB,  -- 性能指标
    model_path VARCHAR(255),  -- 模型文件路径
    status VARCHAR(20) DEFAULT 'training',  -- 'training', 'completed', 'failed'
    training_started_at TIMESTAMP,
    training_completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_models_status ON models(status);
CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type);

COMMENT ON TABLE models IS '机器学习模型表';
COMMENT ON COLUMN models.model_type IS '模型类型：random_forest/lightgbm';
COMMENT ON COLUMN models.status IS '状态：training训练中/completed完成/failed失败';

-- ============ 回测表 ============

-- 3. 回测表
CREATE TABLE IF NOT EXISTS backtests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    strategy_id INTEGER REFERENCES strategies(id) ON DELETE SET NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_cash DECIMAL(15, 2) DEFAULT 1000000,
    commission_rate DECIMAL(6, 4) DEFAULT 0.0003,
    stamp_tax_rate DECIMAL(6, 4) DEFAULT 0.001,
    slippage_rate DECIMAL(6, 4) DEFAULT 0.001,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
    results JSONB,  -- 回测结果（JSON格式）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    user_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_backtests_strategy ON backtests(strategy_id);
CREATE INDEX IF NOT EXISTS idx_backtests_status ON backtests(status);
CREATE INDEX IF NOT EXISTS idx_backtests_created ON backtests(created_at);

COMMENT ON TABLE backtests IS '回测任务表';
COMMENT ON COLUMN backtests.status IS '状态：pending等待/running运行中/completed完成/failed失败';
COMMENT ON COLUMN backtests.results IS '回测结果（JSON格式）';

-- 4. 回测交易明细表
CREATE TABLE IF NOT EXISTS backtest_trades (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER REFERENCES backtests(id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,  -- 'buy', 'sell'
    amount INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    commission DECIMAL(10, 2),
    stamp_tax DECIMAL(10, 2),
    total_cost DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_backtest_trades_backtest ON backtest_trades(backtest_id);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_date ON backtest_trades(trade_date);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_symbol ON backtest_trades(symbol);

COMMENT ON TABLE backtest_trades IS '回测交易明细表';
COMMENT ON COLUMN backtest_trades.direction IS '交易方向：buy买入/sell卖出';

-- ============ 风险监控表 ============

-- 5. 风险指标表
CREATE TABLE IF NOT EXISTS risk_metrics (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20),  -- 'backtest', 'portfolio', 'strategy'
    entity_id INTEGER NOT NULL,
    metric_date DATE NOT NULL,
    var_95_hist DECIMAL(8, 4),
    var_95_param DECIMAL(8, 4),
    var_99_hist DECIMAL(8, 4),
    cvar_95 DECIMAL(8, 4),
    cvar_99 DECIMAL(8, 4),
    beta DECIMAL(8, 4),
    sharpe_ratio DECIMAL(8, 4),
    sortino_ratio DECIMAL(8, 4),
    max_drawdown DECIMAL(8, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_risk_metrics_entity ON risk_metrics(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_risk_metrics_date ON risk_metrics(metric_date);

COMMENT ON TABLE risk_metrics IS '风险指标表';
COMMENT ON COLUMN risk_metrics.entity_type IS '实体类型：backtest回测/portfolio组合/strategy策略';
COMMENT ON COLUMN risk_metrics.var_95_hist IS 'VaR(95%)历史法';
COMMENT ON COLUMN risk_metrics.cvar_95 IS 'CVaR(95%)条件VaR';

-- 6. 风险预警表
CREATE TABLE IF NOT EXISTS risk_alerts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50),  -- 'var_95', 'cvar_95', 'beta', 'max_drawdown'
    threshold_value DECIMAL(8, 4),
    comparison_operator VARCHAR(10),  -- '>', '<', '>=', '<='
    is_active BOOLEAN DEFAULT true,
    notification_channels JSONB,  -- ['email', 'webhook']
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_risk_alerts_active ON risk_alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_risk_alerts_metric ON risk_alerts(metric_type);

COMMENT ON TABLE risk_alerts IS '风险预警规则表';
COMMENT ON COLUMN risk_alerts.metric_type IS '监控指标类型';
COMMENT ON COLUMN risk_alerts.comparison_operator IS '比较运算符：>大于/<小于/>=大于等于/<=小于等于';

-- 7. 预警历史表
CREATE TABLE IF NOT EXISTS alert_history (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES risk_alerts(id) ON DELETE CASCADE,
    triggered_at TIMESTAMP NOT NULL,
    metric_value DECIMAL(8, 4),
    entity_type VARCHAR(20),
    entity_id INTEGER,
    notification_sent BOOLEAN DEFAULT false,
    notification_result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alert_history_alert ON alert_history(alert_id);
CREATE INDEX IF NOT EXISTS idx_alert_history_triggered ON alert_history(triggered_at);

COMMENT ON TABLE alert_history IS '预警触发历史表';
COMMENT ON COLUMN alert_history.notification_sent IS '通知是否已发送';

-- 8. 通知配置表
CREATE TABLE IF NOT EXISTS notification_configs (
    id SERIAL PRIMARY KEY,
    config_type VARCHAR(20),  -- 'email', 'webhook'
    is_enabled BOOLEAN DEFAULT true,
    config_data JSONB,  -- 配置详情（SMTP/Webhook信息）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_notification_configs_user ON notification_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_configs_type ON notification_configs(config_type);

COMMENT ON TABLE notification_configs IS '通知配置表';
COMMENT ON COLUMN notification_configs.config_type IS '配置类型：email邮件/webhook网络钩子';
COMMENT ON COLUMN notification_configs.config_data IS 'JSON格式配置数据';

-- ============ 索引优化 ============

-- 复合索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_backtests_strategy_status
    ON backtests(strategy_id, status);

CREATE INDEX IF NOT EXISTS idx_risk_metrics_entity_date
    ON risk_metrics(entity_type, entity_id, metric_date DESC);

-- ============ 触发器：自动更新时间戳 ============

-- 创建更新时间戳函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为strategies表创建触发器
DROP TRIGGER IF EXISTS update_strategies_updated_at ON strategies;
CREATE TRIGGER update_strategies_updated_at
    BEFORE UPDATE ON strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为notification_configs表创建触发器
DROP TRIGGER IF EXISTS update_notification_configs_updated_at ON notification_configs;
CREATE TRIGGER update_notification_configs_updated_at
    BEFORE UPDATE ON notification_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============ 初始数据 ============

-- 插入示例策略（可选）
INSERT INTO strategies (name, description, strategy_type, status)
VALUES
    ('简单移动平均策略', '基于5日和20日移动平均线的交易策略', 'rule_based', 'draft'),
    ('RandomForest预测策略', '使用随机森林模型预测涨跌', 'model_based', 'draft')
ON CONFLICT DO NOTHING;

-- 插入默认通知配置模板（可选）
INSERT INTO notification_configs (config_type, is_enabled, config_data)
VALUES
    ('email', false, '{"smtp_host": "smtp.gmail.com", "smtp_port": 587}'::jsonb),
    ('webhook', false, '{"url": "https://example.com/webhook"}'::jsonb)
ON CONFLICT DO NOTHING;

-- ============ 权限设置 ============

-- 授予应用用户权限（假设用户名为mystocks_app）
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mystocks_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mystocks_app;

-- ============ 验证 ============

-- 查看所有表
SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN (
        'strategies', 'models', 'backtests', 'backtest_trades',
        'risk_metrics', 'risk_alerts', 'alert_history', 'notification_configs'
    )
ORDER BY tablename;

-- 查看所有索引
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN (
        'strategies', 'models', 'backtests', 'backtest_trades',
        'risk_metrics', 'risk_alerts', 'alert_history', 'notification_configs'
    )
ORDER BY tablename, indexname;
