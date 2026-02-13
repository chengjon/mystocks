"""
Efinance数据源适配器

提供Efinance中国金融数据获取功能，支持基础数据、日线数据、分红数据、实时行情等
"""

from typing import Dict, List, Optional

from .base_adapter import BaseAdapter
from app.core.database import db_service
from app.services.data_quality_monitor import get_data_quality_monitor

logger = __import__("logging").getLogger(__name__)


class EfinanceAdapter(BaseAdapter):
    """Efinance数据源适配器"""

    def __init__(self):
        super().__init__(name="Efinance", source_type="efinance")
        self.db_service = db_service
        self.quality_monitor = get_data_quality_monitor()

        logger.info(f"初始化{self.name}适配器")

    async def get_stock_basic(self, stock_code: str) -> Optional[Dict]:
        """
        获取股票基本信息

        Args:
            stock_code: 股票代码

        Returns:
            Dict: 股票基本信息，失败返回None
        """
        try:
            self._log_request_start("get_stock_basic", {"stock_code": stock_code})

            from efinance import stock_info as ef

            df = ef.stock_info(stock_code)

            if df.empty:
                self._log_request_error("get_stock_basic", Exception("未返回数据"))
                return None

            stock_info = {
                "symbol": stock_code,
                "name": df.iloc[0]["证券名称"] if "证券名称" in df.columns else df.iloc[0]["名称"],
                "code": df.iloc[0]["证券代码"] if "证券代码" in df.columns else stock_code,
                "industry": df.iloc[0]["行业"] if "行业" in df.columns else "",
                "listing_date": df.iloc[0]["上市日期"] if "上市日期" in df.columns else "",
                "total_share": df.iloc[0]["总股本"] if "总股本" in df.columns else 0,
                "market_cap": df.iloc[0]["总市值"] if "总市值" in df.columns else 0,
            }

            self._log_request_success("get_stock_basic", stock_info)
            self._log_data_quality(stock_info, "get_stock_basic")

            return stock_info

        except Exception as e:
            self._log_request_error("get_stock_basic", e)
            return None

    async def get_stock_daily(self, stock_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """
        获取股票日线数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            List[Dict]: 日线数据列表，失败返回空列表
        """
        try:
            self._log_request_start(
                "get_stock_daily", {"stock_code": stock_code, "start_date": start_date, "end_date": end_date}
            )

            from efinance import stock_zh_a_hist as ef

            df = ef.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date)

            if df.empty:
                self._log_request_error("get_stock_daily", Exception("未返回数据"))
                return []

            daily_data = []
            for _, row in df.iterrows():
                daily_data.append(
                    {
                        "symbol": stock_code,
                        "trade_date": row["日期"] if "日期" in row.index else "",
                        "open": row["开盘"] if "开盘" in row else 0,
                        "high": row["最高"] if "最高" in row else 0,
                        "low": row["最低"] if "最低" in row else 0,
                        "close": row["收盘"] if "收盘" in row else 0,
                        "volume": row["成交量"] if "成交量" in row else 0,
                        "amount": row["成交额"] if "成交额" in row else 0,
                    }
                )

            self._log_request_success("get_stock_daily", f"返回{len(daily_data)}条日线数据")
            self._log_data_quality(daily_data, "get_stock_daily")

            return daily_data

        except Exception as e:
            self._log_request_error("get_stock_daily", e)
            return []

    async def get_fund_data(self, stock_code: str, year: str = "2024") -> Optional[Dict]:
        """
        获取基金数据

        Args:
            stock_code: 股票代码
            year: 年份（默认2024）

        Returns:
            Dict: 基金数据，失败返回None
        """
        try:
            self._log_request_start("get_fund_data", {"stock_code": stock_code, "year": year})

            from efinance import fund_em_stock_pool as ef

            df = ef.fund_em_stock_pool(stock_code, year)

            if df.empty:
                self._log_request_error("get_fund_data", Exception("未返回数据"))
                return None

            if len(df) > 0:
                latest = df.iloc[0]
                fund_data = {
                    "symbol": stock_code,
                    "fund_name": latest["基金名称"] if "基金名称" in latest else "",
                    "fund_code": latest["基金代码"] if "基金代码" in latest else "",
                    "fund_manager": latest["基金经理"] if "基金经理" in latest else "",
                    "fund_size": latest["基金规模"] if "基金规模" in latest else 0,
                    "fund_nav": latest["净值"] if "净值" in latest else 0,
                }

                self._log_request_success("get_fund_data", fund_data)
                self._log_data_quality(fund_data, "get_fund_data")
                return fund_data

            self._log_request_error("get_fund_data", Exception("未返回数据"))
            return None

        except Exception as e:
            self._log_request_error("get_fund_data", e)
            return None

    async def get_dividend_data(self, stock_code: str, year: str = "2024") -> Optional[List[Dict]]:
        """
        获取分红数据

        Args:
            stock_code: 股票代码
            year: 年份（默认2024）

        Returns:
            List[Dict]: 分红数据列表，失败返回空列表
        """
        try:
            self._log_request_start("get_dividend_data", {"stock_code": stock_code, "year": year})

            from efinance import dividend_info as ef

            df = ef.dividend_info(stock_code, year)

            if df.empty:
                self._log_request_error("get_dividend_data", Exception("未返回数据"))
                return []

            dividend_data = []
            for _, row in df.iterrows():
                dividend_data.append(
                    {
                        "symbol": stock_code,
                        "dividend_date": row["分红除权日"] if "分红除权日" in row else "",
                        "dividend_per_share": row["每10股分红"] if "每10股分红" in row else 0,
                        "dividend_yield": row["股息率%"] if "股息率%" in row else 0,
                        "ex_dividend_date": row["除权日期"] if "除权日期" in row else "",
                    }
                )

            self._log_request_success("get_dividend_data", f"返回{len(dividend_data)}条分红数据")
            self._log_data_quality(dividend_data, "get_dividend_data")

            return dividend_data

        except Exception as e:
            self._log_request_error("get_dividend_data", e)
            return []

    async def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[List[Dict]]:
        """
        获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            List[Dict]: 实时行情数据列表，失败返回空列表
        """
        try:
            self._log_request_start("get_realtime_quotes", {"stock_codes": stock_codes})

            from efinance import stock_realtime as ef

            quotes = []

            for stock_code in stock_codes[:50]:  # 限制50个股票
                try:
                    df = ef.stock_realtime(stock_code)

                    if not df.empty and len(df) > 0:
                        latest = df.iloc[0]
                        quotes.append(
                            {
                                "symbol": stock_code,
                                "name": latest["证券名称"] if "证券名称" in latest else stock_code,
                                "price": latest["最新价"] if "最新价" in latest else 0,
                                "change": latest["涨跌幅"] if "涨跌幅" in latest else 0,
                                "change_percent": latest["涨跌幅%"] if "涨跌幅%" in latest else 0,
                                "volume": latest["成交量(手)"] if "成交量(手)" in latest else 0,
                                "turnover": latest["换手率"] if "换手率" in latest else 0,
                            }
                        )
                except Exception as stock_error:
                    logger.warning(f"获取{stock_code}实时行情失败: {stock_error}")

            self._log_request_success("get_realtime_quotes", f"返回{len(quotes)}条实时行情")
            self._log_data_quality(quotes, "get_realtime_quotes")

            return quotes

        except Exception as e:
            self._log_request_error("get_realtime_quotes", e)
            return []

    async def check_health(self) -> Optional[str]:
        """
        检查数据源健康状态

        Returns:
            str: 健康状态（healthy/unhealthy/error），失败返回None
        """
        try:
            self._log_request_start("check_health", {})

            from efinance import stock_info as ef

            test_code = "600000"  # 测试股票代码
            df = ef.stock_info(test_code)

            if not df.empty and len(df) > 0:
                return "healthy"

            self._log_request_success("check_health", "Efinance数据源健康")
            return "healthy"

        except Exception as e:
            self._log_request_error("check_health", e)
            return f"error: {e}"
