#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - PostgreSQL数据访问器

专门处理PostgreSQL数据库的历史数据和分析数据操作

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

import pandas as pd
import logging
from typing import Dict, List
import sqlalchemy as sa
from sqlalchemy import create_engine

from src.storage.access.modules.base import (
    IDataAccessLayer,
    normalize_dataframe,
)
from src.storage.database.database_manager import DatabaseTableManager, DatabaseType
from src.core import DataClassification, DataManager
from src.monitoring.monitoring_database import MonitoringDatabase

logger = logging.getLogger("MyStocksPostgreSQLAccess")


class PostgreSQLDataAccess(IDataAccessLayer):
    """PostgreSQL数据访问器 - 历史数据仓库和分析"""

    def __init__(self, monitoring_db: MonitoringDatabase):
        """
        初始化PostgreSQL数据访问器

        Args:
            monitoring_db: 监控数据库
        """
        self.db_manager = DatabaseTableManager()
        self.monitoring_db = monitoring_db
        self.db_type = DatabaseType.POSTGRESQL

    def save_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        **kwargs,
    ) -> bool:
        """
        保存数据到PostgreSQL

        Args:
            data: 数据DataFrame
            classification: 数据分类
            table_name: 表名（可选）
            **kwargs: 其他参数

        Returns:
            bool: 保存是否成功
        """
        # 记录操作开始
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            self.db_type.value,
            DataManager().get_database_name(classification),
            "INSERT",
        )

        try:
            database_name = DataManager().get_database_name(classification)

            # 数据预处理
            processed_data = self._preprocess_analytical_data(data, classification)

            # 获取SQLAlchemy引擎连接（用于pandas.to_sql）
            engine = self._get_postgresql_engine(database_name)

            # 使用pandas to_sql方法
            mode = kwargs.get("mode", "append")  # append, replace, ignore

            if mode == "replace":
                processed_data.to_sql(
                    actual_table_name,
                    engine,
                    if_exists="replace",
                    index=False,
                    method="multi",
                )
            elif mode == "ignore":
                # PostgreSQL的ignore逻辑需要特殊处理
                self._upsert_data_with_engine(
                    processed_data, actual_table_name, engine, classification
                )
            else:  # append
                processed_data.to_sql(
                    actual_table_name,
                    engine,
                    if_exists="append",
                    index=False,
                    method="multi",
                )

            self.monitoring_db.log_operation_result(
                operation_id, True, len(processed_data)
            )
            logger.info(
                f"PostgreSQL保存成功: {actual_table_name}, {len(processed_data)}条记录"
            )

            return True

        except Exception as e:
            error_msg = f"PostgreSQL保存失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
            logger.error(error_msg)
            return False

    def load_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        从PostgreSQL加载数据

        Args:
            classification: 数据分类
            table_name: 表名（可选）
            filters: 过滤条件
            **kwargs: 其他参数

        Returns:
            pd.DataFrame: 加载的数据
        """
        # 记录操作开始
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            self.db_type.value,
            DataManager().get_database_name(classification),
            "SELECT",
        )

        try:
            database_name = DataManager().get_database_name(classification)

            # 构建查询语句
            query = self._build_analytical_query(
                classification, actual_table_name, filters, **kwargs
            )

            # 执行查询
            engine = self._get_postgresql_engine(database_name)
            data = pd.read_sql(query, engine)

            # 后处理
            processed_data = self._postprocess_analytical_data(data, classification)

            self.monitoring_db.log_operation_result(
                operation_id, True, len(processed_data)
            )
            logger.info(
                f"PostgreSQL加载成功: {actual_table_name}, {len(processed_data)}条记录"
            )

            return processed_data

        except Exception as e:
            error_msg = f"PostgreSQL加载失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
            logger.error(error_msg)
            return pd.DataFrame()

    def update_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        key_columns: List[str] = None,
        **kwargs,
    ) -> bool:
        """更新PostgreSQL数据"""
        # 获取连接
        actual_table_name = table_name or self._get_default_table_name(classification)
        database_name = DataManager().get_database_name(classification)
        engine = self._get_postgresql_engine(database_name)

        try:
            # 构造更新条件
            if not key_columns:
                key_columns = ["symbol", "date"]

            where_clause = " AND ".join([f"{col} = %s" for col in key_columns])

            # 构造更新语句
            update_columns = [col for col in data.columns if col not in key_columns]
            set_clause = ", ".join([f"{col} = %s" for col in update_columns])

            # 获取更新值
            for _, row in data.iterrows():
                update_values = [row[col] for col in update_columns]
                key_values = [row[col] for col in key_columns]

                # 构造并执行SQL
                update_sql = f"""
                UPDATE {actual_table_name}
                SET {set_clause}
                WHERE {where_clause}
                """
                with engine.connect() as conn:
                    conn.execute(update_sql, list(update_values) + list(key_values))

            return True

        except Exception as e:
            logger.error(f"PostgreSQL更新失败: {e}")
            return False

    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """删除PostgreSQL数据（谨慎使用）"""
        # 获取连接
        actual_table_name = table_name or self._get_default_table_name(classification)
        database_name = DataManager().get_database_name(classification)
        engine = self._get_postgresql_engine(database_name)

        try:
            # 构建删除条件
            conditions = []
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        # 处理列表值
                        values_str = ",".join([f"'{v}'" for v in value])
                        conditions.append(f"{key} IN ({values_str})")
                    else:
                        conditions.append(f"{key} = '{value}'")

            # 如果没有条件，删除所有数据
            if not conditions:
                logger.error("PostgreSQL删除操作需要指定过滤条件")
                return False

            # 构建SQL
            where_clause = " AND ".join(conditions)
            delete_sql = f"DELETE FROM {actual_table_name} WHERE {where_clause}"

            with engine.connect() as conn:
                conn.execute(delete_sql)

            return True

        except Exception as e:
            logger.error(f"PostgreSQL删除失败: {e}")
            return False

    def _get_default_table_name(self, classification: DataClassification) -> str:
        """根据数据分类获取默认表名"""
        table_mapping = {
            DataClassification.DAILY_KLINE: "daily_kline",
            DataClassification.STOCK_BASIC: "stock_basic",
            DataClassification.FUNDAMENTAL_DATA: "fundamental_data",
            DataClassification.TECHNICAL_INDICATORS: "technical_indicators",
            DataClassification.REFERENCE_DATA: "reference_data",
            DataClassification.TRANSACTION_DATA: "transaction_data",
            DataClassification.META_DATA: "meta_data",
        }
        return table_mapping.get(classification, "unknown_table")

    def _get_postgresql_engine(self, database_name: str) -> sa.engine.Engine:
        """获取PostgreSQL引擎"""
        # 获取数据库连接信息
        conn_info = self.db_manager.get_connection_info(self.db_type, database_name)

        # 构造SQLAlchemy连接字符串
        connection_string = f"postgresql://{conn_info['username']}:{conn_info['password']}@{conn_info['host']}:{conn_info['port']}/{conn_info['database']}"

        # 创建引擎
        return create_engine(connection_string)

    def _preprocess_analytical_data(
        self, data: pd.DataFrame, classification: DataClassification
    ) -> pd.DataFrame:
        """预处理分析数据"""
        processed_data = normalize_dataframe(data)

        # 确保日期时间列是正确的数据类型
        for col in processed_data.columns:
            if "date" in col.lower() or "time" in col.lower():
                processed_data[col] = pd.to_datetime(
                    processed_data[col], errors="coerce"
                )

        return processed_data

    def _postprocess_analytical_data(
        self, data: pd.DataFrame, classification: DataClassification
    ) -> pd.DataFrame:
        """后处理分析数据"""
        if data.empty:
            return data

        # 确保日期时间列格式一致
        for col in data.columns:
            if "date" in col.lower() or "time" in col.lower():
                if pd.api.types.is_datetime64_any_dtype(data[col]):
                    data[col] = data[col].dt.tz_localize(None)  # 移除时区信息以便一致性

        return data

    def _build_analytical_query(
        self,
        classification: DataClassification,
        table_name: str,
        filters: Dict = None,
        **kwargs,
    ) -> str:
        """构建分析数据查询语句"""
        base_query = f"SELECT * FROM {table_name}"

        conditions = []

        # 添加过滤条件
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    values_str = ",".join([f"'{v}'" for v in value])
                    conditions.append(f"{key} IN ({values_str})")
                else:
                    conditions.append(f"{key} = '{value}'")

        # 添加kwargs中的条件
        for key, value in kwargs.items():
            if key == "limit":
                continue
            if isinstance(value, list):
                values_str = ",".join([f"'{v}'" for v in value])
                conditions.append(f"{key} IN ({values_str})")
            else:
                conditions.append(f"{key} = '{value}'")

        # 组装查询语句
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        # 添加排序
        if "order_by" in kwargs:
            base_query += f" ORDER BY {kwargs['order_by']}"
        else:
            # 默认按日期或时间排序（如果表中有这些字段）
            base_query += " ORDER BY date DESC, time DESC"

        # 添加限制
        if "limit" in kwargs:
            base_query += f" LIMIT {kwargs['limit']}"

        return base_query

    def _upsert_data_with_engine(
        self,
        data: pd.DataFrame,
        table_name: str,
        engine: sa.engine.Engine,
        classification: DataClassification,
    ) -> None:
        """PostgreSQL的 IGNORE 逻辑实现 - 使用 ON CONFLICT DO NOTHING"""
        # 获取主键或约束列
        primary_key_columns = self._get_primary_key_columns(classification)

        # 如果没有主键列，尝试查找其他唯一约束
        if not primary_key_columns:
            primary_key_columns = self._get_constraint_columns(classification)

        # 如果仍然没有，使用符号和时间列
        if not primary_key_columns:
            if "symbol" in data.columns:
                if "date" in data.columns:
                    primary_key_columns = ["symbol", "date"]
                elif "time" in data.columns:
                    primary_key_columns = ["symbol", "time"]
                else:
                    primary_key_columns = ["symbol"]
            elif "date" in data.columns:
                primary_key_columns = ["date"]
            else:
                # 退化为忽略重复行，直接导入
                data.to_sql(
                    table_name,
                    engine,
                    if_exists="append",
                    index=False,
                    method="multi",
                )
                return

        # 使用 ON CONFLICT DO NOTHING 进行导入
        try:
            # 构造 VALUES 子句
            value_placeholders = []
            for _, row in data.iterrows():
                values = []
                for col in data.columns:
                    val = row[col]
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    else:
                        values.append(f"'{val}'")
                value_placeholders.append("(" + ", ".join(values) + ")")

            # 构造完整的 INSERT 语句
            columns_str = ", ".join(data.columns)
            values_str = ", ".join(value_placeholders)
            conflict_columns_str = ", ".join(primary_key_columns)

            sql = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES {values_str}
            ON CONFLICT ({conflict_columns_str}) DO NOTHING
            """

            with engine.connect() as conn:
                conn.execute(sql)

        except Exception as e:
            logger.error(f"PostgreSQL使用ON CONFLICT导入数据失败: {e}")
            # 回退到直接导入
            data.to_sql(
                table_name,
                engine,
                if_exists="append",
                index=False,
                method="multi",
            )

    def _get_primary_key_columns(self, classification: DataClassification) -> List[str]:
        """根据数据分类获取主键列"""
        pk_mapping = {
            DataClassification.DAILY_KLINE: ["symbol", "date"],
            DataClassification.STOCK_BASIC: ["symbol"],
            DataClassification.FUNDAMENTAL_DATA: ["symbol", "date"],
            DataClassification.TECHNICAL_INDICATORS: [
                "symbol",
                "date",
                "indicator_name",
            ],
            DataClassification.REFERENCE_DATA: ["key"],
            DataClassification.TRANSACTION_DATA: ["transaction_id"],
            DataClassification.META_DATA: ["key"],
        }
        return pk_mapping.get(classification, [])

    def _get_constraint_columns(self, classification: DataClassification) -> List[str]:
        """根据数据分类获取约束列"""
        constraint_mapping = {
            DataClassification.DAILY_KLINE: ["symbol", "date"],
            DataClassification.STOCK_BASIC: ["symbol"],
            DataClassification.FUNDAMENTAL_DATA: ["symbol", "date"],
            DataClassification.TECHNICAL_INDICATORS: [
                "symbol",
                "date",
                "indicator_name",
            ],
            DataClassification.REFERENCE_DATA: ["key"],
            DataClassification.TRANSACTION_DATA: ["transaction_id"],
            DataClassification.META_DATA: ["key"],
        }
        return constraint_mapping.get(classification, [])
