from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch


REGISTRY_PATH = Path('/opt/claude/mystocks_spec/src/core/datasource/registry.py')


def _load_registry_module(module_name: str = 'test_src_core_datasource_registry_module'):
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, REGISTRY_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_datasource_registry_defaults_to_monitoring_role_url() -> None:
    module = _load_registry_module('test_src_core_datasource_registry_default')

    with patch.object(module, 'get_redis_url_for_role', return_value='redis://redis-host:6380/0', create=True):
        registry = module.DataSourceRegistry()

    assert registry._redis_url == 'redis://redis-host:6380/0'


async def _connect_registry(module):
    registry = module.DataSourceRegistry(redis_url=None)
    await registry.connect()
    return registry


def test_datasource_registry_connect_uses_role_aware_url_when_missing() -> None:
    module = _load_registry_module('test_src_core_datasource_registry_connect')
    fake_redis = AsyncMock()
    fake_redis.ping = AsyncMock(return_value=True)

    with patch.object(module, 'get_redis_url_for_role', return_value='redis://redis-host:6380/0', create=True) as mock_url, patch.object(
        module.redis, 'from_url', return_value=fake_redis
    ) as mock_from_url:
        registry = module.DataSourceRegistry(redis_url=None)
        import asyncio
        asyncio.run(registry.connect())

    mock_url.assert_called_once_with('monitoring_events')
    mock_from_url.assert_called_once_with('redis://redis-host:6380/0', decode_responses=True)
    fake_redis.ping.assert_awaited_once()
    assert registry._redis is fake_redis
