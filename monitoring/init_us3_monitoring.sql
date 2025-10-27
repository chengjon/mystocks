-- ============================================
-- US3 DataManager 监控表结构
-- ============================================
-- 版本: 1.0.0
-- 创建日期: 2025-10-25
-- 用途: 存储 DataManager O(1) 路由性能监控数据
-- ============================================

-- 创建监控 schema（如果不存在）
CREATE SCHEMA IF NOT EXISTS monitoring;

-- 1. DataManager 路由性能表
-- 记录每次路由决策的性能指标
CREATE TABLE IF NOT EXISTS monitoring.datamanager_routing_metrics (
    id SERIAL PRIMARY KEY,
    operation_id VARCHAR(100) NOT NULL,
    classification VARCHAR(100) NOT NULL,  -- 数据分类枚举值
    target_database VARCHAR(50) NOT NULL,  -- TDENGINE 或 POSTGRESQL
    routing_decision_time_ms DECIMAL(10, 6) NOT NULL,  -- 路由决策时间（毫秒）
    operation_type VARCHAR(50) NOT NULL,  -- save_data, load_data
    table_name VARCHAR(100),
    data_count INTEGER DEFAULT 0,
    operation_success BOOLEAN,
    operation_duration_ms DECIMAL(10, 3),  -- 总操作时间（毫秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_routing_created_at
    ON monitoring.datamanager_routing_metrics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_routing_classification
    ON monitoring.datamanager_routing_metrics(classification);
CREATE INDEX IF NOT EXISTS idx_routing_target_db
    ON monitoring.datamanager_routing_metrics(target_database);
CREATE INDEX IF NOT EXISTS idx_routing_operation_type
    ON monitoring.datamanager_routing_metrics(operation_type);

-- 2. 数据分类统计表
-- 聚合统计每种数据分类的使用情况
CREATE TABLE IF NOT EXISTS monitoring.classification_statistics (
    id SERIAL PRIMARY KEY,
    classification VARCHAR(100) NOT NULL,
    target_database VARCHAR(50) NOT NULL,
    total_operations INTEGER DEFAULT 0,
    successful_operations INTEGER DEFAULT 0,
    failed_operations INTEGER DEFAULT 0,
    avg_routing_time_ms DECIMAL(10, 6),
    avg_operation_time_ms DECIMAL(10, 3),
    total_data_count BIGINT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(classification)
);

-- 3. 数据库目标分布表
-- 统计不同数据库的负载分布
CREATE TABLE IF NOT EXISTS monitoring.database_target_distribution (
    id SERIAL PRIMARY KEY,
    target_database VARCHAR(50) NOT NULL,
    operation_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    total_data_count BIGINT DEFAULT 0,
    avg_operation_time_ms DECIMAL(10, 3),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(target_database)
);

-- 4. 路由性能告警表
-- 记录路由性能异常
CREATE TABLE IF NOT EXISTS monitoring.routing_performance_alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,  -- SLOW_ROUTING, HIGH_FAILURE_RATE
    severity VARCHAR(20) NOT NULL,  -- INFO, WARNING, ERROR, CRITICAL
    classification VARCHAR(100),
    target_database VARCHAR(50),
    metric_value DECIMAL(10, 6),
    threshold_value DECIMAL(10, 6),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP
);

-- ============================================
-- 创建 Grafana 查询视图
-- ============================================

-- 视图1: 最近24小时路由性能摘要
CREATE OR REPLACE VIEW monitoring.v_routing_performance_24h AS
SELECT
    COUNT(*) as total_operations,
    COUNT(CASE WHEN operation_success = TRUE THEN 1 END) as successful_operations,
    COUNT(CASE WHEN operation_success = FALSE THEN 1 END) as failed_operations,
    ROUND(AVG(routing_decision_time_ms)::NUMERIC, 6) as avg_routing_time_ms,
    ROUND(MAX(routing_decision_time_ms)::NUMERIC, 6) as max_routing_time_ms,
    ROUND(MIN(routing_decision_time_ms)::NUMERIC, 6) as min_routing_time_ms,
    ROUND(AVG(operation_duration_ms)::NUMERIC, 3) as avg_operation_time_ms,
    SUM(data_count) as total_data_count
FROM monitoring.datamanager_routing_metrics
WHERE created_at >= NOW() - INTERVAL '24 hours';

-- 视图2: 数据库目标分布（最近24小时）
CREATE OR REPLACE VIEW monitoring.v_database_distribution_24h AS
SELECT
    target_database,
    COUNT(*) as operation_count,
    COUNT(CASE WHEN operation_success = TRUE THEN 1 END) as success_count,
    COUNT(CASE WHEN operation_success = FALSE THEN 1 END) as failure_count,
    ROUND((COUNT(CASE WHEN operation_success = TRUE THEN 1 END)::NUMERIC /
           NULLIF(COUNT(*), 0) * 100), 2) as success_rate_percent,
    SUM(data_count) as total_data_count,
    ROUND(AVG(routing_decision_time_ms)::NUMERIC, 6) as avg_routing_time_ms,
    ROUND(AVG(operation_duration_ms)::NUMERIC, 3) as avg_operation_time_ms
FROM monitoring.datamanager_routing_metrics
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY target_database;

-- 视图3: 数据分类频率统计（最近24小时）
CREATE OR REPLACE VIEW monitoring.v_classification_frequency_24h AS
SELECT
    classification,
    target_database,
    COUNT(*) as operation_count,
    ROUND((COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM monitoring.datamanager_routing_metrics
                                 WHERE created_at >= NOW() - INTERVAL '24 hours') * 100), 2) as percentage,
    COUNT(CASE WHEN operation_success = TRUE THEN 1 END) as success_count,
    ROUND(AVG(routing_decision_time_ms)::NUMERIC, 6) as avg_routing_time_ms,
    ROUND(AVG(operation_duration_ms)::NUMERIC, 3) as avg_operation_time_ms,
    SUM(data_count) as total_data_count
FROM monitoring.datamanager_routing_metrics
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY classification, target_database
ORDER BY operation_count DESC;

-- 视图4: 路由性能时序数据（按5分钟聚合）
CREATE OR REPLACE VIEW monitoring.v_routing_performance_timeseries AS
SELECT
    time_bucket('5 minutes', created_at) AS time_bucket,
    target_database,
    COUNT(*) as operation_count,
    ROUND(AVG(routing_decision_time_ms)::NUMERIC, 6) as avg_routing_time_ms,
    ROUND(MAX(routing_decision_time_ms)::NUMERIC, 6) as max_routing_time_ms,
    ROUND(AVG(operation_duration_ms)::NUMERIC, 3) as avg_operation_time_ms,
    COUNT(CASE WHEN operation_success = FALSE THEN 1 END) as failure_count
FROM monitoring.datamanager_routing_metrics
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY time_bucket, target_database
ORDER BY time_bucket DESC;

-- 视图5: 慢路由告警（路由时间 > 1ms）
CREATE OR REPLACE VIEW monitoring.v_slow_routing_operations AS
SELECT
    operation_id,
    classification,
    target_database,
    routing_decision_time_ms,
    operation_duration_ms,
    table_name,
    data_count,
    created_at,
    error_message
FROM monitoring.datamanager_routing_metrics
WHERE routing_decision_time_ms > 1.0  -- 超过1ms的路由决策（正常应该是0.0002ms）
  AND created_at >= NOW() - INTERVAL '24 hours'
ORDER BY routing_decision_time_ms DESC;

-- 视图6: 未解决的路由性能告警
CREATE OR REPLACE VIEW monitoring.v_active_routing_alerts AS
SELECT
    alert_type,
    severity,
    classification,
    target_database,
    metric_value,
    threshold_value,
    message,
    created_at,
    (NOW() - created_at) as age
FROM monitoring.routing_performance_alerts
WHERE resolved = FALSE
ORDER BY
    CASE severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'ERROR' THEN 2
        WHEN 'WARNING' THEN 3
        ELSE 4
    END,
    created_at DESC;

-- ============================================
-- 创建自动聚合函数
-- ============================================

-- 函数: 更新分类统计表
CREATE OR REPLACE FUNCTION monitoring.update_classification_statistics()
RETURNS void AS $$
BEGIN
    INSERT INTO monitoring.classification_statistics (
        classification,
        target_database,
        total_operations,
        successful_operations,
        failed_operations,
        avg_routing_time_ms,
        avg_operation_time_ms,
        total_data_count,
        last_updated
    )
    SELECT
        classification,
        target_database,
        COUNT(*) as total_operations,
        COUNT(CASE WHEN operation_success = TRUE THEN 1 END) as successful_operations,
        COUNT(CASE WHEN operation_success = FALSE THEN 1 END) as failed_operations,
        AVG(routing_decision_time_ms) as avg_routing_time_ms,
        AVG(operation_duration_ms) as avg_operation_time_ms,
        SUM(data_count) as total_data_count,
        NOW() as last_updated
    FROM monitoring.datamanager_routing_metrics
    WHERE created_at >= NOW() - INTERVAL '24 hours'
    GROUP BY classification, target_database
    ON CONFLICT (classification) DO UPDATE SET
        target_database = EXCLUDED.target_database,
        total_operations = EXCLUDED.total_operations,
        successful_operations = EXCLUDED.successful_operations,
        failed_operations = EXCLUDED.failed_operations,
        avg_routing_time_ms = EXCLUDED.avg_routing_time_ms,
        avg_operation_time_ms = EXCLUDED.avg_operation_time_ms,
        total_data_count = EXCLUDED.total_data_count,
        last_updated = EXCLUDED.last_updated;
END;
$$ LANGUAGE plpgsql;

-- 函数: 更新数据库目标分布表
CREATE OR REPLACE FUNCTION monitoring.update_database_distribution()
RETURNS void AS $$
BEGIN
    INSERT INTO monitoring.database_target_distribution (
        target_database,
        operation_count,
        success_count,
        failure_count,
        total_data_count,
        avg_operation_time_ms,
        last_updated
    )
    SELECT
        target_database,
        COUNT(*) as operation_count,
        COUNT(CASE WHEN operation_success = TRUE THEN 1 END) as success_count,
        COUNT(CASE WHEN operation_success = FALSE THEN 1 END) as failure_count,
        SUM(data_count) as total_data_count,
        AVG(operation_duration_ms) as avg_operation_time_ms,
        NOW() as last_updated
    FROM monitoring.datamanager_routing_metrics
    WHERE created_at >= NOW() - INTERVAL '24 hours'
    GROUP BY target_database
    ON CONFLICT (target_database) DO UPDATE SET
        operation_count = EXCLUDED.operation_count,
        success_count = EXCLUDED.success_count,
        failure_count = EXCLUDED.failure_count,
        total_data_count = EXCLUDED.total_data_count,
        avg_operation_time_ms = EXCLUDED.avg_operation_time_ms,
        last_updated = EXCLUDED.last_updated;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 数据清理策略
-- ============================================

-- 函数: 清理旧监控数据（保留30天）
CREATE OR REPLACE FUNCTION monitoring.cleanup_old_routing_metrics()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM monitoring.datamanager_routing_metrics
    WHERE created_at < NOW() - INTERVAL '30 days';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 授予权限
-- ============================================

-- 授予 mystocks 用户权限
GRANT USAGE ON SCHEMA monitoring TO postgres;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA monitoring TO postgres;
GRANT SELECT ON ALL VIEWS IN SCHEMA monitoring TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA monitoring TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA monitoring TO postgres;

-- ============================================
-- 插入测试数据（用于验证）
-- ============================================

-- 插入示例路由监控数据
INSERT INTO monitoring.datamanager_routing_metrics (
    operation_id, classification, target_database,
    routing_decision_time_ms, operation_type, table_name,
    data_count, operation_success, operation_duration_ms
) VALUES
('test_001', 'TICK_DATA', 'TDENGINE', 0.0002, 'save_data', 'tick_data', 1000, TRUE, 125.5),
('test_002', 'DAILY_KLINE', 'POSTGRESQL', 0.0002, 'save_data', 'daily_kline', 500, TRUE, 89.3),
('test_003', 'SYMBOLS_INFO', 'POSTGRESQL', 0.0002, 'load_data', 'symbols_info', 100, TRUE, 45.2),
('test_004', 'MINUTE_KLINE', 'TDENGINE', 0.0002, 'save_data', 'minute_kline', 5000, TRUE, 256.8),
('test_005', 'TECHNICAL_INDICATORS', 'POSTGRESQL', 0.0002, 'save_data', 'technical_indicators', 200, TRUE, 67.4);

-- ============================================
-- 完成
-- ============================================

SELECT 'US3 DataManager 监控表结构创建完成' AS status;
SELECT 'Total Tables: ' || COUNT(*) FROM information_schema.tables WHERE table_schema = 'monitoring' AS table_count;
SELECT 'Total Views: ' || COUNT(*) FROM information_schema.views WHERE table_schema = 'monitoring' AS view_count;
