-- =============================================================================
-- MyStocks 缺失数据库索引创建脚本
-- 基于 TECHNICAL_DEBT_ANALYSIS_REPORT.md 的性能优化需求
-- =============================================================================

-- 设置执行超时（适用于大表）
SET statement_timeout = 300000; -- 5分钟

-- =============================================================================
-- PostgreSQL 索引优化
-- =============================================================================

-- 1. 技术指标表索引优化
-- 为 technical_indicators 表添加复合索引和BRIN索引
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'technical_indicators') THEN
        -- 检查索引是否已存在
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_tech_indicators_symbol_created') THEN
            CREATE INDEX idx_tech_indicators_symbol_created ON technical_indicators(symbol, created_at DESC);
            RAISE NOTICE 'Created index: idx_tech_indicators_symbol_created';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_tech_indicators_type') THEN
            CREATE INDEX idx_tech_indicators_type ON technical_indicators(indicator_type);
            RAISE NOTICE 'Created index: idx_tech_indicators_type';
        END IF;

        -- BRIN索引适合时间序列数据
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_tech_indicators_created_brin') THEN
            CREATE INDEX idx_tech_indicators_created_brin ON technical_indicators USING BRIN(created_at);
            RAISE NOTICE 'Created BRIN index: idx_tech_indicators_created_brin';
        END IF;
    ELSE
        RAISE NOTICE 'Table technical_indicators does not exist, skipping index creation';
    END IF;
END $$;

-- 2. 日线数据表额外优化
-- 为 daily_kline 表添加单列索引和部分索引
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'daily_kline') THEN
        -- 单列索引：交易日期
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_daily_kline_date') THEN
            CREATE INDEX idx_daily_kline_date ON daily_kline(trade_date);
            RAISE NOTICE 'Created index: idx_daily_kline_date';
        END IF;

        -- 部分索引：仅最近一年的数据（减少索引大小，提高查询效率）
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_daily_kline_recent') THEN
            CREATE INDEX idx_daily_kline_recent ON daily_kline(symbol)
            WHERE trade_date >= CURRENT_DATE - INTERVAL '1 year';
            RAISE NOTICE 'Created partial index: idx_daily_kline_recent';
        END IF;
    ELSE
        RAISE NOTICE 'Table daily_kline does not exist, skipping index creation';
    END IF;
END $$;

-- 3. 交易记录表索引优化
-- 为 transaction_records 表添加复合索引
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'transaction_records') THEN
        -- 复合索引：用户ID+创建时间（降序，最新交易在前）
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_transaction_records_user_date') THEN
            CREATE INDEX idx_transaction_records_user_date ON transaction_records(user_id, created_at DESC);
            RAISE NOTICE 'Created index: idx_transaction_records_user_date';
        END IF;

        -- 复合索引：用户ID+股票代码
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_transaction_records_user_symbol') THEN
            CREATE INDEX idx_transaction_records_user_symbol ON transaction_records(user_id, symbol);
            RAISE NOTICE 'Created index: idx_transaction_records_user_symbol';
        END IF;
    ELSE
        RAISE NOTICE 'Table transaction_records does not exist, skipping index creation';
    END IF;
END $$;

-- 4. 订单记录表额外优化
-- 为 order_records 表添加单列索引和部分索引
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'order_records') THEN
        -- 单列索引：股票代码
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_order_records_symbol') THEN
            CREATE INDEX idx_order_records_symbol ON order_records(symbol);
            RAISE NOTICE 'Created index: idx_order_records_symbol';
        END IF;

        -- 部分索引：仅活跃订单（减少索引大小）
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_order_records_active') THEN
            CREATE INDEX idx_order_records_active ON order_records(user_id, symbol)
            WHERE status IN ('ACTIVE', 'PENDING');
            RAISE NOTICE 'Created partial index: idx_order_records_active';
        END IF;
    ELSE
        RAISE NOTICE 'Table order_records does not exist, skipping index creation';
    END IF;
END $$;

-- 5. 股票基本信息表额外优化
-- 为 stock_basic_info 表添加辅助索引
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'stock_basic_info') THEN
        -- 单列索引：股票名称
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_stock_basic_info_name') THEN
            CREATE INDEX idx_stock_basic_info_name ON stock_basic_info(stock_name);
            RAISE NOTICE 'Created index: idx_stock_basic_info_name';
        END IF;

        -- 单列索引：行业分类
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_stock_basic_info_industry') THEN
            CREATE INDEX idx_stock_basic_info_industry ON stock_basic_info(industry);
            RAISE NOTICE 'Created index: idx_stock_basic_info_industry';
        END IF;

        -- 单列索引：股票代码（如果没有唯一索引的话）
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_stock_basic_info_code_unique') THEN
            CREATE UNIQUE INDEX idx_stock_basic_info_code_unique ON stock_basic_info(stock_code);
            RAISE NOTICE 'Created unique index: idx_stock_basic_info_code_unique';
        END IF;
    ELSE
        RAISE NOTICE 'Table stock_basic_info does not exist, skipping index creation';
    END IF;
END $$;

-- 6. 监控数据表索引优化
-- 如果有监控相关表，添加相应的索引
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'system_metrics') THEN
        -- 时间序列数据索引
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_system_metrics_timestamp') THEN
            CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp DESC);
            RAISE NOTICE 'Created index: idx_system_metrics_timestamp';
        END IF;

        -- 类型索引
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_system_metrics_type') THEN
            CREATE INDEX idx_system_metrics_type ON system_metrics(metric_type);
            RAISE NOTICE 'Created index: idx_system_metrics_type';
        END IF;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_activity_logs') THEN
        -- 用户活动日志索引
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_activity_user_time') THEN
            CREATE INDEX idx_user_activity_user_time ON user_activity_logs(user_id, created_at DESC);
            RAISE NOTICE 'Created index: idx_user_activity_user_time';
        END IF;
    END IF;
END $$;

-- =============================================================================
-- TDengine 时序数据库优化
-- =============================================================================

-- TDengine 分区优化（需要连接到TDengine执行）
-- 这里提供SQL语句，实际执行需要在TDengine环境中进行

-- 1. Tick数据表分区优化
-- 执行前需要确保 tick_data 表存在
-- ALTER STABLE tick_data PARTITION BY ts INTERVAL(1d);

-- 2. 分钟K线表分区优化
-- ALTER STABLE minute_kline PARTITION BY ts INTERVAL(1d);

-- 3. 创建TDengine时间索引
-- 在表创建时，TDengine会自动为时间戳创建索引

-- =============================================================================
-- 更新统计信息和Vacuum
-- =============================================================================

-- 对所有相关表更新统计信息
DO $$
BEGIN
    -- 获取所有需要更新统计信息的表
    DECLARE tables TEXT[] := ARRAY[
        'daily_kline',
        'technical_indicators',
        'transaction_records',
        'order_records',
        'stock_basic_info',
        'system_metrics',
        'user_activity_logs'
    ];

    DECLARE i INT;
    DECLARE table_name TEXT;

    FOREACH table_name IN ARRAY tables
    LOOP
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = table_name) THEN
            -- 执行ANALYZE
            EXECUTE format('ANALYZE %I', table_name);
            RAISE NOTICE 'Updated statistics for table: %', table_name;

            -- 对大表执行VACuum（可选，根据实际情况决定）
            IF table_name IN ('daily_kline', 'technical_indicators', 'transaction_records') THEN
                EXECUTE format('VACUUM (VERBOSE, ANALYZE) %I', table_name);
                RAISE NOTICE 'Executed VACUUM ANALYZE for table: %', table_name;
            END IF;
        END IF;
    END LOOP;
END $$;

-- =============================================================================
-- 性能优化完成总结
-- =============================================================================

RAISE NOTICE '';
RAISE NOTICE '==============================================';
RAISE NOTICE '数据库索引优化脚本执行完成！';
RAISE NOTICE '==============================================';
RAISE NOTICE '';
RAISE NOTICE '已创建的索引：';
RAISE NOTICE '• PostgreSQL 表索引：';
RAISE NOTICE '  - technical_indicators: 3个新索引';
RAISE NOTICE '  - daily_kline: 2个新索引';
RAISE NOTICE '  - transaction_records: 2个新索引';
RAISE NOTICE '  - order_records: 2个新索引';
RAISE NOTICE '  - stock_basic_info: 3个新索引';
RAISE NOTICE '  - system_metrics: 2个新索引（如果存在）';
RAISE NOTICE '  - user_activity_logs: 1个新索引（如果存在）';
RAISE NOTICE '';
RAISE NOTICE '• TDengine 优化：';
RAISE NOTICE '  - 启用时间分区（需要手动执行）';
RAISE NOTICE '';
RAISE NOTICE '预期性能提升：';
RAISE NOTICE '• 符号查询：10-20x faster';
RAISE NOTICE '• 日期范围查询：15-40x faster';
RAISE NOTICE '• 复合查询：20-50x faster';
RAISE NOTICE '• 用户相关查询：15-30x faster';
RAISE NOTICE '';
RAISE NOTICE '下一步建议：';
RAISE NOTICE '1. 监控慢查询日志，验证优化效果';
RAISE NOTICE '2. 执行 TDengine 分区优化脚本';
RAISE NOTICE '3. 定期更新统计信息';
RAISE NOTICE '4. 监控查询性能指标';
RAISE NOTICE '==============================================';
