"""
通达信TQLEX数据源适配器
实现竞价抢筹数据获取接口

数据分类: DataClassification.TRADING_ANALYSIS (衍生数据-交易分析)
存储目标: PostgreSQL+TimescaleDB
"""
import os
import requests
import pandas as pd
from typing import Dict, Optional
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)


class TqlexDataSource:
    """通达信TQLEX数据源实现"""

    BASE_URL = "http://excalc.icfqs.com:7616/TQLEX"
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3
    RETRY_DELAY = 1

    def __init__(self, token: Optional[str] = None):
        """
        初始化TQLEX数据源

        Args:
            token: TQLEX接口认证token (如未提供,从环境变量读取)
        """
        if token is None:
            token = os.getenv('TQLEX_TOKEN')

        if not token:
            logger.warning("TQLEX_TOKEN未配置,竞价抢筹功能将不可用")
            self.token = None
            self.session = None
            self.disabled = True
            return

        self.token = token
        self.disabled = False
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'MyStocks/1.0'
        })

    def _retry_api_call(self, func):
        """API调用重试装饰器 (复用akshare_adapter的模式)"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"[TQLEX] 第{attempt}次尝试失败: {str(e)}")
                    if attempt < self.MAX_RETRIES:
                        time.sleep(self.RETRY_DELAY * attempt)
            raise last_exception if last_exception else Exception("未知错误")
        return wrapper

    def get_chip_race_open(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        获取早盘抢筹数据

        Args:
            date: 日期 (格式: YYYY-MM-DD), 默认为最新交易日

        Returns:
            pd.DataFrame: 早盘抢筹数据
                columns: symbol, name, latest_price, change_percent, prev_close,
                        open_price, race_amount, race_amplitude, race_commission,
                        race_transaction, race_ratio
        """
        if self.disabled:
            logger.warning("TQLEX适配器未启用,返回空数据")
            return pd.DataFrame()

        @self._retry_api_call
        def _fetch():
            params = {'type': 'open'}
            if date:
                params['date'] = date

            response = self.session.get(
                f"{self.BASE_URL}/chip_race",
                params=params,
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            if not data or 'data' not in data:
                return pd.DataFrame()

            df = pd.DataFrame(data['data'])

            # 标准化列名(中文 -> 英文)
            column_mapping = {
                '代码': 'symbol',
                '名称': 'name',
                '最新价': 'latest_price',
                '涨跌幅': 'change_percent',
                '昨收价': 'prev_close',
                '今开价': 'open_price',
                '开盘金额': 'race_amount',
                '抢筹幅度': 'race_amplitude',
                '抢筹委托金额': 'race_commission',
                '抢筹成交金额': 'race_transaction',
                '抢筹占比': 'race_ratio'
            }

            df = df.rename(columns=column_mapping)
            df['race_type'] = 'open'  # 标记为早盘抢筹

            return df

        return _fetch()

    def get_chip_race_end(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        获取尾盘抢筹数据

        Args:
            date: 日期 (格式: YYYY-MM-DD), 默认为最新交易日

        Returns:
            pd.DataFrame: 尾盘抢筹数据
        """
        if self.disabled:
            logger.warning("TQLEX适配器未启用,返回空数据")
            return pd.DataFrame()

        @self._retry_api_call
        def _fetch():
            params = {'type': 'end'}
            if date:
                params['date'] = date

            response = self.session.get(
                f"{self.BASE_URL}/chip_race",
                params=params,
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            if not data or 'data' not in data:
                return pd.DataFrame()

            df = pd.DataFrame(data['data'])

            # 标准化列名
            column_mapping = {
                '代码': 'symbol',
                '名称': 'name',
                '最新价': 'latest_price',
                '涨跌幅': 'change_percent',
                '昨收价': 'prev_close',
                '收盘价': 'close_price',
                '收盘金额': 'race_amount',
                '抢筹幅度': 'race_amplitude',
                '抢筹委托金额': 'race_commission',
                '抢筹成交金额': 'race_transaction',
                '抢筹占比': 'race_ratio'
            }

            df = df.rename(columns=column_mapping)
            df['race_type'] = 'end'  # 标记为尾盘抢筹

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

            # 合并数据
            df_combined = pd.concat([df_open, df_end], ignore_index=True)

            return df_combined

        except Exception as e:
            logger.error(f"获取竞价抢筹数据失败: {e}")
            return pd.DataFrame()


# 全局单例
_tqlex_adapter = None


def get_tqlex_adapter() -> TqlexDataSource:
    """获取TQLEX适配器单例"""
    global _tqlex_adapter
    if _tqlex_adapter is None:
        _tqlex_adapter = TqlexDataSource()
    return _tqlex_adapter
