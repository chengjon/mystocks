-- =============================================================================
-- SQL Query Templates for Layer 5: Data Validation
-- =============================================================================
-- Purpose: Provide reusable SQL patterns for verifying data existence,
--          freshness, integrity, and reasonableness
-- Usage: Copy these templates and modify table/column names as needed
-- Database: PostgreSQL (primary) and TDengine (time-series data)
-- =============================================================================

-- =============================================================================
-- 1. DATA EXISTENCE CHECKS
-- =============================================================================

-- Template 1.1: Check if table has any data
SELECT COUNT(*) as record_count FROM table_name;
-- Expected: record_count > 0
-- If 0: Run data collection scripts

-- Template 1.2: Check data count by date (龙虎榜 - Dragon Tiger)
SELECT trade_date, COUNT(*) as count
FROM cn_stock_top
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 10;
-- Expected: Multiple dates with data
-- Verify: Latest date is recent

-- Template 1.3: Check data count by date (ETF 数据 - ETF Data)
SELECT trade_date, COUNT(*) as count
FROM cn_etf_spot
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 10;

-- Template 1.4: Check data count by date (资金流向 - Fund Flow)
SELECT trade_date, COUNT(*) as count
FROM cn_stock_fund_flow_industry
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 10;

-- Template 1.5: Check data count by date (竞价抢筹 - Chip Race)
SELECT trade_date, COUNT(*) as count
FROM cn_stock_chip_race_open
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 10;

-- =============================================================================
-- 2. DATA FRESHNESS CHECKS (时效性)
-- =============================================================================

-- Template 2.1: Get latest trade date
SELECT MAX(trade_date) as latest_date FROM table_name;
-- Expected: Today or most recent trading day
-- Alert if: > 1 business day old

-- Template 2.2: Check data freshness across all market tables
SELECT
    'cn_stock_top' as table_name,
    MAX(trade_date) as latest_date,
    COUNT(*) as record_count
FROM cn_stock_top
UNION ALL
SELECT
    'cn_etf_spot' as table_name,
    MAX(trade_date) as latest_date,
    COUNT(*) as record_count
FROM cn_etf_spot
UNION ALL
SELECT
    'cn_stock_fund_flow_industry' as table_name,
    MAX(trade_date) as latest_date,
    COUNT(*) as record_count
FROM cn_stock_fund_flow_industry
UNION ALL
SELECT
    'cn_stock_chip_race_open' as table_name,
    MAX(trade_date) as latest_date,
    COUNT(*) as record_count
FROM cn_stock_chip_race_open
ORDER BY table_name;

-- Template 2.3: Check if data exists for today (龙虎榜)
SELECT COUNT(*) as today_count
FROM cn_stock_top
WHERE trade_date = CURRENT_DATE;
-- Expected: > 0 (if market is open today)
-- If 0: Check if today is trading day or data collection failed

-- Template 2.4: Check data age in days
SELECT
    MAX(trade_date) as latest_date,
    CURRENT_DATE as today,
    CURRENT_DATE - MAX(trade_date) as days_old
FROM table_name;
-- Expected: days_old ≤ 1 (for daily data)
-- Alert if: days_old > 3

-- =============================================================================
-- 3. DATA INTEGRITY CHECKS (完整性)
-- =============================================================================

-- Template 3.1: Check for NULL values in key fields
SELECT COUNT(*) as null_count
FROM table_name
WHERE key_field1 IS NULL OR key_field2 IS NULL;
-- Expected: 0
-- If > 0: Data collection error

-- Template 3.2: Check NULL values in dragon tiger table
SELECT COUNT(*) as null_count
FROM cn_stock_top
WHERE stock_code IS NULL OR stock_name IS NULL OR trade_date IS NULL;
-- Expected: 0

-- Template 3.3: Check NULL values in multiple fields (detailed)
SELECT
    COUNT(*) as total_records,
    COUNT(stock_code) as has_code,
    COUNT(stock_name) as has_name,
    COUNT(trade_date) as has_date,
    COUNT(close_price) as has_price,
    COUNT(change_percent) as has_change
FROM cn_stock_top;
-- Expected: All counts equal to total_records

-- Template 3.4: Find records with NULL in any critical field
SELECT *
FROM table_name
WHERE key_field1 IS NULL
   OR key_field2 IS NULL
   OR key_field3 IS NULL
LIMIT 10;
-- Expected: No records returned
-- If records found: Investigate data collection logic

-- Template 3.5: Check for empty strings (different from NULL)
SELECT COUNT(*) as empty_string_count
FROM table_name
WHERE key_text_field = '';
-- Expected: 0

-- =============================================================================
-- 4. DATA REASONABLENESS CHECKS (合理性)
-- =============================================================================

-- Template 4.1: View latest data samples
SELECT * FROM table_name
ORDER BY created_at DESC
LIMIT 10;
-- Visual inspection for obvious errors

-- Template 4.2: View latest dragon tiger data with key fields
SELECT
    stock_code,
    stock_name,
    trade_date,
    close_price,
    change_percent,
    turnover_rate
FROM cn_stock_top
ORDER BY trade_date DESC, change_percent DESC
LIMIT 10;

-- Template 4.3: Check data ranges (min/max/avg)
SELECT
    MIN(close_price) as min_price,
    MAX(close_price) as max_price,
    AVG(close_price) as avg_price,
    MIN(change_percent) as min_change,
    MAX(change_percent) as max_change,
    AVG(change_percent) as avg_change
FROM cn_stock_top
WHERE trade_date = (SELECT MAX(trade_date) FROM cn_stock_top);
-- Expected ranges:
-- price: > 0 and < 10000 (most stocks)
-- change_percent: -10% to +10% (normal stocks), -20% to +20% (ST stocks)

-- Template 4.4: Find outlier prices (potentially bad data)
SELECT stock_code, stock_name, close_price, trade_date
FROM cn_stock_top
WHERE close_price <= 0 OR close_price > 10000
ORDER BY close_price DESC
LIMIT 10;
-- Expected: Few or no records
-- If many records: Data quality issue

-- Template 4.5: Find outlier change percentages
SELECT stock_code, stock_name, change_percent, trade_date
FROM cn_stock_top
WHERE ABS(change_percent) > 20
ORDER BY ABS(change_percent) DESC
LIMIT 10;
-- Expected: Only ST stocks or special cases
-- If many normal stocks: Data quality issue

-- Template 4.6: Check stock code format (6 digits)
SELECT stock_code, stock_name
FROM cn_stock_top
WHERE stock_code !~ '^[0-9]{6}$'
LIMIT 10;
-- Expected: No records
-- If records found: Data format error

-- Template 4.7: Check for duplicate records
SELECT stock_code, trade_date, COUNT(*) as count
FROM cn_stock_top
GROUP BY stock_code, trade_date
HAVING COUNT(*) > 1
LIMIT 10;
-- Expected: No records
-- If records found: Data insertion error (duplicate key issue)

-- =============================================================================
-- 5. DATA COMPLETENESS CHECKS (完整性)
-- =============================================================================

-- Template 5.1: Compare record counts across dates
SELECT
    trade_date,
    COUNT(*) as record_count,
    LAG(COUNT(*)) OVER (ORDER BY trade_date) as prev_day_count,
    COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY trade_date) as diff
FROM cn_stock_top
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 10;
-- Expected: Similar record counts across dates
-- Alert if: Sudden large drop (>50%) in record count

-- Template 5.2: Check expected record count for dragon tiger
SELECT
    trade_date,
    COUNT(*) as actual_count,
    CASE
        WHEN COUNT(*) < 10 THEN '⚠️ Too few records'
        WHEN COUNT(*) > 1000 THEN '⚠️ Unusually many records'
        ELSE '✅ Normal'
    END as status
FROM cn_stock_top
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 10;

-- Template 5.3: Check if all expected industries have data (fund flow)
SELECT
    industry_type,
    industry_name,
    COUNT(*) as record_count
FROM cn_stock_fund_flow_industry
WHERE trade_date = (SELECT MAX(trade_date) FROM cn_stock_fund_flow_industry)
GROUP BY industry_type, industry_name
ORDER BY industry_type, record_count DESC;
-- Expected: Multiple industries with data

-- =============================================================================
-- 6. DATA COMPARISON CHECKS (across tables)
-- =============================================================================

-- Template 6.1: Compare stock codes across tables
SELECT
    (SELECT COUNT(DISTINCT stock_code) FROM cn_stock_top) as dragon_tiger_stocks,
    (SELECT COUNT(DISTINCT stock_code) FROM cn_etf_spot) as etf_stocks,
    (SELECT COUNT(DISTINCT stock_code) FROM cn_stock_chip_race_open) as chip_race_stocks;

-- Template 6.2: Find stocks in dragon tiger but not in other tables
SELECT DISTINCT ct.stock_code, ct.stock_name
FROM cn_stock_top ct
WHERE ct.trade_date = (SELECT MAX(trade_date) FROM cn_stock_top)
  AND NOT EXISTS (
      SELECT 1 FROM cn_stock_chip_race_open cr
      WHERE cr.stock_code = ct.stock_code
        AND cr.trade_date = ct.trade_date
  )
LIMIT 10;
-- Expected: Some stocks (not all tables have same coverage)

-- =============================================================================
-- 7. PERFORMANCE AND INDEX CHECKS
-- =============================================================================

-- Template 7.1: Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE 'cn_%'
ORDER BY size_bytes DESC;

-- Template 7.2: Check if indexes exist on key columns
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'cn_stock_top'
ORDER BY tablename, indexname;
-- Expected: Indexes on stock_code, trade_date

-- Template 7.3: Explain query plan for common query
EXPLAIN ANALYZE
SELECT * FROM cn_stock_top
WHERE stock_code = '000001'
  AND trade_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY trade_date DESC;
-- Expected: Index Scan (not Seq Scan) if indexes exist

-- =============================================================================
-- 8. TDENGINE-SPECIFIC QUERIES (high-frequency time-series data)
-- =============================================================================

-- Template 8.1: Check TDengine database exists
-- Run in TDengine CLI: taos -h <host> -u <user> -p<password>
SHOW DATABASES;
-- Expected: market_data database exists

-- Template 8.2: Check TDengine tables (super tables)
USE market_data;
SHOW STABLES;
-- Expected: tick_data, minute_data super tables

-- Template 8.3: Get latest tick data
SELECT LAST(*) FROM tick_data;
-- Expected: Recent timestamp (within last few seconds/minutes)

-- Template 8.4: Get latest minute data
SELECT LAST(*) FROM minute_data;
-- Expected: Recent timestamp (within last minute)

-- Template 8.5: Count tick data records
SELECT COUNT(*) FROM tick_data;
-- Expected: Large number (millions)

-- Template 8.6: Count minute data records
SELECT COUNT(*) FROM minute_data;
-- Expected: Large number (hundreds of thousands)

-- Template 8.7: Check tick data for specific stock
SELECT * FROM tick_data
WHERE stock_code = '000001'
ORDER BY ts DESC
LIMIT 10;

-- Template 8.8: Check data distribution by date (TDengine)
SELECT
    TO_CHAR(ts, 'YYYY-MM-DD') as trade_date,
    COUNT(*) as count
FROM tick_data
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 10;

-- =============================================================================
-- 9. QUICK SMOKE TEST QUERIES (run all at once)
-- =============================================================================

-- Quick Smoke Test: Run all these in sequence
SELECT 'Dragon Tiger Data' as check_name, COUNT(*) as count FROM cn_stock_top;
SELECT 'ETF Data' as check_name, COUNT(*) as count FROM cn_etf_spot;
SELECT 'Fund Flow Data' as check_name, COUNT(*) as count FROM cn_stock_fund_flow_industry;
SELECT 'Chip Race Data' as check_name, COUNT(*) as count FROM cn_stock_chip_race_open;

-- Quick Smoke Test: Latest dates
SELECT 'Dragon Tiger Latest' as check_name, MAX(trade_date) as latest FROM cn_stock_top;
SELECT 'ETF Latest' as check_name, MAX(trade_date) as latest FROM cn_etf_spot;
SELECT 'Fund Flow Latest' as check_name, MAX(trade_date) as latest FROM cn_stock_fund_flow_industry;
SELECT 'Chip Race Latest' as check_name, MAX(trade_date) as latest FROM cn_stock_chip_race_open;

-- Quick Smoke Test: NULL checks
SELECT 'Dragon Tiger NULLs' as check_name, COUNT(*) as null_count
FROM cn_stock_top WHERE stock_code IS NULL OR stock_name IS NULL;

SELECT 'ETF NULLs' as check_name, COUNT(*) as null_count
FROM cn_etf_spot WHERE stock_code IS NULL OR stock_name IS NULL;

-- =============================================================================
-- 10. MONITORING AND ALERTING QUERIES
-- =============================================================================

-- Template 10.1: Data freshness alert (data older than 1 day)
SELECT
    'cn_stock_top' as table_name,
    MAX(trade_date) as latest_date,
    CURRENT_DATE - MAX(trade_date) as days_old,
    CASE
        WHEN CURRENT_DATE - MAX(trade_date) > 1 THEN '⚠️ ALERT: Data is stale'
        ELSE '✅ OK'
    END as status
FROM cn_stock_top
UNION ALL
SELECT
    'cn_etf_spot' as table_name,
    MAX(trade_date) as latest_date,
    CURRENT_DATE - MAX(trade_date) as days_old,
    CASE
        WHEN CURRENT_DATE - MAX(trade_date) > 1 THEN '⚠️ ALERT: Data is stale'
        ELSE '✅ OK'
    END as status
FROM cn_etf_spot
UNION ALL
SELECT
    'cn_stock_fund_flow_industry' as table_name,
    MAX(trade_date) as latest_date,
    CURRENT_DATE - MAX(trade_date) as days_old,
    CASE
        WHEN CURRENT_DATE - MAX(trade_date) > 1 THEN '⚠️ ALERT: Data is stale'
        ELSE '✅ OK'
    END as status
FROM cn_stock_fund_flow_industry
UNION ALL
SELECT
    'cn_stock_chip_race_open' as table_name,
    MAX(trade_date) as latest_date,
    CURRENT_DATE - MAX(trade_date) as days_old,
    CASE
        WHEN CURRENT_DATE - MAX(trade_date) > 1 THEN '⚠️ ALERT: Data is stale'
        ELSE '✅ OK'
    END as status
FROM cn_stock_chip_race_open;

-- Template 10.2: Data completeness alert (sudden drop in record count)
WITH daily_counts AS (
    SELECT
        trade_date,
        COUNT(*) as record_count,
        LAG(COUNT(*)) OVER (ORDER BY trade_date) as prev_count
    FROM cn_stock_top
    GROUP BY trade_date
    ORDER BY trade_date DESC
    LIMIT 5
)
SELECT
    trade_date,
    record_count,
    prev_count,
    ROUND(100.0 * (record_count - prev_count) / NULLIF(prev_count, 0), 2) as percent_change,
    CASE
        WHEN ABS(100.0 * (record_count - prev_count) / NULLIF(prev_count, 0)) > 50
            THEN '⚠️ ALERT: Large change in record count'
        ELSE '✅ OK'
    END as status
FROM daily_counts
WHERE prev_count IS NOT NULL;

-- =============================================================================
-- USAGE NOTES
-- =============================================================================
/*
1. Connect to PostgreSQL:
   pgcli -h localhost -U mystocks_user -d mystocks
   OR
   PGPASSWORD=mystocks2025 pgcli -h localhost -U mystocks_user -d mystocks

2. Run templates by copying and pasting into pgcli

3. Customize table_name, key_field1, etc. for your specific needs

4. For TDengine queries, connect using:
   taos -h 192.168.123.104 -u root -ptaosdata

5. Save custom queries for frequently used validations

6. Integrate these queries into monitoring dashboards (Grafana, etc.)

7. Set up alerts based on Template 10.x queries
*/
