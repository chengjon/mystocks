-- ============================================================================
-- MyStocks 监控数据库初始化脚本
-- ============================================================================
-- 描述: 创建独立监控数据库的表结构,用于记录所有操作日志、性能指标、
--       数据质量检查和告警记录
--
-- 数据库: mystocks_monitor (独立于业务数据库)
-- 引擎: PostgreSQL 14+ (支持分区表和定时任务)
--
-- 创建日期: 2025-10-11
-- 版本: 1.0.0
-- ============================================================================

-- 检查PostgreSQL版本
DO $$
BEGIN
    IF (SELECT current_setting('server_version_num')::int < 140000) THEN
        RAISE EXCEPTION 'PostgreSQL version must be >= 14';
    END IF;
END
$$;

-- ============================================================================
-- 1. 操作日志表 (operation_logs)
-- ============================================================================
-- 用途: 记录所有数据库操作 (保存/查询/删除)
-- 分区: 按月分区 (使用pg_partman自动管理)
-- 保留: 30天
-- ============================================================================

-- 创建操作日志主表 (分区表)
CREATE TABLE IF NOT EXISTS operation_logs (
    id BIGSERIAL NOT NULL,
    operation_id VARCHAR(64) NOT NULL,  -- 操作唯一标识 (UUID)
    operation_type VARCHAR(32) NOT NULL,  -- 操作类型: SAVE/LOAD/DELETE/UPDATE
    classification VARCHAR(64) NOT NULL,  -- 数据分类 (DataClassification)
    target_database VARCHAR(32) NOT NULL,  -- 目标数据库: TDengine/PostgreSQL/MySQL/Redis
    table_name VARCHAR(128),  -- 目标表名
    record_count INTEGER DEFAULT 0,  -- 影响记录数
    operation_status VARCHAR(32) NOT NULL,  -- 状态: SUCCESS/FAILED/PARTIAL
    error_message TEXT,  -- 错误信息 (失败时)
    execution_time_ms INTEGER,  -- 执行时间(毫秒)
    user_agent VARCHAR(256),  -- 调用来源
    client_ip VARCHAR(64),  -- 客户端IP
    additional_info JSONB,  -- 额外信息 (JSON格式)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    CONSTRAINT operation_logs_pkey PRIMARY KEY (id, created_at)  -- 复合主键包含分区键
) PARTITION BY RANGE (created_at);

-- 创建索引 (在主表上,子分区会自动继承)
CREATE INDEX IF NOT EXISTS idx_operation_logs_operation_id
    ON operation_logs(operation_id);

CREATE INDEX IF NOT EXISTS idx_operation_logs_classification
    ON operation_logs(classification);

CREATE INDEX IF NOT EXISTS idx_operation_logs_target_database
    ON operation_logs(target_database);

CREATE INDEX IF NOT EXISTS idx_operation_logs_status
    ON operation_logs(operation_status);

CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at
    ON operation_logs(created_at DESC);

-- 创建GIN索引用于JSONB查询
CREATE INDEX IF NOT EXISTS idx_operation_logs_additional_info
    ON operation_logs USING GIN (additional_info);

-- 注释
COMMENT ON TABLE operation_logs IS '操作日志表 (按月分区, 保留30天)';
COMMENT ON COLUMN operation_logs.operation_id IS '操作唯一标识';
COMMENT ON COLUMN operation_logs.classification IS '数据分类 (23个枚举值)';
COMMENT ON COLUMN operation_logs.execution_time_ms IS '执行时间(毫秒)';

-- 手动创建初始分区 (当前月份和下个月份)
DO $$
DECLARE
    current_month DATE := date_trunc('month', CURRENT_DATE);
    next_month DATE := date_trunc('month', CURRENT_DATE + INTERVAL '1 month');
    current_month_end DATE := next_month;
    next_month_end DATE := date_trunc('month', CURRENT_DATE + INTERVAL '2 months');
BEGIN
    -- 创建当前月份分区
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS operation_logs_%s PARTITION OF operation_logs
         FOR VALUES FROM (%L) TO (%L)',
        to_char(current_month, 'YYYY_MM'),
        current_month,
        current_month_end
    );

    -- 创建下个月份分区
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS operation_logs_%s PARTITION OF operation_logs
         FOR VALUES FROM (%L) TO (%L)',
        to_char(next_month, 'YYYY_MM'),
        next_month,
        next_month_end
    );
END
$$;

-- ============================================================================
-- 2. 性能指标表 (performance_metrics)
-- ============================================================================
-- 用途: 记录查询性能指标和慢查询
-- 保留: 90天
-- ============================================================================

CREATE TABLE IF NOT EXISTS performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(128) NOT NULL,  -- 指标名称
    metric_type VARCHAR(32) NOT NULL,  -- 指标类型: QUERY_TIME/CONNECTION_TIME/BATCH_SIZE
    metric_value NUMERIC(18, 4) NOT NULL,  -- 指标值
    metric_unit VARCHAR(32) DEFAULT 'ms',  -- 单位: ms/seconds/count
    classification VARCHAR(64),  -- 关联数据分类
    database_type VARCHAR(32),  -- 关联数据库类型
    table_name VARCHAR(128),  -- 关联表名
    is_slow_query BOOLEAN DEFAULT FALSE,  -- 是否慢查询 (>5秒)
    query_sql TEXT,  -- SQL语句 (慢查询时记录)
    execution_plan TEXT,  -- 执行计划 (慢查询时记录)
    tags JSONB,  -- 标签 (用于多维度分析)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recorded_date DATE NOT NULL DEFAULT CURRENT_DATE  -- 记录日期 (用于分区)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_performance_metrics_metric_name
    ON performance_metrics(metric_name);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_metric_type
    ON performance_metrics(metric_type);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_classification
    ON performance_metrics(classification);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_database_type
    ON performance_metrics(database_type);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_is_slow_query
    ON performance_metrics(is_slow_query) WHERE is_slow_query = TRUE;

CREATE INDEX IF NOT EXISTS idx_performance_metrics_created_at
    ON performance_metrics(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_recorded_date
    ON performance_metrics(recorded_date DESC);

-- GIN索引用于tags查询
CREATE INDEX IF NOT EXISTS idx_performance_metrics_tags
    ON performance_metrics USING GIN (tags);

-- 注释
COMMENT ON TABLE performance_metrics IS '性能指标表 (保留90天)';
COMMENT ON COLUMN performance_metrics.is_slow_query IS '慢查询标记 (执行时间>5秒)';

-- ============================================================================
-- 3. 数据质量检查表 (data_quality_checks)
-- ============================================================================
-- 用途: 记录数据质量检查结果 (完整性/新鲜度/准确性)
-- 保留: 7天
-- ============================================================================

CREATE TABLE IF NOT EXISTS data_quality_checks (
    id BIGSERIAL PRIMARY KEY,
    check_id VARCHAR(64) NOT NULL,  -- 检查唯一标识
    check_type VARCHAR(32) NOT NULL,  -- 检查类型: COMPLETENESS/FRESHNESS/ACCURACY
    classification VARCHAR(64) NOT NULL,  -- 数据分类
    database_type VARCHAR(32) NOT NULL,  -- 数据库类型
    table_name VARCHAR(128) NOT NULL,  -- 表名
    check_status VARCHAR(32) NOT NULL,  -- 检查状态: PASS/FAIL/WARNING

    -- 完整性检查字段
    total_records BIGINT,  -- 总记录数
    null_records BIGINT,  -- 空值记录数
    missing_rate NUMERIC(5, 2),  -- 缺失率 (%)

    -- 新鲜度检查字段
    latest_timestamp TIMESTAMP,  -- 最新时间戳
    data_delay_seconds INTEGER,  -- 数据延迟(秒)

    -- 准确性检查字段
    invalid_records BIGINT,  -- 无效记录数
    validation_rules TEXT,  -- 验证规则

    check_message TEXT,  -- 检查信息
    threshold_config JSONB,  -- 阈值配置
    check_duration_ms INTEGER,  -- 检查耗时(毫秒)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_data_quality_checks_check_type
    ON data_quality_checks(check_type);

CREATE INDEX IF NOT EXISTS idx_data_quality_checks_classification
    ON data_quality_checks(classification);

CREATE INDEX IF NOT EXISTS idx_data_quality_checks_table_name
    ON data_quality_checks(table_name);

CREATE INDEX IF NOT EXISTS idx_data_quality_checks_status
    ON data_quality_checks(check_status);

CREATE INDEX IF NOT EXISTS idx_data_quality_checks_created_at
    ON data_quality_checks(created_at DESC);

-- 复合索引: 按表+类型查询
CREATE INDEX IF NOT EXISTS idx_data_quality_checks_table_type
    ON data_quality_checks(table_name, check_type, created_at DESC);

-- 注释
COMMENT ON TABLE data_quality_checks IS '数据质量检查表 (保留7天)';
COMMENT ON COLUMN data_quality_checks.missing_rate IS '数据缺失率 (0-100%)';
COMMENT ON COLUMN data_quality_checks.data_delay_seconds IS '数据延迟秒数';

-- ============================================================================
-- 4. 告警记录表 (alert_records)
-- ============================================================================
-- 用途: 记录所有告警信息
-- 保留: 90天
-- ============================================================================

CREATE TABLE IF NOT EXISTS alert_records (
    id BIGSERIAL PRIMARY KEY,
    alert_id VARCHAR(64) NOT NULL UNIQUE,  -- 告警唯一标识
    alert_level VARCHAR(32) NOT NULL,  -- 告警级别: CRITICAL/WARNING/INFO
    alert_type VARCHAR(64) NOT NULL,  -- 告警类型: SLOW_QUERY/DATA_QUALITY/SYSTEM_ERROR
    alert_title VARCHAR(256) NOT NULL,  -- 告警标题
    alert_message TEXT NOT NULL,  -- 告警详细信息
    source VARCHAR(128),  -- 告警来源 (模块名称)
    classification VARCHAR(64),  -- 关联数据分类
    database_type VARCHAR(32),  -- 关联数据库类型
    table_name VARCHAR(128),  -- 关联表名

    -- 告警统计
    occurrence_count INTEGER DEFAULT 1,  -- 发生次数 (相同告警累计)
    first_occurred_at TIMESTAMP NOT NULL,  -- 首次发生时间
    last_occurred_at TIMESTAMP NOT NULL,  -- 最后发生时间

    -- 告警状态
    alert_status VARCHAR(32) DEFAULT 'OPEN',  -- 状态: OPEN/ACKNOWLEDGED/RESOLVED
    acknowledged_by VARCHAR(128),  -- 确认人
    acknowledged_at TIMESTAMP,  -- 确认时间
    resolved_by VARCHAR(128),  -- 解决人
    resolved_at TIMESTAMP,  -- 解决时间
    resolution_notes TEXT,  -- 解决说明

    -- 通知状态
    notification_sent BOOLEAN DEFAULT FALSE,  -- 是否已发送通知
    notification_channels VARCHAR(256)[],  -- 通知渠道: [email, webhook, log]
    notification_attempts INTEGER DEFAULT 0,  -- 通知尝试次数

    additional_data JSONB,  -- 额外数据
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_alert_records_alert_level
    ON alert_records(alert_level);

CREATE INDEX IF NOT EXISTS idx_alert_records_alert_type
    ON alert_records(alert_type);

CREATE INDEX IF NOT EXISTS idx_alert_records_alert_status
    ON alert_records(alert_status);

CREATE INDEX IF NOT EXISTS idx_alert_records_classification
    ON alert_records(classification);

CREATE INDEX IF NOT EXISTS idx_alert_records_database_type
    ON alert_records(database_type);

CREATE INDEX IF NOT EXISTS idx_alert_records_created_at
    ON alert_records(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_alert_records_last_occurred_at
    ON alert_records(last_occurred_at DESC);

-- 复合索引: 查询未解决的告警
CREATE INDEX IF NOT EXISTS idx_alert_records_open_alerts
    ON alert_records(alert_status, alert_level, created_at DESC)
    WHERE alert_status = 'OPEN';

-- GIN索引
CREATE INDEX IF NOT EXISTS idx_alert_records_additional_data
    ON alert_records USING GIN (additional_data);

-- 注释
COMMENT ON TABLE alert_records IS '告警记录表 (保留90天)';
COMMENT ON COLUMN alert_records.occurrence_count IS '相同告警累计发生次数';
COMMENT ON COLUMN alert_records.notification_channels IS '通知渠道数组';

-- ============================================================================
-- 5. 自动更新 updated_at 触发器
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_alert_records_updated_at
    BEFORE UPDATE ON alert_records
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 6. 数据清理策略 (使用pg_cron或手动执行)
-- ============================================================================

-- 清理30天前的操作日志 (手动执行或配置定时任务)
-- DELETE FROM operation_logs WHERE created_at < CURRENT_DATE - INTERVAL '30 days';

-- 清理90天前的性能指标
-- DELETE FROM performance_metrics WHERE created_at < CURRENT_DATE - INTERVAL '90 days';

-- 清理7天前的数据质量检查
-- DELETE FROM data_quality_checks WHERE created_at < CURRENT_DATE - INTERVAL '7 days';

-- 清理90天前的告警记录
-- DELETE FROM alert_records WHERE created_at < CURRENT_DATE - INTERVAL '90 days';

-- ============================================================================
-- 7. 创建视图: 监控仪表板统计
-- ============================================================================

-- 今日操作统计视图
CREATE OR REPLACE VIEW v_today_operation_stats AS
SELECT
    operation_type,
    classification,
    target_database,
    operation_status,
    COUNT(*) as operation_count,
    SUM(record_count) as total_records,
    AVG(execution_time_ms) as avg_execution_time_ms,
    MAX(execution_time_ms) as max_execution_time_ms,
    DATE(created_at) as operation_date
FROM operation_logs
WHERE created_at >= CURRENT_DATE
GROUP BY operation_type, classification, target_database, operation_status, DATE(created_at)
ORDER BY operation_count DESC;

-- 慢查询统计视图
CREATE OR REPLACE VIEW v_slow_queries_today AS
SELECT
    metric_name,
    classification,
    database_type,
    table_name,
    metric_value as execution_time_ms,
    query_sql,
    created_at
FROM performance_metrics
WHERE is_slow_query = TRUE
  AND created_at >= CURRENT_DATE
ORDER BY metric_value DESC
LIMIT 100;

-- 数据质量问题视图
CREATE OR REPLACE VIEW v_data_quality_issues AS
SELECT
    check_type,
    classification,
    table_name,
    check_status,
    missing_rate,
    data_delay_seconds,
    invalid_records,
    check_message,
    created_at
FROM data_quality_checks
WHERE check_status IN ('FAIL', 'WARNING')
  AND created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC;

-- 活跃告警视图
CREATE OR REPLACE VIEW v_active_alerts AS
SELECT
    alert_id,
    alert_level,
    alert_type,
    alert_title,
    alert_message,
    source,
    occurrence_count,
    first_occurred_at,
    last_occurred_at,
    created_at
FROM alert_records
WHERE alert_status = 'OPEN'
ORDER BY
    CASE alert_level
        WHEN 'CRITICAL' THEN 1
        WHEN 'WARNING' THEN 2
        WHEN 'INFO' THEN 3
    END,
    last_occurred_at DESC;

-- ============================================================================
-- 8. 授权 (根据实际需要调整)
-- ============================================================================

-- 示例: 授予监控用户权限
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO monitoring_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO monitoring_user;

-- ============================================================================
-- 初始化完成提示
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'MyStocks 监控数据库初始化完成!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '已创建表:';
    RAISE NOTICE '  1. operation_logs (操作日志, 按月分区, 保留30天)';
    RAISE NOTICE '  2. performance_metrics (性能指标, 保留90天)';
    RAISE NOTICE '  3. data_quality_checks (质量检查, 保留7天)';
    RAISE NOTICE '  4. alert_records (告警记录, 保留90天)';
    RAISE NOTICE '';
    RAISE NOTICE '已创建视图:';
    RAISE NOTICE '  - v_today_operation_stats (今日操作统计)';
    RAISE NOTICE '  - v_slow_queries_today (今日慢查询)';
    RAISE NOTICE '  - v_data_quality_issues (质量问题)';
    RAISE NOTICE '  - v_active_alerts (活跃告警)';
    RAISE NOTICE '============================================================';
END
$$;
