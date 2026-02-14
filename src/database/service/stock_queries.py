"""数据库服务子模块"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd

from src.data_access import PostgreSQLDataAccess

logger = logging.getLogger(__name__)

postgresql_access = PostgreSQLDataAccess()


class StockQueriesMixin:
    """股票基础数据查询"""

    def __init__(self):
        """初始化数据库服务"""
        self.postgresql_access = postgresql_access

    # ==================== 股票相关查询 ====================

    def get_stock_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取股票列表（支持按交易所筛选，支持分页）

        Args:
            params: Dict - 查询参数：
                    exchange: Optional[str] - 交易所筛选（sh=上交所，sz=深交所）
                    limit: int - 每页数量，默认20
                    offset: int - 偏移量，默认0

        Returns:
            List[Dict]: 股票列表数据，与Mock数据格式一致
        """
        try:
            # 默认参数
            params = params or {}
            exchange = params.get("exchange")
            limit = params.get("limit", 20)
            offset = params.get("offset", 0)

            # 构建查询条件
            filters = {}
            if exchange:
                # 根据交易所筛选（需要与数据库中的字段对应）
                if exchange == "sh":
                    filters["market"] = "上交所"
                elif exchange == "sz":
                    filters["market"] = "深交所"

            # 查询股票基本信息表
            where_clause = None
            if filters:
                # 构建WHERE子句
                where_conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        # 处理列表值（IN查询）
                        values_str = "', '".join(value)
                        where_conditions.append(f"{key} IN ('{values_str}')")
                    else:
                        # 处理单个值
                        where_conditions.append(f"{key} = '{value}'")
                where_clause = " AND ".join(where_conditions)

            df = self.postgresql_access.query(
                table_name="symbols_info",
                where=where_clause,
                limit=limit,  # 不使用offset参数，手动处理
            )

            # 手动处理offset
            if offset and offset > 0:
                df = df.iloc[offset:]

            # 获取总数量
            # 为了获取总数量，我们需要查询所有记录而不使用limit和offset
            total_df = self.postgresql_access.query(
                table_name="symbols_info",
                where=where_clause,
                columns=["COUNT(*) as total"],
            )
            total_count = total_df.iloc[0]["total"] if not total_df.empty else 0

            # 转换为与Mock数据一致的格式
            result = []
            if not df.empty:
                for _, row in df.iterrows():
                    result.append(
                        {
                            "symbol": row.get("symbol", ""),
                            "name": row.get("name", ""),
                            "industry": row.get("industry", ""),
                            "area": row.get("area", ""),
                            "market": row.get("market", ""),
                            "list_date": (
                                row.get("list_date", "").strftime("%Y-%m-%d") if pd.notna(row.get("list_date")) else ""
                            ),
                            "total": total_count,  # 用于分页的总数量
                        }
                    )

            return result

        except Exception as e:
            logger.error("获取股票列表失败: %s", e)
            return []

    def get_stock_detail(self, stock_code: str) -> Dict:
        """获取股票详细信息

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 股票详细信息，与Mock数据格式一致
        """
        try:
            if not stock_code:
                return {}

            # 查询股票基本信息表
            where_clause = f"symbol = '{stock_code}'"

            df = self.postgresql_access.query(table_name="symbols_info", where=where_clause, limit=1)

            # 转换为与Mock数据一致的格式
            if not df.empty:
                row = df.iloc[0]
                return {
                    "symbol": row.get("symbol", ""),
                    "name": row.get("name", ""),
                    "industry": row.get("industry", ""),
                    "area": row.get("area", ""),
                    "market": row.get("market", ""),
                    "list_date": (
                        row.get("list_date", "").strftime("%Y-%m-%d") if pd.notna(row.get("list_date")) else ""
                    ),
                }

            return {}

        except Exception as e:
            logger.error("获取股票详细信息失败: %s", e)
            return {}

    def get_realtime_quotes(self, symbols: List[str]) -> List[Dict]:
        """获取实时行情

        Args:
            symbols: List[str] - 股票代码列表

        Returns:
            List[Dict]: 实时行情数据列表，与Mock数据格式一致
        """
        try:
            if not symbols:
                return []

            # 查询实时行情表
            where_clause = None
            if symbols:
                # 构建WHERE子句
                where_conditions = []
                for key, value in {"symbol": symbols}.items():
                    if isinstance(value, list):
                        # 处理列表值（IN查询）
                        values_str = "', '".join(value)
                        where_conditions.append(f"{key} IN ('{values_str}')")
                    else:
                        # 处理单个值
                        where_conditions.append(f"{key} = '{value}'")
                where_clause = " AND ".join(where_conditions)

            df = self.postgresql_access.query(table_name="realtime_quotes", where=where_clause)

            # 转换为与Mock数据一致的格式
            result = []
            if not df.empty:
                for _, row in df.iterrows():
                    result.append(
                        {
                            "symbol": row.get("symbol", ""),
                            "name": row.get("name", ""),
                            "price": float(row.get("price", 0.0)),
                            "change": float(row.get("change", 0.0)),
                            "change_percent": float(row.get("change_percent", 0.0)),
                            "volume": int(row.get("volume", 0)),
                            "amount": float(row.get("amount", 0.0)),
                            "open": float(row.get("open", 0.0)),
                            "high": float(row.get("high", 0.0)),
                            "low": float(row.get("low", 0.0)),
                            "pre_close": float(row.get("pre_close", 0.0)),
                            "timestamp": (
                                row.get("timestamp", "").strftime("%Y-%m-%d %H:%M:%S")
                                if pd.notna(row.get("timestamp"))
                                else ""
                            ),
                        }
                    )

            return result

        except Exception as e:
            logger.error("获取实时行情失败: %s", e)
            return []

    # ==================== 问财相关查询 ====================

