from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
MODULE_PATH = PROJECT_ROOT / "src/utils/check_db_health.py"


def _load_module():
    module_name = "test_check_db_health_module"
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_check_db_health_uses_app_cache_role(monkeypatch) -> None:
    module = _load_module()
    fake_settings = MagicMock(redis_host='redis-host', redis_port=6380, redis_password='', redis_db=9)
    fake_redis_client = MagicMock()
    fake_redis_client.info.return_value = {'redis_version': '7.0'}
    fake_redis_client.dbsize.return_value = 1
    fake_redis_module = MagicMock(Redis=MagicMock(return_value=fake_redis_client))

    with patch.dict(sys.modules, {'redis': fake_redis_module, 'web.backend.app.core.config': MagicMock(settings=fake_settings)}), \
         patch.object(module, 'get_redis_connection_kwargs', return_value={'host': 'redis-host', 'port': 6380, 'db': 1, 'password': None, 'decode_responses': True}) as mock_kwargs:
        ok, err = module.check_redis_connection()

    assert ok is True
    assert err is None
    mock_kwargs.assert_called_once_with('app_cache', decode_responses=True)
    fake_redis_module.Redis.assert_called_once_with(host='redis-host', port=6380, password=None, db=1, socket_connect_timeout=5)
    fake_redis_client.ping.assert_called_once_with()
