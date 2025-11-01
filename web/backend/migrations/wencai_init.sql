-- ============================================================================
-- 问财股票筛选功能 - 数据库初始化脚本
-- ============================================================================
-- 创建日期: 2025-10-17
-- 作者: MyStocks Backend Team
-- 说明: 创建问财查询定义表并插入9个预定义查询
-- ============================================================================

-- 创建问财查询定义表
CREATE TABLE IF NOT EXISTS wencai_queries (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    query_name VARCHAR(20) NOT NULL UNIQUE COMMENT '查询名称，如qs_1',
    query_text TEXT NOT NULL COMMENT '查询语句（自然语言）',
    description VARCHAR(255) DEFAULT NULL COMMENT '查询说明',
    is_active BOOLEAN DEFAULT TRUE NOT NULL COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT '更新时间',
    INDEX idx_query_name (query_name),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问财查询定义表';

-- 插入9个预定义查询
INSERT INTO wencai_queries (query_name, query_text, description, is_active) VALUES
('qs_1', '请列举出20天内出现过涨停，量比大于1.5倍以上，换手率大于3%，振幅小于5%，流通市值小于200亿的股票', '涨停板筛选', TRUE),
('qs_2', '请列出近2周内资金流入持续5天为正，且涨幅不超过5%的股票', '资金流入持续为正', TRUE),
('qs_3', '请列出近3个月内出现过5日平均换手率大于30%的股票', '高换手率', TRUE),
('qs_4', '20日涨跌幅小于10%，换手率小于10%，市值小于100亿元，周成交量环比增长率大于100%前20名，当日涨幅＜4%，排除ST', '成交量放量', TRUE),
('qs_5', '请列出2024年1月1日以来上市满10个月的股票里，平均换手率大于40%或者换手率标准差大于15%的股票', '新股高换手', TRUE),
('qs_6', '请列出现近1周内板块资金流入持续为正的板块名称', '板块资金流向', TRUE),
('qs_7', '请列出现价小于30元、平均换手率大于20%、交易天数不少于250天的股票', '低价活跃股', TRUE),
('qs_8', '今日热度前300', '热度排行', TRUE),
('qs_9', '请列出均线多头排列，10天内有过涨停板，非ST，日线MACD金叉且日线KDJ金叉的股票', '技术形态综合筛选', TRUE)
ON DUPLICATE KEY UPDATE
    query_text = VALUES(query_text),
    description = VALUES(description),
    is_active = VALUES(is_active),
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- 查询结果表 (wencai_qs_1 ~ wencai_qs_9)
-- ============================================================================
-- 注意：查询结果表将在首次执行查询时由程序自动创建
-- 因为不同查询返回的字段不同，无法预先定义
--
-- 表名格式: wencai_qs_1, wencai_qs_2, ..., wencai_qs_9
--
-- 共同字段（所有结果表都会包含）:
--   - id: INT PRIMARY KEY AUTO_INCREMENT
--   - fetch_time: TIMESTAMP (数据获取时间)
--   - 取数区间: VARCHAR(50) (查询时间范围)
--   - 其他字段: 根据问财API返回动态创建
--
-- 索引策略:
--   - PRIMARY KEY (id)
--   - INDEX idx_fetch_time (fetch_time)
--   - INDEX idx_stock_code (股票代码) -- 如果存在该字段
-- ============================================================================

-- 验证数据
SELECT
    query_name,
    description,
    is_active,
    created_at
FROM wencai_queries
ORDER BY query_name;

-- ============================================================================
-- 完成
-- ============================================================================
-- 说明:
-- 1. wencai_queries 表已创建并填充数据
-- 2. 查询结果表会在首次查询时自动创建
-- 3. 支持的查询: qs_1 ~ qs_9
-- ============================================================================
