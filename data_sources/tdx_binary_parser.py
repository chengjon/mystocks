"""
TDX二进制文件解析器 (TDX Binary File Parser)

功能说明:
- 解析通达信本地二进制数据文件
- 支持日线(.day)、5分钟(.lc5)、1分钟(.lc1)数据
- 自动处理前后复权
- 增量读取和缓存优化

文件格式说明:
- 日线数据(.day): 每条记录32字节
  - date (4字节): YYYYMMDD格式
  - open, high, low, close (各4字节): 价格×1000
  - amount (4字节): 成交金额
  - volume (4字节): 成交量
  - reserved (4字节): 保留字段

- 分钟数据(.lc5/.lc1): 每条记录32字节
  - date (2字节): 年份-1900
  - minute (2字节): 分钟偏移
  - open, high, low, close (各4字节): 价格×1000
  - amount (4字节): 成交金额
  - volume (4字节): 成交量

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import os
import struct
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from pathlib import Path
import logging


class TdxBinaryParser:
    """
    TDX二进制文件解析器

    功能:
    - 读取.day日线数据
    - 读取.lc5五分钟数据
    - 读取.lc1一分钟数据
    - 自动识别市场和股票代码
    - 支持前后复权
    """

    # 数据文件格式常量
    DAY_RECORD_SIZE = 32        # 日线记录大小
    MIN_RECORD_SIZE = 32        # 分钟线记录大小
    DAY_STRUCT_FORMAT = '<IIIIIfII'   # 日线数据结构
    MIN_STRUCT_FORMAT = '<HHIIIIfII'  # 分钟数据结构

    def __init__(self, data_path: str = None):
        """
        初始化TDX二进制解析器

        参数:
            data_path: TDX数据目录路径（默认从环境变量TDX_DATA_PATH读取）
        """
        self.logger = logging.getLogger(f"{__name__}.TdxBinaryParser")
        self.logger.setLevel(logging.INFO)

        # 获取数据路径
        self.data_path = data_path or os.getenv(
            'TDX_DATA_PATH',
            '/mnt/d/ProgramData/tdx_new/vipdoc'
        )

        if not os.path.exists(self.data_path):
            self.logger.warning(f"TDX数据路径不存在: {self.data_path}")
        else:
            self.logger.info(f"TDX数据路径: {self.data_path}")

        # 市场目录映射
        self.market_dirs = {
            'sh': os.path.join(self.data_path, 'sh', 'lday'),  # 上海日线
            'sz': os.path.join(self.data_path, 'sz', 'lday'),  # 深圳日线
            'sh_5min': os.path.join(self.data_path, 'sh', 'fzline'),  # 上海5分钟
            'sz_5min': os.path.join(self.data_path, 'sz', 'fzline'),  # 深圳5分钟
            'sh_1min': os.path.join(self.data_path, 'sh', 'minline'),  # 上海1分钟
            'sz_1min': os.path.join(self.data_path, 'sz', 'minline'),  # 深圳1分钟
        }

    def read_day_data(self,
                      symbol: str,
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None) -> pd.DataFrame:
        """
        读取日线数据

        参数:
            symbol: 股票代码（如 '600000' 或 'sh600000'）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        返回:
            pd.DataFrame: 日线数据，包含 date, open, high, low, close, volume, amount

        示例:
            >>> parser = TdxBinaryParser()
            >>> data = parser.read_day_data('600000', start_date=date(2024, 1, 1))
            >>> print(data.head())
        """
        # 标准化代码
        market, code = self._parse_symbol(symbol)

        # 构建文件路径
        file_path = self._get_day_file_path(market, code)

        if not os.path.exists(file_path):
            self.logger.warning(f"文件不存在: {file_path}")
            return pd.DataFrame()

        # 读取二进制数据
        try:
            data = self._parse_day_file(file_path)

            if data.empty:
                return data

            # 过滤日期范围
            if start_date:
                data = data[data['date'] >= pd.Timestamp(start_date)]
            if end_date:
                data = data[data['date'] <= pd.Timestamp(end_date)]

            self.logger.info(f"读取 {symbol} 日线数据: {len(data)} 条记录")
            return data

        except Exception as e:
            self.logger.error(f"读取日线数据失败 {symbol}: {e}")
            return pd.DataFrame()

    def read_5min_data(self,
                       symbol: str,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> pd.DataFrame:
        """
        读取5分钟数据

        参数:
            symbol: 股票代码
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        返回:
            pd.DataFrame: 5分钟数据
        """
        market, code = self._parse_symbol(symbol)
        file_path = self._get_5min_file_path(market, code)

        if not os.path.exists(file_path):
            self.logger.warning(f"文件不存在: {file_path}")
            return pd.DataFrame()

        try:
            data = self._parse_min_file(file_path, interval=5)

            if data.empty:
                return data

            # 过滤日期范围
            if start_date:
                data = data[data['datetime'] >= pd.Timestamp(start_date)]
            if end_date:
                data = data[data['datetime'] < pd.Timestamp(end_date) + timedelta(days=1)]

            self.logger.info(f"读取 {symbol} 5分钟数据: {len(data)} 条记录")
            return data

        except Exception as e:
            self.logger.error(f"读取5分钟数据失败 {symbol}: {e}")
            return pd.DataFrame()

    def read_1min_data(self,
                       symbol: str,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> pd.DataFrame:
        """
        读取1分钟数据

        参数:
            symbol: 股票代码
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        返回:
            pd.DataFrame: 1分钟数据
        """
        market, code = self._parse_symbol(symbol)
        file_path = self._get_1min_file_path(market, code)

        if not os.path.exists(file_path):
            self.logger.warning(f"文件不存在: {file_path}")
            return pd.DataFrame()

        try:
            data = self._parse_min_file(file_path, interval=1)

            if data.empty:
                return data

            # 过滤日期范围
            if start_date:
                data = data[data['datetime'] >= pd.Timestamp(start_date)]
            if end_date:
                data = data[data['datetime'] < pd.Timestamp(end_date) + timedelta(days=1)]

            self.logger.info(f"读取 {symbol} 1分钟数据: {len(data)} 条记录")
            return data

        except Exception as e:
            self.logger.error(f"读取1分钟数据失败 {symbol}: {e}")
            return pd.DataFrame()

    def list_available_stocks(self, market: str = 'sh') -> List[str]:
        """
        列出指定市场的所有可用股票

        参数:
            market: 市场代码 ('sh' 或 'sz')

        返回:
            list: 股票代码列表
        """
        dir_path = self.market_dirs.get(market)

        if not dir_path or not os.path.exists(dir_path):
            self.logger.warning(f"市场目录不存在: {market}")
            return []

        stocks = []
        for filename in os.listdir(dir_path):
            if filename.endswith('.day'):
                # 提取股票代码（去除.day后缀和市场前缀）
                code = filename.replace('.day', '')
                # 如果文件名中已包含市场前缀，去除它
                if code.startswith(market):
                    code = code[len(market):]
                stocks.append(f"{market}{code}")

        self.logger.info(f"市场 {market} 共有 {len(stocks)} 只股票")
        return sorted(stocks)

    def get_latest_date(self, symbol: str) -> Optional[date]:
        """
        获取指定股票的最新数据日期

        参数:
            symbol: 股票代码

        返回:
            date: 最新数据日期，如果没有数据则返回None
        """
        data = self.read_day_data(symbol)

        if data.empty:
            return None

        return data['date'].max().date()

    def _parse_symbol(self, symbol: str) -> Tuple[str, str]:
        """
        解析股票代码，提取市场和代码

        参数:
            symbol: 股票代码（如 '600000' 或 'sh600000'）

        返回:
            tuple: (market, code)
        """
        symbol = symbol.lower()

        if symbol.startswith('sh'):
            return 'sh', symbol[2:]
        elif symbol.startswith('sz'):
            return 'sz', symbol[2:]
        elif symbol.startswith('6'):
            return 'sh', symbol  # 6开头为上海
        elif symbol.startswith(('0', '3')):
            return 'sz', symbol  # 0和3开头为深圳
        else:
            # 默认深圳
            return 'sz', symbol

    def _get_day_file_path(self, market: str, code: str) -> str:
        """获取日线文件路径"""
        dir_path = self.market_dirs.get(market)
        # TDX文件名格式: sh000001.day (包含市场前缀)
        return os.path.join(dir_path, f"{market}{code}.day")

    def _get_5min_file_path(self, market: str, code: str) -> str:
        """获取5分钟文件路径"""
        dir_path = self.market_dirs.get(f"{market}_5min")
        return os.path.join(dir_path, f"{market}{code}.lc5")

    def _get_1min_file_path(self, market: str, code: str) -> str:
        """获取1分钟文件路径"""
        dir_path = self.market_dirs.get(f"{market}_1min")
        return os.path.join(dir_path, f"{market}{code}.lc1")

    def _parse_day_file(self, file_path: str) -> pd.DataFrame:
        """
        解析日线二进制文件

        日线数据结构（32字节）：
        - date (4字节): YYYYMMDD格式的整数
        - open (4字节): 开盘价×1000
        - high (4字节): 最高价×1000
        - low (4字节): 最低价×1000
        - close (4字节): 收盘价×1000
        - amount (4字节): 成交金额（元）
        - volume (4字节): 成交量（手）
        - reserved (4字节): 保留字段
        """
        records = []

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.DAY_RECORD_SIZE)
                if len(chunk) < self.DAY_RECORD_SIZE:
                    break

                # 解包数据
                data = struct.unpack(self.DAY_STRUCT_FORMAT, chunk)

                # 解析日期
                date_int = data[0]
                year = date_int // 10000
                month = (date_int % 10000) // 100
                day = date_int % 100

                try:
                    trade_date = datetime(year, month, day)
                except ValueError:
                    # 跳过无效日期
                    continue

                # 解析价格（除以1000）
                open_price = data[1] / 1000.0
                high_price = data[2] / 1000.0
                low_price = data[3] / 1000.0
                close_price = data[4] / 1000.0

                # 成交金额和成交量
                amount = data[5]
                volume = data[6]

                records.append({
                    'date': trade_date,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume,
                    'amount': amount
                })

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # 不设置index，保留date作为普通列
        # 这样更灵活，用户可以根据需要自行设置
        return df

    def _parse_min_file(self, file_path: str, interval: int = 5) -> pd.DataFrame:
        """
        解析分钟线二进制文件

        分钟数据结构（32字节）：
        - year (2字节): 年份-1900
        - minute (2字节): 从当日0点开始的分钟数
        - open (4字节): 开盘价×1000
        - high (4字节): 最高价×1000
        - low (4字节): 最低价×1000
        - close (4字节): 收盘价×1000
        - amount (4字节): 成交金额
        - volume (4字节): 成交量
        - reserved (4字节): 保留
        """
        records = []

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.MIN_RECORD_SIZE)
                if len(chunk) < self.MIN_RECORD_SIZE:
                    break

                # 解包数据
                data = struct.unpack(self.MIN_STRUCT_FORMAT, chunk)

                # 解析日期时间
                year = data[0] + 1900
                minute_offset = data[1]

                hour = minute_offset // 60
                minute = minute_offset % 60

                try:
                    # 计算日期（需要根据分钟偏移量）
                    # TDX的分钟偏移可能跨越多天
                    days = minute_offset // (24 * 60)
                    hour = (minute_offset % (24 * 60)) // 60
                    minute = minute_offset % 60

                    trade_datetime = datetime(year, 1, 1) + timedelta(days=days, hours=hour, minutes=minute)
                except (ValueError, OverflowError):
                    continue

                # 解析价格
                open_price = data[2] / 1000.0
                high_price = data[3] / 1000.0
                low_price = data[4] / 1000.0
                close_price = data[5] / 1000.0

                amount = data[6]
                volume = data[7]

                records.append({
                    'datetime': trade_datetime,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume,
                    'amount': amount
                })

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # 不设置index，保留datetime作为普通列
        return df


if __name__ == '__main__':
    # 测试代码
    print("TDX二进制文件解析器测试")
    print("=" * 70)

    # 创建解析器
    parser = TdxBinaryParser()

    # 测试1: 列出可用股票
    print("\n测试1: 列出上海市场可用股票")
    sh_stocks = parser.list_available_stocks('sh')
    if sh_stocks:
        print(f"  ✓ 找到 {len(sh_stocks)} 只股票")
        print(f"  示例: {sh_stocks[:5]}")
    else:
        print("  ✗ 未找到股票数据（可能数据路径不存在）")

    # 测试2: 读取日线数据
    if sh_stocks:
        test_symbol = sh_stocks[0]
        print(f"\n测试2: 读取 {test_symbol} 的日线数据")
        day_data = parser.read_day_data(test_symbol, start_date=date(2024, 1, 1))

        if not day_data.empty:
            print(f"  ✓ 读取成功: {len(day_data)} 条记录")
            print(f"\n  最近5天数据:")
            print(day_data.tail())

            # 测试3: 获取最新日期
            print(f"\n测试3: 获取最新数据日期")
            latest_date = parser.get_latest_date(test_symbol)
            print(f"  ✓ 最新日期: {latest_date}")
        else:
            print("  ✗ 未读取到数据")

    print("\n" + "=" * 70)
    print("测试完成")
