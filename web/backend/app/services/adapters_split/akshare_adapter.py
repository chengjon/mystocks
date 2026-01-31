"""
Akshare数据源适配器

提供Akshare中国市场数据获取功能，支持股票、基金、指数、期货等
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_adapter import BaseAdapter
from app.core.database import db_service
from app.services.data_quality_monitor import get_data_quality_monitor

logger = __import__("logging").getLogger(__name__)


class AkshareAdapter(BaseAdapter):
    """Akshare数据源适配器"""

    def __init__(self):
        super().__init__(name="Akshare", source_type="akshare")
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

            from akshare import stock_info as ak

            df = ak.stock_info_a_share_name_indicator(symbol=stock_code)

            if df.empty:
                self._log_request_error("get_stock_basic", Exception("未返回数据"))
                return None

            stock_info = {
                "symbol": stock_code,
                "name": df.iloc[0]["名称"] if "名称" in df.columns else df.iloc[0]["name"],
                "industry": df.iloc[0]["所属行业"] if "所属行业" in df.columns else "",
                "area": df.iloc[0]["所属地域"] if "所属地域" in df.columns else "",
                "outstanding": df.iloc[0]["总股本(万股)"] if "总股本(万股)" in df.columns else 0,
                "total_assets": df.iloc[0]["总资产(万元)"] if "总资产(万元)" in df.columns else 0,
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

            from akshare import stock_zh_a_hist as ak

            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date)

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

            from akshare import stock_zh_a_spot_em as ak

            quotes = []
            for stock_code in stock_codes[:100]:  # 限制100个股票
                try:
                    df = ak.stock_zh_a_spot_em()

                    if not df.empty and len(df) > 0:
                        latest = df.iloc[0]
                        quotes.append(
                            {
                                "symbol": stock_code,
                                "name": latest["名称"] if "名称" in df.columns else stock_code,
                                "price": latest["最新价"] if "最新价" in df.columns else 0,
                                "change": latest["涨跌幅"] if "涨跌幅" in df.columns else 0,
                                "change_percent": latest["涨跌幅%"] if "涨跌幅%" in df.columns else 0,
                                "volume": latest["成交量(手)"] if "成交量(手)" in df.columns else 0,
                                "turnover": latest["换手率"] if "换手率" in df.columns else 0,
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

    async def get_fund_flow(self, stock_code: str, days: int = 5) -> Optional[Dict]:
        """
        获取资金流向

        Args:
            stock_code: 股票代码
            days: 天数（默认5天）

        Returns:
            Dict: 资金流向数据，失败返回None
        """
        try:
            self._log_request_start("get_fund_flow", {"stock_code": stock_code, "days": days})

            from akshare import stock_individual_fund_flow as ak

            df = ak.stock_individual_fund_flow(stock_code, days)

            if df.empty:
                self._log_request_error("get_fund_flow", Exception("未返回数据"))
                return None

            latest = df.iloc[0]
            fund_flow = {
                "symbol": stock_code,
                "main_force_in": latest["主力净流入(万)"] if "主力净流入(万)" in df.columns else 0,
                "main_force_out": latest["主力净流出(万)"] if "主力净流出(万)" in df.columns else 0,
                "main_force_net": latest["主力净流入(万)"] if "主力净流入(万)" in df.columns else 0,
                "retail_force_in": latest["散户净流入(万)"] if "散户净流入(万)" in df.columns else 0,
                "retail_force_out": latest["散户净流出(万)"] if "散户净流出(万)" in df.columns else 0,
            }

            self._log_request_success("get_fund_flow", fund_flow)
            self._log_data_quality(fund_flow, "get_fund_flow")

            return fund_flow

        except Exception as e:
            self._log_request_error("get_fund_flow", e)
            return None

    async def get_board_data(self, stock_code: str) -> Optional[Dict]:
        """
        获取龙虎榜数据

        Args:
            stock_code: 股票代码

        Returns:
            Dict: 龙虎榜数据，失败返回None
        """
        try:
            self._log_request_start("get_board_data", {"stock_code": stock_code})

            from akshare import stock_lhb_detail_em as ak

            df = ak.stock_lhb_detail_em(stock_code)

            if df.empty:
                self._log_request_error("get_board_data", Exception("未返回数据"))
                return None

            if len(df) > 0:
                latest = df.iloc[0]
                board_data = {
                    "symbol": stock_code,
                    "board_date": latest["龙虎榜日期"] if "龙虎榜日期" in latest else "",
                    "board_type": latest["龙虎榜"] if "龙虎榜" in latest else "",
                    "rank": latest["排名"] if "排名" in latest else 0,
                    "reason": latest["上榜理由"] if "上榜理由" in latest else "",
                }
                self._log_request_success("get_board_data", board_data)
                return board_data
            else:
                self._log_request_error("get_board_data", Exception("未上榜"))
                return None

        except Exception as e:
            self._log_request_error("get_board_data", e)
            return None
