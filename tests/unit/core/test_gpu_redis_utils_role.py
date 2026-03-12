from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REDIS_UTILS_PATH = PROJECT_ROOT / "src/gpu/api_system/utils/redis_utils.py"
CACHE_OPT_PATH = PROJECT_ROOT / "src/gpu/api_system/utils/cache_optimization.py"


def _load_module(module_name: str, path: Path):
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_redis_queue_defaults_to_tooling_role_db(monkeypatch) -> None:
    monkeypatch.delenv('REDIS_DB', raising=False)
    monkeypatch.delenv('REDIS_TOOLING_DB', raising=False)
    module = _load_module('test_gpu_redis_utils_module', REDIS_UTILS_PATH)

    queue = module.RedisQueue()

    assert queue.db == 0


def test_redis_queue_prefers_tooling_role_env(monkeypatch) -> None:
    monkeypatch.setenv('REDIS_DB', '9')
    monkeypatch.setenv('REDIS_TOOLING_DB', '4')
    module = _load_module('test_gpu_redis_utils_module_env', REDIS_UTILS_PATH)

    queue = module.RedisQueue()

    assert queue.db == 4


def test_redis_cache_defaults_to_tooling_role_db(monkeypatch) -> None:
    monkeypatch.delenv('REDIS_DB', raising=False)
    monkeypatch.delenv('REDIS_TOOLING_DB', raising=False)
    module = _load_module('test_gpu_cache_opt_module', CACHE_OPT_PATH)

    with patch.object(module.RedisCache, 'connect', return_value=None):
        cache = module.RedisCache()

    assert cache.db == 0


def test_redis_cache_prefers_tooling_role_env(monkeypatch) -> None:
    monkeypatch.setenv('REDIS_DB', '9')
    monkeypatch.setenv('REDIS_TOOLING_DB', '4')
    module = _load_module('test_gpu_cache_opt_module_env', CACHE_OPT_PATH)

    with patch.object(module.RedisCache, 'connect', return_value=None):
        cache = module.RedisCache()

    assert cache.db == 4


def test_multi_level_cache_initialize_uses_tooling_role_db(monkeypatch) -> None:
    monkeypatch.delenv('REDIS_DB', raising=False)
    monkeypatch.delenv('REDIS_TOOLING_DB', raising=False)
    module = _load_module('test_gpu_cache_opt_module_init', CACHE_OPT_PATH)
    fake_redis = MagicMock()
    fake_client = MagicMock()
    fake_redis.Redis.return_value = fake_client

    with patch.object(module, 'redis', fake_redis):
        cache = module.MultiLevelCache()
        cache.initialize(redis_host='redis-host', redis_port=6380)

    fake_redis.Redis.assert_called_once_with(host='redis-host', port=6380, db=0, decode_responses=True, socket_timeout=2, socket_connect_timeout=2)
    fake_client.ping.assert_called_once_with()
