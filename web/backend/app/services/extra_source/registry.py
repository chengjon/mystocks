"""ExtraSource registry and OpenStock static category inventory.

Layer 1 of the three-layer contract. Registration happens at FastAPI
lifespan startup and performs a synchronous, network-free check that
no adapter declares a category owned by OpenStock's static inventory.

``OPENSTOCK_STATIC_CATEGORIES`` is a frozen snapshot sourced from
``/opt/claude/openstock/docs/DATA_CAPABILITY_SCOPE.md``. Drift detection:

* Current: manual quarterly diff against ``DATA_CAPABILITY_SCOPE.md``
  (owner: B4.014 follow-up).
* Future: once OpenStock ships a ``/sources/categories`` static
  endpoint, replace this frozenset with a startup-time dynamic load.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from .contract import (
    ExtraSourceAdapter,
    ExtraSourceCategoryConflictError,
    ExtraSourceMeta,
    ExtraSourceNameConflictError,
    ExtraSourceResult,
)

OPENSTOCK_STATIC_CATEGORIES: frozenset[str] = frozenset(
    {
        # 70 items, source: DATA_CAPABILITY_SCOPE.md 2026-07-02 snapshot.
        # Re-verify via `grep -oE '`[A-Z][A-Z0-9_]+`' DATA_CAPABILITY_SCOPE.md | sort -u`.
        "ADJUSTED_KLINES",
        "ADJUST_FACTOR",
        "ALL_STOCKS",
        "ANNOUNCEMENTS",
        "BLOCK_TRADE",
        "CALL_AUCTION",
        "CONSECUTIVE_LIMIT_UP",
        "CONSENSUS_FORECAST",
        "CONVERTIBLE_BONDS",
        "CORPORATE_ACTIONS",
        "DIVIDEND_DATA",
        "DRAGON_TIGER",
        "DRAGON_TIGER_STOCK_HISTORY",
        "DRAGON_TIGER_TRADER",
        "ETF_SPOT",
        "F10_DATA",
        "FINANCIAL_DATA",
        "FINANCIAL_STATEMENTS",
        "FORECAST_DATA",
        "FUND_FLOW",
        "FUND_NAV",
        "HISTORICAL_KLINES",
        "HK_KLINES",
        "HK_QUOTES",
        "HOT_RANK",
        "INDEX_CONSTITUENTS",
        "INDEX_KLINES",
        "INDEX_QUOTES",
        "INSTITUTION_HOLDING",
        "KLINES",
        "LIMITS",
        "LIMIT_UP_HISTORY",
        "LIMIT_UP_POOL",
        "LIMIT_UP_REASON",
        "MACRO_DATA",
        "MARKET_DEPTH",
        "MARKET_SENTIMENT",
        "MINUTE_DATA",
        "MOVEMENT_ALERTS",
        "NORTHBOUND_FLOW",
        "NORTHBOUND_HOLDING",
        "REALTIME_QUOTES",
        "REGULATORY_ACTIONS",
        "RESEARCH_REPORTS",
        "RESTRICTED_RELEASE",
        "ROADSHOWS",
        "SECTOR_CONSTITUENTS",
        "SECTOR_FUND_FLOW",
        "SECTOR_KLINES",
        "SECTOR_QUOTES",
        "SENTIMENT_DAILY_EFFECT",
        "SENTIMENT_TREND",
        "SHAREHOLDER_CHANGE",
        "SHAREHOLDER_COUNT",
        "STOCK_BASIC",
        "STOCK_CODES",
        "STOCK_INDUSTRY",
        "STOCK_NEWS",
        "STOCK_PROFILE",
        "STOCK_RATING",
        "TICK_DATA",
        "TOPICS_CONCEPTS",
        "TOPIC_DETAIL",
        "TOPIC_HEAT",
        "TRADE_DATES",
        "UPDOWN_DISTRIBUTION",
        "US_KLINES",
        "US_QUOTES",
        "VALUATION",
        "WORKDAYS",
    }
)


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
    if meta.category in OPENSTOCK_STATIC_CATEGORIES:
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
    "OPENSTOCK_STATIC_CATEGORIES",
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
]


# Re-export Protocol/annotations for runtime_checkable consumers without
# creating a circular import.
_ = (Protocol, runtime_checkable)
