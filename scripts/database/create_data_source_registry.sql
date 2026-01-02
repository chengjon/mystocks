-- ============================================================================
-- 数据源注册表创建脚本
-- ============================================================================
-- 用途：统一管理所有外部数据源接口（akshare, tushare, tdx等）
-- 核心功能：端点级治理、5层数据分类绑定、智能路由、监控统计
--
-- 作者：Claude Code
-- 创建时间：2026-01-02
-- 版本：v2.0
-- ============================================================================

-- ============================================================================
-- 1. 核心注册表（元数据，对应第5类数据）
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_source_registry (
    id SERIAL PRIMARY KEY,

    -- 基础标识
    source_name VARCHAR(50) NOT NULL,          -- 数据源名称：akshare、tushare、tdx、system_mock等
    source_type VARCHAR(20) NOT NULL,          -- 类型：api_library/database/crawler/file/mock
    endpoint_name VARCHAR(100) UNIQUE NOT NULL, -- 接口唯一标识：akshare.stock_zh_a_hist

    -- 调用信息
    call_method VARCHAR(20),                   -- http/get/post/function_call
    endpoint_url TEXT,                         -- 完整URL或函数路径
    parameters JSONB,                          -- 参数定义和示例（JSON格式）
    response_format VARCHAR(20),               -- json/csv/dataframe/protobuf

    -- 与5层数据分类绑定（核心关联）
    data_category VARCHAR(50) NOT NULL,        -- 对应34个分类：DAILY_KLINE、TICK_DATA等
    data_classification VARCHAR(20),           -- 5大分类：market_data/reference_data等
    classification_level INT NOT NULL,         -- 1-5层分类层级
    target_db VARCHAR(20) NOT NULL,            -- postgresql/tdengine
    table_name VARCHAR(100),                   -- 存储的目标表名

    -- 元数据
    description TEXT,
    update_frequency VARCHAR(20),              -- realtime/daily/weekly/monthly
    data_quality_score FLOAT DEFAULT 8.0,      -- 数据质量评分（0-10）
    priority INT DEFAULT 10,                   -- 优先级（数字越小优先级越高）
    status VARCHAR(20) DEFAULT 'active',       -- active/deprecated/maintenance/testing

    -- 监控指标
    last_success_time TIMESTAMP,
    last_failure_time TIMESTAMP,
    avg_response_time FLOAT DEFAULT 0,
    success_rate FLOAT DEFAULT 100.0,
    total_calls INT DEFAULT 0,
    failed_calls INT DEFAULT 0,
    consecutive_failures INT DEFAULT 0,
    quota_used INT DEFAULT 0,                  -- 调用额度使用情况
    quota_limit INT,                           -- 调用额度上限

    -- 数据质量
    data_freshness INTERVAL,                   -- 数据新鲜度
    last_check_time TIMESTAMP,
    health_status VARCHAR(20) DEFAULT 'unknown', -- healthy/degraded/failed/unknown

    -- 管理信息
    owner VARCHAR(50) DEFAULT 'system',
    tags TEXT[],                               -- 标签数组
    version VARCHAR(20) DEFAULT '1.0',         -- 接口版本号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT chk_status CHECK (status IN ('active', 'deprecated', 'maintenance', 'testing')),
    CONSTRAINT chk_health CHECK (health_status IN ('healthy', 'degraded', 'failed', 'unknown')),
    CONSTRAINT chk_quality_score CHECK (data_quality_score >= 0 AND data_quality_score <= 10),
    CONSTRAINT chk_target_db CHECK (target_db IN ('postgresql', 'tdengine')),
    CONSTRAINT chk_level CHECK (classification_level IN (1, 2, 3, 4, 5))
);

-- 创建索引（优化查询性能）
CREATE INDEX IF NOT EXISTS idx_dsr_category ON data_source_registry(data_category);
CREATE INDEX IF NOT EXISTS idx_dsr_status ON data_source_registry(status, health_status);
CREATE INDEX IF NOT EXISTS idx_dsr_source_name ON data_source_registry(source_name);
CREATE INDEX IF NOT EXISTS idx_dsr_quality_score ON data_source_registry(data_quality_score DESC, priority ASC);
CREATE INDEX IF NOT EXISTS idx_dsr_last_success ON data_source_registry(last_success_time);
CREATE INDEX IF NOT EXISTS idx_dsr_level_category ON data_source_registry(classification_level, data_category);

-- 创建更新触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_data_source_registry_updated_at ON data_source_registry;
CREATE TRIGGER update_data_source_registry_updated_at
    BEFORE UPDATE ON data_source_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 2. 调用历史表（用于监控和统计）
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_source_call_history (
    id BIGSERIAL PRIMARY KEY,
    endpoint_name VARCHAR(100) NOT NULL,
    call_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 调用参数
    parameters JSONB,

    -- 调用结果
    success BOOLEAN NOT NULL,
    response_time FLOAT,                       -- 响应时间（秒）
    record_count INT,                          -- 返回数据条数

    -- 错误信息
    error_message TEXT,
    error_type VARCHAR(100),

    -- 调用方标识
    caller VARCHAR(100) DEFAULT 'unknown',     -- 调用方标识（内部程序/用户）

    -- 外键关联
    CONSTRAINT fk_endpoint FOREIGN KEY (endpoint_name)
        REFERENCES data_source_registry(endpoint_name) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_dsch_call_time ON data_source_call_history(call_time DESC);
CREATE INDEX IF NOT EXISTS idx_dsch_endpoint ON data_source_call_history(endpoint_name, call_time DESC);
CREATE INDEX IF NOT EXISTS idx_dsch_success ON data_source_call_history(endpoint_name, success);
CREATE INDEX IF NOT EXISTS idx_dsch_caller ON data_source_call_history(caller);

-- ============================================================================
-- 3. 辅助视图（便于查询）
-- ============================================================================

-- 视图：数据源健康状态概览
CREATE OR REPLACE VIEW v_data_source_health AS
SELECT
    source_name,
    endpoint_name,
    data_category,
    classification_level,
    health_status,
    success_rate,
    avg_response_time,
    total_calls,
    failed_calls,
    data_quality_score,
    priority,
    last_success_time,
    last_check_time
FROM data_source_registry
WHERE status = 'active'
ORDER BY classification_level, priority, data_quality_score DESC;

-- 视图：调用统计摘要
CREATE OR REPLACE VIEW v_data_source_call_stats AS
SELECT
    endpoint_name,
    COUNT(*) as total_calls,
    SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) as success_calls,
    SUM(CASE WHEN success = FALSE THEN 1 ELSE 0 END) as failed_calls,
    ROUND(AVG(CASE WHEN success = TRUE THEN response_time ELSE NULL END)::numeric, 3) as avg_response_time,
    ROUND(AVG(CASE WHEN success = TRUE THEN record_count ELSE NULL END)::numeric, 0) as avg_record_count,
    MAX(call_time) as last_call_time
FROM data_source_call_history
WHERE call_time > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY endpoint_name;

-- ============================================================================
-- 4. 初始化核心数据（录入5-10个常用接口）
-- ============================================================================

-- 注意：此处只插入配置元数据，实际配置参数由YAML文件管理

-- 插入Mock数据源（用于测试）
INSERT INTO data_source_registry (
    source_name, source_type, endpoint_name,
    data_category, data_classification, classification_level,
    target_db, table_name,
    call_method, parameters,
    description, update_frequency,
    data_quality_score, priority, status,
    tags, version
) VALUES (
    'system_mock', 'mock', 'mock.daily_kline',
    'DAILY_KLINE', 'market_data', 1,
    'postgresql', 'daily_kline',
    'function_call', '{"symbol": {"type": "string", "required": true}, "period": {"type": "string", "default": "daily"}}'::JSONB,
    'Mock日线数据（用于测试）', 'daily',
    9.0, 999, 'active',
    ARRAY['mock', 'test'], '1.0'
) ON CONFLICT (endpoint_name) DO NOTHING;

-- 插入akshare日线数据
INSERT INTO data_source_registry (
    source_name, source_type, endpoint_name,
    data_category, data_classification, classification_level,
    target_db, table_name,
    call_method, parameters,
    description, update_frequency,
    data_quality_score, priority, status,
    tags, version
) VALUES (
    'akshare', 'api_library', 'akshare.stock_zh_a_hist',
    'DAILY_KLINE', 'market_data', 1,
    'postgresql', 'daily_kline',
    'function_call', '{"symbol": {"type": "string", "required": true}, "period": {"type": "string", "default": "daily"}, "adjust": {"type": "string", "default": "qfq"}}'::JSONB,
    'AKShare A股日线历史行情', 'daily',
    9.5, 2, 'active',
    ARRAY['stock', 'kline', 'free'], '1.0'
) ON CONFLICT (endpoint_name) DO NOTHING;

-- 插入tushare日线数据
INSERT INTO data_source_registry (
    source_name, source_type, endpoint_name,
    data_category, data_classification, classification_level,
    target_db, table_name,
    call_method, parameters,
    description, update_frequency,
    data_quality_score, priority, status,
    tags, version
) VALUES (
    'tushare', 'api_library', 'tushare.daily',
    'DAILY_KLINE', 'market_data', 1,
    'postgresql', 'daily_kline',
    'function_call', '{"ts_code": {"type": "string", "required": true}, "start_date": {"type": "string", "format": "YYYYMMDD"}, "end_date": {"type": "string", "format": "YYYYMMDD"}}'::JSONB,
    'TuShare A股日线行情（专业版）', 'daily',
    9.8, 1, 'active',
    ARRAY['stock', 'kline', 'premium', 'high-quality'], '1.0'
) ON CONFLICT (endpoint_name) DO NOTHING;

-- 插入tdx实时行情
INSERT INTO data_source_registry (
    source_name, source_type, endpoint_name,
    data_category, data_classification, classification_level,
    target_db, table_name,
    call_method, parameters,
    description, update_frequency,
    data_quality_score, priority, status,
    tags, version
) VALUES (
    'tdx', 'database', 'tdx.get_security_quotes',
    'REALTIME_QUOTE', 'market_data', 1,
    'tdengine', 'tick_data',
    'tcp', '{"symbols": {"type": "array", "required": true}}'::JSONB,
    '通达信实时行情数据', 'realtime',
    9.0, 1, 'active',
    ARRAY['realtime', 'tick', 'low-latency'], '1.0'
) ON CONFLICT (endpoint_name) DO NOTHING;

-- 插入akshare股票基本信息
INSERT INTO data_source_registry (
    source_name, source_type, endpoint_name,
    data_category, data_classification, classification_level,
    target_db, table_name,
    call_method, parameters,
    description, update_frequency,
    data_quality_score, priority, status,
    tags, version
) VALUES (
    'akshare', 'api_library', 'akshare.stock_info_a_code_name',
    'SYMBOLS_INFO', 'reference_data', 2,
    'postgresql', 'stock_symbols',
    'function_call', '{}'::JSONB,
    'AKShare A股股票代码和名称', 'weekly',
    9.0, 2, 'active',
    ARRAY['stock', 'symbols', 'free'], '1.0'
) ON CONFLICT (endpoint_name) DO NOTHING;

-- 插入tushare财务数据
INSERT INTO data_source_registry (
    source_name, source_type, endpoint_name,
    data_category, data_classification, classification_level,
    target_db, table_name,
    call_method, parameters,
    description, update_frequency,
    data_quality_score, priority, status,
    tags, version
) VALUES (
    'tushare', 'api_library', 'tushare.income',
    'FINANCIAL_DATA', 'reference_data', 2,
    'postgresql', 'financial_data',
    'function_call', '{"ts_code": {"type": "string", "required": true}, "period": {"type": "string", "default": "20241231"}, "report_type": {"type": "string", "default": "1"}}'::JSONB,
    'TuShare 利润表数据', 'monthly',
    9.5, 1, 'active',
    ARRAY['financial', 'premium'], '1.0'
) ON CONFLICT (endpoint_name) DO NOTHING;

-- ============================================================================
-- 5. 授权（根据实际情况调整）
-- ============================================================================
-- GRANT SELECT, INSERT, UPDATE ON data_source_registry TO your_app_user;
-- GRANT SELECT, INSERT ON data_source_call_history TO your_app_user;
-- GRANT SELECT ON SEQUENCE data_source_registry_id_seq TO your_app_user;
-- GRANT SELECT ON SEQUENCE data_source_call_history_id_seq TO your_app_user;

-- ============================================================================
-- 创建完成提示
-- ============================================================================
SELECT 'Data source registry tables created successfully!' AS status;
SELECT COUNT(*) as registered_endpoints FROM data_source_registry;
SELECT * FROM v_data_source_health;
