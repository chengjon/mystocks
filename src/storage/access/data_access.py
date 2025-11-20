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
from src.core import (
    DataClassification,
    DatabaseTarget,
    DataStorageStrategy,
    ConfigDrivenTableManager,
)
from src.monitoring import (
    MonitoringDatabase,
    DataQualityMonitor,
    PerformanceMonitor,
    AlertManager,
    AlertLevel,
    OperationMetrics,
)

# 导入现有数据库管理器
from src.db_manager.database_manager import DatabaseTableManager, DatabaseType

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


class TDengineDataAccess(IDataAccessLayer):
    """TDengine数据访问器 - 高频时序数据专用"""

    def __init__(self, monitoring_db: MonitoringDatabase):
        """
        初始化TDengine数据访问器

        Args:
            monitoring_db: 监控数据库
        """
        self.db_manager = DatabaseTableManager()
        self.monitoring_db = monitoring_db
        self.db_type = DatabaseType.TDENGINE

    def save_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        **kwargs,
    ) -> bool:
        """
        保存时序数据到TDengine，支持去重策略

        Args:
            data: 数据DataFrame
            classification: 数据分类
            table_name: 表名（可选，默认根据分类确定）
            **kwargs: 其他参数，支持 dedup_strategy 参数

        Returns:
            bool: 保存是否成功
        """
        # 记录操作开始
        operation_id = self.monitoring_db.log_operation_start(
            table_name or self._get_default_table_name(classification),
            self.db_type.value,
            DataManager().get_database_name(classification),
            "upsert_data",
        )

        try:
            # 确定表名
            actual_table_name = table_name or self._get_default_table_name(
                classification
            )
            database_name = DataManager().get_database_name(classification)

            # 数据预处理
            processed_data = self._preprocess_timeseries_data(data, classification)

            # 获取去重策略
            from src.core import DeduplicationStrategy, DataManager

            dedup_strategy = kwargs.get("dedup_strategy")
            if not dedup_strategy:
                dedup_strategy = DS.get_smart_deduplication_strategy(
                    classification, kwargs.get("data_characteristics", {})
                )

            # 应用TDengine特定的去重逻辑
            final_data = self._apply_tdengine_deduplication(
                processed_data, actual_table_name, dedup_strategy, classification
            )

            if final_data is None or final_data.empty:
                logger.info(f"TDengine去重后无数据需要保存: {actual_table_name}")
                self.monitoring_db.log_operation_result(operation_id, True, 0)
                return True

            # 获取连接
            conn = self.db_manager.get_connection(self.db_type, database_name)
            cursor = conn.cursor()

            # 构建插入语句
            if classification == DataClassification.TICK_DATA:
                success = self._insert_tick_data(cursor, final_data, actual_table_name)
            elif classification == DataClassification.MINUTE_KLINE:
                success = self._insert_minute_kline(
                    cursor, final_data, actual_table_name
                )
            else:
                success = self._insert_generic_timeseries(
                    cursor, final_data, actual_table_name
                )

            if success:
                self.monitoring_db.log_operation_result(
                    operation_id, True, len(final_data)
                )
                logger.info(
                    f"TDengine保存成功: {actual_table_name}, {len(final_data)}条记录，去重策略: {dedup_strategy.value}"
                )
            else:
                self.monitoring_db.log_operation_result(
                    operation_id, False, 0, "插入失败"
                )

            return success

        except Exception as e:
            error_msg = f"TDengine保存失败: {e}"
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
        从TDengine加载时序数据

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
            query = self._build_timeseries_query(
                classification, actual_table_name, filters, **kwargs
            )

            # 执行查询
            conn = self.db_manager.get_connection(self.db_type, database_name)
            data = pd.read_sql(query, conn)

            # 后处理
            processed_data = self._postprocess_timeseries_data(data, classification)

            self.monitoring_db.log_operation_result(
                operation_id, True, len(processed_data)
            )
            logger.info(
                f"TDengine加载成功: {actual_table_name}, {len(processed_data)}条记录"
            )

            return processed_data

        except Exception as e:
            error_msg = f"TDengine加载失败: {e}"
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
        """TDengine通常不支持更新操作，使用插入替代"""
        logger.warning("TDengine不支持更新操作，将使用插入")
        return self.save_data(data, classification, table_name, **kwargs)

    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """TDengine删除数据（谨慎使用）"""
        logger.warning("TDengine删除操作需要谨慎使用")
        return False

    def _get_default_table_name(self, classification: DataClassification) -> str:
        """根据数据分类获取默认表名"""
        table_mapping = {
            DataClassification.TICK_DATA: "tick_data",
            DataClassification.MINUTE_KLINE: "minute_kline",
            DataClassification.DEPTH_DATA: "depth_data",
        }
        return table_mapping.get(classification, "unknown_table")

    def _apply_tdengine_deduplication(
        self,
        data: pd.DataFrame,
        table_name: str,
        strategy,
        classification: DataClassification,
    ) -> Optional[pd.DataFrame]:
        """
        应用TDengine特定的去重策略

        Args:
            data: 原始数据
            table_name: 表名
            strategy: 去重策略
            classification: 数据分类

        Returns:
            处理后的数据
        """
        try:
            from src.core import DeduplicationStrategy

            if strategy == DeduplicationStrategy.LATEST_WINS:
                return self._handle_tdengine_latest_wins(
                    data, table_name, classification
                )
            elif strategy == DeduplicationStrategy.FIRST_WINS:
                return self._handle_tdengine_first_wins(
                    data, table_name, classification
                )
            elif strategy == DeduplicationStrategy.MERGE:
                return self._handle_tdengine_merge(data, table_name, classification)
            elif strategy == DeduplicationStrategy.REJECT:
                return self._handle_tdengine_reject(data, table_name, classification)
            else:
                logger.warning(f"未知TDengine去重策略: {strategy}, 使用原始数据")
                return data

        except Exception as e:
            logger.error(f"TDengine去重策略处理失败: {strategy}, 错误: {e}")
            return data

    def _handle_tdengine_latest_wins(
        self, data: pd.DataFrame, table_name: str, classification: DataClassification
    ) -> pd.DataFrame:
        """TDengine最新覆盖策略：基于时间戳去重，保留最新记录"""
        try:
            # 对于时序数据，按时间戳和symbol进行去重，保留最新的记录
            time_column = "ts" if "ts" in data.columns else "timestamp"
            if time_column not in data.columns:
                logger.warning("时间列不存在，跳过时序去重")
                return data

            # 确保时间列是datetime类型
            data[time_column] = pd.to_datetime(data[time_column])

            # 按symbol和时间戳去重，保留最新的记录
            if "symbol" in data.columns:
                deduped_data = data.sort_values([time_column]).drop_duplicates(
                    subset=["symbol", time_column], keep="last"
                )
            else:
                deduped_data = data.sort_values([time_column]).drop_duplicates(
                    subset=[time_column], keep="last"
                )

            removed_count = len(data) - len(deduped_data)
            if removed_count > 0:
                logger.info(
                    f"TDengine LATEST_WINS去重：移除 {removed_count} 条重复记录"
                )

            return deduped_data

        except Exception as e:
            logger.error(f"TDengine LATEST_WINS处理失败: {e}")
            return data

    def _handle_tdengine_first_wins(
        self, data: pd.DataFrame, table_name: str, classification: DataClassification
    ) -> pd.DataFrame:
        """TDengine首次保留策略：查询已存在的数据，过滤重复"""
        try:
            # 查询已存在的时间戳和symbol组合
            time_column = "ts" if "ts" in data.columns else "timestamp"
            if time_column not in data.columns:
                return data

            # 构建查询现有数据的SQL
            database_name = DataManager().get_database_name(classification)
            conn = self.db_manager.get_connection(self.db_type, database_name)

            # 简化实现：基于时间范围查询
            min_time = data[time_column].min()
            max_time = data[time_column].max()

            if "symbol" in data.columns:
                symbols = data["symbol"].unique()
                symbols_str = "','".join(symbols)
                query = f"""
                SELECT DISTINCT {time_column}, symbol
                FROM {table_name}
                WHERE {time_column} BETWEEN '{min_time}' AND '{max_time}'
                AND symbol IN ('{symbols_str}')
                """
            else:
                query = f"""
                SELECT DISTINCT {time_column}
                FROM {table_name}
                WHERE {time_column} BETWEEN '{min_time}' AND '{max_time}'
                """

            existing_data = pd.read_sql(query, conn)

            if existing_data.empty:
                return data

            # 过滤掉已存在的数据
            if "symbol" in data.columns:
                merge_columns = [time_column, "symbol"]
            else:
                merge_columns = [time_column]

            filtered_data = data.merge(
                existing_data, on=merge_columns, how="left", indicator=True
            )
            new_data = filtered_data[filtered_data["_merge"] == "left_only"].drop(
                "_merge", axis=1
            )

            removed_count = len(data) - len(new_data)
            if removed_count > 0:
                logger.info(
                    f"TDengine FIRST_WINS去重：过滤 {removed_count} 条已存在记录"
                )

            return new_data

        except Exception as e:
            logger.error(f"TDengine FIRST_WINS处理失败: {e}")
            return data

    def _handle_tdengine_merge(
        self, data: pd.DataFrame, table_name: str, classification: DataClassification
    ) -> pd.DataFrame:
        """TDengine合并策略：时序数据通常使用最新覆盖"""
        # 对于时序数据，合并策略等同于最新覆盖
        return self._handle_tdengine_latest_wins(data, table_name, classification)

    def _handle_tdengine_reject(
        self, data: pd.DataFrame, table_name: str, classification: DataClassification
    ) -> Optional[pd.DataFrame]:
        """TDengine拒绝重复策略：检查重复并拒绝"""
        try:
            # 首先内部去重检查
            time_column = "ts" if "ts" in data.columns else "timestamp"
            if time_column not in data.columns:
                return data

            # 检查内部重复
            if "symbol" in data.columns:
                duplicates = data.duplicated(subset=[time_column, "symbol"])
            else:
                duplicates = data.duplicated(subset=[time_column])

            if duplicates.any():
                dup_count = duplicates.sum()
                logger.warning(
                    f"TDengine REJECT策略：发现 {dup_count} 条内部重复记录，拒绝保存"
                )
                return pd.DataFrame()  # 返回空DataFrame，拒绝所有数据

            # 简化实现：如果没有内部重复，允许保存
            return data

        except Exception as e:
            logger.error(f"TDengine REJECT处理失败: {e}")
            return data

    def _preprocess_timeseries_data(
        self, data: pd.DataFrame, classification: DataClassification
    ) -> pd.DataFrame:
        """预处理时序数据"""
        processed_data = data.copy()

        # 确保时间戳列存在
        if (
            "timestamp" not in processed_data.columns
            and "ts" not in processed_data.columns
        ):
            processed_data["ts"] = datetime.now()
        elif "timestamp" in processed_data.columns:
            processed_data["ts"] = pd.to_datetime(processed_data["timestamp"])
            processed_data.drop("timestamp", axis=1, inplace=True)

        # 根据分类进行特定预处理
        if classification == DataClassification.TICK_DATA:
            required_columns = ["ts", "symbol", "price", "volume"]
        elif classification == DataClassification.MINUTE_KLINE:
            required_columns = [
                "ts",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        else:
            required_columns = ["ts", "symbol"]

        # 检查必要列
        missing_columns = [
            col for col in required_columns if col not in processed_data.columns
        ]
        if missing_columns:
            logger.warning(f"缺少必要列: {missing_columns}")

        return processed_data

    def _postprocess_timeseries_data(
        self, data: pd.DataFrame, classification: DataClassification
    ) -> pd.DataFrame:
        """后处理时序数据"""
        if data.empty:
            return data

        # 确保时间戳列的格式
        if "ts" in data.columns:
            data["ts"] = pd.to_datetime(data["ts"])
            data = data.sort_values("ts")

        return data

    def _insert_tick_data(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
        """插入Tick数据"""
        try:
            # 构建Tick数据插入语句
            insert_sql = f"""
                INSERT INTO {table_name} (ts, symbol, price, volume, amount, exchange)
                VALUES (?, ?, ?, ?, ?, ?)
            """

            # 准备数据
            records = []
            for _, row in data.iterrows():
                records.append(
                    (
                        row.get("ts", datetime.now()),
                        row.get("symbol", ""),
                        row.get("price", 0.0),
                        row.get("volume", 0),
                        row.get("amount", 0.0),
                        row.get("exchange", "SH"),
                    )
                )

            # 批量插入
            cursor.executemany(insert_sql, records)
            return True

        except Exception as e:
            logger.error(f"插入Tick数据失败: {e}")
            return False

    def _insert_minute_kline(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
        """插入分钟K线数据"""
        try:
            # 构建K线数据插入语句
            insert_sql = f"""
                INSERT INTO {table_name} (ts, symbol, open, high, low, close, volume, amount, frequency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # 准备数据
            records = []
            for _, row in data.iterrows():
                records.append(
                    (
                        row.get("ts", datetime.now()),
                        row.get("symbol", ""),
                        row.get("open", 0.0),
                        row.get("high", 0.0),
                        row.get("low", 0.0),
                        row.get("close", 0.0),
                        row.get("volume", 0),
                        row.get("amount", 0.0),
                        row.get("frequency", "1m"),
                    )
                )

            # 批量插入
            cursor.executemany(insert_sql, records)
            return True

        except Exception as e:
            logger.error(f"插入分钟K线数据失败: {e}")
            return False

    def _insert_generic_timeseries(
        self, cursor, data: pd.DataFrame, table_name: str
    ) -> bool:
        """插入通用时序数据"""
        try:
            # 动态构建插入语句
            columns = list(data.columns)
            placeholders = ", ".join(["?" for _ in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            # 准备数据
            records = data.values.tolist()

            # 批量插入
            cursor.executemany(insert_sql, records)
            return True

        except Exception as e:
            logger.error(f"插入通用时序数据失败: {e}")
            return False

    def _build_timeseries_query(
        self,
        classification: DataClassification,
        table_name: str,
        filters: Dict = None,
        **kwargs,
    ) -> str:
        """构建时序数据查询语句"""
        base_query = f"SELECT * FROM {table_name}"

        conditions = []

        # 添加过滤条件
        if filters:
            for key, value in filters.items():
                if key == "symbol":
                    if isinstance(value, list):
                        symbols = "','".join(value)
                        conditions.append(f"symbol IN ('{symbols}')")
                    else:
                        conditions.append(f"symbol = '{value}'")
                elif key == "start_time":
                    conditions.append(f"ts >= '{value}'")
                elif key == "end_time":
                    conditions.append(f"ts <= '{value}'")
                elif key == "date_range":
                    if isinstance(value, dict) and "start" in value and "end" in value:
                        conditions.append(
                            f"ts >= '{value['start']}' AND ts <= '{value['end']}'"
                        )

        # 添加kwargs中的条件
        if "start_time" in kwargs:
            conditions.append(f"ts >= '{kwargs['start_time']}'")
        if "end_time" in kwargs:
            conditions.append(f"ts <= '{kwargs['end_time']}'")
        if "symbol" in kwargs:
            conditions.append(f"symbol = '{kwargs['symbol']}'")

        # 组装查询语句
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        # 添加排序
        base_query += " ORDER BY ts DESC"

        # 添加限制
        if "limit" in kwargs:
            base_query += f" LIMIT {kwargs['limit']}"

        return base_query


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
            DataManager().get_database_name(classification),
            "UPDATE",
        )

        try:
            database_name = DataManager().get_database_name(classification)
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
            DataManager().get_database_name(classification),
            "DELETE",
        )

        try:
            if not filters:
                logger.error("删除操作必须指定过滤条件")
                return False

            database_name = DataManager().get_database_name(classification)

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
                logger.info(
                    f"MySQL UPSERT完成: {actual_table_name}, 影响行数: {affected_rows}"
                )
            else:
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
            return True

        except Exception as e:
            self.monitoring_db.log_operation_result(operation_id, False, 0, str(e))
            logger.error(f"MySQL保存失败: {e}")
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
            query = self._build_reference_query(
                classification, actual_table_name, filters, **kwargs
            )
            conn = self.db_manager.get_connection(self.db_type, database_name)
            data = pd.read_sql(query, conn)

            self.monitoring_db.log_operation_result(operation_id, True, len(data))
            return data

        except Exception as e:
            self.monitoring_db.log_operation_result(operation_id, False, 0, str(e))
            logger.error(f"MySQL加载失败: {e}")
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
        return self.save_data(
            data, classification, table_name, mode="replace", **kwargs
        )

    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """删除MySQL数据"""
        logger.warning("MySQL删除操作需要谨慎使用")
        return False

    def _get_default_table_name(self, classification: DataClassification) -> str:
        """根据数据分类获取默认表名"""
        table_mapping = {
            DataClassification.SYMBOLS_INFO: "symbols",
            DataClassification.CONTRACT_INFO: "contracts",
            DataClassification.CONSTITUENT_INFO: "constituents",
            DataClassification.TRADE_CALENDAR: "trade_calendar",
            DataClassification.DATA_SOURCE_STATUS: "data_sources",
            DataClassification.TASK_SCHEDULES: "task_schedules",
            DataClassification.STRATEGY_PARAMETERS: "strategy_parameters",
            DataClassification.SYSTEM_CONFIG: "system_config",
        }
        return table_mapping.get(classification, "unknown_table")

    def _mysql_upsert_data(
        self,
        data: pd.DataFrame,
        table_name: str,
        conn,
        classification: DataClassification,
    ) -> int:
        """
        MySQL UPSERT操作 - 使用ON DUPLICATE KEY UPDATE实现

        Args:
            data: 要保存的数据
            table_name: 表名
            conn: MySQL连接
            classification: 数据分类

        Returns:
            int: 影响的行数
        """
        try:
            # DataStorageStrategy已移除
            import pymysql

            # 获取主键列
            key_columns = self._get_mysql_key_columns(classification)
            cursor = conn.cursor()

            # 构建列名和占位符
            columns = list(data.columns)
            placeholders = ", ".join(["%s"] * len(columns))
            column_names = ", ".join([f"`{col}`" for col in columns])

            # 构建ON DUPLICATE KEY UPDATE子句
            update_columns = [col for col in columns if col not in key_columns]
            update_set = ", ".join(
                [f"`{col}` = VALUES(`{col}`)" for col in update_columns]
            )

            # 构建完整的UPSERT SQL
            if update_set:
                upsert_sql = f"""
                INSERT INTO `{table_name}` ({column_names})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE
                    {update_set},
                    updated_at = CURRENT_TIMESTAMP
                """
            else:
                # 如果没有需要更新的列，使用IGNORE
                upsert_sql = f"""
                INSERT IGNORE INTO `{table_name}` ({column_names})
                VALUES ({placeholders})
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
            affected_rows = cursor.rowcount
            conn.commit()
            cursor.close()

            logger.info(
                f"MySQL UPSERT操作完成: {table_name}, 处理记录数: {len(records_to_insert)}, 影响行数: {affected_rows}"
            )
            return affected_rows

        except Exception as e:
            logger.error(f"MySQL UPSERT操作失败: {table_name}, 错误: {e}")
            conn.rollback()
            raise

    def _get_mysql_key_columns(self, classification: DataClassification) -> List[str]:
        """根据数据分类获取MySQL主键列"""
        key_mapping = {
            DataClassification.SYMBOLS_INFO: ["symbol"],
            DataClassification.CONTRACT_INFO: ["contract_code"],
            DataClassification.CONSTITUENT_INFO: ["symbol", "index_code"],
            DataClassification.TRADE_CALENDAR: ["exchange", "trade_date"],
            DataClassification.DATA_SOURCE_STATUS: ["source_name"],
            DataClassification.TASK_SCHEDULES: ["task_id"],
            DataClassification.STRATEGY_PARAMETERS: ["strategy_id", "param_name"],
            DataClassification.SYSTEM_CONFIG: ["config_key"],
        }
        return key_mapping.get(classification, ["id"])

    def _preprocess_reference_data(
        self, data: pd.DataFrame, classification: DataClassification
    ) -> pd.DataFrame:
        """预处理参考数据"""
        processed_data = data.copy()

        if "created_at" not in processed_data.columns:
            processed_data["created_at"] = datetime.now()
        if "updated_at" not in processed_data.columns:
            processed_data["updated_at"] = datetime.now()

        return processed_data

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

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        if "order_by" in kwargs:
            base_query += f" ORDER BY {kwargs['order_by']}"

        if "limit" in kwargs:
            base_query += f" LIMIT {kwargs['limit']}"

        return base_query


class RedisDataAccess:
    """Redis数据访问器 - 实时状态中心"""

    def __init__(self, monitoring_db: MonitoringDatabase):
        """
        初始化Redis数据访问器

        Args:
            monitoring_db: 监控数据库
        """
        self.monitoring_db = monitoring_db
        self.redis_client = None
        self._init_redis_connection()

    def _init_redis_connection(self):
        """初始化Redis连接"""
        try:
            import redis

            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "192.168.123.104"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                password=os.getenv("REDIS_PASSWORD", ""),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True,
            )

            self.redis_client.ping()
            logger.info("Redis连接成功")

        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise

    def save_realtime_data(
        self,
        classification: DataClassification,
        key: str,
        data: Union[Dict, pd.DataFrame],
        expire: int = 300,
    ) -> bool:
        """保存实时数据到Redis"""
        operation_id = self.monitoring_db.log_operation_start(key, "Redis", "0", "SET")

        try:
            if isinstance(data, pd.DataFrame):
                data_json = data.to_json(orient="records")
                self.redis_client.setex(key, expire, data_json)
            elif isinstance(data, dict):
                self.redis_client.hset(key, mapping=data)
                if expire:
                    self.redis_client.expire(key, expire)
            else:
                self.redis_client.setex(key, expire, str(data))

            self.monitoring_db.log_operation_result(operation_id, True, 1)
            return True

        except Exception as e:
            self.monitoring_db.log_operation_result(operation_id, False, 0, str(e))
            logger.error(f"Redis保存失败: {e}")
            return False

    def load_realtime_data(
        self, classification: DataClassification, key: str
    ) -> Optional[Any]:
        """从Redis加载实时数据"""
        operation_id = self.monitoring_db.log_operation_start(key, "Redis", "0", "GET")

        try:
            if self.redis_client.type(key) == "hash":
                data = self.redis_client.hgetall(key)
                self.monitoring_db.log_operation_result(operation_id, True, 1)
                return data
            else:
                data = self.redis_client.get(key)
                if data:
                    try:
                        import json

                        parsed_data = json.loads(data)
                        if isinstance(parsed_data, list):
                            data = pd.DataFrame(parsed_data)
                        else:
                            data = parsed_data
                    except json.JSONDecodeError:
                        pass

                self.monitoring_db.log_operation_result(
                    operation_id, True, 1 if data else 0
                )
                return data

        except Exception as e:
            self.monitoring_db.log_operation_result(operation_id, False, 0, str(e))
            logger.error(f"Redis加载失败: {e}")
            return None

    def cache_dataframe(self, key: str, df: pd.DataFrame, expire: int = 3600) -> bool:
        """缓存DataFrame到Redis"""
        return self.save_realtime_data(
            DataClassification.REALTIME_POSITIONS, key, df, expire
        )
