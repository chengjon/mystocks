"""
数据库事务服务

管理数据库事务、提交、回滚和批量操作
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager

from .connection_service import ConnectionService


logger = logging.getLogger(__name__)


class TransactionService:
    def __init__(self, connection_service: ConnectionService):
        self.connection_service = connection_service
        self.is_in_transaction = False
        self.transaction_id = None

        logger.info("TransactionService initialized")

    @contextmanager
    def begin_transaction(self):
        try:
            if not self.connection_service.check_connection():
                raise RuntimeError("数据库连接不可用")

            with self.connection_service.get_connection() as conn:
                conn.autocommit = False
                self.transaction_id = datetime.now().isoformat()
                logger.info(f"事务开始: {self.transaction_id}")
                yield conn

            self.is_in_transaction = True

        except Exception as e:
            logger.error(f"事务开始失败: {e}")
            raise

    def commit_transaction(self):
        if not self.is_in_transaction:
            raise RuntimeError("没有活动的事务")

        try:
            self.is_in_transaction = False
            logger.info(f"事务已提交: {self.transaction_id}")
            self.transaction_id = None
        except Exception as e:
            logger.error(f"事务提交失败: {e}")
            raise

    def rollback_transaction(self):
        if not self.is_in_transaction:
            raise RuntimeError("没有活动的事务")

        try:
            self.is_in_transaction = False
            logger.warning(f"事务已回滚: {self.transaction_id}")
            self.transaction_id = None
        except Exception as e:
            logger.error(f"事务回滚失败: {e}")
            raise

    def execute_in_transaction(self, operation: callable, *args, **kwargs) -> Any:
        with self.begin_transaction():
            try:
                result = operation(*args, **kwargs)
                self.commit_transaction()
                return result
            except Exception as e:
                self.rollback_transaction()
                raise

    def execute_sql(self, sql: str, params: Optional[List[Any]] = None, auto_commit: bool = True) -> List[Dict]:
        try:
            with self.connection_service.get_connection() as conn:
                cursor = conn.cursor()

                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

                if auto_commit:
                    conn.commit()

                return cursor.fetchall()
        except Exception as e:
            logger.error(f"SQL执行失败: {e}")
            raise

    def execute_update(self, table_name: str, update_data: Dict[str, Any], where_clause: Optional[str] = None) -> int:
        try:
            set_clause = ", ".join([f"{k} = %s" for k in update_data.keys()])
            sql = f"UPDATE {table_name} SET {set_clause}"

            if where_clause:
                sql += f" WHERE {where_clause}"

            params = list(update_data.values())
            rows_affected = self.execute_sql(sql, params, auto_commit=True)

            logger.info(f"更新{len(rows_affected)} 行")
            return rows_affected

        except Exception as e:
            logger.error(f"更新执行失败: {e}")
            raise

    def execute_insert(self, table_name: str, insert_data: Dict[str, Any] or List[Dict[str, Any]]) -> int:
        try:
            if isinstance(insert_data, dict):
                insert_data = [insert_data]

            columns = list(insert_data[0].keys())
            values_list = [", ".join([f"'{v}'" for v in row.values()]) for row in insert_data]

            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"
            params = ", ".join(values_list)

            rows_affected = self.execute_sql(sql, [params], auto_commit=True)

            logger.info(f"插入{len(rows_affected)} 行")
            return rows_affected

        except Exception as e:
            logger.error(f"插入执行失败: {e}")
            raise

    def get_transaction_status(self) -> Dict[str, Any]:
        return {
            "is_in_transaction": self.is_in_transaction,
            "transaction_id": self.transaction_id,
            "connection_available": self.connection_service.check_connection(),
        }
