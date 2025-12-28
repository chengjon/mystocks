#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - PostgreSQL数据访问器

专门处理PostgreSQL数据库的长期分析和历史数据操作

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

import os
import pandas as pd
from typing import Dict, List
import logging
from datetime import datetime
import uuid

# 导入基础模块
from src.storage.access.base import (
    IDataAccessLayer,
    get_database_name_from_classification,
    normalize_dataframe,
    DataClassification,
)
from src.monitoring.monitoring_database import MonitoringDatabase

# 导入数据库管理器
from src.storage.database.database_manager import DatabaseTableManager, DatabaseType

logger = logging.getLogger("MyStocksPostgreSQLAccess")


class PostgreSQLDataAccess(IDataAccessLayer):
    """PostgreSQL数据访问器 - 历史数据仓库和分析"""

    def __init__(self, monitoring_db: MonitoringDatabase):
        super().__init__(monitoring_db)
        self.db_manager = DatabaseTableManager()
        self.db_type = DatabaseType.POSTGRESQL
        self.db_manager = DatabaseTableManager()
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
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        actual_table_name = table_name or self._get_default_table_name(classification)
        database_name = get_database_name_from_classification(classification)

        try:
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
                self._upsert_data_with_engine(processed_data, actual_table_name, engine, classification)
            else:  # append
                processed_data.to_sql(
                    actual_table_name,
                    engine,
                    if_exists="append",
                    index=False,
                    method="multi",
                )

            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            self.monitoring_db.log_operation(
                operation_id=operation_id,
                operation_type="SAVE",
                classification=classification.value,
                target_database=self.db_type.value,
                table_name=actual_table_name,
                record_count=len(processed_data),
                operation_status="SUCCESS",
                execution_time_ms=execution_time_ms,
            )
            logger.info("PostgreSQL保存成功: %s, %s条记录", actual_table_name, len(processed_data))

            return True

        except Exception as e:
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            error_msg = f"PostgreSQL保存失败: {e}"
            self.monitoring_db.log_operation(
                operation_id=operation_id,
                operation_type="SAVE",
                classification=classification.value,
                target_database=self.db_type.value,
                table_name=actual_table_name,
                record_count=0,
                operation_status="FAILED",
                error_message=error_msg,
                execution_time_ms=execution_time_ms,
            )
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
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        actual_table_name = table_name or self._get_default_table_name(classification)
        database_name = get_database_name_from_classification(classification)

        try:
            # 构建查询语句 - SECURITY FIX: Now returns (sql, params)
            query, params = self._build_analytical_query(classification, actual_table_name, filters, **kwargs)

            # 执行查询 - SECURITY FIX: Use parameterized query
            conn = self.db_manager.get_connection(self.db_type, database_name)
            data = pd.read_sql(query, conn, params=params)

            # 后处理
            processed_data = self._postprocess_analytical_data(data, classification)

            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            self.monitoring_db.log_operation(
                operation_id=operation_id,
                operation_type="LOAD",
                classification=classification.value,
                target_database=self.db_type.value,
                table_name=actual_table_name,
                record_count=len(processed_data),
                operation_status="SUCCESS",
                execution_time_ms=execution_time_ms,
            )
            logger.info("PostgreSQL加载成功: %s, %s条记录", actual_table_name, len(processed_data))

            return processed_data

        except Exception as e:
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            error_msg = f"PostgreSQL加载失败: {e}"
            self.monitoring_db.log_operation(
                operation_id=operation_id,
                operation_type="LOAD",
                classification=classification.value,
                target_database=self.db_type.value,
                table_name=actual_table_name,
                record_count=0,
                operation_status="FAILED",
                error_message=error_msg,
                execution_time_ms=execution_time_ms,
            )
            logger.error(error_msg)
            return pd.DataFrame()  # Return empty DataFrame on failure

    def update_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        key_columns: List[str] = None,
        **kwargs,
    ) -> bool:
        """
        更新PostgreSQL数据

        Args:
            data: 数据DataFrame
            classification: 数据分类
            table_name: 表名（可选）
            key_columns: 主键列
            **kwargs: 其他参数

        Returns:
            bool: 更新是否成功
        """
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        actual_table_name = table_name or self._get_default_table_name(classification)
        database_name = get_database_name_from_classification(classification)

        try:
            key_columns = key_columns or self._get_default_key_columns(classification)

            # 获取连接
            conn = self.db_manager.get_connection(self.db_type, database_name)
            cursor = conn.cursor()

            # 执行更新
            success = self._execute_update(cursor, data, actual_table_name, key_columns)

            if success:
                conn.commit()
                end_time = datetime.now()
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                self.monitoring_db.log_operation(
                    operation_id=operation_id,
                    operation_type="UPDATE",
                    classification=classification.value,
                    target_database=self.db_type.value,
                    table_name=actual_table_name,
                    record_count=len(data),
                    operation_status="SUCCESS",
                    execution_time_ms=execution_time_ms,
                )
                logger.info("PostgreSQL更新成功: %s, %s条记录", actual_table_name, len(data))
            else:
                conn.rollback()
                end_time = datetime.now()
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                self.monitoring_db.log_operation(
                    operation_id=operation_id,
                    operation_type="UPDATE",
                    classification=classification.value,
                    target_database=self.db_type.value,
                    table_name=actual_table_name,
                    record_count=0,
                    operation_status="FAILED",
                    error_message="更新失败，无记录受影响",
                    execution_time_ms=execution_time_ms,
                )

            return success

        except Exception as e:
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            error_msg = f"PostgreSQL更新失败: {e}"
            self.monitoring_db.log_operation(
                operation_id=operation_id,
                operation_type="UPDATE",
                classification=classification.value,
                target_database=self.db_type.value,
                table_name=actual_table_name,
                record_count=0,
                operation_status="FAILED",
                error_message=error_msg,
                execution_time_ms=execution_time_ms,
            )
            logger.error(error_msg)
            return False

    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """
        删除PostgreSQL数据

        Args:
            classification: 数据分类
            table_name: 表名（可选）
            filters: 过滤条件
            **kwargs: 其他参数

        Returns:
            bool: 删除是否成功
        """
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        actual_table_name = table_name or self._get_default_table_name(classification)
        database_name = get_database_name_from_classification(classification)

        try:
            if not filters:
                error_msg = "删除操作必须指定过滤条件"
                logger.error(error_msg)
                self.monitoring_db.log_operation(
                    operation_id=operation_id,
                    operation_type="DELETE",
                    classification=classification.value,
                    target_database=self.db_type.value,
                    table_name=actual_table_name,
                    record_count=0,
                    operation_status="FAILED",
                    error_message=error_msg,
                    execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                )
                return False

            # 获取连接
            conn = self.db_manager.get_connection(self.db_type, database_name)
            cursor = conn.cursor()

            # 构建删除语句 - SECURITY FIX: Now returns (sql, params)
            delete_sql, params = self._build_delete_query(actual_table_name, filters)

            # 执行删除 - SECURITY FIX: Use parameterized query with params
            cursor.execute(delete_sql, params)
            affected_rows = cursor.rowcount
            conn.commit()

            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            self.monitoring_db.log_operation(
                operation_id=operation_id,
                operation_type="DELETE",
                classification=classification.value,
                target_database=self.db_type.value,
                table_name=actual_table_name,
                record_count=affected_rows,
                operation_status="SUCCESS",
                execution_time_ms=execution_time_ms,
            )
            logger.info("PostgreSQL删除成功: %s, %s条记录", actual_table_name, affected_rows)

            return True

        except Exception as e:
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            error_msg = f"PostgreSQL删除失败: {e}"
            self.monitoring_db.log_operation(
                operation_id=operation_id,
                operation_type="DELETE",
                classification=classification.value,
                target_database=self.db_type.value,
                table_name=actual_table_name,
                record_count=0,
                operation_status="FAILED",
                error_message=error_msg,
                execution_time_ms=execution_time_ms,
            )
            logger.error(error_msg)
            return False

    def _get_default_table_name(self, classification: DataClassification) -> str:
        """根据数据分类获取默认表名"""
        table_mapping = {
            DataClassification.DAILY_KLINE: "daily_kline",
            DataClassification.TECHNICAL_INDICATORS: "technical_indicators",
            DataClassification.QUANTITATIVE_FACTORS: "quantitative_factors",
            DataClassification.MODEL_OUTPUTS: "model_outputs",
            DataClassification.TRADING_SIGNALS: "trading_signals",
            DataClassification.ORDER_RECORDS: "order_records",
            DataClassification.TRANSACTION_RECORDS: "transaction_records",
            DataClassification.POSITION_RECORDS: "position_records",
            DataClassification.ACCOUNT_FUNDS: "account_funds",
            DataClassification.REALTIME_QUOTES: "realtime_quotes",
        }
        return table_mapping.get(classification, "unknown_table")

    def _get_default_key_columns(self, classification: DataClassification) -> List[str]:
        """根据数据分类获取默认主键列"""
        key_mapping = {
            DataClassification.DAILY_KLINE: ["symbol", "trade_date"],
            DataClassification.REALTIME_QUOTES: [
                "symbol",
                "fetch_timestamp",
            ],  # 添加实时行情主键
            DataClassification.TECHNICAL_INDICATORS: [
                "symbol",
                "calc_date",
                "indicator_name",
            ],
            DataClassification.QUANTITATIVE_FACTORS: [
                "symbol",
                "calc_date",
                "factor_name",
            ],
            DataClassification.MODEL_OUTPUTS: ["model_id", "symbol", "calc_date"],
            DataClassification.TRADING_SIGNALS: ["signal_id"],
            DataClassification.ORDER_RECORDS: ["order_id"],
            DataClassification.TRANSACTION_RECORDS: ["transaction_id"],
            DataClassification.POSITION_RECORDS: ["position_id"],
            DataClassification.ACCOUNT_FUNDS: ["account_id", "record_date"],
        }
        return key_mapping.get(classification, ["id"])

    def _preprocess_analytical_data(self, data: pd.DataFrame, classification: DataClassification) -> pd.DataFrame:
        """预处理分析数据"""
        processed_data = normalize_dataframe(data)

        # 根据分类进行特定预处理
        if classification == DataClassification.DAILY_KLINE:
            # 确保日线数据必要字段
            required_columns = [
                "symbol",
                "trade_date",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
            for col in required_columns:
                if col not in processed_data.columns:
                    logger.warning("日线数据缺少必要字段: %s", col)

        elif classification == DataClassification.TECHNICAL_INDICATORS:
            # 确保技术指标必要字段
            required_columns = [
                "symbol",
                "calc_date",
                "indicator_name",
                "indicator_value",
            ]
            for col in required_columns:
                if col not in processed_data.columns:
                    logger.warning("技术指标数据缺少必要字段: %s", col)

        return processed_data

    def _get_postgresql_engine(self, database_name: str):
        """获取PostgreSQL SQLAlchemy引擎"""
        import sqlalchemy

        # 从环境变量读取PostgreSQL配置
        host = os.getenv("POSTGRESQL_HOST")
        user = os.getenv("POSTGRESQL_USER")
        password = os.getenv("POSTGRESQL_PASSWORD")
        port = os.getenv("POSTGRESQL_PORT", "5432")

        # 构建连接字符串
        connection_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database_name}"

        # 创建SQLAlchemy引擎
        engine = sqlalchemy.create_engine(connection_url)
        return engine

    def _upsert_data_with_engine(
        self,
        data: pd.DataFrame,
        table_name: str,
        engine,
        classification: DataClassification,
    ):
        """使用SQLAlchemy引擎执行UPSERT操作"""
        try:
            # 首先尝试使用原生UPSERT逻辑
            with engine.begin() as conn:
                raw_conn = conn.connection
                affected_rows = self._upsert_data(data, table_name, raw_conn, classification)
                logger.info("UPSERT完成: %s, 影响行数: %s", table_name, affected_rows)

        except Exception as e:
            logger.error("UPSERT操作失败，回退到简单插入模式: %s", e)
            # 回退到简单插入模式
            try:
                data.to_sql(table_name, engine, if_exists="append", index=False, method="multi")
            except Exception as fallback_error:
                if "duplicate key" in str(fallback_error).lower() or "unique constraint" in str(fallback_error).lower():
                    logger.warning("检测到重复数据，跳过插入: %s", fallback_error)
                    # 对于重复数据，我们已经有了UPSERT逻辑处理，这里可以忽略
                    pass
                else:
                    raise fallback_error

    def _postprocess_analytical_data(self, data: pd.DataFrame, classification: DataClassification) -> pd.DataFrame:
        """后处理分析数据"""
        if data.empty:
            return data

        # 确保日期列的格式
        date_columns = ["trade_date", "calc_date", "created_at", "updated_at"]
        for col in date_columns:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col])

        return data

    def _upsert_data(
        self,
        data: pd.DataFrame,
        table_name: str,
        conn,
        classification: DataClassification,
    ):
        """PostgreSQL Upsert操作 - 使用ON CONFLICT实现"""
        try:
            key_columns = self._get_default_key_columns(classification)
            cursor = conn.cursor()

            # 构建列名和占位符
            columns = list(data.columns)
            placeholders = ", ".join(["%s"] * len(columns))
            column_names = ", ".join(columns)

            # 构建ON CONFLICT子句
            conflict_columns = ", ".join(key_columns)

            # 构建UPDATE SET子句（排除主键列）
            update_columns = [col for col in columns if col not in key_columns]
            update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_columns])

            # 构建完整的UPSERT SQL
            upsert_sql = f"""
            INSERT INTO {table_name} ({column_names})
            VALUES ({placeholders})
            ON CONFLICT ({conflict_columns})
            DO UPDATE SET
                {update_set},
                updated_at = CURRENT_TIMESTAMP
            """

            # 执行批量UPSERT
            records_to_insert = []
            for _, row in data.iterrows():
                record = []
                for col in columns:
                    value = row[col]
                    # 处理NaN值和pandas特殊类型
                    if pd.isna(value):
                        record.append(None)
                    elif isinstance(value, pd.Timestamp):
                        record.append(value.to_pydatetime())
                    else:
                        record.append(value)
                records_to_insert.append(tuple(record))

            # 批量执行UPSERT
            cursor.executemany(upsert_sql, records_to_insert)
            conn.commit()

            logger.info("PostgreSQL UPSERT操作完成: %s, 处理记录数: %s", table_name, len(records_to_insert))
            return len(records_to_insert)

        except Exception as e:
            logger.error("PostgreSQL UPSERT操作失败: %s, 错误: %s", table_name, e)
            conn.rollback()
            raise

    def _execute_update(self, cursor, data: pd.DataFrame, table_name: str, key_columns: List[str]) -> bool:
        """执行更新操作"""
        try:
            for _, row in data.iterrows():
                # 构建SET子句
                set_clauses = []
                set_values = []
                for col in data.columns:
                    if col not in key_columns:
                        set_clauses.append(f"{col} = %s")
                        set_values.append(row[col])

                # 构建WHERE子句
                where_clauses = []
                where_values = []
                for col in key_columns:
                    where_clauses.append(f"{col} = %s")
                    where_values.append(row[col])

                # 组装SQL
                update_sql = f"""
                    UPDATE {table_name}
                    SET {", ".join(set_clauses)}
                    WHERE {" AND ".join(where_clauses)}
                """

                # 执行更新
                cursor.execute(update_sql, set_values + where_values)

            return True

        except Exception as e:
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
        # SECURITY FIX: Whitelist table names to prevent injection through table_name
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
        if table_name not in ALLOWED_TABLES:
            raise ValueError(f"Invalid table name: {table_name}")

        base_query = f"SELECT * FROM {table_name}"
        conditions = []
        params = []

        # 添加过滤条件 - 使用参数化查询
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    # SECURITY FIX: Use individual placeholders for IN clause
                    placeholders = ", ".join(["%s"] * len(value))
                    conditions.append(f"{key} IN ({placeholders})")
                    params.extend(value)
                elif isinstance(value, str):
                    # SECURITY FIX: Use parameterized query instead of string concatenation
                    conditions.append(f"{key} = %s")
                    params.append(value)
                else:
                    # SECURITY FIX: Even numeric values use parameterized approach
                    conditions.append(f"{key} = %s")
                    params.append(value)

        # 添加kwargs中的条件
        for key, value in kwargs.items():
            if key in ["limit", "offset", "order_by"]:
                continue  # 这些在后面处理

            if isinstance(value, str):
                # SECURITY FIX: Parameterize string conditions
                conditions.append(f"{key} = %s")
                params.append(value)
            else:
                # SECURITY FIX: Parameterize all conditions
                conditions.append(f"{key} = %s")
                params.append(value)

        # 组装查询语句
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        # 添加排序 - SECURITY: 添加ORDER BY列白名单防止SQL注入
        if "order_by" in kwargs:
            order_by = kwargs["order_by"]

            # 根据数据分类定义允许的ORDER BY列白名单
            ALLOWED_ORDER_BY_COLUMNS = {
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
                DataClassification.STOCK_INFO: [
                    "symbol",
                    "name",
                    "market",
                    "industry",
                    "list_date",
                    "created_at",
                    "updated_at",
                ],
                DataClassification.FINANCIAL_REPORTS: [
                    "report_date",
                    "symbol",
                    "report_type",
                    "revenue",
                    "net_profit",
                    "created_at",
                    "updated_at",
                ],
            }

            # 获取当前分类允许的列
            allowed_columns = ALLOWED_ORDER_BY_COLUMNS.get(classification, [])

            # 验证和清理order_by参数
            if isinstance(order_by, str):
                # 支持多列排序，如 "trade_date DESC, symbol ASC"
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
                            direction = "ASC"  # 默认升序
                    else:
                        continue  # 跳过无效格式

                    # 验证列名是否在白名单中
                    if column_name in allowed_columns:
                        order_columns.append(f"{column_name} {direction}".strip())

                if order_columns:
                    validated_order_by = ", ".join(order_columns)
                    base_query += f" ORDER BY {validated_order_by}"
                else:
                    # 如果没有有效的排序列，使用默认排序
                    self.logger.warning("Invalid order_by columns: %s, using default sort", order_by)
                    if classification == DataClassification.DAILY_KLINE:
                        base_query += " ORDER BY trade_date DESC"
                    elif classification in [
                        DataClassification.TECHNICAL_INDICATORS,
                        DataClassification.QUANTITATIVE_FACTORS,
                    ]:
                        base_query += " ORDER BY calc_date DESC"
                    else:
                        base_query += " ORDER BY created_at DESC"
        else:
            # 默认排序
            if classification == DataClassification.DAILY_KLINE:
                base_query += " ORDER BY trade_date DESC"
            elif classification in [
                DataClassification.TECHNICAL_INDICATORS,
                DataClassification.QUANTITATIVE_FACTORS,
            ]:
                base_query += " ORDER BY calc_date DESC"
            else:
                base_query += " ORDER BY created_at DESC"

        # 添加限制 - SECURITY: limit and offset should also use parameterization
        if "limit" in kwargs:
            # For LIMIT/OFFSET, use parameterized approach
            limit_val = kwargs["limit"]
            if isinstance(limit_val, int):
                base_query += f" LIMIT {limit_val}"  # Integers are safe for LIMIT
            else:
                base_query += " LIMIT %s"
                params.append(limit_val)

        if "offset" in kwargs:
            offset_val = kwargs["offset"]
            if isinstance(offset_val, int):
                base_query += f" OFFSET {offset_val}"  # Integers are safe for OFFSET
            else:
                base_query += " OFFSET %s"
                params.append(offset_val)

        return base_query, tuple(params)

    def _build_delete_query(self, table_name: str, filters: Dict) -> tuple:
        """
        构建删除查询语句 - 使用参数化查询防止SQL注入

        返回值: (sql_string, bind_parameters)
        """
        # SECURITY FIX: Whitelist table names to prevent injection through table_name
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
        if table_name not in ALLOWED_TABLES:
            raise ValueError(f"Invalid table name: {table_name}")

        base_query = f"DELETE FROM {table_name}"

        conditions = []
        params = []

        for key, value in filters.items():
            if isinstance(value, str):
                # SECURITY FIX: Use parameterized query instead of string concatenation
                conditions.append(f"{key} = %s")
                params.append(value)
            else:
                # SECURITY FIX: Parameterize numeric conditions too
                conditions.append(f"{key} = %s")
                params.append(value)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        return base_query, tuple(params)
