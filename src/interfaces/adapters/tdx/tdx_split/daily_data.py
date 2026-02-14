"""TDX 数据源适配器子模块"""

import logging
import os
import struct
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TdxDailyDataMixin:
    """TDX 日线数据：股票日线、指数日线"""

def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取股票日线数据

    Args:
        symbol: 6位数字股票代码 (如'600519')
        start_date: 开始日期 (格式: 'YYYY-MM-DD')
        end_date: 结束日期 (格式: 'YYYY-MM-DD')

    Returns:
        pd.DataFrame: 日线数据,包含以下列:
            - date: 日期
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            - amount: 成交额

    Note:
        - pytdx单次最多返回800条数据,需要分页获取
        - 数据从最新日期开始向前获取
        - 返回的数据按日期升序排列

    Example:
        >>> tdx = TdxDataSource()
        >>> df = tdx.get_stock_daily('600519', '2024-01-01', '2024-12-31')
        >>> print(df.head())
    """
    # T019: 输入验证
    if not symbol or len(symbol) != 6 or not symbol.isdigit():
        error_msg = f"无效的股票代码格式: {symbol} (需要6位数字)"
        self.logger.warning(error_msg)
        return pd.DataFrame()

    try:
        # 日期标准化
        start_date = normalize_date(start_date)
        end_date = normalize_date(end_date)

        # 识别市场代码
        market = self._get_market_code(symbol)

        # T020: 分页获取K线数据
        # pytdx的get_security_bars参数: (category, market, code, start, count)
        # category: 9=日K线
        # start: 起始位置(0=最新)
        # count: 数量(最多800)

        all_data = []
        start_pos = 0
        batch_size = 800
        max_batches = 20  # 最多获取20批(16000条,约40年)

        self.logger.info("开始获取股票日线: %s, 日期范围: %s ~ %s", symbol, start_date, end_date)

        @self._retry_api_call
        def fetch_kline_batch(start_position):
            """获取单批K线数据"""
            with self._get_tdx_connection() as api:
                if not api.connect(self.tdx_host, self.tdx_port):
                    raise ConnectionError(
                        f"无法连接到TDX服务器: {
                            self.tdx_host}:{
                            self.tdx_port}"
                    )

                # category=9表示日K线
                result = api.get_security_bars(9, market, symbol, start_position, batch_size)
                return result

        # 分批获取数据
        for batch_num in range(max_batches):
            try:
                result_batch = fetch_kline_batch(start_pos)

                # pytdx返回list of OrderedDict,需要转换为DataFrame
                if result_batch is None or not isinstance(result_batch, list) or len(result_batch) == 0:
                    self.logger.info("第%s批数据为空,已获取所有数据", batch_num + 1)
                    break

                # 转换为DataFrame
                df_batch = pd.DataFrame(result_batch)

                # 列名映射
                df_batch = ColumnMapper.to_english(df_batch)

                # 日期格式化(pytdx返回的datetime格式)
                if "datetime" in df_batch.columns:
                    df_batch["date"] = pd.to_datetime(df_batch["datetime"]).dt.strftime("%Y-%m-%d")
                    df_batch = df_batch.drop(columns=["datetime"])

                all_data.append(df_batch)
                self.logger.debug("获取第%s批数据: %s条", batch_num + 1, len(df_batch))

                # 检查是否已获取到start_date之前的数据
                if "date" in df_batch.columns and len(df_batch) > 0:
                    earliest_date = df_batch["date"].min()
                    if earliest_date < start_date:
                        self.logger.info("已获取到%s之前的数据,停止分页", start_date)
                        break

                # 如果返回数据少于batch_size,说明已到最早数据
                if len(df_batch) < batch_size:
                    self.logger.info("返回数据量(%s) < batch_size(%s), 已到最早数据", len(df_batch), batch_size)
                    break

                start_pos += batch_size

            except Exception as e:
                self.logger.error("获取第%s批数据失败: %s", batch_num + 1, str(e))
                break

        # T021: 合并和过滤数据
        if not all_data:
            self.logger.warning("未获取到股票%s的日线数据", symbol)
            return pd.DataFrame()

        # 合并所有批次
        df_result = pd.concat(all_data, ignore_index=True)

        # 按日期过滤
        df_result = df_result[(df_result["date"] >= start_date) & (df_result["date"] <= end_date)]

        # 按日期升序排列
        df_result = df_result.sort_values("date").reset_index(drop=True)

        # T022: 数据验证
        df_result = self._validate_kline_data(df_result)

        # T023: 成功日志
        self.logger.info(
            "获取股票日线成功: %s, 共%d条数据 (%s ~ %s)",
            symbol,
            len(df_result),
            df_result["date"].min(),
            df_result["date"].max(),
        )

        return df_result

    except ValueError as e:
        error_msg = f"参数错误: {str(e)}"
        self.logger.error(error_msg)
        return pd.DataFrame()

    except ConnectionError as e:
        error_msg = f"网络连接失败: {str(e)}"
        self.logger.error(error_msg, exc_info=True)
        return pd.DataFrame()

    except Exception as e:
        error_msg = f"获取股票日线失败: {str(e)}"
        self.logger.error(error_msg, exc_info=True)
        return pd.DataFrame()


def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取指数日线数据

    Args:
        symbol: 6位数字指数代码 (如'000001'=上证指数, '399001'=深证成指)
        start_date: 开始日期 (格式: 'YYYY-MM-DD')
        end_date: 结束日期 (格式: 'YYYY-MM-DD')

    Returns:
        pd.DataFrame: 指数日线数据,包含以下列:
            - date: 日期
            - open: 开盘点位
            - high: 最高点位
            - low: 最低点位
            - close: 收盘点位
            - volume: 成交量
            - amount: 成交额

    Note:
        - 指数代码识别: 000xxx/399xxx=深圳, 其他=上海
        - 实现逻辑与get_stock_daily类似,但使用指数API

    Example:
        >>> tdx = TdxDataSource()
        >>> df = tdx.get_index_daily('000001', '2024-01-01', '2024-12-31')
        >>> print(df.head())
    """
    # T024: 输入验证
    if not symbol or len(symbol) != 6 or not symbol.isdigit():
        error_msg = f"无效的指数代码格式: {symbol} (需要6位数字)"
        self.logger.warning(error_msg)
        return pd.DataFrame()

    try:
        # 日期标准化
        start_date = normalize_date(start_date)
        end_date = normalize_date(end_date)

        # 指数市场识别: 399xxx → 深圳(0), 000xxx → 上海(1)
        # 注意: 指数的市场代码与股票不同!
        prefix = symbol[:3]
        if prefix == "399":
            market = 0  # 深圳指数(深证成指等)
        elif prefix == "000":
            market = 1  # 上海指数(上证指数等)
        else:
            # 默认尝试上海
            market = 1

        # T025: 分页获取指数K线数据
        all_data = []
        start_pos = 0
        batch_size = 800
        max_batches = 20

        self.logger.info("开始获取指数日线: %s, 日期范围: %s ~ %s", symbol, start_date, end_date)

        @self._retry_api_call
        def fetch_index_batch(start_position):
            """获取单批指数K线数据"""
            with self._get_tdx_connection() as api:
                if not api.connect(self.tdx_host, self.tdx_port):
                    raise ConnectionError(
                        f"无法连接到TDX服务器: {
                            self.tdx_host}:{
                            self.tdx_port}"
                    )

                # 使用get_index_bars获取指数K线
                # category=9表示日K线
                result = api.get_index_bars(9, market, symbol, start_position, batch_size)
                return result

        # 分批获取数据
        for batch_num in range(max_batches):
            try:
                result_batch = fetch_index_batch(start_pos)

                # pytdx返回list of OrderedDict,需要转换为DataFrame
                if result_batch is None or not isinstance(result_batch, list) or len(result_batch) == 0:
                    self.logger.info("第%s批数据为空,已获取所有数据", batch_num + 1)
                    break

                # 转换为DataFrame
                df_batch = pd.DataFrame(result_batch)

                # 列名映射
                df_batch = ColumnMapper.to_english(df_batch)

                # 日期格式化
                if "datetime" in df_batch.columns:
                    df_batch["date"] = pd.to_datetime(df_batch["datetime"]).dt.strftime("%Y-%m-%d")
                    df_batch = df_batch.drop(columns=["datetime"])

                all_data.append(df_batch)
                self.logger.debug("获取第%s批数据: %s条", batch_num + 1, len(df_batch))

                # 检查是否已获取到start_date之前的数据
                if "date" in df_batch.columns and len(df_batch) > 0:
                    earliest_date = df_batch["date"].min()
                    if earliest_date < start_date:
                        self.logger.info("已获取到%s之前的数据,停止分页", start_date)
                        break

                # 如果返回数据少于batch_size,说明已到最早数据
                if len(df_batch) < batch_size:
                    self.logger.info("返回数据量(%s) < batch_size(%s), 已到最早数据", len(df_batch), batch_size)
                    break

                start_pos += batch_size

            except Exception as e:
                self.logger.error("获取第%s批数据失败: %s", batch_num + 1, str(e))
                break

        # T026: 合并和过滤数据
        if not all_data:
            self.logger.warning("未获取到指数%s的日线数据", symbol)
            return pd.DataFrame()

        # 合并所有批次
        df_result = pd.concat(all_data, ignore_index=True)

        # 按日期过滤
        df_result = df_result[(df_result["date"] >= start_date) & (df_result["date"] <= end_date)]

        # 按日期升序排列
        df_result = df_result.sort_values("date").reset_index(drop=True)

        # T027: 数据验证
        df_result = self._validate_kline_data(df_result)

        # T028: 成功日志
        self.logger.info(
            "获取指数日线成功: %s, 共%d条数据 (%s ~ %s)",
            symbol,
            len(df_result),
            df_result["date"].min(),
            df_result["date"].max(),
        )

        return df_result

    except ValueError as e:
        error_msg = f"参数错误: {str(e)}"
        self.logger.error(error_msg)
        return pd.DataFrame()

    except ConnectionError as e:
        error_msg = f"网络连接失败: {str(e)}"
        self.logger.error(error_msg, exc_info=True)
        return pd.DataFrame()

    except Exception as e:
        error_msg = f"获取指数日线失败: {str(e)}"
        self.logger.error(error_msg, exc_info=True)
        return pd.DataFrame()


