-- ========================================
-- MyStocks 股票数据扩展功能 - MySQL表初始化脚本
-- 版本: 1.0.0
-- 日期: 2025-10-14
-- 说明: 创建2个MySQL表(策略配置 + 分红数据)
-- ========================================

USE quant_research;

-- 1. 策略配置表
CREATE TABLE IF NOT EXISTS strategy_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL UNIQUE,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_description TEXT,
    category VARCHAR(50),
    parameters JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_active (is_active),
    INDEX idx_strategy_id (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略配置表';

-- 2. 分红配送数据表
CREATE TABLE IF NOT EXISTS dividend_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    announce_date DATE NOT NULL,
    ex_dividend_date DATE,
    record_date DATE,
    dividend_ratio DECIMAL(10, 4),
    bonus_share_ratio DECIMAL(10, 4),
    transfer_ratio DECIMAL(10, 4),
    allotment_ratio DECIMAL(10, 4),
    allotment_price DECIMAL(10, 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_symbol_announce_date (symbol, announce_date),
    INDEX idx_symbol (symbol),
    INDEX idx_ex_dividend_date (ex_dividend_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分红配送数据表';

SELECT '✅ MySQL tables created successfully!' AS status;
SELECT '   - strategy_configs' AS tables;
SELECT '   - dividend_data' AS tables;
