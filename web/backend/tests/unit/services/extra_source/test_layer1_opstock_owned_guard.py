"""Layer 1 OpenStock-owned category guard — Direction 6 PoC test (test-first).

Purpose
-------
This test pins the contract that the six categories
``multi_source_manager`` historically served via bespoke adapters are
**owned by OpenStock** and MUST be rejected by Layer 1
``register_extra_source`` if anyone attempts to register them as an
ExtraSource.

The six categories come from the C3 Direction 6 PoC scope
(see ``openspec/changes/add-extra-source-adapter-contract/design.md``
§2 Layer 1):

    ANNOUNCEMENTS, DRAGON_TIGER, FUND_FLOW, REALTIME_QUOTES,
    KLINES, BLOCK_TRADE

These are populated in :data:`OPENSTOCK_STATIC_CATEGORIES` sourced
from OpenStock ``DATA_CAPABILITY_SCOPE.md`` (70-item 2026-07-02
snapshot). If a future OpenStock drift check removes any of these
six from the static inventory, the corresponding test will fail
loudly — which is exactly the safety net we want.

Why test-first
--------------
The PoC removes ``fetch_realtime_quote`` /
``fetch_fund_flow`` / ``fetch_dragon_tiger`` /
``fetch_announcements`` from ``multi_source_manager`` and migrates
``announcement_service`` to ``OpenStockClient.fetch("ANNOUNCEMENTS",
...)``. Writing the Layer 1 guard test FIRST proves the safety net
exists before any production code is touched.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.services.extra_source import (
    OPENSTOCK_STATIC_CATEGORIES,
    ExtraSourceCategoryConflictError,
    ExtraSourceMeta,
    ExtraSourceResult,
    clear_registered,
    register_extra_source,
)


# Six categories owned by OpenStock that historically leaked through
# multi_source_manager. They MUST be in the static inventory; if any
# drift-removes them, this test fails and forces a human decision.
OPENSTOCK_OWNED_CATEGORIES: tuple[str, ...] = (
    "ANNOUNCEMENTS",
    "DRAGON_TIGER",
    "FUND_FLOW",
    "REALTIME_QUOTES",
    "KLINES",
    "BLOCK_TRADE",
)


class _OverlappingStubAdapter:
    """Minimal adapter that declares a category owned by OpenStock.
    Used to prove Layer 1 rejects the registration."""

    def __init__(self, name: str, category: str) -> None:
        self._meta = ExtraSourceMeta(name=name, category=category)

    def get_meta(self) -> ExtraSourceMeta:
        return self._meta

    def fetch(self, params: dict[str, Any]) -> ExtraSourceResult:
        return ExtraSourceResult(data={"params": params}, provider_used="stub")


@pytest.fixture(autouse=True)
def _isolate_registry() -> None:
    clear_registered()
    yield
    clear_registered()


class TestOpenStockOwnedCategoriesPresent:
    """If any of the six categories drift-removed from
    :data:`OPENSTOCK_STATIC_CATEGORIES`, the Layer 1 guard stops
    protecting it. This test forces a loud failure."""

    @pytest.mark.parametrize("category", OPENSTOCK_OWNED_CATEGORIES)
    def test_category_is_in_static_inventory(self, category: str) -> None:
        assert category in OPENSTOCK_STATIC_CATEGORIES, (
            f"Drift detected: '{category}' was removed from "
            "OPENSTOCK_STATIC_CATEGORIES. This means OpenStock no "
            "longer claims ownership — re-evaluate before proceeding."
        )


class TestLayer1RejectsOpenStockOwned:
    """Direction 6 PoC core: any attempt to register an ExtraSource
    adapter declaring one of the six OpenStock-owned categories MUST
    raise :class:`ExtraSourceCategoryConflictError` so the migration
    target (``OpenStockClient.fetch(category, ...)``) is unambiguous.
    """

    @pytest.mark.parametrize("category", OPENSTOCK_OWNED_CATEGORIES)
    def test_register_overlapping_category_raises(self, category: str) -> None:
        adapter = _OverlappingStubAdapter(
            name=f"legacy-{category.lower()}",
            category=category,
        )
        with pytest.raises(ExtraSourceCategoryConflictError) as exc:
            register_extra_source(adapter)
        msg = str(exc.value)
        assert category in msg
        assert "OpenStock static inventory" in msg

    @pytest.mark.parametrize("category", OPENSTOCK_OWNED_CATEGORIES)
    def test_failed_registration_does_not_pollute_registry(
        self,
        category: str,
    ) -> None:
        adapter = _OverlappingStubAdapter(
            name=f"legacy-{category.lower()}",
            category=category,
        )
        with pytest.raises(ExtraSourceCategoryConflictError):
            register_extra_source(adapter)
        # Registry must remain empty — failed registrations cannot
        # leave partial state that later bypasses the guard.
        from app.services.extra_source import get_registered

        assert get_registered() == {}
