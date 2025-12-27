-- 数据库索引创建脚本
-- 用于解决技术债务中的数据库性能优化需求

-- 连接数据库
-- \c mystocks;

-- ========================================
-- 创建 order_records 表的索引
-- ========================================

-- 检查索引是否已存在，不存在则创建
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'order_records'
        AND indexname = 'idx_order_records_user_time'
    ) THEN
        -- 复合索引：用户ID和创建时间
        -- 提高按用户查询订单的性能
        CREATE INDEX idx_order_records_user_time
        ON order_records (user_id, created_at);
        RAISE NOTICE 'Created idx_order_records_user_time index on order_records table';
    ELSE
        RAISE NOTICE 'Index idx_order_records_user_time already exists on order_records table';
    END IF;
END $$;

-- 检查现有索引
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'order_records'
ORDER BY indexname;

-- ========================================
-- 创建 daily_kline 表的索引
-- ========================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'daily_kline'
        AND indexname = 'idx_daily_kline_symbol_date'
    ) THEN
        -- 复合索引：股票代码和交易日期
        -- 提高按股票和日期范围查询的性能
        CREATE INDEX idx_daily_kline_symbol_date
        ON daily_kline (symbol, trade_date);
        RAISE NOTICE 'Created idx_daily_kline_symbol_date index on daily_kline table';
    ELSE
        RAISE NOTICE 'Index idx_daily_kline_symbol_date already exists on daily_kline table';
    END IF;
END $$;

-- ========================================
-- 创建 stock_basic_info 表的索引
-- ========================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'stock_basic_info'
        AND indexname = 'idx_stock_basic_info_code'
    ) THEN
        -- 唯一索引：股票代码
        -- 确保股票代码唯一性，提高查询性能
        CREATE UNIQUE INDEX idx_stock_basic_info_code
        ON stock_basic_info (stock_code);
        RAISE NOTICE 'Created idx_stock_basic_info_code unique index on stock_basic_info table';
    ELSE
        RAISE NOTICE 'Index idx_stock_basic_info_code already exists on stock_basic_info table';
    END IF;
END $$;

-- ========================================
-- 创建 watchlist 表的索引
-- ========================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'watchlist'
        AND indexname = 'idx_watchlist_user_symbol'
    ) THEN
        -- 复合索引：用户ID和股票代码
        -- 提高查询用户自选股列表的性能
        CREATE INDEX idx_watchlist_user_symbol
        ON watchlist (user_id, symbol);
        RAISE NOTICE 'Created idx_watchlist_user_symbol index on watchlist table';
    ELSE
        RAISE NOTICE 'Index idx_watchlist_user_symbol already exists on watchlist table';
    END IF;
END $$;

-- ========================================
-- 创建 portfolio 表的索引
-- ========================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'portfolio'
        AND indexname = 'idx_portfolio_user_code'
    ) THEN
        -- 复合索引：用户ID和股票代码
        -- 提高查询用户持仓的性能
        CREATE INDEX idx_portfolio_user_code
        ON portfolio (user_id, stock_code);
        RAISE NOTICE 'Created idx_portfolio_user_code index on portfolio table';
    ELSE
        RAISE NOTICE 'Index idx_portfolio_user_code already exists on portfolio table';
    END IF;
END $$;

-- ========================================
-- 创建 alert_conditions 表的索引
-- ========================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'alert_conditions'
        AND indexname = 'idx_alert_user_symbol'
    ) THEN
        -- 复合索引：用户ID和股票代码
        -- 提高查询用户告警条件的性能
        CREATE INDEX idx_alert_user_symbol
        ON alert_conditions (user_id, symbol);
        RAISE NOTICE 'Created idx_alert_user_symbol index on alert_conditions table';
    ELSE
        RAISE NOTICE 'Index idx_alert_user_symbol already exists on alert_conditions table';
    END IF;
END $$;

-- ========================================
-- 创建 strategy_backtest 表的索引
-- ========================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'strategy_backtest'
        AND indexname = 'idx_strategy_user_time'
    ) THEN
        -- 复合索引：用户ID和创建时间
        -- 提高查询用户回测历史的性能
        CREATE INDEX idx_strategy_user_time
        ON strategy_backtest (user_id, created_at);
        RAISE NOTICE 'Created idx_strategy_user_time index on strategy_backtest table';
    ELSE
        RAISE NOTICE 'Index idx_strategy_user_time already exists on strategy_backtest table';
    END IF;
END $$;

-- ========================================
-- 创建 trade_log 表的索引
-- ========================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'trade_log'
        AND indexname = 'idx_trade_user_symbol_time'
    ) THEN
        -- 三复合索引：用户ID、股票代码、交易时间
        -- 提高查询用户交易历史的性能
        CREATE INDEX idx_trade_user_symbol_time
        ON trade_log (user_id, symbol, trade_time);
        RAISE NOTICE 'Created idx_trade_user_symbol_time index on trade_log table';
    ELSE
        RAISE NOTICE 'Index idx_trade_user_symbol_time already exists on trade_log table';
    END IF;
END $$;

-- ========================================
-- 创建 user_audit_log 表的索引
-- ========================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'user_audit_log'
        AND indexname = 'idx_audit_user_time'
    ) THEN
        -- 复合索引：用户ID和操作时间
        -- 提高查询审计日志的性能
        CREATE INDEX idx_audit_user_time
        ON user_audit_log (user_id, action_time);
        RAISE NOTICE 'Created idx_audit_user_time index on user_audit_log table';
    ELSE
        RAISE NOTICE 'Index idx_audit_user_time already exists on user_audit_log table';
    END IF;
END $$;

-- ========================================
-- 查看所有表的索引状态
-- ========================================

-- 显示所有表的索引数量
SELECT
    schemaname,
    tablename,
    count(*) as index_count
FROM pg_indexes
WHERE tablename IN (
    'order_records', 'daily_kline', 'stock_basic_info',
    'watchlist', 'portfolio', 'alert_conditions',
    'strategy_backtest', 'trade_log', 'user_audit_log'
)
GROUP BY schemaname, tablename
ORDER BY tablename;

-- 显示每个表的主要索引
SELECT
    t.tablename,
    array_agg(i.indexname ORDER BY i.indexname) as indexes
FROM
    pg_tables t
    LEFT JOIN pg_indexes i ON t.tablename = i.tablename
WHERE
    t.tablename IN (
        'order_records', 'daily_kline', 'stock_basic_info',
        'watchlist', 'portfolio', 'alert_conditions',
        'strategy_backtest', 'trade_log', 'user_audit_log'
    )
GROUP BY t.tablename
ORDER BY t.tablename;

-- ========================================
-- 性能优化建议
-- ========================================

-- 为大表添加分区（如果需要）
-- CREATE TABLE daily_kline_partitioned (
--     symbol VARCHAR(32) NOT NULL,
--     trade_date DATE NOT NULL,
--     open_price DECIMAL(18, 4),
--     high_price DECIMAL(18, 4),
--     low_price DECIMAL(18, 4),
--     close_price DECIMAL(18, 4),
--     volume BIGINT
-- ) PARTITION BY RANGE (trade_date);

-- 更新统计信息（可选）
-- ANALYZE daily_kline;
-- ANALYZE order_records;
-- ANALYZE stock_basic_info;
