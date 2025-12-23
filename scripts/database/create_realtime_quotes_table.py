#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建实时行情数据表
"""

import psycopg2
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def create_realtime_quotes_table():
    """创建实时行情数据表"""
    try:
        # 连接PostgreSQL数据库
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST"),
            port=os.getenv("POSTGRESQL_PORT"),
            database=os.getenv("POSTGRESQL_DATABASE"),
            user=os.getenv("POSTGRESQL_USER"),
            password=os.getenv("POSTGRESQL_PASSWORD"),
        )

        cursor = conn.cursor()

        # 删除已存在的表（如果存在）
        cursor.execute("DROP TABLE IF EXISTS realtime_market_quotes")

        # 创建实时行情数据表
        create_table_sql = """
        CREATE TABLE realtime_market_quotes (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            name VARCHAR(100),
            pct_chg DECIMAL(10,4),
            close DECIMAL(10,4),
            high DECIMAL(10,4),
            low DECIMAL(10,4),
            open DECIMAL(10,4),
            change DECIMAL(10,4),
            turnover_rate DECIMAL(10,4),
            volume BIGINT,
            amount DECIMAL(18,2),
            total_mv DECIMAL(18,2),
            circ_mv DECIMAL(18,2),
            fetch_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_source VARCHAR(50) DEFAULT 'efinance',
            data_type VARCHAR(50) DEFAULT 'realtime_quotes',
            market VARCHAR(10) DEFAULT 'HS',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 创建索引
        CREATE INDEX idx_realtime_quotes_symbol ON realtime_market_quotes(symbol);
        CREATE INDEX idx_realtime_quotes_timestamp ON realtime_market_quotes(fetch_timestamp);

        -- 添加列注释（PostgreSQL方式）
        COMMENT ON TABLE realtime_market_quotes IS '实时行情数据表';
        COMMENT ON COLUMN realtime_market_quotes.symbol IS '股票代码';
        COMMENT ON COLUMN realtime_market_quotes.name IS '股票名称';
        COMMENT ON COLUMN realtime_market_quotes.pct_chg IS '涨跌幅(%)';
        COMMENT ON COLUMN realtime_market_quotes.close IS '最新价';
        COMMENT ON COLUMN realtime_market_quotes.high IS '最高价';
        COMMENT ON COLUMN realtime_market_quotes.low IS '最低价';
        COMMENT ON COLUMN realtime_market_quotes.open IS '开盘价';
        COMMENT ON COLUMN realtime_market_quotes.change IS '涨跌额';
        COMMENT ON COLUMN realtime_market_quotes.turnover_rate IS '换手率(%)';
        COMMENT ON COLUMN realtime_market_quotes.volume IS '成交量';
        COMMENT ON COLUMN realtime_market_quotes.amount IS '成交额';
        COMMENT ON COLUMN realtime_market_quotes.total_mv IS '总市值';
        COMMENT ON COLUMN realtime_market_quotes.circ_mv IS '流通市值';
        COMMENT ON COLUMN realtime_market_quotes.fetch_timestamp IS '数据获取时间';
        COMMENT ON COLUMN realtime_market_quotes.data_source IS '数据来源';
        COMMENT ON COLUMN realtime_market_quotes.data_type IS '数据类型';
        COMMENT ON COLUMN realtime_market_quotes.market IS '市场代码';
        """

        cursor.execute(create_table_sql)
        conn.commit()

        print("✅ 成功创建 realtime_market_quotes 表")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ 创建表失败: {str(e)}")
        return False


if __name__ == "__main__":
    create_realtime_quotes_table()
