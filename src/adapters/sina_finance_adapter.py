"""
Sina Finance 数据源适配器
Sina Finance Data Source Adapter

实现新浪财经股票评级数据的获取和处理。
"""

import logging
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import random
import requests
from bs4 import BeautifulSoup

from src.adapters.base_adapter import BaseDataSourceAdapter
from src.interfaces import IDataSource

logger = logging.getLogger(__name__)


class SinaFinanceAdapter(BaseDataSourceAdapter, IDataSource):
    """
    新浪财经数据源适配器

    提供新浪财经网站数据的获取和处理，包括股票评级数据等。
    继承BaseDataSourceAdapter获取数据质量检查和基础功能。
    """

    def __init__(self, source_name: str = "sina_finance"):
        """
        初始化新浪财经适配器

        Args:
            source_name: 数据源名称
        """
        super().__init__(source_name)

        # 设置默认请求头，模拟真实浏览器
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # 评级映射表
        self.rating_mapping = {
            "买入": "BUY",
            "增持": "HOLD",
            "中性": "NEUTRAL",
            "减持": "REDUCE",
            "卖出": "SELL",
        }

    def get_sina_stock_ratings(self, max_pages: int = 5) -> pd.DataFrame:
        """
        获取新浪财经股票评级数据

        从新浪财经网站爬取最新的股票评级信息，包括目标价、最新评级、评级机构、分析师等。

        Args:
            max_pages: 最大爬取页数，默认5页

        Returns:
            DataFrame: 包含股票评级数据的DataFrame
                列包括: 股票代码, 股票名称, 目标价, 最新评级, 评级机构, 分析师, 行业, 评级日期, 摘要
        """

        def crawl_table(url: str) -> pd.DataFrame:
            """
            爬取单个页面的评级表格数据
            """
            try:
                response = requests.get(url, headers=self.default_headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", class_="list_table")
                if not table:
                    logger.warning(f"未找到评级表格: {url}")
                    return pd.DataFrame()

                table_data = []
                rows = table.find_all("tr")[1:]  # 跳过表头
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 9:
                        stock_code = cols[0].text.strip()
                        stock_name = cols[1].text.strip()
                        target_price = cols[2].text.strip()
                        rating = cols[3].text.strip()
                        agency = cols[4].text.strip()
                        analyst = cols[5].text.strip()
                        industry = cols[6].text.strip()
                        date = cols[7].text.strip()
                        summary = cols[8].text.strip()

                        table_data.append(
                            {
                                "股票代码": stock_code,
                                "股票名称": stock_name,
                                "目标价": target_price,
                                "最新评级": rating,
                                "评级机构": agency,
                                "分析师": analyst,
                                "行业": industry,
                                "评级日期": date,
                                "摘要": summary,
                            }
                        )

                return pd.DataFrame(table_data)
            except Exception as e:
                logger.error(f"爬取失败: {e}")
                return pd.DataFrame()

        all_data = []
        logger.info(f"开始爬取新浪财经股票评级数据，共{max_pages}页")

        for i in range(1, max_pages + 1):
            url = f"https://stock.finance.sina.com.cn/stock/go.php/vIR_RatingNewest/index.phtml?num=60&p={
                i}"
            logger.info(f"正在爬取第 {i} 页...")

            df = crawl_table(url)
            if df.empty:
                logger.info(f"第 {i} 页未找到表格数据，停止爬取")
                break

            all_data.append(df)

            # 生成0-3秒的随机延迟，避免请求过于频繁
            sleep_time = round(random.uniform(0, 3), 3)
            logger.debug(f"等待 {sleep_time} 秒后继续...")
            time.sleep(sleep_time)

        if all_data:
            result_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"爬取完成！共获取 {len(result_df)} 条评级数据")

            # 应用数据质量检查
            result_df = self._apply_quality_check(result_df, "ALL", "stock_ratings")

            return result_df
        else:
            logger.warning("未获取到任何评级数据")
            return pd.DataFrame()

    # ================ IDataSource 接口实现 ================

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票日线数据

        Sina Finance适配器主要专注于评级数据，此方法返回空DataFrame。
        如需日线数据，请使用其他适配器如akshare或tdx。
        """
        logger.info(f"SinaFinanceAdapter不提供日线数据，请使用其他数据源获取股票 {symbol} 的日线数据")
        return pd.DataFrame()

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据 - 不支持"""
        logger.info("SinaFinanceAdapter不提供指数日线数据")
        return pd.DataFrame()

    def get_stock_basic(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息 - 不支持"""
        logger.info(f"SinaFinanceAdapter不提供股票 {symbol} 的基本信息")
        return {}

    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股 - 不支持"""
        logger.info(f"SinaFinanceAdapter不提供指数 {symbol} 的成分股信息")
        return []

    def get_real_time_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取实时数据 - 不支持"""
        logger.info(f"SinaFinanceAdapter不提供股票 {symbol} 的实时数据")
        return None

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取交易日历 - 不支持"""
        logger.info("SinaFinanceAdapter不提供交易日历数据")
        return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """获取财务数据 - 不支持"""
        logger.info(f"SinaFinanceAdapter不提供股票 {symbol} 的财务数据")
        return pd.DataFrame()

    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取新闻数据

        对于Sina Finance适配器，返回评级数据作为一种特殊的"新闻"数据。
        """
        logger.info("获取新浪财经评级数据作为新闻数据")

        df = self.get_sina_stock_ratings(max_pages=1)  # 只获取第一页作为新闻
        if df.empty:
            return []

        # 转换为新闻格式
        news_list = []
        for _, row in df.head(limit).iterrows():
            news_item = {
                "title": f"{row['股票名称']}({row['股票代码']}) - {row['评级机构']}评级",
                "content": f"评级: {row['最新评级']}, 目标价: {row['目标价']}, 分析师: {row['分析师']}",
                "timestamp": datetime.now().isoformat(),
                "source": "sina_finance_ratings",
                "symbol": row["股票代码"],
            }
            news_list.append(news_item)

        return news_list

    # ================ 扩展方法 ================

    def get_ratings_summary(self) -> Dict[str, Any]:
        """
        获取评级数据汇总统计

        Returns:
            包含评级统计信息的字典
        """
        df = self.get_sina_stock_ratings(max_pages=3)
        if df.empty:
            return {}

        # 计算统计信息
        summary = {
            "total_ratings": len(df),
            "unique_stocks": df["股票代码"].nunique(),
            "rating_agencies": df["评级机构"].nunique(),
            "industries": df["行业"].nunique(),
            "latest_update": datetime.now().isoformat(),
            "rating_distribution": df["最新评级"].value_counts().to_dict(),
        }

        return summary

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            健康检查结果
        """
        try:
            # 尝试获取少量数据进行健康检查
            df = self.get_sina_stock_ratings(max_pages=1)
            return {
                "status": "healthy" if not df.empty else "unhealthy",
                "data_count": len(df),
                "timestamp": datetime.now().isoformat(),
                "source": self.source_name,
            }
        except Exception as e:
            logger.error(f"SinaFinanceAdapter健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "source": self.source_name,
            }
