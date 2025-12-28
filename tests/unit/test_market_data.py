"""Unit tests for MyStocks."""

import pytest
from src.data_access.tdengine_access import TDengineDataAccess
from src.data_access.postgresql_access import PostgreSQLDataAccess
from src.core.config_driven_table_manager import ConfigDrivenTableManager
from src.core.data_classification import DataClassification
from src.core.unified_manager import MyStocksUnifiedManager
from src.storage.database.connection_manager import DatabaseConnectionManager


# Test data
class TestMarketData:
    def test_symbol_info_storage(self):
        """测试股票信息存储和检索"""
        manager = MyStocksUnifiedManager()
        symbols_data = [
            {"symbol": "600000", "name": "浦发银行", "exchange": "SH", "sector": "银行"},
            {"symbol": "000001", "name": "平安银行", "exchange": "SZ", "sector": "银行"},
        ]

        # Save symbols
        from src.core import DataClassification

        result = manager.save_data_by_classification(symbols_data, DataClassification.SYMBOLS_INFO)
        assert result, "股票信息保存失败"

        # Retrieve symbols
        loaded = manager.load_data_by_classification(DataClassification.SYMBOLS_INFO, filters={"symbol": "600000"})
        assert loaded is not None and len(loaded) > 0
        assert loaded[0]["symbol"] == "600000"
        print("✓ 股票信息存储和检索测试通过")
