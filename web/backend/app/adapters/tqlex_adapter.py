"""
通达信TQLEX数据源适配器
实现竞价抢筹数据获取接口

参考instock实现:
- /opt/iflow/instock/instock/core/crawling/stock_chip_race.py
- /opt/iflow/instock/instock/core/tablestructure.py

字段说明:
- sort:1=抢筹委托金额, 2=抢筹成交金额, 3=开盘金额, 4=抢筹幅度, 5=抢筹占比
- period: 0=早盘(集合竞价), 1=尾盘(收盘竞价)
"""

import logging
import os
import time
from functools import wraps
from typing import Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class TqlexDataSource:
    """通达信TQLEX数据源实现"""

    BASE_URL = "http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    REQUEST_INTERVAL = 3

    HEADERS = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 TdxW",
    }

    def __init__(self, token: Optional[str] = None):
        """初始化TQLEX数据源"""
        if token is None:
            token = os.getenv("TQLEX_TOKEN")

        if not token:
            logger.warning("TQLEX_TOKEN未配置,竞价抢筹功能将不可用")
            self.token = None
            self.session = None
            self.disabled = True
            return

        self.token = token
        self.disabled = False
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _retry_api_call(self, func):
        """API调用重试装饰器"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning("[TQLEX] 第%(attempt)s次尝试失败: {str(e)}")
                    if attempt < self.MAX_RETRIES:
                        time.sleep(self.RETRY_DELAY * attempt)
            raise last_exception if last_exception else Exception("未知错误")

        return wrapper

    def _build_request_params(self, period: int, date: Optional[str] = None, count: int = 100) -> list:
        """构建请求参数"""
        params = {
            "funcId": 20,
            "offset": 0,
            "count": count,
            "sort": 1,
            "period": period,
            "Token": self.token,
            "modname": "JJQC",
        }
        if date:
            params["date"] = date
        return [params]

    def _process_open_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理早盘抢筹数据"""
        if df.empty:
            return df

        df.columns = [
            "code",
            "name",
            "pre_close",
            "open_price",
            "deal_amount",
            "bid_rate",
            "bid_trust_amount",
            "bid_deal_amount",
            "new_price",
            "_",
            "limitup_days",
            "continuation_days",
        ]

        df["pre_close"] = df["pre_close"] / 10000
        df["open_price"] = df["open_price"] / 10000
        df["bid_rate"] = round(df["bid_rate"] * 100, 2)
        df["new_price"] = round(df["new_price"], 2)
        df["change_rate"] = round((df["new_price"] / df["pre_close"] - 1) * 100, 2)
        df["bid_ratio"] = round((df["bid_deal_amount"] / df["deal_amount"]) * 100, 2)

        df = df[
            [
                "code",
                "name",
                "new_price",
                "change_rate",
                "pre_close",
                "open_price",
                "deal_amount",
                "bid_rate",
                "bid_trust_amount",
                "bid_deal_amount",
                "bid_ratio",
            ]
        ]

        return df

    def _process_end_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理尾盘抢筹数据"""
        if df.empty:
            return df

        df.columns = [
            "code",
            "name",
            "pre_close",
            "open_price",
            "deal_amount",
            "bid_rate",
            "bid_trust_amount",
            "bid_deal_amount",
            "new_price",
            "_",
            "limitup_days",
            "continuation_days",
        ]

        df["pre_close"] = df["pre_close"] / 10000
        df["open_price"] = df["open_price"] / 10000
        df["bid_rate"] = round(df["bid_rate"] * 100, 2)
        df["new_price"] = round(df["new_price"], 2)
        df["change_rate"] = round((df["new_price"] / df["pre_close"] - 1) * 100, 2)
        df["bid_ratio"] = round((df["bid_deal_amount"] / df["deal_amount"]) * 100, 2)

        df = df[
            [
                "code",
                "name",
                "new_price",
                "change_rate",
                "pre_close",
                "open_price",
                "deal_amount",
                "bid_rate",
                "bid_trust_amount",
                "bid_deal_amount",
                "bid_ratio",
            ]
        ]

        return df

    def get_chip_race_open(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        获取早盘抢筹数据 (集合竞价)

        Args:
            date: 日期 (格式: YYYY-MM-DD 或 YYYYMMDD), 默认为最新交易日

        Returns:
            pd.DataFrame: 早盘抢筹数据
        """
        if self.disabled:
            logger.warning("TQLEX适配器未启用,返回空数据")
            return pd.DataFrame()

        @self._retry_api_call
        def _fetch():
            if not self.session:
                return pd.DataFrame()

            date_str = ""
            if date:
                date_str = date.replace("-", "")

            params = self._build_request_params(period=0, date=date_str)

            response = self.session.post(
                self.BASE_URL,
                json=params,
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            data_json = response.json()
            if not data_json or "datas" not in data_json:
                return pd.DataFrame()

            datas = data_json["datas"]
            if not datas:
                return pd.DataFrame()

            df = pd.DataFrame(datas)
            df = self._process_open_data(df)

            return df

        return _fetch()

    def get_chip_race_end(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        获取尾盘抢筹数据 (收盘竞价)

        Args:
            date: 日期 (格式: YYYY-MM-DD 或 YYYYMMDD), 默认为最新交易日

        Returns:
            pd.DataFrame: 尾盘抢筹数据
        """
        if self.disabled:
            logger.warning("TQLEX适配器未启用,返回空数据")
            return pd.DataFrame()

        @self._retry_api_call
        def _fetch():
            if not self.session:
                return pd.DataFrame()

            date_str = ""
            if date:
                date_str = date.replace("-", "")

            params = self._build_request_params(period=1, date=date_str)

            response = self.session.post(
                self.BASE_URL,
                json=params,
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            data_json = response.json()
            if not data_json or "datas" not in data_json:
                return pd.DataFrame()

            datas = data_json["datas"]
            if not datas:
                return pd.DataFrame()

            df = pd.DataFrame(datas)
            df = self._process_end_data(df)

            return df

        return _fetch()

    def get_chip_race_combined(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        获取完整的竞价抢筹数据(早盘+尾盘)

        Args:
            date: 日期 (格式: YYYY-MM-DD), 默认为最新交易日

        Returns:
            pd.DataFrame: 合并的抢筹数据
        """
        try:
            df_open = self.get_chip_race_open(date)
            df_end = self.get_chip_race_end(date)

            if df_open.empty and df_end.empty:
                return pd.DataFrame()

            df_open["race_type"] = "open"
            df_end["race_type"] = "end"

            df_combined = pd.concat([df_open, df_end], ignore_index=True)

            return df_combined

        except Exception as e:
            logger.error("获取竞价抢筹数据失败: %(e)s")
            return pd.DataFrame()


_tqlex_adapter = None


def get_tqlex_adapter() -> TqlexDataSource:
    """获取TQLEX适配器单例"""
    global _tqlex_adapter
    if _tqlex_adapter is None:
        _tqlex_adapter = TqlexDataSource()
    return _tqlex_adapter
