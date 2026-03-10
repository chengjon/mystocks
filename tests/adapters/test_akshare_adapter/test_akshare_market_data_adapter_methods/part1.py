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


class TestAkshareMarketDataAdapterCoreMixin:
    """TestAkshareMarketDataAdapter 方法集 Part 1"""

    def setUp(self):
        """测试前准备"""
        self.adapter = AkshareMarketDataAdapter()

    def test_init(self):
        """测试适配器初始化"""
        self.assertIsNotNone(self.adapter)
        self.assertIsNotNone(self.adapter.logger)

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

