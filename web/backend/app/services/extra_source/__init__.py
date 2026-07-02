"""ExtraSource adapter registry and contract.

Public entry points:

* :class:`ExtraSourceAdapter` — Protocol to implement for each
  consumer-side auxiliary data source.
* :func:`register_extra_source` — registration function called from
  FastAPI lifespan startup.
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

__all__ = [
    "ExtraSourceAdapter",
    "ExtraSourceCategoryConflictError",
    "ExtraSourceMeta",
    "ExtraSourceNameConflictError",
    "ExtraSourceResult",
    "OPENSTOCK_STATIC_CATEGORIES",
    "clear_registered",
    "dump_registered_snapshot",
    "find_by_category",
    "get_registered",
    "register_extra_source",
]
