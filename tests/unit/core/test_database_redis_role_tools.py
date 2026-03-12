from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SAVER_PATH = PROJECT_ROOT / "src/storage/database/save_realtime_market_data_simple.py"
MENU_PATH = PROJECT_ROOT / "src/storage/database/test_database_menu.py"


def _load_module(module_name: str, module_path: Path):
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    with patch('dotenv.load_dotenv', return_value=True):
        spec.loader.exec_module(module)
    return module


def test_simple_realtime_data_saver_defaults_to_app_cache_role(monkeypatch) -> None:
    monkeypatch.delenv('REDIS_DB', raising=False)
    monkeypatch.delenv('REDIS_APP_CACHE_DB', raising=False)
    module = _load_module('test_simple_realtime_data_saver_module', SAVER_PATH)

    with patch.object(module, 'load_dotenv', return_value=True):
        saver = module.SimpleRealtimeDataSaver()

    assert saver.config['redis_db'] == 1


def test_database_test_tool_defaults_to_tooling_role(monkeypatch) -> None:
    monkeypatch.delenv('REDIS_DB', raising=False)
    monkeypatch.delenv('REDIS_TOOLING_DB', raising=False)
    module = _load_module('test_database_test_tool_module', MENU_PATH)

    tool = module.DatabaseTestTool()
    config = tool.load_config()

    assert config['redis']['db'] == 0
