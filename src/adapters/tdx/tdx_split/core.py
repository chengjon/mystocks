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


class TdxCoreMixin:
    """TDX 核心：初始化、连接、工具方法"""

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
                self.logger.info("主服务器: %s:%s", self.tdx_host, self.tdx_port)
                self.logger.info("可用服务器总数: %s", self.server_config.get_server_count())
            except Exception as e:
                self.logger.warning("加载connect.cfg失败: %s, 使用环境变量配置", e)
                self.use_server_config = False
                self.server_config = None
                self.tdx_host = tdx_host or os.getenv("TDX_SERVER_HOST", "101.227.73.20")
                self.tdx_port = int(tdx_port or os.getenv("TDX_SERVER_PORT", "7709"))
        else:
            self.server_config = None
            self.tdx_host = tdx_host or os.getenv("TDX_SERVER_HOST", "101.227.73.20")
            self.tdx_port = int(tdx_port or os.getenv("TDX_SERVER_PORT", "7709"))
            self.logger.info("TDX适配器初始化: %s:%s", self.tdx_host, self.tdx_port)

        self.logger.info("重试配置: max_retries=%s, retry_delay=%ss", self.max_retries, self.retry_delay)

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
                                self.logger.info("切换服务器: %s → %s", old_server, new_server)
                            except Exception as switch_error:
                                self.logger.warning("切换服务器失败: %s", switch_error)

                        self.logger.warning(
                            "API调用失败 (尝试 %d/%d): %s, %d秒后重试...", attempt, self.max_retries, str(e), delay
                        )
                        time.sleep(delay)
                    else:
                        self.logger.error(
                            "API调用失败 (所有%d次尝试均失败): %s",
                            self.max_retries,
                            str(e),
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
            self.logger.error("K线数据缺少必需列: %s", missing_cols)
            return pd.DataFrame()

        # 2. 价格列非负
        price_cols = ["open", "high", "low", "close"]
        for col in price_cols:
            if (df[col] < 0).any():
                self.logger.warning("%s列存在负值,已修正为0", col)
                df[col] = df[col].clip(lower=0)

        # 3. 成交量非负
        if (df["volume"] < 0).any():
            self.logger.warning("volume列存在负值,已修正为0")
            df["volume"] = df["volume"].clip(lower=0)

        # 4. OHLC逻辑检查(仅警告,不修改数据)
        invalid_rows = df[df["high"] < df[["open", "close", "low"]].max(axis=1)]
        if not invalid_rows.empty:
            self.logger.warning("发现%s行OHLC逻辑异常(high < max(open, close, low))", len(invalid_rows))

        return df

    # ==================== T011: 所有IDataSource方法的stub实现 ====================
    # 这些将在后续Phase中逐个实现

