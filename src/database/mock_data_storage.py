"""
Mock数据存储层
模拟真实数据库的存储逻辑，用于测试数据落地功能
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List


class MockDataStorage:
    """
    Mock数据存储层
    模拟真实数据库的存储逻辑，用于测试数据落地功能
    """

    def __init__(self, storage_path: str = "./mock_data_storage"):
        """
        初始化Mock数据存储

        Args:
            storage_path: 存储路径
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        self._init_storage()

    def _init_storage(self):
        """初始化存储结构"""
        # 创建SQLite数据库来模拟数据落地
        self.db_path = os.path.join(self.storage_path, "mock_data.db")
        self.conn = sqlite3.connect(self.db_path)

        # 创建表结构以模拟真实数据库
        self._create_tables()

    def _create_tables(self):
        """创建模拟表"""
        cursor = self.conn.cursor()

        # 模拟技术指标表
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS technical_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            calc_date TIMESTAMP NOT NULL,
            indicator_name TEXT NOT NULL,
            indicator_value REAL,
            indicator_params TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # 模拟实时行情表
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS realtime_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            trade_time TIMESTAMP NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume BIGINT,
            amount REAL,
            pre_close REAL,
            change REAL,
            change_pct REAL,
            turnover_rate REAL,
            pe_ratio REAL,
            pb_ratio REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # 模拟股票信息表
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS stock_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            name TEXT,
            exchange TEXT,
            security_type TEXT,
            list_date DATE,
            delist_date DATE,
            status TEXT,
            listing_board TEXT,
            market_cap REAL,
            circulating_market_cap REAL,
            total_shares BIGINT,
            circulating_shares BIGINT,
            created_at TEXT,
            updated_at TEXT
        )
        """
        )

        self.conn.commit()

    def insert_technical_indicators(self, data: List[Dict]) -> bool:
        """
        插入技术指标数据

        Args:
            data: 技术指标数据列表

        Returns:
            bool: 操作是否成功
        """
        try:
            cursor = self.conn.cursor()

            for item in data:
                # 确保indicator_params是字符串
                indicator_params = item.get("indicator_params", {})
                if isinstance(indicator_params, dict):
                    indicator_params_str = json.dumps(indicator_params)
                else:
                    indicator_params_str = str(indicator_params)

                cursor.execute(
                    """
                INSERT INTO technical_indicators
                (symbol, calc_date, indicator_name, indicator_value, indicator_params)
                VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        item.get("symbol"),
                        item.get("calc_date", datetime.now()),
                        item.get("indicator_name"),
                        item.get("indicator_value"),
                        indicator_params_str,
                    ),
                )

            self.conn.commit()
            return True
        except Exception as e:
            print(f"插入技术指标数据失败: {e}")
            return False

    def insert_realtime_quotes(self, data: List[Dict]) -> bool:
        """
        插入实时行情数据

        Args:
            data: 实时行情数据列表

        Returns:
            bool: 操作是否成功
        """
        try:
            cursor = self.conn.cursor()

            for item in data:
                cursor.execute(
                    """
                INSERT INTO realtime_quotes
                (symbol, trade_time, open, high, low, close, volume, amount, pre_close,
                 change, change_pct, turnover_rate, pe_ratio, pb_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        item.get("symbol"),
                        item.get("trade_time", datetime.now()),
                        item.get("open"),
                        item.get("high"),
                        item.get("low"),
                        item.get("close"),
                        item.get("volume"),
                        item.get("amount"),
                        item.get("pre_close"),
                        item.get("change"),
                        item.get("change_pct"),
                        item.get("turnover_rate"),
                        item.get("pe_ratio"),
                        item.get("pb_ratio"),
                    ),
                )

            self.conn.commit()
            return True
        except Exception as e:
            print(f"插入实时行情数据失败: {e}")
            return False

    def insert_stock_info(self, data: List[Dict]) -> bool:
        """
        插入股票信息数据

        Args:
            data: 股票信息数据列表

        Returns:
            bool: 操作是否成功
        """
        try:
            cursor = self.conn.cursor()

            for item in data:
                cursor.execute(
                    """
                INSERT OR REPLACE INTO stock_info
                (symbol, name, exchange, security_type, list_date, delist_date, status,
                 listing_board, market_cap, circulating_market_cap, total_shares,
                 circulating_shares, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        item.get("symbol"),
                        item.get("name"),
                        item.get("exchange"),
                        item.get("security_type"),
                        item.get("list_date"),
                        item.get("delist_date"),
                        item.get("status"),
                        item.get("listing_board"),
                        item.get("market_cap"),
                        item.get("circulating_market_cap"),
                        item.get("total_shares"),
                        item.get("circulating_shares"),
                        item.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        item.get("updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    ),
                )

            self.conn.commit()
            return True
        except Exception as e:
            print(f"插入股票信息数据失败: {e}")
            return False

    def query_technical_indicators(
        self, symbol: str = None, start_date: str = None, end_date: str = None
    ) -> List[Dict]:
        """
        查询技术指标数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict]: 查询结果
        """
        try:
            cursor = self.conn.cursor()

            where_conditions = []
            params = []

            if symbol:
                where_conditions.append("symbol = ?")
                params.append(symbol)
            if start_date:
                where_conditions.append("calc_date >= ?")
                params.append(start_date)
            if end_date:
                where_conditions.append("calc_date <= ?")
                params.append(end_date)

            where_clause = " AND ".join(where_conditions)
            if where_clause:
                where_clause = f"WHERE {where_clause}"

            query = f"""
            SELECT symbol, calc_date, indicator_name, indicator_value, indicator_params
            FROM technical_indicators
            {where_clause}
            ORDER BY calc_date DESC
            """

            cursor.execute(query, params)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    {
                        "symbol": row[0],
                        "calc_date": row[1],
                        "indicator_name": row[2],
                        "indicator_value": row[3],
                        "indicator_params": json.loads(row[4]) if row[4] else {},
                    }
                )

            return result
        except Exception as e:
            print(f"查询技术指标数据失败: {e}")
            return []

    def query_realtime_quotes(self, symbol: str = None) -> List[Dict]:
        """
        查询实时行情数据

        Args:
            symbol: 股票代码

        Returns:
            List[Dict]: 查询结果
        """
        try:
            cursor = self.conn.cursor()

            where_clause = ""
            params = []

            if symbol:
                where_clause = "WHERE symbol = ?"
                params.append(symbol)

            query = f"""
            SELECT symbol, trade_time, open, high, low, close, volume, amount,
                   pre_close, change, change_pct, turnover_rate, pe_ratio, pb_ratio
            FROM realtime_quotes
            {where_clause}
            ORDER BY trade_time DESC
            LIMIT 100
            """

            cursor.execute(query, params)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    {
                        "symbol": row[0],
                        "trade_time": row[1],
                        "open": row[2],
                        "high": row[3],
                        "low": row[4],
                        "close": row[5],
                        "volume": row[6],
                        "amount": row[7],
                        "pre_close": row[8],
                        "change": row[9],
                        "change_pct": row[10],
                        "turnover_rate": row[11],
                        "pe_ratio": row[12],
                        "pb_ratio": row[13],
                    }
                )

            return result
        except Exception as e:
            print(f"查询实时行情数据失败: {e}")
            return []

    def query_stock_info(self, symbol: str = None) -> List[Dict]:
        """
        查询股票信息数据

        Args:
            symbol: 股票代码

        Returns:
            List[Dict]: 查询结果
        """
        try:
            cursor = self.conn.cursor()

            where_clause = ""
            params = []

            if symbol:
                where_clause = "WHERE symbol = ?"
                params.append(symbol)

            query = f"""
            SELECT symbol, name, exchange, security_type, list_date, delist_date, status,
                   listing_board, market_cap, circulating_market_cap, total_shares,
                   circulating_shares, created_at, updated_at
            FROM stock_info
            {where_clause}
            LIMIT 100
            """

            cursor.execute(query, params)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    {
                        "symbol": row[0],
                        "name": row[1],
                        "exchange": row[2],
                        "security_type": row[3],
                        "list_date": row[4],
                        "delist_date": row[5],
                        "status": row[6],
                        "listing_board": row[7],
                        "market_cap": row[8],
                        "circulating_market_cap": row[9],
                        "total_shares": row[10],
                        "circulating_shares": row[11],
                        "created_at": row[12],
                        "updated_at": row[13],
                    }
                )

            return result
        except Exception as e:
            print(f"查询股票信息数据失败: {e}")
            return []

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


# 全局Mock数据存储实例
mock_data_storage = MockDataStorage()
