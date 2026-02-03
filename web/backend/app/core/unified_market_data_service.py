"""
Unified Market Data Service - Consolidate market_data_service.py and market_data_service_v2.py
Task 1.4 Phase 2: Remove Duplicate Code - Service Consolidation

Consolidates 300+ LOC of duplicate market data service implementations.

BEFORE (two separate services with identical structure):
```python
# In services/market_data_service.py
class MarketDataService:
    def __init__(self):
        self.akshare = get_akshare_extension()

    def fetch_and_save_fund_flow(self, symbol, timeframe):
        # ... implementation with Akshare adapter

# In services/market_data_service_v2.py
class MarketDataServiceV2:
    def __init__(self):
        self.em_adapter = get_eastmoney_adapter()

    def fetch_and_save_fund_flow(self, symbol, timeframe):
        # ... implementation with EastMoney adapter
```

AFTER (single unified service with pluggable adapters):
```python
from app.core.unified_market_data_service import UnifiedMarketDataService

# Use with default adapter
service = UnifiedMarketDataService(adapter_name="akshare")

# Or switch adapters
service = UnifiedMarketDataService(adapter_name="eastmoney")

result = service.fetch_and_save_fund_flow(symbol, timeframe)
```

Estimated Duplication Reduced: 300+ lines
"""

import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import structlog
from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker

logger = structlog.get_logger()


class UnifiedMarketDataService:
    """
    Unified market data service consolidating MarketDataService and MarketDataServiceV2.

    Supports multiple data source adapters (Akshare, EastMoney, etc.) with a single interface.
    Automatically handles data persistence, validation, and error recovery.

    Usage:
        ```python
        from app.core.unified_market_data_service import UnifiedMarketDataService
        from app.core.adapter_factory import AdapterFactory

        # Initialize with default Akshare adapter
        service = UnifiedMarketDataService()

        # Or specify different adapter
        service = UnifiedMarketDataService(adapter_name="eastmoney")

        # Fetch and save fund flow data
        result = service.fetch_and_save_fund_flow(
            symbol="000001",
            timeframe="1"
        )

        # Fetch all fund flow for all symbols (EastMoney adapter)
        result = service.fetch_and_save_fund_flow(
            symbol=None,  # Fetch all
            timeframe="今日"
        )

        # Query historical data
        flows = service.query_fund_flow(symbol="000001", days=30)
        ```
    """

    def __init__(
        self,
        adapter_name: str = "akshare",
        db_url: Optional[str] = None,
        pool_size: int = 10,
        max_overflow: int = 20,
    ):
        """
        Initialize market data service

        Args:
            adapter_name: Name of adapter to use (default: "akshare")
            db_url: Database connection URL (default: from environment)
            pool_size: Database connection pool size
            max_overflow: Max overflow connections

        Raises:
            KeyError: If adapter not found or not registered
        """
        self.adapter_name = adapter_name

        # Initialize database connection
        if db_url is None:
            db_url = os.getenv("DATABASE_URL") or self._build_db_url()

        self.engine = create_engine(
            db_url,
            pool_pre_ping=True,
            echo=False,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Initialize adapter via factory
        from app.core.adapter_factory import AdapterFactory

        try:
            self.adapter = AdapterFactory.get(adapter_name)
            logger.info("✅ Initialized market data service with adapter: %(adapter_name)s")
        except KeyError as e:
            logger.error("❌ Adapter '%(adapter_name)s' not registered: {str(e)}")
            raise

        # Adapter-specific configuration
        self._setup_adapter_specific()

    def _build_db_url(self) -> str:
        """Build database URL from environment variables"""
        user = os.getenv("POSTGRESQL_USER", "postgres")
        password = os.getenv("POSTGRESQL_PASSWORD")
        host = os.getenv("POSTGRESQL_HOST", "192.168.123.104")
        port = os.getenv("POSTGRESQL_PORT", "5438")
        database = os.getenv("POSTGRESQL_DATABASE", "mystocks")

        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

    def _setup_adapter_specific(self):
        """Setup adapter-specific configuration"""
        if self.adapter_name == "eastmoney":
            # EastMoney specific setup if needed
            logger.info("📦 Using EastMoney adapter for market data")
        elif self.adapter_name == "akshare":
            # Akshare specific setup if needed
            logger.info("📦 Using Akshare adapter for market data")
        else:
            logger.info("📦 Using custom adapter: {self.adapter_name}")

    def switch_adapter(self, adapter_name: str):
        """
        Switch to a different data source adapter

        Args:
            adapter_name: Name of adapter to switch to

        Raises:
            KeyError: If adapter not found
        """
        from app.core.adapter_factory import AdapterFactory

        try:
            self.adapter = AdapterFactory.get(adapter_name)
            self.adapter_name = adapter_name
            logger.info("🔄 Switched to adapter: %(adapter_name)s")
            self._setup_adapter_specific()
        except KeyError as e:
            logger.error("❌ Failed to switch to adapter '%(adapter_name)s': {str(e)}")
            raise

    # ==================== Fund Flow Methods ====================

    def fetch_and_save_fund_flow(
        self, symbol: Optional[str] = None, timeframe: Union[str, int] = "1"
    ) -> Dict[str, Any]:
        """
        Fetch and save fund flow data from adapter

        Supports both single symbol and batch (all symbols) modes.

        Args:
            symbol: Stock symbol (None for batch fetch all symbols)
            timeframe: Time dimension (1/3/5/10 days or "今日"/"3日" for EastMoney)

        Returns:
            Dict with keys:
                - success (bool): Whether fetch succeeded
                - saved_count (int): Number of records saved
                - message (str): Status message
                - error (str, optional): Error details if failed
        """
        try:
            logger.info("📊 Fetching fund flow: symbol=%(symbol)s, timeframe=%(timeframe)s")

            # Normalize timeframe for different adapters
            if self.adapter_name == "eastmoney" and isinstance(timeframe, int):
                timeframe_map = {1: "今日", 3: "3日", 5: "5日", 10: "10日"}
                timeframe = timeframe_map.get(timeframe, "1")

            # Fetch data from adapter
            if symbol is None:
                # Batch fetch (EastMoney specific)
                if self.adapter_name != "eastmoney":
                    return {
                        "success": False,
                        "message": "Batch fetch not supported by this adapter",
                        "error": f"Adapter {self.adapter_name} requires symbol parameter",
                    }
                df = self.adapter.get_stock_fund_flow(None, timeframe)
                return self._save_fund_flow_batch(df, timeframe)
            else:
                # Single symbol fetch
                data = self.adapter.get_stock_fund_flow(symbol, timeframe)
                return self._save_fund_flow_single(symbol, data, timeframe)

        except Exception as e:
            logger.error("❌ Failed to fetch/save fund flow: {str(e)}", exc_info=e)
            return {
                "success": False,
                "message": "Failed to fetch fund flow data",
                "error": str(e),
            }

    def _save_fund_flow_single(self, symbol: str, data: Dict[str, Any], timeframe: Union[str, int]) -> Dict[str, Any]:
        """Save single symbol fund flow data"""
        if not data:
            return {"success": False, "message": "No data returned from adapter"}

        try:
            # Import model (lazy import to avoid circular dependency)
            from app.models.market_data import FundFlow

            db = self.SessionLocal()
            try:
                # Normalize timeframe
                tf_value = str(timeframe).replace("日", "").replace("今", "1")

                fund_flow = FundFlow(
                    symbol=symbol,
                    trade_date=datetime.now().date(),
                    timeframe=tf_value,
                    main_net_inflow=data.get("main_net_inflow", 0),
                    main_net_inflow_rate=data.get("main_net_inflow_rate", 0),
                    super_large_net_inflow=data.get("super_large_net_inflow", 0),
                    large_net_inflow=data.get("large_net_inflow", 0),
                    medium_net_inflow=data.get("medium_net_inflow", 0),
                    small_net_inflow=data.get("small_net_inflow", 0),
                )

                # Upsert strategy
                existing = (
                    db.query(FundFlow)
                    .filter(
                        and_(
                            FundFlow.symbol == symbol,
                            FundFlow.trade_date == fund_flow.trade_date,
                        )
                    )
                    .first()
                )

                if existing:
                    for key, value in fund_flow.__dict__.items():
                        if not key.startswith("_"):
                            setattr(existing, key, value)
                else:
                    db.add(fund_flow)

                db.commit()
                logger.info("✅ Saved fund flow: %(symbol)s")

                return {
                    "success": True,
                    "saved_count": 1,
                    "message": f"Saved fund flow for {symbol}",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            finally:
                db.close()

        except Exception as e:
            logger.error("❌ Failed to save fund flow: {str(e)}")
            return {
                "success": False,
                "message": "Failed to save fund flow",
                "error": str(e),
            }

    def _save_fund_flow_batch(self, df: pd.DataFrame, timeframe: str) -> Dict[str, Any]:
        """Save batch fund flow data (multiple symbols)"""
        if df.empty:
            return {"success": False, "message": "No data to save"}

        try:
            from app.models.market_data import FundFlow

            db = self.SessionLocal()
            try:
                today = datetime.now().date()
                saved_count = 0
                skipped_count = 0

                # Normalize timeframe
                timeframe_map = {"今日": "1", "3日": "3", "5日": "5", "10日": "10"}
                tf_value = timeframe_map.get(timeframe, "1")

                for _, row in df.iterrows():
                    try:
                        fund_flow = FundFlow(
                            symbol=row.get("代码") or row.get("symbol"),
                            trade_date=today,
                            timeframe=tf_value,
                            main_net_inflow=float(row.get(f"{timeframe}主力净流入-净额", 0) or 0),
                            main_net_inflow_rate=float(row.get(f"{timeframe}主力净流入-净占比", 0) or 0),
                            super_large_net_inflow=float(row.get(f"{timeframe}超大单净流入-净额", 0) or 0),
                            large_net_inflow=float(row.get(f"{timeframe}大单净流入-净额", 0) or 0),
                            medium_net_inflow=float(row.get(f"{timeframe}中单净流入-净额", 0) or 0),
                            small_net_inflow=float(row.get(f"{timeframe}小单净流入-净额", 0) or 0),
                        )

                        # Check if exists
                        existing = (
                            db.query(FundFlow)
                            .filter(
                                and_(
                                    FundFlow.symbol == fund_flow.symbol,
                                    FundFlow.trade_date == today,
                                )
                            )
                            .first()
                        )

                        if existing:
                            for key, value in fund_flow.__dict__.items():
                                if not key.startswith("_"):
                                    setattr(existing, key, value)
                        else:
                            db.add(fund_flow)

                        saved_count += 1

                    except Exception as e:
                        logger.warning("⚠️ Skipped row: {str(e)}")
                        skipped_count += 1
                        continue

                db.commit()
                logger.info("✅ Batch saved: %(saved_count)s records, skipped: %(skipped_count)s")

                return {
                    "success": True,
                    "saved_count": saved_count,
                    "skipped_count": skipped_count,
                    "message": f"Saved {saved_count} fund flow records",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            finally:
                db.close()

        except Exception as e:
            logger.error("❌ Batch save failed: {str(e)}")
            return {
                "success": False,
                "message": "Failed to batch save fund flow",
                "error": str(e),
            }

    def query_fund_flow(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: int = 7,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query fund flow data from database

        Args:
            symbol: Filter by symbol (optional)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            days: If start_date not provided, query last N days (default: 7)
            limit: Max results to return (default: 100)

        Returns:
            List of fund flow records as dicts
        """
        try:
            from app.models.market_data import FundFlow

            db = self.SessionLocal()
            try:
                query = db.query(FundFlow)

                # Date range filter
                if start_date is None:
                    start_date = datetime.now().date() - timedelta(days=days)
                if end_date is None:
                    end_date = datetime.now().date()

                query = query.filter(
                    and_(
                        FundFlow.trade_date >= start_date,
                        FundFlow.trade_date <= end_date,
                    )
                )

                # Symbol filter
                if symbol:
                    query = query.filter(FundFlow.symbol == symbol)

                # Order and limit
                results = query.order_by(FundFlow.trade_date.desc()).limit(limit).all()

                return [
                    {
                        "symbol": r.symbol,
                        "trade_date": r.trade_date.isoformat(),
                        "timeframe": r.timeframe,
                        "main_net_inflow": (float(r.main_net_inflow) if r.main_net_inflow else 0),
                        "main_net_inflow_rate": (float(r.main_net_inflow_rate) if r.main_net_inflow_rate else 0),
                    }
                    for r in results
                ]

            finally:
                db.close()

        except Exception as e:
            logger.error("❌ Query failed: {str(e)}")
            return []

    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("✅ Database connection closed")


"""
MIGRATION GUIDE:

From MarketDataService (Akshare):
    ```python
    from app.services.market_data_service import MarketDataService
    service = MarketDataService()
    result = service.fetch_and_save_fund_flow("000001", "1")
    ```

To UnifiedMarketDataService:
    ```python
    from app.core.unified_market_data_service import UnifiedMarketDataService
    service = UnifiedMarketDataService(adapter_name="akshare")
    result = service.fetch_and_save_fund_flow("000001", "1")
    ```

From MarketDataServiceV2 (EastMoney):
    ```python
    from app.services.market_data_service_v2 import MarketDataServiceV2
    service = MarketDataServiceV2()
    result = service.fetch_and_save_fund_flow(None, "今日")  # Batch fetch all
    ```

To UnifiedMarketDataService:
    ```python
    from app.core.unified_market_data_service import UnifiedMarketDataService
    service = UnifiedMarketDataService(adapter_name="eastmoney")
    result = service.fetch_and_save_fund_flow(None, "今日")  # Batch fetch all
    ```

Switching adapters at runtime:
    ```python
    service = UnifiedMarketDataService(adapter_name="akshare")
    result1 = service.fetch_and_save_fund_flow("000001")

    # Switch to EastMoney
    service.switch_adapter("eastmoney")
    result2 = service.fetch_and_save_fund_flow(None, "今日")
    ```
"""
