"""
Customer (自定义数据源) 适配器测试

测试CustomerDataSource类的核心功能
- 初始化和双数据源配置
- 股票日线数据获取（efinance为主，easyquotation为备）
- 指数日线数据获取
- 股票基本信息获取
- 指数成分股获取
- 实时数据获取（市场快照+单股）
- 交易日历获取
- 财务数据获取
- 新闻数据获取
- 数据处理和列名标准化

创建日期: 2026-01-03
Phase: 2 - Task 2.2.5
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime

from src.adapters.customer_adapter import CustomerDataSource


class TestCustomerDataSourceInit(unittest.TestCase):
    """测试CustomerDataSource初始化"""

    @patch("src.adapters.customer_adapter.COLUMN_MAPPER_AVAILABLE", True)
    def test_init_with_column_mapping(self):
        """测试启用列名映射初始化"""
        with patch(
            "src.adapters.customer_adapter.CustomerDataSource.__init__", lambda self, use_column_mapping=True: None
        ):
            adapter = CustomerDataSource.__new__(CustomerDataSource)
            adapter.efinance_available = True
            adapter.easyquotation_available = True
            adapter.use_column_mapping = True

            self.assertTrue(adapter.use_column_mapping)

    @patch("src.adapters.customer_adapter.COLUMN_MAPPER_AVAILABLE", False)
    def test_init_without_column_mapping(self):
        """测试禁用列名映射初始化"""
        with patch(
            "src.adapters.customer_adapter.CustomerDataSource.__init__", lambda self, use_column_mapping=False: None
        ):
            adapter = CustomerDataSource.__new__(CustomerDataSource)
            adapter.efinance_available = False
            adapter.easyquotation_available = False
            adapter.use_column_mapping = False

            self.assertFalse(adapter.use_column_mapping)


class TestCustomerDataSourceStockDaily(unittest.TestCase):
    """测试股票日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = CustomerDataSource.__new__(CustomerDataSource)
        self.adapter.efinance_available = True
        self.adapter.easyquotation_available = True
        self.adapter.use_column_mapping = False

    @patch("src.adapters.customer_adapter.CustomerDataSource._standardize_dataframe")
    def test_get_stock_daily_efinance_success(self, mock_standardize):
        """测试使用efinance成功获取股票日线数据"""
        # Setup mock
        mock_ef = Mock()
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-12-31", "2024-12-30"],
                "收盘": [10.5, 10.3],
                "开盘": [10.0, 10.2],
            }
        )
        mock_ef.stock.get_quote_history.return_value = mock_df
        mock_standardize.return_value = mock_df
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_stock_daily("000001", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        mock_ef.stock.get_quote_history.assert_called_once()

    @patch("src.adapters.customer_adapter.CustomerDataSource._standardize_dataframe")
    def test_get_stock_daily_efinance_empty(self, mock_standardize):
        """测试efinance返回空数据"""
        # Setup mock - 返回空DataFrame
        mock_ef = Mock()
        mock_ef.stock.get_quote_history.return_value = pd.DataFrame()
        mock_standardize.return_value = pd.DataFrame()
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_stock_daily("000001", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    @patch("src.adapters.customer_adapter.CustomerDataSource._standardize_dataframe")
    def test_get_stock_daily_efinance_fail_easyquotation_success(self, mock_standardize):
        """测试efinance失败，easyquotation成功"""
        # Setup mocks
        mock_ef = Mock()
        mock_ef.stock.get_quote_history.side_effect = Exception("efinance error")
        self.adapter.ef = mock_ef

        mock_eq = Mock()
        mock_data = {"000001": {"name": "平安银行", "price": 10.5}}
        mock_eq.use.return_value.real.return_value = mock_data
        self.adapter.eq = mock_eq

        mock_standardize.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_stock_daily("000001", "2024-12-01", "2024-12-31")

        # Verify - 应该返回easyquotation的数据
        mock_eq.use.assert_called_once_with("sina")

    @patch("src.adapters.customer_adapter.CustomerDataSource._standardize_dataframe")
    def test_get_stock_daily_both_fail(self, mock_standardize):
        """测试两个数据源都失败"""
        # Setup mocks - 都失败
        mock_ef = Mock()
        mock_ef.stock.get_quote_history.side_effect = Exception("efinance error")
        self.adapter.ef = mock_ef

        mock_eq = Mock()
        mock_eq.use.return_value.real.side_effect = Exception("easyquotation error")
        self.adapter.eq = mock_eq

        mock_standardize.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_stock_daily("000001", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestCustomerDataSourceIndexDaily(unittest.TestCase):
    """测试指数日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = CustomerDataSource.__new__(CustomerDataSource)
        self.adapter.efinance_available = True
        self.adapter.use_column_mapping = False

    @patch("src.adapters.customer_adapter.CustomerDataSource._standardize_dataframe")
    def test_get_index_daily_success(self, mock_standardize):
        """测试成功获取指数日线数据"""
        # Setup mock
        mock_ef = Mock()
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-12-31"],
                "收盘": [3000.0],
            }
        )
        mock_ef.index.get_quote_history.return_value = mock_df
        mock_standardize.return_value = mock_df
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_index_daily("000001", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)

    @patch("src.adapters.customer_adapter.CustomerDataSource._standardize_dataframe")
    def test_get_index_daily_fail(self, mock_standardize):
        """测试获取指数日线数据失败"""
        # Setup mock - 抛出异常
        mock_ef = Mock()
        mock_ef.index.get_quote_history.side_effect = Exception("API error")
        self.adapter.ef = mock_ef

        mock_standardize.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_index_daily("000001", "2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestCustomerDataSourceStockBasic(unittest.TestCase):
    """测试股票基本信息获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = CustomerDataSource.__new__(CustomerDataSource)
        self.adapter.efinance_available = True

    def test_get_stock_basic_success_series(self):
        """测试成功获取股票基本信息（Series格式）"""
        # Setup mock - 返回Series
        mock_ef = Mock()
        mock_series = pd.Series({"股票名称": "平安银行", "行业": "银行", "上市日期": "1991-04-03"})
        mock_ef.stock.get_base_info.return_value = mock_series
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_stock_basic("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("股票名称"), "平安银行")

    def test_get_stock_basic_success_dict(self):
        """测试成功获取股票基本信息（dict格式）"""
        # Setup mock - 返回dict
        mock_ef = Mock()
        mock_info = {"股票名称": "平安银行", "行业": "银行"}
        mock_ef.stock.get_base_info.return_value = mock_info
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_stock_basic("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("股票名称"), "平安银行")

    def test_get_stock_basic_fail(self):
        """测试获取股票基本信息失败"""
        # Setup mock - 抛出异常
        mock_ef = Mock()
        mock_ef.stock.get_base_info.side_effect = Exception("API error")
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_stock_basic("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)


class TestCustomerDataSourceIndexComponents(unittest.TestCase):
    """测试指数成分股获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = CustomerDataSource.__new__(CustomerDataSource)
        self.adapter.efinance_available = True

    def test_get_index_components_success(self):
        """测试成功获取指数成分股"""
        # Setup mock
        mock_ef = Mock()
        mock_components = ["600000.SH", "000001.SZ", "601318.SH"]
        mock_ef.index.get_index_components.return_value = mock_components
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_index_components("上证50")

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_get_index_components_fail(self):
        """测试获取指数成分股失败"""
        # Setup mock - 抛出异常
        mock_ef = Mock()
        mock_ef.index.get_index_components.side_effect = Exception("API error")
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_index_components("上证50")

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestCustomerDataSourceRealtimeData(unittest.TestCase):
    """测试实时数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = CustomerDataSource.__new__(CustomerDataSource)
        self.adapter.efinance_available = True
        self.adapter.easyquotation_available = True
        self.adapter.use_column_mapping = False

    @patch("src.adapters.customer_adapter.CustomerDataSource._process_realtime_dataframe")
    @patch("src.adapters.customer_adapter.datetime")
    def test_get_real_time_data_market_quotes(self, mock_datetime, mock_process):
        """测试获取市场实时行情（sh/sz/hs）"""
        # Setup mocks
        mock_datetime.now.return_value = datetime(2024, 12, 31, 15, 0, 0)

        mock_ef = Mock()
        mock_df = pd.DataFrame(
            {"股票代码": ["000001", "600000"], "股票名称": ["平安银行", "浦发银行"], "涨跌幅": [1.5, 2.0]}
        )
        mock_ef.stock.get_realtime_quotes.return_value = mock_df

        mock_process.return_value = mock_df
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_real_time_data("hs")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        mock_ef.stock.get_realtime_quotes.assert_called_once()

    @patch("src.adapters.customer_adapter.CustomerDataSource._process_realtime_dataframe")
    @patch("src.adapters.customer_adapter.datetime")
    def test_get_real_time_data_single_stock(self, mock_datetime, mock_process):
        """测试获取单只股票实时数据"""
        # Setup mocks
        mock_datetime.now.return_value = datetime(2024, 12, 31, 15, 0, 0)

        mock_ef = Mock()
        mock_df = pd.DataFrame({"股票代码": ["000001"], "股票名称": ["平安银行"], "涨跌幅": [1.5]})
        mock_ef.stock.get_realtime_quotes.return_value = mock_df

        mock_process.return_value = mock_df
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify - 应该返回字典
        self.assertIsInstance(result, dict)
        self.assertIn("股票代码", result)

    @patch("src.adapters.customer_adapter.CustomerDataSource._process_realtime_dataframe")
    def test_get_real_time_data_easyquotation_fallback(self, mock_process):
        """测试efinance失败，回退到easyquotation"""
        # Setup mocks
        mock_ef = Mock()
        mock_ef.stock.get_realtime_quotes.side_effect = Exception("efinance error")
        self.adapter.ef = mock_ef

        mock_eq = Mock()
        mock_data = {"000001": {"name": "平安银行", "price": 10.5}}
        mock_eq.use.return_value.real.return_value = mock_data

        mock_df = pd.DataFrame([{"name": "平安银行", "price": 10.5}])
        mock_process.return_value = mock_df
        self.adapter.eq = mock_eq

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify
        mock_eq.use.assert_called_once_with("sina")

    def test_get_real_time_data_both_fail(self):
        """测试所有数据源都失败"""
        # Setup mocks - 都失败
        mock_ef = Mock()
        mock_ef.stock.get_realtime_quotes.side_effect = Exception("efinance error")
        self.adapter.ef = mock_ef

        mock_eq = Mock()
        mock_eq.use.return_value.real.side_effect = Exception("easyquotation error")
        self.adapter.eq = mock_eq

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)


class TestCustomerDataSourceMarketCalendar(unittest.TestCase):
    """测试交易日历获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = CustomerDataSource.__new__(CustomerDataSource)

    @patch("akshare.tool_trade_date_hist_sina")
    def test_get_market_calendar_success(self, mock_ak_calendar):
        """测试成功获取交易日历"""
        # Setup mock
        mock_df = pd.DataFrame({"trade_date": ["2024-12-31", "2024-12-30", "2024-12-29"]})
        mock_ak_calendar.return_value = mock_df

        # Execute
        result = self.adapter.get_market_calendar("2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn("date", result.columns)

    @patch("akshare.tool_trade_date_hist_sina")
    def test_get_market_calendar_import_error(self, mock_ak_calendar):
        """测试akshare未安装"""
        # Setup mock - ImportError
        mock_ak_calendar.side_effect = ImportError("akshare not installed")

        # Execute
        result = self.adapter.get_market_calendar("2024-12-01", "2024-12-31")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestCustomerDataSourceFinancialData(unittest.TestCase):
    """测试财务数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = CustomerDataSource.__new__(CustomerDataSource)
        self.adapter.efinance_available = True

    @patch("src.adapters.customer_adapter.CustomerDataSource._standardize_dataframe")
    def test_get_financial_data_success(self, mock_standardize):
        """测试成功获取财务数据"""
        # Setup mock
        mock_ef = Mock()
        mock_df = pd.DataFrame(
            {"股票代码": ["000001", "000001"], "报告期": ["2024-09-30", "2024-06-30"], "营业收入": [1000000, 900000]}
        )
        mock_ef.stock.get_all_company_performance.return_value = mock_df

        mock_standardize.return_value = mock_df
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_financial_data("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)

    @patch("src.adapters.customer_adapter.CustomerDataSource._standardize_dataframe")
    def test_get_financial_data_no_match(self, mock_standardize):
        """测试未找到匹配的财务数据"""
        # Setup mock - 返回不包含该股票的数据
        mock_ef = Mock()
        mock_df = pd.DataFrame({"股票代码": ["600000", "601318"], "报告期": ["2024-09-30", "2024-06-30"]})
        mock_ef.stock.get_all_company_performance.return_value = mock_df

        mock_standardize.return_value = mock_df
        self.adapter.ef = mock_ef

        # Execute
        result = self.adapter.get_financial_data("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestCustomerDataSourceNewsData(unittest.TestCase):
    """测试新闻数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = CustomerDataSource.__new__(CustomerDataSource)

    @patch("akshare.stock_news_em")
    def test_get_news_data_success(self, mock_ak_news):
        """测试成功获取新闻数据"""
        # Setup mock
        mock_df = pd.DataFrame(
            {
                "title": ["新闻标题1", "新闻标题2"],
                "content": ["内容1", "内容2"],
                "publish_time": ["2024-12-31", "2024-12-30"],
                "source": ["来源1", "来源2"],
            }
        )
        mock_ak_news.return_value = mock_df

        # Execute
        result = self.adapter.get_news_data("000001", limit=10)

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("title", result[0])

    @patch("akshare.stock_news_em")
    def test_get_news_data_empty(self, mock_ak_news):
        """测试获取空新闻数据"""
        # Setup mock - 返回空DataFrame
        mock_ak_news.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_news_data("000001", limit=10)

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestCustomerDataSourceProcessRealtimeDataframe(unittest.TestCase):
    """测试实时数据处理功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = CustomerDataSource.__new__(CustomerDataSource)
        self.adapter.use_column_mapping = False

    @patch("src.adapters.customer_adapter.datetime")
    def test_process_realtime_dataframe(self, mock_datetime):
        """测试处理实时数据DataFrame"""
        # Setup mocks
        mock_datetime.now.return_value = datetime(2024, 12, 31, 15, 0, 0)

        mock_df = pd.DataFrame(
            {
                "股票代码": ["000001"],
                "股票名称": ["平安银行"],
                "涨跌幅": [1.5],
                "收盘": [10.5],
            }
        )

        # Execute
        result = self.adapter._process_realtime_dataframe(mock_df, "000001", "efinance", "realtime_quotes")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        # 验证列被添加
        self.assertIn("fetch_timestamp", result.columns)
        self.assertIn("data_source", result.columns)
        self.assertIn("data_type", result.columns)

    @patch("src.adapters.customer_adapter.datetime")
    def test_process_realtime_dataframe_empty(self, mock_datetime):
        """测试处理空DataFrame"""
        # Setup
        mock_df = pd.DataFrame()

        # Execute
        result = self.adapter._process_realtime_dataframe(mock_df, "000001", "efinance", "realtime_quotes")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main(verbosity=2)
