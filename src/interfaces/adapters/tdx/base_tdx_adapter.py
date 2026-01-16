"""
# 功能：基础TDX适配器
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：TDX适配器的基础类和共享组件
"""

import logging
import os
import sys
import time
from datetime import datetime
from functools import wraps
from typing import Dict, Optional, Any, Callable

import pandas as pd

# 导入MyStocks工具类
from src.interfaces.data_source import IDataSource
from src.utils.column_mapper import ColumnMapper
from src.utils.date_utils import normalize_date
from src.utils.tdx_server_config import TdxServerConfig

# 添加temp目录到路径以导入本地pytdx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "temp"))
try:
    from pytdx.hq import TdxHq_API

    PYTDX_AVAILABLE = True
except ImportError:
    PYTDX_AVAILABLE = False
    TdxHq_API = None


def tdx_retry(
    max_retries: int = 3,
    retry_delay: int = 1,
     api_timeout: int = 10):
    """
    TDX API重试装饰器

    Args:
        max_retries: 最大重试次数
        retry_delay: 重试延迟秒数
        api_timeout: API超时时间
    """


def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == max_retries:
                        self.logger.error(
    "TDX API调用失败 (尝试 %s/%s): %s", attempt + 1, max_retries + 1, e)
                        raise

                    self.logger.warning(
                        "TDX API调用失败，%s秒后重试 (尝试 %s/%s): %s", retry_delay, attempt +
                                             1, max_retries + 1, e
                    )
                    time.sleep(retry_delay)

            # 如果所有重试都失败了，抛出最后的异常
            raise last_exception

        return wrapper

    return decorator


class BaseTdxAdapter(IDataSource):
    """
    基础TDX适配器抽象类

    提供TDX数据访问的通用功能和接口
    """

def __init__(self):
        """初始化基础TDX适配器"""
        # TDX配置
        self.max_retries = int(os.getenv("TDX_MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("TDX_RETRY_DELAY", "1"))
        self.api_timeout = int(os.getenv("TDX_API_TIMEOUT", "10"))

        # 日志配置
        self.logger = logging.getLogger(__name__)

        # 服务器配置
        self.use_server_config = True
        self.server_config: Optional[TdxServerConfig] = None
        self.tdx_host = None
        self.tdx_port = None

        # 检查依赖
        self._check_dependencies()

        # 初始化服务器配置
        self._init_server_config()

        # 列映射器
        self.column_mapper = ColumnMapper()

        # 连接实例
        self._connection = None

def _check_dependencies(self) -> None:
        """检查TDX依赖库的可用性"""
        if not PYTDX_AVAILABLE:
            raise ImportError("TDX库(pytdx)不可用。请安装pytdx: pip install pytdx")

        self.logger.info("TDX依赖库检查通过")

def _init_server_config(self) -> None:
        """初始化服务器配置"""
        if self.use_server_config:
            try:
                self.server_config = TdxServerConfig()
                self.tdx_host, self.tdx_port = self.server_config.get_primary_server()
                self.logger.info("TDX适配器初始化: 使用connect.cfg配置")
                self.logger.info("主服务器: %s:%s", self.tdx_host, self.tdx_port)
                self.logger.info("可用服务器总数: %s", self.server_config.get_server_count())
            except Exception as e:
                self.logger.warning("加载connect.cfg失败: %s, 使用环境变量配置", e)
                self.use_server_config = False
                self._load_env_config()

        if not self.tdx_host or not self.tdx_port:
            self._load_env_config()

def _load_env_config(self) -> None:
        """从环境变量加载配置"""
        self.tdx_host = os.getenv("TDX_SERVER_HOST", "119.147.212.81")
        self.tdx_port = int(os.getenv("TDX_SERVER_PORT", "7709"))
        self.logger.info("TDX适配器初始化: 使用环境变量配置")
        self.logger.info("服务器: %s:%s", self.tdx_host, self.tdx_port)

def _get_tdx_connection(self) -> TdxHq_API:
        """获取TDX连接"""
        if self._connection is None:
            try:
                self.logger.info("创建TDX连接到 %s:%s", self.tdx_host, self.tdx_port)
                self._connection = TdxHq_API()

                # 连接到服务器
                if not self._connection.connect(self.tdx_host, self.tdx_port):
                    raise ConnectionError(f"无法连接到TDX服务器 {self.tdx_host}:{self.tdx_port}")

                self.logger.info("TDX连接创建成功")
            except Exception as e:
                self.logger.error("创建TDX连接失败: %s", e)
                raise

        return self._connection

def _get_market_code(self, symbol: str) -> int:
        """获取市场代码"""
        if not symbol:
            raise ValueError("股票代码不能为空")

        # 上交所股票代码以6开头，深交所以0或3开头
        if symbol.startswith(("6", "60")):
            return 1  # 上海市场
        elif symbol.startswith(("0", "30", "00", "300")):
            return 0  # 深圳市场
        else:
            # 默认为深圳市场
            return 0

    @tdx_retry(max_retries=3, retry_delay=1)
def _safe_api_call(self, func, *args, **kwargs):
        """安全的API调用包装"""
        return func(*args, **kwargs)

def _validate_kline_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """验证K线数据的完整性"""
        if df is None or df.empty:
            raise ValueError("K线数据为空")

        # 检查必要的列
        required_columns = ["datetime", "open", "high", "low", "close", "volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            # 尝试使用备用的列名
            column_mapping = {
                "datetime": ["time", "date", "trade_date"],
                "open": ["开盘", "open_price"],
                "high": ["最高", "high_price"],
                "low": ["最低", "low_price"],
                "close": ["收盘", "close_price", "now"],
                "volume": ["成交量", "vol", "volume_amount"],
            }

            for required_col in missing_columns:
                found = False
                for alt_col in column_mapping.get(required_col, []):
                    if alt_col in df.columns:
                        df = df.rename(columns={alt_col: required_col})
                        found = True
                        break
                if not found:
                    raise ValueError(f"缺少必要的列: {required_col}")

        # 数据类型转换和验证
        df["datetime"] = pd.to_datetime(df["datetime"])
        numeric_columns = ["open", "high", "low", "close", "volume"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 删除无效数据行
        df = df.dropna(subset=["datetime", "open", "high", "low", "close"])

        # 按日期排序
        df = df.sort_values("datetime").reset_index(drop=True)

        return df

def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化DataFrame格式"""
        if df is None or df.empty:
            return df

        # 使用列映射器进行标准化
        df = self.column_mapper.standardize_columns(df)
        return df

def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码格式"""
        if not symbol:
            return symbol

        # 移除后缀
        if symbol.endswith((".SS", ".SZ", ".SH")):
            symbol = symbol[:-3]
        elif symbol.endswith((".ss", ".sz", ".sh")):
            symbol = symbol[:-3]

        # 确保是6位数
        return symbol.zfill(6)

def _normalize_date(self, date_str: str) -> str:
        """标准化日期格式"""
        return normalize_date(date_str)

def _build_success_response(self, data: Any, operation: str) -> Dict:
        """构建成功响应"""
        return {
            "success": True,
            "data": data,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "source": "tdx",
        }

def _build_error_response(self, error: Exception, operation: str) -> Dict:
        """构建错误响应"""
        return {
            "success": False,
            "error": str(error),
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "source": "tdx",
        }

def disconnect(self) -> None:
        """断开TDX连接"""
        if self._connection and hasattr(self._connection, "disconnect"):
            try:
                self._connection.disconnect()
                self._connection = None
                self.logger.info("TDX连接已断开")
            except Exception as e:
                self.logger.warning("断开TDX连接失败: %s", e)

def __del__(self):
        """析构函数，确保连接被正确关闭"""
        self.disconnect()
