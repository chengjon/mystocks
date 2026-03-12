from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
MODULE_PATH = PROJECT_ROOT / "src/gpu/api_system/config/system_config.py"


def _load_module():
    module_name = "test_gpu_system_config_redis_role_module"
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_gpu_system_config_defaults_to_tooling_redis_role(monkeypatch) -> None:
    for key in ['REDIS_DB', 'REDIS_TOOLING_DB']:
        monkeypatch.delenv(key, raising=False)
    module = _load_module()

    config = module.SystemConfig()

    assert config.redis_config['db'] == 0


def test_gpu_system_config_prefers_tooling_role_env(monkeypatch) -> None:
    monkeypatch.setenv('REDIS_DB', '9')
    monkeypatch.setenv('REDIS_TOOLING_DB', '4')
    module = _load_module()

    config = module.SystemConfig()

    assert config.redis_config['db'] == 4
