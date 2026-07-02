"""Unit tests for ExtraSource registry (Phase 1.3).

Covers Layer 1 static registration checks:

* Normal ExtraSource (category not in OpenStock static inventory, expires_on=None)
  registers successfully.
* TEMP_OVERRIDE (category not in static inventory, expires_on set) also
  registers successfully — Layer 1 does NOT enforce expiration; CI does.
* Category overlap with OpenStock static inventory raises
  ``ExtraSourceCategoryConflictError``.
* Duplicate name raises ``ExtraSourceNameConflictError``.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.services.extra_source import (
    OPENSTOCK_STATIC_CATEGORIES,
    ExtraSourceCategoryConflictError,
    ExtraSourceMeta,
    ExtraSourceNameConflictError,
    ExtraSourceResult,
    clear_registered,
    find_by_category,
    get_registered,
    register_extra_source,
)
from app.services.extra_source.registry import _registered


class _StubAdapter:
    def __init__(
        self,
        name: str,
        category: str,
        expires_on: str | None = None,
    ) -> None:
        self._meta = ExtraSourceMeta(name=name, category=category, expires_on=expires_on)

    def get_meta(self) -> ExtraSourceMeta:
        return self._meta

    def fetch(self, params: dict[str, Any]) -> ExtraSourceResult:
        return ExtraSourceResult(data={"params": params}, provider_used="stub")


@pytest.fixture(autouse=True)
def _isolate_registry() -> None:
    """Clear registry before AND after each test so test order does not
    produce cross-test contamination via residual registrations."""
    clear_registered()
    yield
    clear_registered()


class TestStaticInventory:
    def test_static_inventory_has_seventy_entries(self) -> None:
        assert len(OPENSTOCK_STATIC_CATEGORIES) == 70

    def test_static_inventory_is_frozenset(self) -> None:
        assert isinstance(OPENSTOCK_STATIC_CATEGORIES, frozenset)

    @pytest.mark.parametrize(
        "category",
        [
            "FUND_FLOW",
            "NORTHBOUND_FLOW",
            "NORTHBOUND_HOLDING",
            "KLINES",
            "F10_DATA",  # Includes digit — confirms regex extraction
        ],
    )
    def test_known_openstock_categories_present(self, category: str) -> None:
        assert category in OPENSTOCK_STATIC_CATEGORIES


class TestRegisterNormalExtraSource:
    def test_basic_registration_succeeds(self) -> None:
        adapter = _StubAdapter(name="bespoke-thing", category="SOME_BESPOKE_CATEGORY")
        register_extra_source(adapter)
        registered = get_registered()
        assert "bespoke-thing" in registered
        assert registered["bespoke-thing"] is adapter

    def test_temp_override_passes_static_check(self) -> None:
        # expires_on does NOT participate in Layer 1 static check.
        # CI (separate script) enforces expiration.
        adapter = _StubAdapter(
            name="big-deal",
            category="MARKET_BIG_DEAL",  # NOT in OpenStock static inventory
            expires_on="2026-09-30",
        )
        register_extra_source(adapter)
        assert find_by_category("MARKET_BIG_DEAL") is adapter


class TestCategoryConflictRejection:
    def test_fund_flow_overlap_rejected(self) -> None:
        adapter = _StubAdapter(name="bad", category="FUND_FLOW")
        with pytest.raises(ExtraSourceCategoryConflictError) as exc:
            register_extra_source(adapter)
        msg = str(exc.value)
        assert "bad" in msg
        assert "FUND_FLOW" in msg

    def test_northbound_flow_overlap_rejected(self) -> None:
        adapter = _StubAdapter(name="nb", category="NORTHBOUND_FLOW")
        with pytest.raises(ExtraSourceCategoryConflictError):
            register_extra_source(adapter)

    def test_failed_registration_does_not_mutate_registry(self) -> None:
        adapter = _StubAdapter(name="bad", category="KLINES")
        with pytest.raises(ExtraSourceCategoryConflictError):
            register_extra_source(adapter)
        assert get_registered() == {}


class TestNameConflictRejection:
    def test_duplicate_name_rejected_even_with_different_category(self) -> None:
        first = _StubAdapter(name="dup", category="CATEGORY_A")
        second = _StubAdapter(name="dup", category="CATEGORY_B")
        register_extra_source(first)
        with pytest.raises(ExtraSourceNameConflictError) as exc:
            register_extra_source(second)
        assert "dup" in str(exc.value)

    def test_same_category_different_name_is_allowed(self) -> None:
        # Category uniqueness is enforced by OpenStock static inventory
        # overlap (Layer 1) — NOT by ExtraSource registry. Two adapters
        # MAY share a non-overlapping category if they have distinct
        # names, although typical deployments will have one adapter
        # per category.
        a = _StubAdapter(name="adapter-a", category="SOMETHING")
        b = _StubAdapter(name="adapter-b", category="SOMETHING")
        register_extra_source(a)
        register_extra_source(b)
        # find_by_category returns whichever was registered first when
        # multiple share a category; documented ambiguity.
        found = find_by_category("SOMETHING")
        assert found is not None


class TestFindByCategory:
    def test_unknown_category_returns_none(self) -> None:
        assert find_by_category("DOES_NOT_EXIST") is None

    def test_registered_category_returns_adapter(self) -> None:
        adapter = _StubAdapter(name="x", category="CAT_X")
        register_extra_source(adapter)
        assert find_by_category("CAT_X") is adapter


class TestClearRegistered:
    def test_clear_empties_registry(self) -> None:
        register_extra_source(_StubAdapter(name="a", category="A"))
        register_extra_source(_StubAdapter(name="b", category="B"))
        assert len(get_registered()) == 2
        clear_registered()
        assert get_registered() == {}
        # Internal invariant: the private dict is the SAME object across
        # the process lifetime so that registrations made before
        # import-time patterns still see the clear.
        assert _registered == {}
