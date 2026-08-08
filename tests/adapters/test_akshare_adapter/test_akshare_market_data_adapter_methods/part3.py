"""
Akshare 市场数据适配器测试 - 分析类方法集
"""

from unittest.mock import patch

import pandas as pd



class TestAkshareMarketDataAdapterAnalyticsMixin:
    """TestAkshareMarketDataAdapter 分析类方法集 Part 3"""

    async def test_get_stock_profit_forecast_em_success(self, mock_profit_forecast):
        """测试成功获取盈利预测-东方财富"""
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

        result = await self.adapter.get_stock_profit_forecast_em("000001")

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("year", result.columns)
        self.assertIn("eps_forecast", result.columns)
        self.assertIn("forecast_source", result.columns)
        self.assertEqual(result["forecast_source"].iloc[0], "em")

    async def test_get_stock_profit_forecast_ths_success(self, mock_profit_forecast_ths):
        """测试成功获取盈利预测-同花顺"""
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

        result = await self.adapter.get_stock_profit_forecast_ths("000001")

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("symbol", result.columns)
        self.assertIn("report_date", result.columns)
        self.assertIn("eps_forecast", result.columns)
        self.assertIn("forecast_source", result.columns)
        self.assertEqual(result["forecast_source"].iloc[0], "ths")

    async def test_get_stock_technical_indicator_em_success(self, mock_technical_indicator):
        """测试成功获取技术指标数据"""
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

        result = await self.adapter.get_stock_technical_indicator_em("000001")

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn("symbol", result.columns)
        self.assertIn("date", result.columns)
        self.assertIn("ma5", result.columns)
        self.assertIn("macd", result.columns)
        self.assertIn("rsi", result.columns)
        self.assertIn("boll_upper", result.columns)

    async def test_get_stock_account_statistics_em_success(self, mock_account_statistics):
        """测试成功获取股票账户统计月度"""
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

        result = await self.adapter.get_stock_account_statistics_em("2024-01")

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn("date", result.columns)
        self.assertIn("total_accounts", result.columns)
        self.assertIn("active_accounts", result.columns)
        self.assertIn("trading_accounts", result.columns)

    async def test_get_stock_profit_forecast_em_empty_data(self):
        """测试盈利预测-东方财富返回空数据"""
        with patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_profit_forecast_em", create=True) as mock_profit:
            mock_profit.return_value = pd.DataFrame()

            result = await self.adapter.get_stock_profit_forecast_em("000001")

            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_profit_forecast_ths_empty_data(self):
        """测试盈利预测-同花顺返回空数据"""
        with patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_profit_forecast_ths", create=True) as mock_profit_ths:
            mock_profit_ths.return_value = pd.DataFrame()

            result = await self.adapter.get_stock_profit_forecast_ths("000001")

            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_technical_indicator_em_empty_data(self):
        """测试技术指标数据返回空数据"""
        with patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_technical_indicator_em", create=True) as mock_technical:
            mock_technical.return_value = pd.DataFrame()

            result = await self.adapter.get_stock_technical_indicator_em("000001")

            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)

    async def test_get_stock_account_statistics_em_empty_data(self):
        """测试股票账户统计月度返回空数据"""
        with patch("src.adapters.akshare.market_adapter.forecast_analysis.ak.stock_account_statistics_em", create=True) as mock_account:
            mock_account.return_value = pd.DataFrame()

            result = await self.adapter.get_stock_account_statistics_em("2024-01")

            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)
