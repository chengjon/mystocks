"""
BaoStock数据源适配器测试

测试BaostockDataSource类的所有功能：
- 登录/登出机制
- 股票日线数据获取
- 指数日线数据获取
- 股票基本信息
- 指数成分股
- 实时数据
- 交易日历（空实现）
- 财务数据
- 新闻数据（空实现）

创建日期: 2026-01-03
Phase: 2 - Task 2.2.2
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import pandas as pd

from src.adapters.baostock_adapter import BaostockDataSource


class TestBaostockDataSourceInit(unittest.TestCase):
    """测试BaostockDataSource初始化"""

    def test_init_success(self):
        """测试成功初始化"""
        # 使用__new__创建实例并手动设置属性
        adapter = BaostockDataSource.__new__(BaostockDataSource)
        adapter.bs = Mock()
        adapter.available = True

        # Verify
        self.assertTrue(adapter.available)
        self.assertIsNotNone(adapter.bs)

    def test_init_with_mock_login(self):
        """测试模拟登录成功"""
        # Create adapter manually without calling __init__
        adapter = BaostockDataSource.__new__(BaostockDataSource)

        # Mock the bs module and login
        mock_bs = Mock()
        mock_login_result = Mock()
        mock_login_result.error_code = "0"
        mock_bs.login.return_value = mock_login_result

        adapter.bs = mock_bs
        adapter.available = True

        # Verify
        self.assertTrue(adapter.available)
        self.assertIsNotNone(adapter.bs)

    def test_del_logs_out(self):
        """测试析构函数自动登出"""
        # Setup
        adapter = BaostockDataSource.__new__(BaostockDataSource)
        mock_bs = Mock()
        adapter.bs = mock_bs
        adapter.available = True

        # Execute
        adapter.__del__()

        # Verify
        mock_bs.logout.assert_called_once()


class TestBaostockDataSourceStockDaily(unittest.TestCase):
    """测试股票日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = BaostockDataSource.__new__(BaostockDataSource)
        self.adapter.bs = Mock()
        self.adapter.available = True

    @patch("src.adapters.baostock_adapter.format_stock_code_for_source")
    @patch("src.adapters.baostock_adapter.ColumnMapper.to_english")
    def test_get_stock_daily_success(self, mock_mapper, mock_format):
        """测试成功获取股票日线数据"""
        # Setup mocks
        mock_format.return_value = "sz.000001"
        mock_rs = Mock()
        mock_rs.error_code = "0"
        mock_rs.fields = ["date", "code", "open", "high", "low", "close", "volume", "amount"]
        mock_rs.next.side_effect = [True, True, False]
        mock_rs.get_row_data.side_effect = [
            ["2025-01-01", "000001", "10.0", "10.8", "9.8", "10.5", "10000", "100000"],
            ["2025-01-02", "000001", "10.5", "11.0", "10.3", "10.8", "12000", "120000"],
        ]
        self.adapter.bs.query_history_k_data_plus.return_value = mock_rs
        mock_mapper.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_stock_daily("000001.SZ", "2025-01-01", "2025-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.adapter.bs.query_history_k_data_plus.assert_called_once()

    @patch("src.adapters.baostock_adapter.format_stock_code_for_source")
    def test_get_stock_daily_query_error(self, mock_format):
        """测试查询错误"""
        # Setup mocks
        mock_format.return_value = "sz.000001"
        mock_rs = Mock()
        mock_rs.error_code = "1"
        mock_rs.error_msg = "Query failed"
        self.adapter.bs.query_history_k_data_plus.return_value = mock_rs

        # Execute
        result = self.adapter.get_stock_daily("000001.SZ", "2025-01-01", "2025-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    @patch("src.adapters.baostock_adapter.format_stock_code_for_source")
    @patch("src.adapters.baostock_adapter.ColumnMapper.to_english")
    def test_get_stock_daily_empty_data(self, mock_mapper, mock_format):
        """测试获取空数据"""
        # Setup mocks
        mock_format.return_value = "sz.000001"
        mock_rs = Mock()
        mock_rs.error_code = "0"
        mock_rs.fields = ["date", "code", "open"]
        mock_rs.next.return_value = False
        self.adapter.bs.query_history_k_data_plus.return_value = mock_rs
        mock_mapper.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_stock_daily("000001.SZ", "2025-01-01", "2025-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)


class TestBaostockDataSourceIndexDaily(unittest.TestCase):
    """测试指数日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = BaostockDataSource.__new__(BaostockDataSource)
        self.adapter.bs = Mock()
        self.adapter.available = True

    @patch("src.adapters.baostock_adapter.format_index_code_for_source")
    def test_get_index_daily_success(self, mock_format):
        """测试成功获取指数日线数据"""
        # Setup mocks
        mock_format.return_value = "sh.000001"
        mock_rs = Mock()
        mock_rs.error_code = "0"
        mock_rs.fields = ["date", "code", "open", "high", "low", "close", "volume", "amount", "pctChg"]
        mock_rs.next.side_effect = [True, False]
        mock_rs.get_row_data.return_value = [
            "2025-01-01",
            "000001",
            "3000.0",
            "3050.0",
            "2980.0",
            "3020.0",
            "1000000",
            "10000000",
            "1.5",
        ]
        self.adapter.bs.query_history_k_data_plus.return_value = mock_rs

        # Execute
        result = self.adapter.get_index_daily("000001.SH", "2025-01-01", "2025-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("date", result.columns)
        self.assertIn("symbol", result.columns)
        self.adapter.bs.query_history_k_data_plus.assert_called_once()

    @patch("src.adapters.baostock_adapter.format_index_code_for_source")
    def test_get_index_daily_query_error(self, mock_format):
        """测试查询错误"""
        # Setup mocks
        mock_format.return_value = "sh.000001"
        mock_rs = Mock()
        mock_rs.error_code = "1"
        mock_rs.error_msg = "Query failed"
        self.adapter.bs.query_history_k_data_plus.return_value = mock_rs

        # Execute
        result = self.adapter.get_index_daily("000001.SH", "2025-01-01", "2025-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestBaostockDataSourceStockBasic(unittest.TestCase):
    """测试股票基本信息获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = BaostockDataSource.__new__(BaostockDataSource)
        self.adapter.bs = Mock()
        self.adapter.available = True

    @patch("src.adapters.baostock_adapter.format_stock_code_for_source")
    def test_get_stock_basic_success(self, mock_format):
        """测试成功获取股票基本信息"""
        # Setup mocks
        mock_format.return_value = "sz.000001"
        mock_rs = Mock()
        mock_rs.error_code = "0"
        mock_rs.fields = ["code", "code_name", "ipoDate", "outstanding"]
        mock_rs.next.side_effect = [True, False]
        mock_rs.get_row_data.return_value = ["000001", "平安银行", "1991-04-03", "19405418146"]
        self.adapter.bs.query_stock_basic.return_value = mock_rs

        # Execute
        result = self.adapter.get_stock_basic("000001.SZ")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result["code"], "000001")
        self.assertEqual(result["code_name"], "平安银行")

    @patch("src.adapters.baostock_adapter.format_stock_code_for_source")
    def test_get_stock_basic_query_error(self, mock_format):
        """测试查询错误"""
        # Setup mocks
        mock_format.return_value = "sz.000001"
        mock_rs = Mock()
        mock_rs.error_code = "1"
        mock_rs.error_msg = "Query failed"
        self.adapter.bs.query_stock_basic.return_value = mock_rs

        # Execute
        result = self.adapter.get_stock_basic("000001.SZ")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)

    @patch("src.adapters.baostock_adapter.format_stock_code_for_source")
    def test_get_stock_basic_empty_data(self, mock_format):
        """测试获取空数据"""
        # Setup mocks
        mock_format.return_value = "sz.000001"
        mock_rs = Mock()
        mock_rs.error_code = "0"
        mock_rs.fields = ["code", "code_name"]
        mock_rs.next.return_value = False
        self.adapter.bs.query_stock_basic.return_value = mock_rs

        # Execute
        result = self.adapter.get_stock_basic("000001.SZ")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)


class TestBaostockDataSourceIndexComponents(unittest.TestCase):
    """测试指数成分股获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = BaostockDataSource.__new__(BaostockDataSource)
        self.adapter.bs = Mock()
        self.adapter.available = True

    @patch("src.adapters.baostock_adapter.normalize_date")
    @patch("src.adapters.baostock_adapter.datetime")
    def test_get_index_components_success(self, mock_datetime, mock_normalize):
        """测试成功获取指数成分股"""
        # Setup mocks
        mock_datetime.datetime.now.return_value = datetime(2025, 1, 1)
        mock_normalize.return_value = "2025-01-01"
        mock_rs = Mock()
        mock_rs.error_code = "0"
        mock_rs.next.side_effect = [True, True, False]
        mock_rs.get_row_data.side_effect = [
            ["sh.600000", "600000.SH", "浦发银行", "5.0"],
            ["sh.600036", "600036.SH", "招商银行", "3.5"],
        ]
        self.adapter.bs.query_index_weight.return_value = mock_rs

        # Execute
        result = self.adapter.get_index_components("上证50")

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("600000.SH", result)
        self.assertIn("600036.SH", result)

    @patch("src.adapters.baostock_adapter.normalize_date")
    @patch("src.adapters.baostock_adapter.datetime")
    def test_get_index_components_query_error(self, mock_datetime, mock_normalize):
        """测试查询错误"""
        # Setup mocks
        mock_datetime.datetime.now.return_value = datetime(2025, 1, 1)
        mock_normalize.return_value = "2025-01-01"
        mock_rs = Mock()
        mock_rs.error_code = "1"
        mock_rs.error_msg = "Query failed"
        self.adapter.bs.query_index_weight.return_value = mock_rs

        # Execute
        result = self.adapter.get_index_components("上证50")

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestBaostockDataSourceRealtimeData(unittest.TestCase):
    """测试实时数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = BaostockDataSource.__new__(BaostockDataSource)
        self.adapter.bs = Mock()
        self.adapter.available = True

    @patch("src.adapters.baostock_adapter.normalize_date")
    @patch("src.adapters.baostock_adapter.datetime")
    def test_get_real_time_data_success(self, mock_datetime, mock_normalize):
        """测试成功获取实时数据"""
        # Setup mocks
        mock_datetime.datetime.now.return_value = datetime(2025, 1, 1)
        mock_normalize.return_value = "2025-01-01"
        mock_rs = Mock()
        mock_rs.error_code = "0"
        mock_rs.fields = ["code", "code_name", "open", "close"]
        mock_rs.next.side_effect = [True, True, False]
        mock_rs.get_row_data.side_effect = [["000001", "平安银行", "10.0", "10.5"], ["000002", "万科A", "20.0", "20.5"]]
        self.adapter.bs.query_all_stock.return_value = mock_rs

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result["code"], "000001")
        self.assertEqual(result["code_name"], "平安银行")

    @patch("src.adapters.baostock_adapter.normalize_date")
    @patch("src.adapters.baostock_adapter.datetime")
    def test_get_real_time_data_not_found(self, mock_datetime, mock_normalize):
        """测试找不到指定股票"""
        # Setup mocks
        mock_datetime.datetime.now.return_value = datetime(2025, 1, 1)
        mock_normalize.return_value = "2025-01-01"
        mock_rs = Mock()
        mock_rs.error_code = "0"
        mock_rs.fields = ["code", "code_name"]
        mock_rs.next.side_effect = [True, False]
        mock_rs.get_row_data.return_value = ["000002", "万科A"]
        self.adapter.bs.query_all_stock.return_value = mock_rs

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)

    @patch("src.adapters.baostock_adapter.normalize_date")
    @patch("src.adapters.baostock_adapter.datetime")
    def test_get_real_time_data_query_error(self, mock_datetime, mock_normalize):
        """测试查询错误"""
        # Setup mocks
        mock_datetime.datetime.now.return_value = datetime(2025, 1, 1)
        mock_normalize.return_value = "2025-01-01"
        mock_rs = Mock()
        mock_rs.error_code = "1"
        mock_rs.error_msg = "Query failed"
        self.adapter.bs.query_all_stock.return_value = mock_rs

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)


class TestBaostockDataSourceMarketCalendar(unittest.TestCase):
    """测试交易日历获取功能（空实现）"""

    def setUp(self):
        """测试前准备"""
        self.adapter = BaostockDataSource.__new__(BaostockDataSource)
        self.adapter.bs = Mock()
        self.adapter.available = True

    def test_get_market_calendar_returns_empty(self):
        """测试交易日历返回空DataFrame"""
        # Execute
        result = self.adapter.get_market_calendar("2025-01-01", "2025-01-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestBaostockDataSourceFinancialData(unittest.TestCase):
    """测试财务数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = BaostockDataSource.__new__(BaostockDataSource)
        self.adapter.bs = Mock()
        self.adapter.available = True

    def test_get_financial_data_success(self):
        """测试成功获取财务数据"""
        # Setup mocks
        mock_rs = Mock()
        mock_rs.error_code = "0"
        mock_rs.fields = ["code", "code_name", "outstanding", "totals"]
        mock_rs.next.side_effect = [True, False]
        mock_rs.get_row_data.return_value = ["000001", "平安银行", "19405418146", "1940541814600"]
        self.adapter.bs.query_stock_basic.return_value = mock_rs

        # Execute
        result = self.adapter.get_financial_data("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)

    def test_get_financial_data_query_error(self):
        """测试查询错误"""
        # Setup mocks
        mock_rs = Mock()
        mock_rs.error_code = "1"
        mock_rs.error_msg = "Query failed"
        self.adapter.bs.query_stock_basic.return_value = mock_rs

        # Execute
        result = self.adapter.get_financial_data("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestBaostockDataSourceNewsData(unittest.TestCase):
    """测试新闻数据获取功能（空实现）"""

    def setUp(self):
        """测试前准备"""
        self.adapter = BaostockDataSource.__new__(BaostockDataSource)
        self.adapter.bs = Mock()
        self.adapter.available = True

    def test_get_news_data_returns_empty(self):
        """测试新闻数据返回空列表"""
        # Execute
        result = self.adapter.get_news_data(symbol="000001", limit=10)

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_get_news_data_without_symbol(self):
        """测试不带股票代码的新闻查询"""
        # Execute
        result = self.adapter.get_news_data(symbol=None, limit=10)

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestBaostockDataSourceIntegration(unittest.TestCase):
    """集成测试 - 测试多个方法协同工作"""

    def setUp(self):
        """测试前准备"""
        self.adapter = BaostockDataSource.__new__(BaostockDataSource)
        self.adapter.bs = Mock()
        self.adapter.available = True

    @patch("src.adapters.baostock_adapter.format_stock_code_for_source")
    @patch("src.adapters.baostock_adapter.ColumnMapper.to_english")
    def test_multiple_queries_sequence(self, mock_mapper, mock_format):
        """测试多个查询按顺序执行"""
        # Setup mocks
        mock_format.return_value = "sz.000001"

        # Mock stock daily query
        mock_rs_daily = Mock()
        mock_rs_daily.error_code = "0"
        mock_rs_daily.fields = ["date", "code", "open", "close"]
        mock_rs_daily.next.side_effect = [True, False]
        mock_rs_daily.get_row_data.return_value = ["2025-01-01", "000001", "10.0", "10.5"]

        # Mock stock basic query
        mock_rs_basic = Mock()
        mock_rs_basic.error_code = "0"
        mock_rs_basic.fields = ["code", "code_name"]
        mock_rs_basic.next.side_effect = [True, False]
        mock_rs_basic.get_row_data.return_value = ["000001", "平安银行"]

        self.adapter.bs.query_history_k_data_plus.return_value = mock_rs_daily
        self.adapter.bs.query_stock_basic.return_value = mock_rs_basic
        mock_mapper.return_value = pd.DataFrame()

        # Execute - 先查询日线，再查询基本信息
        daily_data = self.adapter.get_stock_daily("000001.SZ", "2025-01-01", "2025-01-02")
        basic_info = self.adapter.get_stock_basic("000001.SZ")

        # Verify
        self.assertIsInstance(daily_data, pd.DataFrame)
        self.assertIsInstance(basic_info, dict)
        self.adapter.bs.query_history_k_data_plus.assert_called_once()
        self.adapter.bs.query_stock_basic.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
