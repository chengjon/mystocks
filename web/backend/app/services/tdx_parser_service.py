"""
通达信数据解析服务
用于解析通达信二进制 .day 文件格式
"""

import struct
from pathlib import Path
from typing import List, Optional
import pandas as pd


class TdxDayFileParser:
    """
    通达信 .day 文件解析器

    文件格式说明：
    - 每条记录 32 字节
    - 结构：IIIIIfII
    - 字段：日期、开盘、最高、最低、收盘、成交额、成交量、保留
    """

    RECORD_SIZE = 32
    STRUCT_FORMAT = "IIIIIfII"

    @staticmethod
    def parse_date(date_int: int) -> str:
        """
        解析通达信日期格式

        Args:
            date_int: 整数格式的日期（如：20231201）

        Returns:
            str: YYYY-MM-DD 格式的日期字符串
        """
        try:
            date_str = str(date_int)
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            return f"{year:04d}-{month:02d}-{day:02d}"
        except Exception:
            return str(date_int)

    @staticmethod
    def read_tdx_day_file(file_path: str, stock_code: str = None) -> pd.DataFrame:
        """
        读取通达信 .day 文件

        Args:
            file_path: .day 文件路径
            stock_code: 股票代码（可选）

        Returns:
            pd.DataFrame: 包含 OHLCV 数据的 DataFrame
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        data_list = []

        with open(file_path, "rb") as f:
            while True:
                buffer = f.read(TdxDayFileParser.RECORD_SIZE)
                if len(buffer) < TdxDayFileParser.RECORD_SIZE:
                    break

                # 解析二进制数据
                record = struct.unpack(TdxDayFileParser.STRUCT_FORMAT, buffer)

                # 提取字段
                date_int = record[0]
                open_price = record[1] / 100.0  # 价格字段需要除以100
                high_price = record[2] / 100.0
                low_price = record[3] / 100.0
                close_price = record[4] / 100.0
                amount = record[5]  # 成交额
                volume = record[6]  # 成交量

                # 解析日期
                trade_date = TdxDayFileParser.parse_date(date_int)

                data_list.append(
                    {
                        "code": stock_code or "unknown",
                        "tradeDate": trade_date,
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "amount": amount,
                        "volume": volume,
                    }
                )

        # 创建 DataFrame
        df = pd.DataFrame(data_list)

        # 按日期排序
        if not df.empty:
            df = df.sort_values("tradeDate").reset_index(drop=True)

        return df

    @staticmethod
    def convert_to_csv(input_file: str, output_file: str, stock_code: str = None) -> str:
        """
        将 .day 文件转换为 CSV 文件

        Args:
            input_file: 输入的 .day 文件路径
            output_file: 输出的 CSV 文件路径
            stock_code: 股票代码

        Returns:
            str: 输出文件路径
        """
        df = TdxDayFileParser.read_tdx_day_file(input_file, stock_code)
        df.to_csv(output_file, index=False, encoding="utf-8")
        return output_file

    @staticmethod
    def get_latest_data(file_path: str, days: int = 30) -> pd.DataFrame:
        """
        获取最近 N 天的数据

        Args:
            file_path: .day 文件路径
            days: 天数

        Returns:
            pd.DataFrame: 最近 N 天的数据
        """
        df = TdxDayFileParser.read_tdx_day_file(file_path)

        if df.empty:
            return df

        # 返回最后 N 行
        return df.tail(days)

    @staticmethod
    def get_date_range_data(file_path: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指定日期范围的数据

        Args:
            file_path: .day 文件路径
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）

        Returns:
            pd.DataFrame: 指定日期范围的数据
        """
        df = TdxDayFileParser.read_tdx_day_file(file_path)

        if df.empty:
            return df

        # 过滤日期范围
        mask = (df["tradeDate"] >= start_date) & (df["tradeDate"] <= end_date)
        return df[mask].reset_index(drop=True)


class TdxDataService:
    """通达信数据服务"""

    def __init__(self, data_dir: str = "/mnt/d/ProgramData/tdx_new/vipdoc"):
        """
        初始化服务

        Args:
            data_dir: 通达信数据目录路径
        """
        self.data_dir = Path(data_dir)
        self.parser = TdxDayFileParser()

    def get_stock_data(self, stock_code: str, market: str = "sh") -> Optional[pd.DataFrame]:
        """
        获取股票数据

        Args:
            stock_code: 股票代码（如：000001）
            market: 市场代码（sh-上海，sz-深圳）

        Returns:
            Optional[pd.DataFrame]: 股票数据，如果文件不存在返回 None
        """
        # 构建文件路径
        market_dir = "sh" if market.lower() == "sh" else "sz"
        file_path = self.data_dir / market_dir / "lday" / f"{market_dir}{stock_code}.day"

        if not file_path.exists():
            return None

        try:
            return self.parser.read_tdx_day_file(str(file_path), f"{market}{stock_code}")
        except Exception as e:
            print(f"读取股票数据失败: {e}")
            return None

    def get_index_data(self, index_code: str = "000001") -> Optional[pd.DataFrame]:
        """
        获取指数数据

        Args:
            index_code: 指数代码（默认：上证指数 000001）

        Returns:
            Optional[pd.DataFrame]: 指数数据
        """
        return self.get_stock_data(index_code, "sh")

    def list_available_stocks(self, market: str = "sh") -> List[str]:
        """
        列出可用的股票代码

        Args:
            market: 市场代码（sh 或 sz）

        Returns:
            List[str]: 股票代码列表
        """
        market_dir = "sh" if market.lower() == "sh" else "sz"
        lday_dir = self.data_dir / market_dir / "lday"

        if not lday_dir.exists():
            return []

        stocks = []
        for file_path in lday_dir.glob(f"{market_dir}*.day"):
            # 提取股票代码（去掉市场前缀和 .day 后缀）
            stock_code = file_path.stem[2:]  # 去掉 sh 或 sz 前缀
            stocks.append(stock_code)

        return sorted(stocks)

    def export_to_csv(self, stock_code: str, market: str, output_dir: str = "./exports") -> Optional[str]:
        """
        导出股票数据到 CSV

        Args:
            stock_code: 股票代码
            market: 市场代码
            output_dir: 输出目录

        Returns:
            Optional[str]: 输出文件路径，失败返回 None
        """
        df = self.get_stock_data(stock_code, market)

        if df is None or df.empty:
            return None

        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        output_file = output_path / f"{market}{stock_code}.csv"

        # 保存到 CSV
        df.to_csv(output_file, index=False, encoding="utf-8")

        return str(output_file)
