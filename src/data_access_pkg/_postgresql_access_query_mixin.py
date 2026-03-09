"""Shared query/update helpers for `postgresql_access.py`."""

from __future__ import annotations

import logging
from typing import Dict, List

import pandas as pd

from src.core import DataClassification

logger = logging.getLogger(__name__)

ALLOWED_TABLES = {
    "daily_kline",
    "minute_kline",
    "tick_data",
    "symbols_info",
    "technical_indicators",
    "quantitative_factors",
    "model_outputs",
    "trading_signals",
    "order_records",
    "transaction_records",
    "position_records",
    "account_funds",
    "realtime_quotes",
}


class PostgreSQLDataAccessQueryMixin:
    """抽离 PostgreSQL 查询/更新辅助逻辑。"""

    def _execute_update(self, cursor, data: pd.DataFrame, table_name: str, key_columns: List[str]) -> bool:
        """执行更新操作"""
        try:
            for _, row in data.iterrows():
                set_clauses = []
                set_values = []
                for col in data.columns:
                    if col not in key_columns:
                        set_clauses.append(f"{col} = %s")
                        set_values.append(row[col])

                where_clauses = []
                where_values = []
                for col in key_columns:
                    where_clauses.append(f"{col} = %s")
                    where_values.append(row[col])

                update_sql = f"""
                    UPDATE {table_name}
                    SET {", ".join(set_clauses)}
                    WHERE {" AND ".join(where_clauses)}
                """
                cursor.execute(update_sql, set_values + where_values)

            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("执行更新操作失败: %s", e)
            return False

    def _build_analytical_query(
        self,
        classification: DataClassification,
        table_name: str,
        filters: Dict = None,
        **kwargs,
    ) -> tuple:
        """
        构建分析数据查询语句 - 使用参数化查询防止SQL注入

        返回值: (sql_string, bind_parameters)
        """
        if table_name not in ALLOWED_TABLES:
            raise ValueError(f"Invalid table name: {table_name}")

        base_query = f"SELECT * FROM {table_name}"
        conditions = []
        params = []

        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    placeholders = ", ".join(["%s"] * len(value))
                    conditions.append(f"{key} IN ({placeholders})")
                    params.extend(value)
                else:
                    conditions.append(f"{key} = %s")
                    params.append(value)

        for key, value in kwargs.items():
            if key in ["limit", "offset", "order_by"]:
                continue
            conditions.append(f"{key} = %s")
            params.append(value)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query = self._apply_order_by_clause(base_query, classification, kwargs.get("order_by"))
        base_query, params = self._apply_limit_offset(base_query, params, kwargs)
        return base_query, tuple(params)

    def _build_delete_query(self, table_name: str, filters: Dict) -> tuple:
        """
        构建删除查询语句 - 使用参数化查询防止SQL注入

        返回值: (sql_string, bind_parameters)
        """
        if table_name not in ALLOWED_TABLES:
            raise ValueError(f"Invalid table name: {table_name}")

        base_query = f"DELETE FROM {table_name}"
        conditions = []
        params = []

        for key, value in filters.items():
            conditions.append(f"{key} = %s")
            params.append(value)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        return base_query, tuple(params)

    def _apply_order_by_clause(
        self,
        base_query: str,
        classification: DataClassification,
        order_by,
    ) -> str:
        """追加安全的 ORDER BY 子句。"""
        if not order_by:
            return base_query + self._default_order_by_clause(classification)

        allowed_columns = self._get_allowed_order_by_columns(classification)
        if not isinstance(order_by, str):
            return base_query + self._default_order_by_clause(classification)

        order_columns = []
        for column_spec in order_by.split(","):
            column_spec = column_spec.strip()
            parts = column_spec.split()

            if len(parts) == 1:
                column_name = parts[0]
                direction = ""
            elif len(parts) == 2:
                column_name, direction = parts
                if direction.upper() not in ["ASC", "DESC"]:
                    direction = "ASC"
            else:
                continue

            if column_name in allowed_columns:
                order_columns.append(f"{column_name} {direction}".strip())

        if not order_columns:
            return base_query + self._default_order_by_clause(classification)

        validated_order_by = ", ".join(order_columns)
        return f"{base_query} ORDER BY {validated_order_by}"

    def _apply_limit_offset(self, base_query: str, params: List, kwargs: Dict) -> tuple[str, List]:
        """追加 LIMIT / OFFSET 子句。"""
        if "limit" in kwargs:
            limit_val = kwargs["limit"]
            if isinstance(limit_val, int):
                base_query += f" LIMIT {limit_val}"
            else:
                base_query += " LIMIT %s"
                params.append(limit_val)

        if "offset" in kwargs:
            offset_val = kwargs["offset"]
            if isinstance(offset_val, int):
                base_query += f" OFFSET {offset_val}"
            else:
                base_query += " OFFSET %s"
                params.append(offset_val)

        return base_query, params

    def _default_order_by_clause(self, classification: DataClassification) -> str:
        """获取默认排序子句。"""
        if classification == DataClassification.DAILY_KLINE:
            return " ORDER BY trade_date DESC"
        if classification in [
            DataClassification.TECHNICAL_INDICATORS,
            DataClassification.QUANTITATIVE_FACTORS,
        ]:
            return " ORDER BY calc_date DESC"
        return " ORDER BY created_at DESC"

    def _get_allowed_order_by_columns(self, classification: DataClassification) -> List[str]:
        """根据数据分类返回可排序列白名单。"""
        order_by_columns = {
            DataClassification.DAILY_KLINE: [
                "trade_date",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "amount",
                "adjust_flag",
                "created_at",
                "updated_at",
            ],
            DataClassification.MINUTE_KLINE: [
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "amount",
                "created_at",
            ],
            DataClassification.TICK_DATA: [
                "datetime",
                "price",
                "volume",
                "amount",
                "direction",
            ],
            DataClassification.TECHNICAL_INDICATORS: [
                "calc_date",
                "symbol",
                "indicator_name",
                "indicator_value",
                "created_at",
                "updated_at",
            ],
            DataClassification.QUANTITATIVE_FACTORS: [
                "calc_date",
                "symbol",
                "factor_name",
                "factor_value",
                "created_at",
                "updated_at",
            ],
        }

        symbols_info = getattr(DataClassification, "STOCK_INFO", getattr(DataClassification, "SYMBOLS_INFO", None))
        if symbols_info is not None:
            order_by_columns[symbols_info] = [
                "symbol",
                "name",
                "market",
                "industry",
                "list_date",
                "created_at",
                "updated_at",
            ]

        financial_reports = getattr(DataClassification, "FINANCIAL_REPORTS", None)
        if financial_reports is not None:
            order_by_columns[financial_reports] = [
                "report_date",
                "symbol",
                "report_type",
                "revenue",
                "net_profit",
                "created_at",
                "updated_at",
            ]

        return order_by_columns.get(classification, [])
