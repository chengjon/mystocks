-- 创建市场数据表的SQL脚本
-- 包含7个表：
-- 1. stock_fund_flow - 个股资金流向
-- 2. etf_spot_data - ETF实时数据
-- 3. chip_race_data - 竞价抢筹数据
-- 4. stock_lhb_detail - 龙虎榜详细数据
-- 5. sector_fund_flow - 行业/概念资金流向
-- 6. stock_dividend - 股票分红配送
-- 7. stock_blocktrade - 股票大宗交易

-- 1. 个股资金流向表
CREATE TABLE IF NOT EXISTS stock_fund_flow (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    main_net_inflow DECIMAL(20, 2),
    main_net_inflow_rate DECIMAL(10, 4),
    super_large_net_inflow DECIMAL(20, 2),
    large_net_inflow DECIMAL(20, 2),
    medium_net_inflow DECIMAL(20, 2),
    small_net_inflow DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_stock_fund_flow UNIQUE (symbol, trade_date, timeframe)
);

CREATE INDEX IF NOT EXISTS idx_stock_fund_flow_symbol_date ON stock_fund_flow(symbol, trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_fund_flow_timeframe ON stock_fund_flow(timeframe, trade_date);

COMMENT ON TABLE stock_fund_flow IS '个股资金流向表';

-- 2. ETF实时数据表
CREATE TABLE IF NOT EXISTS etf_spot_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    trade_date DATE NOT NULL,
    latest_price DECIMAL(10, 3),
    change_percent DECIMAL(10, 4),
    change_amount DECIMAL(10, 3),
    volume BIGINT,
    amount DECIMAL(20, 2),
    open_price DECIMAL(10, 3),
    high_price DECIMAL(10, 3),
    low_price DECIMAL(10, 3),
    prev_close DECIMAL(10, 3),
    turnover_rate DECIMAL(10, 4),
    total_market_cap DECIMAL(20, 2),
    circulating_market_cap DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_etf_spot_data UNIQUE (symbol, trade_date)
);

CREATE INDEX IF NOT EXISTS idx_etf_spot_symbol ON etf_spot_data(symbol, trade_date);

COMMENT ON TABLE etf_spot_data IS 'ETF实时数据表';

-- 3. 竞价抢筹数据表
CREATE TABLE IF NOT EXISTS chip_race_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    trade_date DATE NOT NULL,
    race_type VARCHAR(10) NOT NULL,
    latest_price DECIMAL(10, 3),
    change_percent DECIMAL(10, 4),
    prev_close DECIMAL(10, 3),
    open_price DECIMAL(10, 3),
    race_amount DECIMAL(20, 2),
    race_amplitude DECIMAL(10, 4),
    race_commission DECIMAL(20, 2),
    race_transaction DECIMAL(20, 2),
    race_ratio DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_chip_race_data UNIQUE (symbol, trade_date, race_type)
);

CREATE INDEX IF NOT EXISTS idx_chip_race_symbol ON chip_race_data(symbol, trade_date);

COMMENT ON TABLE chip_race_data IS '竞价抢筹数据表';

-- 4. 龙虎榜详细数据表
CREATE TABLE IF NOT EXISTS stock_lhb_detail (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    trade_date DATE NOT NULL,
    reason VARCHAR(200),
    buy_amount DECIMAL(20, 2),
    sell_amount DECIMAL(20, 2),
    net_amount DECIMAL(20, 2),
    turnover_rate DECIMAL(10, 4),
    institution_buy DECIMAL(20, 2),
    institution_sell DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_stock_lhb_detail UNIQUE (symbol, trade_date)
);

CREATE INDEX IF NOT EXISTS idx_stock_lhb_symbol ON stock_lhb_detail(symbol, trade_date);

COMMENT ON TABLE stock_lhb_detail IS '龙虎榜详细数据表';

-- 5. 行业/概念资金流向表
CREATE TABLE IF NOT EXISTS sector_fund_flow (
    id BIGSERIAL PRIMARY KEY,
    sector_code VARCHAR(50) NOT NULL,
    sector_name VARCHAR(100) NOT NULL,
    sector_type VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    latest_price DECIMAL(10, 3),
    change_percent DECIMAL(10, 4),
    main_net_inflow DECIMAL(20, 2),
    main_net_inflow_rate DECIMAL(10, 4),
    super_large_net_inflow DECIMAL(20, 2),
    super_large_net_inflow_rate DECIMAL(10, 4),
    large_net_inflow DECIMAL(20, 2),
    large_net_inflow_rate DECIMAL(10, 4),
    medium_net_inflow DECIMAL(20, 2),
    medium_net_inflow_rate DECIMAL(10, 4),
    small_net_inflow DECIMAL(20, 2),
    small_net_inflow_rate DECIMAL(10, 4),
    leading_stock VARCHAR(100),
    leading_stock_change_percent DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_sector_fund_flow UNIQUE (sector_code, trade_date, timeframe)
);

CREATE INDEX IF NOT EXISTS idx_sector_fund_flow_code ON sector_fund_flow(sector_code, trade_date);
CREATE INDEX IF NOT EXISTS idx_sector_fund_flow_type ON sector_fund_flow(sector_type, timeframe, trade_date);

COMMENT ON TABLE sector_fund_flow IS '行业/概念资金流向表';

-- 6. 股票分红配送表
CREATE TABLE IF NOT EXISTS stock_dividend (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    announce_date DATE,
    ex_dividend_date DATE,
    record_date DATE,
    payment_date DATE,
    dividend_year VARCHAR(10),
    plan_profile VARCHAR(200),
    dividend_ratio DECIMAL(10, 4),
    bonus_share_ratio DECIMAL(10, 4),
    transfer_ratio DECIMAL(10, 4),
    allotment_ratio DECIMAL(10, 4),
    allotment_price DECIMAL(10, 3),
    plan_progress VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stock_dividend_symbol ON stock_dividend(symbol, announce_date);
CREATE INDEX IF NOT EXISTS idx_stock_dividend_ex_date ON stock_dividend(ex_dividend_date);

COMMENT ON TABLE stock_dividend IS '股票分红配送表';

-- 7. 股票大宗交易表
CREATE TABLE IF NOT EXISTS stock_blocktrade (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    trade_date DATE NOT NULL,
    deal_price DECIMAL(10, 3),
    close_price DECIMAL(10, 3),
    premium_ratio DECIMAL(10, 4),
    deal_amount DECIMAL(20, 2),
    deal_volume BIGINT,
    turnover_rate DECIMAL(10, 4),
    buyer_name VARCHAR(200),
    seller_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stock_blocktrade_symbol ON stock_blocktrade(symbol, trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_blocktrade_date ON stock_blocktrade(trade_date);

COMMENT ON TABLE stock_blocktrade IS '股票大宗交易表';
