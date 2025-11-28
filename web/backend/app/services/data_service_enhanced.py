"""
Enhanced Data Service with Comprehensive Error Handling and Monitoring
增强数据服务 - 集成综合错误处理和监控

创建日期: 2025-11-26
版本: 1.0.0
"""

import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Add project root to path to import unified_manager
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.core.data_classification import DataClassification
from src.core.unified_manager import MyStocksUnifiedManager

# Import enhanced error handling and monitoring
try:
    from src.core.error_handling import (
        CircuitBreaker,
        DatabaseConnectionError,
        DatabaseQueryError,
        ErrorCategory,
        ErrorSeverity,
        NonRetryableError,
        RetryableError,
        handle_errors,
        safe_execute,
        validate_dataframe,
    )
    from src.core.monitoring import get_alert_manager, get_api_monitor, get_metrics_collector
    ENHANCED_ERROR_HANDLING = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"Enhanced error handling not available: {e}")
    ENHANCED_ERROR_HANDLING = False

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
    import os
    import sys

    parent_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))
    )
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from src.adapters.akshare_adapter import AkshareDataSource

    AKSHARE_AVAILABLE = True
    logger.info("Akshare adapter imported successfully")
except ImportError as e:
    AKSHARE_AVAILABLE = False
    logger.warning(f"Akshare adapter not available: {e}")


class EnhancedDataService:
    """
    增强数据服务

    集成综合错误处理、监控、熔断器和恢复机制
    """

    def __init__(self, auto_fetch: bool = True, use_cache: bool = True):
        """初始化增强数据服务"""

        # Initialize monitoring and error handling
        if ENHANCED_ERROR_HANDLING:
            self.api_monitor = get_api_monitor()
            self.metrics_collector = get_metrics_collector()
            self.alert_manager = get_alert_manager()
            self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
        else:
            self.api_monitor = None
            self.metrics_collector = None
            self.alert_manager = None
            self.circuit_breaker = None

        try:
            # Initialize unified manager (with monitoring disabled for web service)
            self.unified_manager = MyStocksUnifiedManager(enable_monitoring=False)
            logger.info("Enhanced DataService initialized with MyStocksUnifiedManager")
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
                logger.info("Cache integration initialized for Enhanced DataService")
            except Exception as e:
                logger.warning(f"Failed to initialize cache integration: {e}")
                self.use_cache = False

    @handle_errors(max_attempts=3, fallback_value=pd.DataFrame())
    def get_daily_ohlcv(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> Tuple[pd.DataFrame, Dict[str, np.ndarray]]:
        """
        获取日线OHLCV数据 (带增强错误处理)

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
        start_time = time.time()

        try:
            # Record API request start
            if self.api_monitor:
                self.api_monitor.record_request("/data/ohlcv", "GET", 200, 0.0)

            # Validate input parameters
            self._validate_date_range(start_date, end_date)
            self._validate_symbol_format(symbol)

            # Check circuit breaker
            if self.circuit_breaker:
                df, ohlcv_data = self.circuit_breaker(self._load_data_with_retry)(symbol, start_date, end_date)
            else:
                df, ohlcv_data = self._load_data_with_retry(symbol, start_date, end_date)

            if df.empty:
                raise ValueError(f"未找到股票 {symbol} 在 {start_date.date()} 到 {end_date.date()} 的数据")

            # Validate result DataFrame
            if ENHANCED_ERROR_HANDLING:
                validate_dataframe(
                    df,
                    required_columns=["trade_date", "open", "high", "low", "close", "volume"],
                    min_rows=1
                )

            # Convert to TA-Lib format
            ohlcv_data = self._dataframe_to_ohlcv_arrays(df)

            # Record successful request
            response_time = time.time() - start_time
            if self.api_monitor:
                self.api_monitor.record_request("/data/ohlcv", "GET", 200, response_time)
            if self.metrics_collector:
                self.metrics_collector.record_timer("data_ohlcv_response_time", response_time)
                self.metrics_collector.increment("data_ohlcv_requests_total")
                self.metrics_collector.set_gauge("data_ohlcv_success_rate", 100.0)

            logger.info(
                f"Loaded {len(df)} records for {symbol} "
                f"from {start_date.date()} to {end_date.date()} in {response_time:.2f}s"
            )

            return df, ohlcv_data

        except Exception as e:
            # Record failed request
            response_time = time.time() - start_time
            if self.api_monitor:
                status_code = 500 if isinstance(e, (ValueError, ValidationError)) else 503
                self.api_monitor.record_request("/data/ohlcv", "GET", status_code, response_time)
            if self.metrics_collector:
                self.metrics_collector.record_timer("data_ohlcv_response_time", response_time)
                self.metrics_collector.increment("data_ohlcv_requests_total")
                self.metrics_collector.increment("data_ohlcv_errors_total")
                self.metrics_collector.set_gauge("data_ohlcv_success_rate", 0.0)

            logger.error(f"Failed to load daily OHLCV data: {e}")
            raise

    def _load_data_with_retry(self, symbol: str, start_date: datetime, end_date: datetime) -> Tuple[pd.DataFrame, Dict[str, np.ndarray]]:
        """带重试机制的数据加载"""

        @handle_errors(max_attempts=3, delay_strategy=lambda x: 1.0 * (2 ** x))
        def _load_from_sources():
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

            return df

        df = _load_from_sources()

        if df.empty:
            raise ValueError(f"未找到股票 {symbol} 在 {start_date.date()} 到 {end_date.date()} 的数据")

        # Convert to TA-Lib format
        ohlcv_data = self._dataframe_to_ohlcv_arrays(df)
        return df, ohlcv_data

    def _validate_date_range(self, start_date: datetime, end_date: datetime) -> None:
        """验证日期范围"""
        if start_date >= end_date:
            raise ValueError(f"开始日期 ({start_date.date()}) 必须早于结束日期 ({end_date.date()})")

        if end_date > datetime.now():
            raise ValueError(f"结束日期 ({end_date.date()}) 不能是未来日期")

    def _validate_symbol_format(self, symbol: str) -> None:
        """验证股票代码格式"""
        import re

        # Pattern: 6位数字.SH或SZ
        pattern = r"^\d{6}\.(SH|SZ)$"

        if not re.match(pattern, symbol):
            raise ValueError(f"无效的股票代码格式: {symbol} (应为6位数字.SH或SZ)")

    def get_service_health(self) -> Dict[str, any]:
        """获取服务健康状态"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "service": "EnhancedDataService",
            "status": "healthy",
            "components": {}
        }

        # Check unified manager
        health_status["components"]["unified_manager"] = {
            "status": "available" if self.unified_manager else "unavailable",
            "type": "database"
        }

        # Check cache
        health_status["components"]["cache"] = {
            "status": "available" if self.cache else "unavailable",
            "type": "cache"
        }

        # Check akshare adapter
        health_status["components"]["akshare_adapter"] = {
            "status": "available" if self.akshare_adapter else "unavailable",
            "type": "data_source"
        }

        # Check error handling
        health_status["components"]["error_handling"] = {
            "status": "available" if ENHANCED_ERROR_HANDLING else "unavailable",
            "type": "monitoring"
        }

        # Check monitoring
        health_status["components"]["monitoring"] = {
            "status": "available" if self.api_monitor else "unavailable",
            "type": "monitoring"
        }

        # Get circuit breaker status
        if self.circuit_breaker:
            health_status["components"]["circuit_breaker"] = {
                "status": "closed" if self.circuit_breaker.state == "CLOSED" else "open",
                "type": "circuit_breaker",
                "failure_count": getattr(self.circuit_breaker, 'failure_count', 0)
            }

        # Check overall health
        component_status = [comp["status"] for comp in health_status["components"].values()]
        if "unavailable" in component_status:
            health_status["status"] = "degraded"
        if len(health_status["components"]) == 0:
            health_status["status"] = "unhealthy"

        return health_status

    def get_performance_metrics(self) -> Dict[str, any]:
        """获取性能指标"""
        if not self.metrics_collector:
            return {"error": "Metrics collection not available"}

        metrics_summary = self.metrics_collector.get_metrics_summary()

        # Add service-specific metrics
        performance_metrics = {
            "timestamp": datetime.now().isoformat(),
            "service": "EnhancedDataService",
            "metrics": metrics_summary
        }

        return performance_metrics

    def _load_from_unified_manager(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """从UnifiedManager加载数据 (带错误处理)"""
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
            raise DatabaseQueryError(f"数据库查询失败: {str(e)}")

    def _fetch_and_save_from_akshare(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """从Akshare获取数据并保存到数据库 (带错误处理)"""
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

                # Record save operation
                if self.metrics_collector:
                    self.metrics_collector.increment("data_akshare_saves_total")
                    self.metrics_collector.increment("data_records_saved", len(df_save))

            # Return with proper column name for trade_date
            return df_save

        except Exception as e:
            logger.error(f"Failed to fetch and save from Akshare: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment("data_akshare_errors_total")
            return pd.DataFrame()

    def _generate_mock_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        base_price: float = 100.0,
    ) -> pd.DataFrame:
        """生成模拟数据 (用于开发测试)"""
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
        """将DataFrame转换为TA-Lib所需的NumPy数组格式"""
        return {
            "open": df["open"].to_numpy(dtype=np.float64),
            "high": df["high"].to_numpy(dtype=np.float64),
            "low": df["low"].to_numpy(dtype=np.float64),
            "close": df["close"].to_numpy(dtype=np.float64),
            "volume": df["volume"].to_numpy(dtype=np.float64),
        }

    def get_symbol_name(self, symbol: str) -> str:
        """获取股票名称"""
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
        """验证股票代码格式"""
        try:
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
        except Exception:
            return False

    def get_available_date_range(
        self, symbol: str
    ) -> Optional[Tuple[datetime, datetime]]:
        """获取股票可用的数据日期范围"""
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

            min_date = pd.to_datetime(df["trade_date"]).min()
            max_date = pd.to_datetime(df["trade_date"]).max()

            return (min_date.to_pydatetime(), max_date.to_pydatetime())

        except Exception as e:
            logger.warning(f"Failed to get available date range: {e}")
            return None


# Enhanced singleton
_enhanced_data_service = None


def get_enhanced_data_service() -> EnhancedDataService:
    """获取增强数据服务单例"""
    global _enhanced_data_service
    if _enhanced_data_service is None:
        _enhanced_data_service = EnhancedDataService()
    return _enhanced_data_service


if __name__ == "__main__":
    print("Testing Enhanced Data Service...")

    # Test enhanced data service
    service = get_enhanced_data_service()

    # Test health check
    health = service.get_service_health()
    print(f"Service Health: {health}")

    # Test performance metrics
    metrics = service.get_performance_metrics()
    print(f"Performance Metrics: {metrics}")

    # Test data loading with error handling
    try:
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # Test with valid symbol
        df, ohlcv = service.get_daily_ohlcv("600000.SH", start_date, end_date)
        print(f"Successfully loaded {len(df)} records for 600000.SH")

        # Test with invalid symbol (should use fallback)
        df, ohlcv = service.get_daily_ohlcv("INVALID.XX", start_date, end_date)
        print(f"Fallback test: loaded {len(df)} records")

    except Exception as e:
        print(f"Expected error for invalid symbol: {e}")

    print("\nEnhanced Data Service basic functionality implemented")
    print("Main features:")
    print("  - Comprehensive error handling and recovery")
    print("  - Circuit breaker pattern")
    print("  - Performance monitoring and metrics")
    print("  - Health check endpoints")
    print("  - Retry mechanisms with exponential backoff")
    print("  - Input validation and sanitization")
    print("  - Graceful degradation and fallbacks")
    print("  - Real-time monitoring integration")
