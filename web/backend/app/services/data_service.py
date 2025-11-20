"""
Data Service for Technical Analysis
股票数据服务 - 为技术指标计算提供OHLCV数据

Integrates with MyStocksUnifiedManager to load historical price data
Includes automatic data fetching via Akshare adapter when data is missing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import logging
import sys
import os

# Add project root to path to import unified_manager
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.core.data_classification import DataClassification
from src.unified_manager import MyStocksUnifiedManager

logger = logging.getLogger(__name__)

# Import cache integration
try:
    from app.core.cache_integration import get_cache_integration

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("Cache integration not available")

# Import Akshare adapter for automatic data fetching
AKSHARE_AVAILABLE = False
AkshareDataSource = None

try:
    # Try to import from parent directory
    import sys
    import os

    parent_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from src.adapters.akshare_adapter import AkshareDataSource

    AKSHARE_AVAILABLE = True
    logger.info("Akshare adapter imported successfully")
except ImportError as e:
    AKSHARE_AVAILABLE = False
    logger.warning(f"Akshare adapter not available: {e}")


class StockDataNotFoundError(Exception):
    """股票数据未找到错误"""

    pass


class InvalidDateRangeError(Exception):
    """无效日期范围错误"""

    pass


class DataService:
    """
    数据服务

    提供股票OHLCV数据加载功能,集成MyStocksUnifiedManager和缓存管理
    """

    def __init__(self, auto_fetch: bool = True, use_cache: bool = True):
        """初始化数据服务

        Args:
            auto_fetch: 当数据库无数据时,是否自动从Akshare获取 (默认True)
            use_cache: 是否启用缓存 (默认True)
        """
        try:
            # Initialize unified manager (with monitoring disabled for web service)
            self.unified_manager = MyStocksUnifiedManager(enable_monitoring=False)
            logger.info("DataService initialized with MyStocksUnifiedManager")
        except Exception as e:
            logger.warning(f"Failed to initialize MyStocksUnifiedManager: {e}")
            self.unified_manager = None

        # Initialize Akshare adapter if auto_fetch enabled
        self.auto_fetch = auto_fetch and AKSHARE_AVAILABLE
        self.akshare_adapter = None

        if self.auto_fetch:
            try:
                self.akshare_adapter = AkshareDataSource()
                logger.info("Akshare adapter initialized for automatic data fetching")
            except Exception as e:
                logger.warning(f"Failed to initialize Akshare adapter: {e}")
                self.auto_fetch = False

        # Initialize cache integration
        self.cache = None
        self.use_cache = use_cache and CACHE_AVAILABLE

        if self.use_cache:
            try:
                self.cache = get_cache_integration()
                logger.info("Cache integration initialized for DataService")
            except Exception as e:
                logger.warning(f"Failed to initialize cache integration: {e}")
                self.use_cache = False

    def get_daily_ohlcv(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> Tuple[pd.DataFrame, Dict[str, np.ndarray]]:
        """
        获取日线OHLCV数据

        Args:
            symbol: 股票代码 (如 '600519.SH')
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Tuple[pd.DataFrame, Dict[str, np.ndarray]]:
                - 原始DataFrame (包含日期列)
                - OHLCV数组字典 (用于TA-Lib计算)

        Raises:
            InvalidDateRangeError: 日期范围无效
            StockDataNotFoundError: 未找到数据
        """
        # Validate date range
        if start_date >= end_date:
            raise InvalidDateRangeError(
                f"开始日期 ({start_date.date()}) 必须早于结束日期 ({end_date.date()})"
            )

        if end_date > datetime.now():
            raise InvalidDateRangeError(f"结束日期 ({end_date.date()}) 不能是未来日期")

        try:
            # Load data from PostgreSQL via UnifiedManager
            if self.unified_manager:
                df = self._load_from_unified_manager(symbol, start_date, end_date)
            else:
                # Fallback to mock data if UnifiedManager not available
                logger.warning("UnifiedManager not available, using mock data")
                df = self._generate_mock_data(symbol, start_date, end_date)

            # If data not found and auto_fetch enabled, fetch from Akshare
            if df.empty and self.auto_fetch:
                logger.info(
                    f"Data not found in database, fetching from Akshare for {symbol}"
                )
                df = self._fetch_and_save_from_akshare(symbol, start_date, end_date)

            if df.empty:
                raise StockDataNotFoundError(
                    f"未找到股票 {symbol} 在 {start_date.date()} 到 {end_date.date()} 的数据"
                )

            # Convert to TA-Lib format
            ohlcv_data = self._dataframe_to_ohlcv_arrays(df)

            logger.info(
                f"Loaded {len(df)} records for {symbol} "
                f"from {start_date.date()} to {end_date.date()}"
            )

            return df, ohlcv_data

        except (InvalidDateRangeError, StockDataNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to load daily OHLCV data: {e}")
            raise RuntimeError(f"加载股票数据失败: {str(e)}")

    def _fetch_and_save_from_akshare(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """
        从Akshare获取数据并保存到数据库

        Args:
            symbol: 股票代码 (如 '600519.SH')
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 下载并保存的数据
        """
        try:
            if not self.akshare_adapter:
                logger.warning("Akshare adapter not initialized")
                return pd.DataFrame()

            # Call Akshare adapter to fetch data
            logger.info(
                f"Fetching data from Akshare: {symbol} from {start_date.date()} to {end_date.date()}"
            )

            df = self.akshare_adapter.get_stock_daily(
                symbol=symbol,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )

            if df.empty:
                logger.warning(f"Akshare returned empty data for {symbol}")
                return pd.DataFrame()

            # Normalize column names - Akshare adapter already returns English column names
            # Expected columns from Akshare: date, open, close, high, low, volume, amount
            # Map to database schema
            df_save = pd.DataFrame(
                {
                    "symbol": symbol,
                    "trade_date": (
                        pd.to_datetime(df["date"])
                        if "date" in df.columns
                        else pd.to_datetime(df.index)
                    ),
                    "open": df["open"],
                    "high": df["high"],
                    "low": df["low"],
                    "close": df["close"],
                    "volume": df["volume"],
                    "amount": df.get(
                        "amount", df["volume"] * df["close"]
                    ),  # Calculate if missing
                }
            )

            # Save to database via UnifiedManager
            if self.unified_manager:
                logger.info(f"Saving {len(df_save)} records to database for {symbol}")

                result = self.unified_manager.save_data_by_classification(
                    classification=DataClassification.DAILY_KLINE,
                    table_name="daily_kline",
                    data=df_save,
                )

                logger.info(f"Data saved to database: {result}")

            # Return with proper column name for trade_date
            return df_save

        except Exception as e:
            logger.error(f"Failed to fetch and save from Akshare: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def _load_from_unified_manager(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """
        从UnifiedManager加载数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 日线数据
        """
        try:
            # Use load_data_by_classification to query PostgreSQL daily_kline table
            df = self.unified_manager.load_data_by_classification(
                classification=DataClassification.DAILY_KLINE,
                table_name="daily_kline",
                filters={"symbol": symbol},
                time_column="trade_date",
                start_time=start_date,
                end_time=end_date,
            )

            # Validate required columns
            required_columns = ["trade_date", "open", "high", "low", "close", "volume"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                logger.warning(f"Missing required columns: {missing_columns}")
                return pd.DataFrame()

            # Ensure trade_date is datetime type
            df["trade_date"] = pd.to_datetime(df["trade_date"])

            # Sort by date
            df = df.sort_values("trade_date")

            return df

        except Exception as e:
            logger.error(f"Failed to load from UnifiedManager: {e}")
            return pd.DataFrame()

    def _generate_mock_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        base_price: float = 100.0,
    ) -> pd.DataFrame:
        """
        生成模拟数据 (用于开发测试)

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            base_price: 基准价格

        Returns:
            pd.DataFrame: 模拟的日线数据
        """
        logger.warning(f"Generating mock data for {symbol}")

        # Generate date range (business days only)
        dates = pd.date_range(start=start_date, end=end_date, freq="B")

        if len(dates) == 0:
            return pd.DataFrame()

        # Generate random walk price data
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol

        # Generate returns
        returns = np.random.normal(
            0.001, 0.02, len(dates)
        )  # 0.1% daily return, 2% volatility
        prices = base_price * np.exp(np.cumsum(returns))

        # Generate OHLC from close prices
        volatility = 0.01  # 1% intraday volatility

        opens = prices * (1 + np.random.normal(0, volatility, len(dates)))
        highs = np.maximum(opens, prices) * (
            1 + np.abs(np.random.normal(0, volatility, len(dates)))
        )
        lows = np.minimum(opens, prices) * (
            1 - np.abs(np.random.normal(0, volatility, len(dates)))
        )
        closes = prices

        # Generate volume
        base_volume = 10000000
        volumes = np.random.lognormal(np.log(base_volume), 0.5, len(dates)).astype(int)

        # Create DataFrame
        df = pd.DataFrame(
            {
                "symbol": symbol,
                "trade_date": dates,
                "open": opens,
                "high": highs,
                "low": lows,
                "close": closes,
                "volume": volumes,
                "amount": closes * volumes,
                "adj_factor": 1.0,
            }
        )

        return df

    def _dataframe_to_ohlcv_arrays(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        将DataFrame转换为TA-Lib所需的NumPy数组格式

        Args:
            df: 包含OHLCV数据的DataFrame

        Returns:
            Dict[str, np.ndarray]: OHLCV数组字典
        """
        return {
            "open": df["open"].to_numpy(dtype=np.float64),
            "high": df["high"].to_numpy(dtype=np.float64),
            "low": df["low"].to_numpy(dtype=np.float64),
            "close": df["close"].to_numpy(dtype=np.float64),
            "volume": df["volume"].to_numpy(dtype=np.float64),
        }

    def get_symbol_name(self, symbol: str) -> str:
        """
        获取股票名称

        Args:
            symbol: 股票代码

        Returns:
            str: 股票名称
        """
        try:
            if self.unified_manager:
                # Query symbols table from MySQL
                df = self.unified_manager.load_data_by_classification(
                    classification=DataClassification.SYMBOLS_INFO,
                    table_name="symbols",
                    filters={"symbol": symbol},
                    limit=1,
                )

                if not df.empty and "name" in df.columns:
                    return df.iloc[0]["name"]

        except Exception as e:
            logger.warning(f"Failed to get symbol name: {e}")

        # Fallback to symbol itself
        return symbol

    def validate_symbol_format(self, symbol: str) -> bool:
        """
        验证股票代码格式

        Args:
            symbol: 股票代码

        Returns:
            bool: 是否有效

        Examples:
            - 600519.SH (上海主板)
            - 000001.SZ (深圳主板)
            - 300XXX.SZ (创业板)
            - 688XXX.SH (科创板)
        """
        import re

        # Pattern: 6位数字.SH或SZ
        pattern = r"^\d{6}\.(SH|SZ)$"

        if not re.match(pattern, symbol):
            return False

        code, exchange = symbol.split(".")

        # Validate exchange-specific code ranges
        if exchange == "SH":
            # Shanghai: 600/601/603/688/689
            return code.startswith(("600", "601", "603", "688", "689"))
        elif exchange == "SZ":
            # Shenzhen: 000/001/002/003/300
            return code.startswith(("000", "001", "002", "003", "300"))

        return False

    def get_available_date_range(
        self, symbol: str
    ) -> Optional[Tuple[datetime, datetime]]:
        """
        获取股票可用的数据日期范围

        Args:
            symbol: 股票代码

        Returns:
            Optional[Tuple[datetime, datetime]]: (最早日期, 最晚日期) 或 None
        """
        try:
            if not self.unified_manager:
                return None

            # Query date range from PostgreSQL
            df = self.unified_manager.load_data_by_classification(
                classification=DataClassification.DAILY_KLINE,
                table_name="daily_kline",
                filters={"symbol": symbol},
                columns=["trade_date"],
                limit=None,
            )

            if df.empty:
                return None

            min_date = pd.to_datetime(df["trade_date"].min())
            max_date = pd.to_datetime(df["trade_date"].max())

            return (min_date.to_pydatetime(), max_date.to_pydatetime())

        except Exception as e:
            logger.warning(f"Failed to get available date range: {e}")
            return None


# Global singleton
_data_service = None


def get_data_service() -> DataService:
    """获取数据服务单例"""
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service
