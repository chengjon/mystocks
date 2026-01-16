# Root-level entry point for backward compatibility
# Re-export from src.core.unified_manager

from src.core.unified_manager import MyStocksUnifiedManager

__all__ = [
    "MyStocksUnifiedManager",
]
