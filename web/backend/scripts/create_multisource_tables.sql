-- ============================================================================
-- Phase 3: ValueCell Migration - Multi-data Source Integration
-- Database Schema for Multi-source Data and Announcements
-- ============================================================================

-- 数据源配置表
CREATE TABLE IF NOT EXISTS data_source_config (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL UNIQUE,  -- 数据源类型：akshare, eastmoney, cninfo, wencai
    priority INTEGER NOT NULL DEFAULT 1,  -- 优先级（1最高）
    enabled BOOLEAN DEFAULT TRUE,  -- 是否启用
    timeout INTEGER DEFAULT 30,  -- 超时时间（秒）
    retry_count INTEGER DEFAULT 3,  -- 重试次数
    rate_limit INTEGER,  -- 每分钟请求限制
    api_key VARCHAR(200),  -- API密钥
    extra_params JSONB DEFAULT '{}',  -- 额外参数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_source_config IS '数据源配置表';
COMMENT ON COLUMN data_source_config.source_type IS '数据源类型';
COMMENT ON COLUMN data_source_config.priority IS '优先级，1最高，数字越小优先级越高';
COMMENT ON COLUMN data_source_config.rate_limit IS '每分钟请求限制';

-- 数据源健康状态表
CREATE TABLE IF NOT EXISTS data_source_health (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,  -- 数据源类型
    status VARCHAR(50) NOT NULL,  -- 状态：available, degraded, unavailable, maintenance, rate_limited, error
    success_rate DECIMAL(5, 4) DEFAULT 0.0,  -- 成功率 (0-1)
    avg_response_time DECIMAL(10, 3) DEFAULT 0.0,  -- 平均响应时间（秒）
    error_count INTEGER DEFAULT 0,  -- 错误次数
    error_message TEXT,  -- 最后错误信息
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 最后检查时间
    supported_categories JSONB DEFAULT '[]',  -- 支持的数据类别
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_source_health IS '数据源健康状态表';
COMMENT ON COLUMN data_source_health.status IS '状态：available(可用), degraded(降级), unavailable(不可用), maintenance(维护中), rate_limited(请求受限), error(错误)';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_dsh_source_type ON data_source_health(source_type);
CREATE INDEX IF NOT EXISTS idx_dsh_last_check ON data_source_health(last_check);

-- 公告数据表
CREATE TABLE IF NOT EXISTS announcement (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,  -- 股票代码
    stock_name VARCHAR(100),  -- 股票名称
    announcement_title TEXT NOT NULL,  -- 公告标题
    announcement_type VARCHAR(100),  -- 公告类型
    publish_date DATE NOT NULL,  -- 发布日期
    publish_time TIMESTAMP,  -- 发布时间
    url TEXT,  -- 公告链接
    content TEXT,  -- 公告内容（可选）
    summary TEXT,  -- 公告摘要
    keywords JSONB DEFAULT '[]',  -- 关键词
    importance_level INTEGER DEFAULT 0,  -- 重要性级别 (0-5, 5最重要)

    -- 多数据源字段
    data_source VARCHAR(50) NOT NULL,  -- 数据来源：cninfo, eastmoney等
    source_id VARCHAR(200),  -- 来源系统中的ID

    -- 分析字段
    is_analyzed BOOLEAN DEFAULT FALSE,  -- 是否已分析
    sentiment VARCHAR(20),  -- 情感分析结果：positive, negative, neutral
    impact_score DECIMAL(5, 2),  -- 影响评分 (0-100)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(stock_code, source_id, data_source)  -- 防止重复
);

COMMENT ON TABLE announcement IS '股票公告数据表';
COMMENT ON COLUMN announcement.announcement_type IS '公告类型：业绩预告、重大事项、分红送转等';
COMMENT ON COLUMN announcement.importance_level IS '重要性级别：0-5，5最重要';
COMMENT ON COLUMN announcement.sentiment IS '情感分析：positive(利好), negative(利空), neutral(中性)';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_announcement_stock ON announcement(stock_code);
CREATE INDEX IF NOT EXISTS idx_announcement_date ON announcement(publish_date DESC);
CREATE INDEX IF NOT EXISTS idx_announcement_type ON announcement(announcement_type);
CREATE INDEX IF NOT EXISTS idx_announcement_importance ON announcement(importance_level DESC);
CREATE INDEX IF NOT EXISTS idx_announcement_source ON announcement(data_source);

-- 公告监控规则表
CREATE TABLE IF NOT EXISTS announcement_monitor_rule (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL UNIQUE,  -- 规则名称
    keywords JSONB DEFAULT '[]',  -- 关键词列表
    announcement_types JSONB DEFAULT '[]',  -- 监控的公告类型
    stock_codes JSONB DEFAULT '[]',  -- 监控的股票代码（空表示全部）
    min_importance_level INTEGER DEFAULT 0,  -- 最小重要性级别

    -- 通知设置
    notify_enabled BOOLEAN DEFAULT TRUE,  -- 是否启用通知
    notify_channels JSONB DEFAULT '["email"]',  -- 通知渠道：email, webhook, sms

    is_active BOOLEAN DEFAULT TRUE,  -- 是否激活
    created_by INTEGER,  -- 创建人ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE announcement_monitor_rule IS '公告监控规则表';
COMMENT ON COLUMN announcement_monitor_rule.keywords IS '关键词列表，匹配标题或内容';
COMMENT ON COLUMN announcement_monitor_rule.announcement_types IS '监控的公告类型列表';

-- 公告监控记录表
CREATE TABLE IF NOT EXISTS announcement_monitor_record (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES announcement_monitor_rule(id) ON DELETE CASCADE,  -- 规则ID
    announcement_id INTEGER REFERENCES announcement(id) ON DELETE CASCADE,  -- 公告ID
    matched_keywords JSONB DEFAULT '[]',  -- 匹配的关键词
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 触发时间
    notified BOOLEAN DEFAULT FALSE,  -- 是否已通知
    notified_at TIMESTAMP,  -- 通知时间
    notification_result TEXT  -- 通知结果
);

COMMENT ON TABLE announcement_monitor_record IS '公告监控触发记录表';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_amr_rule ON announcement_monitor_record(rule_id);
CREATE INDEX IF NOT EXISTS idx_amr_announcement ON announcement_monitor_record(announcement_id);
CREATE INDEX IF NOT EXISTS idx_amr_triggered ON announcement_monitor_record(triggered_at DESC);

-- 数据源使用统计表
CREATE TABLE IF NOT EXISTS data_source_usage (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,  -- 数据源类型
    data_category VARCHAR(100) NOT NULL,  -- 数据类别
    request_count INTEGER DEFAULT 0,  -- 请求次数
    success_count INTEGER DEFAULT 0,  -- 成功次数
    error_count INTEGER DEFAULT 0,  -- 失败次数
    total_response_time DECIMAL(15, 3) DEFAULT 0.0,  -- 总响应时间
    avg_response_time DECIMAL(10, 3) DEFAULT 0.0,  -- 平均响应时间
    last_used_at TIMESTAMP,  -- 最后使用时间
    date DATE NOT NULL,  -- 统计日期

    UNIQUE(source_type, data_category, date)
);

COMMENT ON TABLE data_source_usage IS '数据源使用统计表（按日统计）';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_dsu_source ON data_source_usage(source_type);
CREATE INDEX IF NOT EXISTS idx_dsu_date ON data_source_usage(date DESC);

-- ============================================================================
-- 插入默认配置数据
-- ============================================================================

-- 插入默认数据源配置
INSERT INTO data_source_config (source_type, priority, enabled, timeout, retry_count, extra_params)
VALUES
    ('eastmoney', 1, TRUE, 30, 3, '{"description": "东方财富网免费API"}'),
    ('cninfo', 2, TRUE, 30, 3, '{"description": "巨潮资讯官方公告"}'),
    ('akshare', 3, TRUE, 30, 3, '{"description": "AKShare免费数据源"}'),
    ('wencai', 4, TRUE, 30, 3, '{"description": "问财筛选系统"}')
ON CONFLICT (source_type) DO NOTHING;

-- 插入初始健康状态
INSERT INTO data_source_health (source_type, status, success_rate, supported_categories)
VALUES
    ('eastmoney', 'available', 1.0, '["realtime_quote", "fund_flow", "dragon_tiger", "etf_data", "sector_data", "dividend", "block_trade"]'),
    ('cninfo', 'available', 1.0, '["announcement", "financial_report"]'),
    ('akshare', 'available', 1.0, '["realtime_quote", "historical_quote", "fund_flow", "dragon_tiger"]'),
    ('wencai', 'available', 1.0, '["realtime_quote", "sector_data"]')
ON CONFLICT DO NOTHING;

-- 插入默认公告监控规则
INSERT INTO announcement_monitor_rule (rule_name, keywords, announcement_types, min_importance_level, notify_enabled)
VALUES
    ('重大事项监控', '["重大资产重组", "收购", "并购", "增发", "定向增发"]', '["重大事项"]', 3, TRUE),
    ('业绩预告监控', '["业绩预增", "业绩预降", "业绩快报", "业绩预告"]', '["业绩预告", "业绩快报"]', 2, TRUE),
    ('分红送转监控', '["分红", "送转", "派息", "股权激励"]', '["分红派息", "送转"]', 2, TRUE),
    ('风险提示监控', '["风险提示", "退市", "ST", "*ST", "诉讼", "仲裁"]', '["风险提示"]', 4, TRUE),
    ('高管变动监控', '["董事", "高管", "总经理", "财务总监", "辞职", "任免"]', '["人事变动"]', 1, TRUE)
ON CONFLICT (rule_name) DO NOTHING;

-- ============================================================================
-- 创建视图
-- ============================================================================

-- 数据源健康状态视图（最新）
CREATE OR REPLACE VIEW v_data_source_health_latest AS
SELECT DISTINCT ON (source_type)
    dsh.*,
    dsc.priority,
    dsc.enabled
FROM data_source_health dsh
LEFT JOIN data_source_config dsc ON dsh.source_type = dsc.source_type
ORDER BY source_type, last_check DESC;

COMMENT ON VIEW v_data_source_health_latest IS '数据源最新健康状态视图';

-- 今日公告统计视图
CREATE OR REPLACE VIEW v_announcement_today_stats AS
SELECT
    data_source,
    COUNT(*) as announcement_count,
    COUNT(DISTINCT stock_code) as stock_count,
    COUNT(*) FILTER (WHERE importance_level >= 3) as important_count,
    COUNT(*) FILTER (WHERE sentiment = 'positive') as positive_count,
    COUNT(*) FILTER (WHERE sentiment = 'negative') as negative_count,
    COUNT(*) FILTER (WHERE sentiment = 'neutral') as neutral_count
FROM announcement
WHERE publish_date = CURRENT_DATE
GROUP BY data_source;

COMMENT ON VIEW v_announcement_today_stats IS '今日公告统计视图';

-- 公告监控触发统计视图
CREATE OR REPLACE VIEW v_announcement_monitor_stats AS
SELECT
    amr.rule_name,
    COUNT(DISTINCT amr_rec.announcement_id) as triggered_count,
    COUNT(*) FILTER (WHERE amr_rec.notified = TRUE) as notified_count,
    MAX(amr_rec.triggered_at) as last_triggered_at
FROM announcement_monitor_rule amr
LEFT JOIN announcement_monitor_record amr_rec ON amr.id = amr_rec.rule_id
WHERE amr.is_active = TRUE
GROUP BY amr.id, amr.rule_name;

COMMENT ON VIEW v_announcement_monitor_stats IS '公告监控规则触发统计视图';

-- ============================================================================
-- 完成
-- ============================================================================

-- 打印创建成功信息
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Phase 3: Multi-source Integration Tables Created Successfully';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Created Tables:';
    RAISE NOTICE '  1. data_source_config - 数据源配置';
    RAISE NOTICE '  2. data_source_health - 数据源健康状态';
    RAISE NOTICE '  3. announcement - 公告数据';
    RAISE NOTICE '  4. announcement_monitor_rule - 公告监控规则';
    RAISE NOTICE '  5. announcement_monitor_record - 公告监控记录';
    RAISE NOTICE '  6. data_source_usage - 数据源使用统计';
    RAISE NOTICE '';
    RAISE NOTICE 'Created Views:';
    RAISE NOTICE '  1. v_data_source_health_latest - 最新健康状态';
    RAISE NOTICE '  2. v_announcement_today_stats - 今日公告统计';
    RAISE NOTICE '  3. v_announcement_monitor_stats - 监控触发统计';
    RAISE NOTICE '';
    RAISE NOTICE 'Default Data:';
    RAISE NOTICE '  - 4 data source configurations';
    RAISE NOTICE '  - 4 health status records';
    RAISE NOTICE '  - 5 announcement monitor rules';
    RAISE NOTICE '============================================================================';
END $$;
