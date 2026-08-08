from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch



READINESS_MODULE_PATH = Path('/opt/claude/mystocks_spec/web/backend/app/core/readiness.py')
SCRIPT_PATH = Path('/opt/claude/mystocks_spec/scripts/dev/check_mongodb_runtime_health.sh')


def _load_readiness_module(module_name: str = 'test_web_backend_readiness_module'):
    sys.modules.pop(module_name, None)

    fake_database_module = type('FakeDatabaseModule', (), {'get_postgresql_engine': lambda: None})()
    fake_config_module = type('FakeConfigModule', (), {'settings': object()})()

    spec = importlib.util.spec_from_file_location(module_name, READINESS_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None

    with patch.dict(
        sys.modules,
        {
            'app': type('FakeApp', (), {})(),
            'app.core': type('FakeCore', (), {})(),
            'app.core.database': fake_database_module,
            'app.core.config': fake_config_module,
        },
    ):
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return module


def test_collect_readiness_checks_keeps_mongodb_optional() -> None:
    module = _load_readiness_module('test_web_backend_readiness_optional')

    with patch.object(module, 'check_postgresql_readiness', return_value={'status': 'ready', 'required': True}), patch.object(
        module, 'check_redis_readiness', return_value={'status': 'ready', 'required': True}
    ), patch.object(module, 'check_mongodb_readiness', return_value={'status': 'optional_unavailable', 'required': False}):
        ready, checks = module.collect_readiness_checks()

    assert ready is True
    assert checks['mongodb']['status'] == 'optional_unavailable'
    assert checks['mongodb']['required'] is False


def test_collect_readiness_checks_fails_on_required_checks_only() -> None:
    module = _load_readiness_module('test_web_backend_readiness_required')

    with patch.object(module, 'check_postgresql_readiness', return_value={'status': 'error', 'required': True}), patch.object(
        module, 'check_redis_readiness', return_value={'status': 'ready', 'required': True}
    ), patch.object(module, 'check_mongodb_readiness', return_value={'status': 'ready', 'required': False}):
        ready, checks = module.collect_readiness_checks()

    assert ready is False
    assert checks['postgresql']['status'] == 'error'


def test_mongodb_runtime_health_script_uses_mongosh_and_standard_env_contract() -> None:
    script = SCRIPT_PATH.read_text()

    assert 'mongosh' in script
    assert 'db.adminCommand({ ping: 1 })' in script
    assert 'MONGODB_HOST' in script
    assert 'MONGODB_PORT' in script
    assert 'MONGODB_ROOT_USERNAME' in script
    assert 'MONGODB_ROOT_PASSWORD' in script
    assert 'MONGODB_AUTH_SOURCE' in script
    assert 'MONGODB_IP' in script
    assert 'MONGODB_CONTAINER_NAME' in script
    assert 'docker exec' in script
    assert 'mongo --eval' not in script
