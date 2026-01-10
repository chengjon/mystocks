-- 003_signal_statistics_hourly.sql
-- 信号统计小时表
-- 用于存储每小时聚合的信号统计数据
-- 支持性能分析和趋势监控

-- 创建小时统计表
CREATE TABLE IF NOT EXISTS signal_statistics_hourly (
    id BIGSERIAL PRIMARY KEY,

    -- 分组字段
    strategy_id VARCHAR(50) NOT NULL,
    hour_timestamp TIMESTAMP NOT NULL,  -- 统计小时（精确到小时）

    -- 信号统计
    signal_count INTEGER NOT NULL DEFAULT 0,  -- 总信号数
    buy_count INTEGER NOT NULL DEFAULT 0,     -- BUY信号数
    sell_count INTEGER NOT NULL DEFAULT 0,    -- SELL信号数
    hold_count INTEGER NOT NULL DEFAULT 0,    -- HOLD信号数

    -- 执行统计
    executed_count INTEGER NOT NULL DEFAULT 0,  -- 已执行数
    execution_rate DECIMAL(5,2),               -- 执行率 (%)

    -- 性能指标
    profitable_count INTEGER NOT NULL DEFAULT 0,  -- 盈利信号数
    accuracy_rate DECIMAL(5,2),                  -- 准确率 (%)
    profit_ratio DECIMAL(5,2),                   -- 盈利比率 (%)

    -- 盈亏统计
    total_profit_loss DECIMAL(15,2),       -- 总盈亏
    avg_profit_loss DECIMAL(10,2),         -- 平均盈亏
    max_profit DECIMAL(10,2),              -- 最大盈利
    max_loss DECIMAL(10,2),                -- 最大亏损

    -- 延迟统计
    avg_execution_time_ms DECIMAL(10,2),   -- 平均执行时间
    p50_execution_time_ms DECIMAL(10,2),   -- P50执行时间
    p95_execution_time_ms DECIMAL(10,2),   -- P95执行时间
    p99_execution_time_ms DECIMAL(10,2),   -- P99执行时间

    -- GPU使用统计
    gpu_used_count INTEGER NOT NULL DEFAULT 0,  -- 使用GPU的信号数
    gpu_rate DECIMAL(5,2),                    -- GPU使用率 (%)

    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 唯一约束（防止重复统计）
    CONSTRAINT unique_strategy_hour UNIQUE (strategy_id, hour_timestamp)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_signal_statistics_hourly_strategy
    ON signal_statistics_hourly(strategy_id);

CREATE INDEX IF NOT EXISTS idx_signal_statistics_hourly_timestamp
    ON signal_statistics_hourly(hour_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_signal_statistics_hourly_strategy_timestamp
    ON signal_statistics_hourly(strategy_id, hour_timestamp DESC);

-- 创建视图：最近24小时统计
CREATE OR REPLACE VIEW v_signal_statistics_24h AS
SELECT
    strategy_id,
    SUM(signal_count) as total_signals,
    SUM(executed_count) as total_executed,
    SUM(profitable_count) as total_profitable,
    AVG(execution_rate) as avg_execution_rate,
    AVG(accuracy_rate) as avg_accuracy_rate,
    AVG(profit_ratio) as avg_profit_ratio,
    SUM(total_profit_loss) as total_profit_loss,
    AVG(avg_execution_time_ms) as avg_execution_time_ms,
    NOW() as view_generated_at
FROM signal_statistics_hourly
WHERE hour_timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY strategy_id;

-- 创建视图：策略性能趋势（最近7天）
CREATE OR REPLACE VIEW v_signal_performance_trend_7d AS
SELECT
    strategy_id,
    DATE_TRUNC('day', hour_timestamp) as date,
    SUM(signal_count) as daily_signals,
    AVG(execution_rate) as avg_execution_rate,
    AVG(accuracy_rate) as avg_accuracy_rate,
    AVG(profit_ratio) as avg_profit_ratio,
    SUM(total_profit_loss) as daily_profit_loss,
    AVG(avg_execution_time_ms) as avg_execution_time_ms
FROM signal_statistics_hourly
WHERE hour_timestamp >= NOW() - INTERVAL '7 days'
GROUP BY strategy_id, DATE_TRUNC('day', hour_timestamp)
ORDER BY strategy_id, date DESC;

-- 创建聚合函数
CREATE OR REPLACE FUNCTION aggregate_signal_statistics(
    p_strategy_id VARCHAR(50),
    p_hour_timestamp TIMESTAMP
) RETURNS BOOLEAN AS $$
DECLARE
    v_signal_count INTEGER;
    v_buy_count INTEGER;
    v_sell_count INTEGER;
    v_hold_count INTEGER;
    v_executed_count INTEGER;
    v_execution_rate DECIMAL(5,2);
    v_profitable_count INTEGER;
    v_accuracy_rate DECIMAL(5,2);
    v_profit_ratio DECIMAL(5,2);
    v_total_profit_loss DECIMAL(15,2);
    v_avg_profit_loss DECIMAL(10,2);
    v_max_profit DECIMAL(10,2);
    v_max_loss DECIMAL(10,2);
    v_avg_execution_time_ms DECIMAL(10,2);
    v_p50_execution_time_ms DECIMAL(10,2);
    v_p95_execution_time_ms DECIMAL(10,2);
    v_p99_execution_time_ms DECIMAL(10,2);
    v_gpu_used_count INTEGER;
    v_gpu_rate DECIMAL(5,2);
BEGIN
    -- 计算信号统计
    SELECT
        COUNT(*) as signal_count,
        COUNT(*) FILTER (WHERE signal_type = 'BUY') as buy_count,
        COUNT(*) FILTER (WHERE signal_type = 'SELL') as sell_count,
        COUNT(*) FILTER (WHERE signal_type = 'HOLD') as hold_count,
        COUNT(*) FILTER (WHERE status = 'executed') as executed_count,
        COUNT(*) FILTER (WHERE executed = true AND profit_loss > 0) as profitable_count,
        COALESCE(SUM(profit_loss), 0) as total_profit_loss,
        AVG(execution_time_ms) as avg_execution_time_ms,
        COUNT(*) FILTER (WHERE gpu_used = true) as gpu_used_count
    INTO v_signal_count, v_buy_count, v_sell_count, v_hold_count,
         v_executed_count, v_profitable_count, v_total_profit_loss,
         v_avg_execution_time_ms, v_gpu_used_count
    FROM signal_records sr
    LEFT JOIN signal_execution_results ser ON sr.id = ser.signal_id
    WHERE sr.strategy_id = p_strategy_id
      AND DATE_TRUNC('hour', sr.generated_at) = p_hour_timestamp;

    -- 计算派生指标
    IF v_signal_count > 0 THEN
        v_execution_rate := (v_executed_count::DECIMAL / v_signal_count::DECIMAL) * 100;
        v_gpu_rate := (v_gpu_used_count::DECIMAL / v_signal_count::DECIMAL) * 100;
    ELSE
        v_execution_rate := 0;
        v_gpu_rate := 0;
    END IF;

    IF v_executed_count > 0 THEN
        v_accuracy_rate := (v_profitable_count::DECIMAL / v_executed_count::DECIMAL) * 100;
        v_profit_ratio := v_accuracy_rate;  -- 简化处理：盈利比率 = 准确率
        v_avg_profit_loss := v_total_profit_loss / v_executed_count;
    ELSE
        v_accuracy_rate := 0;
        v_profit_ratio := 0;
        v_avg_profit_loss := 0;
    END IF;

    -- 查询最大盈利和最大亏损
    SELECT
        COALESCE(MAX(profit_loss), 0),
        COALESCE(MIN(profit_loss), 0)
    INTO v_max_profit, v_max_loss
    FROM signal_execution_results ser
    JOIN signal_records sr ON ser.signal_id = sr.id
    WHERE sr.strategy_id = p_strategy_id
      AND DATE_TRUNC('hour', sr.generated_at) = p_hour_timestamp
      AND ser.executed = true;

    -- 查询延迟百分位数
    SELECT
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY execution_time_ms),
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms),
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY execution_time_ms)
    INTO v_p50_execution_time_ms, v_p95_execution_time_ms, v_p99_execution_time_ms
    FROM signal_records
    WHERE strategy_id = p_strategy_id
      AND DATE_TRUNC('hour', generated_at) = p_hour_timestamp;

    -- 插入或更新统计记录
    INSERT INTO signal_statistics_hourly (
        strategy_id, hour_timestamp,
        signal_count, buy_count, sell_count, hold_count,
        executed_count, execution_rate,
        profitable_count, accuracy_rate, profit_ratio,
        total_profit_loss, avg_profit_loss, max_profit, max_loss,
        avg_execution_time_ms, p50_execution_time_ms, p95_execution_time_ms, p99_execution_time_ms,
        gpu_used_count, gpu_rate,
        updated_at
    ) VALUES (
        p_strategy_id, p_hour_timestamp,
        v_signal_count, v_buy_count, v_sell_count, v_hold_count,
        v_executed_count, v_execution_rate,
        v_profitable_count, v_accuracy_rate, v_profit_ratio,
        v_total_profit_loss, v_avg_profit_loss, v_max_profit, v_max_loss,
        v_avg_execution_time_ms, v_p50_execution_time_ms, v_p95_execution_time_ms, v_p99_execution_time_ms,
        v_gpu_used_count, v_gpu_rate,
        NOW()
    )
    ON CONFLICT (strategy_id, hour_timestamp)
    DO UPDATE SET
        signal_count = EXCLUDED.signal_count,
        buy_count = EXCLUDED.buy_count,
        sell_count = EXCLUDED.sell_count,
        hold_count = EXCLUDED.hold_count,
        executed_count = EXCLUDED.executed_count,
        execution_rate = EXCLUDED.execution_rate,
        profitable_count = EXCLUDED.profitable_count,
        accuracy_rate = EXCLUDED.accuracy_rate,
        profit_ratio = EXCLUDED.profit_ratio,
        total_profit_loss = EXCLUDED.total_profit_loss,
        avg_profit_loss = EXCLUDED.avg_profit_loss,
        max_profit = EXCLUDED.max_profit,
        max_loss = EXCLUDED.max_loss,
        avg_execution_time_ms = EXCLUDED.avg_execution_time_ms,
        p50_execution_time_ms = EXCLUDED.p50_execution_time_ms,
        p95_execution_time_ms = EXCLUDED.p95_execution_time_ms,
        p99_execution_time_ms = EXCLUDED.p99_execution_time_ms,
        gpu_used_count = EXCLUDED.gpu_used_count,
        gpu_rate = EXCLUDED.gpu_rate,
        updated_at = NOW();

    RETURN TRUE;

EXCEPTION WHEN OTHERS THEN
    RAISE WARNING '聚合信号统计失败: %', SQLERRM;
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- 创建批量聚合函数（为所有策略聚合最近N小时）
CREATE OR REPLACE FUNCTION aggregate_all_strategies_statistics(
    p_hours_back INTEGER DEFAULT 1
) RETURNS INTEGER AS $$
DECLARE
    v_strategy_id VARCHAR(50);
    v_hour_timestamp TIMESTAMP;
    v_count INTEGER := 0;
BEGIN
    -- 遍历最近N小时的每个小时
    FOR v_hour_timestamp IN
        SELECT generate_series(
            DATE_TRUNC('hour', NOW() - INTERVAL '1 hour' * p_hours_back),
            DATE_TRUNC('hour', NOW()),
            INTERVAL '1 hour'
        )::TIMESTAMP
    LOOP
        -- 遍历每个策略
        FOR v_strategy_id IN
            SELECT DISTINCT strategy_id
            FROM signal_records
            WHERE generated_at >= v_hour_timestamp
              AND generated_at < v_hour_timestamp + INTERVAL '1 hour'
        LOOP
            -- 执行聚合
            IF aggregate_signal_statistics(v_strategy_id, v_hour_timestamp) THEN
                v_count := v_count + 1;
            END IF;
        END LOOP;
    END LOOP;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- 创建数据清理函数（删除90天前的小时统计数据）
CREATE OR REPLACE FUNCTION cleanup_old_signal_statistics()
RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM signal_statistics_hourly
    WHERE hour_timestamp < CURRENT_TIMESTAMP - INTERVAL '90 days';

    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RAISE NOTICE '已删除 % 条旧的信号统计记录', v_deleted_count;

    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 注释
COMMENT ON TABLE signal_statistics_hourly IS '信号统计小时表 - 存储每小时聚合的信号统计数据';
COMMENT ON FUNCTION aggregate_signal_statistics IS '聚合指定策略和小时的信号统计';
COMMENT ON FUNCTION aggregate_all_strategies_statistics IS '聚合所有策略最近N小时的信号统计';
COMMENT ON FUNCTION cleanup_old_signal_statistics IS '清理90天前的小时统计数据';
COMMENT ON VIEW v_signal_statistics_24h IS '最近24小时信号统计视图';
COMMENT ON VIEW v_signal_performance_trend_7d IS '最近7天策略性能趋势视图';

-- 授权（如果需要）
-- GRANT SELECT, INSERT, UPDATE ON signal_statistics_hourly TO mystocks_user;
-- GRANT SELECT ON v_signal_statistics_24h TO mystocks_user;
-- GRANT SELECT ON v_signal_performance_trend_7d TO mystocks_user;
-- GRANT EXECUTE ON FUNCTION aggregate_signal_statistics TO mystocks_user;
-- GRANT EXECUTE ON FUNCTION aggregate_all_strategies_statistics TO mystocks_user;
