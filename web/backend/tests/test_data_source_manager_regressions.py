from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_module(module_path: str, module_name: str):
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, Path(module_path))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_data_source_manager_loads_current_data_sources_json_shape(tmp_path):
    module = _load_module(
        "web/backend/app/core/data_source_manager.py",
        "test_data_source_manager_regressions_module",
    )
    config_path = tmp_path / "config" / "data_sources.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "version": "1.0",
                "data_sources": {
                    "market": {
                        "type": "market",
                        "enabled": True,
                        "mode": "real",
                        "fallback_enabled": True,
                        "cache_ttl": 300,
                    },
                    "dashboard": {
                        "type": "dashboard",
                        "enabled": False,
                        "mode": "mock",
                        "fallback_enabled": False,
                        "cache_ttl": 120,
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    manager = module.DataSourceManager(str(config_path))

    assert manager.get_enabled_modules() == ["market"]
    assert manager.get_module_source("market") == module.DataSourceType.REAL
    assert manager.get_module_source("dashboard") == module.DataSourceType.MOCK


def test_backend_duplicate_data_sources_json_is_removed():
    assert not (REPO_ROOT / "web/backend/config/data_sources.json").exists()
