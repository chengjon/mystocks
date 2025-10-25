-- ============================================================================
-- 实时监控和告警系统数据库表
-- Phase 1: ValueCell Migration - Real-time Monitoring System
-- 创建日期: 2025-10-23
-- ============================================================================

-- 1. 告警规则表
-- 用于定义各种监控告警规则
CREATE TABLE IF NOT EXISTS alert_rule (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL UNIQUE,
    rule_type VARCHAR(50) NOT NULL,  -- price_change, volume_surge, technical_break, limit_up, limit_down, dragon_tiger
    description TEXT,
    symbol VARCHAR(20),               -- NULL表示全市场规则
    stock_name VARCHAR(100),

    -- 规则参数 (JSON格式)
    parameters JSONB DEFAULT '{}',
    -- 示例参数:
    -- 价格变动: {"change_percent": 5, "direction": "up"}
    -- 成交量激增: {"volume_ratio": 2, "vs_period": "5d_avg"}
    -- 技术突破: {"indicator": "ma", "period": 20, "direction": "break_up"}
    -- 涨跌停: {"type": "limit_up", "consecutive_days": 1}
    -- 龙虎榜: {"min_buy_amount": 10000000}

    -- 触发条件
    trigger_conditions JSONB DEFAULT '{}',
    -- 示例: {"trading_hours_only": true, "min_volume": 100000}

    -- 通知配置
    notification_config JSONB DEFAULT '{}',
    -- 示例: {"channels": ["ui", "sound", "email"], "level": "warning"}

    -- 状态和元数据
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 1,       -- 1-5, 5为最高优先级
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. 告警记录表
-- 存储所有触发的告警记录
CREATE TABLE IF NOT EXISTS alert_record (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES alert_rule(id) ON DELETE SET NULL,
    rule_name VARCHAR(100),           -- 冗余存储，防止规则删除后找不到

    -- 股票信息
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),

    -- 告警信息
    alert_time TIMESTAMP DEFAULT NOW(),
    alert_type VARCHAR(50) NOT NULL,  -- 同 rule_type
    alert_level VARCHAR(20) DEFAULT 'info',  -- info, warning, critical
    alert_title VARCHAR(200),
    alert_message TEXT,
    alert_details JSONB,              -- 详细数据

    -- 市场数据快照
    snapshot_data JSONB,
    -- 示例: {
    --   "price": 100.5,
    --   "change_percent": 5.2,
    --   "volume": 1000000,
    --   "amount": 100500000,
    --   "indicators": {...}
    -- }

    -- 状态
    is_read BOOLEAN DEFAULT FALSE,
    is_handled BOOLEAN DEFAULT FALSE,
    handled_by VARCHAR(50),
    handled_at TIMESTAMP,
    handle_note TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. 实时监控数据表
-- 存储实时监控的市场数据
CREATE TABLE IF NOT EXISTS realtime_monitoring (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),

    -- 时间戳
    timestamp TIMESTAMP NOT NULL,
    trade_date DATE NOT NULL,

    -- 行情数据
    price DECIMAL(10, 2),
    open_price DECIMAL(10, 2),
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    pre_close DECIMAL(10, 2),

    -- 涨跌信息
    change_amount DECIMAL(10, 2),
    change_percent DECIMAL(10, 2),

    -- 成交信息
    volume BIGINT,                    -- 成交量(手)
    amount DECIMAL(20, 2),            -- 成交额(元)
    turnover_rate DECIMAL(10, 2),     -- 换手率

    -- 技术指标
    indicators JSONB DEFAULT '{}',
    -- 示例: {
    --   "ma5": 95.5,
    --   "ma10": 93.2,
    --   "rsi": 65.5,
    --   "macd": 0.5,
    --   "volume_ratio": 1.8
    -- }

    -- 市场强度
    market_strength VARCHAR(20),      -- strong, normal, weak

    -- 特殊标记
    is_limit_up BOOLEAN DEFAULT FALSE,
    is_limit_down BOOLEAN DEFAULT FALSE,
    is_st BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. 龙虎榜数据表
-- 存储龙虎榜数据
CREATE TABLE IF NOT EXISTS dragon_tiger_list (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    trade_date DATE NOT NULL,

    -- 上榜原因
    reason VARCHAR(200),              -- 连续三日涨幅偏离值达20%、日振幅达15%等
    reason_code VARCHAR(50),

    -- 买卖数据
    total_buy_amount DECIMAL(20, 2),
    total_sell_amount DECIMAL(20, 2),
    net_amount DECIMAL(20, 2),        -- 净买入额

    -- 机构席位
    institution_buy_count INTEGER DEFAULT 0,
    institution_sell_count INTEGER DEFAULT 0,
    institution_net_amount DECIMAL(20, 2),

    -- 详细数据
    detail_data JSONB,
    -- 示例: {
    --   "buy_seats": [
    --     {"name": "机构专用", "buy_amount": 5000000, "sell_amount": 0},
    --     {"name": "某某营业部", "buy_amount": 3000000, "sell_amount": 500000}
    --   ],
    --   "sell_seats": [...]
    -- }

    -- 影响评估
    impact_score INTEGER,             -- 1-10, 影响力评分

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(symbol, trade_date)
);

-- 5. 监控统计表
-- 存储监控系统的统计数据
CREATE TABLE IF NOT EXISTS monitoring_statistics (
    id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    stat_hour INTEGER,                -- 小时统计 (0-23)

    -- 监控覆盖
    total_monitored_stocks INTEGER,   -- 监控股票数
    active_alerts INTEGER,            -- 活跃告警数

    -- 告警统计
    total_alerts_triggered INTEGER,   -- 触发告警总数
    alerts_by_type JSONB,             -- 按类型统计
    alerts_by_level JSONB,            -- 按级别统计

    -- 市场统计
    limit_up_count INTEGER,           -- 涨停数
    limit_down_count INTEGER,         -- 跌停数
    dragon_tiger_count INTEGER,       -- 龙虎榜数

    -- 性能指标
    avg_response_time_ms INTEGER,     -- 平均响应时间
    data_update_frequency INTEGER,    -- 数据更新频率(秒)

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(stat_date, stat_hour)
);

-- ============================================================================
-- 创建索引以提升查询性能
-- ============================================================================

-- alert_rule 索引
CREATE INDEX IF NOT EXISTS idx_alert_rule_symbol ON alert_rule(symbol);
CREATE INDEX IF NOT EXISTS idx_alert_rule_type ON alert_rule(rule_type);
CREATE INDEX IF NOT EXISTS idx_alert_rule_active ON alert_rule(is_active);

-- alert_record 索引
CREATE INDEX IF NOT EXISTS idx_alert_record_symbol ON alert_record(symbol);
CREATE INDEX IF NOT EXISTS idx_alert_record_time ON alert_record(alert_time DESC);
CREATE INDEX IF NOT EXISTS idx_alert_record_type ON alert_record(alert_type);
CREATE INDEX IF NOT EXISTS idx_alert_record_level ON alert_record(alert_level);
CREATE INDEX IF NOT EXISTS idx_alert_record_read ON alert_record(is_read);
CREATE INDEX IF NOT EXISTS idx_alert_record_rule ON alert_record(rule_id);

-- realtime_monitoring 索引
CREATE INDEX IF NOT EXISTS idx_realtime_symbol_time ON realtime_monitoring(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_realtime_date ON realtime_monitoring(trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_realtime_limit_up ON realtime_monitoring(is_limit_up) WHERE is_limit_up = TRUE;
CREATE INDEX IF NOT EXISTS idx_realtime_limit_down ON realtime_monitoring(is_limit_down) WHERE is_limit_down = TRUE;

-- dragon_tiger_list 索引
CREATE INDEX IF NOT EXISTS idx_dragon_tiger_symbol ON dragon_tiger_list(symbol);
CREATE INDEX IF NOT EXISTS idx_dragon_tiger_date ON dragon_tiger_list(trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_dragon_tiger_net_amount ON dragon_tiger_list(net_amount DESC);

-- monitoring_statistics 索引
CREATE INDEX IF NOT EXISTS idx_monitoring_stat_date ON monitoring_statistics(stat_date DESC);

-- ============================================================================
-- 插入默认告警规则
-- ============================================================================

INSERT INTO alert_rule (rule_name, rule_type, description, parameters, notification_config, priority) VALUES
('涨停监控', 'limit_up', '监控涨停股票',
 '{"consecutive_days": 1, "include_st": false}'::jsonb,
 '{"channels": ["ui", "sound"], "level": "warning"}'::jsonb, 4),

('跌停监控', 'limit_down', '监控跌停股票',
 '{"consecutive_days": 1, "include_st": false}'::jsonb,
 '{"channels": ["ui"], "level": "info"}'::jsonb, 3),

('成交量激增', 'volume_surge', '成交量超过5日均量2倍',
 '{"volume_ratio": 2.0, "vs_period": "5d_avg", "min_volume": 10000}'::jsonb,
 '{"channels": ["ui"], "level": "info"}'::jsonb, 3),

('价格急涨', 'price_change', '单日涨幅超过5%',
 '{"change_percent": 5.0, "direction": "up", "trading_hours_only": true}'::jsonb,
 '{"channels": ["ui"], "level": "info"}'::jsonb, 2),

('价格急跌', 'price_change', '单日跌幅超过5%',
 '{"change_percent": -5.0, "direction": "down", "trading_hours_only": true}'::jsonb,
 '{"channels": ["ui"], "level": "warning"}'::jsonb, 2),

('龙虎榜上榜', 'dragon_tiger', '上榜龙虎榜的股票',
 '{"min_net_amount": 10000000, "institution_involved": true}'::jsonb,
 '{"channels": ["ui"], "level": "info"}'::jsonb, 4),

('突破20日均线', 'technical_break', '股价向上突破20日均线',
 '{"indicator": "ma", "period": 20, "direction": "break_up", "confirm_bars": 1}'::jsonb,
 '{"channels": ["ui"], "level": "info"}'::jsonb, 2),

('跌破20日均线', 'technical_break', '股价向下跌破20日均线',
 '{"indicator": "ma", "period": 20, "direction": "break_down", "confirm_bars": 1}'::jsonb,
 '{"channels": ["ui"], "level": "info"}'::jsonb, 2)
ON CONFLICT (rule_name) DO NOTHING;

-- ============================================================================
-- 创建视图以便快速查询
-- ============================================================================

-- 今日告警摘要视图
CREATE OR REPLACE VIEW v_today_alerts_summary AS
SELECT
    alert_type,
    alert_level,
    COUNT(*) as alert_count,
    COUNT(DISTINCT symbol) as affected_stocks,
    MAX(alert_time) as latest_alert_time
FROM alert_record
WHERE alert_time::date = CURRENT_DATE
GROUP BY alert_type, alert_level
ORDER BY alert_count DESC;

-- 活跃告警规则视图
CREATE OR REPLACE VIEW v_active_alert_rules AS
SELECT
    ar.id,
    ar.rule_name,
    ar.rule_type,
    ar.symbol,
    ar.stock_name,
    ar.priority,
    COUNT(DISTINCT rec.id) as triggered_count_today
FROM alert_rule ar
LEFT JOIN alert_record rec ON ar.id = rec.rule_id
    AND rec.alert_time::date = CURRENT_DATE
WHERE ar.is_active = TRUE
GROUP BY ar.id, ar.rule_name, ar.rule_type, ar.symbol, ar.stock_name, ar.priority
ORDER BY ar.priority DESC, triggered_count_today DESC;

-- 实时监控摘要视图
CREATE OR REPLACE VIEW v_realtime_summary AS
SELECT
    COUNT(*) as total_stocks,
    COUNT(*) FILTER (WHERE is_limit_up) as limit_up_count,
    COUNT(*) FILTER (WHERE is_limit_down) as limit_down_count,
    COUNT(*) FILTER (WHERE change_percent > 5) as strong_up_count,
    COUNT(*) FILTER (WHERE change_percent < -5) as strong_down_count,
    AVG(change_percent) as avg_change_percent,
    SUM(amount) as total_amount
FROM realtime_monitoring
WHERE trade_date = CURRENT_DATE
  AND timestamp >= CURRENT_DATE;

-- ============================================================================
-- 创建完成
-- ============================================================================

-- 输出创建结果
DO $$
BEGIN
    RAISE NOTICE '✅ 监控系统数据库表创建完成！';
    RAISE NOTICE '📊 已创建 5 个表: alert_rule, alert_record, realtime_monitoring, dragon_tiger_list, monitoring_statistics';
    RAISE NOTICE '📈 已创建 3 个视图: v_today_alerts_summary, v_active_alert_rules, v_realtime_summary';
    RAISE NOTICE '🔔 已插入 8 个默认告警规则';
    RAISE NOTICE '';
    RAISE NOTICE '下一步:';
    RAISE NOTICE '1. 执行此脚本创建表: psql -h localhost -p 5438 -U postgres -d mystocks -f create_monitoring_tables.sql';
    RAISE NOTICE '2. 实现监控服务: monitoring_service.py';
    RAISE NOTICE '3. 创建 API 端点: app/api/monitoring.py';
END $$;
