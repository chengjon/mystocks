"""
# 功能：通达信(TDX)数据源适配器，提供实时行情和多周期K线数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import logging
import os
import sys
import time
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional

import pandas as pd

# 添加temp目录到路径以导入本地pytdx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "temp"))
from pytdx.hq import TdxHq_API

# 导入MyStocks工具类
sys.path.insert(0, os.path.dirname(__file__) + "/..")
from src.interfaces.data_source import IDataSource
from src.utils.column_mapper import ColumnMapper
from src.utils.date_utils import normalize_date
from src.utils.tdx_server_config import TdxServerConfig


class TdxDataSource(IDataSource):
    """
    TDX(通达信)数据源适配器

    实现IDataSource接口,提供A股市场数据访问:
    - 实时行情 (get_real_time_data)
    - 历史日线 (get_stock_daily, get_index_daily)
    - 财务数据 (get_financial_data - 有限支持)
    - 板块信息 (get_index_components - 有限支持)

    特点:
    - 直连通达信服务器,无API限流
    - 使用本地pytdx代码(temp/pytdx/),可二次开发
    - 自动重试、连接管理、数据验证
    - 完整日志记录

    限制:
    - 仅支持A股(深交所+上交所),不含期货/期权
    - 部分IDataSource方法为stub实现(get_market_calendar, get_news_data)
    """

    def __init__(
        self,
        tdx_host: Optional[str] = None,
        tdx_port: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[int] = None,
        api_timeout: Optional[int] = None,
        use_server_config: bool = True,
        config_file: Optional[str] = None,
    ):
        """
        初始化TDX数据源适配器

        Args:
            tdx_host: TDX服务器地址 (默认从环境变量TDX_SERVER_HOST读取)
            tdx_port: TDX服务器端口 (默认从环境变量TDX_SERVER_PORT读取)
            max_retries: 最大重试次数 (默认从环境变量TDX_MAX_RETRIES读取,默认3)
            retry_delay: 重试延迟秒数 (默认从环境变量TDX_RETRY_DELAY读取,默认1)
            api_timeout: API超时时间 (默认从环境变量TDX_API_TIMEOUT读取,默认10)
            use_server_config: 是否使用connect.cfg配置的服务器列表(默认True)
            config_file: connect.cfg文件路径(可选)
        """
        # T005: 配置加载
        self.max_retries = int(max_retries or os.getenv("TDX_MAX_RETRIES", "3"))
        self.retry_delay = int(retry_delay or os.getenv("TDX_RETRY_DELAY", "1"))
        self.api_timeout = int(api_timeout or os.getenv("TDX_API_TIMEOUT", "10"))

        # T010: 日志初始化
        self.logger = logging.getLogger(__name__)

        # 服务器配置管理
        self.use_server_config = use_server_config
        self.server_config: Optional[TdxServerConfig] = None
        if use_server_config:
            try:
                self.server_config = TdxServerConfig(config_file)
                self.tdx_host, self.tdx_port = self.server_config.get_primary_server()
                self.logger.info("TDX适配器初始化: 使用connect.cfg配置")
                self.logger.info(f"主服务器: {self.tdx_host}:{self.tdx_port}")
                self.logger.info(f"可用服务器总数: {self.server_config.get_server_count()}")
            except Exception as e:
                self.logger.warning(f"加载connect.cfg失败: {e}, 使用环境变量配置")
                self.use_server_config = False
                self.server_config = None
                self.tdx_host = tdx_host or os.getenv("TDX_SERVER_HOST", "101.227.73.20")
                self.tdx_port = int(tdx_port or os.getenv("TDX_SERVER_PORT", "7709"))
        else:
            self.server_config = None
            self.tdx_host = tdx_host or os.getenv("TDX_SERVER_HOST", "101.227.73.20")
            self.tdx_port = int(tdx_port or os.getenv("TDX_SERVER_PORT", "7709"))
            self.logger.info(f"TDX适配器初始化: {self.tdx_host}:{self.tdx_port}")

        self.logger.info(f"重试配置: max_retries={self.max_retries}, retry_delay={self.retry_delay}s")

    # ==================== T006: 连接管理辅助方法 ====================

    def _get_tdx_connection(self):
        """
        获取TDX连接(上下文管理器)

        Returns:
            TdxHq_API实例的上下文管理器

        Example:
            with self._get_tdx_connection() as api:
                data = api.get_security_quotes([...])
        """
        return TdxHq_API()

    # ==================== T007: 市场代码识别辅助方法 ====================

    def _get_market_code(self, symbol: str) -> int:
        """
        识别股票代码对应的市场类型

        Args:
            symbol: 6位数字股票代码 (如'600519', '000001')

        Returns:
            0 = 深圳证券交易所 (深市主板/中小板/创业板)
            1 = 上海证券交易所 (沪市主板/科创板)

        Raises:
            ValueError: 如果股票代码格式无效或无法识别市场

        市场识别规则:
            - 000xxx, 002xxx, 300xxx → 深圳 (主板/中小板/创业板)
            - 600xxx, 601xxx, 603xxx, 688xxx → 上海 (主板/科创板)
        """
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            raise ValueError(f"无效的股票代码格式: {symbol} (需要6位数字)")

        prefix = symbol[:3]

        # 深圳市场
        if prefix in ["000", "002", "300"]:
            return 0

        # 上海市场 (包含ETF)
        if prefix in [
            "600",
            "601",
            "603",
            "688",
            "510",
            "511",
            "512",
            "513",
            "514",
            "515",
            "516",
            "517",
            "518",
            "519",
            "588",
        ]:
            return 1

        raise ValueError(f"无法识别的股票代码: {symbol} (前缀{prefix}不在已知范围)")

    # ==================== T008: 重试装饰器 ====================

    def _retry_api_call(self, func):
        """
        API调用重试装饰器(带指数退避和服务器故障转移)

        Args:
            func: 要包装的函数

        Returns:
            包装后的函数(自动重试)

        行为:
            - 失败时自动重试max_retries次
            - 每次重试延迟逐渐增加(指数退避)
            - 如果启用server_config,在重试时切换到备用服务器
            - 最后一次失败时抛出原始异常
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < self.max_retries:
                        delay = self.retry_delay * (2 ** (attempt - 1))  # 指数退避: 1s, 2s, 4s...

                        # 如果启用服务器配置,尝试切换到备用服务器
                        if self.use_server_config and self.server_config:
                            try:
                                old_server = f"{self.tdx_host}:{self.tdx_port}"
                                self.tdx_host, self.tdx_port = self.server_config.get_random_server()
                                new_server = f"{self.tdx_host}:{self.tdx_port}"
                                self.logger.info(f"切换服务器: {old_server} → {new_server}")
                            except Exception as switch_error:
                                self.logger.warning(f"切换服务器失败: {switch_error}")

                        self.logger.warning(
                            f"API调用失败 (尝试 {attempt}/{self.max_retries}): {str(e)}, " f"{delay}秒后重试..."
                        )
                        time.sleep(delay)
                    else:
                        self.logger.error(
                            f"API调用失败 (所有{self.max_retries}次尝试均失败): {str(e)}",
                            exc_info=True,
                        )
                        raise

        return wrapper

    # ==================== T009: 数据验证辅助方法 ====================

    def _validate_kline_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        验证K线数据完整性和合法性

        Args:
            df: K线DataFrame

        Returns:
            验证并清理后的DataFrame

        验证项:
            1. 检查必需列是否存在
            2. 价格列非负
            3. 成交量非负
            4. OHLC逻辑 (high >= max(open, close, low))
        """
        if df.empty:
            return df

        # 1. 检查必需列
        required_cols = ["date", "open", "high", "low", "close", "volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            self.logger.error(f"K线数据缺少必需列: {missing_cols}")
            return pd.DataFrame()

        # 2. 价格列非负
        price_cols = ["open", "high", "low", "close"]
        for col in price_cols:
            if (df[col] < 0).any():
                self.logger.warning(f"{col}列存在负值,已修正为0")
                df[col] = df[col].clip(lower=0)

        # 3. 成交量非负
        if (df["volume"] < 0).any():
            self.logger.warning("volume列存在负值,已修正为0")
            df["volume"] = df["volume"].clip(lower=0)

        # 4. OHLC逻辑检查(仅警告,不修改数据)
        invalid_rows = df[df["high"] < df[["open", "close", "low"]].max(axis=1)]
        if not invalid_rows.empty:
            self.logger.warning(f"发现{len(invalid_rows)}行OHLC逻辑异常(high < max(open, close, low))")

        return df

    # ==================== T011: 所有IDataSource方法的stub实现 ====================
    # 这些将在后续Phase中逐个实现

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

            self.logger.info(f"开始获取股票日线: {symbol}, 日期范围: {start_date} ~ {end_date}")

            @self._retry_api_call
            def fetch_kline_batch(start_position):
                """获取单批K线数据"""
                with self._get_tdx_connection() as api:
                    if not api.connect(self.tdx_host, self.tdx_port):
                        raise ConnectionError(f"无法连接到TDX服务器: {self.tdx_host}:{self.tdx_port}")

                    # category=9表示日K线
                    result = api.get_security_bars(9, market, symbol, start_position, batch_size)
                    return result

            # 分批获取数据
            for batch_num in range(max_batches):
                try:
                    result_batch = fetch_kline_batch(start_pos)

                    # pytdx返回list of OrderedDict,需要转换为DataFrame
                    if result_batch is None or not isinstance(result_batch, list) or len(result_batch) == 0:
                        self.logger.info(f"第{batch_num + 1}批数据为空,已获取所有数据")
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
                    self.logger.debug(f"获取第{batch_num + 1}批数据: {len(df_batch)}条")

                    # 检查是否已获取到start_date之前的数据
                    if "date" in df_batch.columns and len(df_batch) > 0:
                        earliest_date = df_batch["date"].min()
                        if earliest_date < start_date:
                            self.logger.info(f"已获取到{start_date}之前的数据,停止分页")
                            break

                    # 如果返回数据少于batch_size,说明已到最早数据
                    if len(df_batch) < batch_size:
                        self.logger.info(f"返回数据量({len(df_batch)}) < batch_size({batch_size}), 已到最早数据")
                        break

                    start_pos += batch_size

                except Exception as e:
                    self.logger.error(f"获取第{batch_num + 1}批数据失败: {str(e)}")
                    break

            # T021: 合并和过滤数据
            if not all_data:
                self.logger.warning(f"未获取到股票{symbol}的日线数据")
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
                f"获取股票日线成功: {symbol}, 共{len(df_result)}条数据 "
                f"({df_result['date'].min()} ~ {df_result['date'].max()})"
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

            self.logger.info(f"开始获取指数日线: {symbol}, 日期范围: {start_date} ~ {end_date}")

            @self._retry_api_call
            def fetch_index_batch(start_position):
                """获取单批指数K线数据"""
                with self._get_tdx_connection() as api:
                    if not api.connect(self.tdx_host, self.tdx_port):
                        raise ConnectionError(f"无法连接到TDX服务器: {self.tdx_host}:{self.tdx_port}")

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
                        self.logger.info(f"第{batch_num + 1}批数据为空,已获取所有数据")
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
                    self.logger.debug(f"获取第{batch_num + 1}批数据: {len(df_batch)}条")

                    # 检查是否已获取到start_date之前的数据
                    if "date" in df_batch.columns and len(df_batch) > 0:
                        earliest_date = df_batch["date"].min()
                        if earliest_date < start_date:
                            self.logger.info(f"已获取到{start_date}之前的数据,停止分页")
                            break

                    # 如果返回数据少于batch_size,说明已到最早数据
                    if len(df_batch) < batch_size:
                        self.logger.info(f"返回数据量({len(df_batch)}) < batch_size({batch_size}), 已到最早数据")
                        break

                    start_pos += batch_size

                except Exception as e:
                    self.logger.error(f"获取第{batch_num + 1}批数据失败: {str(e)}")
                    break

            # T026: 合并和过滤数据
            if not all_data:
                self.logger.warning(f"未获取到指数{symbol}的日线数据")
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
                f"获取指数日线成功: {symbol}, 共{len(df_result)}条数据 "
                f"({df_result['date'].min()} ~ {df_result['date'].max()})"
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

    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息 - Phase 6实现(有限支持)"""
        try:
            # 通过查询日线数据获取基本信息
            df = self.get_stock_daily(symbol, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d"))

            if not df.empty:
                # 提取基本信息
                latest_record = df.iloc[-1]  # 最新记录

                # 构建股票基本信息
                basic_info = {
                    "symbol": symbol,
                    "name": latest_record.get("name", f"股票{symbol}"),  # 实际上可能需要单独的接口获取名称
                    "market": "SH" if symbol.startswith("6") else "SZ",
                    "category": "stock",  # 类别可以是stock, index, fund等
                    "status": "trading",  # 交易状态
                    "currency": "CNY",  # 货币
                    "industry": "",  # 行业信息，需要另外获取
                    "area": "",  # 地区信息
                    "list_date": latest_record.get("date", ""),  # 上市日期
                    "total_shares": None,  # 总股本
                    "float_shares": None,  # 流通股本
                }

                return basic_info
            else:
                # 如果无法从日线数据获取，返回默认值
                return {
                    "symbol": symbol,
                    "name": f"股票{symbol}",
                    "market": "SH" if symbol.startswith("6") else "SZ",
                    "category": "stock",
                    "status": "unknown",
                    "currency": "CNY",
                    "industry": "",
                    "area": "",
                    "list_date": "",
                    "total_shares": None,
                    "float_shares": None,
                }
        except Exception as e:
            self.logger.error(f"获取股票基本信息失败 {symbol}: {str(e)}")
            return {}

    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股 - Phase 7实现(有限支持)"""
        try:
            # TDX API不直接支持获取指数成分股，返回空列表
            # 这是一个已知限制，因为TDX API功能有限
            self.logger.info(f"TDX不支持直接获取指数成分股: {symbol}")

            # 如果是常见的指数，我们可以返回模拟数据
            if symbol in ["000001", "000300", "000016", "399001", "399006"]:
                # 这些是上证指数、沪深300、上证50、深证成指、创业板指
                # 实际应用中应通过其他接口获取这些指数的成分股
                self.logger.warning(f"{symbol} 为常见指数,但TDX不提供成分股查询")

            return []
        except Exception as e:
            self.logger.error(f"获取指数成分股失败 {symbol}: {str(e)}")
            return []

    def get_real_time_data(self, symbol: str) -> Optional[Dict]:
        """
        获取实时行情数据

        Args:
            symbol: 6位数字股票代码 (如'600519')

        Returns:
            Dict: 成功时返回包含实时行情的字典
                {
                    'code': str,          # 股票代码
                    'name': str,          # 股票名称
                    'price': float,       # 最新价
                    'pre_close': float,   # 昨收价
                    'open': float,        # 今开价
                    'high': float,        # 最高价
                    'low': float,         # 最低价
                    'volume': int,        # 成交量(手)
                    'amount': float,      # 成交额(元)
                    'bid1': float,        # 买一价
                    'bid1_volume': int,   # 买一量
                    'ask1': float,        # 卖一价
                    'ask1_volume': int,   # 卖一量
                    'timestamp': str      # 查询时间戳
                }
            str: 失败时返回错误消息字符串

        Example:
            >>> tdx = TdxDataSource()
            >>> quote = tdx.get_real_time_data('600519')
            >>> if isinstance(quote, dict):
            >>>     print(f"当前价: {quote['price']}")
        """
        # T018: 输入验证
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            error_msg = f"无效的股票代码格式: {symbol} (需要6位数字)"
            self.logger.warning(error_msg)
            return error_msg

        try:
            # 识别市场代码
            market = self._get_market_code(symbol)

            # 包装API调用以支持重试
            @self._retry_api_call
            def fetch_quote():
                with self._get_tdx_connection() as api:
                    if not api.connect(self.tdx_host, self.tdx_port):
                        raise ConnectionError(f"无法连接到TDX服务器: {self.tdx_host}:{self.tdx_port}")

                    # 调用get_security_quotes获取实时行情
                    # 参数: [(market, code), ...]  市场代码和股票代码的元组列表
                    result = api.get_security_quotes([(market, symbol)])

                    # 返回DataFrame
                    return result

            # 执行API调用
            result = fetch_quote()

            # pytdx返回list of OrderedDict,需要转换为DataFrame
            if result is None or not isinstance(result, list) or len(result) == 0:
                error_msg = f"未获取到股票{symbol}的实时行情数据"
                self.logger.warning(error_msg)
                return error_msg

            # 转换为DataFrame
            df = pd.DataFrame(result)

            # 应用列名映射(中文→英文)
            df = ColumnMapper.to_english(df)

            # 提取第一行数据转为字典
            row = df.iloc[0]

            # 构建标准化返回字典
            quote_dict = {
                "code": symbol,
                "name": row.get("name", ""),
                "price": float(row.get("price", 0)),
                "pre_close": float(row.get("last_close", 0)),  # pytdx中昨收叫last_close
                "open": float(row.get("open", 0)),
                "high": float(row.get("high", 0)),
                "low": float(row.get("low", 0)),
                "volume": int(row.get("vol", 0)),  # pytdx中成交量叫vol,单位:手
                "amount": float(row.get("amount", 0)),  # 成交额,单位:元
                "bid1": float(row.get("bid1", 0)),  # 买一价
                "bid1_volume": int(row.get("bid_vol1", 0)),  # 买一量
                "ask1": float(row.get("ask1", 0)),  # 卖一价
                "ask1_volume": int(row.get("ask_vol1", 0)),  # 卖一量
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 当前时间戳
            }

            # T017: 成功日志
            self.logger.info(
                f"获取实时行情成功: {symbol}({quote_dict['name']}) "
                f"价格={quote_dict['price']:.2f} 成交量={quote_dict['volume']}"
            )

            return quote_dict

        except ConnectionError as e:
            error_msg = f"网络连接失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return error_msg

        except ValueError as e:
            # _get_market_code抛出的异常
            error_msg = f"股票代码错误: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

        except Exception as e:
            error_msg = f"获取实时行情失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return error_msg

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取交易日历 - Phase 8 stub实现(TDX不支持)"""
        self.logger.warning("get_market_calendar不被TDX适配器支持,请使用akshare等其他数据源")
        return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "quarter") -> pd.DataFrame:
        """获取财务数据 - Phase 6实现(有限支持)"""
        try:
            # TDX API不直接支持财务数据查询，返回空DataFrame
            # 在实际应用中，这功能通常需要其他数据源支持
            self.logger.info(f"TDX不支持财务数据查询: {symbol}, 建议使用其他数据源")

            # 返回包含列名的空DataFrame，以保持接口一致性
            financial_columns = [
                "symbol",
                "report_date",
                "eps",
                "bvps",
                "roe",
                "roa",
                "pe",
                "pb",
                "ps",
                "pcf",
                "total_revenue",
                "net_profit",
                "total_assets",
                "total_liabilities",
                "operating_cash_flow",
            ]

            return pd.DataFrame(columns=financial_columns)
        except Exception as e:
            self.logger.error(f"获取财务数据失败 {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_news_data(self, symbol: str, limit: int = 20) -> List[Dict]:
        """获取新闻数据 - Phase 8 stub实现(TDX不支持)"""
        self.logger.warning("get_news_data不被TDX适配器支持,请使用akshare等其他数据源")
        return []

    # ==================== 扩展功能: 多周期K线 ====================

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

        Returns:
            pd.DataFrame: K线数据

        Example:
            >>> tdx = TdxDataSource()
            >>> # 获取5分钟K线
            >>> df = tdx.get_stock_kline('600519', '2024-01-01', '2024-01-31', period='5m')
        """
        # 周期代码映射 (pytdx category参数)
        period_map = {
            "1m": 8,  # 1分钟
            "5m": 0,  # 5分钟
            "15m": 1,  # 15分钟
            "30m": 2,  # 30分钟
            "1h": 3,  # 1小时
            "1d": 9,  # 日线
        }

        if period not in period_map:
            self.logger.error(f"不支持的K线周期: {period}, 支持的周期: {list(period_map.keys())}")
            return pd.DataFrame()

        category = period_map[period]

        # 输入验证
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            self.logger.warning(f"无效的股票代码格式: {symbol}")
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

            self.logger.info(f"开始获取股票{period}K线: {symbol}, 日期范围: {start_date} ~ {end_date}")

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
                        self.logger.info(f"第{batch_num + 1}批数据为空")
                        break

                    df_batch = pd.DataFrame(result_batch)
                    df_batch = ColumnMapper.to_english(df_batch)

                    # 日期格式化
                    if "datetime" in df_batch.columns:
                        df_batch["datetime"] = pd.to_datetime(df_batch["datetime"])
                        df_batch["date"] = df_batch["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

                    all_data.append(df_batch)
                    self.logger.debug(f"获取第{batch_num + 1}批: {len(df_batch)}条")

                    # 检查是否已获取到start_date之前的数据
                    if "date" in df_batch.columns and len(df_batch) > 0:
                        earliest_date = df_batch["date"].min()[:10]  # 只比较日期部分
                        if earliest_date < start_date:
                            self.logger.info(f"已获取到{start_date}之前的数据")
                            break

                    if len(df_batch) < batch_size:
                        break

                    start_pos += batch_size

                except Exception as e:
                    self.logger.error(f"获取第{batch_num + 1}批失败: {e}")
                    break

            if not all_data:
                self.logger.warning(f"未获取到{period}K线数据")
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

            self.logger.info(f"获取{period}K线成功: {symbol}, 共{len(df_result)}条数据")

            return df_result

        except Exception as e:
            self.logger.error(f"获取{period}K线失败: {e}", exc_info=True)
            return pd.DataFrame()

    def get_index_kline(self, symbol: str, start_date: str, end_date: str, period: str = "1d") -> pd.DataFrame:
        """
        获取指数K线数据(支持多种周期)

        Args:
            symbol: 6位数字指数代码
            start_date: 开始日期
            end_date: 结束日期
            period: K线周期 ('1m', '5m', '15m', '30m', '1h', '1d')

        Returns:
            pd.DataFrame: 指数K线数据
        """
        period_map = {
            "1m": 8,
            "5m": 0,
            "15m": 1,
            "30m": 2,
            "1h": 3,
            "1d": 9,
        }

        if period not in period_map:
            self.logger.error(f"不支持的K线周期: {period}")
            return pd.DataFrame()

        category = period_map[period]

        # 输入验证
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            self.logger.warning(f"无效的指数代码格式: {symbol}")
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

            self.logger.info(f"开始获取指数{period}K线: {symbol}")

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
                    self.logger.error(f"获取第{batch_num + 1}批失败: {e}")
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

            self.logger.info(f"获取指数{period}K线成功: {symbol}, 共{len(df_result)}条")

            return df_result

        except Exception as e:
            self.logger.error(f"获取指数{period}K线失败: {e}", exc_info=True)
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
        import struct

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
                        self.logger.warning(f"解析第{i//row_size}条记录失败: {e}")
                        continue

        except Exception as e:
            self.logger.error(f"读取文件失败: {e}")
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
            self.logger.warning(f"文件{file_path}没有有效数据")
            return df

        # 转换日期格式 (从整数YYYYMMDD转为字符串)
        df["tradeDate"] = df["tradeDate"].astype(str)

        # 数据质量检查
        invalid_count = (df[["open", "high", "low", "close"]] <= 0).any(axis=1).sum()
        if invalid_count > 0:
            self.logger.warning(f"发现{invalid_count}条无效价格记录(价格<=0)")

        self.logger.info(f"成功读取{file_path}: {len(df)}条记录")

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
        self.logger.info(f"[TDX] 注意：TDX不直接提供个股 {symbol} 的行业和概念信息，建议使用AkShare适配器")
        return {"symbol": symbol, "industries": [], "concepts": []}
