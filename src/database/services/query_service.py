"""
数据库查询服务

提供标准化的数据库查询接口，支持参数化查询和结果缓存
"""

import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
from functools import lru_cache

from .connection_service import ConnectionService


logger = logging.getLogger(__name__)


class QueryService:
    def __init__(self, connection_service: ConnectionService):
        self.connection_service = connection_service
        self.query_cache = {}
        self.cache_ttl = 300

        logger.info("QueryService initialized")

    def execute_query(
        self,
        table_name: str,
        where_clause: Optional[str] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        params: Optional[Dict] = None,
    ) -> List[Dict]:
        try:
            with self.connection_service.get_connection() as conn:
                cursor = conn.cursor()

                query = f"SELECT {self._build_select_clause(columns)} FROM {table_name}"

                if where_clause:
                    query += f" WHERE {where_clause}"

                if order_by:
                    query += f" ORDER BY {order_by}"

                if limit:
                    query += f" LIMIT {limit}"

                if offset:
                    query += f" OFFSET {offset}"

                if params:
                    query = self._apply_params(query, params)

                cursor.execute(query)

                columns_desc = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()

                result = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        column_name = columns_desc[i][0]
                        row_dict[column_name] = value
                    result.append(row_dict)

                logger.debug(f"查询执行成功: {len(result)} 行")
                return result

        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise

    @lru_cache(maxsize=100)
    def cached_query(
        self,
        table_name: str,
        where_clause: Optional[str] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        cache_key: Optional[str] = None,
    ) -> List[Dict]:
        if not cache_key:
            cache_key = f"{table_name}_{where_clause}_{columns}_{limit}_{offset}"

        if cache_key in self.query_cache:
            cached_time, cached_result = self.query_cache[cache_key]
            age = (datetime.now() - cached_time).total_seconds()

            if age < self.cache_ttl:
                logger.debug(f"返回缓存结果: {cache_key}")
                return cached_result

        result = self.execute_query(
            table_name=table_name, where_clause=where_clause, columns=columns, limit=limit, offset=offset
        )

        self.query_cache[cache_key] = (datetime.now(), result)
        return result

    def build_where_clause(self, filters: Dict[str, Union[str, List[str]]]) -> str:
        if not filters:
            return ""

        conditions = []

        for key, value in filters.items():
            if isinstance(value, list):
                values_str = "', '".join([f"'{v}'" for v in value])
                conditions.append(f"{key} IN ({values_str})")
            else:
                conditions.append(f"{key} = '{value}'")

        return " AND ".join(conditions)

    def _build_select_clause(self, columns: Optional[List[str]]) -> str:
        if not columns:
            return "*"
        return ", ".join(columns)

    def _apply_params(self, query: str, params: Optional[Dict]) -> str:
        if not params:
            return query

        try:
            for key, value in params.items():
                if f"%{key}%" in query:
                    query = query.replace(f"%{key}%", f"'{value}'")
                elif f":{key}:" in query:
                    query = query.replace(f":{key}:", f"'{value}'")
                else:
                    query = query.replace(f"${key}", f"'{value}'")

            return query
        except Exception as e:
            logger.warning(f"参数应用失败: {e}, 返回原查询")
            return query

    def get_stock_by_code(self, stock_code: str, columns: Optional[List[str]] = None) -> Optional[Dict]:
        result = self.execute_query(
            table_name="symbols_info", where_clause=f"symbol = '{stock_code}'", columns=columns, limit=1
        )

        return result[0] if result else None

    def batch_get_stocks(
        self, stock_codes: List[str], columns: Optional[List[str]] = None, chunk_size: int = 100
    ) -> List[Dict]:
        all_stocks = []

        for i in range(0, len(stock_codes), chunk_size):
            chunk = stock_codes[i : i + chunk_size]

            where_clause = ""
            if len(chunk) > 1:
                values_str = "', '".join(chunk)
                where_clause = f"symbol IN ({values_str})"
            else:
                where_clause = f"symbol = '{chunk[0]}'"

            results = self.execute_query(table_name="symbols_info", where_clause=where_clause, columns=columns)

            all_stocks.extend(results)

        logger.info(f"批量获取股票信息: {len(all_stocks)} 条记录")
        return all_stocks

    def count_records(self, table_name: str, where_clause: Optional[str] = None) -> int:
        try:
            with self.connection_service.get_connection() as conn:
                cursor = conn.cursor()

                query = f"SELECT COUNT(*) as count FROM {table_name}"
                if where_clause:
                    query += f" WHERE {where_clause}"

                cursor.execute(query)
                result = cursor.fetchone()
                count = result[0] if result else 0

                logger.debug(f"记录数: {count}")
                return count

        except Exception as e:
            logger.error(f"记录数查询失败: {e}")
            return 0

    def clear_cache(self):
        self.query_cache.clear()
        logger.info("查询缓存已清除")
