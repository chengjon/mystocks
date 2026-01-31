"""
Byapi (biyingapi.com) 数据源适配器测试

测试ByapiDataSource类的核心功能：
- 初始化和频率控制
- 股票列表获取
- K线数据获取
- 实时行情获取
- 财务数据获取
- 涨跌停股池获取
- 技术指标获取
- 错误处理

创建日期: 2026-01-03
Phase: 2 - Task 2.2.5
"""

import unittest
from unittest.mock import Mock, patch

import pandas as pd

from src.adapters.byapi_adapter import ByapiAdapter, DataSourceError


class TestByapiDataSourceInit(unittest.TestCase):
    """测试ByapiDataSource初始化"""

    def test_init_default_params(self):
        """测试默认参数初始化"""
        adapter = ByapiAdapter()

        self.assertEqual(adapter.licence, "04C01BF1-7F2F-41A3-B470-1F81F14B1FC8")
        self.assertEqual(adapter.base_url, "http://api.biyingapi.com")
        self.assertEqual(adapter.min_interval, 0.2)
        self.assertEqual(adapter.last_request_time, 0.0)

    def test_init_custom_params(self):
        """测试自定义参数初始化"""
        adapter = ByapiAdapter(licence="CUSTOM-LICENCE", base_url="https://custom.api.com", min_interval=0.5)

        self.assertEqual(adapter.licence, "CUSTOM-LICENCE")
        self.assertEqual(adapter.base_url, "https://custom.api.com")
        self.assertEqual(adapter.min_interval, 0.5)

    def test_init_frequency_map(self):
        """测试频率映射配置"""
        adapter = ByapiAdapter()

        expected_map = {
            "1min": "5",
            "5min": "5",
            "15min": "15",
            "30min": "30",
            "60min": "60",
            "daily": "d",
            "weekly": "w",
            "monthly": "m",
            "yearly": "y",
        }

        self.assertEqual(adapter.frequency_map, expected_map)

    def test_init_fundamental_type_map(self):
        """测试财务类型映射配置"""
        adapter = ByapiAdapter()

        expected_map = {
            "income": "income",
            "balance": "balance",
            "cashflow": "cashflow",
            "metrics": "pershareindex",
        }

        self.assertEqual(adapter.fundamental_type_map, expected_map)

    def test_source_name_property(self):
        """测试source_name属性"""
        adapter = ByapiAdapter()
        self.assertEqual(adapter.source_name, "Byapi")

    def test_supported_markets_property(self):
        """测试supported_markets属性"""
        adapter = ByapiAdapter()
        self.assertEqual(adapter.supported_markets, ["CN_A"])


class TestByapiDataSourceStandardizeSymbol(unittest.TestCase):
    """测试股票代码标准化功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = ByapiAdapter()

    def test_standardize_symbol_with_suffix(self):
        """测试带后缀的股票代码"""
        symbol = self.adapter._standardize_symbol("600000.SH")
        self.assertEqual(symbol, "600000.SH")

        symbol = self.adapter._standardize_symbol("000001.SZ")
        self.assertEqual(symbol, "000001.SZ")

    def test_standardize_symbol_shanghai(self):
        """测试上海股票代码（6开头）"""
        symbol = self.adapter._standardize_symbol("600000")
        self.assertEqual(symbol, "600000.SH")

        symbol = self.adapter._standardize_symbol("601318")
        self.assertEqual(symbol, "601318.SH")

        symbol = self.adapter._standardize_symbol("688981")
        self.assertEqual(symbol, "688981.SH")

    def test_standardize_symbol_shenzhen(self):
        """测试深圳股票代码（0/3开头）"""
        symbol = self.adapter._standardize_symbol("000001")
        self.assertEqual(symbol, "000001.SZ")

        symbol = self.adapter._standardize_symbol("002001")
        self.assertEqual(symbol, "002001.SZ")

        symbol = self.adapter._standardize_symbol("300001")
        self.assertEqual(symbol, "300001.SZ")

    def test_standardize_symbol_invalid(self):
        """测试无效股票代码"""
        with self.assertRaises(ValueError) as context:
            self.adapter._standardize_symbol("900001")
        self.assertIn("无法识别的股票代码", str(context.exception))


class TestByapiDataSourceRateLimit(unittest.TestCase):
    """测试频率控制功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = ByapiAdapter()
        self.adapter.last_request_time = 0.0

    @patch("src.adapters.byapi_adapter.time.sleep")
    @patch("src.adapters.byapi_adapter.time.time")
    def test_rate_limit_first_request(self, mock_time, mock_sleep):
        """测试首次请求（无需等待）"""
        mock_time.return_value = 100.0

        self.adapter._rate_limit()

        self.assertEqual(self.adapter.last_request_time, 100.0)
        mock_sleep.assert_not_called()

    @patch("src.adapters.byapi_adapter.time.sleep")
    @patch("src.adapters.byapi_adapter.time.time")
    def test_rate_limit_with_enough_interval(self, mock_time, mock_sleep):
        """测试请求间隔足够（无需等待）"""
        # 首次请求
        mock_time.return_value = 100.0
        self.adapter._rate_limit()

        # 第二次请求，间隔1秒（大于0.2秒）
        mock_time.return_value = 101.0
        self.adapter._rate_limit()

        self.assertEqual(self.adapter.last_request_time, 101.0)
        mock_sleep.assert_not_called()

    @patch("src.adapters.byapi_adapter.time.sleep")
    @patch("src.adapters.byapi_adapter.time.time")
    def test_rate_limit_with_insufficient_interval(self, mock_time, mock_sleep):
        """测试请求间隔不足（需要等待）"""
        # 首次请求
        mock_time.return_value = 100.0
        self.adapter._rate_limit()

        # 第二次请求，间隔0.1秒（小于0.2秒）
        mock_time.return_value = 100.1
        self.adapter._rate_limit()

        # 应该sleep 0.1秒
        mock_sleep.assert_called_once()
        sleep_arg = mock_sleep.call_args[0][0]
        self.assertAlmostEqual(sleep_arg, 0.1, places=5)
        self.assertEqual(self.adapter.last_request_time, 100.1)


class TestByapiDataSourceStockList(unittest.TestCase):
    """测试股票列表获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = ByapiAdapter()
        self.adapter.licence = "TEST-LICENCE"
        self.adapter.base_url = "http://api.biyingapi.com"
        self.adapter.min_interval = 0.0  # 禁用频率控制

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_stock_list_success(self, mock_get):
        """测试成功获取股票列表"""
        # Setup mock
        mock_data = [
            {"dm": "600000.SH", "mc": "浦发银行", "jys": "SH"},
            {"dm": "000001.SZ", "mc": "平安银行", "jys": "SZ"},
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_stock_list()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("name", result.columns)
        self.assertIn("exchange", result.columns)
        self.assertIn("list_date", result.columns)
        self.assertIn("status", result.columns)

        # 验证交易所映射
        self.assertEqual(result[result["symbol"] == "600000.SH"]["exchange"].values[0], "SSE")
        self.assertEqual(result[result["symbol"] == "000001.SZ"]["exchange"].values[0], "SZSE")

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_stock_list_empty_data(self, mock_get):
        """测试获取空数据"""
        # Setup mock - 空列表
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Execute & Verify
        with self.assertRaises(DataSourceError) as context:
            self.adapter.get_stock_list()
        self.assertIn("股票列表数据为空", str(context.exception))

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_stock_list_api_error(self, mock_get):
        """测试API请求失败"""
        # Setup mock - HTTP错误
        mock_get.side_effect = Exception("Network error")

        # Execute & Verify
        with self.assertRaises(DataSourceError) as context:
            self.adapter.get_stock_list()
        self.assertIn("获取股票列表失败", str(context.exception))


class TestByapiDataSourceKlineData(unittest.TestCase):
    """测试K线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = ByapiAdapter()
        self.adapter.licence = "TEST-LICENCE"
        self.adapter.base_url = "https://api.biyingapi.com"
        self.adapter.min_interval = 0.0

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_kline_data_daily_success(self, mock_get):
        """测试成功获取日线数据"""
        # Setup mock
        mock_data = [
            {"t": "20241231", "o": 10.0, "h": 10.5, "l": 9.8, "c": 10.2, "v": 10000, "a": 100000},
            {"t": "20241230", "o": 9.9, "h": 10.3, "l": 9.7, "c": 10.0, "v": 12000, "a": 120000},
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_kline_data("600000", "2024-12-01", "2024-12-31", "daily")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("date", result.columns)
        self.assertIn("open", result.columns)
        self.assertIn("high", result.columns)
        self.assertIn("low", result.columns)
        self.assertIn("close", result.columns)
        self.assertIn("volume", result.columns)
        self.assertIn("amount", result.columns)

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_kline_data_empty_result(self, mock_get):
        """测试获取空K线数据"""
        # Setup mock - 空列表
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_kline_data("600000", "2024-12-01", "2024-12-31", "daily")

        # Verify - 应返回空DataFrame，包含所有列
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        self.assertIn("symbol", result.columns)
        self.assertIn("date", result.columns)

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_kline_data_invalid_frequency(self, mock_get):
        """测试无效的频率参数"""
        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            self.adapter.get_kline_data("600000", "2024-12-01", "2024-12-31", "invalid_freq")
        self.assertIn("不支持的频率", str(context.exception))

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_kline_data_api_error(self, mock_get):
        """测试API请求失败"""
        # Setup mock - HTTP错误
        mock_get.side_effect = Exception("Network error")

        # Execute & Verify
        with self.assertRaises(DataSourceError) as context:
            self.adapter.get_kline_data("600000", "2024-12-01", "2024-12-31", "daily")
        self.assertIn("获取K线数据失败", str(context.exception))


class TestByapiDataSourceRealtimeQuotes(unittest.TestCase):
    """测试实时行情获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = ByapiAdapter()
        self.adapter.licence = "TEST-LICENCE"
        self.adapter.base_url = "http://api.biyingapi.com"
        self.adapter.min_interval = 0.0

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_realtime_quotes_success(self, mock_get):
        """测试成功获取实时行情"""
        # Setup mock
        mock_data_1 = {
            "p": 10.5,
            "o": 10.0,
            "h": 10.8,
            "l": 9.9,
            "yc": 10.0,
            "v": 10000,
            "cje": 100000,
            "ud": 0.5,
            "pc": 5.0,
            "t": "2024-12-31 15:00:00",
            "hs": 2.5,
        }
        mock_data_2 = {
            "p": 15.2,
            "o": 15.0,
            "h": 15.5,
            "l": 14.8,
            "yc": 15.0,
            "v": 8000,
            "cje": 120000,
            "ud": 0.2,
            "pc": 1.3,
            "t": "2024-12-31 15:00:00",
            "hs": 1.8,
        }

        mock_response = Mock()
        mock_response.json.side_effect = [mock_data_1, mock_data_2]
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_realtime_quotes(["600000", "000001"])

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("current_price", result.columns)
        self.assertIn("change", result.columns)
        self.assertIn("change_pct", result.columns)

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_realtime_quotes_all_fail(self, mock_get):
        """测试所有股票获取失败"""
        # Setup mock - 所有请求失败（使用requests.RequestException）
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # Execute & Verify
        with self.assertRaises(DataSourceError) as context:
            self.adapter.get_realtime_quotes(["600000", "000001"])
        self.assertIn("获取实时行情失败", str(context.exception))

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_realtime_quotes_partial_fail(self, mock_get):
        """测试部分股票获取失败（跳过失败的）"""
        # Setup mock - 第一个成功，第二个失败
        import requests

        mock_data_1 = {
            "p": 10.5,
            "o": 10.0,
            "h": 10.8,
            "l": 9.9,
            "yc": 10.0,
            "v": 10000,
            "cje": 100000,
            "ud": 0.5,
            "pc": 5.0,
            "t": "2024-12-31 15:00:00",
            "hs": 2.5,
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_data_1
        mock_get.side_effect = [mock_response, requests.exceptions.RequestException("Network error")]

        # Execute
        result = self.adapter.get_realtime_quotes(["600000", "000001"])

        # Verify - 应该只返回成功的股票
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)


class TestByapiDataSourceFundamentalData(unittest.TestCase):
    """测试财务数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = ByapiAdapter()
        self.adapter.licence = "TEST-LICENCE"
        self.adapter.base_url = "http://api.biyingapi.com"
        self.adapter.min_interval = 0.0

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_fundamental_data_latest(self, mock_get):
        """测试获取最新财务数据"""
        # Setup mock
        mock_data = [{"jzrq": "2024-12-31", "yysr": 1000000, "jlr": 100000}]
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_fundamental_data("600000", "latest", "income")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn("symbol", result.columns)
        self.assertIn("report_period", result.columns)

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_fundamental_data_specific_period(self, mock_get):
        """测试获取指定报告期财务数据"""
        # Setup mock
        mock_data = [{"jzrq": "2024-09-30", "yysr": 900000, "jlr": 90000}]
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_fundamental_data("600000", "2024-09-30", "income")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_fundamental_data_empty_result(self, mock_get):
        """测试获取空财务数据"""
        # Setup mock - 空列表
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_fundamental_data("600000", "latest", "income")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_fundamental_data_invalid_type(self, mock_get):
        """测试无效的财务数据类型"""
        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            self.adapter.get_fundamental_data("600000", "latest", "invalid_type")
        self.assertIn("不支持的财务数据类型", str(context.exception))


class TestByapiDataSourceLimitStocks(unittest.TestCase):
    """测试涨跌停股池获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = ByapiAdapter()
        self.adapter.licence = "TEST-LICENCE"
        self.adapter.base_url = "http://api.biyingapi.com"
        self.adapter.min_interval = 0.0

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_limit_up_stocks_success(self, mock_get):
        """测试成功获取涨停股池"""
        # Setup mock
        mock_data = [{"dm": "600000.SH", "mc": "浦发银行", "ztjg": "10.00"}]
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_limit_up_stocks("2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("trade_date", result.columns)
        self.assertEqual(result["trade_date"].iloc[0], "2024-12-31")

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_limit_down_stocks_success(self, mock_get):
        """测试成功获取跌停股池"""
        # Setup mock
        mock_data = [{"dm": "000001.SZ", "mc": "平安银行", "dtjg": "10.00"}]
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_limit_down_stocks("2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("trade_date", result.columns)

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_limit_up_stocks_empty_result(self, mock_get):
        """测试获取空涨停股池"""
        # Setup mock - 非列表数据
        mock_response = Mock()
        mock_response.json.return_value = {"error": "no data"}
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_limit_up_stocks("2024-12-31")

        # Verify - 应返回空DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestByapiDataSourceTechnicalIndicator(unittest.TestCase):
    """测试技术指标获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = ByapiAdapter()
        self.adapter.licence = "TEST-LICENCE"
        self.adapter.base_url = "http://api.biyingapi.com"
        self.adapter.min_interval = 0.0

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_technical_indicator_success(self, mock_get):
        """测试成功获取技术指标"""
        # Setup mock
        mock_data = [{"t": "20241231", "macd": 0.5, "dif": 0.3, "dea": 0.2}]
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_technical_indicator("600000", "macd", "daily")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn("symbol", result.columns)
        self.assertIn("timestamp", result.columns)

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_technical_indicator_with_limit(self, mock_get):
        """测试带限制的技术指标获取"""
        # Setup mock
        mock_data = [
            {"t": "20241231", "ma": 10.5},
            {"t": "20241230", "ma": 10.3},
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_technical_indicator("600000", "ma", "daily", limit=2)

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)

    @patch("src.adapters.byapi_adapter.requests.get")
    def test_get_technical_indicator_empty_result(self, mock_get):
        """测试获取空技术指标数据"""
        # Setup mock - 空列表
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Execute
        result = self.adapter.get_technical_indicator("600000", "macd", "daily")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main(verbosity=2)
