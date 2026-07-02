"""Integration tests for lifespan-time adapter loading (Phase 2.3).

Validates the dynamic-loading mechanism the lifespan uses (import path
string → importlib → instantiate → register_extra_source), without
booting the full FastAPI app (which requires Postgres/Redis/etc).

Covers the four scenarios from tasks.md Phase 2.3:

* 启动时正常注册一个 stub ExtraSource
* 启动时重叠 category 触发启动 fail
* ExtraSourceRouter.fetch(registered_category) 命中 stub adapter
* ExtraSourceRouter.fetch(static_category) / fetch(unknown_category)
  → UnsupportedCategoryError

The dynamic import path is exercised via real importable module paths
under ``app.services.extra_source_adapters`` (test stubs registered as
first-class modules so ``importlib.import_module`` resolves them the
same way production adapters will).
"""

from __future__ import annotations

import importlib
from typing import Any

import pytest

from app.services.extra_source import (
    ExtraSourceCategoryConflictError,
    ExtraSourceResult,
    UnsupportedCategoryError,
    clear_registered,
    default_router,
    find_by_category,
    register_extra_source,
)

# Test fixture (not hardcoded historical data — synthetic param for router).
_TEST_DATE = "2026-07-02"

# Importable module paths for stub adapters. Stubs live under
# app/services/extra_source/_test_stubs/ to avoid the namespace collision
# between repo-root tests/__init__.py and web/backend/tests/.
_BIGDEAL_PATH = "app.services.extra_source._test_stubs._stub_bigdeal_adapter.BigDealAdapter"
_FUNDFLOW_OVERLAP_PATH = "app.services.extra_source._test_stubs._stub_fundflow_adapter.FundFlowOverlapAdapter"


def _load_adapter_from_path(path: str) -> Any:
    """Mirror of lifespan loader — given 'module.path.ClassName',
    import the module, get the class, instantiate with no args.
    """
    module_path, _, class_name = path.rpartition(".")
    if not module_path or not class_name:
        raise ValueError(f"EXTRA_SOURCE_ADAPTERS 条目格式错误,期望 'module.path.ClassName', 实际 '{path}'")
    module = importlib.import_module(module_path)
    adapter_cls = getattr(module, class_name)
    return adapter_cls()


@pytest.fixture(autouse=True)
def _isolate_registry() -> None:
    clear_registered()
    yield
    clear_registered()


class TestLifespanLoaderPath:
    """End-to-end test of the import path → registered adapter flow."""

    def test_load_stub_adapter_and_register(self) -> None:
        adapter = _load_adapter_from_path(_BIGDEAL_PATH)
        register_extra_source(adapter)

        found = find_by_category("MARKET_BIG_DEAL")
        assert found is adapter

        result = default_router.fetch("MARKET_BIG_DEAL", {"date": _TEST_DATE})
        assert isinstance(result, ExtraSourceResult)
        assert result.provider_used == "big-deal-stub"
        assert result.data == {"rows": [{"deal": "stubbed"}]}

    def test_router_fetch_after_dynamic_load_hits_stub(self) -> None:
        adapter = _load_adapter_from_path(_BIGDEAL_PATH)
        register_extra_source(adapter)

        result = default_router.fetch("MARKET_BIG_DEAL", {})
        assert result.data == {"rows": [{"deal": "stubbed"}]}

    def test_static_category_rejected_at_register(self) -> None:
        # Layer 1 guard: register_extra_source itself rejects static
        # categories. This is the "启动 fail" path during lifespan.
        adapter = _load_adapter_from_path(_FUNDFLOW_OVERLAP_PATH)
        with pytest.raises(ExtraSourceCategoryConflictError) as exc:
            register_extra_source(adapter)
        assert "FUND_FLOW" in str(exc.value)


class TestRouterDispatchIntegration:
    """Full router paths after dynamic registration."""

    def test_unknown_category_unsupported(self) -> None:
        with pytest.raises(UnsupportedCategoryError) as exc:
            default_router.fetch("DOES_NOT_EXIST", {})
        assert exc.value.category == "DOES_NOT_EXIST"
        assert "not registered" in exc.value.reason

    def test_static_category_unsupported(self) -> None:
        with pytest.raises(UnsupportedCategoryError) as exc:
            default_router.fetch("FUND_FLOW", {})
        assert exc.value.category == "FUND_FLOW"
        assert "OpenStock" in exc.value.reason


class TestSettingsFieldParsing:
    """Validates the settings.extra_source_adapters property that the
    lifespan reads before invoking the loader.
    """

    def test_empty_string_yields_empty_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("EXTRA_SOURCE_ADAPTERS", "")
        from app.core.config import Settings

        s = Settings()
        assert s.extra_source_adapters == []

    def test_comma_separated_parses_to_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("EXTRA_SOURCE_ADAPTERS", " mod.a.Cls1 , mod.b.Cls2 ,, mod.c.Cls3 ")
        from app.core.config import Settings

        s = Settings()
        assert s.extra_source_adapters == ["mod.a.Cls1", "mod.b.Cls2", "mod.c.Cls3"]
