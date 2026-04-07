from typing import Dict, List, Optional

from .connection_service import ConnectionService
from .query_service import QueryService
from .transaction_service import TransactionService
from .migration_service import MigrationService


class DatabaseService:
    def __init__(self, database_url: str):
        self.connection_service = ConnectionService(database_url)
        self.query_service = QueryService(self.connection_service)
        self.transaction_service = TransactionService(self.connection_service)
        self.migration_service = MigrationService(self.connection_service)

    def get_stock_list(self, params: Optional[Dict] = None) -> List[Dict]:
        return self.query_service.get_stock_list(params)

    def get_stock_detail(self, stock_code: str) -> Dict:
        return self.query_service.get_stock_by_code(stock_code)

    def get_realtime_quotes(self, symbols: List[str]) -> List[Dict]:
        return self.query_service.batch_get_stocks(symbols)

    def execute_query(
        self,
        table_name: str,
        where: Optional[str] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        params: Optional[Dict] = None,
    ) -> List[Dict]:
        return self.query_service.execute_query(
            table_name=table_name, where_clause=where, columns=columns, limit=limit, offset=offset, params=params
        )

    def begin_transaction(self):
        return self.transaction_service.begin_transaction()

    def commit_transaction(self):
        return self.transaction_service.commit_transaction()

    def rollback_transaction(self):
        return self.transaction_service.rollback_transaction()

    def execute_transaction(self, operation, *args, **kwargs):
        return self.transaction_service.execute_in_transaction(operation, *args, **kwargs)

    def get_transaction_status(self) -> Dict:
        return self.transaction_service.get_transaction_status()

    def check_connection(self) -> Dict:
        return self.connection_service.check_connection()

    def get_connection_pool_stats(self) -> Dict:
        return self.connection_service.get_pool_stats()

    def execute_update(self, table_name: str, update_data: Dict, where: Optional[str] = None) -> int:
        return self.query_service.execute_update(table_name=table_name, update_data=update_data, where_clause=where)

    def execute_insert(self, table_name: str, insert_data: Dict) -> int:
        return self.query_service.execute_insert(table_name=table_name, insert_data=insert_data)

    def count_records(self, table_name: str, where: Optional[str] = None) -> int:
        return self.query_service.count_records(table_name, where)

    def get_migration_status(self) -> Dict:
        return self.migration_service.get_migration_status()

    def apply_migration(self, migration: Dict) -> Dict:
        return self.migration_service.apply_migration(migration)

    def get_migration_history(self, limit: int = 50) -> Dict:
        return self.migration_service.get_migration_history(limit)

    def check_migration_status(self, version: str) -> Dict:
        return self.migration_service.check_migration_status(version)
