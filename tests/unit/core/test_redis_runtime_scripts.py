from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


VERIFY_SCRIPT = Path('/opt/claude/mystocks_spec/scripts/dev/tools/verify-database-connections.sh')
CHECK_DB_HEALTH_MODULE = Path('/opt/claude/mystocks_spec/scripts/dev/check_db_health.py')


def test_verify_database_connections_script_mentions_role_aware_redis_contract() -> None:
    text = VERIFY_SCRIPT.read_text()
    assert 'REDIS_APP_CACHE_DB' in text
    assert 'REDIS_MONITORING_DB' in text
    assert 'app_cache' in text or 'role=app_cache' in text


def test_check_db_health_uses_role_aware_redis_connection_kwargs() -> None:
    module_name = 'test_dev_check_db_health_module'
    spec = importlib.util.spec_from_file_location(module_name, CHECK_DB_HEALTH_MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None

    fake_settings = MagicMock(redis_host='redis-host', redis_port=6380, redis_password='', redis_db=9)
    fake_redis_client = MagicMock()
    fake_redis_client.info.return_value = {'redis_version': '7.0', 'used_memory_human': '1M'}
    fake_redis_client.dbsize.return_value = 12
    fake_redis_module = MagicMock(Redis=MagicMock(return_value=fake_redis_client))

    with patch.dict(sys.modules, {'redis': fake_redis_module, 'web.backend.app.core.config': MagicMock(settings=fake_settings)}), patch(
        'src.utils.redis_runtime_config.get_redis_connection_kwargs',
        return_value={'host': 'redis-host', 'port': 6380, 'db': 1, 'password': None, 'decode_responses': True},
    ) as mock_kwargs:
        sys.modules.pop(module_name, None)
        spec.loader.exec_module(module)
        ok, err = module.check_redis_connection()

    assert ok is True
    assert err is None
    mock_kwargs.assert_called_once_with('app_cache', decode_responses=True)
    fake_redis_module.Redis.assert_called_once_with(host='redis-host', port=6380, password=None, db=1, socket_connect_timeout=5)
    fake_redis_client.ping.assert_called_once_with()
