-- 创建策略系统相关表的SQL脚本
-- 包含3个表：
-- 1. strategy_definition - 策略定义和元数据
-- 2. strategy_result - 策略筛选结果
-- 3. strategy_backtest - 策略回测结果

-- 1. 策略定义表
CREATE TABLE IF NOT EXISTS strategy_definition (
    id SERIAL PRIMARY KEY,
    strategy_code VARCHAR(50) UNIQUE NOT NULL,
    strategy_name_cn VARCHAR(100) NOT NULL,
    strategy_name_en VARCHAR(100) NOT NULL,
    description TEXT,
    parameters JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_strategy_code ON strategy_definition(strategy_code);

COMMENT ON TABLE strategy_definition IS '策略定义表';
COMMENT ON COLUMN strategy_definition.strategy_code IS '策略代码';
COMMENT ON COLUMN strategy_definition.strategy_name_cn IS '策略中文名';
COMMENT ON COLUMN strategy_definition.strategy_name_en IS '策略英文名';
COMMENT ON COLUMN strategy_definition.description IS '策略描述';
COMMENT ON COLUMN strategy_definition.parameters IS '策略参数(JSON格式)';
COMMENT ON COLUMN strategy_definition.is_active IS '是否启用';

-- 2. 策略筛选结果表
CREATE TABLE IF NOT EXISTS strategy_result (
    id BIGSERIAL PRIMARY KEY,
    strategy_code VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    check_date DATE NOT NULL,
    match_result BOOLEAN NOT NULL,
    match_score INTEGER,
    match_details JSONB,
    latest_price VARCHAR(20),
    change_percent VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_strategy_result_code_date ON strategy_result(strategy_code, check_date);
CREATE INDEX IF NOT EXISTS idx_strategy_result_symbol_date ON strategy_result(symbol, check_date);
CREATE INDEX IF NOT EXISTS idx_strategy_result_match ON strategy_result(match_result, check_date);

COMMENT ON TABLE strategy_result IS '策略筛选结果表';
COMMENT ON COLUMN strategy_result.strategy_code IS '策略代码';
COMMENT ON COLUMN strategy_result.symbol IS '股票代码';
COMMENT ON COLUMN strategy_result.stock_name IS '股票名称';
COMMENT ON COLUMN strategy_result.check_date IS '检查日期';
COMMENT ON COLUMN strategy_result.match_result IS '是否匹配策略条件';
COMMENT ON COLUMN strategy_result.match_score IS '匹配度评分(0-100)';
COMMENT ON COLUMN strategy_result.match_details IS '匹配详情(JSON格式)';
COMMENT ON COLUMN strategy_result.latest_price IS '最新价';
COMMENT ON COLUMN strategy_result.change_percent IS '涨跌幅';

-- 3. 策略回测结果表
CREATE TABLE IF NOT EXISTS strategy_backtest (
    id BIGSERIAL PRIMARY KEY,
    strategy_code VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    signal_date DATE NOT NULL,
    entry_price VARCHAR(20),
    exit_price VARCHAR(20),
    exit_date DATE,
    holding_days INTEGER,
    return_rate VARCHAR(20),
    max_drawdown VARCHAR(20),
    backtest_period VARCHAR(50),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_backtest_code_date ON strategy_backtest(strategy_code, signal_date);
CREATE INDEX IF NOT EXISTS idx_backtest_symbol ON strategy_backtest(symbol, signal_date);

COMMENT ON TABLE strategy_backtest IS '策略回测结果表';
COMMENT ON COLUMN strategy_backtest.strategy_code IS '策略代码';
COMMENT ON COLUMN strategy_backtest.symbol IS '股票代码';
COMMENT ON COLUMN strategy_backtest.stock_name IS '股票名称';
COMMENT ON COLUMN strategy_backtest.signal_date IS '信号日期';
COMMENT ON COLUMN strategy_backtest.entry_price IS '入场价格';
COMMENT ON COLUMN strategy_backtest.exit_price IS '出场价格';
COMMENT ON COLUMN strategy_backtest.exit_date IS '出场日期';
COMMENT ON COLUMN strategy_backtest.holding_days IS '持有天数';
COMMENT ON COLUMN strategy_backtest.return_rate IS '收益率(%)';
COMMENT ON COLUMN strategy_backtest.max_drawdown IS '最大回撤(%)';
COMMENT ON COLUMN strategy_backtest.backtest_period IS '回测区间';
COMMENT ON COLUMN strategy_backtest.parameters IS '策略参数';

-- 初始化10个策略定义数据
INSERT INTO strategy_definition (strategy_code, strategy_name_cn, strategy_name_en, description, parameters, is_active) VALUES
('volume_surge', '放量上涨', 'Volume Surge', '成交量放大2倍以上且价格上涨的股票', '{"threshold": 60, "min_amount": 200000000, "vol_ratio": 2}', TRUE),
('ma_bullish', '均线多头', 'MA Bullish', '短期均线在长期均线上方，多条均线向上发散', '{"threshold": 30, "ma_period": 30, "growth_rate": 1.2}', TRUE),
('turtle_trading', '海龟交易法则', 'Turtle Trading', '创出60日新高的股票', '{"threshold": 60}', TRUE),
('consolidation_platform', '停机坪', 'Consolidation Platform', '股价横盘整理，成交量缩小，蓄势待发', '{"threshold": 15, "surge_threshold": 9.5}', TRUE),
('ma250_pullback', '回踩年线', 'MA250 Pullback', '股价回踩250日均线获得支撑', '{"threshold": 60, "ma_period": 250, "vol_ratio": 2}', TRUE),
('breakthrough_platform', '突破平台', 'Breakthrough Platform', '股价突破前期平台高点', '{"threshold": 60, "ma_period": 60}', TRUE),
('low_drawdown', '无大幅回撤', 'Low Drawdown', '上涨过程中回撤幅度较小的强势股', '{"threshold": 60, "min_growth": 0.6}', TRUE),
('high_tight_flag', '高而窄的旗形', 'High Tight Flag', '快速上涨后窄幅整理的旗形形态', '{"threshold": 60, "price_ratio": 1.9}', TRUE),
('volume_limit_down', '放量跌停', 'Volume Limit Down', '放量且跌停，识别恐慌性抛售', '{"threshold": 60, "drop_rate": -9.5, "vol_ratio": 4}', TRUE),
('low_atr_growth', '低ATR成长', 'Low ATR Growth', 'ATR（平均真实波幅）较低但稳定增长', '{"threshold": 10, "min_days": 250, "growth_ratio": 1.1, "max_atr": 10}', TRUE)
ON CONFLICT (strategy_code) DO NOTHING;
