"""
监控模块数据库初始化脚本 (v3.0)

功能:
1. 连接PostgreSQL
2. 创建监控模块所需的表结构
   - monitoring_watchlists (监控清单)
   - monitoring_watchlist_stocks (清单成员+入库上下文)
   - monitoring_health_scores (健康度评分)

使用方法:
python src/monitoring/infrastructure/init_db.py
"""

import asyncio
import os
import sys
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.monitoring.infrastructure.postgresql_async import postgres_async

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def init_monitoring_tables():
    """初始化监控表结构"""
    logger.info("开始初始化监控模块数据库...")

    try:
        await postgres_async.initialize()

        async with postgres_async.pool.acquire() as conn:
            # 1. 创建 monitoring_watchlists 表
            logger.info("正在创建表: monitoring_watchlists...")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_watchlists (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    type VARCHAR(20) DEFAULT 'manual', -- manual(手动), strategy(策略自动), benchmark(基准)
                    risk_profile JSONB, -- 存储风控配置 {risk_tolerance: 'high', max_drawdown_limit: 0.2}
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                COMMENT ON TABLE monitoring_watchlists IS '监控清单主表';
                CREATE INDEX IF NOT EXISTS idx_mw_user_id ON monitoring_watchlists(user_id);
            """)

            # 2. 创建 monitoring_watchlist_stocks 表
            logger.info("正在创建表: monitoring_watchlist_stocks...")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_watchlist_stocks (
                    id SERIAL PRIMARY KEY,
                    watchlist_id INTEGER REFERENCES monitoring_watchlists(id) ON DELETE CASCADE,
                    stock_code VARCHAR(20) NOT NULL,
                    
                    -- 入库上下文 (关键新增)
                    entry_price DECIMAL(10,2),           -- 入库价格
                    entry_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 入库时间
                    entry_reason VARCHAR(50),            -- 入库理由: 'macd_gold_cross', 'manual_pick'
                    entry_strategy_id VARCHAR(50),       -- 关联的策略ID (如果有)
                    
                    -- 风控设置
                    stop_loss_price DECIMAL(10,2),       -- 止损价格
                    target_price DECIMAL(10,2),          -- 止盈价格
                    
                    weight DECIMAL(5,4) DEFAULT 0.0,     -- 目标权重
                    is_active BOOLEAN DEFAULT TRUE,
                    
                    UNIQUE(watchlist_id, stock_code)
                );
                
                COMMENT ON TABLE monitoring_watchlist_stocks IS '清单成员表 - 包含入库上下文';
                CREATE INDEX IF NOT EXISTS idx_mws_watchlist_id ON monitoring_watchlist_stocks(watchlist_id);
                CREATE INDEX IF NOT EXISTS idx_mws_stock_code ON monitoring_watchlist_stocks(stock_code);
            """)

            # 3. 创建 monitoring_health_scores 表
            logger.info("正在创建表: monitoring_health_scores...")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_health_scores (
                    id SERIAL PRIMARY KEY,
                    stock_code VARCHAR(20) NOT NULL,
                    score_date DATE NOT NULL,
                    
                    -- 综合评分
                    total_score DECIMAL(5,2),
                    
                    -- 五维雷达分 (JSONB存储)
                    -- {trend: 80, technical: 70, funding: 60, emotion: 50, risk: 90}
                    radar_scores JSONB, 
                    
                    -- 市场环境快照
                    market_regime VARCHAR(20), -- 'bull', 'bear', 'shock'
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(stock_code, score_date)
                );
                
                COMMENT ON TABLE monitoring_health_scores IS '股票健康度评分表';
                CREATE INDEX IF NOT EXISTS idx_mhs_stock_date ON monitoring_health_scores(stock_code, score_date);
            """)

        logger.info("✅ 监控模块数据库表初始化完成")

    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}")
        raise
    finally:
        await postgres_async.close()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(init_monitoring_tables())
