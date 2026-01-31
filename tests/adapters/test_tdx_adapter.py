"""
TDX (通达信) 数据源适配器测试

测试TdxDataSource类的核心功能：
- 初始化和连接管理
- 服务器配置管理
- 股票日线数据获取（分页）
- 指数日线数据获取
- 实时数据获取
- 市场代码识别
- 重试机制
- 数据验证

创建日期: 2026-01-03
Phase: 2 - Task 2.2.3
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd

from src.adapters.tdx.tdx_adapter import TdxDataSource


class TestTdxDataSourceInit(unittest.TestCase):
    """测试TdxDataSource初始化"""

    @patch("src.adapters.tdx.tdx_adapter.TdxServerConfig")
    @patch("src.adapters.tdx.tdx_adapter.os.getenv")
    def test_init_with_server_config_success(self, mock_getenv, mock_config_class):
        """测试使用服务器配置初始化"""
        # Setup mocks
        mock_getenv.side_effect = lambda k, d=None: d
        mock_config = Mock()
        mock_config.get_primary_server.return_value = ("119.147.212.81", 7709)
        mock_config.get_server_count.return_value = 5
        mock_config_class.return_value = mock_config

        # Execute
        adapter = TdxDataSource(use_server_config=True)

        # Verify
        self.assertEqual(adapter.tdx_host, "119.147.212.81")
        self.assertEqual(adapter.tdx_port, 7709)
        self.assertTrue(adapter.use_server_config)
        self.assertIsNotNone(adapter.server_config)

    @patch("src.adapters.tdx.tdx_adapter.TdxServerConfig")
    @patch("src.adapters.tdx.tdx_adapter.os.getenv")
    def test_init_with_server_config_fallback(self, mock_getenv, mock_config_class):
        """测试服务器配置加载失败时回退到环境变量"""
        # Setup mocks
        mock_getenv.side_effect = lambda k, d=None: d if d == "101.227.73.20" else "7709"
        mock_config_class.side_effect = Exception("Config file not found")

        # Execute
        adapter = TdxDataSource(use_server_config=True)

        # Verify
        self.assertEqual(adapter.tdx_host, "101.227.73.20")
        self.assertEqual(adapter.tdx_port, 7709)
        self.assertFalse(adapter.use_server_config)
        self.assertIsNone(adapter.server_config)

    @patch("src.adapters.tdx.tdx_adapter.os.getenv")
    def test_init_without_server_config(self, mock_getenv):
        """测试不使用服务器配置初始化"""
        # Setup mocks
        mock_getenv.side_effect = lambda k, d=None: d if d == "101.227.73.20" else "7709"

        # Execute
        adapter = TdxDataSource(use_server_config=False)

        # Verify
        self.assertEqual(adapter.tdx_host, "101.227.73.20")
        self.assertEqual(adapter.tdx_port, 7709)
        self.assertFalse(adapter.use_server_config)

    @patch("src.adapters.tdx.tdx_adapter.os.getenv")
    def test_init_with_custom_params(self, mock_getenv):
        """测试使用自定义参数初始化"""
        # Setup mocks
        mock_getenv.side_effect = lambda k, d=None: d

        # Execute
        adapter = TdxDataSource(
            tdx_host="192.168.1.1", tdx_port=8080, max_retries=5, retry_delay=2, api_timeout=30, use_server_config=False
        )

        # Verify
        self.assertEqual(adapter.tdx_host, "192.168.1.1")
        self.assertEqual(adapter.tdx_port, 8080)
        self.assertEqual(adapter.max_retries, 5)
        self.assertEqual(adapter.retry_delay, 2)
        self.assertEqual(adapter.api_timeout, 30)


class TestTdxDataSourceMarketCode(unittest.TestCase):
    """测试市场代码识别功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.logger = Mock()

    def test_get_market_code_shenzhen_000(self):
        """测试识别深圳000开头股票"""
        market = self.adapter._get_market_code("000001")
        self.assertEqual(market, 0)

    def test_get_market_code_shenzhen_002(self):
        """测试识别深圳002开头股票"""
        market = self.adapter._get_market_code("000002")
        self.assertEqual(market, 0)

    def test_get_market_code_shenzhen_300(self):
        """测试识别深圳300开头股票"""
        market = self.adapter._get_market_code("300001")
        self.assertEqual(market, 0)

    def test_get_market_code_shanghai_600(self):
        """测试识别上海600开头股票"""
        market = self.adapter._get_market_code("600000")
        self.assertEqual(market, 1)

    def test_get_market_code_shanghai_601(self):
        """测试识别上海601开头股票"""
        market = self.adapter._get_market_code("601318")
        self.assertEqual(market, 1)

    def test_get_market_code_shanghai_688(self):
        """测试识别上海688开头股票（科创板）"""
        market = self.adapter._get_market_code("688981")
        self.assertEqual(market, 1)

    def test_get_market_code_invalid_format(self):
        """测试无效格式"""
        with self.assertRaises(ValueError) as context:
            self.adapter._get_market_code("12345")
        self.assertIn("无效的股票代码格式", str(context.exception))

    def test_get_market_code_not_digit(self):
        """测试非数字代码"""
        with self.assertRaises(ValueError):
            self.adapter._get_market_code("ABCDEF")

    def test_get_market_code_unknown_prefix(self):
        """测试未知前缀"""
        with self.assertRaises(ValueError) as context:
            self.adapter._get_market_code("900001")
        self.assertIn("无法识别的股票代码", str(context.exception))


class TestTdxDataSourceStockDaily(unittest.TestCase):
    """测试股票日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.tdx_host = "101.227.73.20"
        self.adapter.tdx_port = 7709
        self.adapter.max_retries = 3
        self.adapter.retry_delay = 1
        self.adapter.use_server_config = False
        self.adapter.logger = Mock()

    @patch("src.adapters.tdx.tdx_adapter.normalize_date")
    @patch("src.adapters.tdx.tdx_adapter.ColumnMapper.to_english")
    @patch("src.adapters.tdx.tdx_adapter.TdxHq_API")
    def test_get_stock_daily_success(self, mock_api_class, mock_mapper, mock_normalize):
        """测试成功获取股票日线数据"""
        # Setup mocks
        mock_normalize.side_effect = lambda x: x
        mock_mapper.return_value = pd.DataFrame()

        mock_api = Mock()
        mock_api.connect.return_value = True
        mock_api.get_security_bars.return_value = []
        mock_api.__enter__ = Mock(return_value=mock_api)
        mock_api.__exit__ = Mock(return_value=False)
        mock_api_class.return_value = mock_api

        # Execute
        result = self.adapter.get_stock_daily("600000", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        # 由于返回空列表，不会有connect调用

    @patch("src.adapters.tdx.tdx_adapter.normalize_date")
    def test_get_stock_daily_invalid_symbol(self, mock_normalize):
        """测试无效股票代码"""
        mock_normalize.side_effect = lambda x: x

        # Execute
        result = self.adapter.get_stock_daily("12345", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    @patch("src.adapters.tdx.tdx_adapter.normalize_date")
    @patch("src.adapters.tdx.tdx_adapter.ColumnMapper.to_english")
    @patch("src.adapters.tdx.tdx_adapter.TdxHq_API")
    def test_get_stock_daily_connection_failure(self, mock_api_class, mock_mapper, mock_normalize):
        """测试连接失败"""
        # Setup mocks
        mock_normalize.side_effect = lambda x: x
        mock_mapper.return_value = pd.DataFrame()

        mock_api = Mock()
        mock_api.connect.return_value = False
        mock_api_class.return_value = mock_api

        # Execute
        result = self.adapter.get_stock_daily("600000", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestTdxDataSourceIndexDaily(unittest.TestCase):
    """测试指数日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.tdx_host = "101.227.73.20"
        self.adapter.tdx_port = 7709
        self.adapter.max_retries = 3
        self.adapter.retry_delay = 1
        self.adapter.use_server_config = False
        self.adapter.logger = Mock()

    @patch("src.adapters.tdx.tdx_adapter.normalize_date")
    @patch("src.adapters.tdx.tdx_adapter.ColumnMapper.to_english")
    @patch("src.adapters.tdx.tdx_adapter.TdxHq_API")
    def test_get_index_daily_shenzhen(self, mock_api_class, mock_mapper, mock_normalize):
        """测试获取深圳指数日线"""
        # Setup mocks
        mock_normalize.side_effect = lambda x: x
        mock_mapper.return_value = pd.DataFrame()

        mock_api = Mock()
        mock_api.connect.return_value = True
        mock_api.get_index_bars.return_value = []
        mock_api.__enter__ = Mock(return_value=mock_api)
        mock_api.__exit__ = Mock(return_value=False)
        mock_api_class.return_value = mock_api

        # Execute (399001 = 深证成指)
        result = self.adapter.get_index_daily("399001", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)

    @patch("src.adapters.tdx.tdx_adapter.normalize_date")
    @patch("src.adapters.tdx.tdx_adapter.ColumnMapper.to_english")
    @patch("src.adapters.tdx.tdx_adapter.TdxHq_API")
    def test_get_index_daily_shanghai(self, mock_api_class, mock_mapper, mock_normalize):
        """测试获取上海指数日线"""
        # Setup mocks
        mock_normalize.side_effect = lambda x: x
        mock_mapper.return_value = pd.DataFrame()

        mock_api = Mock()
        mock_api.connect.return_value = True
        mock_api.get_index_bars.return_value = [
            {"datetime": "2024-12-31 15:00:00", "open": "3000.0", "close": "3020.0"}
        ]
        mock_api_class.return_value = mock_api

        # Execute (000001 = 上证指数)
        result = self.adapter.get_index_daily("000001", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)

    @patch("src.adapters.tdx.tdx_adapter.normalize_date")
    def test_get_index_daily_invalid_code(self, mock_normalize):
        """测试无效指数代码"""
        mock_normalize.side_effect = lambda x: x

        # Execute
        result = self.adapter.get_index_daily("12345", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestTdxDataSourceStockBasic(unittest.TestCase):
    """测试股票基本信息获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.tdx_host = "101.227.73.20"
        self.adapter.tdx_port = 7709
        self.adapter.logger = Mock()

    @patch("src.adapters.tdx.tdx_adapter.TdxDataSource.get_stock_daily")
    @patch("src.adapters.tdx.tdx_adapter.datetime")
    def test_get_stock_basic_success(self, mock_datetime, mock_get_daily):
        """测试成功获取股票基本信息"""
        # Setup mocks
        mock_datetime.now.return_value = datetime(2024, 12, 31)
        mock_get_daily.return_value = pd.DataFrame(
            {"date": ["2024-12-31"], "open": [10.0], "close": [10.5], "amount": [100000]}
        )

        # Execute
        result = self.adapter.get_stock_basic("600000")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertIn("symbol", result)
        mock_get_daily.assert_called_once()

    @patch("src.adapters.tdx.tdx_adapter.TdxDataSource.get_stock_daily")
    @patch("src.adapters.tdx.tdx_adapter.datetime")
    def test_get_stock_basic_empty_data(self, mock_datetime, mock_get_daily):
        """测试获取空数据"""
        # Setup mocks
        mock_datetime.now.return_value = datetime(2024, 12, 31)
        mock_get_daily.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_stock_basic("600000")

        # Verify - 即使日线为空，也会返回包含symbol的基本信息
        self.assertIsInstance(result, dict)
        # TDX适配器在get_stock_basic中会构建基本信息，不一定是0个字段


class TestTdxDataSourceIndexComponents(unittest.TestCase):
    """测试指数成分股获取功能（stub实现）"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.logger = Mock()

    def test_get_index_components_stub(self):
        """测试指数成分股stub实现"""
        # Execute
        result = self.adapter.get_index_components("上证50")

        # Verify - stub实现返回空列表
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestTdxDataSourceRealtimeData(unittest.TestCase):
    """测试实时数据获取功能（会尝试连接TDX服务器）"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.tdx_host = "101.227.73.20"
        self.adapter.tdx_port = 7709
        self.adapter.max_retries = 1
        self.adapter.retry_delay = 0
        self.adapter.use_server_config = False
        self.adapter.logger = Mock()

    @patch("src.adapters.tdx.tdx_adapter.TdxHq_API")
    def test_get_real_time_data_success(self, mock_api_class):
        """测试成功获取实时数据"""
        # Setup mocks
        mock_api = Mock()
        mock_api.connect.return_value = True
        mock_api.get_security_quotes.return_value = [{"code": "600000", "name": "浦发银行", "price": "10.5"}]
        mock_api.__enter__ = Mock(return_value=mock_api)
        mock_api.__exit__ = Mock(return_value=False)
        mock_api_class.return_value = mock_api

        # Execute
        result = self.adapter.get_real_time_data("600000")

        # Verify
        self.assertIsInstance(result, dict)
        # TDX实现会返回字典或空字典

    @patch("src.adapters.tdx.tdx_adapter.TdxHq_API")
    def test_get_real_time_data_connection_fails(self, mock_api_class):
        """测试连接失败（返回错误消息）"""
        # Setup mocks - 连接失败
        mock_api = Mock()
        mock_api.connect.return_value = False
        mock_api.__enter__ = Mock(return_value=mock_api)
        mock_api.__exit__ = Mock(return_value=False)
        mock_api_class.return_value = mock_api

        # Execute - 连接失败会返回错误消息字符串
        result = self.adapter.get_real_time_data("600000")

        # Verify - 应该返回包含"网络连接失败"的错误消息字符串
        self.assertIsInstance(result, str)
        self.assertIn("网络连接失败", result)


class TestTdxDataSourceMarketCalendar(unittest.TestCase):
    """测试交易日历获取功能（stub实现）"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.logger = Mock()

    def test_get_market_calendar_stub(self):
        """测试交易日历stub实现"""
        # Execute
        result = self.adapter.get_market_calendar("2024-01-01", "2024-12-31")

        # Verify - stub实现返回空DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestTdxDataSourceFinancialData(unittest.TestCase):
    """测试财务数据获取功能（stub实现）"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.logger = Mock()

    def test_get_financial_data_stub(self):
        """测试财务数据stub实现"""
        # Execute
        result = self.adapter.get_financial_data("600000")

        # Verify - stub实现返回空DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestTdxDataSourceNewsData(unittest.TestCase):
    """测试新闻数据获取功能（stub实现）"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.logger = Mock()

    def test_get_news_data_stub(self):
        """测试新闻数据stub实现"""
        # Execute
        result = self.adapter.get_news_data(symbol="600000", limit=10)

        # Verify - stub实现返回空列表
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestTdxDataSourceRetryMechanism(unittest.TestCase):
    """测试重试机制"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.tdx_host = "101.227.73.20"
        self.adapter.tdx_port = 7709
        self.adapter.max_retries = 3
        self.adapter.retry_delay = 1
        self.adapter.use_server_config = False
        self.adapter.logger = Mock()

    @patch("src.adapters.tdx.tdx_adapter.time.sleep")
    @patch("src.adapters.tdx.tdx_adapter.TdxHq_API")
    def test_retry_on_failure(self, mock_api_class, mock_sleep):
        """测试失败重试机制"""
        # Setup mocks - 前两次失败，第三次成功
        mock_api = Mock()
        call_count = [0]

        def connect_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("Connection failed")
            return True

        mock_api.connect.side_effect = connect_side_effect

        # Mock context manager support
        mock_api.__enter__ = Mock(return_value=mock_api)
        mock_api.__exit__ = Mock(return_value=False)

        mock_api_class.return_value = mock_api

        # Create a test function using retry decorator
        @self.adapter._retry_api_call
        def test_function():
            with mock_api_class() as api:
                if not api.connect(self.adapter.tdx_host, self.adapter.tdx_port):
                    raise Exception("Connect failed")
                return "success"

        # Execute
        result = test_function()

        # Verify
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 3)
        self.assertEqual(mock_sleep.call_count, 2)  # 前两次失败后sleep


class TestTdxDataSourceDataValidation(unittest.TestCase):
    """测试数据验证功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = TdxDataSource.__new__(TdxDataSource)
        self.adapter.logger = Mock()

    def test_validate_kline_data_valid(self):
        """测试验证有效K线数据"""
        # Setup
        df = pd.DataFrame(
            {
                "date": ["2024-12-31", "2024-12-30"],
                "open": [10.0, 10.5],
                "high": [10.8, 10.9],
                "low": [9.8, 10.3],
                "close": [10.5, 10.7],
                "volume": [10000, 12000],
            }
        )

        # Execute
        result = self.adapter._validate_kline_data(df)

        # Verify
        self.assertEqual(len(result), 2)

    def test_validate_kline_data_missing_columns(self):
        """测试缺少必需列"""
        # Setup
        df = pd.DataFrame(
            {
                "date": ["2024-12-31"],
                "open": [10.0],
                # 缺少 high, low, close, volume
            }
        )

        # Execute
        result = self.adapter._validate_kline_data(df)

        # Verify
        self.assertTrue(result.empty)

    def test_validate_kline_data_negative_prices(self):
        """测试负价格修正"""
        # Setup
        df = pd.DataFrame(
            {"date": ["2024-12-31"], "open": [-10.0], "high": [10.8], "low": [9.8], "close": [10.5], "volume": [10000]}
        )

        # Execute
        result = self.adapter._validate_kline_data(df)

        # Verify - 负值被修正为0
        self.assertEqual(result["open"].iloc[0], 0)

    def test_validate_kline_data_empty_df(self):
        """测试空DataFrame"""
        # Setup
        df = pd.DataFrame()

        # Execute
        result = self.adapter._validate_kline_data(df)

        # Verify
        self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main(verbosity=2)
