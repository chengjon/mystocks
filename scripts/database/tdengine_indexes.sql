-- MyStocks TDengine Index Optimization
-- Phase 5 Database Performance Optimization
-- Note: TDengine uses time-series specific optimizations

-- ============================================================================
-- TDENGINE STABLE DEFINITIONS WITH OPTIMIZED TAGS
-- ============================================================================

-- Tick Data Stable (high-frequency)
CREATE STABLE IF NOT EXISTS ts_tick_data (
    ts TIMESTAMP,
    price FLOAT,
    volume FLOAT,
    buy_volume FLOAT,
    sell_volume FLOAT,
    turnover FLOAT,
    change FLOAT,
    bid1_price FLOAT,
    bid1_volume FLOAT,
    ask1_price FLOAT,
    ask1_volume FLOAT
) TAGS (
    stock_code BINARY(20),
    exchange BINARY(10)
);

-- Minute K-line Stable
CREATE STABLE IF NOT EXISTS ts_minute_kline (
    ts TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    turnover FLOAT,
    change FLOAT
) TAGS (
    stock_code BINARY(20),
    period BINARY(10)  -- '1min', '5min', '15min', etc.
);

-- Daily K-line Stable
CREATE STABLE IF NOT EXISTS ts_daily_kline (
    ts TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    turnover FLOAT,
    change FLOAT,
    change_percent FLOAT,
    amplitude FLOAT,
    turnover_rate FLOAT
) TAGS (
    stock_code BINARY(20),
    isST BINARY(5)
);

-- ============================================================================
-- TDENGINE TAG INDEXES (Critical for Performance)
-- ============================================================================

-- These are automatically created when tags are defined
-- But we ensure they're properly configured

-- Stock code tag index (used in all queries)
-- Already created by TDengine automatically

-- ============================================================================
-- COMMON QUERY PATTERNS AND OPTIMIZATION
-- ============================================================================

-- Pattern 1: Get latest tick data for a stock
-- Optimization: Use cache for recent data
-- The tag filter on stock_code is already optimized by TDengine

-- Pattern 2: Get K-line data for date range
-- Optimization: Use time-range queries efficiently
-- Example: SELECT * FROM ts_daily_kline WHERE stock_code='000001'
--          AND ts >= '2024-01-01' AND ts < '2024-12-31'

-- Pattern 3: Get multiple stocks data
-- Optimization: Use batch queries
-- Example: SELECT * FROM ts_daily_kline WHERE stock_code IN ('000001', '000002')

-- ============================================================================
-- DATA RETENTION POLICIES
-- ============================================================================

-- Set retention policy for tick data (keep 3 months)
ALTER STABLE ts_tick_data RETENTION 90d;

-- Set retention policy for minute data (keep 1 year)
ALTER STABLE ts_minute_kline RETENTION 365d;

-- Daily data is kept indefinitely by default

-- ============================================================================
-- QUERY OPTIMIZATION GUIDELINES
-- ============================================================================

-- 1. Always filter by time range first (TDengine optimizes this)
-- Bad: SELECT * FROM ts_daily_kline WHERE stock_code='000001'
-- Good: SELECT * FROM ts_daily_kline WHERE ts >= '2024-01-01' AND ts < '2024-12-31' AND stock_code='000001'

-- 2. Use INTERVAL for time-series aggregations
-- Example: SELECT _WSTART, AVG(close) FROM ts_minute_kline
--          INTERVAL('1h') WHERE stock_code='000001'

-- 3. Cache frequently accessed data in Redis
-- Pattern: Cache K-line data for 5 minutes
-- Pattern: Cache quote data for 1 second

-- ============================================================================
-- PERFORMANCE MONITORING
-- ============================================================================

-- Check query performance
SHOW QUERIES;

-- Check stream processing
SHOW STREAMS;

-- Check storage usage
SELECT * FROM information_schema.ins_databases;

-- ============================================================================
-- SAMPLE QUERIES FOR REFERENCE
-- ============================================================================

-- Get daily K-line for single stock
-- SELECT * FROM ts_daily_kline WHERE stock_code='000001'
-- ORDER BY ts DESC LIMIT 100;

-- Get K-line for multiple stocks
-- SELECT ts, stock_code, close FROM ts_daily_kline
-- WHERE stock_code IN ('000001', '000002', '000003')
-- ORDER BY ts DESC;

-- Get minute data with aggregation
-- SELECT _WSTART AS window_start, AVG(close) AS avg_close,
--        MAX(high) AS max_high, MIN(low) AS min_low
-- FROM ts_minute_kline
-- WHERE stock_code='000001' AND ts >= '2024-01-01' AND ts < '2024-01-02'
-- INTERVAL('15m');

-- Get trading statistics
-- SELECT COUNT(*) AS trade_count, SUM(volume) AS total_volume
-- FROM ts_tick_data
-- WHERE stock_code='000001' AND ts >= '2024-01-01';
