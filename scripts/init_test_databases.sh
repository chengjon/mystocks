#!/bin/bash
# init_test_databases.sh
# 初始化测试数据库脚本
# 基于生产环境配置创建测试数据库

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo -e "  MyStocks 测试数据库初始化"
echo -e "==========================================${NC}"
echo ""

# 加载测试环境变量
if [ -f .env.test ]; then
    echo -e "${GREEN}✅ 加载测试环境变量: .env.test${NC}"
    export $(cat .env.test | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ 错误: .env.test 文件不存在${NC}"
    echo -e "${YELLOW}请先创建 .env.test 文件${NC}"
    exit 1
fi

echo ""
echo "==========================================="
echo "  配置信息"
echo "==========================================="
echo "TDengine Host: $TDENGINE_HOST:$TDENGINE_PORT"
echo "TDengine User: $TDENGINE_USER"
echo "TDengine Database: $TDENGINE_DATABASE"
echo ""
echo "PostgreSQL Host: $POSTGRESQL_HOST:$POSTGRESQL_PORT"
echo "PostgreSQL User: $POSTGRESQL_USER"
echo "PostgreSQL Database: $POSTGRESQL_DATABASE"
echo "==========================================="
echo ""

# 确认操作
echo -e "${YELLOW}警告: 此操作将在测试数据库中创建表和示例数据${NC}"
read -p "是否继续? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}操作已取消${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}=========================================="
echo -e "  开始初始化数据库"
echo -e "==========================================${NC}"
echo ""

# ============================================
# 1. 初始化 TDengine 测试数据库
# ============================================
echo -e "[1/4] ${BLUE}初始化 TDengine 测试数据库...${NC}"

# 创建测试数据库
echo "创建数据库: $TDENGINE_DATABASE"
taos -h "$TDENGINE_HOST" -P "$TDENGINE_PORT" -u "$TDENGINE_USER" -p "$TDENGINE_PASSWORD" -s "
CREATE DATABASE IF NOT EXISTS $TDENGINE_DATABASE;
" 2>/dev/null || echo -e "${YELLOW}⚠️  TDengine连接失败，跳过初始化${NC}"

# 创建超表（时序数据）
echo "创建超表: tick_data"
taos -h "$TDENGINE_HOST" -P "$TDENGINE_PORT" -u "$TDENGINE_USER" -p "$TDENGINE_PASSWORD" -s "
USE $TDENGINE_DATABASE;
CREATE STABLE IF NOT EXISTS tick_data (
    ts TIMESTAMP,
    price FLOAT,
    volume BIGINT,
    amount DOUBLE,
    bid_price FLOAT,
    ask_price FLOAT
) TAGS (
    symbol BINARY(20),
    exchange BINARY(10)
);

CREATE STABLE IF NOT EXISTS minute_kline (
    ts TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    amount DOUBLE,
    turnover DOUBLE
) TAGS (
    symbol BINARY(20),
    exchange BINARY(10)
);
" 2>/dev/null && echo -e "${GREEN}✅ TDengine 数据库初始化完成${NC}" || echo -e "${YELLOW}⚠️  TDengine 初始化失败${NC}"

echo ""

# ============================================
# 2. 初始化 PostgreSQL 测试数据库
# ============================================
echo -e "[2/4] ${BLUE}初始化 PostgreSQL 测试数据库...${NC}"

# 创建测试数据库
echo "创建数据库: $POSTGRESQL_DATABASE"
PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -c "
DROP DATABASE IF EXISTS $POSTGRESQL_DATABASE;
CREATE DATABASE $POSTGRESQL_DATABASE;
" 2>/dev/null || echo -e "${YELLOW}⚠️  PostgreSQL连接失败，跳过初始化${NC}"

# 连接到测试数据库并创建表
echo "创建表结构..."
PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" << 'EOFSQL'
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 日线数据表
CREATE TABLE IF NOT EXISTS daily_kline (
    symbol VARCHAR(20),
    date DATE,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    amount DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (symbol, date)
);

-- 转换为Hypertable
SELECT create_hypertable('daily_kline', 'date', if_not_exists => TRUE);

-- 股票基本信息表
CREATE TABLE IF NOT EXISTS stock_basic_info (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    industry VARCHAR(100),
    market VARCHAR(20),
    list_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

SELECT create_hypertable('stock_basic_info', 'created_at', if_not_exists => TRUE);

-- 技术指标表
CREATE TABLE IF NOT EXISTS technical_indicators (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    date DATE,
    indicator_type VARCHAR(50),
    indicator_value DECIMAL(20,4),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

SELECT create_hypertable('technical_indicators', 'created_at', if_not_exists => TRUE);
EOFSQL

echo -e "${GREEN}✅ PostgreSQL 数据库初始化完成${NC}"

echo ""

# ============================================
# 3. 初始化监控表
# ============================================
echo -e "[3/4] ${BLUE}初始化监控表...${NC}"

PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" << 'EOFSQL'
-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    operation_id VARCHAR(50) PRIMARY KEY,
    operation_type VARCHAR(50),
    classification VARCHAR(100),
    target_database VARCHAR(20),
    table_name VARCHAR(100),
    record_count INTEGER,
    operation_status VARCHAR(20),
    error_message TEXT,
    execution_time_ms INTEGER,
    user_agent VARCHAR(200),
    client_ip VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 性能指标表
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value DOUBLE,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

SELECT create_hypertable('performance_metrics', 'timestamp', if_not_exists => TRUE);

-- 警报表
CREATE TABLE IF NOT EXISTS alert_records (
    alert_id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    message TEXT,
    details JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

SELECT create_hypertable('alert_records', 'created_at', if_not_exists => TRUE);

-- 数据质量检查表
CREATE TABLE IF NOT EXISTS data_quality_checks (
    check_id SERIAL PRIMARY KEY,
    data_type VARCHAR(100),
    check_type VARCHAR(50),
    total_records INTEGER,
    passed_records INTEGER,
    failed_records INTEGER,
    pass_rate DECIMAL(5,2),
    check_timestamp TIMESTAMP DEFAULT NOW(),
    details JSONB
);
EOFSQL

echo -e "${GREEN}✅ 监控表初始化完成${NC}"

echo ""

# ============================================
# 4. 插入测试数据（可选）
# ============================================
echo -e "[4/4] ${BLUE}插入测试数据...${NC}"

read -p "是否插入示例测试数据? (yes/no): " insert_data

if [ "$insert_data" = "yes" ]; then
    echo "插入日线测试数据..."
    PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" << 'EOFSQL'
    -- 插入日线测试数据
    INSERT INTO daily_kline (symbol, date, open, high, low, close, volume) VALUES
    ('600000.SH', '2024-01-01', 10.50, 10.80, 10.30, 10.70, 1000000),
    ('600000.SH', '2024-01-02', 10.70, 10.90, 10.60, 10.85, 1200000),
    ('600000.SH', '2024-01-03', 10.85, 11.00, 10.75, 10.95, 1500000),
    ('600001.SH', '2024-01-01', 20.50, 20.80, 20.30, 20.70, 500000),
    ('600001.SH', '2024-01-02', 20.70, 21.00, 20.60, 20.90, 600000);

    -- 插入股票基本信息
    INSERT INTO stock_basic_info (symbol, name, industry, market, list_date) VALUES
    ('600000.SH', '浦发银行', '银行', 'sh', '1999-11-10'),
    ('600001.SH', '上证指数', '指数', 'sh', '1990-12-19'),
    ('000001.SZ', '平安银行', '银行', 'sz', '1991-04-03');
EOFSQL
    echo -e "${GREEN}✅ 测试数据插入完成${NC}"
else
    echo -e "${YELLOW}⏭  跳过测试数据插入${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo -e "  数据库初始化完成！"
echo -e "==========================================${NC}"
echo ""
echo "测试数据库已准备就绪："
echo "  - TDengine: $TDENGINE_HOST:$TDENGINE_PORT/$TDENGINE_DATABASE"
echo "  - PostgreSQL: $POSTGRESQL_HOST:$POSTGRESQL_PORT/$POSTGRESQL_DATABASE"
echo ""
echo "下一步："
echo "  1. 加载环境变量: export \$(cat .env.test | xargs)"
echo "  2. 运行测试: pytest tests/unit/ -v"
echo ""
