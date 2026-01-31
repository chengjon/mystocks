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

以及市场总貌数据适配器：
- 上海证券交易所市场总貌
- 深圳证券交易所市场总貌
- 深圳地区交易排序数据
- 深圳行业成交数据
- 上海交易所每日概况

创建日期: 2026-01-03
Phase: 2 - Task 2.2.1
更新日期: 2026-01-10
Phase: 1 - Task 1.8 (添加市场总貌数据测试)
"""

import asyncio
import unittest
from unittest.mock import patch, AsyncMock

import pandas as pd

from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter
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

    @patch("src.adapters.akshare.base.logger")
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
        self, mock_mapper, mock_normalize, mock_format, mock_ak_hist, mock_ak_spot
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

    @patch("misc_data.logger", create=True)
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


class TestAkshareMarketDataAdapter(unittest.IsolatedAsyncioTestCase):
    """测试AkShare市场总貌数据适配器"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareMarketDataAdapter()

    def test_init(self):
        """测试适配器初始化"""
        self.assertIsNotNone(self.adapter)
        self.assertIsNotNone(self.adapter.logger)

    @patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_sse_summary", create=True)
    async def test_get_market_overview_sse_success(self, mock_sse_summary):
        """测试成功获取上海证券交易所市场总貌"""
        # Setup mocks
        mock_sse_summary.return_value = pd.DataFrame(
            {
                "指数代码": ["000001", "000002"],
                "指数名称": ["上证指数", "上证A股"],
                "昨收": [3200.0, 3100.0],
                "今开": [3250.0, 3150.0],
                "最新价": [3280.0, 3180.0],
                "涨跌幅": [2.5, 2.58],
                "成交量": [1000000, 900000],
                "成交额": [50000000, 45000000],
            }
        )

        # Execute
        result = await self.adapter.get_market_overview_sse()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("index_code", result.columns)
        self.assertIn("index_name", result.columns)
        self.assertIn("latest_price", result.columns)
        self.assertIn("change_percent", result.columns)
        self.assertIn("query_timestamp", result.columns)

    @patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_szse_summary", create=True)
    async def test_get_market_overview_szse_success(self, mock_szse_summary):
        """测试成功获取深圳证券交易所市场总貌"""
        # Setup mocks
        mock_szse_summary.return_value = pd.DataFrame(
            {
                "板块": ["主板", "创业板", "中小板"],
                "涨跌幅": [1.5, 2.0, -0.5],
                "总市值": [1000000000, 500000000, 300000000],
                "平均市盈率": [15.5, 25.0, 20.0],
                "换手率": [1.2, 2.5, 1.8],
                "上涨家数": [1200, 800, 500],
                "下跌家数": [800, 600, 400],
            }
        )

        # Execute
        result = await self.adapter.get_market_overview_szse("2024-01-15")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn("sector", result.columns)
        self.assertIn("change_percent", result.columns)
        self.assertIn("query_date", result.columns)
        self.assertIn("query_timestamp", result.columns)

    @patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_szse_area_summary", create=True)
    async def test_get_szse_area_trading_success(self, mock_area_summary):
        """测试成功获取深圳地区交易排序数据"""
        # Setup mocks
        mock_area_summary.return_value = pd.DataFrame(
            {
                "地区": ["深圳", "北京", "上海"],
                "总市值": [500000000, 300000000, 400000000],
                "平均市盈率": [18.5, 22.0, 20.5],
                "涨跌幅": [1.8, -0.5, 2.2],
                "换手率": [2.1, 1.5, 1.8],
                "上涨家数": [150, 80, 120],
                "下跌家数": [100, 60, 90],
            }
        )

        # Execute
        result = await self.adapter.get_szse_area_trading_summary("2024-01-15")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn("region", result.columns)
        self.assertIn("change_percent", result.columns)
        self.assertIn("query_date", result.columns)

    @patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_szse_sector_summary", create=True)
    async def test_get_szse_sector_trading_success(self, mock_sector_summary):
        """测试成功获取深圳行业成交数据"""
        # Setup mocks
        mock_sector_summary.return_value = pd.DataFrame(
            {
                "板块代码": ["BK0477", "BK0478"],
                "板块名称": ["银行", "房地产"],
                "涨跌幅": [1.5, -0.8],
                "总市值": [200000000, 150000000],
                "换手率": [1.2, 0.8],
                "上涨家数": [25, 15],
                "下跌家数": [15, 20],
            }
        )

        # Execute
        result = await self.adapter.get_szse_sector_trading_summary("BK0477", "2024-01-15")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("sector_code", result.columns)
        self.assertIn("sector_name", result.columns)
        self.assertIn("query_symbol", result.columns)
        self.assertIn("query_date", result.columns)

    @patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_sse_deal_daily", create=True)
    async def test_get_sse_daily_deal_success(self, mock_sse_deal):
        """测试成功获取上海交易所每日概况"""
        # Setup mocks
        mock_sse_deal.return_value = pd.DataFrame(
            {
                "项目": ["股票", "债券", "基金"],
                "数量": [1500, 800, 200],
                "金额": [50000000, 30000000, 10000000],
                "占总计": [55.6, 33.3, 11.1],
            }
        )

        # Execute
        result = await self.adapter.get_sse_daily_deal_summary("2024-01-15")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn("item", result.columns)
        self.assertIn("count", result.columns)
        self.assertIn("amount", result.columns)
        self.assertIn("percentage", result.columns)
        self.assertIn("query_date", result.columns)

    async def test_get_market_overview_sse_empty_data(self):
        """测试SSE市场总貌返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_sse_summary", create=True) as mock_sse:
            mock_sse.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_market_overview_sse()

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_market_overview_szse_empty_data(self):
        """测试SZSE市场总貌返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_szse_summary", create=True) as mock_szse:
            mock_szse.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_market_overview_szse("2024-01-15")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_szse_area_trading_empty_data(self):
        """测试SZSE地区交易返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_szse_area_summary", create=True) as mock_area:
            mock_area.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_szse_area_trading_summary("2024-01-15")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_szse_sector_trading_empty_data(self):
        """测试SZSE行业成交返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_szse_sector_summary", create=True) as mock_sector:
            mock_sector.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_szse_sector_trading_summary("BK0477", "2024-01-15")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_sse_daily_deal_empty_data(self):
        """测试SSE每日概况返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.market_overview.ak.stock_sse_deal_daily", create=True) as mock_deal:
            mock_deal.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_sse_daily_deal_summary("2024-01-15")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    # ============================================================================
    # Phase 2: 个股信息数据测试
    # ============================================================================

    @patch("src.adapters.akshare.market_adapter.stock_profile.ak.stock_individual_info_em", create=True)
    async def test_get_stock_individual_info_em_success(self, mock_individual_info):
        """测试成功获取个股信息查询-东财"""
        # Setup mocks
        mock_individual_info.return_value = pd.DataFrame(
            {"item": ["总市值", "每股净资产", "净利润"], "value": ["500000000", "8.5", "100000000"]}
        )

        # Execute
        result = await self.adapter.get_stock_individual_info_em("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result["symbol"], "000001")
        self.assertIn("query_timestamp", result)
        self.assertEqual(len([k for k in result.keys() if k not in ["symbol", "query_timestamp"]]), 3)

    @patch("src.adapters.akshare.market_adapter.stock_profile.ak.stock_individual_basic_info_xq", create=True)
    async def test_get_stock_individual_basic_info_xq_success(self, mock_basic_info_xq):
        """测试成功获取个股信息查询-雪球"""
        # Setup mocks
        mock_basic_info_xq.return_value = pd.DataFrame(
            {"item": ["当前价", "涨跌幅", "市值"], "value": ["25.5", "2.1%", "500亿"]}
        )

        # Execute
        result = await self.adapter.get_stock_individual_basic_info_xq("SZ000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result["symbol"], "SZ000001")
        self.assertIn("query_timestamp", result)

    @patch("src.adapters.akshare.market_adapter.stock_profile.ak.stock_zyjs_ths", create=True)
    async def test_get_stock_zyjs_ths_success(self, mock_zyjs_ths):
        """测试成功获取主营介绍-同花顺"""
        # Setup mocks
        mock_zyjs_ths.return_value = pd.DataFrame(
            {"item": ["公司简介", "主营业务"], "value": ["某某银行股份有限公司", "商业银行业务"]}
        )

        # Execute
        result = await self.adapter.get_stock_zyjs_ths("000001")

        # Verify
        self.assertIsInstance(result, dict)
        self.assertEqual(result["symbol"], "000001")
        self.assertIn("query_timestamp", result)

    @patch("src.adapters.akshare.market_adapter.stock_profile.ak.stock_zygc_em", create=True)
    async def test_get_stock_zygc_em_success(self, mock_zygc_em):
        """测试成功获取主营构成-东财"""
        # Setup mocks
        mock_zygc_em.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "000001"],
                "业务板块": ["利息收入", "手续费收入"],
                "营业收入": ["50000000", "20000000"],
                "收入占比": ["70%", "30%"],
                "利润": ["30000000", "10000000"],
                "利润占比": ["75%", "25%"],
                "报告期": ["2024Q1", "2024Q1"],
            }
        )

        # Execute
        result = await self.adapter.get_stock_zygc_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("business_segment", result.columns)
        self.assertIn("query_timestamp", result.columns)

    @patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_comment_em", create=True)
    async def test_get_stock_comment_em_success(self, mock_comment_em):
        """测试成功获取千股千评"""
        # Setup mocks
        mock_comment_em.return_value = pd.DataFrame(
            {
                "股票代码": ["000001"],
                "分析师数量": [25],
                "平均评级": ["增持"],
                "买入": [10],
                "增持": [8],
                "中性": [5],
                "减持": [1],
                "卖出": [1],
                "平均目标价": [12.5],
                "最高目标价": [15.0],
                "最低目标价": [10.0],
            }
        )

        # Execute
        result = await self.adapter.get_stock_comment_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn("symbol", result.columns)
        self.assertIn("analyst_count", result.columns)
        self.assertIn("query_timestamp", result.columns)

    @patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_comment_detail_zlkp_jgcyd_em", create=True)
    async def test_get_stock_comment_detail_em_success(self, mock_comment_detail):
        """测试成功获取千股千评详情"""
        # Setup mocks
        mock_comment_detail.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "000001"],
                "分析师": ["张三", "李四"],
                "机构": ["中信证券", "国泰君安"],
                "评级": ["买入", "增持"],
                "目标价": [13.5, 12.8],
                "报告日期": ["2024-01-15", "2024-01-10"],
                "报告标题": ["2024年投资策略", "年度业绩分析"],
            }
        )

        # Execute
        result = await self.adapter.get_stock_comment_detail_zlkp_jgcyd_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("analyst_name", result.columns)
        self.assertIn("organization", result.columns)

    @patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_news_em", create=True)
    async def test_get_stock_news_em_success(self, mock_news_em):
        """测试成功获取个股新闻"""
        # Setup mocks
        mock_news_em.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "000001"],
                "标题": ["某某银行业绩超预期", "某某银行获评最佳银行"],
                "内容": ["某某银行发布2024年Q1业绩...", "某某银行荣获2024年度最佳银行称号..."],
                "发布时间": ["2024-01-15 09:30:00", "2024-01-14 14:20:00"],
                "来源": ["东方财富", "同花顺"],
                "链接": ["http://news1.com", "http://news2.com"],
            }
        )

        # Execute
        result = await self.adapter.get_stock_news_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("title", result.columns)
        self.assertIn("content", result.columns)

    @patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_bid_ask_em", create=True)
    async def test_get_stock_bid_ask_em_success(self, mock_bid_ask):
        """测试成功获取行情报价"""
        # Setup mocks
        mock_bid_ask.return_value = pd.DataFrame(
            {
                "股票代码": ["000001"],
                "买一价": [11.5],
                "买一量": [1000],
                "卖一价": [11.6],
                "卖一量": [800],
                "买二价": [11.4],
                "买二量": [1500],
                "卖二价": [11.7],
                "卖二量": [1200],
                "买三价": [11.3],
                "买三量": [2000],
                "卖三价": [11.8],
                "卖三量": [900],
                "买四价": [11.2],
                "买四量": [1800],
                "卖四价": [11.9],
                "卖四量": [1100],
                "买五价": [11.1],
                "买五量": [2200],
                "卖五价": [12.0],
                "卖五量": [700],
            }
        )

        # Execute
        result = await self.adapter.get_stock_bid_ask_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn("symbol", result.columns)
        self.assertIn("bid_price_1", result.columns)
        self.assertIn("ask_price_1", result.columns)

    # 测试空数据情况
    async def test_get_stock_individual_info_em_empty_data(self):
        """测试个股信息查询-东财返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.stock_profile.ak.stock_individual_info_em", create=True) as mock_individual:
            mock_individual.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_individual_info_em("000001")

            # Verify
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)
            self.assertEqual(result["error"], "No data found")

    async def test_get_stock_zygc_em_empty_data(self):
        """测试主营构成-东财返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.stock_profile.ak.stock_zygc_em", create=True) as mock_zygc:
            mock_zygc.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_zygc_em("000001")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_comment_em_empty_data(self):
        """测试千股千评返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_comment_em", create=True) as mock_comment:
            mock_comment.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_comment_em("000001")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_news_em_empty_data(self):
        """测试个股新闻返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_news_em", create=True) as mock_news:
            mock_news.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_news_em("000001")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_bid_ask_em_empty_data(self):
        """测试行情报价返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_bid_ask_em", create=True) as mock_bid_ask:
            mock_bid_ask.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_bid_ask_em("000001")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    # ============================================================================
    # Phase 3: 资金流向数据测试
    # ============================================================================

    @patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_fund_flow_summary_em", create=True)
    async def test_get_stock_hsgt_fund_flow_summary_em_success(self, mock_hsgt_summary):
        """测试成功获取沪深港通资金流向汇总"""
        # Setup mocks
        mock_hsgt_summary.return_value = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "北向资金": [10000000, 15000000],
                "南向资金": [8000000, 12000000],
                "当日额度": [50000000, 50000000],
                "当日余额": [45000000, 40000000],
                "当日使用额度": [5000000, 10000000],
            }
        )

        # Execute
        result = await self.adapter.get_stock_hsgt_fund_flow_summary_em("2024-01-01", "2024-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("date", result.columns)
        self.assertIn("north_money", result.columns)
        self.assertIn("south_money", result.columns)

    @patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_fund_flow_detail_em", create=True)
    async def test_get_stock_hsgt_fund_flow_detail_em_success(self, mock_hsgt_detail):
        """测试成功获取沪深港通资金流向明细"""
        # Setup mocks
        mock_hsgt_detail.return_value = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "市场": ["沪股通", "深股通"],
                "资金方向": ["买入", "卖出"],
                "资金金额": [10000000, 8000000],
                "买入金额": [10000000, 0],
                "卖出金额": [0, 8000000],
                "净流入": [10000000, -8000000],
            }
        )

        # Execute
        result = await self.adapter.get_stock_hsgt_fund_flow_detail_em("2024-01-01", "2024-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("date", result.columns)
        self.assertIn("market", result.columns)
        self.assertIn("direction", result.columns)

    @patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_north_net_flow_in_em", create=True)
    async def test_get_stock_hsgt_north_net_flow_in_em_success(self, mock_north_flow):
        """测试成功获取北向资金每日统计"""
        # Setup mocks
        mock_north_flow.return_value = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "净流入": [10000000, 8000000],
                "买入金额": [15000000, 12000000],
                "卖出金额": [5000000, 4000000],
                "累计净流入": [50000000, 58000000],
            }
        )

        # Execute
        result = await self.adapter.get_stock_hsgt_north_net_flow_in_em("2024-01-01", "2024-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("date", result.columns)
        self.assertIn("net_flow", result.columns)
        self.assertIn("fund_direction", result.columns)
        self.assertEqual(result["fund_direction"].iloc[0], "north")

    @patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_south_net_flow_in_em", create=True)
    async def test_get_stock_hsgt_south_net_flow_in_em_success(self, mock_south_flow):
        """测试成功获取南向资金每日统计"""
        # Setup mocks
        mock_south_flow.return_value = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "净流入": [8000000, 6000000],
                "买入金额": [12000000, 10000000],
                "卖出金额": [4000000, 4000000],
                "累计净流入": [30000000, 36000000],
            }
        )

        # Execute
        result = await self.adapter.get_stock_hsgt_south_net_flow_in_em("2024-01-01", "2024-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("fund_direction", result.columns)
        self.assertEqual(result["fund_direction"].iloc[0], "south")

    @patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_north_acc_flow_in_em", create=True)
    async def test_get_stock_hsgt_north_acc_flow_in_em_success(self, mock_north_stock):
        """测试成功获取北向资金个股统计"""
        # Setup mocks
        mock_north_stock.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "000001"],
                "日期": ["2024-01-01", "2024-01-02"],
                "持股数量": [1000000, 1100000],
                "持股市值": [15000000, 16500000],
                "持股变化数量": [100000, 0],
                "持股变化市值": [1500000, 0],
            }
        )

        # Execute
        result = await self.adapter.get_stock_hsgt_north_acc_flow_in_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("hold_amount", result.columns)
        self.assertIn("fund_direction", result.columns)

    @patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_south_acc_flow_in_em", create=True)
    async def test_get_stock_hsgt_south_acc_flow_in_em_success(self, mock_south_stock):
        """测试成功获取南向资金个股统计"""
        # Setup mocks
        mock_south_stock.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "000001"],
                "日期": ["2024-01-01", "2024-01-02"],
                "持股数量": [500000, 550000],
                "持股市值": [7500000, 8250000],
                "持股变化数量": [50000, 0],
                "持股变化市值": [750000, 0],
            }
        )

        # Execute
        result = await self.adapter.get_stock_hsgt_south_acc_flow_in_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("fund_direction", result.columns)
        self.assertEqual(result["fund_direction"].iloc[0], "south")

    @patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_hold_stock_em", create=True)
    async def test_get_stock_hsgt_hold_stock_em_success(self, mock_hsgt_hold):
        """测试成功获取沪深港通持股明细"""
        # Setup mocks
        mock_hsgt_hold.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "000001"],
                "日期": ["2024-01-01", "2024-01-02"],
                "参与者名称": ["中央汇金", "全国社保"],
                "持股数量": [500000, 300000],
                "持股比例": ["1.5%", "0.9%"],
                "市场类型": ["沪股通", "沪股通"],
            }
        )

        # Execute
        result = await self.adapter.get_stock_hsgt_hold_stock_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("participant_name", result.columns)
        self.assertIn("hold_ratio", result.columns)

    @patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_fund_flow_big_deal", create=True)
    async def test_get_stock_fund_flow_big_deal_success(self, mock_big_deal):
        """测试成功获取资金流向大单统计"""
        # Setup mocks
        mock_big_deal.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "600000"],
                "股票名称": ["平安银行", "浦发银行"],
                "大单成交金额": [50000000, 30000000],
                "大单买入金额": [40000000, 25000000],
                "大单卖出金额": [10000000, 5000000],
                "大单净流入": [30000000, 20000000],
            }
        )

        # Execute
        result = await self.adapter.get_stock_fund_flow_big_deal()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("name", result.columns)
        self.assertIn("big_deal_amount", result.columns)

    @patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_cyq_em", create=True)
    async def test_get_stock_cyq_em_success(self, mock_cyq):
        """测试成功获取筹码分布数据"""
        # Setup mocks
        mock_cyq.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "000001", "000001"],
                "价格区间": ["5.0-10.0", "10.0-15.0", "15.0-20.0"],
                "筹码数量": [1000000, 2000000, 1500000],
                "筹码占比": ["20%", "40%", "30%"],
                "集中度": [0.8, 0.6, 0.4],
            }
        )

        # Execute
        result = await self.adapter.get_stock_cyq_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn("symbol", result.columns)
        self.assertIn("price_range", result.columns)
        self.assertIn("chip_amount", result.columns)

    # 测试空数据情况
    async def test_get_stock_hsgt_fund_flow_summary_em_empty_data(self):
        """测试沪深港通资金流向汇总返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_fund_flow_summary_em", create=True) as mock_hsgt_summary:
            mock_hsgt_summary.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_hsgt_fund_flow_summary_em("2024-01-01", "2024-01-02")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_hsgt_north_net_flow_in_em_empty_data(self):
        """测试北向资金每日统计返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_north_net_flow_in_em", create=True) as mock_north_flow:
            mock_north_flow.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_hsgt_north_net_flow_in_em("2024-01-01", "2024-01-02")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_hsgt_north_acc_flow_in_em_empty_data(self):
        """测试北向资金个股统计返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_hsgt_north_acc_flow_in_em", create=True) as mock_north_stock:
            mock_north_stock.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_hsgt_north_acc_flow_in_em("000001")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_fund_flow_big_deal_empty_data(self):
        """测试资金流向大单统计返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_fund_flow_big_deal", create=True) as mock_big_deal:
            mock_big_deal.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_fund_flow_big_deal()

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_cyq_em_empty_data(self):
        """测试筹码分布数据返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.fund_flow.ak.stock_cyq_em", create=True) as mock_cyq:
            mock_cyq.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_cyq_em("000001")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    # ============================================================================
    # Phase 4: 预测和分析数据测试
    # ============================================================================

    @patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_profit_forecast_em", create=True)
    async def test_get_stock_profit_forecast_em_success(self, mock_profit_forecast):
        """测试成功获取盈利预测-东方财富"""
        # Setup mocks
        mock_profit_forecast.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "000001"],
                "年度": [2024, 2025],
                "季度": ["Q1", "Q1"],
                "预测每股收益": [1.2, 1.5],
                "预测净利润": [100000000, 120000000],
                "预测增长率": [15.5, 18.2],
                "分析师数量": [25, 28],
                "机构名称": ["中信证券", "国泰君安"],
            }
        )

        # Execute
        result = await self.adapter.get_stock_profit_forecast_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("year", result.columns)
        self.assertIn("eps_forecast", result.columns)
        self.assertIn("forecast_source", result.columns)
        self.assertEqual(result["forecast_source"].iloc[0], "em")

    @patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_profit_forecast_ths", create=True)
    async def test_get_stock_profit_forecast_ths_success(self, mock_profit_forecast_ths):
        """测试成功获取盈利预测-同花顺"""
        # Setup mocks
        mock_profit_forecast_ths.return_value = pd.DataFrame(
            {
                "股票代码": ["000001", "000001"],
                "报告日期": ["2024-01-15", "2024-01-20"],
                "预测类型": ["年度", "年度"],
                "每股收益预测": [1.2, 1.3],
                "营收预测": [500000000, 520000000],
                "净利润预测": [100000000, 110000000],
                "市盈率预测": [12.5, 13.2],
                "分析师评级": ["买入", "增持"],
            }
        )

        # Execute
        result = await self.adapter.get_stock_profit_forecast_ths("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("report_date", result.columns)
        self.assertIn("eps_forecast", result.columns)
        self.assertIn("forecast_source", result.columns)
        self.assertEqual(result["forecast_source"].iloc[0], "ths")

    @patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_technical_indicator_em", create=True)
    async def test_get_stock_technical_indicator_em_success(self, mock_technical_indicator):
        """测试成功获取技术指标数据"""
        # Setup mocks
        mock_technical_indicator.return_value = pd.DataFrame(
            {
                "股票代码": ["000001"],
                "日期": ["2024-01-15"],
                "MA5": [11.2],
                "MA10": [11.5],
                "MA20": [11.8],
                "MA30": [12.0],
                "MA60": [12.2],
                "MACD": [0.15],
                "MACD信号": [0.12],
                "MACD柱状图": [0.03],
                "RSI": [65.5],
                "KDJ_K": [70.2],
                "KDJ_D": [68.5],
                "KDJ_J": [73.4],
                "布林线上轨": [12.5],
                "布林线中轨": [11.8],
                "布林线下轨": [11.1],
            }
        )

        # Execute
        result = await self.adapter.get_stock_technical_indicator_em("000001")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn("symbol", result.columns)
        self.assertIn("date", result.columns)
        self.assertIn("ma5", result.columns)
        self.assertIn("macd", result.columns)
        self.assertIn("rsi", result.columns)
        self.assertIn("boll_upper", result.columns)

    @patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_account_statistics_em", create=True)
    async def test_get_stock_account_statistics_em_success(self, mock_account_statistics):
        """测试成功获取股票账户统计月度"""
        # Setup mocks
        mock_account_statistics.return_value = pd.DataFrame(
            {
                "日期": ["2024-01"],
                "期末总账户数": [200000000],
                "期末活跃账户数": [150000000],
                "新增账户数": [5000000],
                "休眠账户数": [45000000],
                "交易账户数": [120000000],
                "股票账户数": [180000000],
                "基金账户数": [15000000],
                "债券账户数": [8000000],
            }
        )

        # Execute
        result = await self.adapter.get_stock_account_statistics_em("2024-01")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn("date", result.columns)
        self.assertIn("total_accounts", result.columns)
        self.assertIn("active_accounts", result.columns)
        self.assertIn("trading_accounts", result.columns)

    # 测试空数据情况
    async def test_get_stock_profit_forecast_em_empty_data(self):
        """测试盈利预测-东方财富返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_profit_forecast_em", create=True) as mock_profit:
            mock_profit.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_profit_forecast_em("000001")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_profit_forecast_ths_empty_data(self):
        """测试盈利预测-同花顺返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_profit_forecast_ths", create=True) as mock_profit_ths:
            mock_profit_ths.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_profit_forecast_ths("000001")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_technical_indicator_em_empty_data(self):
        """测试技术指标数据返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_technical_indicator_em", create=True) as mock_technical:
            mock_technical.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_technical_indicator_em("000001")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_account_statistics_em_empty_data(self):
        """测试股票账户统计月度返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_account_statistics_em", create=True) as mock_account:
            mock_account.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_account_statistics_em("2024-01")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    # ============================================================================
    # Phase 5: 板块和行业数据测试
    # ============================================================================

    @patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_board_concept_cons_em", create=True)
    async def test_get_stock_board_concept_cons_em_success(self, mock_concept_cons):
        """测试成功获取概念板块成分股"""
        # Setup mocks
        mock_concept_cons.return_value = pd.DataFrame(
            {
                "代码": ["000001", "000002"],
                "名称": ["平安银行", "万科A"],
                "最新价": [11.5, 15.8],
                "涨跌幅": [2.1, -0.8],
                "成交量": [1000000, 500000],
                "成交额": [11500000, 7900000],
                "市值": [200000000000, 150000000000],
                "市盈率-动态": [8.5, 12.3],
                "市净率": [0.85, 1.2],
            }
        )

        # Execute
        result = await self.adapter.get_stock_board_concept_cons_em("BK0477")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("name", result.columns)
        self.assertIn("concept_code", result.columns)
        self.assertEqual(result["concept_code"].iloc[0], "BK0477")

    @patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_board_concept_hist_em", create=True)
    async def test_get_stock_board_concept_hist_em_success(self, mock_concept_hist):
        """测试成功获取概念板块行情"""
        # Setup mocks
        mock_concept_hist.return_value = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "开盘": [11.0, 11.5],
                "收盘": [11.5, 12.0],
                "最高": [11.8, 12.2],
                "最低": [10.8, 11.3],
                "成交量": [1000000, 1200000],
                "成交额": [11500000, 13800000],
                "振幅": [8.2, 7.8],
                "涨跌幅": [5.0, 4.3],
                "涨跌额": [0.55, 0.5],
                "换手率": [2.1, 2.5],
            }
        )

        # Execute
        result = await self.adapter.get_stock_board_concept_hist_em("BK0477", "2024-01-01", "2024-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("date", result.columns)
        self.assertIn("open", result.columns)
        self.assertIn("close", result.columns)
        self.assertIn("concept_code", result.columns)

    @patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_board_concept_hist_min_em", create=True)
    async def test_get_stock_board_concept_hist_min_em_success(self, mock_concept_min):
        """测试成功获取概念板块分钟行情"""
        # Setup mocks
        mock_concept_min.return_value = pd.DataFrame(
            {"时间": ["2024-01-15 09:30:00", "2024-01-15 09:31:00"], "价格": [11.5, 11.6], "成交量": [10000, 15000]}
        )

        # Execute
        result = await self.adapter.get_stock_board_concept_hist_min_em("BK0477")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("datetime", result.columns)
        self.assertIn("price", result.columns)
        self.assertIn("concept_code", result.columns)

    @patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_board_industry_cons_em", create=True)
    async def test_get_stock_board_industry_cons_em_success(self, mock_industry_cons):
        """测试成功获取行业板块成分股"""
        # Setup mocks
        mock_industry_cons.return_value = pd.DataFrame(
            {
                "代码": ["000001", "600000"],
                "名称": ["平安银行", "浦发银行"],
                "最新价": [11.5, 8.8],
                "涨跌幅": [2.1, 1.8],
                "成交量": [1000000, 800000],
                "成交额": [11500000, 7040000],
                "市值": [200000000000, 180000000000],
                "市盈率-动态": [8.5, 9.2],
                "市净率": [0.85, 0.92],
            }
        )

        # Execute
        result = await self.adapter.get_stock_board_industry_cons_em("BK0477")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("industry_code", result.columns)
        self.assertEqual(result["industry_code"].iloc[0], "BK0477")

    @patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_board_industry_hist_em", create=True)
    async def test_get_stock_board_industry_hist_em_success(self, mock_industry_hist):
        """测试成功获取行业板块行情"""
        # Setup mocks
        mock_industry_hist.return_value = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "开盘": [11.0, 11.5],
                "收盘": [11.5, 12.0],
                "最高": [11.8, 12.2],
                "最低": [10.8, 11.3],
                "成交量": [2000000, 2200000],
                "成交额": [23000000, 25200000],
                "振幅": [8.2, 7.8],
                "涨跌幅": [5.0, 4.3],
                "涨跌额": [0.55, 0.5],
                "换手率": [4.2, 4.8],
            }
        )

        # Execute
        result = await self.adapter.get_stock_board_industry_hist_em("BK0477", "2024-01-01", "2024-01-02")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("industry_code", result.columns)
        self.assertEqual(result["industry_code"].iloc[0], "BK0477")

    @patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_board_industry_hist_min_em", create=True)
    async def test_get_stock_board_industry_hist_min_em_success(self, mock_industry_min):
        """测试成功获取行业板块分钟行情"""
        # Setup mocks
        mock_industry_min.return_value = pd.DataFrame(
            {"时间": ["2024-01-15 09:30:00", "2024-01-15 09:31:00"], "价格": [11.5, 11.6], "成交量": [20000, 25000]}
        )

        # Execute
        result = await self.adapter.get_stock_board_industry_hist_min_em("BK0477")

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("industry_code", result.columns)

    @patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_sector_spot_em", create=True)
    async def test_get_stock_sector_spot_em_success(self, mock_sector_spot):
        """测试成功获取热门行业排行"""
        # Setup mocks
        mock_sector_spot.return_value = pd.DataFrame(
            {
                "板块": ["银行", "房地产", "白酒"],
                "板块代码": ["BK0477", "BK0451", "BK0478"],
                "涨跌幅": [2.1, -0.8, 1.5],
                "总市值": [5000000000000, 3000000000000, 4000000000000],
                "换手率": [1.2, 0.8, 1.5],
                "上涨家数": [25, 15, 20],
                "下跌家数": [15, 20, 10],
                "领涨股": ["平安银行", "万科A", "贵州茅台"],
            }
        )

        # Execute
        result = await self.adapter.get_stock_sector_spot_em()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn("sector_name", result.columns)
        self.assertIn("change_percent", result.columns)
        self.assertIn("rise_count", result.columns)

    @patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_sector_fund_flow_rank_em", create=True)
    async def test_get_stock_sector_fund_flow_rank_em_success(self, mock_sector_fund_flow):
        """测试成功获取行业资金流向"""
        # Setup mocks
        mock_sector_fund_flow.return_value = pd.DataFrame(
            {
                "行业板块": ["银行", "房地产", "白酒"],
                "行业代码": ["BK0477", "BK0451", "BK0478"],
                "主力净流入-净额": [100000000, -50000000, 200000000],
                "主力净流入-净占比": [15.5, -8.2, 25.8],
                "超大单净流入": [80000000, -30000000, 150000000],
                "大单净流入": [20000000, -20000000, 50000000],
                "中单净流入": [-10000000, 10000000, -20000000],
                "小单净流入": [-20000000, 20000000, -10000000],
                "行业涨跌幅": [2.1, -0.8, 1.5],
            }
        )

        # Execute
        result = await self.adapter.get_stock_sector_fund_flow_rank_em()

        # Verify
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn("sector_name", result.columns)
        self.assertIn("main_net_inflow", result.columns)
        self.assertIn("super_large_net_inflow", result.columns)

    # 测试空数据情况
    async def test_get_stock_board_concept_cons_em_empty_data(self):
        """测试概念板块成分股返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_board_concept_cons_em", create=True) as mock_concept_cons:
            mock_concept_cons.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_board_concept_cons_em("BK0477")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_board_concept_hist_em_empty_data(self):
        """测试概念板块行情返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_board_concept_hist_em", create=True) as mock_concept_hist:
            mock_concept_hist.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_board_concept_hist_em("BK0477", "2024-01-01", "2024-01-02")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_board_industry_cons_em_empty_data(self):
        """测试行业板块成分股返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_board_industry_cons_em", create=True) as mock_industry_cons:
            mock_industry_cons.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_board_industry_cons_em("BK0477")

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_sector_spot_em_empty_data(self):
        """测试热门行业排行返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_sector_spot_em", create=True) as mock_sector_spot:
            mock_sector_spot.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_sector_spot_em()

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_sector_fund_flow_rank_em_empty_data(self):
        """测试行业资金流向返回空数据"""
        # Setup mocks
        with patch("src.adapters.akshare.market_adapter.board_sector.ak.stock_sector_fund_flow_rank_em", create=True) as mock_sector_fund_flow:
            mock_sector_fund_flow.return_value = pd.DataFrame()

            # Execute
            result = await self.adapter.get_stock_sector_fund_flow_rank_em()

            # Verify
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main(verbosity=2)
