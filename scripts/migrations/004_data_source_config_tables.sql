-- ============================================================================
-- MyStocks Data Source Configuration Management - Migration Script
-- Version: 004
-- Date: 2026-01-09
-- Description: 创建数据源配置版本管理和审计日志表
--
-- Tables:
--   1. data_source_versions - 配置版本历史
--   2. data_source_audit_log - 配置变更审计日志
--
-- Dependencies:
--   - data_source_registry (existing table from Phase 1/2)
--
-- Author: Claude Code (Main CLI)
-- ============================================================================

-- ============================================================================
-- Table 1: data_source_versions - 配置版本历史表
-- ============================================================================
-- Purpose: 跟踪数据源配置的所有历史变更，支持版本回滚
-- Features:
--   - 记录每次配置变更的完整快照
--   - 支持变更类型分类（create, update, delete）
--   - 记录变更人和变更时间
--   - 存储变更摘要和元数据

CREATE TABLE IF NOT EXISTS data_source_versions (
    -- 主键
    id SERIAL PRIMARY KEY,

    -- 数据源标识
    endpoint_name VARCHAR(255) NOT NULL,

    -- 版本号（每个数据源独立版本号）
    version INTEGER NOT NULL,

    -- 配置快照（完整配置JSON）
    config_snapshot JSONB NOT NULL,

    -- 变更类型
    change_type VARCHAR(20) NOT NULL CHECK (change_type IN ('create', 'update', 'delete', 'restore')),

    -- 变更人信息
    changed_by VARCHAR(100) NOT NULL DEFAULT 'system',

    -- 变更时间
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 变更摘要（简短描述）
    change_summary TEXT,

    -- 元数据（扩展字段）
    metadata JSONB DEFAULT '{}',

    -- 约束：同一数据源的版本号唯一
    CONSTRAINT unique_endpoint_version UNIQUE (endpoint_name, version)
);

-- 索引：加速查询
-- 1. 按数据源查询版本历史（倒序）
CREATE INDEX idx_versions_endpoint ON data_source_versions(endpoint_name, version DESC);

-- 2. 按变更时间查询（倒序）
CREATE INDEX idx_versions_changed_at ON data_source_versions(changed_at DESC);

-- 3. 按变更人查询
CREATE INDEX idx_versions_changed_by ON data_source_versions(changed_by);

-- 4. 全文搜索配置快照
CREATE INDEX idx_versions_config_gin ON data_source_versions USING GIN (config_snapshot);

-- 5. 部分索引：仅索引未删除的版本
CREATE INDEX idx_versions_active ON data_source_versions(endpoint_name, version DESC)
    WHERE change_type != 'delete';

-- 注释
COMMENT ON TABLE data_source_versions IS '数据源配置版本历史表';
COMMENT ON COLUMN data_source_versions.endpoint_name IS '数据源端点名称（唯一标识）';
COMMENT ON COLUMN data_source_versions.version IS '版本号（从1开始递增）';
COMMENT ON COLUMN data_source_versions.config_snapshot IS '配置快照（JSON格式）';
COMMENT ON COLUMN data_source_versions.change_type IS '变更类型：create=创建, update=更新, delete=删除, restore=恢复';
COMMENT ON COLUMN data_source_versions.changed_by IS '变更人（用户名或system）';
COMMENT ON COLUMN data_source_versions.change_summary IS '变更摘要（人类可读的描述）';
COMMENT ON COLUMN data_source_versions.metadata IS '元数据（扩展字段）';

-- ============================================================================
-- Table 2: data_source_audit_log - 配置变更审计日志表
-- ============================================================================
-- Purpose: 记录所有数据源配置操作的详细审计日志
-- Features:
--   - 记录所有CRUD操作（create, read, update, delete, reload）
--   - 记录完整的请求和响应
--   - 记录执行时间（性能监控）
--   - 记录客户端信息（IP、User-Agent）

CREATE TABLE IF NOT EXISTS data_source_audit_log (
    -- 主键
    id SERIAL PRIMARY KEY,

    -- 数据源标识
    endpoint_name VARCHAR(255) NOT NULL,

    -- 操作类型
    action VARCHAR(50) NOT NULL CHECK (action IN (
        'create', 'read', 'update', 'delete', 'reload',
        'batch_create', 'batch_update', 'batch_delete',
        'rollback', 'test', 'health_check'
    )),

    -- 操作人信息
    actor VARCHAR(100) NOT NULL DEFAULT 'system',

    -- 操作时间
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 请求数据
    request_body JSONB,

    -- 响应状态（HTTP状态码）
    response_status INTEGER,

    -- 错误信息（如果失败）
    error_message TEXT,

    -- 执行时间（毫秒）
    execution_time_ms INTEGER,

    -- 客户端信息
    ip_address INET,
    user_agent TEXT,

    -- 元数据（扩展字段）
    metadata JSONB DEFAULT '{}'
);

-- 索引：加速查询
-- 1. 按数据源查询审计日志
CREATE INDEX idx_audit_endpoint ON data_source_audit_log(endpoint_name);

-- 2. 按操作类型查询
CREATE INDEX idx_audit_action ON data_source_audit_log(action);

-- 3. 按时间查询（倒序）
CREATE INDEX idx_audit_timestamp ON data_source_audit_log(timestamp DESC);

-- 4. 按操作人查询
CREATE INDEX idx_audit_actor ON data_source_audit_log(actor);

-- 5. 按响应状态查询（筛选失败操作）
CREATE INDEX idx_audit_status ON data_source_audit_log(response_status)
    WHERE response_status >= 400;

-- 6. 部分索引：仅索引慢查询（>1秒）
CREATE INDEX idx_audit_slow_queries ON data_source_audit_log(endpoint_name, timestamp DESC)
    WHERE execution_time_ms > 1000;

-- 7. 全文搜索错误消息
CREATE INDEX idx_audit_error_gin ON data_source_audit_log USING GIN (to_tsvector('english', error_message))
    WHERE error_message IS NOT NULL;

-- 注释
COMMENT ON TABLE data_source_audit_log IS '数据源配置审计日志表';
COMMENT ON COLUMN data_source_audit_log.endpoint_name IS '数据源端点名称';
COMMENT ON COLUMN data_source_audit_log.action IS '操作类型（CRUD + 特殊操作）';
COMMENT ON COLUMN data_source_audit_log.actor IS '操作人（用户名或system）';
COMMENT ON COLUMN data_source_audit_log.request_body IS '请求体（JSON格式）';
COMMENT ON COLUMN data_source_audit_log.response_status IS 'HTTP响应状态码';
COMMENT ON COLUMN data_source_audit_log.execution_time_ms IS '执行时间（毫秒）';
COMMENT ON COLUMN data_source_audit_log.ip_address IS '客户端IP地址';
COMMENT ON COLUMN data_source_audit_log.user_agent IS '客户端User-Agent';
COMMENT ON COLUMN data_source_audit_log.error_message IS '错误消息（如果操作失败）';

-- ============================================================================
-- Foreign Keys and Constraints
-- ============================================================================

-- 外键：版本表引用数据源注册表
-- 注意：如果 data_source_registry 表不存在，需要先创建或注释掉此约束
ALTER TABLE data_source_versions
ADD CONSTRAINT fk_versions_endpoint
FOREIGN KEY (endpoint_name)
REFERENCES data_source_registry(endpoint_name)
ON DELETE CASCADE;

-- 外键：审计日志引用数据源注册表
ALTER TABLE data_source_audit_log
ADD CONSTRAINT fk_audit_endpoint
FOREIGN KEY (endpoint_name)
REFERENCES data_source_registry(endpoint_name)
ON DELETE CASCADE;

-- ============================================================================
-- Triggers and Functions
-- ============================================================================

-- 触发器函数：自动创建版本记录
CREATE OR REPLACE FUNCTION create_version_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO data_source_versions (
            endpoint_name,
            version,
            config_snapshot,
            change_type,
            changed_by,
            change_summary,
            metadata
        )
        SELECT
            NEW.endpoint_name,
            COALESCE((
                SELECT MAX(version)
                FROM data_source_versions
                WHERE endpoint_name = NEW.endpoint_name
            ), 0) + 1,
            row_to_json(NEW)::jsonb,
            'create',
            current_user,
            'Initial creation',
            '{"trigger": "auto_create"}'::jsonb;

    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO data_source_versions (
            endpoint_name,
            version,
            config_snapshot,
            change_type,
            changed_by,
            change_summary,
            metadata
        )
        SELECT
            NEW.endpoint_name,
            COALESCE((
                SELECT MAX(version)
                FROM data_source_versions
                WHERE endpoint_name = NEW.endpoint_name
            ), 0) + 1,
            row_to_json(NEW)::jsonb,
            'update',
            current_user,
            'Configuration updated',
            '{"trigger": "auto_update", "changed_fields": ["..."]}'::jsonb;

    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO data_source_versions (
            endpoint_name,
            version,
            config_snapshot,
            change_type,
            changed_by,
            change_summary,
            metadata
        )
        SELECT
            OLD.endpoint_name,
            COALESCE((
                SELECT MAX(version)
                FROM data_source_versions
                WHERE endpoint_name = OLD.endpoint_name
            ), 0) + 1,
            row_to_json(OLD)::jsonb,
            'delete',
            current_user,
            'Configuration deleted',
            '{"trigger": "auto_delete"}'::jsonb;
    END IF;

    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 注意：此触发器需要在实际应用时手动创建和绑定
-- CREATE TRIGGER auto_create_version
-- AFTER INSERT OR UPDATE OR DELETE ON data_source_registry
-- FOR EACH ROW EXECUTE FUNCTION create_version_trigger();

-- ============================================================================
-- Sample Data (Optional - for testing)
-- ============================================================================

-- 插入示例版本记录（测试用）
-- INSERT INTO data_source_versions (
--     endpoint_name,
--     version,
--     config_snapshot,
--     change_type,
--     changed_by,
--     change_summary,
--     metadata
-- )
-- SELECT
--     'akshare.stock_zh_a_hist',
--     1,
--     '{"source_name": "akshare", "data_category": "DAILY_KLINE", "priority": 2}'::jsonb,
--     'create',
--     'system',
--     'Initial version from YAML config',
--     '{"imported_from": "yaml"}'::jsonb
-- ON CONFLICT DO NOTHING;

-- 插入示例审计日志（测试用）
-- INSERT INTO data_source_audit_log (
--     endpoint_name,
--     action,
--     actor,
--     timestamp,
--     request_body,
--     response_status,
--     execution_time_ms
-- )
-- VALUES
--     ('akshare.stock_zh_a_hist', 'read', 'system', CURRENT_TIMESTAMP,
--      '{"endpoint_name": "akshare.stock_zh_a_hist"}'::jsonb,
--      200, 45);

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- 验证表是否创建成功
-- SELECT table_name, table_type
-- FROM information_schema.tables
-- WHERE table_schema = 'public'
--   AND table_name IN ('data_source_versions', 'data_source_audit_log')
-- ORDER BY table_name;

-- 验证索引是否创建成功
-- SELECT indexname, tablename
-- FROM pg_indexes
-- WHERE schemaname = 'public'
--   AND tablename IN ('data_source_versions', 'data_source_audit_log')
-- ORDER BY tablename, indexname;

-- 验证外键是否创建成功
-- SELECT constraint_name, table_name, foreign_table_name
-- FROM information_schema.table_constraints AS tc
-- JOIN information_schema.key_column_usage AS kcu
--   ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.referential_constraints AS rc
--   ON tc.constraint_name = rc.constraint_name
-- WHERE tc.table_schema = 'public'
--   AND tc.table_name IN ('data_source_versions', 'data_source_audit_log');

-- ============================================================================
-- Rollback Instructions
-- ============================================================================
-- If you need to rollback this migration:

-- DROP TRIGGER IF EXISTS auto_create_version ON data_source_registry;
-- DROP FUNCTION IF EXISTS create_version_trigger();
-- DROP TABLE IF EXISTS data_source_audit_log CASCADE;
-- DROP TABLE IF EXISTS data_source_versions CASCADE;

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Status: ✅ Successfully created
-- Version: 004
-- Date: 2026-01-09
-- Next Steps:
--   1. Run this script in PostgreSQL database
--   2. Verify tables and indexes are created
--   3. Implement ConfigManager class
--   4. Implement CRUD API endpoints
-- ============================================================================
