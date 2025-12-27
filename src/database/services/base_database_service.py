"""
# 功能：基础数据库服务
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：数据库服务的基础类和共享组件
"""

from abc import ABC
import logging
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime

# 导入数据访问层
from src.data_access import PostgreSQLDataAccess

logger = logging.getLogger(__name__)


class BaseDatabaseService(ABC):
    """
    基础数据库服务抽象类

    提供数据库服务的通用功能和接口
    """

    def __init__(self):
        """初始化基础数据库服务"""
        self.postgresql_access = PostgreSQLDataAccess()

    def _build_where_clause(self, filters: Dict[str, Union[str, List[str]]]) -> Optional[str]:
        """构建WHERE子句"""
        if not filters:
            return None

        conditions = []
        for key, value in filters.items():
            if isinstance(value, list):
                # 处理列表值（IN查询）
                if len(value) == 0:
                    continue
                placeholders = ",".join(["%s"] * len(value))
                conditions.append(f"{key} IN ({placeholders})")
            else:
                # 处理单个值
                conditions.append(f"{key} = %s")

        return " AND ".join(conditions)

    def _get_filter_params(self, filters: Dict[str, Union[str, List[str]]]) -> List:
        """获取过滤参数列表"""
        params = []
        for value in filters.values():
            if isinstance(value, list):
                params.extend(value)
            else:
                params.append(value)
        return params

    def _execute_query(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        filters: Optional[Dict[str, Union[str, List[str]]]] = None,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> pd.DataFrame:
        """执行查询的通用方法"""
        try:
            where_clause = self._build_where_clause(filters) if filters else None
            params = self._get_filter_params(filters) if filters else None

            if params:
                df = self.postgresql_access.query(
                    table_name=table_name,
                    columns=columns,
                    where=where_clause,
                    limit=limit,
                    order_by=order_by,
                )
            else:
                df = self.postgresql_access.query(
                    table_name=table_name,
                    columns=columns,
                    where=where_clause,
                    limit=limit,
                    order_by=order_by,
                )

            return df

        except Exception as e:
            logger.error(f"查询数据库失败: {e}")
            return pd.DataFrame()

    def _count_records(
        self,
        table_name: str,
        filters: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> int:
        """记录数量统计"""
        try:
            where_clause = self._build_where_clause(filters) if filters else None
            self._get_filter_params(filters) if filters else None

            df = self.postgresql_access.query(table_name=table_name, columns=["COUNT(*) as total"], where=where_clause)

            return df.iloc[0]["total"] if not df.empty else 0

        except Exception as e:
            logger.error(f"统计记录数量失败: {e}")
            return 0

    def _validate_pagination_params(self, limit: Optional[int], offset: Optional[int]) -> tuple:
        """验证分页参数"""
        limit = max(1, limit or 20)  # 最少1条
        limit = min(1000, limit)  # 最多1000条

        offset = max(0, offset or 0)  # 不小于0

        return limit, offset

    def _apply_pagination(self, df: pd.DataFrame, limit: int, offset: int) -> pd.DataFrame:
        """应用分页"""
        if offset >= len(df):
            return pd.DataFrame()

        end_index = offset + limit
        return df.iloc[offset:end_index].reset_index(drop=True)

    def _handle_database_error(self, error: Exception, operation: str) -> Dict:
        """处理数据库错误"""
        error_msg = f"{operation}失败: {str(error)}"
        logger.error(error_msg)

        return {
            "success": False,
            "error": error_msg,
            "data": None,
            "timestamp": datetime.now().isoformat(),
        }

    def _build_success_response(
        self, data: Union[List[Dict], Dict], operation: str, meta: Optional[Dict] = None
    ) -> Dict:
        """构建成功响应"""
        response = {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
        }

        if meta:
            response.update(meta)

        return response
