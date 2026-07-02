"""ExtraSource adapter registry and contract.

Public entry points:

* :class:`ExtraSourceAdapter` — Protocol to implement for each
  consumer-side auxiliary data source.
* :func:`register_extra_source` — registration function called from
  FastAPI lifespan startup.
* :class:`ExtraSourceRouter` — category-driven dispatch to registered
  adapters; sibling of (not embedded in) :class:`HybridDataSource`.
* :data:`OPENSTOCK_STATIC_CATEGORIES` — frozen 70-category snapshot
  sourced from OpenStock ``DATA_CAPABILITY_SCOPE.md``.

See ``openspec/changes/add-extra-source-adapter-contract/`` for the
authoritative contract.
"""

from .contract import (
    ExtraSourceAdapter,
    ExtraSourceCategoryConflictError,
    ExtraSourceMeta,
    ExtraSourceNameConflictError,
    ExtraSourceResult,
)
from .registry import (
    OPENSTOCK_STATIC_CATEGORIES,
    clear_registered,
    dump_registered_snapshot,
    find_by_category,
    get_registered,
    register_extra_source,
)
from .router import (
    ExtraSourceFetchError,
    ExtraSourceRouter,
    UnsupportedCategoryError,
    default_router,
)

__all__ = [
    "ExtraSourceAdapter",
    "ExtraSourceCategoryConflictError",
    "ExtraSourceFetchError",
    "ExtraSourceMeta",
    "ExtraSourceNameConflictError",
    "ExtraSourceResult",
    "ExtraSourceRouter",
    "OPENSTOCK_STATIC_CATEGORIES",
    "UnsupportedCategoryError",
    "clear_registered",
    "default_router",
    "dump_registered_snapshot",
    "find_by_category",
    "get_registered",
    "register_extra_source",
]
