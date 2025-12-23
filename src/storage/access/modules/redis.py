#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - Redis数据访问器

专门处理Redis缓存和实时状态操作

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

import pandas as pd
import logging
import json
import os
from typing import Dict, List, Union, Any

from src.core import DataClassification
from src.monitoring.monitoring_database import MonitoringDatabase

logger = logging.getLogger("MyStocksRedisAccess")


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
                host=os.getenv("REDIS_HOST"),
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
            else:
                # 其他类型数据，转换为字符串
                data_str = str(data)
                self.redis_client.setex(key, expire, data_str)

            self.monitoring_db.log_operation_result(operation_id, True, 1)
            logger.info(f"Redis保存成功: {key}")

            return True

        except Exception as e:
            error_msg = f"Redis保存失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
            logger.error(error_msg)
            return False

    def load_realtime_data(
        self,
        classification: DataClassification,
        key: str,
        data_type: str = "dict",
    ) -> Union[Dict, List, pd.DataFrame, None]:
        """从Redis加载实时数据"""
        operation_id = self.monitoring_db.log_operation_start(key, "Redis", "0", "GET")

        try:
            # 判断数据类型
            if data_type == "dict":
                data = self.redis_client.hgetall(key)
            elif data_type == "list":
                data = self.redis_client.lrange(key, 0, -1)
            elif data_type == "json":
                # JSON数据，尝试转换为原始格式
                json_data = self.redis_client.get(key)
                if json_data:
                    data = json.loads(json_data)
                else:
                    data = None
            else:
                # 默认按字符串处理
                data = self.redis_client.get(key)

            self.monitoring_db.log_operation_result(operation_id, True, 1)
            logger.info(f"Redis加载成功: {key}")

            return data

        except Exception as e:
            error_msg = f"Redis加载失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
            logger.error(error_msg)
            return None

    def delete_realtime_data(self, key: str) -> bool:
        """从Redis删除数据"""
        operation_id = self.monitoring_db.log_operation_start(
            key, "Redis", "0", "DELETE"
        )

        try:
            self.redis_client.delete(key)

            self.monitoring_db.log_operation_result(operation_id, True, 1)
            logger.info(f"Redis删除成功: {key}")

            return True

        except Exception as e:
            error_msg = f"Redis删除失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
            logger.error(error_msg)
            return False

    def save_dataframe_as_json(
        self,
        classification: DataClassification,
        key: str,
        data: pd.DataFrame,
        expire: int = 300,
    ) -> bool:
        """将DataFrame保存为JSON格式到Redis"""
        try:
            # 转换DataFrame为JSON
            data_json = data.to_json(orient="records")

            # 保存到Redis
            self.redis_client.setex(key, expire, data_json)

            logger.info(f"DataFrame保存到Redis成功: {key}, {len(data)}行")

            return True

        except Exception as e:
            logger.error(f"DataFrame保存到Redis失败: {e}")
            return False

    def load_json_as_dataframe(
        self,
        classification: DataClassification,
        key: str,
    ) -> pd.DataFrame:
        """从Redis加载JSON数据为DataFrame"""
        try:
            # 从Redis获取JSON数据
            json_data = self.redis_client.get(key)

            if json_data:
                # 将JSON转换为DataFrame
                data = pd.read_json(json_data, orient="records")

                logger.info(f"从Redis加载DataFrame成功: {key}, {len(data)}行")

                return data
            else:
                logger.warning(f"Redis中找不到数据: {key}")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"从Redis加载DataFrame失败: {e}")
            return pd.DataFrame()

    def update_realtime_data(
        self,
        classification: DataClassification,
        key: str,
        data: Dict,
        expire: int = 300,
    ) -> bool:
        """更新Redis中的Hash数据"""
        try:
            # 将数据添加到Hash
            result = self.redis_client.hset(key, mapping=data)

            # 设置过期时间
            self.redis_client.expire(key, expire)

            logger.info(f"Redis Hash更新成功: {key}, {result}字段")

            return True

        except Exception as e:
            logger.error(f"Redis Hash更新失败: {e}")
            return False

    def get_realtime_data_keys(self, pattern: str = "*") -> List[str]:
        """获取符合模式的键名列表"""
        try:
            # 使用模式匹配获取键
            keys = self.redis_client.keys(pattern)

            logger.info(f"获取Redis键列表成功: {len(keys)}个键")

            return keys

        except Exception as e:
            logger.error(f"获取Redis键列表失败: {e}")
            return []

    def clear_realtime_data(self, pattern: str = "*") -> int:
        """根据模式清理Redis中的数据"""
        try:
            # 获取匹配的键
            keys = self.redis_client.keys(pattern)

            if keys:
                # 删除匹配的键
                count = self.redis_client.delete(*keys)

                logger.info(f"清理Redis数据成功: {count}个键")

                return count
            else:
                logger.info("没有找到匹配的数据")
                return 0

        except Exception as e:
            logger.error(f"清理Redis数据失败: {e}")
            return 0

    def cache_data(
        self,
        classification: DataClassification,
        key: str,
        data: Union[Dict, List, pd.DataFrame],
        expire: int = 3600,
    ) -> bool:
        """通用数据缓存方法"""
        return self.save_realtime_data(classification, key, data, expire)

    def get_cached_data(
        self,
        classification: DataClassification,
        key: str,
        expected_type: str = "dict",
    ) -> Union[Dict, List, pd.DataFrame, None]:
        """通用数据获取方法"""
        return self.load_realtime_data(classification, key, expected_type)

    def cache_df_for_quick_access(
        self,
        classification: DataClassification,
        symbol: str,
        data: pd.DataFrame,
        expire: int = 300,
    ) -> bool:
        """为快速访问缓存DataFrame"""
        key = f"{classification.value}:{symbol}"
        return self.save_dataframe_as_json(classification, key, data, expire)

    def get_cached_df_for_symbol(
        self,
        classification: DataClassification,
        symbol: str,
    ) -> pd.DataFrame:
        """获取缓存的DataFrame"""
        key = f"{classification.value}:{symbol}"
        return self.load_json_as_dataframe(classification, key)

    def cache_result_for_computation(
        self,
        classification: DataClassification,
        operation: str,
        params: Dict,
        data: Any,
        expire: int = 3600,
    ) -> bool:
        """缓存计算结果"""
        # 生成键
        key_parts = [f"{classification.value}:{operation}"]

        # 添加参数信息到键中
        for k, v in sorted(params.items()):
            key_parts.append(f"{k}={str(v)}")

        key = ":".join(key_parts)

        return self.save_realtime_data(classification, key, data, expire)

    def get_cached_result_for_computation(
        self,
        classification: DataClassification,
        operation: str,
        params: Dict,
        expected_type: str = "dict",
    ) -> Any:
        """获取缓存的计算结果"""
        # 生成键
        key_parts = [f"{classification.value}:{operation}"]

        # 添加参数信息到键中
        for k, v in sorted(params.items()):
            key_parts.append(f"{k}={str(v)}")

        key = ":".join(key_parts)

        return self.load_realtime_data(classification, key, expected_type)
