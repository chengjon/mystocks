"""
# 功能：AkShare数据源适配器，提供A股行情和基本面数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import logging
import sys
import os
import importlib.util
from functools import wraps
from types import ModuleType

# 常量定义
MAX_RETRIES = 3
RETRY_DELAY = 1
REQUEST_TIMEOUT = 10

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.error_handler import retry_on_failure  # noqa: E402
from src.interfaces.data_source import IDataSource  # noqa: E402

# 统一日志配置

# 获取或创建logger
logger = logging.getLogger(__name__)

# 确保日志配置已设置
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _load_mixin_methods(cls):
    """动态加载混入方法到类中

    从akshare子模块中加载方法并添加到类中，实现mixin模式。
    """
    mixin_files = [
        "stock_basic",
        "stock_daily",
        "index_daily",
        "realtime_data",
        "financial_data",
        "market_data",
        "industry_data",
        "misc_data",
    ]

    current_dir = os.path.dirname(os.path.abspath(__file__))

    for mixin_file in mixin_files:
        mixin_path = os.path.join(current_dir, f"{mixin_file}.py")
        if os.path.exists(mixin_path):
            try:
                # 动态导入模块
                spec = importlib.util.spec_from_file_location(mixin_file, mixin_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # 将模块中的函数添加到类中
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if callable(attr) and not attr_name.startswith("_"):
                            # 只添加没有冲突的方法
                            if not hasattr(cls, attr_name):
                                setattr(cls, attr_name, attr)
                                logger.debug(f"[Akshare] 加载混入方法: {attr_name} from {mixin_file}")

            except Exception as e:
                logger.warning(f"[Akshare] 加载混入模块 {mixin_file} 失败: {e}")
                continue

    logger.info("[Akshare] 混入方法加载完成")


class AkshareDataSource(IDataSource):
    """Akshare数据源实现

    属性:
        api_timeout (int): API请求超时时间(秒)
        max_retries (int): 最大重试次数
    """


def __init__(self, api_timeout: int = REQUEST_TIMEOUT, max_retries: int = MAX_RETRIES):
    """初始化Akshare数据源

    Args:
        api_timeout: API请求超时时间(秒)
        max_retries: 最大重试次数
    """
    self.api_timeout = api_timeout
    self.max_retries = max_retries
    logger.info("[Akshare] 数据源初始化完成 (超时: %ss, 重试: %s次)", api_timeout, max_retries)


def _retry_api_call(self, func):
    """API调用重试装饰器 - 使用统一错误处理"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 使用统一错误处理的重试机制
        retry_decorator = retry_on_failure(
            max_retries=self.max_retries,
            delay=RETRY_DELAY,
            backoff=1.0,
            exceptions=(Exception,),
            context=f"Akshare API调用: {func.__name__}",
        )
        return retry_decorator(func)(*args, **kwargs)

    return wrapper

    # 实现IDataSource抽象方法 (基础实现)


def get_stock_daily(self, symbol: str, start_date: str, end_date: str):
    """基础实现 - 子类应重写"""
    raise NotImplementedError("get_stock_daily must be implemented by subclass")


def get_index_daily(self, symbol: str, start_date: str, end_date: str):
    """基础实现 - 子类应重写"""
    raise NotImplementedError("get_index_daily must be implemented by subclass")


def get_stock_basic(self, symbol: str):
    """基础实现 - 子类应重写"""
    raise NotImplementedError("get_stock_basic must be implemented by subclass")


def get_index_components(self, symbol: str):
    """基础实现 - 子类应重写"""
    raise NotImplementedError("get_index_components must be implemented by subclass")


def get_real_time_data(self, symbol: str):
    """基础实现 - 子类应重写"""
    raise NotImplementedError("get_real_time_data must be implemented by subclass")


def get_market_calendar(self, start_date: str, end_date: str):
    """基础实现 - 子类应重写"""
    raise NotImplementedError("get_market_calendar must be implemented by subclass")


def get_financial_data(self, symbol: str, period: str = "annual"):
    """基础实现 - 子类应重写"""
    raise NotImplementedError("get_financial_data must be implemented by subclass")


def get_news_data(self, symbol=None, limit: int = 10):
    """基础实现 - 子类应重写"""
    raise NotImplementedError("get_news_data must be implemented by subclass")

    # 股指期货相关方法 - 直接实现在基类中


def get_futures_index_daily(self, symbol: str, start_date: str, end_date: str):
    """获取股指期货日线数据-Akshare实现"""
    try:
        logger.info(
            r"[Akshare] 开始获取股指期货日线数据: symbol=%s, 开始日期=%s, 结束日期=%s", symbol, start_date, end_date
        )

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_futures_data():
            import akshare as ak

            return ak.futures_zh_daily_sina(symbol=symbol)

        # 调用akshare接口获取股指期货日线数据
        df = _get_futures_data()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到股指期货日线数据")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取股指期货日线数据: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "日期": "date",
            "开盘价": "open",
            "最高价": "high",
            "最低价": "low",
            "收盘价": "close",
            "成交量": "volume",
            "持仓量": "open_interest",
            "结算价": "settlement_price",
        }
        df = df.rename(columns=column_mapping)

        # 筛选日期范围
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            mask = (df["date"] >= start_date) & (df["date"] <= end_date)
            df = df[mask]

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取股指期货日线数据失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_futures_index_realtime(self, symbol: str):
    """获取股指期货实时行情-Akshare实现"""
    try:
        logger.info(r"[Akshare] 开始获取股指期货实时行情: symbol=%s", symbol)

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_realtime_data():
            import akshare as ak

            return ak.futures_zh_spot(symbol=symbol, market="FF", adjust="0")

        # 调用akshare接口获取股指期货实时行情
        df = _get_realtime_data()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到股指期货实时行情")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取股指期货实时行情: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "symbol": "symbol",
            "name": "name",
            "trade": "price",
            "settlement": "settlement_price",
            "presettlement": "pre_settlement",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
            "amount": "amount",
            "open_interest": "open_interest",
            "change": "change",
            "change_pct": "change_pct",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取股指期货实时行情失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_futures_index_main_contract(self, symbol: str, start_date: str, end_date: str):
    """获取股指期货主力连续合约-Akshare实现"""
    try:
        logger.info(
            r"[Akshare] 开始获取股指期货主力连续合约: symbol=%s, 开始日期=%s, 结束日期=%s",
            symbol,
            start_date,
            end_date,
        )

        # 使用重试装饰器包装API调用
        @self._retry_api_call
        def _get_main_contract_data():
            import akshare as ak

            return ak.futures_main_sina(symbol=symbol, start_date=start_date, end_date=end_date)

        # 调用akshare接口获取股指期货主力连续合约
        df = _get_main_contract_data()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到股指期货主力连续合约数据")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取股指期货主力连续合约: %s行, 列名=%s", len(df), df.columns.tolist())

        # 重命名列名为英文
        column_mapping = {
            "日期": "date",
            "开盘价": "open",
            "最高价": "high",
            "最低价": "low",
            "收盘价": "close",
            "成交量": "volume",
            "持仓量": "open_interest",
            "动态结算价": "settlement_price",
        }
        df = df.rename(columns=column_mapping)

        # 添加数据获取时间戳
        df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        logger.error("[Akshare] 获取股指期货主力连续合约失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_futures_basis_analysis(self, symbol: str, start_date: str, end_date: str):
    """获取股指期货期现基差分析-Akshare实现"""
    try:
        logger.info(
            r"[Akshare] 开始计算股指期货期现基差: symbol=%s, 开始日期=%s, 结束日期=%s", symbol, start_date, end_date
        )

        # 获取期货数据
        futures_df = self.get_futures_index_daily(symbol, start_date, end_date)
        if futures_df.empty:
            logger.warning("无法获取期货数据，跳过基差分析")
            return pd.DataFrame()

        # 根据期货代码确定对应的现货指数
        spot_index_mapping = {
            "IF": "000300",  # 沪深300
            "IH": "000016",  # 上证50
            "IC": "000905",  # 中证500
            "IM": "000852",  # 中证1000
        }

        futures_type = symbol[:2]  # IF, IH, IC, IM
        spot_symbol = spot_index_mapping.get(futures_type)

        if not spot_symbol:
            logger.warning(f"无法确定期货 {symbol} 对应的现货指数")
            return pd.DataFrame()

        # 获取现货指数数据 (需要实现get_stock_daily方法)
        try:
            spot_df = self.get_stock_daily(spot_symbol, start_date, end_date)
        except NotImplementedError:
            logger.warning("get_stock_daily方法未实现，无法进行基差分析")
            return pd.DataFrame()

        if spot_df.empty:
            logger.warning("无法获取现货指数数据，跳过基差分析")
            return pd.DataFrame()

        # 合并数据并计算基差
        merged_df = pd.merge(
            futures_df[["date", "close"]].rename(columns={"close": "futures_price"}),
            spot_df[["date", "close"]].rename(columns={"close": "spot_index"}),
            on="date",
            how="inner",
        )

        if merged_df.empty:
            logger.warning("无法匹配期货和现货数据")
            return pd.DataFrame()

        # 计算基差
        merged_df["basis"] = merged_df["futures_price"] - merged_df["spot_index"]
        merged_df["basis_rate"] = (merged_df["basis"] / merged_df["spot_index"] * 100).round(4)

        # 选择输出列
        result_df = merged_df[["date", "futures_price", "spot_index", "basis", "basis_rate"]]

        # 添加数据获取时间戳
        result_df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info("[Akshare] 成功计算股指期货期现基差: %s行", len(result_df))
        return result_df

    except Exception as e:
        logger.error("[Akshare] 计算股指期货期现基差失败: %s", e)
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


# 动态加载混入方法
_load_mixin_methods(AkshareDataSource)
