"""TDX 数据源适配器子模块"""

import logging
import os
import struct
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


class TdxKlineClassifyMixin:
    """TDX K线与分类数据"""

    def get_stock_kline(self, symbol: str, start_date: str, end_date: str, period: str = "1d") -> pd.DataFrame:
        """
        获取股票K线数据(支持多种周期)

        Args:
            symbol: 6位数字股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: K线周期
                - '1m':  1分钟
                - '5m':  5分钟
                - '15m': 15分钟
                - '30m': 30分钟
                - '1h':  1小时
                - '1d':  日线 (默认)
                - '1w':  周线 (新增)
                - '1M':  月线 (新增)
                - '1q':  季线 (新增)
                - '1y':  年线 (新增)

        Returns:
            pd.DataFrame: K线数据

        Example:
            >>> tdx = TdxDataSource()
            >>> # 获取5分钟K线
            >>> df = tdx.get_stock_kline('600519', '2024-01-01', '2024-01-31', period='5m')
            >>> # 获取周线数据 (新增)
            >>> df_weekly = tdx.get_stock_kline('600519', '2020-01-01', '2024-12-31', period='1w')
        """
        # 周期代码映射 (pytdx category参数)
        period_map = {
            "1m": 8,  # 1分钟
            "5m": 0,  # 5分钟
            "15m": 1,  # 15分钟
            "30m": 2,  # 30分钟
            "1h": 3,  # 1小时
            "1d": 9,  # 日线
            "1w": 5,  # 周线 (新增)
            "1M": 6,  # 月线 (新增)
            "1q": 10,  # 季线 (新增)
            "1y": 11,  # 年线 (新增)
        }

        if period not in period_map:
            self.logger.error("不支持的K线周期: %s, 支持的周期: %s", period, list(period_map.keys()))
            return pd.DataFrame()

        category = period_map[period]

        # 输入验证
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            self.logger.warning("无效的股票代码格式: %s", symbol)
            return pd.DataFrame()

        try:
            # 日期标准化
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)

            # 识别市场代码
            market = self._get_market_code(symbol)

            # 分页获取数据
            all_data = []
            start_pos = 0
            batch_size = 800
            max_batches = 50  # 分钟线数据量大,增加批次上限

            self.logger.info("开始获取股票%sK线: %s, 日期范围: %s ~ %s", period, symbol, start_date, end_date)

            @self._retry_api_call
            def fetch_kline_batch(start_position):
                with self._get_tdx_connection() as api:
                    if not api.connect(self.tdx_host, self.tdx_port):
                        raise ConnectionError("无法连接到TDX服务器")

                    result = api.get_security_bars(category, market, symbol, start_position, batch_size)
                    return result

            # 分批获取
            for batch_num in range(max_batches):
                try:
                    result_batch = fetch_kline_batch(start_pos)

                    if result_batch is None or not isinstance(result_batch, list) or len(result_batch) == 0:
                        self.logger.info("第%s批数据为空", batch_num + 1)
                        break

                    df_batch = pd.DataFrame(result_batch)
                    df_batch = ColumnMapper.to_english(df_batch)

                    # 日期格式化
                    if "datetime" in df_batch.columns:
                        df_batch["datetime"] = pd.to_datetime(df_batch["datetime"])
                        df_batch["date"] = df_batch["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

                    all_data.append(df_batch)
                    self.logger.debug("获取第%s批: %s条", batch_num + 1, len(df_batch))

                    # 检查是否已获取到start_date之前的数据
                    if "date" in df_batch.columns and len(df_batch) > 0:
                        earliest_date = df_batch["date"].min()[:10]  # 只比较日期部分
                        if earliest_date < start_date:
                            self.logger.info("已获取到%s之前的数据", start_date)
                            break

                    if len(df_batch) < batch_size:
                        break

                    start_pos += batch_size

                except Exception as e:
                    self.logger.error("获取第%s批失败: %s", batch_num + 1, e)
                    break

            if not all_data:
                self.logger.warning("未获取到%sK线数据", period)
                return pd.DataFrame()

            # 合并数据
            df_result = pd.concat(all_data, ignore_index=True)

            # 过滤日期范围
            if "date" in df_result.columns:
                df_result["date_only"] = pd.to_datetime(df_result["date"]).dt.strftime("%Y-%m-%d")
                df_result = df_result[(df_result["date_only"] >= start_date) & (df_result["date_only"] <= end_date)]
                df_result = df_result.drop(columns=["date_only"])

            # 按时间升序排列
            df_result = df_result.sort_values("date").reset_index(drop=True)

            self.logger.info("获取%sK线成功: %s, 共%s条数据", period, symbol, len(df_result))

            return df_result

        except Exception:
            self.logger.error("获取{period}K线失败: {e}", exc_info=True)
            return pd.DataFrame()

    def get_index_kline(self, symbol: str, start_date: str, end_date: str, period: str = "1d") -> pd.DataFrame:
        """
        获取指数K线数据(支持多种周期)

        Args:
            symbol: 6位数字指数代码
            start_date: 开始日期
            end_date: 结束日期
            period: K线周期
                - '1m':  1分钟
                - '5m':  5分钟
                - '15m': 15分钟
                - '30m': 30分钟
                - '1h':  1小时
                - '1d':  日线 (默认)
                - '1w':  周线 (新增)
                - '1M':  月线 (新增)
                - '1q':  季线 (新增)
                - '1y':  年线 (新增)

        Returns:
            pd.DataFrame: 指数K线数据
        """
        period_map = {
            "1m": 8,  # 1分钟
            "5m": 0,  # 5分钟
            "15m": 1,  # 15分钟
            "30m": 2,  # 30分钟
            "1h": 3,  # 1小时
            "1d": 9,  # 日线
            "1w": 5,  # 周线 (新增)
            "1M": 6,  # 月线 (新增)
            "1q": 10,  # 季线 (新增)
            "1y": 11,  # 年线 (新增)
        }

        if period not in period_map:
            self.logger.error("不支持的K线周期: %s", period)
            return pd.DataFrame()

        category = period_map[period]

        # 输入验证
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            self.logger.warning("无效的指数代码格式: %s", symbol)
            return pd.DataFrame()

        try:
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)

            # 指数市场识别
            prefix = symbol[:3]
            market = 0 if prefix == "399" else 1

            all_data = []
            start_pos = 0
            batch_size = 800
            max_batches = 50

            self.logger.info("开始获取指数%sK线: %s", period, symbol)

            @self._retry_api_call
            def fetch_index_batch(start_position):
                with self._get_tdx_connection() as api:
                    if not api.connect(self.tdx_host, self.tdx_port):
                        raise ConnectionError("无法连接到TDX服务器")

                    result = api.get_index_bars(category, market, symbol, start_position, batch_size)
                    return result

            for batch_num in range(max_batches):
                try:
                    result_batch = fetch_index_batch(start_pos)

                    if result_batch is None or not isinstance(result_batch, list) or len(result_batch) == 0:
                        break

                    df_batch = pd.DataFrame(result_batch)
                    df_batch = ColumnMapper.to_english(df_batch)

                    if "datetime" in df_batch.columns:
                        df_batch["datetime"] = pd.to_datetime(df_batch["datetime"])
                        df_batch["date"] = df_batch["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

                    all_data.append(df_batch)

                    if len(df_batch) < batch_size:
                        break

                    start_pos += batch_size

                except Exception as e:
                    self.logger.error("获取第%s批失败: %s", batch_num + 1, e)
                    break

            if not all_data:
                return pd.DataFrame()

            df_result = pd.concat(all_data, ignore_index=True)

            # 过滤日期
            if "date" in df_result.columns:
                df_result["date_only"] = pd.to_datetime(df_result["date"]).dt.strftime("%Y-%m-%d")
                df_result = df_result[(df_result["date_only"] >= start_date) & (df_result["date_only"] <= end_date)]
                df_result = df_result.drop(columns=["date_only"])

            df_result = df_result.sort_values("date").reset_index(drop=True)

            self.logger.info("获取指数%sK线成功: %s, 共%s条", period, symbol, len(df_result))

            return df_result

        except Exception:
            self.logger.error("获取指数{period}K线失败: {e}", exc_info=True)
            return pd.DataFrame()

    # ==================== 扩展功能: 二进制文件读取 ====================

    def read_day_file(self, file_path: str) -> pd.DataFrame:
        """
        读取通达信二进制 .day 文件

        通达信 .day 文件格式:
        - 每条记录32字节
        - 格式: struct.unpack('IIIIIfII', ...)
        - 字段: [日期, 开盘价*100, 最高价*100, 最低价*100,
                收盘价*100, 成交额, 成交量, 保留字段]

        Args:
            file_path: .day 文件的绝对路径

        Returns:
            pd.DataFrame: 包含OHLCV数据
                - code: 股票代码
                - tradeDate: 交易日期
                - open: 开盘价
                - high: 最高价
                - low: 最低价
                - close: 收盘价
                - amount: 成交额
                - vol: 成交量

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式错误

        Example:
            >>> tdx = TdxDataSource()
            >>> df = tdx.read_day_file('/path/to/sh000001.day')
            >>> print(df.head())
        """

        # 验证文件存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 从文件名提取股票代码
        code = os.path.basename(file_path).replace(".day", "")

        data_set = []
        row_size = 32  # 每条记录32字节

        try:
            with open(file_path, "rb") as fl:
                buffer = fl.read()
                size = len(buffer)

                # 验证文件大小
                if size % row_size != 0:
                    raise ValueError(f"文件大小({size}字节)不是{row_size}的倍数,可能损坏")

                # 逐条解析记录
                for i in range(0, size, row_size):
                    try:
                        # 解包二进制数据
                        row = list(struct.unpack("IIIIIfII", buffer[i : i + row_size]))

                        # 价格字段除以100 (索引1-4: 开高低收)
                        row[1] = row[1] / 100.0
                        row[2] = row[2] / 100.0
                        row[3] = row[3] / 100.0
                        row[4] = row[4] / 100.0

                        # 移除保留字段(最后一个)
                        row.pop()

                        # 添加股票代码到开头
                        row.insert(0, code)

                        data_set.append(row)

                    except struct.error as e:
                        self.logger.warning("解析第%s条记录失败: %s", i // row_size, e)
                        continue

        except Exception as e:
            self.logger.error("读取文件失败: %s", e)
            raise

        # 创建DataFrame
        df = pd.DataFrame(
            data=data_set,
            columns=[
                "code",
                "tradeDate",
                "open",
                "high",
                "low",
                "close",
                "amount",
                "vol",
            ],
        )

        # 数据验证
        if df.empty:
            self.logger.warning("文件%s没有有效数据", file_path)
            return df

        # 转换日期格式 (从整数YYYYMMDD转为字符串)
        df["tradeDate"] = df["tradeDate"].astype(str)

        # 数据质量检查
        invalid_count = (df[["open", "high", "low", "close"]] <= 0).any(axis=1).sum()
        if invalid_count > 0:
            self.logger.warning("发现%s条无效价格记录(价格<=0)", invalid_count)

        self.logger.info("成功读取%s: %s条记录", file_path, len(df))

        return df

    def get_minute_kline(self, symbol: str, period: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取分钟K线数据

        Args:
            symbol: str - 股票代码
            period: str - 周期 (1m/5m/15m/30m/60m)
            start_date: str - 开始日期
            end_date: str - 结束日期

        Returns:
            pd.DataFrame: 分钟K线数据
        """
        return self.get_stock_kline(symbol, start_date, end_date, period)

    def get_industry_classify(self) -> pd.DataFrame:
        """
        获取行业分类数据（TDX不直接提供此功能，返回空DataFrame）

        Returns:
            pd.DataFrame: 行业分类数据
        """
        self.logger.info("[TDX] 注意：TDX不直接提供行业分类数据，建议使用AkShare适配器")
        return pd.DataFrame()

    def get_concept_classify(self) -> pd.DataFrame:
        """
        获取概念分类数据（TDX不直接提供此功能，返回空DataFrame）

        Returns:
            pd.DataFrame: 概念分类数据
        """
        self.logger.info("[TDX] 注意：TDX不直接提供概念分类数据，建议使用AkShare适配器")
        return pd.DataFrame()

    def get_stock_industry_concept(self, symbol: str) -> Dict:
        """
        获取个股的行业和概念分类信息（TDX不直接提供此功能，返回空字典）

        Args:
            symbol: str - 股票代码

        Returns:
            Dict: 个股行业和概念信息
        """
        self.logger.info("[TDX] 注意：TDX不直接提供个股 %s 的行业和概念信息，建议使用AkShare适配器", symbol)
        return {"symbol": symbol, "industries": [], "concepts": []}
