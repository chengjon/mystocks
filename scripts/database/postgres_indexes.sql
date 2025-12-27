-- MyStocks PostgreSQL Index Optimization
-- Phase 5 Database Performance Optimization
-- Generated for high-frequency query patterns

-- ============================================================================
-- CRITICAL: High-Frequency Query Indexes
-- ============================================================================

-- Market Data Table Indexes
-- Used by: /api/v1/market/overview, /api/v1/market/index
CREATE INDEX IF NOT EXISTS idx_market_daily_kline_date_symbol
ON market_daily_kline (trade_date DESC, stock_code)
INCLUDE (open_price, close_price, high_price, low_price, volume);

CREATE INDEX IF NOT EXISTS idx_market_daily_kline_stock_date
ON market_daily_kline (stock_code, trade_date DESC);

-- Stock Quote Table Indexes
-- Used by: /api/v1/stock/{code}/quote
CREATE INDEX IF NOT EXISTS idx_stock_quote_stock_updated
ON stock_quote (stock_code, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_stock_quote_change_desc
ON stock_quote (change_percent DESC NULLS LAST)
WHERE change_percent IS NOT NULL;

-- Fund Flow Table Indexes
-- Used by: /api/v1/market/fund-flow
CREATE INDEX IF NOT EXISTS idx_fund_flow_date_type
ON fund_flow (flow_date DESC, flow_type);

CREATE INDEX IF NOT EXISTS idx_fund_flow_stock_date
ON fund_flow (stock_code, flow_date DESC);

-- Dragon Tiger List Indexes
-- Used by: /api/v1/market/dragon-tiger
CREATE INDEX IF NOT EXISTS idx_dragon_tiger_date
ON dragon_tiger_list (trade_date DESC);

CREATE INDEX IF NOT EXISTS idx_dragon_tiger_buy_amount
ON dragon_tiger_list (buy_amount DESC NULLS LAST)
WHERE trade_date = CURRENT_DATE;

-- ============================================================================
-- COMPOSITE INDEXES FOR COMPLEX QUERIES
-- ============================================================================

-- Portfolio Holdings Composite Index
-- Used by: /api/v1/portfolio/summary
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_user_stock
ON portfolio_holdings (user_id, stock_code);

CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_user_value
ON portfolio_holdings (user_id, current_value DESC NULLS LAST);

-- Order History Composite Index
-- Used by: /api/v1/trade/history
CREATE INDEX IF NOT EXISTS idx_orders_user_date
ON orders (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_orders_user_status
ON orders (user_id, status)
WHERE status IN ('pending', 'filled');

-- Strategy Performance Composite Index
-- Used by: /api/v1/strategy/backtest
CREATE INDEX IF NOT EXISTS idx_strategy_backtest_user_date
ON strategy_backtests (user_id, created_at DESC);

-- ============================================================================
-- PARTIAL INDEXES FOR COMMON FILTER PATTERNS
-- ============================================================================

-- Index for today's data only (used frequently)
CREATE INDEX IF NOT EXISTS idx_market_daily_kline_today
ON market_daily_kline (stock_code, trade_date DESC)
WHERE trade_date >= CURRENT_DATE - INTERVAL '7 days';

-- Index for active orders
CREATE INDEX IF NOT EXISTS idx_orders_pending
ON orders (user_id, created_at DESC)
WHERE status = 'pending';

-- Index for profitable positions
CREATE INDEX IF NOT EXISTS idx_portfolio_profitable
ON portfolio_holdings (user_id, unrealized_pnl DESC NULLS LAST)
WHERE unrealized_pnl > 0;

-- ============================================================================
-- TEXT SEARCH INDEXES
-- ============================================================================

-- For stock search functionality
CREATE INDEX IF NOT EXISTS idx_stock_info_name_trgm
ON stock_info USING GIN (stock_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_stock_info_code_trgm
ON stock_info USING GIN (stock_code gin_trgm_ops);

-- ============================================================================
-- INDEX MAINTENANCE
-- ============================================================================

-- Run periodically to maintain index efficiency
ANALYZE market_daily_kline;
ANALYZE stock_quote;
ANALYZE fund_flow;
ANALYZE dragon_tiger_list;
ANALYZE portfolio_holdings;
ANALYZE orders;

-- Reindex periodically for performance
-- REINDEX INDEX CONCURRENTLY idx_market_daily_kline_date_symbol;

-- ============================================================================
-- INDEX USAGE MONITORING
-- ============================================================================

-- Check which indexes are being used
SELECT
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;

-- Find unused indexes (candidates for removal)
SELECT
    indexrelname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexrelname NOT LIKE 'pg_%';
