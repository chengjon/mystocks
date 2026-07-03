"""ExtraSource registry and OpenStock static category inventory.

Layer 1 of the three-layer contract. Registration happens at FastAPI
lifespan startup and performs a synchronous, network-free check that
no adapter declares a category owned by OpenStock's static inventory.

``OPENSTOCK_STATIC_CATEGORIES`` is loaded at startup from the
``deps/openstock`` git submodule's
``docs/DATA_CAPABILITY_SCOPE.md`` (single source of truth). The
frozenset starts empty at import time and is populated by
:func:`initialize_openstock_static_categories`, which the FastAPI
lifespan invokes before any ``register_extra_source`` call.

Future: once OpenStock ships a ``/sources/categories`` static endpoint,
the submodule parse can be swapped for an HTTP fetch without touching
callers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from ._openstock_categories import (
    OpenStockDataScopeFileMissingError,
    OpenStockDataScopeParseError,
    load_openstock_categories_from_submodule,
)
from .contract import (
    ExtraSourceAdapter,
    ExtraSourceCategoryConflictError,
    ExtraSourceMeta,
    ExtraSourceNameConflictError,
    ExtraSourceResult,
)

# OpenStock static category inventory. Populated by
# :func:`initialize_openstock_static_categories` at lifespan startup.
# Stored inside a one-element dict so that ``from registry import
# OPENSTOCK_STATIC_CATEGORIES`` exposes a stable reference whose
# underlying frozenset can be swapped by reassigning ``_state["set"]``
# — reassigning a bare module-level ``frozenset`` global would leave
# earlier importers pinned to the empty initial frozenset.
_state: dict[str, frozenset[str]] = {"set": frozenset()}


def initialize_openstock_static_categories(repo_root: Path | None = None) -> frozenset[str]:
    """Populate the OpenStock static category inventory from the submodule.

    Idempotent: safe to call multiple times across lifespan reloads.
    The lifespan MUST call this before any ``register_extra_source``
    invocation so the Layer 1 overlap check sees the canonical inventory.

    Args:
        repo_root: Optional explicit repository root. When ``None``,
            the loader auto-discovers via ``deps/openstock`` location.

    Returns:
        The loaded frozenset (same reference stored under
        ``_state["set"]``).

    Raises:
        OpenStockDataScopeFileMissingError: submodule not checked out.
        OpenStockDataScopeParseError: document format drifted.
    """
    loaded = load_openstock_categories_from_submodule(repo_root)
    _state["set"] = loaded
    return loaded


def get_openstock_static_categories() -> frozenset[str]:
    """Read accessor for the loaded static category inventory.

    Always returns the current contents of ``_state["set"]`` — use
    this in code paths that need the post-initialize view (router,
    tests, snapshots) without tripping the ``from … import`` binding
    pitfall.
    """
    return _state["set"]


_registered: dict[str, ExtraSourceAdapter] = {}


def register_extra_source(adapter: ExtraSourceAdapter) -> None:
    """Register an ExtraSource adapter.

    Layer 1 static checks (network-free, runs at startup):

    1. ``meta.category`` MUST NOT be in :data:`OPENSTOCK_STATIC_CATEGORIES`.
    2. ``meta.name`` MUST be globally unique.

    ``expires_on`` is NOT validated here; CI handles expiration
    enforcement for TEMP_OVERRIDE adapters.
    """
    meta = adapter.get_meta()
    if meta.category in _state["set"]:
        raise ExtraSourceCategoryConflictError(
            f"ExtraSource '{meta.name}' declares category '{meta.category}' "
            f"which overlaps with OpenStock static inventory"
        )
    if meta.name in _registered:
        raise ExtraSourceNameConflictError(
            f"ExtraSource name '{meta.name}' is already registered " f"by another adapter"
        )
    _registered[meta.name] = adapter


def clear_registered() -> None:
    """Clear the registry. Intended for test isolation only."""
    _registered.clear()


def get_registered() -> dict[str, ExtraSourceAdapter]:
    """Return a shallow copy of the registry. Read-only access for
    routing layer and CI snapshot dump."""
    return dict(_registered)


def find_by_category(category: str) -> ExtraSourceAdapter | None:
    """Return the adapter registered for ``category``, or ``None`` if
    no adapter matches. Routing layer uses this to decide whether to
    dispatch to ExtraSource or fall through to Mock/UNSUPPORTED_CATEGORY.
    """
    for adapter in _registered.values():
        if adapter.get_meta().category == category:
            return adapter
    return None


def dump_registered_snapshot(path: str | Path) -> None:
    """Dump a JSON snapshot of the registry for CI TEMP_OVERRIDE
    expiration enforcement.

    Output schema::

        {
          "adapters": [
            {"name": "...", "category": "...", "expires_on": "YYYY-MM-DD" | null},
            ...
          ]
        }

    Called by FastAPI lifespan AFTER all ``register_extra_source``
    calls have completed.
    """
    payload: dict[str, Any] = {
        "adapters": [
            {
                "name": meta.name,
                "category": meta.category,
                "expires_on": meta.expires_on,
            }
            for meta in (adapter.get_meta() for adapter in _registered.values())
        ]
    }
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True))


__all__ = [
    "initialize_openstock_static_categories",
    "get_openstock_static_categories",
    "OpenStockDataScopeFileMissingError",
    "OpenStockDataScopeParseError",
    "ExtraSourceAdapter",
    "ExtraSourceMeta",
    "ExtraSourceResult",
    "ExtraSourceCategoryConflictError",
    "ExtraSourceNameConflictError",
    "register_extra_source",
    "clear_registered",
    "get_registered",
    "find_by_category",
    "dump_registered_snapshot",
    # NOTE: ``OPENSTOCK_STATIC_CATEGORIES`` is intentionally absent — it
    # resolves via PEP 562 ``__getattr__`` to the current contents of
    # ``_state["set"]``. Listing it here would trip ruff F822.
]


# Re-export Protocol/annotations for runtime_checkable consumers without
# creating a circular import.
_ = (Protocol, runtime_checkable)


# PEP 562 module-level __getattr__: make ``from registry import
# OPENSTOCK_STATIC_CATEGORIES`` resolve to the *current* contents of
# ``_state["set"]`` rather than pinning to whatever frozenset reference
# existed at import time. This lets :func:`initialize_openstock_static_categories`
# swap the inventory at lifespan startup without breaking earlier
# importers (router.py, tests, sibling package __init__.py).
def __getattr__(name: str) -> Any:
    if name == "OPENSTOCK_STATIC_CATEGORIES":
        return _state["set"]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
