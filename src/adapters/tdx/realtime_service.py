"""
# 功能：TDX实时数据服务
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：专门处理TDX实时行情数据的服务
"""

from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from .base_tdx_adapter import BaseTdxAdapter


class RealtimeService(BaseTdxAdapter):
    """
    TDX实时数据服务

    专门处理实时行情、板块分类等实时数据
    """

    def __init__(self):
        super().__init__()
        logger.info("TDX实时数据服务初始化完成")

    def get_real_time_data(self, symbol: str) -> Optional[Dict]:
        """获取实时行情数据

        Args:
            symbol: 股票代码

        Returns:
            Dict: 实时行情数据
        """
        try:
            if not symbol:
                raise ValueError("股票代码不能为空")

            # 标准化股票代码
            symbol = self._normalize_symbol(symbol)

            # 获取TDX连接
            tdx_api = self._get_tdx_connection()

            # 获取市场代码
            market_code = self._get_market_code(symbol)

            # 获取实时行情
            logger.info("获取实时行情数据: %s", symbol)
            data = tdx_api.get_security_quotes([symbol], [market_code])

            if not data or len(data) == 0:
                logger.warning("未找到股票 %s 的实时数据", symbol)
                return None

            # 提取第一个数据
            quote_data = data[0]

            # 构建标准化的实时行情格式
            result = {
                "symbol": symbol,
                "name": quote_data.get("name", ""),
                "price": quote_data.get("price", 0),
                "open": quote_data.get("open", 0),
                "high": quote_data.get("high", 0),
                "low": quote_data.get("low", 0),
                "pre_close": quote_data.get("pre_close", 0),
                "change": quote_data.get("change", 0),
                "change_pct": quote_data.get("change_pct", 0),
                "volume": quote_data.get("volume", 0),
                "amount": quote_data.get("amount", 0),
                "turnover": quote_data.get("turnover", 0),
                "pe": quote_data.get("pe", 0),
                "pb": quote_data.get("pb", 0),
                "market": "上交所" if market_code == 1 else "深交所",
                "timestamp": datetime.now().isoformat(),
                "source": "tdx",
            }

            return result

        except Exception as e:
            logger.error("获取实时行情数据失败: %s", e)
            return None

    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            Dict: 股票基本信息
        """
        try:
            if not symbol:
                raise ValueError("股票代码不能为空")

            # 标准化股票代码
            symbol = self._normalize_symbol(symbol)

            # 获取TDX连接
            tdx_api = self._get_tdx_connection()

            # 获取市场代码
            market_code = self._get_market_code(symbol)

            # 获取股票基本信息
            logger.info("获取股票基本信息: %s", symbol)
            data = tdx_api.get_security_list(market_code, 1)

            if not data:
                logger.warning("未找到股票 %s 的基本信息", symbol)
                return {}

            # 查找匹配的股票
            stock_info = None
            for stock in data:
                if stock.get("code") == symbol:
                    stock_info = stock
                    break

            if not stock_info:
                return {}

            # 构建股票基本信息
            result = {
                "symbol": stock_info.get("code", ""),
                "name": stock_info.get("name", ""),
                "market": stock_info.get("market", ""),
                "industry": stock_info.get("industry", ""),
                "area": stock_info.get("area", ""),
                "pe": stock_info.get("pe", 0),
                "outstanding": stock_info.get("total_shares", 0),
                "total_shares": stock_info.get("total_shares", 0),
                "float_shares": stock_info.get("float_shares", 0),
                "asset_per_share": stock_info.get("asset_per_share", 0),
                "bv_per_share": stock_info.get("bv_per_share", 0),
                "pb": stock.get("pb", 0),
                "time_to_market": stock_info.get("time_to_market", ""),
                "listing_date": stock_info.get("listing_date", ""),
                "is_st": stock_info.get("is_st", False),
                "timestamp": datetime.now().isoformat(),
                "source": "tdx",
            }

            return result

        except Exception as e:
            logger.error("获取股票基本信息失败: %s", e)
            return {}

    def get_industry_classify(self) -> pd.DataFrame:
        """获取行业分类数据

        Returns:
            pd.DataFrame: 行业分类数据
        """
        try:
            # 获取TDX连接
            tdx_api = self._get_tdx_connection()

            # 获取行业分类 (使用 get_block_info)
            logger.info("获取行业分类数据")
            data = tdx_api.get_block_info("blocknew.dat", 0, 1000)

            if not data:
                return pd.DataFrame()

            # 转换为DataFrame
            df = pd.DataFrame(data)

            logger.info("成功获取行业分类数据: %s 条记录", len(df))
            return df

        except Exception as e:
            logger.error("获取行业分类数据失败: %s", e)
            return pd.DataFrame()

    def get_concept_classify(self) -> pd.DataFrame:
        """获取概念分类数据

        Returns:
            pd.DataFrame: 概念分类数据
        """
        try:
            # 获取TDX连接
            tdx_api = self._get_tdx_connection()

            # 获取概念分类 (使用 get_block_info)
            logger.info("获取概念分类数据")
            data = tdx_api.get_block_info("blockgn.dat", 0, 1000)

            if not data:
                return pd.DataFrame()

            # 转换为DataFrame
            df = pd.DataFrame(data)

            logger.info("成功获取概念分类数据: %s 条记录", len(df))
            return df

        except Exception as e:
            logger.error("获取概念分类数据失败: %s", e)
            return pd.DataFrame()

    def get_stock_industry_concept(self, symbol: str) -> Dict:
        """获取股票的行业和概念信息

        Args:
            symbol: 股票代码

        Returns:
            Dict: 股票的行业和概念信息
        """
        try:
            if not symbol:
                raise ValueError("股票代码不能为空")

            result = {
                "symbol": symbol,
                "industry": {},
                "concepts": {},
                "timestamp": datetime.now().isoformat(),
            }

            # 获取股票基本信息，从中提取行业信息
            stock_basic = self.get_stock_basic(symbol)
            if stock_basic and "industry" in stock_basic:
                result["industry"] = {
                    "name": stock_basic["industry"],
                    "code": stock_basic.get("industry_code", ""),
                }

            # 这里可以根据需要进一步扩展

            return result

        except Exception as e:
            logger.error("获取股票行业概念信息失败: %s", e)
            return {
                "symbol": symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_batch_real_time_data(self, symbols: List[str]) -> List[Dict]:
        """批量获取实时行情数据

        Args:
            symbols: 股票代码列表

        Returns:
            List[Dict]: 实时行情数据列表
        """
        try:
            if not symbols:
                return []

            # 限制批量查询数量
            symbols = symbols[:50]  # 最多一次查询50只股票

            # 标准化股票代码
            normalized_symbols = [self._normalize_symbol(sym) for sym in symbols]

            # 获取市场代码
            market_codes = []
            for sym in normalized_symbols:
                market_codes.append(self._get_market_code(sym))

            # 获取TDX连接
            tdx_api = self._get_tdx_connection()

            # 批量获取实时行情
            logger.info("批量获取实时行情数据: %s 只股票", len(symbols))
            data = tdx_api.get_security_quotes(normalized_symbols, market_codes)

            results = []
            if data:
                for i, quote_data in enumerate(data):
                    if i < len(symbols):
                        symbol = symbols[i]
                        market = "上交所" if i < len(market_codes) else "深交所"

                        result = {
                            "symbol": symbol,
                            "name": quote_data.get("name", ""),
                            "price": quote_data.get("price", 0),
                            "open": quote_data.get("open", 0),
                            "high": quote_data.get("high", 0),
                            "low": quote_data.get("low", 0),
                            "pre_close": quote_data.get("pre_close", 0),
                            "change": quote_data.get("change", 0),
                            "change_pct": quote_data.get("change_pct", 0),
                            "volume": quote_data.get("volume", 0),
                            "amount": quote_data.get("amount", 0),
                            "market": market,
                            "timestamp": datetime.now().isoformat(),
                            "source": "tdx",
                        }
                        results.append(result)

            logger.info("成功获取批量实时行情数据: %s 条记录", len(results))
            return results

        except Exception as e:
            logger.error("批量获取实时行情数据失败: %s", e)
            return []

    # ==================== IDataSource接口实现（补全） ====================

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 日线数据

        Note:
            RealtimeService专注于实时数据，不支持历史K线
        """
        logger.warning("RealtimeService不支持获取历史日线数据: %s", symbol)
        return pd.DataFrame()

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指数日线数据

        Args:
            symbol: 指数代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 日线数据

        Note:
            RealtimeService专注于实时数据，不支持历史K线
        """
        logger.warning("RealtimeService不支持获取历史指数数据: %s", symbol)
        return pd.DataFrame()

    def get_index_components(self, symbol: str) -> list:
        """
        获取指数成分股

        Args:
            symbol: 指数代码

        Returns:
            list: 指数成分股代码列表

        Note:
            RealtimeService专注于实时数据，暂不支持指数成分股
        """
        logger.warning("RealtimeService不支持获取指数成分股: %s", symbol)
        return []

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 交易日历数据

        Note:
            RealtimeService专注于实时数据，不支持交易日历
        """
        logger.warning("RealtimeService不支持获取交易日历")
        return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            period: 报告期间

        Returns:
            pd.DataFrame: 财务数据

        Note:
            RealtimeService专注于实时数据，不支持财务数据
        """
        logger.warning("RealtimeService不支持获取财务数据: %s", symbol)
        return pd.DataFrame()

    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> list:
        """
        获取新闻数据

        Args:
            symbol: 股票代码
            limit: 返回数量限制

        Returns:
            list: 新闻数据列表

        Note:
            RealtimeService专注于实时行情，不支持新闻数据
        """
        logger.warning("RealtimeService不支持获取新闻数据")
        return []
