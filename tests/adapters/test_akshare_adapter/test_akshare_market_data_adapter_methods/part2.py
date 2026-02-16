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


class TestAkshareMarketDataAdapterTestGetStockMixin:
    """TestAkshareMarketDataAdapter 方法集 Part 2"""

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

