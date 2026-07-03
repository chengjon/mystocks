"""ExtraSource adapter registry and contract.

Public entry points:

* :class:`ExtraSourceAdapter` — Protocol to implement for each
  consumer-side auxiliary data source.
* :func:`register_extra_source` — registration function called from
  FastAPI lifespan startup.
* :class:`ExtraSourceRouter` — category-driven dispatch to registered
  adapters; sibling of (not embedded in) :class:`HybridDataSource`.
* :data:`OPENSTOCK_STATIC_CATEGORIES` — OpenStock 70-category
  inventory loaded at startup from the ``deps/openstock`` submodule.
* :func:`initialize_openstock_static_categories` — startup-time
  loader (called by FastAPI lifespan before registration).

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
    OpenStockDataScopeFileMissingError,
    OpenStockDataScopeParseError,
    clear_registered,
    dump_registered_snapshot,
    find_by_category,
    get_openstock_static_categories,
    get_registered,
    initialize_openstock_static_categories,
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
    "OpenStockDataScopeFileMissingError",
    "OpenStockDataScopeParseError",
    "UnsupportedCategoryError",
    "clear_registered",
    "default_router",
    "dump_registered_snapshot",
    "find_by_category",
    "get_openstock_static_categories",
    "get_registered",
    "initialize_openstock_static_categories",
    "register_extra_source",
]


# PEP 562: resolve ``OPENSTOCK_STATIC_CATEGORIES`` dynamically so that
# lifespan-time ``initialize_openstock_static_categories()`` is visible
# to callers that did ``from app.services.extra_source import
# OPENSTOCK_STATIC_CATEGORIES`` before initialization ran.
def __getattr__(name: str):
    if name == "OPENSTOCK_STATIC_CATEGORIES":
        from .registry import get_openstock_static_categories

        return get_openstock_static_categories()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
