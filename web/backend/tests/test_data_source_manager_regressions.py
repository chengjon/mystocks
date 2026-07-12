from __future__ import annotations

import importlib.util
import inspect
import json
import os
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
            },
        ),
        encoding="utf-8",
    )

    manager = module.DataSourceManager(str(config_path))

    assert manager.get_enabled_modules() == ["market"]
    assert manager.get_module_source("market") == module.DataSourceType.REAL
    assert manager.get_module_source("dashboard") == module.DataSourceType.MOCK


def test_backend_duplicate_data_sources_json_is_removed():
    assert not (REPO_ROOT / "web/backend/config/data_sources.json").exists()


def test_data_source_config_matrix_distinguishes_yaml_and_json_roles():
    from config.data_sources_loader import (
        JSON_DATA_SOURCES_CONFIG_PATH,
        YAML_DATA_SOURCES_REGISTRY_PATH,
        DataSourcesLoader,
        get_data_source_config_matrix,
    )

    matrix = get_data_source_config_matrix()

    assert matrix["yaml_registry"]["path"] == YAML_DATA_SOURCES_REGISTRY_PATH
    assert matrix["yaml_registry"]["format"] == "yaml"
    assert "DataSourcesLoader" in matrix["yaml_registry"]["consumers"]
    assert "DataSourceManagerV2" in matrix["yaml_registry"]["consumers"]
    assert "ConfigManager" in matrix["yaml_registry"]["consumers"]
    assert "data_source_config.get_config_manager" in matrix["yaml_registry"]["consumers"]

    assert matrix["json_runtime"]["path"] == JSON_DATA_SOURCES_CONFIG_PATH
    assert matrix["json_runtime"]["format"] == "json"
    assert "DataSourceManager" in matrix["json_runtime"]["consumers"]
    assert "DataSourceFactory" in matrix["json_runtime"]["consumers"]

    custom_loader = DataSourcesLoader("tmp-demo")
    assert custom_loader.main_config_file == Path("tmp-demo") / Path(YAML_DATA_SOURCES_REGISTRY_PATH).name
    assert custom_loader.sources_dir == Path("tmp-demo") / "data_sources"


def test_data_source_config_matrix_returns_isolated_copy():
    from config.data_sources_loader import get_data_source_config_matrix

    first = get_data_source_config_matrix()
    first["yaml_registry"]["consumers"].append("mutated")

    second = get_data_source_config_matrix()

    assert "mutated" not in second["yaml_registry"]["consumers"]


def test_default_entry_points_follow_declared_source_of_truth_paths():
    from config.data_sources_loader import JSON_DATA_SOURCES_CONFIG_PATH, YAML_DATA_SOURCES_REGISTRY_PATH
    from src.core.data_source.base import DataSourceManagerV2
    from src.core.data_source.config_manager import ConfigManager
    from web.backend.tests._test_data_source_factory_support import DataSourceFactory

    backend_manager_module = _load_module(
        "web/backend/app/core/data_source_manager.py",
        "test_data_source_manager_regressions_backend_manager_module",
    )

    expected_yaml_path = str((REPO_ROOT / "config" / "data_sources_registry.yaml").resolve())
    expected_json_path = str((REPO_ROOT / "config" / "data_sources.json").resolve())

    assert expected_yaml_path == YAML_DATA_SOURCES_REGISTRY_PATH
    assert expected_json_path == JSON_DATA_SOURCES_CONFIG_PATH
    assert inspect.signature(DataSourceManagerV2).parameters["yaml_config_path"].default == expected_yaml_path
    assert inspect.signature(ConfigManager).parameters["yaml_config_path"].default == expected_yaml_path
    assert inspect.signature(backend_manager_module.DataSourceManager).parameters["config_path"].default == expected_json_path
    assert inspect.signature(DataSourceFactory).parameters["config_file"].default == expected_json_path

    previous_cwd = Path.cwd()
    try:
        os.chdir(REPO_ROOT / "web/backend")
        backend_manager = backend_manager_module.DataSourceManager()
        data_source_factory = DataSourceFactory()
    finally:
        os.chdir(previous_cwd)

    assert backend_manager.config_path == expected_json_path
    assert data_source_factory.config_file == expected_json_path
