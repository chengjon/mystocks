"""Regression tests for data source registry exception contract."""

from __future__ import annotations

import pytest

from app.api import data_source_registry
from app.core.exceptions import BusinessException


class _EmptyRegistryManager:
    registry: dict[str, object] = {}


class _SingleRegistryManager:
    registry = {
        "akshare.stock_zh_a_hist": {
            "config": {"source_name": "akshare", "status": "active"},
            "last_call": None,
            "call_count": 0,
        }
    }

    def health_check(self, endpoint_name: str | None = None):
        if endpoint_name is None:
            return {"summary": {"total": 1, "healthy": 1, "unhealthy": 0}, "results": {}}
        return {"endpoint_name": endpoint_name, "status": "healthy"}


@pytest.mark.asyncio
async def test_get_data_source_uses_business_exception_for_missing_endpoint(monkeypatch):
    monkeypatch.setattr(data_source_registry, "get_manager", lambda: _EmptyRegistryManager())

    with pytest.raises(BusinessException) as exc_info:
        await data_source_registry.get_data_source("missing.endpoint")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "接口不存在: missing.endpoint"


@pytest.mark.asyncio
async def test_get_data_source_success_uses_unified_response(monkeypatch):
    monkeypatch.setattr(data_source_registry, "get_manager", lambda: _SingleRegistryManager())

    response = await data_source_registry.get_data_source("akshare.stock_zh_a_hist")

    assert response.success is True
    assert response.message == "数据源详情获取成功"
    assert response.data["endpoint_name"] == "akshare.stock_zh_a_hist"
    assert response.data["source_name"] == "akshare"


def test_require_write_auth_uses_business_exception_for_missing_token(monkeypatch):
    monkeypatch.setattr(data_source_registry.settings, "testing", False, raising=False)

    with pytest.raises(BusinessException) as exc_info:
        data_source_registry._require_write_auth(None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["error"]["code"] == "UNAUTHORIZED"
    assert exc_info.value.detail["message"] == "缺少或无效的认证凭据"


@pytest.mark.asyncio
async def test_update_data_source_uses_business_exception_for_empty_update(monkeypatch):
    monkeypatch.setattr(data_source_registry.settings, "testing", True, raising=False)
    monkeypatch.setattr(data_source_registry, "get_manager", lambda: _SingleRegistryManager())

    with pytest.raises(BusinessException) as exc_info:
        await data_source_registry.update_data_source(
            "akshare.stock_zh_a_hist",
            data_source_registry.DataSourceUpdate(),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "无更新内容"


@pytest.mark.asyncio
async def test_health_check_data_source_success_uses_unified_response(monkeypatch):
    monkeypatch.setattr(data_source_registry.settings, "testing", True, raising=False)
    monkeypatch.setattr(data_source_registry, "get_manager", lambda: _SingleRegistryManager())

    response = await data_source_registry.health_check_data_source("akshare.stock_zh_a_hist")

    assert response.success is True
    assert response.message == "无预设测试参数"
    assert response.data["endpoint_name"] == "akshare.stock_zh_a_hist"
    assert response.data["status"] == "skipped"
