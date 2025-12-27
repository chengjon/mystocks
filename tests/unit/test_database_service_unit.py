"""
单元测试：Mock函数单元测试（快速验证）
测试文件：tests/unit/test_database_service_unit.py
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.database.database_service import DatabaseService


class TestDatabaseServiceUnit:
    """数据库服务单元测试类"""

    @pytest.fixture(autouse=True)
    def setup_with_mock(self):
        """使用fixture设置测试环境确保mock正确应用"""
        self.mock_postgresql_access = MagicMock()
        with patch("src.database.database_service.PostgreSQLDataAccess") as MockPostgreSQLAccess:
            MockPostgreSQLAccess.return_value = self.mock_postgresql_access
            self.db_service = DatabaseService()
            # 确保mock被注入
            self.db_service.postgresql_access = self.mock_postgresql_access
            yield

    def test_get_stock_list_empty_params(self):
        """测试获取股票列表 - 空参数"""
        # 模拟数据库返回空DataFrame
        mock_df_empty = pd.DataFrame(columns=["symbol", "name", "industry", "area", "market", "list_date"])
        mock_total_df = pd.DataFrame({"total": [0]})

        def side_effect(table_name, **kwargs):
            columns = kwargs.get("columns", [])
            if columns and len(columns) > 0 and "COUNT(*)" in str(columns[0]):
                return mock_total_df
            return mock_df_empty

        self.mock_postgresql_access.query.side_effect = side_effect

        result = self.db_service.get_stock_list()
        assert result == []

    def test_get_stock_list_with_data(self):
        """测试获取股票列表 - 有数据"""
        # 模拟数据库返回
        mock_df = pd.DataFrame(
            {
                "symbol": ["000001", "600000"],
                "name": ["平安银行", "浦发银行"],
                "industry": ["银行", "银行"],
                "area": ["深圳", "上海"],
                "market": ["深交所", "上交所"],
                "list_date": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-02")],
            }
        )

        # 模拟总数量查询
        mock_total_df = pd.DataFrame({"total": [2]})

        def side_effect(table_name, **kwargs):
            columns = kwargs.get("columns", [])
            # 检查是否是统计查询
            if columns and len(columns) > 0 and "COUNT(*)" in str(columns[0]):
                return mock_total_df
            else:
                return mock_df

        self.mock_postgresql_access.query.side_effect = side_effect

        result = self.db_service.get_stock_list({"limit": 20, "offset": 0})

        assert len(result) == 2
        assert result[0]["symbol"] == "000001"
        assert result[0]["name"] == "平安银行"
        assert result[0]["market"] == "深交所"
        assert result[0]["total"] == 2  # 每个结果都应该包含总数

    def test_get_stock_detail_empty_code(self):
        """测试获取股票详情 - 空股票代码"""
        result = self.db_service.get_stock_detail("")
        assert result == {}

    def test_get_technical_indicators_empty_symbol(self):
        """测试获取技术指标 - 空股票代码"""
        # get_technical_indicators接受Dict参数，空symbol时返回空列表
        result = self.db_service.get_technical_indicators({"symbol": ""})
        assert result == []
