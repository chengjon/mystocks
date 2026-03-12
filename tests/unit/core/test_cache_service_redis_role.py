from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
MODULE_PATH = PROJECT_ROOT / "web/backend/app/services/cache_service.py"


def _load_module():
    module_name = "test_cache_service_redis_role_module"
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_cache_service_defaults_to_app_cache_role_db() -> None:
    module = _load_module()
    service = module.CacheService(cache_type=module.CacheType.REDIS)

    assert service.redis_db == 1
