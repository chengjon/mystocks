#!/usr/bin/env python3
"""
股票基础信息数据填充脚本

功能:
- 从AkShare获取A股股票列表
- 填充到PostgreSQL的stock_info表
- 支持增量更新
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import akshare as ak
import psycopg2
from datetime import datetime
from typing import List, Dict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_stock_list_from_akshare() -> List[Dict]:
    """
    从AkShare获取股票列表

    Returns:
        List[Dict]: 股票信息列表
    """
    logger.info("正在从AkShare获取股票列表...")

    try:
        # 获取A股股票列表
        df = ak.stock_info_a_code_name()

        logger.info(f"成功获取 {len(df)} 只股票信息")

        # Convert to list of dicts
        stocks = []
        for _, row in df.iterrows():
            # AkShare returns: code, name
            symbol = row["code"]
            name = row["name"]

            # Determine exchange and format symbol
            if symbol.startswith("6"):
                exchange = "SSE"  # Shanghai Stock Exchange
                full_symbol = f"{symbol}.SH"
            elif symbol.startswith("0") or symbol.startswith("3"):
                exchange = "SZSE"  # Shenzhen Stock Exchange
                full_symbol = f"{symbol}.SZ"
            elif symbol.startswith("4") or symbol.startswith("8"):
                exchange = "BSE"  # Beijing Stock Exchange
                full_symbol = f"{symbol}.BJ"
            else:
                exchange = "UNKNOWN"
                full_symbol = symbol

            # Determine security type
            if symbol.startswith("688"):
                security_type = "STAR"  # 科创板
                listing_board = "STAR"
            elif symbol.startswith("300"):
                security_type = "GEM"  # 创业板
                listing_board = "GEM"
            elif symbol.startswith("8") or symbol.startswith("4"):
                security_type = "BSE"  # 北交所
                listing_board = "BSE"
            else:
                security_type = "MAIN"  # 主板
                listing_board = "MAIN"

            stocks.append(
                {
                    "symbol": full_symbol,
                    "name": name,
                    "exchange": exchange,
                    "security_type": security_type,
                    "listing_board": listing_board,
                    "status": "ACTIVE",  # Assume active if in current list
                }
            )

        return stocks

    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        raise


def populate_stock_info(stocks: List[Dict], db_config: Dict):
    """
    将股票信息写入PostgreSQL数据库

    Args:
        stocks: 股票信息列表
        db_config: 数据库连接配置
    """
    logger.info(f"开始写入 {len(stocks)} 条股票信息到数据库...")

    conn = None
    cursor = None

    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Get current timestamp
        current_time = datetime.now().isoformat()

        # Insert stocks
        insert_sql = """
        INSERT INTO stock_info (
            symbol, name, exchange, security_type,
            listing_board, status, created_at, updated_at
        ) VALUES (
            %(symbol)s, %(name)s, %(exchange)s, %(security_type)s,
            %(listing_board)s, %(status)s, %(created_at)s, %(updated_at)s
        )
        ON CONFLICT (symbol) DO UPDATE SET
            name = EXCLUDED.name,
            exchange = EXCLUDED.exchange,
            security_type = EXCLUDED.security_type,
            listing_board = EXCLUDED.listing_board,
            status = EXCLUDED.status,
            updated_at = EXCLUDED.updated_at
        """

        # Prepare batch data
        batch_data = []
        for stock in stocks:
            batch_data.append(
                {**stock, "created_at": current_time, "updated_at": current_time}
            )

        # Execute batch insert
        cursor.executemany(insert_sql, batch_data)
        conn.commit()

        logger.info(f"✅ 成功写入 {len(stocks)} 条股票信息")

        # Verify
        cursor.execute("SELECT COUNT(*) FROM stock_info")
        count = cursor.fetchone()[0]
        logger.info(f"📊 stock_info表当前共有 {count} 条记录")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"写入数据库失败: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def main():
    """主函数"""

    # Database configuration (from environment variables)
    db_config = {
        "host": os.getenv("POSTGRESQL_HOST", "192.168.123.104"),
        "port": int(os.getenv("POSTGRESQL_PORT", "5438")),
        "user": os.getenv("POSTGRESQL_USER", "postgres"),
        "password": os.getenv("POSTGRESQL_PASSWORD", "c790414J"),
        "database": os.getenv("POSTGRESQL_DATABASE", "mystocks"),
    }

    logger.info("=" * 60)
    logger.info("股票基础信息填充脚本")
    logger.info("=" * 60)

    try:
        # Step 1: Get stock list from AkShare
        stocks = get_stock_list_from_akshare()

        # Step 2: Populate database
        populate_stock_info(stocks, db_config)

        logger.info("=" * 60)
        logger.info("✅ 数据填充完成!")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ 数据填充失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
