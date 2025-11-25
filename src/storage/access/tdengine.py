#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - TDengine数据访问器

专门处理TDengine数据库的高频时序数据操作

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple, Any
import logging
import uuid

# 导入基础模块
from src.storage.access.base import (
    IDataAccessLayer, 
    get_database_name_from_classification,
    normalize_dataframe,
    validate_time_series_data,
    DataClassification
)
from src.monitoring.monitoring_database import MonitoringDatabase

# 导入数据库管理器
from src.storage.database.database_manager import DatabaseTableManager, DatabaseType

logger = logging.getLogger("MyStocksTDengineAccess")


class TDengineDataAccess(IDataAccessLayer):
    """TDengine数据访问器 - 高频时序数据专用"""

    def __init__(self, monitoring_db: MonitoringDatabase):
        """
        初始化TDengine数据访问器
        
        Args:
            monitoring_db: 监控数据库实例
        """
        super().__init__(monitoring_db)
        self.db_manager = DatabaseTableManager()
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
            get_database_name_from_classification(classification),
            "upsert_data",
        )

        try:
            # 确定表名
            actual_table_name = table_name or self._get_default_table_name(
                classification
            )
            database_name = get_database_name_from_classification(classification)

            # 数据预处理
            processed_data = self._preprocess_timeseries_data(data, classification)

            # 获取去重策略
            dedup_strategy = kwargs.get("dedup_strategy")
            if not dedup_strategy:
                # 简化版：使用默认去重策略
                dedup_strategy = "latest_wins"  # 最新数据覆盖旧数据

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
                    f"TDengine保存成功: {actual_table_name}, {len(final_data)}条记录，去重策略: {dedup_strategy}"
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
            get_database_name_from_classification(classification),
            "SELECT",
        )

        try:
            database_name = get_database_name_from_classification(classification)

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
            # 由于简化后的策略是字符串，我们直接实现字符串判断逻辑
            if strategy == "latest_wins":
                return self._handle_tdengine_latest_wins(
                    data, table_name, classification
                )
            elif strategy == "first_wins":
                return self._handle_tdengine_first_wins(
                    data, table_name, classification
                )
            elif strategy == "merge":
                return self._handle_tdengine_merge(data, table_name, classification)
            elif strategy == "reject":
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
            database_name = get_database_name_from_classification(classification)
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
        processed_data = normalize_dataframe(data)

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