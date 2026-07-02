"""Unit tests for ExtraSource contract types (Phase 1.4).

Covers frozen dataclass immutability, default field values, and
Protocol structural checks. Registration behavior is covered in
``test_registry.py``.
"""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

from app.services.extra_source import (
    ExtraSourceAdapter,
    ExtraSourceCategoryConflictError,
    ExtraSourceMeta,
    ExtraSourceNameConflictError,
    ExtraSourceResult,
)


class TestExtraSourceMeta:
    def test_basic_construction(self) -> None:
        meta = ExtraSourceMeta(name="big-deal", category="MARKET_BIG_DEAL", expires_on=None)
        assert meta.name == "big-deal"
        assert meta.category == "MARKET_BIG_DEAL"
        assert meta.expires_on is None

    def test_temp_override_with_expiration(self) -> None:
        meta = ExtraSourceMeta(
            name="big-deal",
            category="MARKET_BIG_DEAL",
            expires_on="2026-09-30",
        )
        assert meta.expires_on == "2026-09-30"

    def test_frozen_instance_raises_on_assignment(self) -> None:
        meta = ExtraSourceMeta(name="x", category="Y", expires_on=None)
        with pytest.raises(dataclasses.FrozenInstanceError):
            meta.name = "other"  # type: ignore[misc]

    def test_frozen_instance_raises_on_category_assignment(self) -> None:
        meta = ExtraSourceMeta(name="x", category="Y", expires_on=None)
        with pytest.raises(dataclasses.FrozenInstanceError):
            meta.category = "Z"  # type: ignore[misc]

    def test_frozen_instance_raises_on_expires_on_assignment(self) -> None:
        meta = ExtraSourceMeta(name="x", category="Y", expires_on=None)
        with pytest.raises(dataclasses.FrozenInstanceError):
            meta.expires_on = "2026-12-31"  # type: ignore[misc]


class TestExtraSourceResult:
    def test_construction_with_data_and_provider(self) -> None:
        result = ExtraSourceResult(data={"rows": [1, 2]}, provider_used="akshare")
        assert result.data == {"rows": [1, 2]}
        assert result.provider_used == "akshare"

    def test_no_fallback_field(self) -> None:
        # fallback_triggered removed per REVIEW_2026-07-02.md D2 (YAGNI:
        # ExtraSource is single-source, the field was always False).
        fields = {f.name for f in dataclasses.fields(ExtraSourceResult)}
        assert "fallback_triggered" not in fields

    def test_frozen(self) -> None:
        result = ExtraSourceResult(data=None, provider_used="x")
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.provider_used = "y"  # type: ignore[misc]


class _ValidAdapter:
    def __init__(self, name: str, category: str) -> None:
        self._meta = ExtraSourceMeta(name=name, category=category)

    def get_meta(self) -> ExtraSourceMeta:
        return self._meta

    def fetch(self, params: dict[str, Any]) -> ExtraSourceResult:
        return ExtraSourceResult(data={"echo": params}, provider_used="stub")


class _MissingFetchAdapter:
    def __init__(self) -> None:
        self._meta = ExtraSourceMeta(name="incomplete", category="X")

    def get_meta(self) -> ExtraSourceMeta:
        return self._meta

    # Missing fetch(): should fail Protocol check.


class TestExtraSourceAdapterProtocol:
    def test_valid_adapter_isinstance(self) -> None:
        adapter = _ValidAdapter(name="x", category="Y")
        assert isinstance(adapter, ExtraSourceAdapter)

    def test_adapter_missing_fetch_not_isinstance(self) -> None:
        adapter = _MissingFetchAdapter()
        assert not isinstance(adapter, ExtraSourceAdapter)


class TestExceptionTypes:
    def test_category_conflict_is_runtime_error(self) -> None:
        assert issubclass(ExtraSourceCategoryConflictError, RuntimeError)

    def test_name_conflict_is_runtime_error(self) -> None:
        assert issubclass(ExtraSourceNameConflictError, RuntimeError)

    def test_two_exceptions_distinct(self) -> None:
        assert ExtraSourceCategoryConflictError is not ExtraSourceNameConflictError
