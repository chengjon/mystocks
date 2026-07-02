"""Unit tests for ExtraSourceRouter (Phase 2.1).

Covers the three dispatch paths defined in the spec:

* Static category → ``UnsupportedCategoryError`` (programmer error)
* Registered ExtraSource category → dispatch to adapter
* Unknown category → ``UnsupportedCategoryError``

Also covers adapter ``fetch()`` exception wrapping into
``ExtraSourceFetchError`` with diagnostic context.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.services.extra_source import (
    ExtraSourceFetchError,
    ExtraSourceMeta,
    ExtraSourceResult,
    ExtraSourceRouter,
    UnsupportedCategoryError,
    clear_registered,
    register_extra_source,
)


class _StubAdapter:
    """Stub adapter for tests. Records calls and returns canned data."""

    def __init__(
        self,
        name: str,
        category: str,
        payload: Any = None,
        raise_on_fetch: BaseException | None = None,
    ) -> None:
        self._meta = ExtraSourceMeta(name=name, category=category)
        self._payload = payload
        self._raise_on_fetch = raise_on_fetch
        self.fetch_calls: list[dict[str, Any]] = []

    def get_meta(self) -> ExtraSourceMeta:
        return self._meta

    def fetch(self, params: dict[str, Any]) -> ExtraSourceResult:
        self.fetch_calls.append({"params": params})
        if self._raise_on_fetch is not None:
            raise self._raise_on_fetch
        return ExtraSourceResult(
            data=self._payload,
            provider_used=self._meta.name,
        )


@pytest.fixture(autouse=True)
def _isolate_registry() -> None:
    clear_registered()
    yield
    clear_registered()


class TestStaticCategoryRejected:
    def test_fund_flow_raises(self) -> None:
        router = ExtraSourceRouter()
        with pytest.raises(UnsupportedCategoryError) as exc:
            router.fetch("FUND_FLOW", {})
        assert exc.value.category == "FUND_FLOW"
        assert "OpenStock" in exc.value.reason

    def test_northbound_flow_raises(self) -> None:
        router = ExtraSourceRouter()
        with pytest.raises(UnsupportedCategoryError):
            router.fetch("NORTHBOUND_FLOW", {})

    def test_static_category_rejected_even_if_adapter_somehow_registered(
        self,
    ) -> None:
        # Defensive: even if a bug allowed an adapter with a static
        # category to be registered (Layer 1 should have caught it),
        # the router still refuses. Belt-and-braces.
        # We can't actually register such an adapter (Layer 1 rejects),
        # so we test the path the router actually takes: any category
        # in OPENSTOCK_STATIC_CATEGORIES is refused before registry
        # lookup.
        router = ExtraSourceRouter()
        with pytest.raises(UnsupportedCategoryError):
            router.fetch("KLINES", {})


class TestRegisteredCategoryDispatched:
    def test_registered_category_calls_adapter(self) -> None:
        adapter = _StubAdapter(
            name="big-deal",
            category="MARKET_BIG_DEAL",
            payload={"rows": [{"deal": "x"}]},
        )
        register_extra_source(adapter)

        router = ExtraSourceRouter()
        result = router.fetch("MARKET_BIG_DEAL", {"date": "2026-07-02"})

        assert isinstance(result, ExtraSourceResult)
        assert result.data == {"rows": [{"deal": "x"}]}
        assert result.provider_used == "big-deal"
        assert adapter.fetch_calls == [{"params": {"date": "2026-07-02"}}]

    def test_temp_override_category_dispatched(self) -> None:
        # TEMP_OVERRIDE adapters (expires_on set) dispatch the same as
        # regular ones; CI handles expiration, router does not.
        meta = ExtraSourceMeta(
            name="temp",
            category="TEMP_CATEGORY",
            expires_on="2026-09-30",
        )

        class _Explicit:
            def get_meta(self) -> ExtraSourceMeta:
                return meta

            def fetch(self, params: dict[str, Any]) -> ExtraSourceResult:
                return ExtraSourceResult(data="ok", provider_used="temp")

        register_extra_source(_Explicit())
        router = ExtraSourceRouter()
        result = router.fetch("TEMP_CATEGORY", {})
        assert result.data == "ok"


class TestUnknownCategoryRejected:
    def test_unknown_category_raises(self) -> None:
        router = ExtraSourceRouter()
        with pytest.raises(UnsupportedCategoryError) as exc:
            router.fetch("DOES_NOT_EXIST", {})
        assert exc.value.category == "DOES_NOT_EXIST"
        assert "not registered" in exc.value.reason


class TestAdapterFetchExceptionWrapped:
    def test_generic_exception_wrapped(self) -> None:
        adapter = _StubAdapter(
            name="fail-adapter",
            category="FAIL_CAT",
            raise_on_fetch=RuntimeError("upstream timeout"),
        )
        register_extra_source(adapter)

        router = ExtraSourceRouter()
        with pytest.raises(ExtraSourceFetchError) as exc:
            router.fetch("FAIL_CAT", {})

        assert exc.value.adapter_name == "fail-adapter"
        assert exc.value.category == "FAIL_CAT"
        assert exc.value.cause_type == "RuntimeError"
        assert isinstance(exc.value.__cause__, RuntimeError)
        assert "upstream timeout" in str(exc.value.__cause__)

    def test_value_error_wrapped(self) -> None:
        adapter = _StubAdapter(
            name="value-adapter",
            category="VAL_CAT",
            raise_on_fetch=ValueError("bad param"),
        )
        register_extra_source(adapter)

        router = ExtraSourceRouter()
        with pytest.raises(ExtraSourceFetchError) as exc:
            router.fetch("VAL_CAT", {})
        assert exc.value.cause_type == "ValueError"

    def test_no_retry_on_failure(self) -> None:
        # The router must NOT retry the adapter after a failure.
        # Verified by counting fetch_calls == 1 after exception.
        adapter = _StubAdapter(
            name="once",
            category="ONCE_CAT",
            raise_on_fetch=RuntimeError("boom"),
        )
        register_extra_source(adapter)

        router = ExtraSourceRouter()
        with pytest.raises(ExtraSourceFetchError):
            router.fetch("ONCE_CAT", {})
        assert len(adapter.fetch_calls) == 1


class TestDefaultRouter:
    def test_default_router_is_extra_source_router_instance(self) -> None:
        from app.services.extra_source import default_router

        assert isinstance(default_router, ExtraSourceRouter)

    def test_default_router_shares_global_registry(self) -> None:
        # default_router uses module-level find_by_category, so it
        # observes registrations made via register_extra_source.
        from app.services.extra_source import default_router

        adapter = _StubAdapter(
            name="def",
            category="DEFAULT_ROUTER_CAT",
            payload={"hi": True},
        )
        register_extra_source(adapter)
        result = default_router.fetch("DEFAULT_ROUTER_CAT", {})
        assert result.data == {"hi": True}
