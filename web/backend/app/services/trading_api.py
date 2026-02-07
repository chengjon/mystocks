"""Service wrapper for trading data API classes."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_trading_api_module():
    module_path = Path(__file__).resolve().parents[1] / "api" / "data" / "trading_api.py"
    if not module_path.exists():
        return None
    spec = spec_from_file_location("app.api.data.trading_api", module_path)
    if spec is None or spec.loader is None:
        return None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_trading_api_module()


if _module:
    TradingDataService = getattr(_module, "TradingDataService", None)
    OrderStatus = getattr(_module, "OrderStatus", None)
    OrderType = getattr(_module, "OrderType", None)
    OrderSide = getattr(_module, "OrderSide", None)
    Order = getattr(_module, "Order", None)
    Position = getattr(_module, "Position", None)
    Trade = getattr(_module, "Trade", None)
else:

    class TradingDataService:  # type: ignore[no-redef]
        """Fallback TradingDataService when api/data module is unavailable."""

        def __init__(self, *args, **kwargs):
            pass

    OrderStatus = None
    OrderType = None
    OrderSide = None
    Order = None
    Position = None
    Trade = None
