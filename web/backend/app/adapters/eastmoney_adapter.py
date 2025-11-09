"""
东方财富网直接API适配器
直接调用东方财富网API，不经过akshare
提供稳定高效的数据获取服务
"""

import math
import json
import time
import pandas as pd
import requests
from typing import Dict, Optional, List, Any
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class EastMoneyAdapter:
    """东方财富网直接API适配器"""

    def __init__(self):
        """初始化适配器"""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
        )

    # ==================== 资金流向数据 ====================

    def get_stock_fund_flow(
        self, symbol: str = None, timeframe: str = "今日"
    ) -> pd.DataFrame:
        """
        获取个股资金流向数据

        Args:
            symbol: 股票代码(可选，不传则返回全市场)
            timeframe: 时间维度 ("今日", "3日", "5日", "10日")

        Returns:
            pd.DataFrame: 资金流向数据
        """
        try:
            indicator_map = {
                "今日": [
                    "f62",
                    "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124",
                ],
                "3日": [
                    "f267",
                    "f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124",
                ],
                "5日": [
                    "f164",
                    "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124",
                ],
                "10日": [
                    "f174",
                    "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124",
                ],
            }

            url = "http://push2.eastmoney.com/api/qt/clist/get"
            page_size = 100
            page_current = 1

            params = {
                "fid": indicator_map[timeframe][0],
                "po": "1",
                "pz": page_size,
                "pn": page_current,
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "ut": "b2884a393a59ad64002292a3e90d46a5",
                "fs": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
                "fields": indicator_map[timeframe][1],
            }

            r = self.session.get(url, params=params)
            data_json = r.json()

            if not data_json.get("data"):
                return pd.DataFrame()

            data = data_json["data"]["diff"]
            data_count = data_json["data"]["total"]
            page_count = math.ceil(data_count / page_size)

            while page_count > 1:
                page_current += 1
                params["pn"] = page_current
                r = self.session.get(url, params=params)
                data_json = r.json()
                _data = data_json["data"]["diff"]
                data.extend(_data)
                page_count -= 1

            temp_df = pd.DataFrame(data)
            temp_df = temp_df[~temp_df["f2"].isin(["-"])]

            # 重命名列
            if timeframe == "今日":
                temp_df.columns = [
                    "最新价",
                    "今日涨跌幅",
                    "代码",
                    "名称",
                    "今日主力净流入-净额",
                    "今日超大单净流入-净额",
                    "今日超大单净流入-净占比",
                    "今日大单净流入-净额",
                    "今日大单净流入-净占比",
                    "今日中单净流入-净额",
                    "今日中单净流入-净占比",
                    "今日小单净流入-净额",
                    "今日小单净流入-净占比",
                    "_",
                    "今日主力净流入-净占比",
                    "_",
                    "_",
                    "_",
                ]
                temp_df = temp_df[
                    [
                        "代码",
                        "名称",
                        "最新价",
                        "今日涨跌幅",
                        "今日主力净流入-净额",
                        "今日主力净流入-净占比",
                        "今日超大单净流入-净额",
                        "今日超大单净流入-净占比",
                        "今日大单净流入-净额",
                        "今日大单净流入-净占比",
                        "今日中单净流入-净额",
                        "今日中单净流入-净占比",
                        "今日小单净流入-净额",
                        "今日小单净流入-净占比",
                    ]
                ]

            # 数据类型转换
            for col in temp_df.columns:
                if "净流入" in col or "涨跌幅" in col or "最新价" in col:
                    temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")

            # 如果指定了股票代码，则筛选
            if symbol:
                stock_code = symbol.split(".")[0] if "." in symbol else symbol
                temp_df = temp_df[temp_df["代码"] == stock_code]

            return temp_df

        except Exception as e:
            logger.error(f"获取资金流向数据失败: {e}")
            return pd.DataFrame()

    # ==================== ETF数据 ====================

    def get_etf_spot(self) -> pd.DataFrame:
        """
        获取ETF实时行情数据

        Returns:
            pd.DataFrame: ETF实时数据
        """
        try:
            url = "http://88.push2.eastmoney.com/api/qt/clist/get"
            page_size = 100
            page_current = 1

            params = {
                "pn": page_current,
                "pz": page_size,
                "po": "1",
                "np": "1",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2",
                "wbp2u": "|0|0|0|web",
                "fid": "f3",
                "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024",
                "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
                "_": str(int(time.time() * 1000)),
            }

            r = self.session.get(url, params=params)
            data_json = r.json()

            if not data_json.get("data"):
                return pd.DataFrame()

            data = data_json["data"]["diff"]
            if not data:
                return pd.DataFrame()

            data_count = data_json["data"]["total"]
            page_count = math.ceil(data_count / page_size)

            while page_count > 1:
                page_current += 1
                params["pn"] = page_current
                r = self.session.get(url, params=params)
                data_json = r.json()
                _data = data_json["data"]["diff"]
                data.extend(_data)
                page_count -= 1

            temp_df = pd.DataFrame(data)
            temp_df.rename(
                columns={
                    "f12": "代码",
                    "f14": "名称",
                    "f2": "最新价",
                    "f3": "涨跌幅",
                    "f4": "涨跌额",
                    "f5": "成交量",
                    "f6": "成交额",
                    "f17": "开盘价",
                    "f15": "最高价",
                    "f16": "最低价",
                    "f18": "昨收",
                    "f8": "换手率",
                    "f21": "流通市值",
                    "f20": "总市值",
                },
                inplace=True,
            )

            temp_df = temp_df[
                [
                    "代码",
                    "名称",
                    "最新价",
                    "涨跌幅",
                    "涨跌额",
                    "成交量",
                    "成交额",
                    "开盘价",
                    "最高价",
                    "最低价",
                    "昨收",
                    "换手率",
                    "流通市值",
                    "总市值",
                ]
            ]

            # 数据类型转换
            numeric_columns = [
                "最新价",
                "涨跌幅",
                "涨跌额",
                "成交量",
                "成交额",
                "开盘价",
                "最高价",
                "最低价",
                "昨收",
                "换手率",
                "流通市值",
                "总市值",
            ]
            for col in numeric_columns:
                temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")

            return temp_df

        except Exception as e:
            logger.error(f"获取ETF数据失败: {e}")
            return pd.DataFrame()

    # ==================== 龙虎榜数据 ====================

    def get_stock_lhb_detail(self, date_str: str) -> pd.DataFrame:
        """
        获取指定日期龙虎榜详细数据

        Args:
            date_str: 日期 (格式: YYYY-MM-DD)

        Returns:
            pd.DataFrame: 龙虎榜数据
        """
        try:
            # 转换日期格式
            date_formatted = date_str.replace("-", "")

            url = "http://datacenter-web.eastmoney.com/api/data/v1/get"

            params = {
                "sortColumns": "SECURITY_CODE,TRADE_DATE",
                "sortTypes": "1,-1",
                "pageSize": 500,
                "pageNumber": 1,
                "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
                "columns": "SECURITY_CODE,SECUCODE,SECURITY_NAME_ABBR,TRADE_DATE,EXPLAIN,CLOSE_PRICE,CHANGE_RATE,BILLBOARD_NET_AMT,BILLBOARD_BUY_AMT,BILLBOARD_SELL_AMT,BILLBOARD_DEAL_AMT,ACCUM_AMOUNT,DEAL_NET_RATIO,DEAL_AMOUNT_RATIO,TURNOVERRATE,FREE_MARKET_CAP,EXPLANATION,D1_CLOSE_ADJCHRATE,D2_CLOSE_ADJCHRATE,D5_CLOSE_ADJCHRATE,D10_CLOSE_ADJCHRATE",
                "source": "WEB",
                "client": "WEB",
                "filter": f"(TRADE_DATE='{date_str}')",
            }

            r = self.session.get(url, params=params)
            data_json = r.json()

            if not data_json.get("result") or not data_json["result"].get("data"):
                return pd.DataFrame()

            temp_df = pd.DataFrame(data_json["result"]["data"])

            # 重命名列
            temp_df.rename(
                columns={
                    "SECURITY_CODE": "代码",
                    "SECURITY_NAME_ABBR": "名称",
                    "TRADE_DATE": "日期",
                    "EXPLAIN": "解读",
                    "CLOSE_PRICE": "收盘价",
                    "CHANGE_RATE": "涨跌幅",
                    "BILLBOARD_NET_AMT": "龙虎榜净买额",
                    "BILLBOARD_BUY_AMT": "龙虎榜买入额",
                    "BILLBOARD_SELL_AMT": "龙虎榜卖出额",
                    "BILLBOARD_DEAL_AMT": "龙虎榜成交额",
                    "ACCUM_AMOUNT": "市场总成交额",
                    "DEAL_NET_RATIO": "净买额占总成交比",
                    "DEAL_AMOUNT_RATIO": "成交额占总成交比",
                    "TURNOVERRATE": "换手率",
                    "FREE_MARKET_CAP": "流通市值",
                },
                inplace=True,
            )

            # 数据类型转换
            numeric_columns = [
                "收盘价",
                "涨跌幅",
                "龙虎榜净买额",
                "龙虎榜买入额",
                "龙虎榜卖出额",
                "龙虎榜成交额",
                "市场总成交额",
                "净买额占总成交比",
                "成交额占总成交比",
                "换手率",
                "流通市值",
            ]
            for col in numeric_columns:
                if col in temp_df.columns:
                    temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")

            return temp_df

        except Exception as e:
            logger.error(f"获取龙虎榜数据失败: {e}")
            return pd.DataFrame()

    # ==================== 竞价抢筹数据 ====================

    def get_chip_race(
        self, race_type: str = "open", date_str: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取竞价抢筹数据（早盘/尾盘）
        注意：此功能需要通达信或其他数据源支持，东方财富网暂不提供

        Args:
            race_type: 类型 ("open"=早盘, "end"=尾盘)
            date_str: 日期

        Returns:
            pd.DataFrame: 竞价抢筹数据
        """
        # 东方财富网暂不提供竞价抢筹数据，需要其他数据源
        logger.warning("东方财富网暂不提供竞价抢筹数据，请使用TQLEX或其他数据源")
        return pd.DataFrame()

    # ==================== 行业/概念资金流向 ====================

    def get_sector_fund_flow(
        self, sector_type: str = "行业", timeframe: str = "今日"
    ) -> pd.DataFrame:
        """
        获取行业/概念板块资金流向

        Args:
            sector_type: 板块类型 ("行业", "概念", "地域")
            timeframe: 时间维度 ("今日", "3日", "5日", "10日")

        Returns:
            pd.DataFrame: 板块资金流向数据
        """
        try:
            # 板块类型映射
            sector_map = {"行业": "m:90+t:2", "概念": "m:90+t:3", "地域": "m:90+t:1"}

            # 时间字段映射
            timeframe_fields = {
                "今日": "f62,f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
                "3日": "f62,f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124,f1,f13",
                "5日": "f62,f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124,f1,f13",
                "10日": "f62,f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124,f1,f13",
            }

            url = "http://push2.eastmoney.com/api/qt/clist/get"

            params = {
                "pn": 1,
                "pz": 500,
                "po": "1",
                "np": "1",
                "ut": "b2884a393a59ad64002292a3e90d46a5",
                "fltt": "2",
                "invt": "2",
                "fid": "f62",
                "fs": sector_map.get(sector_type, "m:90+t:2"),
                "fields": timeframe_fields.get(timeframe, timeframe_fields["今日"]),
            }

            r = self.session.get(url, params=params)
            data_json = r.json()

            if not data_json.get("data") or not data_json["data"].get("diff"):
                return pd.DataFrame()

            temp_df = pd.DataFrame(data_json["data"]["diff"])

            # 重命名列（根据时间维度）
            if timeframe == "今日":
                temp_df = temp_df.rename(
                    columns={
                        "f12": "代码",
                        "f14": "名称",
                        "f2": "最新价",
                        "f3": "涨跌幅",
                        "f62": "主力净流入",
                        "f184": "主力净流入占比",
                        "f66": "超大单净流入",
                        "f69": "超大单净流入占比",
                        "f72": "大单净流入",
                        "f75": "大单净流入占比",
                        "f78": "中单净流入",
                        "f81": "中单净流入占比",
                        "f84": "小单净流入",
                        "f87": "小单净流入占比",
                    }
                )

            # 数据类型转换
            for col in temp_df.columns:
                if any(
                    keyword in col for keyword in ["净流入", "占比", "涨跌幅", "最新价"]
                ):
                    temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")

            return temp_df

        except Exception as e:
            logger.error(f"获取板块资金流向失败: {e}")
            return pd.DataFrame()

    # ==================== 股票分红配送 ====================

    def get_stock_dividend(self, symbol: str) -> pd.DataFrame:
        """
        获取股票分红配送数据

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 分红配送数据
        """
        try:
            stock_code = symbol.split(".")[0] if "." in symbol else symbol

            url = "http://datacenter-web.eastmoney.com/api/data/v1/get"

            params = {
                "sortColumns": "REPORT_DATE",
                "sortTypes": "-1",
                "pageSize": 50,
                "pageNumber": 1,
                "reportName": "RPT_SHAREBONUS_DET",
                "columns": "ALL",
                "filter": f'(SECURITY_CODE="{stock_code}")',
            }

            r = self.session.get(url, params=params)
            data_json = r.json()

            if not data_json.get("result") or not data_json["result"].get("data"):
                return pd.DataFrame()

            temp_df = pd.DataFrame(data_json["result"]["data"])

            # 重命名列
            temp_df = temp_df.rename(
                columns={
                    "SECURITY_CODE": "股票代码",
                    "SECURITY_NAME_ABBR": "股票名称",
                    "REPORT_DATE": "公告日期",
                    "IMPL_PLAN_PROFILE": "分红方案",
                    "DIVIDEND_RATIO": "每股派息",
                    "BONUS_RATIO": "每股送股",
                    "TRANSFER_RATIO": "每股转增",
                    "EX_DIVIDEND_DATE": "除权除息日",
                    "RECORD_DATE": "股权登记日",
                    "PAYMENT_DATE": "派息日",
                }
            )

            return temp_df

        except Exception as e:
            logger.error(f"获取分红配送数据失败: {e}")
            return pd.DataFrame()

    # ==================== 股票大宗交易 ====================

    def get_stock_blocktrade(self, date_str: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票大宗交易数据

        Args:
            date_str: 日期 (格式: YYYY-MM-DD)，不传则获取最新

        Returns:
            pd.DataFrame: 大宗交易数据
        """
        try:
            url = "http://datacenter-web.eastmoney.com/api/data/v1/get"

            filter_str = f"(TRADE_DATE='{date_str}')" if date_str else ""

            params = {
                "sortColumns": "TRADE_DATE,SECURITY_CODE",
                "sortTypes": "-1,1",
                "pageSize": 500,
                "pageNumber": 1,
                "reportName": "RPT_DATA_BLOCKTRADE",
                "columns": "ALL",
                "source": "WEB",
                "client": "WEB",
                "filter": filter_str,
            }

            r = self.session.get(url, params=params)
            data_json = r.json()

            if not data_json.get("result") or not data_json["result"].get("data"):
                return pd.DataFrame()

            temp_df = pd.DataFrame(data_json["result"]["data"])

            # 重命名列
            temp_df = temp_df.rename(
                columns={
                    "TRADE_DATE": "交易日期",
                    "SECURITY_CODE": "股票代码",
                    "SECURITY_NAME_ABBR": "股票名称",
                    "DEAL_PRICE": "成交价",
                    "CLOSE_PRICE": "收盘价",
                    "PREMIUM_RATIO": "溢价率",
                    "DEAL_AMT": "成交金额",
                    "DEAL_VOL": "成交量",
                    "TURNOVER_RATE": "成交占比",
                    "BUYER_NAME": "买方营业部",
                    "SELLER_NAME": "卖方营业部",
                }
            )

            # 数据类型转换
            numeric_columns = [
                "成交价",
                "收盘价",
                "溢价率",
                "成交金额",
                "成交量",
                "成交占比",
            ]
            for col in numeric_columns:
                if col in temp_df.columns:
                    temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")

            return temp_df

        except Exception as e:
            logger.error(f"获取大宗交易数据失败: {e}")
            return pd.DataFrame()


# 全局单例
_eastmoney_adapter = None


def get_eastmoney_adapter() -> EastMoneyAdapter:
    """获取东方财富适配器单例"""
    global _eastmoney_adapter
    if _eastmoney_adapter is None:
        _eastmoney_adapter = EastMoneyAdapter()
    return _eastmoney_adapter
