from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


MULTI_LEVEL_PATH = Path('/opt/claude/mystocks_spec/src/core/cache/multi_level.py')


def _load_multi_level_module(module_name: str = 'test_src_core_multi_level_module'):
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, MULTI_LEVEL_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    with patch('prometheus_client.Counter', side_effect=lambda *a, **k: MagicMock()), patch(
        'prometheus_client.Gauge', side_effect=lambda *a, **k: MagicMock()
    ), patch('prometheus_client.Histogram', side_effect=lambda *a, **k: MagicMock()):
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return module


def test_src_core_multilevel_cache_initialize_defaults_to_app_cache_url() -> None:
    module = _load_multi_level_module('test_src_core_multi_level_default')
    cache = module.MultiLevelCache()
    fake_redis = AsyncMock()
    fake_redis.ping = AsyncMock(return_value=True)

    with patch.object(module, 'get_redis_url_for_role', return_value='redis://:secret@redis-host:6380/1', create=True) as mock_url, patch.object(
        module.redis, 'from_url', return_value=fake_redis
    ) as mock_from_url:
        asyncio.run(cache.initialize())

    mock_url.assert_called_once_with('app_cache')
    mock_from_url.assert_called_once_with('redis://:secret@redis-host:6380/1', decode_responses=True)
    fake_redis.ping.assert_awaited_once()
    assert cache._redis_connected is True


def test_src_core_init_cache_uses_role_aware_url_when_not_provided() -> None:
    module = _load_multi_level_module('test_src_core_multi_level_init_cache')
    fake_cache = AsyncMock()

    with patch.object(module, 'get_cache', return_value=fake_cache), patch.object(
        module, 'get_redis_url_for_role', return_value='redis://redis-host:6380/1', create=True
    ) as mock_url:
        asyncio.run(module.init_cache())

    mock_url.assert_called_once_with('app_cache')
    fake_cache.initialize.assert_awaited_once_with('redis://redis-host:6380/1')
