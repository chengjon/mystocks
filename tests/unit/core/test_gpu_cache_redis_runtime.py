from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


PROJECT_ROOT = Path('/opt/claude/mystocks_spec')
CACHE_OPT_PATH = PROJECT_ROOT / 'src/gpu/api_system/utils/cache_optimization.py'
ENTRYPOINT_PATH = PROJECT_ROOT / 'src/gpu/api_system/deployment/entrypoint.sh'


def _load_cache_opt(module_name: str):
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, CACHE_OPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_gpu_multilevel_cache_initialize_respects_tooling_role_env(monkeypatch) -> None:
    monkeypatch.setenv('REDIS_DB', '9')
    monkeypatch.setenv('REDIS_TOOLING_DB', '4')
    module = _load_cache_opt('test_gpu_cache_opt_runtime_module')

    fake_redis = MagicMock()
    fake_client = MagicMock()
    fake_redis.Redis.return_value = fake_client

    with patch.object(module, 'redis', fake_redis):
        cache = module.MultiLevelCache()
        cache.initialize(redis_host='redis-host', redis_port=6380)

    fake_redis.Redis.assert_called_once_with(
        host='redis-host',
        port=6380,
        db=4,
        decode_responses=True,
        socket_timeout=2,
        socket_connect_timeout=2,
    )
    fake_client.ping.assert_called_once_with()


def test_gpu_entrypoint_prefers_tooling_role_env_fallback_chain() -> None:
    text = ENTRYPOINT_PATH.read_text(encoding='utf-8')
    assert 'REDIS_TOOLING_DB' in text
    assert "os.getenv('REDIS_TOOLING_DB', os.getenv('REDIS_DB', 0))" in text
