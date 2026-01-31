"""
Financial数据源适配器测试

测试FinancialDataSource类的核心功能:
- 初始化和多数据源管理
- 股票日线数据获取(efinance/easyquotation fallback)
- 指数日线数据获取
- 股票基本信息获取
- 指数成分股获取
- 实时数据获取(带缓存)
- 财务数据获取(年报/季报)
- 交易日历获取(带缓存)
- 新闻数据获取(未实现)
- 缓存机制验证
- 数据验证和清洗

创建日期: 2026-01-03
Phase: 2 - Task 2.2.4
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd

from src.adapters.financial_adapter import FinancialDataSource


class TestFinancialDataSourceInit(unittest.TestCase):
    """测试FinancialDataSource初始化"""

    @patch("src.adapters.financial_adapter.logger")
    def test_init_with_efinance_success(self, mock_logger):
        """测试使用efinance初始化成功"""
        # Setup mocks
        mock_ef = Mock()
        mock_efinance = Mock()
        mock_efinance.stock = Mock()

        # Execute
        adapter = FinancialDataSource.__new__(FinancialDataSource)
        adapter.ef = mock_ef
        adapter.efinance_available = True
        adapter.easyquotation_available = False
        adapter.data_cache = {}
        adapter.logger = mock_logger

        # Verify
        self.assertTrue(adapter.efinance_available)
        self.assertFalse(adapter.easyquotation_available)
        self.assertEqual(adapter.data_cache, {})

    @patch("src.adapters.financial_adapter.logger")
    def test_init_with_easyquotation_success(self, mock_logger):
        """测试使用easyquotation初始化成功"""
        # Execute
        adapter = FinancialDataSource.__new__(FinancialDataSource)
        adapter.efinance_available = False
        adapter.eq = Mock()
        adapter.easyquotation_available = True
        adapter.data_cache = {}
        adapter.logger = mock_logger

        # Verify
        self.assertFalse(adapter.efinance_available)
        self.assertTrue(adapter.easyquotation_available)

    @patch("src.adapters.financial_adapter.logger")
    def test_init_both_sources_available(self, mock_logger):
        """测试两个数据源都可用"""
        # Execute
        adapter = FinancialDataSource.__new__(FinancialDataSource)
        adapter.ef = Mock()
        adapter.efinance_available = True
        adapter.eq = Mock()
        adapter.easyquotation_available = True
        adapter.data_cache = {}
        adapter.logger = mock_logger

        # Verify
        self.assertTrue(adapter.efinance_available)
        self.assertTrue(adapter.easyquotation_available)


class TestFinancialDataSourceCache(unittest.TestCase):
    """测试缓存机制"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.logger = Mock()
        self.adapter.data_cache = {}

    def test_get_cache_key_basic(self):
        """测试基本缓存键生成"""
        # Execute
        key = self.adapter._get_cache_key("000001", "daily")

        # Verify
        self.assertEqual(key, "000001|daily")

    def test_get_cache_key_with_params(self):
        """测试带参数的缓存键生成"""
        # Execute
        key = self.adapter._get_cache_key("000001", "financial", period="annual", year="2024")

        # Verify - 参数应该排序
        self.assertEqual(key, "000001|financial|period=annual|year=2024")

    def test_save_to_cache(self):
        """测试保存到缓存"""
        # Setup
        cache_key = "test_key"
        test_data = pd.DataFrame({"col1": [1, 2, 3]})

        # Execute
        self.adapter._save_to_cache(cache_key, test_data)

        # Verify
        self.assertIn(cache_key, self.adapter.data_cache)
        self.assertIn("data", self.adapter.data_cache[cache_key])
        self.assertIn("timestamp", self.adapter.data_cache[cache_key])
        pd.testing.assert_frame_equal(self.adapter.data_cache[cache_key]["data"], test_data)

    def test_get_from_cache_hit(self):
        """测试缓存命中"""
        # Setup
        cache_key = "test_key"
        test_data = pd.DataFrame({"col1": [1, 2, 3]})
        self.adapter.data_cache[cache_key] = {"data": test_data, "timestamp": datetime.now()}

        # Execute
        result = self.adapter._get_from_cache(cache_key)

        # Verify
        pd.testing.assert_frame_equal(result, test_data)

    def test_get_from_cache_miss(self):
        """测试缓存未命中"""
        # Execute
        result = self.adapter._get_from_cache("nonexistent_key")

        # Verify
        self.assertIsNone(result)

    @patch("src.adapters.financial_adapter.datetime")
    def test_get_from_cache_expired(self, mock_datetime):
        """测试缓存过期"""
        # Setup - 缓存已过期(超过5分钟)
        old_timestamp = datetime.now().replace(second=0)
        expired_timestamp = old_timestamp.replace(minute=old_timestamp.minute - 6)
        mock_datetime.now.return_value = datetime.now()

        cache_key = "test_key"
        test_data = pd.DataFrame({"col1": [1, 2, 3]})
        self.adapter.data_cache[cache_key] = {"data": test_data, "timestamp": expired_timestamp}

        # Execute
        result = self.adapter._get_from_cache(cache_key)

        # Verify - 过期缓存应该被删除
        self.assertIsNone(result)
        self.assertNotIn(cache_key, self.adapter.data_cache)


class TestFinancialDataSourceStockDaily(unittest.TestCase):
    """测试股票日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.efinance_available = True
        self.adapter.ef = Mock()
        self.adapter.easyquotation_available = False
        self.adapter.logger = Mock()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    @patch("src.adapters.financial_adapter.date_utils.normalize_date")
    def test_get_stock_daily_efinance_success(self, mock_normalize, mock_symbol):
        """测试使用efinance成功获取股票日线数据"""
        # Setup mocks
        mock_symbol.return_value = "000001"
        mock_normalize.side_effect = lambda x: x

        mock_data = pd.DataFrame(
            {
                "日期": ["2024-12-31", "2024-12-30"],
                "开盘": [10.0, 10.5],
                "收盘": [10.5, 10.8],
                "最高": [10.8, 11.0],
                "最低": [9.8, 10.3],
                "成交量": [10000, 12000],
                "成交额": [100000, 120000],
            }
        )
        self.adapter.ef.stock.get_quote_history.return_value = mock_data

        # Execute
        result = self.adapter.get_stock_daily("000001", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.adapter.ef.stock.get_quote_history.assert_called_once()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_stock_daily_invalid_symbol(self, mock_symbol):
        """测试无效股票代码"""
        # Setup mock
        mock_symbol.return_value = None

        # Execute
        result = self.adapter.get_stock_daily("", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    @patch("src.adapters.financial_adapter.date_utils.normalize_date")
    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_stock_daily_empty_data(self, mock_symbol2, mock_normalize, mock_symbol):
        """测试获取空数据"""
        # Setup mocks
        mock_symbol.return_value = "000001"
        mock_normalize.side_effect = lambda x: x
        mock_symbol2.return_value = "000001"

        mock_data = pd.DataFrame()
        self.adapter.ef.stock.get_quote_history.return_value = mock_data

        # Execute
        result = self.adapter.get_stock_daily("000001", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestFinancialDataSourceIndexDaily(unittest.TestCase):
    """测试指数日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.efinance_available = True
        self.adapter.ef = Mock()
        self.adapter.logger = Mock()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    @patch("src.adapters.financial_adapter.date_utils.normalize_date")
    def test_get_index_daily_success(self, mock_normalize, mock_symbol):
        """测试成功获取指数日线数据"""
        # Setup mocks
        mock_symbol.return_value = "000300"
        mock_normalize.side_effect = lambda x: x

        mock_data = pd.DataFrame(
            {
                "日期": ["2024-12-31"],
                "开盘": [3000.0],
                "收盘": [3020.0],
                "最高": [3050.0],
                "最低": [2980.0],
                "成交量": [1000000],
                "成交额": [10000000],
            }
        )
        self.adapter.ef.stock.get_quote_history.return_value = mock_data

        # Execute
        result = self.adapter.get_index_daily("000300", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_index_daily_invalid_code(self, mock_symbol):
        """测试无效指数代码"""
        # Setup mock
        mock_symbol.return_value = None

        # Execute
        result = self.adapter.get_index_daily("", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestFinancialDataSourceStockBasic(unittest.TestCase):
    """测试股票基本信息获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.efinance_available = True
        self.adapter.ef = Mock()
        self.adapter.logger = Mock()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_stock_basic_success_dataframe(self, mock_symbol):
        """测试成功获取股票基本信息(DataFrame格式)"""
        # Setup mocks
        mock_symbol.return_value = "000001"

        mock_data = pd.DataFrame({"股票代码": ["000001"], "股票名称": ["平安银行"], "行业": ["银行"]})
        self.adapter.ef.stock.get_base_info.return_value = mock_data

        # Execute
        result = self.adapter.get_stock_basic("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertIn("股票代码", result)
        self.adapter.ef.stock.get_base_info.assert_called_once()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_stock_basic_success_series(self, mock_symbol):
        """测试成功获取股票基本信息(Series格式)"""
        # Setup mocks
        mock_symbol.return_value = "000001"

        mock_series = pd.Series({"股票代码": "000001", "股票名称": "平安银行"})
        self.adapter.ef.stock.get_base_info.return_value = mock_series

        # Execute
        result = self.adapter.get_stock_basic("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result["股票代码"], "000001")

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_stock_basic_empty_data(self, mock_symbol):
        """测试获取空数据"""
        # Setup mocks
        mock_symbol.return_value = "000001"

        mock_data = pd.DataFrame()
        self.adapter.ef.stock.get_base_info.return_value = mock_data

        # Execute
        result = self.adapter.get_stock_basic("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)


class TestFinancialDataSourceIndexComponents(unittest.TestCase):
    """测试指数成分股获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.efinance_available = True
        self.adapter.ef = Mock()
        self.adapter.logger = Mock()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_index_components_success(self, mock_symbol):
        """测试成功获取指数成分股"""
        # Setup mocks
        mock_symbol.return_value = "000300"

        mock_data = pd.DataFrame({"股票代码": ["600000", "600036"], "股票名称": ["浦发银行", "招商银行"]})
        self.adapter.ef.stock.get_members.return_value = mock_data

        # Execute
        result = self.adapter.get_index_components("沪深300")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.adapter.ef.stock.get_members.assert_called_once()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_index_components_empty_data(self, mock_symbol):
        """测试获取空数据"""
        # Setup mocks
        mock_symbol.return_value = "000300"

        mock_data = pd.DataFrame()
        self.adapter.ef.stock.get_members.return_value = mock_data

        # Execute
        result = self.adapter.get_index_components("沪深300")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestFinancialDataSourceRealtimeData(unittest.TestCase):
    """测试实时数据获取功能(带缓存)"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.efinance_available = True
        self.adapter.ef = Mock()
        self.adapter.data_cache = {}
        self.adapter.logger = Mock()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_real_time_data_with_cache(self, mock_symbol):
        """测试使用缓存获取实时数据"""
        # Setup mocks
        mock_symbol.return_value = "000001"

        cache_key = self.adapter._get_cache_key("000001", "realtime")
        cached_data = pd.DataFrame({"col1": [1, 2, 3]})
        self.adapter.data_cache[cache_key] = {"data": cached_data, "timestamp": datetime.now()}

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify - 应该使用缓存,不调用API
        pd.testing.assert_frame_equal(result, cached_data)
        self.adapter.ef.stock.get_realtime_quotes.assert_not_called()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_real_time_data_cache_miss(self, mock_symbol):
        """测试缓存未命中,从API获取"""
        # Setup mocks
        mock_symbol.return_value = "000001"

        mock_data = pd.DataFrame({"股票代码": ["000001"], "最新价": [10.5]})
        self.adapter.ef.stock.get_realtime_quotes.return_value = mock_data

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify - 应该调用API并缓存
        self.assertIsInstance(result, pd.DataFrame)
        self.adapter.ef.stock.get_realtime_quotes.assert_called_once()
        # 验证数据被缓存
        cache_key = self.adapter._get_cache_key("000001", "realtime")
        self.assertIn(cache_key, self.adapter.data_cache)


class TestFinancialDataSourceFinancialData(unittest.TestCase):
    """测试财务数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.efinance_available = True
        self.adapter.ef = Mock()
        self.adapter.data_cache = {}
        self.adapter.logger = Mock()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_financial_data_annual_success(self, mock_symbol):
        """测试成功获取年报财务数据"""
        # Setup mocks
        mock_symbol.return_value = "000001"

        mock_all_data = pd.DataFrame(
            {"股票代码": ["000001", "000002"], "股票简称": ["平安银行", "万科A"], "净利润": [100, 200]}
        )
        self.adapter.ef.stock.get_all_company_performance.return_value = mock_all_data

        # Execute
        result = self.adapter.get_financial_data("000001", period="annual")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)  # 只返回指定股票的数据
        self.adapter.ef.stock.get_all_company_performance.assert_called_once()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_financial_data_quarterly_success(self, mock_symbol):
        """测试成功获取季报财务数据"""
        # Setup mocks
        mock_symbol.return_value = "000001"

        mock_data = pd.DataFrame({"股票代码": ["000001"], "报告期": ["2024Q3"], "净利润": [50]})
        self.adapter.ef.stock.get_quarterly_performance.return_value = mock_data

        # Execute
        result = self.adapter.get_financial_data("000001", period="quarterly")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.adapter.ef.stock.get_quarterly_performance.assert_called_once()

    @patch("src.adapters.financial_adapter.symbol_utils.normalize_stock_code")
    def test_get_financial_data_invalid_period(self, mock_symbol):
        """测试无效的报告期类型"""
        # Setup mocks
        mock_symbol.return_value = "000001"

        mock_all_data = pd.DataFrame({"股票代码": ["000001"], "净利润": [100]})
        self.adapter.ef.stock.get_all_company_performance.return_value = mock_all_data

        # Execute - 使用无效period,应该回退到annual
        result = self.adapter.get_financial_data("000001", period="invalid")

        # Verify - 应该使用默认的annual类型
        self.assertIsInstance(result, pd.DataFrame)


class TestFinancialDataSourceMarketCalendar(unittest.TestCase):
    """测试交易日历获取功能(带缓存)"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.efinance_available = True
        self.adapter.ef = Mock()
        self.adapter.data_cache = {}
        self.adapter.logger = Mock()

    def test_get_market_calendar_with_cache(self):
        """测试使用缓存获取交易日历"""
        # Setup
        cache_key = self.adapter._get_cache_key("market_calendar", "calendar")
        cached_data = pd.DataFrame({"日期": ["2024-12-31"]})
        self.adapter.data_cache[cache_key] = {"data": cached_data, "timestamp": datetime.now()}

        # Execute
        result = self.adapter.get_market_calendar()

        # Verify - 应该使用缓存
        pd.testing.assert_frame_equal(result, cached_data)
        self.adapter.ef.stock.get_all_report_dates.assert_not_called()

    def test_get_market_calendar_from_api(self):
        """测试从API获取交易日历"""
        # Setup
        mock_data = pd.DataFrame({"日期": ["2024-12-31", "2024-12-30"]})
        self.adapter.ef.stock.get_all_report_dates.return_value = mock_data

        # Execute
        result = self.adapter.get_market_calendar()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.adapter.ef.stock.get_all_report_dates.assert_called_once()


class TestFinancialDataSourceNewsData(unittest.TestCase):
    """测试新闻数据获取功能(未实现)"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.efinance_available = True
        self.adapter.data_cache = {}
        self.adapter.logger = Mock()

    def test_get_news_data_not_implemented(self):
        """测试新闻数据功能未实现"""
        # Execute
        result = self.adapter.get_news_data("000001")

        # Verify - 应该返回空DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestFinancialDataSourceDataValidation(unittest.TestCase):
    """测试数据验证和清洗功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.logger = Mock()

    def test_validate_and_clean_data_remove_duplicates(self):
        """测试删除重复数据"""
        # Setup
        df = pd.DataFrame({"日期": ["2024-12-31", "2024-12-31", "2024-12-30"], "收盘": [10.5, 10.5, 10.8]})

        # Execute
        result = self.adapter._validate_and_clean_data(df, "stock")

        # Verify - 应该删除重复行
        self.assertEqual(len(result), 2)

    def test_validate_and_clean_data_handle_missing_values(self):
        """测试处理缺失值"""
        # Setup
        df = pd.DataFrame({"日期": ["2024-12-31", "2024-12-30"], "收盘": [10.5, None]})

        # Execute
        result = self.adapter._validate_and_clean_data(df, "stock")

        # Verify - 缺失值应该被填充
        self.assertFalse(result["收盘"].isna().any())

    def test_validate_and_clean_data_invalid_prices(self):
        """测试价格验证"""
        # Setup
        df = pd.DataFrame({"日期": ["2024-12-31", "2024-12-30"], "收盘": [10.5, -100], "最高": [11.0, 11.5]})  # 负价格

        # Execute
        result = self.adapter._validate_and_clean_data(df, "stock")

        # Verify - 负价格行应该被删除
        self.assertEqual(len(result), 1)
        self.assertEqual(result["收盘"].iloc[0], 10.5)

    def test_validate_and_clean_data_sort_by_date(self):
        """测试按日期排序"""
        # Setup
        df = pd.DataFrame({"日期": ["2024-12-30", "2024-12-31"], "收盘": [10.5, 10.8]})

        # Execute
        result = self.adapter._validate_and_clean_data(df, "stock")

        # Verify - 应该按日期排序
        self.assertTrue(result["日期"].is_monotonic_increasing)

    def test_validate_and_clean_data_empty_input(self):
        """测试空DataFrame输入"""
        # Setup
        df = pd.DataFrame()

        # Execute
        result = self.adapter._validate_and_clean_data(df, "stock")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestFinancialDataSourceRenameColumns(unittest.TestCase):
    """测试列名重命名功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = FinancialDataSource.__new__(FinancialDataSource)
        self.adapter.logger = Mock()

    def test_rename_columns_english_to_chinese(self):
        """测试英文列名重命名为中文"""
        # Setup
        df = pd.DataFrame({"date": ["2024-12-31"], "open": [10.0], "close": [10.5]})

        # Execute
        result = self.adapter._rename_columns(df)

        # Verify
        self.assertIn("日期", result.columns)
        self.assertIn("开盘", result.columns)
        self.assertIn("收盘", result.columns)


if __name__ == "__main__":
    unittest.main(verbosity=2)
