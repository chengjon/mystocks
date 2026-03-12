from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = PROJECT_ROOT / 'src/core/config.py'


def _load_module():
    module_name = 'test_cfg002_src_core_config_module'
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _clear_database_env(monkeypatch) -> None:
    for key in [
        'DB_POSTGRESQL_HOST',
        'DB_POSTGRESQL_PORT',
        'DB_POSTGRESQL_USERNAME',
        'DB_POSTGRESQL_PASSWORD',
        'DB_POSTGRESQL_DATABASE',
        'DB_TDENGINE_HOST',
        'DB_TDENGINE_PORT',
        'DB_TDENGINE_USERNAME',
        'DB_TDENGINE_PASSWORD',
        'DB_TDENGINE_DATABASE',
        'POSTGRESQL_HOST',
        'POSTGRESQL_PORT',
        'POSTGRESQL_USER',
        'POSTGRESQL_PASSWORD',
        'POSTGRESQL_DATABASE',
        'TDENGINE_HOST',
        'TDENGINE_PORT',
        'TDENGINE_USER',
        'TDENGINE_PASSWORD',
        'TDENGINE_DATABASE',
    ]:
        monkeypatch.delenv(key, raising=False)


def test_database_config_accepts_standard_env_names(monkeypatch) -> None:
    _clear_database_env(monkeypatch)
    module = _load_module()
    monkeypatch.setenv('POSTGRESQL_HOST', 'pg-host')
    monkeypatch.setenv('POSTGRESQL_PORT', '55432')
    monkeypatch.setenv('POSTGRESQL_USER', 'pg-user')
    monkeypatch.setenv('POSTGRESQL_PASSWORD', 'pg-pass')
    monkeypatch.setenv('POSTGRESQL_DATABASE', 'pg-db')
    monkeypatch.setenv('TDENGINE_HOST', 'td-host')
    monkeypatch.setenv('TDENGINE_PORT', '6041')
    monkeypatch.setenv('TDENGINE_USER', 'td-user')
    monkeypatch.setenv('TDENGINE_PASSWORD', 'td-pass')
    monkeypatch.setenv('TDENGINE_DATABASE', 'td-db')

    config = module.DatabaseConfig()

    assert config.postgresql_host == 'pg-host'
    assert config.postgresql_port == 55432
    assert config.postgresql_username == 'pg-user'
    assert config.postgresql_password == 'pg-pass'
    assert config.postgresql_database == 'pg-db'
    assert config.tdengine_host == 'td-host'
    assert config.tdengine_port == 6041
    assert config.tdengine_username == 'td-user'
    assert config.tdengine_password == 'td-pass'
    assert config.tdengine_database == 'td-db'


def test_database_config_prefers_standard_env_names_over_db_prefixed_aliases(monkeypatch) -> None:
    _clear_database_env(monkeypatch)
    module = _load_module()
    monkeypatch.setenv('DB_POSTGRESQL_HOST', 'legacy-pg-host')
    monkeypatch.setenv('DB_POSTGRESQL_PORT', '5433')
    monkeypatch.setenv('DB_POSTGRESQL_USERNAME', 'legacy-pg-user')
    monkeypatch.setenv('DB_POSTGRESQL_PASSWORD', 'legacy-pg-pass')
    monkeypatch.setenv('DB_POSTGRESQL_DATABASE', 'legacy-pg-db')
    monkeypatch.setenv('DB_TDENGINE_HOST', 'legacy-td-host')
    monkeypatch.setenv('DB_TDENGINE_PORT', '6031')
    monkeypatch.setenv('DB_TDENGINE_USERNAME', 'legacy-td-user')
    monkeypatch.setenv('DB_TDENGINE_PASSWORD', 'legacy-td-pass')
    monkeypatch.setenv('DB_TDENGINE_DATABASE', 'legacy-td-db')
    monkeypatch.setenv('POSTGRESQL_HOST', 'pg-host')
    monkeypatch.setenv('POSTGRESQL_PORT', '55432')
    monkeypatch.setenv('POSTGRESQL_USER', 'pg-user')
    monkeypatch.setenv('POSTGRESQL_PASSWORD', 'pg-pass')
    monkeypatch.setenv('POSTGRESQL_DATABASE', 'pg-db')
    monkeypatch.setenv('TDENGINE_HOST', 'td-host')
    monkeypatch.setenv('TDENGINE_PORT', '6041')
    monkeypatch.setenv('TDENGINE_USER', 'td-user')
    monkeypatch.setenv('TDENGINE_PASSWORD', 'td-pass')
    monkeypatch.setenv('TDENGINE_DATABASE', 'td-db')

    config = module.DatabaseConfig()

    assert config.postgresql_host == 'pg-host'
    assert config.postgresql_port == 55432
    assert config.postgresql_username == 'pg-user'
    assert config.postgresql_password == 'pg-pass'
    assert config.postgresql_database == 'pg-db'
    assert config.tdengine_host == 'td-host'
    assert config.tdengine_port == 6041
    assert config.tdengine_username == 'td-user'
    assert config.tdengine_password == 'td-pass'
    assert config.tdengine_database == 'td-db'


def test_database_config_keeps_db_prefixed_fallback(monkeypatch) -> None:
    _clear_database_env(monkeypatch)
    module = _load_module()
    monkeypatch.setenv('DB_POSTGRESQL_HOST', 'legacy-pg-host')
    monkeypatch.setenv('DB_POSTGRESQL_PORT', '5433')
    monkeypatch.setenv('DB_POSTGRESQL_USERNAME', 'legacy-pg-user')
    monkeypatch.setenv('DB_POSTGRESQL_PASSWORD', 'legacy-pg-pass')
    monkeypatch.setenv('DB_POSTGRESQL_DATABASE', 'legacy-pg-db')
    monkeypatch.setenv('DB_TDENGINE_HOST', 'legacy-td-host')
    monkeypatch.setenv('DB_TDENGINE_PORT', '6031')
    monkeypatch.setenv('DB_TDENGINE_USERNAME', 'legacy-td-user')
    monkeypatch.setenv('DB_TDENGINE_PASSWORD', 'legacy-td-pass')
    monkeypatch.setenv('DB_TDENGINE_DATABASE', 'legacy-td-db')

    config = module.DatabaseConfig()

    assert config.postgresql_host == 'legacy-pg-host'
    assert config.postgresql_port == 5433
    assert config.postgresql_username == 'legacy-pg-user'
    assert config.postgresql_password == 'legacy-pg-pass'
    assert config.postgresql_database == 'legacy-pg-db'
    assert config.tdengine_host == 'legacy-td-host'
    assert config.tdengine_port == 6031
    assert config.tdengine_username == 'legacy-td-user'
    assert config.tdengine_password == 'legacy-td-pass'
    assert config.tdengine_database == 'legacy-td-db'
