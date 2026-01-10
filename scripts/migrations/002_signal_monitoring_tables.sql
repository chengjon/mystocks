-- =====================================================
-- 信号监控系统 - 数据库表创建脚本
-- =====================================================
-- 版本: v1.0
-- 创建日期: 2026-01-08
-- 作者: Claude Code (Main CLI)
-- 描述: Phase 2 - 创建信号监控相关的PostgreSQL表
--
-- 包含表:
-- 1. signal_records - 信号生成记录
-- 2. signal_execution_results - 信号执行结果
-- 3. signal_push_logs - 信号推送日志
-- 4. strategy_health - 策略健康状态
-- =====================================================

-- 设置搜索路径
SET search_path TO public;

-- =====================================================
-- 1. 信号生成记录表
-- =====================================================
-- 用途: 记录所有策略生成的信号（BUY/SELL/HOLD）
-- 数据保留: 90天（可通过TTL自动清理）
CREATE TABLE IF NOT EXISTS signal_records (
    id BIGSERIAL PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,  -- BUY/SELL/HOLD

    -- 信号上下文
    indicator_count INTEGER DEFAULT 1,
    execution_time_ms DECIMAL(10,2),

    -- 信号元数据
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expiry_at TIMESTAMP,  -- 信号过期时间

    -- 性能追踪字段
    gpu_used BOOLEAN DEFAULT FALSE,
    gpu_latency_ms DECIMAL(10,2),

    -- 附加信息（JSONB格式，灵活扩展）
    metadata JSONB,

    -- 索引字段
    status VARCHAR(20) DEFAULT 'generated'  -- generated/rejected/filtered/executed
);

-- 创建索引（优化查询性能）
CREATE INDEX IF NOT EXISTS idx_signal_records_strategy_symbol
    ON signal_records(strategy_id, symbol, generated_at DESC);

CREATE INDEX IF NOT EXISTS idx_signal_records_generated_at
    ON signal_records(generated_at DESC);

CREATE INDEX IF NOT EXISTS idx_signal_records_symbol_type
    ON signal_records(symbol, signal_type, generated_at DESC);

CREATE INDEX IF NOT EXISTS idx_signal_records_status
    ON signal_records(status, generated_at DESC);

-- 添加表注释
COMMENT ON TABLE signal_records IS '信号生成记录表 - 记录所有策略生成的交易信号';
COMMENT ON COLUMN signal_records.strategy_id IS '策略标识符（用于Prometheus label）';
COMMENT ON COLUMN signal_records.signal_type IS '信号类型: BUY/SELL/HOLD';
COMMENT ON COLUMN signal_records.status IS '信号状态: generated/rejected/filtered/executed';
COMMENT ON COLUMN signal_records.metadata IS '附加信息（JSONB）: {confidence, reason, indicators_used, etc.}';

-- =====================================================
-- 2. 信号执行结果表
-- =====================================================
-- 用途: 记录信号的执行结果和盈亏情况
-- 关联: signal_records.id (signal_id)
CREATE TABLE IF NOT EXISTS signal_execution_results (
    id BIGSERIAL PRIMARY KEY,
    signal_id BIGINT NOT NULL REFERENCES signal_records(id) ON DELETE CASCADE,

    -- 执行状态
    executed BOOLEAN NOT NULL DEFAULT FALSE,
    executed_at TIMESTAMP,

    -- 执行结果
    execution_price DECIMAL(10,2),
    execution_quantity INTEGER,

    -- 盈亏分析
    profit_loss DECIMAL(15,2),
    profit_loss_percent DECIMAL(10,4),
    holding_period_days INTEGER,

    -- 风险指标
    max_adverse_excursion DECIMAL(10,4),  -- 最大不利偏移
    max_favorable_excursion DECIMAL(10,4), -- 最大有利偏移

    -- 执行上下文
    execution_reason TEXT,
    rejection_reason TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_signal_execution_signal_id
    ON signal_execution_results(signal_id);

CREATE INDEX IF NOT EXISTS idx_signal_execution_executed_at
    ON signal_execution_results(executed_at DESC);

CREATE INDEX IF NOT EXISTS idx_signal_execution_executed
    ON signal_execution_results(executed, executed_at DESC);

-- 添加表注释
COMMENT ON TABLE signal_execution_results IS '信号执行结果表 - 记录信号执行情况和盈亏分析';
COMMENT ON COLUMN signal_execution_results.signal_id IS '关联signal_records.id';
COMMENT ON COLUMN signal_execution_results.max_adverse_excursion IS '最大不利偏移（MAE）- 持仓期间最大浮亏';
COMMENT ON COLUMN signal_execution_results.max_favorable_excursion IS '最大有利偏移（MFE）- 持仓期间最大浮盈';

-- =====================================================
-- 3. 信号推送日志表
-- =====================================================
-- 用途: 记录信号推送通知的状态和性能
-- 关联: signal_records.id (signal_id)
CREATE TABLE IF NOT EXISTS signal_push_logs (
    id BIGSERIAL PRIMARY KEY,
    signal_id BIGINT NOT NULL REFERENCES signal_records(id) ON DELETE CASCADE,

    -- 推送渠道
    channel VARCHAR(20) NOT NULL,  -- websocket/email/sms/app

    -- 推送状态
    status VARCHAR(20) NOT NULL,  -- success/failed/timeout
    push_latency_ms DECIMAL(10,2),

    -- 推送内容（JSONB格式）
    payload JSONB,

    -- 错误信息
    error_message TEXT,
    error_code VARCHAR(50),

    -- 重试信息
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP,

    pushed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_signal_push_signal_id
    ON signal_push_logs(signal_id);

CREATE INDEX IF NOT EXISTS idx_signal_push_channel_status
    ON signal_push_logs(channel, status, pushed_at DESC);

CREATE INDEX IF NOT EXISTS idx_signal_push_pushed_at
    ON signal_push_logs(pushed_at DESC);

-- 添加表注释
COMMENT ON TABLE signal_push_logs IS '信号推送日志表 - 记录信号通知的发送状态和性能';
COMMENT ON COLUMN signal_push_logs.channel IS '推送渠道: websocket/email/sms/app';
COMMENT ON COLUMN signal_push_logs.status IS '推送状态: success/failed/timeout';
COMMENT ON COLUMN signal_push_logs.push_latency_ms IS '推送延迟（毫秒）';

-- =====================================================
-- 4. 策略健康状态表
-- =====================================================
-- 用途: 持久化策略健康状态（用于长期趋势分析）
-- 注意: 实时健康状态主要用Prometheus Gauge
CREATE TABLE IF NOT EXISTS strategy_health (
    id BIGSERIAL PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL,

    -- 健康状态
    health_status INTEGER NOT NULL,  -- 1=healthy, 0=degraded, -1=unhealthy

    -- 健康度指标
    signal_success_rate DECIMAL(5,2),  -- 0-100
    signal_accuracy DECIMAL(5,2),      -- 0-100
    avg_execution_time_ms DECIMAL(10,2),

    -- 错误信息
    error_count INTEGER DEFAULT 0,
    last_error_message TEXT,

    -- 时间戳
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 唯一约束（每个策略每个时间点一条记录）
    UNIQUE(strategy_id, recorded_at)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_strategy_health_strategy_recorded
    ON strategy_health(strategy_id, recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_strategy_health_status
    ON strategy_health(health_status, recorded_at DESC);

-- 创建索引（用于删除旧数据）
CREATE INDEX IF NOT EXISTS idx_strategy_health_recorded_at
    ON strategy_health(recorded_at DESC);

-- 添加表注释
COMMENT ON TABLE strategy_health IS '策略健康状态表 - 持久化策略健康状态（用于长期趋势分析）';
COMMENT ON COLUMN strategy_health.health_status IS '健康状态: 1=healthy, 0=degraded, -1=unhealthy';
COMMENT ON COLUMN strategy_health.signal_success_rate IS '信号成功率（0-100）';
COMMENT ON COLUMN strategy_health.signal_accuracy IS '信号准确率（0-100）';

-- =====================================================
-- 5. 数据保留策略（自动清理旧数据）
-- =====================================================

-- 信号记录保留90天
CREATE OR REPLACE FUNCTION cleanup_old_signal_records()
RETURNS void AS $$
BEGIN
    DELETE FROM signal_records
    WHERE generated_at < CURRENT_TIMESTAMP - INTERVAL '90 days';

    RAISE NOTICE '✅ 清理了90天前的信号记录';
END;
$$ LANGUAGE plpgsql;

-- 策略健康状态保留30天
CREATE OR REPLACE FUNCTION cleanup_old_strategy_health()
RETURNS void AS $$
BEGIN
    DELETE FROM strategy_health
    WHERE recorded_at < CURRENT_TIMESTAMP - INTERVAL '30 days';

    RAISE NOTICE '✅ 清理了30天前的策略健康状态记录';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. 实用视图（方便查询）
-- =====================================================

-- 信号执行摘要视图
CREATE OR REPLACE VIEW v_signal_execution_summary AS
SELECT
    sr.strategy_id,
    sr.symbol,
    sr.signal_type,
    sr.generated_at,
    ser.executed,
    ser.executed_at,
    ser.profit_loss,
    ser.profit_loss_percent,
    sr.status as signal_status
FROM signal_records sr
LEFT JOIN signal_execution_results ser ON sr.id = ser.signal_id
ORDER BY sr.generated_at DESC;

COMMENT ON VIEW v_signal_execution_summary IS '信号执行摘要视图 - 便于查询信号和执行结果';

-- 策略性能统计视图（最近7天）
CREATE OR REPLACE VIEW v_strategy_performance_7d AS
SELECT
    strategy_id,
    COUNT(*) as total_signals,
    SUM(CASE WHEN signal_type = 'BUY' THEN 1 ELSE 0 END) as buy_signals,
    SUM(CASE WHEN signal_type = 'SELL' THEN 1 ELSE 0 END) as sell_signals,
    SUM(CASE WHEN status = 'executed' THEN 1 ELSE 0 END) as executed_signals,
    AVG(execution_time_ms) as avg_execution_time_ms,
    SUM(CASE WHEN gpu_used = TRUE THEN 1 ELSE 0 END) as gpu_signals_count
FROM signal_records
WHERE generated_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY strategy_id
ORDER BY strategy_id;

COMMENT ON VIEW v_strategy_performance_7d IS '策略性能统计视图（最近7天）';

-- =====================================================
-- 7. 验证脚本执行
-- =====================================================

DO $$
DECLARE
    tbl_name TEXT;
    tbl_exists BOOLEAN;
    view_name TEXT;
    view_exists BOOLEAN;
BEGIN
    -- 检查表创建
    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE '验证信号监控表创建';
    RAISE NOTICE '═══════════════════════════════════════';

    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'signal_records') INTO tbl_exists;
    RAISE NOTICE 'signal_records: %', CASE WHEN tbl_exists THEN '✅ 已创建' ELSE '❌ 未创建' END;

    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'signal_execution_results') INTO tbl_exists;
    RAISE NOTICE 'signal_execution_results: %', CASE WHEN tbl_exists THEN '✅ 已创建' ELSE '❌ 未创建' END;

    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'signal_push_logs') INTO tbl_exists;
    RAISE NOTICE 'signal_push_logs: %', CASE WHEN tbl_exists THEN '✅ 已创建' ELSE '❌ 未创建' END;

    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'strategy_health') INTO tbl_exists;
    RAISE NOTICE 'strategy_health: %', CASE WHEN tbl_exists THEN '✅ 已创建' ELSE '❌ 未创建' END;

    -- 检查视图创建
    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE '验证视图创建';
    RAISE NOTICE '═══════════════════════════════════════';

    SELECT EXISTS(SELECT 1 FROM information_schema.views WHERE table_name = 'v_signal_execution_summary') INTO view_exists;
    RAISE NOTICE 'v_signal_execution_summary: %', CASE WHEN view_exists THEN '✅ 已创建' ELSE '❌ 未创建' END;

    SELECT EXISTS(SELECT 1 FROM information_schema.views WHERE table_name = 'v_strategy_performance_7d') INTO view_exists;
    RAISE NOTICE 'v_strategy_performance_7d: %', CASE WHEN view_exists THEN '✅ 已创建' ELSE '❌ 未创建' END;

    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE '✅ 信号监控表创建完成!';
    RAISE NOTICE '═══════════════════════════════════════';
END $$;

-- =====================================================
-- 8. 使用示例
-- =====================================================

/*
-- 示例1: 插入信号记录
INSERT INTO signal_records (strategy_id, symbol, signal_type, indicator_count, execution_time_ms, gpu_used, gpu_latency_ms)
VALUES ('macd_strategy', '600519.SH', 'BUY', 3, 45.5, true, 12.3);

-- 示例2: 记录信号执行结果
INSERT INTO signal_execution_results (signal_id, executed, executed_at, execution_price, profit_loss)
VALUES (1, true, CURRENT_TIMESTAMP, 1850.00, 125.50);

-- 示例3: 记录推送日志
INSERT INTO signal_push_logs (signal_id, channel, status, push_latency_ms)
VALUES (1, 'websocket', 'success', 15.5);

-- 示例4: 记录策略健康状态
INSERT INTO strategy_health (strategy_id, health_status, signal_success_rate, signal_accuracy)
VALUES ('macd_strategy', 1, 85.5, 78.2);

-- 示例5: 查询策略7天性能
SELECT * FROM v_strategy_performance_7d WHERE strategy_id = 'macd_strategy';

-- 示例6: 清理旧数据（可配置cron定时执行）
SELECT cleanup_old_signal_records();
SELECT cleanup_old_strategy_health();
*/

-- =====================================================
-- 9. 回滚脚本（如需要）
-- =====================================================

/*
-- 删除表（谨慎使用）
DROP TABLE IF EXISTS signal_push_logs CASCADE;
DROP TABLE IF EXISTS signal_execution_results CASCADE;
DROP TABLE IF EXISTS signal_records CASCADE;
DROP TABLE IF EXISTS strategy_health CASCADE;

-- 删除视图
DROP VIEW IF EXISTS v_signal_execution_summary CASCADE;
DROP VIEW IF EXISTS v_strategy_performance_7d CASCADE;

-- 删除清理函数
DROP FUNCTION IF EXISTS cleanup_old_signal_records CASCADE;
DROP FUNCTION IF EXISTS cleanup_old_strategy_health CASCADE;
*/

-- =====================================================
-- 结束
-- =====================================================
