#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问财数据服务

业务逻辑层：
  1. 数据获取和清理
  2. 去重和存储
  3. 查询结果管理
  4. 历史数据统计

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from sqlalchemy import exc as sqlalchemy_exc

from app.adapters.wencai_adapter import WencaiDataSource
from app.models.wencai_data import WencaiQuery
from app.core.database import get_mysql_engine
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 表名白名单 - 防止 SQL 注入
ALLOWED_QUERY_TABLES = {
    "qs_1": "wencai_qs_1",
    "qs_2": "wencai_qs_2",
    "qs_3": "wencai_qs_3",
    "qs_4": "wencai_qs_4",
    "qs_5": "wencai_qs_5",
    "qs_6": "wencai_qs_6",
    "qs_7": "wencai_qs_7",
    "qs_8": "wencai_qs_8",
    "qs_9": "wencai_qs_9",
}


class WencaiService:
    """
    问财数据服务

    提供问财数据的完整业务逻辑
    """

    def __init__(self, db: Session = None):
        """
        初始化服务

        Args:
            db: 数据库会话（可选，用于ORM操作）
        """
        self.db = db
        self.adapter = WencaiDataSource(
            timeout=getattr(settings, "WENCAI_TIMEOUT", 30),
            retry_count=getattr(settings, "WENCAI_RETRY_COUNT", 3),
        )
        # 复用全局 MySQL 引擎，避免每次请求创建新的连接池
        self.engine = get_mysql_engine()
        logger.info("WencaiService initialized")

    @staticmethod
    def _get_safe_table_name(query_name: str) -> str:
        """
        从白名单获取安全的表名，防止 SQL 注入

        Args:
            query_name: 查询名称（如 'qs_1'）

        Returns:
            安全的表名

        Raises:
            ValueError: 如果 query_name 不在白名单中
        """
        table_name = ALLOWED_QUERY_TABLES.get(query_name)
        if not table_name:
            raise ValueError(
                f"Invalid query_name: {query_name}. Must be one of {list(ALLOWED_QUERY_TABLES.keys())}"
            )
        return table_name

    def get_all_queries(self) -> List[Dict[str, Any]]:
        """
        获取所有查询列表

        Returns:
            查询信息列表
        """
        try:
            queries = self.db.query(WencaiQuery).all()
            return [q.to_dict() for q in queries]
        except Exception as e:
            logger.error(f"Failed to get queries: {str(e)}")
            raise

    def get_query_by_name(self, query_name: str) -> Optional[Dict[str, Any]]:
        """
        根据名称获取查询

        Args:
            query_name: 查询名称

        Returns:
            查询信息，不存在返回None
        """
        try:
            query = (
                self.db.query(WencaiQuery)
                .filter(WencaiQuery.query_name == query_name)
                .first()
            )
            return query.to_dict() if query else None
        except Exception as e:
            logger.error(f"Failed to get query {query_name}: {str(e)}")
            return None

    def fetch_and_save(self, query_name: str, pages: int = 1) -> Dict[str, Any]:
        """
        获取并保存查询结果（核心方法）

        Args:
            query_name: 查询名称
            pages: 获取页数

        Returns:
            执行结果统计

        Raises:
            ValueError: 查询不存在或参数无效
            Exception: 数据获取或保存失败
        """
        logger.info(f"=== Starting fetch_and_save: {query_name}, pages={pages} ===")

        # 1. 验证查询是否存在
        query_info = self.get_query_by_name(query_name)
        if not query_info:
            raise ValueError(f"Query '{query_name}' not found")

        if not query_info.get("is_active"):
            raise ValueError(f"Query '{query_name}' is not active")

        query_text = query_info.get("query_text")
        logger.info(f"Query text: {query_text}")

        # 2. 调用适配器获取数据
        try:
            raw_data = self.adapter.fetch_data(query_text, pages)
            if raw_data.empty:
                logger.warning("No data fetched from Wencai API")
                return {
                    "success": False,
                    "message": "未获取到数据",
                    "total_records": 0,
                    "new_records": 0,
                    "duplicate_records": 0,
                }

            logger.info(f"Fetched {len(raw_data)} records from Wencai")

        except Exception as e:
            logger.error(f"Failed to fetch data: {str(e)}", exc_info=True)
            raise

        # 3. 清理数据
        try:
            cleaned_data = self.adapter.clean_data(raw_data)
            logger.info(f"Data cleaned: {len(cleaned_data)} rows")
        except Exception as e:
            logger.error(f"Failed to clean data: {str(e)}", exc_info=True)
            raise

        # 4. 去重并保存
        try:
            save_result = self._save_to_database(cleaned_data, query_name)
            logger.info(f"Save result: {save_result}")

            return {
                "success": True,
                "message": "数据获取成功",
                "query_name": query_name,
                "total_records": len(cleaned_data),
                "new_records": save_result["new_records"],
                "duplicate_records": save_result["duplicate_records"],
                "table_name": save_result["table_name"],
                "fetch_time": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Failed to save data: {str(e)}", exc_info=True)
            raise

    def _save_to_database(self, data: pd.DataFrame, query_name: str) -> Dict[str, Any]:
        """
        保存数据到MySQL并去重

        Args:
            data: 清理后的数据
            query_name: 查询名称

        Returns:
            保存结果统计
        """
        # 使用白名单获取安全的表名
        table_name = self._get_safe_table_name(query_name)
        logger.info(f"Saving to table: {table_name}")

        # 使用复用的 MySQL 引擎
        inspector = inspect(self.engine)

        try:
            # 查重逻辑
            if inspector.has_table(table_name):
                logger.info(f"Table {table_name} exists, checking for duplicates...")

                try:
                    # 读取现有数据（排除fetch_time列）
                    existing_data = pd.read_sql_table(table_name, self.engine)
                    existing_data = existing_data.drop(
                        columns=["fetch_time"], errors="ignore"
                    )

                    # 准备新数据（排除fetch_time列进行比较）
                    new_data = data.drop(columns=["fetch_time"], errors="ignore")

                    # 找出唯一记录
                    merged = pd.merge(
                        new_data, existing_data, how="left", indicator=True
                    )
                    unique_rows = merged["_merge"] == "left_only"
                    data_to_save = data[unique_rows].copy()

                    duplicate_count = len(data) - len(data_to_save)
                    logger.info(
                        f"Deduplication: {len(data)} total, "
                        f"{len(data_to_save)} new, {duplicate_count} duplicates"
                    )

                except Exception as e:
                    logger.warning(f"Deduplication failed: {str(e)}, saving all data")
                    data_to_save = data.copy()
                    duplicate_count = 0
            else:
                logger.info(f"Table {table_name} does not exist, creating...")
                data_to_save = data.copy()
                duplicate_count = 0

            # 保存数据
            if not data_to_save.empty:
                data_to_save.to_sql(
                    name=table_name,
                    con=self.engine,
                    if_exists="append",
                    index=False,
                    chunksize=1000,
                )
                logger.info(f"✅ Saved {len(data_to_save)} records to {table_name}")
            else:
                logger.info("⚠️ No new records to save")

            return {
                "table_name": table_name,
                "new_records": len(data_to_save),
                "duplicate_records": duplicate_count,
            }

        except sqlalchemy_exc.SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while saving: {str(e)}")
            raise

    def get_query_results(
        self, query_name: str, limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取查询结果

        Args:
            query_name: 查询名称
            limit: 返回条数
            offset: 偏移量

        Returns:
            查询结果
        """
        # 使用白名单获取安全的表名
        table_name = self._get_safe_table_name(query_name)
        logger.info(
            f"Getting results from {table_name}, limit={limit}, offset={offset}"
        )

        try:
            inspector = inspect(self.engine)
            if not inspector.has_table(table_name):
                return {
                    "query_name": query_name,
                    "total": 0,
                    "results": [],
                    "columns": [],
                    "message": "Table does not exist yet",
                }

            # 查询总数
            with self.engine.connect() as conn:
                count_query = text(f"SELECT COUNT(*) as cnt FROM {table_name}")
                total = conn.execute(count_query).scalar()

                # 查询数据（按fetch_time降序）
                data_query = text(
                    f"SELECT * FROM {table_name} "
                    f"ORDER BY fetch_time DESC "
                    f"LIMIT :limit OFFSET :offset"
                )
                result = conn.execute(data_query, {"limit": limit, "offset": offset})

                # 转换为字典列表
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result]

                # 获取最新fetch_time
                latest_query = text(
                    f"SELECT MAX(fetch_time) as latest FROM {table_name}"
                )
                latest_fetch_time = conn.execute(latest_query).scalar()

            return {
                "query_name": query_name,
                "total": total,
                "results": rows,
                "columns": list(columns),
                "latest_fetch_time": latest_fetch_time,
            }

        except Exception as e:
            logger.error(f"Failed to get results: {str(e)}")
            raise

    def get_query_history(self, query_name: str, days: int = 7) -> Dict[str, Any]:
        """
        获取查询历史统计

        Args:
            query_name: 查询名称
            days: 查询天数

        Returns:
            历史统计数据
        """
        # 使用白名单获取安全的表名
        table_name = self._get_safe_table_name(query_name)
        logger.info(f"Getting history for {table_name}, days={days}")

        try:
            inspector = inspect(self.engine)
            if not inspector.has_table(table_name):
                return {
                    "query_name": query_name,
                    "date_range": [],
                    "history": [],
                    "total_days": 0,
                }

            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            with self.engine.connect() as conn:
                # 按日期统计
                history_query = text(
                    f"""
                    SELECT
                        DATE(fetch_time) as date,
                        COUNT(*) as total_records,
                        COUNT(DISTINCT fetch_time) as fetch_count
                    FROM {table_name}
                    WHERE fetch_time >= :start_date
                    GROUP BY DATE(fetch_time)
                    ORDER BY date DESC
                    """
                )
                result = conn.execute(history_query, {"start_date": start_date})

                history = []
                for row in result:
                    history.append(
                        {
                            "date": row.date.strftime("%Y-%m-%d"),
                            "total_records": row.total_records,
                            "fetch_count": row.fetch_count,
                        }
                    )

            date_range = [
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            ]

            return {
                "query_name": query_name,
                "date_range": date_range,
                "history": history,
                "total_days": len(history),
            }

        except Exception as e:
            logger.error(f"Failed to get history: {str(e)}")
            raise

    def close(self):
        """关闭资源"""
        if hasattr(self, "adapter"):
            self.adapter.close()
        logger.info("WencaiService closed")


# 工厂函数
def get_wencai_service(db: Session = None) -> WencaiService:
    """
    获取WencaiService实例

    Args:
        db: 数据库会话

    Returns:
        WencaiService实例
    """
    return WencaiService(db=db)
