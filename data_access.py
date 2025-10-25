#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 统一数据访问层
完全按照原始设计理念实现的5大数据分类体系和自动化路由

设计理念：
1. 5大数据分类：市场数据、参考数据、衍生数据、交易数据、元数据
2. 自动路由：根据数据特性自动选择最适合的数据库
3. TDengine为高频数据核心：专门处理Tick和分钟级数据
4. 监控集成：所有操作自动记录到监控数据库
5. 配置驱动：表结构和访问模式完全由配置文件管理

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-09-21
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple, Any
from abc import ABC, abstractmethod
import logging
import uuid

# 导入核心模块
from core import (
    DataClassification,
    DatabaseTarget,
    DataStorageStrategy,
    ConfigDrivenTableManager,
)
from monitoring import (
    MonitoringDatabase,
    DataQualityMonitor,
    PerformanceMonitor,
    AlertManager,
    AlertLevel,
    OperationMetrics,
)

# 导入现有数据库管理器
from db_manager.database_manager import DatabaseTableManager, DatabaseType

logger = logging.getLogger("MyStocksDataAccess")


class IDataAccessLayer(ABC):
    """数据访问层接口"""

    @abstractmethod
    def save_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        **kwargs,
    ) -> bool:
        """保存数据"""
        pass

    @abstractmethod
    def load_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> pd.DataFrame:
        """加载数据"""
        pass

    @abstractmethod
    def update_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        key_columns: List[str] = None,
        **kwargs,
    ) -> bool:
        """更新数据"""
        pass

    @abstractmethod
    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """删除数据"""
        pass


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
            DataStorageStrategy.get_database_name(classification),
            "INSERT",
        )

        try:
            database_name = DataStorageStrategy.get_database_name(classification)

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
            DataStorageStrategy.get_database_name(classification),
            "SELECT",
        )

        try:
            database_name = DataStorageStrategy.get_database_name(classification)

            # 构建查询语句
            query = self._build_analytical_query(
                classification, actual_table_name, filters, **kwargs
            )

            # 执行查询
            conn = self.db_manager.get_connection(self.db_type, database_name)
            data = pd.read_sql(query, conn)

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
        # 记录操作开始
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            self.db_type.value,
            DataStorageStrategy.get_database_name(classification),
            "UPDATE",
        )

        try:
            database_name = DataStorageStrategy.get_database_name(classification)
            key_columns = key_columns or self._get_default_key_columns(classification)

            # 获取连接
            conn = self.db_manager.get_connection(self.db_type, database_name)
            cursor = conn.cursor()

            # 执行更新
            success = self._execute_update(cursor, data, actual_table_name, key_columns)

            if success:
                conn.commit()
                self.monitoring_db.log_operation_result(operation_id, True, len(data))
                logger.info(
                    f"PostgreSQL更新成功: {actual_table_name}, {len(data)}条记录"
                )
            else:
                conn.rollback()
                self.monitoring_db.log_operation_result(
                    operation_id, False, 0, "更新失败"
                )

            return success

        except Exception as e:
            error_msg = f"PostgreSQL更新失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
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
        # 记录操作开始
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            self.db_type.value,
            DataStorageStrategy.get_database_name(classification),
            "DELETE",
        )

        try:
            if not filters:
                logger.error("删除操作必须指定过滤条件")
                return False

            database_name = DataStorageStrategy.get_database_name(classification)

            # 获取连接
            conn = self.db_manager.get_connection(self.db_type, database_name)
            cursor = conn.cursor()

            # 构建删除语句
            delete_sql = self._build_delete_query(actual_table_name, filters)

            # 执行删除
            cursor.execute(delete_sql)
            affected_rows = cursor.rowcount
            conn.commit()

            self.monitoring_db.log_operation_result(operation_id, True, affected_rows)
            logger.info(
                f"PostgreSQL删除成功: {actual_table_name}, {affected_rows}条记录"
            )

            return True

        except Exception as e:
            error_msg = f"PostgreSQL删除失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
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

    def _preprocess_analytical_data(
        self, data: pd.DataFrame, classification: DataClassification
    ) -> pd.DataFrame:
        """预处理分析数据"""
        processed_data = data.copy()

        # 添加创建时间和更新时间
        if "created_at" not in processed_data.columns:
            processed_data["created_at"] = datetime.now()
        if "updated_at" not in processed_data.columns:
            processed_data["updated_at"] = datetime.now()

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
                    logger.warning(f"日线数据缺少必要字段: {col}")

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
                    logger.warning(f"技术指标数据缺少必要字段: {col}")

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
        connection_url = (
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database_name}"
        )

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
                affected_rows = self._upsert_data(
                    data, table_name, raw_conn, classification
                )
                logger.info(f"UPSERT完成: {table_name}, 影响行数: {affected_rows}")

        except Exception as e:
            logger.error(f"UPSERT操作失败，回退到简单插入模式: {e}")
            # 回退到简单插入模式
            try:
                data.to_sql(
                    table_name, engine, if_exists="append", index=False, method="multi"
                )
            except Exception as fallback_error:
                if (
                    "duplicate key" in str(fallback_error).lower()
                    or "unique constraint" in str(fallback_error).lower()
                ):
                    logger.warning(f"检测到重复数据，跳过插入: {fallback_error}")
                    # 对于重复数据，我们已经有了UPSERT逻辑处理，这里可以忽略
                    pass
                else:
                    raise fallback_error

    def _postprocess_analytical_data(
        self, data: pd.DataFrame, classification: DataClassification
    ) -> pd.DataFrame:
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
            update_set = ", ".join(
                [f"{col} = EXCLUDED.{col}" for col in update_columns]
            )

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

            logger.info(
                f"PostgreSQL UPSERT操作完成: {table_name}, 处理记录数: {len(records_to_insert)}"
            )
            return len(records_to_insert)

        except Exception as e:
            logger.error(f"PostgreSQL UPSERT操作失败: {table_name}, 错误: {e}")
            conn.rollback()
            raise

    def _execute_update(
        self, cursor, data: pd.DataFrame, table_name: str, key_columns: List[str]
    ) -> bool:
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
                    SET {', '.join(set_clauses)} 
                    WHERE {' AND '.join(where_clauses)}
                """

                # 执行更新
                cursor.execute(update_sql, set_values + where_values)

            return True

        except Exception as e:
            logger.error(f"执行更新操作失败: {e}")
            return False

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
                    if isinstance(value[0], str):
                        values = "','".join(value)
                        conditions.append(f"{key} IN ('{values}')")
                    else:
                        values = ",".join([str(v) for v in value])
                        conditions.append(f"{key} IN ({values})")
                elif isinstance(value, str):
                    conditions.append(f"{key} = '{value}'")
                else:
                    conditions.append(f"{key} = {value}")

        # 添加kwargs中的条件
        for key, value in kwargs.items():
            if key in ["limit", "offset", "order_by"]:
                continue  # 这些在后面处理

            if isinstance(value, str):
                conditions.append(f"{key} = '{value}'")
            else:
                conditions.append(f"{key} = {value}")

        # 组装查询语句
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        # 添加排序
        if "order_by" in kwargs:
            base_query += f" ORDER BY {kwargs['order_by']}"
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

        # 添加限制
        if "limit" in kwargs:
            base_query += f" LIMIT {kwargs['limit']}"

        if "offset" in kwargs:
            base_query += f" OFFSET {kwargs['offset']}"

        return base_query

    def _build_delete_query(self, table_name: str, filters: Dict) -> str:
        """构建删除查询语句"""
        base_query = f"DELETE FROM {table_name}"

        conditions = []
        for key, value in filters.items():
            if isinstance(value, str):
                conditions.append(f"{key} = '{value}'")
            else:
                conditions.append(f"{key} = {value}")

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        return base_query
