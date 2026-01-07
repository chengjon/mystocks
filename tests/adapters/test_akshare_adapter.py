"""
Akshare数据源适配器测试

测试AkshareDataSource类的所有功能：
- 初始化和配置
- 股票日线数据获取
- 指数日线数据获取（多API fallback）
- 股票基本信息
- 指数成分股
- 实时数据
- 交易日历
- 财务数据
- 新闻数据
- 同花顺行业数据
- 分钟K线（空实现）
- 行业/概念分类

创建日期: 2026-01-03
Phase: 2 - Task 2.2.1
"""

import unittest
from unittest.mock import patch
import pandas as pd

from src.adapters.akshare_adapter import AkshareDataSource


class TestAkshareDataSourceInit(unittest.TestCase):
    """测试AkshareDataSource初始化"""

    def test_init_with_defaults(self):
        """测试使用默认参数初始化"""
        adapter = AkshareDataSource()

        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.api_timeout, 10)
        self.assertEqual(adapter.max_retries, 3)

    def test_init_with_custom_params(self):
        """测试使用自定义参数初始化"""
        adapter = AkshareDataSource(api_timeout=30, max_retries=5)

        self.assertEqual(adapter.api_timeout, 30)
        self.assertEqual(adapter.max_retries, 5)

    @patch("src.adapters.akshare_adapter.logger")
    def test_init_logs_info(self, mock_logger):
        """测试初始化时记录日志"""
        adapter = AkshareDataSource(api_timeout=20, max_retries=4)

        mock_logger.info.assert_called()


class TestAkshareDataSourceStockDaily(unittest.TestCase):
    """测试股票日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.stock_zh_a_hist")
    @patch("src.adapters.akshare_adapter.format_stock_code_for_source")
    @patch("src.adapters.akshare_adapter.normalize_date")
    @patch("src.adapters.akshare_adapter.ColumnMapper.to_english")
    def test_get_stock_daily_main_api_success(self, mock_mapper, mock_normalize, mock_format, mock_ak_hist):
        """测试主要API成功获取数据"""
        # Setup mocks
        mock_format.return_value = "000001"
        mock_normalize.side_effect = lambda x: x
        mock_ak_hist.return_value = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02"],
                "开盘": [10.0, 11.0],
                "收盘": [10.5, 11.5],
                "最高": [10.8, 11.8],
                "最低": [9.8, 10.8],
                "成交量": [10000, 12000],
                "成交额": [100000, 120000],
            }
        )
        mock_mapper.return_value = pd.DataFrame(
            {
                "date": ["2025-01-01", "2025-01-02"],
                "open": [10.0, 11.0],
                "close": [10.5, 11.5],
                "high": [10.8, 11.8],
                "low": [9.8, 10.8],
                "volume": [10000, 12000],
                "amount": [100000, 120000],
            }
        )

        # Execute
        result = self.adapter.get_stock_daily("000001.SZ", "2025-01-01", "2025-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        mock_ak_hist.assert_called_once()

    @patch("src.adapters.akshare_adapter.ak.stock_zh_a_spot")
    @patch("src.adapters.akshare_adapter.ak.stock_zh_a_hist")
    @patch("src.adapters.akshare_adapter.format_stock_code_for_source")
    @patch("src.adapters.akshare_adapter.normalize_date")
    @patch("src.adapters.akshare_adapter.ColumnMapper.to_english")
    def test_get_stock_daily_fallback_to_spot(
        self, mock_mapper, mock_normalize, mock_format, mock_ak_spot, mock_ak_hist
    ):
        """测试主要API失败后回退到spot API"""
        # Setup mocks
        mock_format.return_value = "000001"
        mock_normalize.side_effect = lambda x: x
        mock_ak_hist.side_effect = Exception("Main API failed")
        mock_ak_spot.return_value = pd.DataFrame(
            {
                "代码": ["000001"],
                "今开": [10.0],
                "最新价": [10.5],
                "最高": [10.8],
                "最低": [9.8],
                "成交量": [10000],
                "成交额": [100000],
            }
        )
        mock_mapper.return_value = pd.DataFrame(
            {
                "date": ["2025-01-01"],
                "open": [10.0],
                "close": [10.5],
                "high": [10.8],
                "low": [9.8],
                "volume": [10000],
                "amount": [100000],
            }
        )

        # Execute
        result = self.adapter.get_stock_daily("000001.SZ", "2025-01-01", "2025-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        mock_ak_hist.assert_called_once()
        mock_ak_spot.assert_called_once()

    @patch("src.adapters.akshare_adapter.ak.stock_zh_a_hist")
    @patch("src.adapters.akshare_adapter.format_stock_code_for_source")
    @patch("src.adapters.akshare_adapter.normalize_date")
    def test_get_stock_daily_all_apis_fail(self, mock_normalize, mock_format, mock_ak_hist):
        """测试所有API失败"""
        # Setup mocks
        mock_format.return_value = "000001"
        mock_normalize.side_effect = lambda x: x
        mock_ak_hist.side_effect = Exception("API failed")

        # Execute
        result = self.adapter.get_stock_daily("000001.SZ", "2025-01-01", "2025-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestAkshareDataSourceIndexDaily(unittest.TestCase):
    """测试指数日线数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.stock_zh_index_daily")
    @patch("src.adapters.akshare_adapter.format_index_code_for_source")
    @patch("src.adapters.akshare_adapter.normalize_date")
    @patch("src.adapters.akshare_adapter.ColumnMapper.to_english")
    def test_get_index_daily_sina_api_success(self, mock_mapper, mock_normalize, mock_format, mock_sina):
        """测试新浪接口成功获取指数数据"""
        # Setup mocks
        mock_format.return_value = "sh000001"
        mock_normalize.side_effect = lambda x: x
        mock_sina.return_value = pd.DataFrame(
            {
                "date": ["2025-01-01", "2025-01-02"],
                "open": [3000.0, 3100.0],
                "close": [3050.0, 3150.0],
                "high": [3080.0, 3180.0],
                "low": [2980.0, 3080.0],
                "volume": [1000000, 1200000],
            }
        )
        mock_mapper.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_index_daily("000001.SH", "2025-01-01", "2025-01-02")

        # Verify
        mock_sina.assert_called_once()
        self.assertIsInstance(result, pd.DataFrame)

    @patch("src.adapters.akshare_adapter.ak.stock_zh_index_daily_em")
    @patch("src.adapters.akshare_adapter.ak.stock_zh_index_daily")
    @patch("src.adapters.akshare_adapter.format_index_code_for_source")
    @patch("src.adapters.akshare_adapter.normalize_date")
    @patch("src.adapters.akshare_adapter.ColumnMapper.to_english")
    def test_get_index_daily_fallback_to_em(self, mock_mapper, mock_normalize, mock_format, mock_sina, mock_em):
        """测试新浪接口失败后回退到东方财富接口"""
        # Setup mocks
        mock_format.return_value = "sh000001"
        mock_normalize.side_effect = lambda x: x
        mock_sina.side_effect = Exception("Sina API failed")
        mock_em.return_value = pd.DataFrame({"date": ["2025-01-01"], "open": [3000.0], "close": [3050.0]})
        mock_mapper.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_index_daily("000001.SH", "2025-01-01", "2025-01-02")

        # Verify
        mock_sina.assert_called_once()
        mock_em.assert_called_once()

    @patch("src.adapters.akshare_adapter.ak.index_zh_a_hist")
    @patch("src.adapters.akshare_adapter.ak.stock_zh_index_daily_em")
    @patch("src.adapters.akshare_adapter.ak.stock_zh_index_daily")
    @patch("src.adapters.akshare_adapter.format_index_code_for_source")
    @patch("src.adapters.akshare_adapter.normalize_date")
    @patch("src.adapters.akshare_adapter.ColumnMapper.to_english")
    def test_get_index_daily_fallback_to_generic(
        self, mock_mapper, mock_normalize, mock_format, mock_sina, mock_em, mock_generic
    ):
        """测试前两个接口失败后回退到通用接口"""
        # Setup mocks
        mock_format.return_value = "sh000001"
        mock_normalize.side_effect = lambda x: x
        mock_sina.side_effect = Exception("Sina failed")
        mock_em.side_effect = Exception("EM failed")
        mock_generic.return_value = pd.DataFrame({"date": ["2025-01-01"], "open": [3000.0], "close": [3050.0]})
        mock_mapper.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_index_daily("000001.SH", "2025-01-01", "2025-01-02")

        # Verify
        mock_generic.assert_called_once()


class TestAkshareDataSourceStockBasic(unittest.TestCase):
    """测试股票基本信息获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.stock_individual_info_em")
    @patch("src.adapters.akshare_adapter.format_stock_code_for_source")
    def test_get_stock_basic_success(self, mock_format, mock_ak_info):
        """测试成功获取股票基本信息"""
        # Setup mocks
        mock_format.return_value = "000001"
        mock_ak_info.return_value = pd.DataFrame(
            {"item": ["股票名称", "行业", "总市值"], "value": ["平安银行", "银行", "2000亿"]}
        )

        # Execute
        result = self.adapter.get_stock_basic("000001.SZ")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result["股票名称"], "平安银行")
        self.assertEqual(result["行业"], "银行")

    @patch("src.adapters.akshare_adapter.ak.stock_individual_info_em")
    @patch("src.adapters.akshare_adapter.format_stock_code_for_source")
    def test_get_stock_basic_empty(self, mock_format, mock_ak_info):
        """测试获取空数据"""
        # Setup mocks
        mock_format.return_value = "000001"
        mock_ak_info.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_stock_basic("000001.SZ")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)


class TestAkshareDataSourceIndexComponents(unittest.TestCase):
    """测试指数成分股获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.index_stock_cons")
    def test_get_index_components_success(self, mock_ak_cons):
        """测试成功获取指数成分股"""
        # Setup mocks
        mock_ak_cons.return_value = pd.DataFrame(
            {"品种代码": ["000001.SZ", "000002.SZ", "600000.SH"], "品种名称": ["平安银行", "万科A", "浦发银行"]}
        )

        # Execute
        result = self.adapter.get_index_components("沪深300")

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIn("000001.SZ", result)

    @patch("src.adapters.akshare_adapter.ak.index_stock_cons")
    def test_get_index_components_alternative_column(self, mock_ak_cons):
        """测试使用备用列名获取成分股"""
        # Setup mocks
        mock_ak_cons.return_value = pd.DataFrame({"成分券代码": ["000001.SZ", "000002.SZ"]})

        # Execute
        result = self.adapter.get_index_components("中证500")

        # Verify
        self.assertEqual(len(result), 2)

    @patch("src.adapters.akshare_adapter.ak.index_stock_cons")
    def test_get_index_components_empty(self, mock_ak_cons):
        """测试获取空数据"""
        # Setup mocks
        mock_ak_cons.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_index_components("上证50")

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestAkshareDataSourceRealtimeData(unittest.TestCase):
    """测试实时数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.stock_zh_a_spot")
    def test_get_real_time_data_success(self, mock_ak_spot):
        """测试成功获取实时数据"""
        # Setup mocks
        mock_ak_spot.return_value = pd.DataFrame(
            {
                "代码": ["000001", "000002"],
                "今开": [10.0, 20.0],
                "最新价": [10.5, 20.5],
                "最高": [10.8, 20.8],
                "最低": [9.8, 19.8],
                "成交量": [10000, 20000],
                "成交额": [100000, 200000],
            }
        )

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result["代码"], "000001")
        self.assertEqual(result["最新价"], 10.5)

    @patch("src.adapters.akshare_adapter.ak.stock_zh_a_spot")
    def test_get_real_time_data_not_found(self, mock_ak_spot):
        """测试找不到指定股票"""
        # Setup mocks
        mock_ak_spot.return_value = pd.DataFrame({"代码": ["000002"], "最新价": [20.5]})

        # Execute
        result = self.adapter.get_real_time_data("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)


class TestAkshareDataSourceMarketCalendar(unittest.TestCase):
    """测试交易日历获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.tool_trade_date_hist_sina")
    @patch("src.adapters.akshare_adapter.normalize_date")
    def test_get_market_calendar_success(self, mock_normalize, mock_ak_calendar):
        """测试成功获取交易日历"""
        # Setup mocks
        mock_normalize.side_effect = lambda x: x
        mock_ak_calendar.return_value = pd.DataFrame(
            {"trade_date": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"])}
        )

        # Execute
        result = self.adapter.get_market_calendar("2025-01-01", "2025-01-10")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreaterEqual(len(result), 0)

    @patch("src.adapters.akshare_adapter.ak.tool_trade_date_hist_sina")
    def test_get_market_calendar_empty(self, mock_ak_calendar):
        """测试获取空数据"""
        # Setup mocks
        mock_ak_calendar.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_market_calendar("2025-01-01", "2025-01-10")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestAkshareDataSourceFinancialData(unittest.TestCase):
    """测试财务数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.stock_financial_abstract")
    @patch("src.adapters.akshare_adapter.format_stock_code_for_source")
    def test_get_financial_data_success(self, mock_format, mock_ak_fin):
        """测试成功获取财务数据"""
        # Setup mocks
        mock_format.return_value = "000001"
        mock_ak_fin.return_value = pd.DataFrame(
            {"报告期": ["2024-12-31", "2023-12-31"], "营业收入": [1000000, 900000], "净利润": [100000, 90000]}
        )

        # Execute
        result = self.adapter.get_financial_data("000001.SZ")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)

    @patch("src.adapters.akshare_adapter.ak.stock_financial_abstract")
    @patch("src.adapters.akshare_adapter.format_stock_code_for_source")
    def test_get_financial_data_empty(self, mock_format, mock_ak_fin):
        """测试获取空数据"""
        # Setup mocks
        mock_format.return_value = "000001"
        mock_ak_fin.return_value = pd.DataFrame()

        # Execute
        result = self.adapter.get_financial_data("000001.SZ")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)


class TestAkshareDataSourceNewsData(unittest.TestCase):
    """测试新闻数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.stock_news_em")
    @patch("src.adapters.akshare_adapter.format_stock_code_for_source")
    def test_get_news_data_with_symbol(self, mock_format, mock_ak_news):
        """测试获取个股新闻"""
        # Setup mocks
        mock_format.return_value = "000001"
        mock_ak_news.return_value = pd.DataFrame(
            {
                "新闻标题": ["标题1", "标题2", "标题3"],
                "发布时间": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "新闻来源": ["来源1", "来源2", "来源3"],
            }
        )

        # Execute
        result = self.adapter.get_news_data(symbol="000001.SZ", limit=2)

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("新闻标题", result[0])

    @patch("src.adapters.akshare_adapter.ak.stock_news_em")
    def test_get_news_data_market_news(self, mock_ak_news):
        """测试获取市场新闻"""
        # Setup mocks
        mock_ak_news.return_value = pd.DataFrame({"新闻标题": ["市场标题1", "市场标题2"]})

        # Execute
        result = self.adapter.get_news_data(symbol=None, limit=10)

        # Verify
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)


class TestAkshareDataSourceTHSIndustry(unittest.TestCase):
    """测试同花顺行业数据获取功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.stock_board_industry_summary_ths")
    def test_get_ths_industry_summary_success(self, mock_ak_industry):
        """测试成功获取同花顺行业一览表"""
        # Setup mocks
        mock_ak_industry.return_value = pd.DataFrame(
            {
                "行业": ["银行", "房地产", "白酒"],
                "最新价": [1000.0, 2000.0, 3000.0],
                "涨跌幅": [1.5, -2.0, 0.8],
                "成交量": [1000000, 2000000, 3000000],
            }
        )

        # Execute
        result = self.adapter.get_ths_industry_summary()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn("数据获取时间", result.columns)

    @patch("src.adapters.akshare_adapter.ak.stock_board_industry_cons_em")
    def test_get_ths_industry_stocks_success(self, mock_ak_stocks):
        """测试成功获取行业成分股"""
        # Setup mocks
        mock_ak_stocks.return_value = pd.DataFrame(
            {
                "代码": ["000001.SZ", "600000.SH"],
                "名称": ["平安银行", "浦发银行"],
                "最新价": [10.5, 8.5],
                "涨跌幅": [1.2, -0.5],
            }
        )

        # Execute
        result = self.adapter.get_ths_industry_stocks("银行")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("所属行业", result.columns)
        self.assertIn("数据获取时间", result.columns)

    @patch("src.adapters.akshare_adapter.ak.stock_board_industry_name_ths")
    def test_get_ths_industry_names_success(self, mock_ak_names):
        """测试成功获取行业名称列表"""
        # Setup mocks
        mock_ak_names.return_value = pd.DataFrame(
            {"name": ["银行", "房地产", "白酒"], "code": ["BK0001", "BK0002", "BK0003"]}
        )

        # Execute
        result = self.adapter.get_ths_industry_names()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn("数据获取时间", result.columns)


class TestAkshareDataSourceMinuteKline(unittest.TestCase):
    """测试分钟K线功能（空实现）"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.logger")
    def test_get_minute_kline_returns_empty(self, mock_logger):
        """测试分钟K线返回空DataFrame"""
        # Execute
        result = self.adapter.get_minute_kline("000001.SZ", "1m", "2025-01-01", "2025-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        mock_logger.info.assert_called()


class TestAkshareDataSourceClassify(unittest.TestCase):
    """测试行业/概念分类功能"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    @patch("src.adapters.akshare_adapter.ak.stock_board_industry_name_em")
    def test_get_industry_classify_success(self, mock_ak_industry):
        """测试成功获取行业分类"""
        # Setup mocks
        mock_ak_industry.return_value = pd.DataFrame(
            {
                "板块代码": ["BK0001", "BK0002"],
                "板块名称": ["银行", "房地产"],
                "最新价": [1000.0, 2000.0],
                "上涨家数": [20, 15],
                "下跌家数": [10, 20],
            }
        )

        # Execute
        result = self.adapter.get_industry_classify()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("index", result.columns)
        self.assertIn("name", result.columns)
        self.assertIn("stock_count", result.columns)

    @patch("src.adapters.akshare_adapter.ak.stock_board_concept_name_em")
    def test_get_concept_classify_success(self, mock_ak_concept):
        """测试成功获取概念分类"""
        # Setup mocks
        mock_ak_concept.return_value = pd.DataFrame(
            {
                "板块代码": ["BK1001", "BK1002"],
                "板块名称": ["人工智能", "新能源汽车"],
                "最新价": [1500.0, 2500.0],
                "上涨家数": [25, 30],
                "下跌家数": [5, 10],
            }
        )

        # Execute
        result = self.adapter.get_concept_classify()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("index", result.columns)
        self.assertIn("name", result.columns)
        self.assertIn("stock_count", result.columns)

    @patch("src.adapters.akshare_adapter.ak.stock_individual_info_em")
    def test_get_stock_industry_concept_success(self, mock_ak_info):
        """测试成功获取个股行业概念信息"""
        # Setup mocks
        mock_ak_info.return_value = pd.DataFrame(
            {"item": ["行业", "概念", "主营业务"], "value": ["银行", "金融科技,数字货币", "银行业务"]}
        )

        # Execute
        result = self.adapter.get_stock_industry_concept("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertIn("symbol", result)
        self.assertIn("industries", result)
        self.assertIn("concepts", result)
        self.assertEqual(len(result["industries"]), 1)
        self.assertEqual(len(result["concepts"]), 2)  # 金融科技,数字货币


if __name__ == "__main__":
    unittest.main(verbosity=2)
