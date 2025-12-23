#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - MySQL数据访问器

专门处理MySQL数据库的元数据和参考数据操作

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

import pandas as pd
import logging
import uuid
from typing import Dict, List

from src.storage.access.modules.base import (
    IDataAccessLayer,
    normalize_dataframe,
)
from src.storage.database.database_manager import DatabaseTableManager, DatabaseType
from src.core import DataClassification, DataManager
from src.monitoring.monitoring_database import MonitoringDatabase

logger = logging.getLogger("MyStocksMySQLAccess")


class MySQLDataAccess(IDataAccessLayer):
    """MySQL数据访问器 - 元数据与参考数据仓库"""

    def __init__(self, monitoring_db: MonitoringDatabase):
        """
        初始化MySQL数据访问器

        Args:
            monitoring_db: 监控数据库
        """
        self.db_manager = DatabaseTableManager()
        self.monitoring_db = monitoring_db
        self.db_type = DatabaseType.MYSQL

    def save_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        **kwargs,
    ) -> bool:
        """保存数据到MySQL，支持UPSERT操作"""
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            self.db_type.value,
            DataManager().get_database_name(classification),
            "upsert_data",
        )

        try:
            database_name = DataManager().get_database_name(classification)
            processed_data = self._preprocess_reference_data(data, classification)

            # 获取MySQL连接
            conn = self.db_manager.get_connection(self.db_type, database_name)

            mode = kwargs.get("mode", "upsert")
            if mode == "replace":
                processed_data.to_sql(
                    actual_table_name,
                    conn,
                    if_exists="replace",
                    index=False,
                    method="multi",
                )
            elif mode == "upsert":
                # 使用MySQL UPSERT实现
                affected_rows = self._mysql_upsert_data(
                    processed_data, actual_table_name, conn, classification
                )
                self.monitoring_db.log_operation_result(
                    operation_id, True, affected_rows
                )
                logger.info(
                    f"MySQL保存成功: {actual_table_name}, {affected_rows}条记录"
                )
                return True
            else:  # default append
                processed_data.to_sql(
                    actual_table_name,
                    conn,
                    if_exists="append",
                    index=False,
                    method="multi",
                )

            self.monitoring_db.log_operation_result(
                operation_id, True, len(processed_data)
            )
            logger.info(
                f"MySQL保存成功: {actual_table_name}, {len(processed_data)}条记录"
            )

            return True

        except Exception as e:
            error_msg = f"MySQL保存失败: {e}"
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
        """从MySQL加载数据"""
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            self.db_type.value,
            DataManager().get_database_name(classification),
            "SELECT",
        )

        try:
            database_name = DataManager().get_database_name(classification)
            conn = self.db_manager.get_connection(self.db_type, database_name)

            # 构建查询语句
            query = self._build_reference_query(
                classification, actual_table_name, filters, **kwargs
            )

            # 执行查询
            data = pd.read_sql(query, conn)

            # 后处理
            processed_data = self._postprocess_reference_data(data, classification)

            self.monitoring_db.log_operation_result(
                operation_id, True, len(processed_data)
            )
            logger.info(
                f"MySQL加载成功: {actual_table_name}, {len(processed_data)}条记录"
            )

            return processed_data

        except Exception as e:
            error_msg = f"MySQL加载失败: {e}"
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
        """更新MySQL数据"""
        # 获取连接
        actual_table_name = table_name or self._get_default_table_name(classification)
        database_name = DataManager().get_database_name(classification)
        conn = self.db_manager.get_connection(self.db_type, database_name)

        try:
            # 构造更新条件
            if not key_columns:
                key_columns = ["key"]

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
                with conn.cursor() as cursor:
                    cursor.execute(update_sql, list(update_values) + list(key_values))

            return True

        except Exception as e:
            logger.error(f"MySQL更新失败: {e}")
            return False

    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """删除MySQL数据（谨慎使用）"""
        # 获取连接
        actual_table_name = table_name or self._get_default_table_name(classification)
        database_name = DataManager().get_database_name(classification)
        conn = self.db_manager.get_connection(self.db_type, database_name)

        try:
            # 构建删除条件
            conditions = []
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        # 处理列表值
                        placeholders = ", ".join(["%s"] * len(value))
                        conditions.append(f"{key} IN ({placeholders})")
                    else:
                        conditions.append(f"{key} = %s")

            # 如果没有条件，删除所有数据
            if not conditions:
                logger.error("MySQL删除操作需要指定过滤条件")
                return False

            # 构建SQL
            where_clause = " AND ".join(conditions)
            delete_sql = f"DELETE FROM {actual_table_name} WHERE {where_clause}"

            with conn.cursor() as cursor:
                cursor.execute(delete_sql)

            return True

        except Exception as e:
            logger.error(f"MySQL删除失败: {e}")
            return False

    def _get_default_table_name(self, classification: DataClassification) -> str:
        """根据数据分类获取默认表名"""
        table_mapping = {
            DataClassification.STOCK_BASIC: "stock_basic",
            DataClassification.REFERENCE_DATA: "reference_data",
            DataClassification.META_DATA: "meta_data",
        }
        return table_mapping.get(classification, "unknown_table")

    def _preprocess_reference_data(
        self, data: pd.DataFrame, classification: DataClassification
    ) -> pd.DataFrame:
        """预处理参考数据"""
        processed_data = normalize_dataframe(data)

        # 确保关键列存在
        if classification == DataClassification.REFERENCE_DATA:
            if "key" not in processed_data.columns:
                processed_data["key"] = f"key_{uuid.uuid4()}"
        elif classification == DataClassification.META_DATA:
            if "key" not in processed_data.columns:
                processed_data["key"] = f"key_{uuid.uuid4()}"

        return processed_data

    def _postprocess_reference_data(
        self, data: pd.DataFrame, classification: DataClassification
    ) -> pd.DataFrame:
        """后处理参考数据"""
        if data.empty:
            return data

        return data

    def _build_reference_query(
        self,
        classification: DataClassification,
        table_name: str,
        filters: Dict = None,
        **kwargs,
    ) -> str:
        """构建参考数据查询语句"""
        base_query = f"SELECT * FROM {table_name}"

        conditions = []

        # 添加过滤条件
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    placeholders = ", ".join(["%s"] * len(value))
                    conditions.append(f"{key} IN ({placeholders})")
                else:
                    conditions.append(f"{key} = %s")

        # 添加kwargs中的条件
        for key, value in kwargs.items():
            if key == "limit":
                continue
            if isinstance(value, list):
                placeholders = ", ".join(["%s"] * len(value))
                conditions.append(f"{key} IN ({placeholders})")
            else:
                conditions.append(f"{key} = %s")

        # 组装查询语句
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        # 添加排序
        if "order_by" in kwargs:
            base_query += f" ORDER BY {kwargs['order_by']}"

        # 添加限制
        if "limit" in kwargs:
            base_query += f" LIMIT {kwargs['limit']}"

        return base_query

    def _mysql_upsert_data(
        self,
        data: pd.DataFrame,
        table_name: str,
        conn,
        classification: DataClassification,
    ) -> int:
        """MySQL UPSERT操作 - 插入或更新数据"""
        # 获取主键列
        primary_key_columns = self._get_primary_key_columns(classification)

        # 如果没有主键列，尝试查找其他唯一约束
        if not primary_key_columns:
            primary_key_columns = self._get_constraint_columns(classification)

        # 如果仍然没有，使用符号列
        if not primary_key_columns:
            primary_key_columns = ["symbol"] if "symbol" in data.columns else ["id"]

        # 开始事务
        affected_rows = 0

        try:
            # 准备数据
            data_list = data.to_dict("records")

            # 构造SQL语句
            columns = list(data.columns)
            placeholders = ", ".join(["%s"] * len(columns))
            set_columns = [col for col in columns if col not in primary_key_columns]
            set_clause = ", ".join([f"{col} = VALUES({col})" for col in set_columns])
            primary_key_clause = ", ".join(primary_key_columns)

            # 构造并执行INSERT ... ON DUPLICATE KEY UPDATE语句
            sql = f"""
            INSERT INTO {table_name} ({", ".join(columns)})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {set_clause}
            """

            with conn.cursor() as cursor:
                affected_rows = cursor.executemany(sql, data_list)

            conn.commit()

            return affected_rows

        except Exception as e:
            conn.rollback()
            logger.error(f"MySQL UPSERT操作失败: {e}")
            raise

    def _get_primary_key_columns(self, classification: DataClassification) -> List[str]:
        """根据数据分类获取主键列"""
        pk_mapping = {
            DataClassification.STOCK_BASIC: ["symbol"],
            DataClassification.REFERENCE_DATA: ["key"],
            DataClassification.META_DATA: ["key"],
        }
        return pk_mapping.get(classification, [])

    def _get_constraint_columns(self, classification: DataClassification) -> List[str]:
        """根据数据分类获取约束列"""
        constraint_mapping = {
            DataClassification.STOCK_BASIC: ["symbol"],
            DataClassification.REFERENCE_DATA: ["key"],
            DataClassification.META_DATA: ["key"],
        }
        return constraint_mapping.get(classification, [])
