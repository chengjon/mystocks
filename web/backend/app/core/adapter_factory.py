"""
Adapter Factory - Unified adapter instantiation and management
Task 1.4 Phase 2: Remove Duplicate Code - Service Consolidation

Consolidates repeated adapter initialization patterns across 6+ adapter files.

BEFORE (in multiple services):
```python
from app.adapters.akshare_extension import get_akshare_extension
from app.adapters.eastmoney_adapter import get_eastmoney_adapter
from app.adapters.tqlex_adapter import get_tqlex_adapter

akshare = get_akshare_extension()
eastmoney = get_eastmoney_adapter()
tqlex = get_tqlex_adapter()
```

AFTER (use factory):
```python
from app.core.adapter_factory import AdapterFactory

# Get or create any adapter
akshare = AdapterFactory.get_adapter("akshare")
eastmoney = AdapterFactory.get_adapter("eastmoney")
```

Estimated Duplication Reduced: 100+ lines
"""

from typing import Dict, Type, TypeVar, Any
import structlog

logger = structlog.get_logger()

T = TypeVar("T")


class AdapterRegistry:
    """
    Central registry for all data source adapters.

    Provides lazy-loading and singleton pattern for all adapters.
    """

    _adapters: Dict[str, Any] = {}
    _adapter_classes: Dict[str, Type] = {}

    @staticmethod
    def register_adapter(name: str, adapter_class: Type, lazy_load: bool = True):
        """
        Register an adapter class in the registry

        Args:
            name: Unique adapter name (e.g., "akshare", "eastmoney")
            adapter_class: Adapter class or factory function
            lazy_load: Whether to instantiate on-demand (True) or at registration (False)
        """
        AdapterRegistry._adapter_classes[name] = adapter_class
        logger.info(f"✅ Registered adapter: {name} (lazy_load={lazy_load})")

        if not lazy_load:
            AdapterRegistry._adapters[name] = AdapterRegistry._instantiate(name)

    @staticmethod
    def get_adapter(name: str, *args, **kwargs) -> Any:
        """
        Get or create singleton instance of an adapter

        Args:
            name: Adapter name
            *args: Arguments to pass to adapter constructor (first call only)
            **kwargs: Keyword arguments to pass to adapter constructor (first call only)

        Returns:
            Adapter instance

        Raises:
            KeyError: If adapter not registered
        """
        if name not in AdapterRegistry._adapter_classes:
            raise KeyError(
                f"Adapter '{name}' not registered. Available: {list(AdapterRegistry._adapter_classes.keys())}"
            )

        if name not in AdapterRegistry._adapters:
            logger.info(f"📦 Instantiating adapter: {name}")
            AdapterRegistry._adapters[name] = AdapterRegistry._instantiate(
                name, *args, **kwargs
            )

        return AdapterRegistry._adapters[name]

    @staticmethod
    def _instantiate(name: str, *args, **kwargs) -> Any:
        """Instantiate an adapter"""
        adapter_class = AdapterRegistry._adapter_classes[name]
        try:
            if (
                callable(adapter_class)
                and hasattr(adapter_class, "__name__")
                and adapter_class.__name__.startswith("get_")
            ):
                # It's a factory function
                return adapter_class(*args, **kwargs)
            else:
                # It's a class
                return adapter_class(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Failed to instantiate adapter '{name}': {str(e)}")
            raise

    @staticmethod
    def reset_adapter(name: str):
        """Reset/reload an adapter instance"""
        if name in AdapterRegistry._adapters:
            logger.info(f"🔄 Resetting adapter: {name}")
            del AdapterRegistry._adapters[name]

    @staticmethod
    def reset_all():
        """Reset all adapter instances"""
        logger.info(f"🔄 Resetting all {len(AdapterRegistry._adapters)} adapters")
        AdapterRegistry._adapters.clear()

    @staticmethod
    def get_registered_adapters() -> Dict[str, Type]:
        """Get all registered adapter classes"""
        return AdapterRegistry._adapter_classes.copy()

    @staticmethod
    def get_loaded_adapters() -> Dict[str, Any]:
        """Get all currently instantiated adapters"""
        return AdapterRegistry._adapters.copy()


class AdapterFactory:
    """
    Generic factory for managing all data source adapters.

    Consolidates repeated adapter initialization patterns.
    Supports lazy-loading and singleton pattern for all adapters.

    Usage:
        ```python
        # Register adapters (usually done at app startup)
        from app.adapters.akshare_extension import get_akshare_extension
        from app.adapters.eastmoney_adapter import get_eastmoney_adapter

        AdapterFactory.register("akshare", get_akshare_extension)
        AdapterFactory.register("eastmoney", get_eastmoney_adapter)

        # Get singleton instances
        akshare = AdapterFactory.get("akshare")
        eastmoney = AdapterFactory.get("eastmoney")

        # Use adapters
        fund_flow = akshare.get_stock_fund_flow("000001")
        ```
    """

    @staticmethod
    def register(name: str, adapter_class_or_factory: Type, lazy_load: bool = True):
        """
        Register an adapter

        Args:
            name: Unique adapter name
            adapter_class_or_factory: Adapter class or factory function
            lazy_load: Instantiate on-demand if True
        """
        AdapterRegistry.register_adapter(name, adapter_class_or_factory, lazy_load)

    @staticmethod
    def get(name: str, *args, **kwargs) -> Any:
        """
        Get or create singleton adapter instance

        Args:
            name: Adapter name
            *args: Constructor arguments (first call only)
            **kwargs: Constructor keyword arguments (first call only)

        Returns:
            Adapter instance
        """
        return AdapterRegistry.get_adapter(name, *args, **kwargs)

    @staticmethod
    def reset(name: str):
        """Reset specific adapter"""
        AdapterRegistry.reset_adapter(name)

    @staticmethod
    def reset_all():
        """Reset all adapters"""
        AdapterRegistry.reset_all()

    @staticmethod
    def registered() -> Dict[str, Type]:
        """Get all registered adapters"""
        return AdapterRegistry.get_registered_adapters()

    @staticmethod
    def loaded() -> Dict[str, Any]:
        """Get all instantiated adapters"""
        return AdapterRegistry.get_loaded_adapters()

    @staticmethod
    def info() -> Dict[str, Any]:
        """Get factory status information"""
        return {
            "registered": len(AdapterRegistry.get_registered_adapters()),
            "loaded": len(AdapterRegistry.get_loaded_adapters()),
            "adapters": list(AdapterRegistry.get_registered_adapters().keys()),
        }


# ==================== INITIALIZATION HELPERS ====================


def init_default_adapters():
    """
    Initialize default adapters at application startup.

    Should be called in main.py or app initialization.
    """
    try:
        from app.adapters.akshare_extension import get_akshare_extension

        AdapterFactory.register("akshare", get_akshare_extension, lazy_load=True)
        logger.info("✅ Registered akshare adapter")
    except ImportError:
        logger.warning("⚠️ akshare adapter not available")

    try:
        from app.adapters.eastmoney_adapter import get_eastmoney_adapter

        AdapterFactory.register("eastmoney", get_eastmoney_adapter, lazy_load=True)
        logger.info("✅ Registered eastmoney adapter")
    except ImportError:
        logger.warning("⚠️ eastmoney adapter not available")

    try:
        from app.adapters.tqlex_adapter import get_tqlex_adapter

        AdapterFactory.register("tqlex", get_tqlex_adapter, lazy_load=True)
        logger.info("✅ Registered tqlex adapter")
    except ImportError:
        logger.warning("⚠️ tqlex adapter not available")

    try:
        from app.adapters.financial_adapter import get_financial_adapter

        AdapterFactory.register("financial", get_financial_adapter, lazy_load=True)
        logger.info("✅ Registered financial adapter")
    except ImportError:
        logger.warning("⚠️ financial adapter not available")


"""
USAGE EXAMPLES:

1. Register adapters at app startup (in main.py):
    ```python
    from app.core.adapter_factory import init_default_adapters

    @app.on_event("startup")
    async def startup_event():
        init_default_adapters()
    ```

2. Use adapters in services:
    ```python
    from app.core.adapter_factory import AdapterFactory

    class MarketDataService:
        def __init__(self, adapter_name: str = "akshare"):
            self.adapter = AdapterFactory.get(adapter_name)

        def fetch_fund_flow(self, symbol: str):
            return self.adapter.get_stock_fund_flow(symbol)
    ```

3. Test with different adapters:
    ```python
    # Use akshare for testing
    service = MarketDataService("akshare")

    # Reset and use eastmoney
    AdapterFactory.reset("akshare")
    service = MarketDataService("eastmoney")
    ```

4. Get factory status:
    ```python
    info = AdapterFactory.info()
    print(f"Loaded adapters: {info}")
    # Output: {"registered": 4, "loaded": 2, "adapters": [...]}
    ```
"""
