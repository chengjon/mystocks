"""MyStocks Phase 1-5 API - Compatibility Shim

Split into domain-specific modules under api/v1/:
  v1/system/   | v1/strategy/ | v1/trading/
  v1/admin/    | v1/analysis/

Aggregated router: app.api.v1.router.api_v1_router
Remove this shim after deprecation period (4-8 weeks).
"""

import warnings

from app.api.v1.router import api_v1_router as router


warnings.warn(
    "app.api.mystocks_complete is deprecated. Use app.api.v1.router.api_v1_router instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["router"]
