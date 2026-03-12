from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
MENU_PATH = PROJECT_ROOT / "src/storage/database/test_database_menu.py"
GPU_CONFTEST_PATH = PROJECT_ROOT / "src/gpu/api_system/tests/conftest.py"


def _load_module(module_name: str, path: Path):
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    with patch('dotenv.load_dotenv', return_value=True):
        spec.loader.exec_module(module)
    return module


def test_database_test_tool_prefers_tooling_role_env(monkeypatch) -> None:
    monkeypatch.setenv('REDIS_DB', '9')
    monkeypatch.setenv('REDIS_TOOLING_DB', '4')
    module = _load_module('test_database_menu_tooling_role_module', MENU_PATH)

    tool = module.DatabaseTestTool()
    cfg = tool.load_config()

    assert cfg['redis']['db'] == 4


def test_gpu_redis_available_fixture_prefers_tooling_role_env(monkeypatch) -> None:
    monkeypatch.setenv('REDIS_HOST', 'redis-host')
    monkeypatch.setenv('REDIS_PORT', '6380')
    monkeypatch.setenv('REDIS_DB', '9')
    monkeypatch.setenv('REDIS_TOOLING_DB', '4')
    fake_client = MagicMock()
    fake_redis_module = MagicMock(Redis=MagicMock(return_value=fake_client))

    with patch.dict(sys.modules, {'redis': fake_redis_module}):
        module = _load_module('test_gpu_conftest_tooling_role_module', GPU_CONFTEST_PATH)
        result = module.redis_available.__wrapped__()

    assert result is True
    fake_redis_module.Redis.assert_called_once_with(host='redis-host', port=6380, db=4)
    fake_client.ping.assert_called_once_with()
