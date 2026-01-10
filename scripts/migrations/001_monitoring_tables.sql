-- =====================================================
-- 智能量化监控与决策系统 - 数据库表创建脚本
-- =====================================================
-- 版本: v1.0
-- 创建日期: 2026-01-07
-- 作者: Claude Code (Main CLI)
-- 描述: Phase 1.1 - 创建监控相关的PostgreSQL表
-- =====================================================

-- 设置搜索路径
SET search_path TO public;

-- =====================================================
-- 1. 监控清单主表
-- =====================================================
CREATE TABLE IF NOT EXISTS monitoring_watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) DEFAULT 'manual',
    risk_profile JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON monitoring_watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_type ON monitoring_watchlists(type);
CREATE INDEX IF NOT EXISTS idx_watchlists_active ON monitoring_watchlists(is_active);

-- 添加注释
COMMENT ON TABLE monitoring_watchlists IS '监控清单主表 - 存储投资组合/观察列表信息';
COMMENT ON COLUMN monitoring_watchlists.type IS '清单类型: manual(手动), strategy(策略自动), benchmark(基准)';
COMMENT ON COLUMN monitoring_watchlists.risk_profile IS '风控配置 JSONB - {risk_tolerance, max_drawdown_limit, etc.}';

-- =====================================================
-- 2. 清单成员表（增强版：入库上下文）
-- =====================================================
CREATE TABLE IF NOT EXISTS monitoring_watchlist_stocks (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER NOT NULL REFERENCES monitoring_watchlists(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    
    -- 入库上下文（关键新增）
    entry_price DECIMAL(10,2),
    entry_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entry_reason VARCHAR(50),
    
    -- 风控设置
    stop_loss_price DECIMAL(10,2),
    target_price DECIMAL(10,2),
    
    weight DECIMAL(5,4) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- 唯一约束
    UNIQUE(watchlist_id, stock_code)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_watchlist_stocks_watchlist ON monitoring_watchlist_stocks(watchlist_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_stocks_stock_code ON monitoring_watchlist_stocks(stock_code);
CREATE INDEX IF NOT EXISTS idx_watchlist_stocks_active ON monitoring_watchlist_stocks(is_active);

-- 添加注释
COMMENT ON TABLE monitoring_watchlist_stocks IS '清单成员表 - 存储股票及其入库上下文';
COMMENT ON COLUMN monitoring_watchlist_stocks.entry_price IS '入库价格';
COMMENT ON COLUMN monitoring_watchlist_stocks.entry_reason IS '入库理由: macd_gold_cross, manual_pick, etc.';
COMMENT ON COLUMN monitoring_watchlist_stocks.stop_loss_price IS '止损价格';
COMMENT ON COLUMN monitoring_watchlist_stocks.target_price IS '止盈价格';

-- =====================================================
-- 3. 每日健康度评分
-- =====================================================

-- 先添加缺失的列（如果表已存在）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'monitoring_health_scores') THEN
        -- 添加高级风险指标列（如果不存在）
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monitoring_health_scores' AND column_name = 'sortino_ratio') THEN
            ALTER TABLE monitoring_health_scores ADD COLUMN sortino_ratio DECIMAL(10,4);
            RAISE NOTICE '添加列: sortino_ratio';
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monitoring_health_scores' AND column_name = 'calmar_ratio') THEN
            ALTER TABLE monitoring_health_scores ADD COLUMN calmar_ratio DECIMAL(10,4);
            RAISE NOTICE '添加列: calmar_ratio';
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monitoring_health_scores' AND column_name = 'max_drawdown_duration') THEN
            ALTER TABLE monitoring_health_scores ADD COLUMN max_drawdown_duration INTEGER;
            RAISE NOTICE '添加列: max_drawdown_duration';
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monitoring_health_scores' AND column_name = 'downside_deviation') THEN
            ALTER TABLE monitoring_health_scores ADD COLUMN downside_deviation DECIMAL(10,4);
            RAISE NOTICE '添加列: downside_deviation';
        END IF;
        
        -- 添加 max_drawdown 列（如果不存在）
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'monitoring_health_scores' AND column_name = 'max_drawdown') THEN
            ALTER TABLE monitoring_health_scores ADD COLUMN max_drawdown DECIMAL(5,4);
            RAISE NOTICE '添加列: max_drawdown';
        END IF;
        
        RAISE NOTICE '✅ monitoring_health_scores 表已更新';
    ELSE
        -- 表不存在，创建新表
        CREATE TABLE monitoring_health_scores (
            id SERIAL PRIMARY KEY,
            stock_code VARCHAR(20) NOT NULL,
            score_date DATE NOT NULL,
            
            -- 综合评分
            total_score DECIMAL(5,2),
            
            -- 五维雷达分 (JSONB存储，便于扩展)
            radar_scores JSONB,
            
            -- 高级风险指标（用户要求必须包含）
            sortino_ratio DECIMAL(10,4),
            calmar_ratio DECIMAL(10,4),
            max_drawdown DECIMAL(5,4),
            max_drawdown_duration INTEGER,
            downside_deviation DECIMAL(10,4),
            
            -- 市场环境快照
            market_regime VARCHAR(20),
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- 唯一约束
            UNIQUE(stock_code, score_date)
        );
        RAISE NOTICE '创建表: monitoring_health_scores';
    END IF;
END $$;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_health_scores_stock_date ON monitoring_health_scores(stock_code, score_date DESC);
CREATE INDEX IF NOT EXISTS idx_health_scores_date ON monitoring_health_scores(score_date DESC);
CREATE INDEX IF NOT EXISTS idx_health_scores_total ON monitoring_health_scores(total_score);
CREATE INDEX IF NOT EXISTS idx_health_scores_regime ON monitoring_health_scores(market_regime);

-- 添加注释（使用 DO 块处理列不存在的情况）
DO $$
DECLARE
    col_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'monitoring_health_scores' AND column_name = 'sortino_ratio'
    ) INTO col_exists;
    
    IF col_exists THEN
        COMMENT ON COLUMN monitoring_health_scores.sortino_ratio IS 'Sortino比率 - 仅惩罚下行波动';
    END IF;
END $$;

DO $$
DECLARE
    col_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'monitoring_health_scores' AND column_name = 'calmar_ratio'
    ) INTO col_exists;
    
    IF col_exists THEN
        COMMENT ON COLUMN monitoring_health_scores.calmar_ratio IS 'Calmar比率 - 年化收益/最大回撤';
    END IF;
END $$;

DO $$
DECLARE
    col_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'monitoring_health_scores' AND column_name = 'max_drawdown_duration'
    ) INTO col_exists;
    
    IF col_exists THEN
        COMMENT ON COLUMN monitoring_health_scores.max_drawdown_duration IS '最大回撤持续天数';
    END IF;
END $$;

DO $$
DECLARE
    col_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'monitoring_health_scores' AND column_name = 'downside_deviation'
    ) INTO col_exists;
    
    IF col_exists THEN
        COMMENT ON COLUMN monitoring_health_scores.downside_deviation IS '下行标准差';
    END IF;
END $$;

-- =====================================================
-- 4. 性能优化视图（可选）
-- =====================================================

-- 先删除旧视图（如果存在且列不完整）
DROP VIEW IF EXISTS v_latest_health_scores;

-- 最新健康度评分视图（用于快速查询）
-- 使用 DO 块处理列不存在的情况
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    -- 检查是否存在所需的列
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'monitoring_health_scores'
    AND column_name IN ('sortino_ratio', 'calmar_ratio', 'max_drawdown', 'max_drawdown_duration', 'downside_deviation');
    
    IF col_count >= 5 THEN
        -- 所有列都存在，创建完整视图
        CREATE OR REPLACE VIEW v_latest_health_scores AS
        SELECT DISTINCT ON (stock_code)
            stock_code,
            score_date,
            total_score,
            radar_scores,
            sortino_ratio,
            calmar_ratio,
            max_drawdown,
            max_drawdown_duration,
            downside_deviation,
            market_regime,
            created_at
        FROM monitoring_health_scores
        ORDER BY stock_code, score_date DESC;
        
        COMMENT ON VIEW v_latest_health_scores IS '每只股票的最新健康度评分（含高级风险指标）';
    ELSE
        -- 列不完整，创建简化视图
        CREATE OR REPLACE VIEW v_latest_health_scores AS
        SELECT DISTINCT ON (stock_code)
            stock_code,
            score_date,
            total_score,
            radar_scores,
            market_regime,
            created_at
        FROM monitoring_health_scores
        ORDER BY stock_code, score_date DESC;
        
        COMMENT ON VIEW v_latest_health_scores IS '每只股票的最新健康度评分（简化版）';
    END IF;
END $$;

-- =====================================================
-- 5. 插入示例数据（开发环境用）
-- =====================================================

-- 注意：生产环境不应执行以下插入语句

-- 示例：创建测试清单
INSERT INTO monitoring_watchlists (user_id, name, type, risk_profile) VALUES
(1, '核心科技股', 'manual', '{"risk_tolerance": "high", "max_drawdown_limit": 0.2}'),
(1, '金融蓝筹', 'manual', '{"risk_tolerance": "medium", "max_drawdown_limit": 0.15}'),
(1, '成长股精选', 'manual', '{"risk_tolerance": "low", "max_drawdown_limit": 0.25}')
ON CONFLICT DO NOTHING;

-- 示例：添加股票到清单
INSERT INTO monitoring_watchlist_stocks (watchlist_id, stock_code, entry_price, entry_reason, stop_loss_price, target_price, weight) VALUES
(1, '600519.SH', 1850.00, 'macd_gold_cross', 1750.00, 2000.00, 0.30),
(1, '000001.SZ', 15.00, 'manual_pick', 14.25, 16.50, 0.25),
(1, '000002.SZ', 30.00, 'rsi_oversold', 28.50, 33.00, 0.20),
(1, '000333.SZ', 8.50, 'manual_pick', 8.00, 9.50, 0.15),
(1, '600000.SH', 12.50, 'volume_breakout', 11.80, 14.00, 0.10)
ON CONFLICT (watchlist_id, stock_code) DO NOTHING;

-- 示例：健康度评分数据（测试用）- 检查列是否存在后插入
DO $$
DECLARE
    col_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'monitoring_health_scores' AND column_name = 'sortino_ratio'
    ) INTO col_exists;
    
    IF col_exists THEN
        INSERT INTO monitoring_health_scores (
            stock_code, score_date, total_score, 
            radar_scores, 
            sortino_ratio, calmar_ratio, max_drawdown, max_drawdown_duration, downside_deviation,
            market_regime
        ) VALUES
        ('600519.SH', '2026-01-07', 85.50, 
         '{"trend": 90, "technical": 88, "momentum": 82, "volatility": 85, "risk": 82}',
         1.45, 2.30, -0.12, 15, 0.08, 'bull'),
        ('000001.SZ', '2026-01-07', 78.20,
         '{"trend": 75, "technical": 80, "momentum": 78, "volatility": 82, "risk": 76}',
         1.20, 1.80, -0.18, 22, 0.10, 'bull'),
        ('000002.SZ', '2026-01-07', 72.50,
         '{"trend": 68, "technical": 75, "momentum": 70, "volatility": 78, "risk": 71}',
         0.95, 1.40, -0.22, 28, 0.12, 'bull'),
        ('000333.SZ', '2026-01-07', 82.30,
         '{"trend": 80, "technical": 82, "momentum": 85, "volatility": 80, "risk": 84}',
         1.65, 2.60, -0.08, 18, 0.07, 'bull'),
        ('600000.SH', '2026-01-07', 80.80,
         '{"trend": 78, "technical": 80, "momentum": 78, "volatility": 82, "risk": 86}',
         1.35, 1.90, -0.15, 20, 0.09, 'bull')
        ON CONFLICT (stock_code, score_date) DO NOTHING;
    ELSE
        -- 如果列不存在，插入简化版数据
        INSERT INTO monitoring_health_scores (
            stock_code, score_date, total_score, 
            radar_scores, market_regime
        ) VALUES
        ('600519.SH', '2026-01-07', 85.50, '{"trend": 90, "technical": 88, "momentum": 82, "volatility": 85, "risk": 82}', 'bull'),
        ('000001.SZ', '2026-01-07', 78.20, '{"trend": 75, "technical": 80, "momentum": 78, "volatility": 82, "risk": 76}', 'bull'),
        ('000002.SZ', '2026-01-07', 72.50, '{"trend": 68, "technical": 75, "momentum": 70, "volatility": 78, "risk": 71}', 'bull'),
        ('000333.SZ', '2026-01-07', 82.30, '{"trend": 80, "technical": 82, "momentum": 85, "volatility": 80, "risk": 84}', 'bull'),
        ('600000.SH', '2026-01-07', 80.80, '{"trend": 78, "technical": 80, "momentum": 78, "volatility": 82, "risk": 86}', 'bull')
        ON CONFLICT (stock_code, score_date) DO NOTHING;
    END IF;
END $$;

-- =====================================================
-- 6. 验证脚本执行
-- =====================================================

-- 验证表创建
DO $$
DECLARE
    tbl_name TEXT;
    tbl_exists BOOLEAN;
BEGIN
    -- 检查 monitoring_watchlists
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'monitoring_watchlists') INTO tbl_exists;
    RAISE NOTICE 'monitoring_watchlists: %', tbl_exists;
    
    -- 检查 monitoring_watchlist_stocks
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'monitoring_watchlist_stocks') INTO tbl_exists;
    RAISE NOTICE 'monitoring_watchlist_stocks: %', tbl_exists;
    
    -- 检查 monitoring_health_scores
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'monitoring_health_scores') INTO tbl_exists;
    RAISE NOTICE 'monitoring_health_scores: %', tbl_exists;
    
    -- 检查 v_latest_health_scores
    SELECT EXISTS(SELECT 1 FROM information_schema.views WHERE table_name = 'v_latest_health_scores') INTO tbl_exists;
    RAISE NOTICE 'v_latest_health_scores: %', tbl_exists;
    
    RAISE NOTICE '✅ 数据库表创建完成!';
END $$;

-- 显示创建结果
SELECT '✅ 数据库表创建完成!' AS status;

-- =====================================================
-- 7. 性能优化说明
-- =====================================================

-- 性能优化措施：
-- 1. 使用JSONB存储雷达图 - 灵活扩展，支持后续添加维度
-- 2. 创建复合索引 (stock_code, score_date DESC) - 优化最新数据查询
-- 3. 外键约束使用 ON DELETE CASCADE - 自动清理孤儿记录
-- 4. 使用视图 v_latest_health_scores - 避免重复子查询

-- 查询性能预期：
-- - INSERT: <10ms (单条)
-- - SELECT (按stock_code): <5ms
-- - SELECT (按score_date): <15ms
-- - JOIN查询: <20ms

-- =====================================================
-- 回滚脚本（如需要）
-- =====================================================

/*
-- 删除表（谨慎使用）
DROP TABLE IF EXISTS monitoring_watchlist_stocks CASCADE;
DROP TABLE IF EXISTS monitoring_watchlists CASCADE;
DROP TABLE IF EXISTS monitoring_health_scores CASCADE;
DROP VIEW IF EXISTS v_latest_health_scores CASCADE;
*/

-- =====================================================
-- 结束
-- =====================================================
