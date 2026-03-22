from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = PROJECT_ROOT / 'web/backend/app/core/config.py'


REQUIRED_ENV = {
    'TDENGINE_HOST': 'localhost',
    'TDENGINE_PORT': '6030',
    'TDENGINE_USER': 'root',
    'TDENGINE_PASSWORD': 'your-tdengine-password',
    'TDENGINE_DATABASE': 'market_data',
    'POSTGRESQL_HOST': 'localhost',
    'POSTGRESQL_PORT': '5438',
    'POSTGRESQL_USER': 'postgres',
    'POSTGRESQL_PASSWORD': 'password',
    'POSTGRESQL_DATABASE': 'mystocks',
    'JWT_SECRET_KEY': 'secret',
    'BACKEND_PORT': '8020',
    'BACKEND_BACKUP_PORT': '8021',
}


OPTIONAL_KEYS = [
    'REDIS_HOST', 'REDIS_PORT', 'REDIS_DB', 'REDIS_APP_CACHE_DB', 'REDIS_CELERY_BROKER_DB', 'REDIS_CELERY_RESULT_DB',
    'MONGODB_HOST', 'MONGODB_PORT', 'MONGODB_ROOT_USERNAME', 'MONGODB_ROOT_PASSWORD', 'MONGODB_DATABASE',
    'MONGODB_AUTH_SOURCE', 'MONGODB_IP', 'USERNAME', 'PASSWORD',
]


def _load_backend_config_module(module_name: str = 'test_web_backend_runtime_settings_module'):
    from unittest.mock import patch

    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    with patch('pydantic_settings.sources.providers.dotenv.DotEnvSettingsSource._read_env_files', return_value={}):
        spec.loader.exec_module(module)
    return module


def _set_minimum_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in OPTIONAL_KEYS:
        monkeypatch.delenv(key, raising=False)
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)


def test_settings_prefers_standard_mongo_env_names(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_minimum_env(monkeypatch)
    monkeypatch.setenv('MONGODB_HOST', 'mongo-host')
    monkeypatch.setenv('MONGODB_PORT', '27019')
    monkeypatch.setenv('MONGODB_ROOT_USERNAME', 'root-user')
    monkeypatch.setenv('MONGODB_ROOT_PASSWORD', 'root-pass')
    monkeypatch.setenv('MONGODB_DATABASE', 'mystocks_docs')
    monkeypatch.setenv('MONGODB_AUTH_SOURCE', 'admin')
    monkeypatch.setenv('MONGODB_IP', 'legacy-host:27017')
    monkeypatch.setenv('USERNAME', 'legacy-user')
    monkeypatch.setenv('PASSWORD', 'legacy-pass')

    module = _load_backend_config_module('test_web_backend_runtime_settings_standard')

    assert module.settings.mongodb_host == 'mongo-host'
    assert module.settings.mongodb_port == 27019
    assert module.settings.mongodb_root_username == 'root-user'
    assert module.settings.mongodb_root_password == 'root-pass'
    assert module.settings.mongodb_database == 'mystocks_docs'
    assert module.settings.mongodb_auth_source == 'admin'
    assert module.settings.mongodb_runtime_host == 'mongo-host'
    assert module.settings.mongodb_runtime_port == 27019
    assert module.settings.mongodb_connection_kwargs == {
        'host': 'mongo-host',
        'port': 27019,
        'username': 'root-user',
        'password': 'root-pass',
        'authSource': 'admin',
    }


def test_settings_ignore_generic_username_password_for_mongo_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_minimum_env(monkeypatch)
    monkeypatch.setenv('MONGODB_IP', 'localhost:27017')
    monkeypatch.setenv('USERNAME', 'mongo')
    monkeypatch.setenv('PASSWORD', 'secret')

    module = _load_backend_config_module('test_web_backend_runtime_settings_legacy')

    assert module.settings.mongodb_runtime_host == 'localhost'
    assert module.settings.mongodb_runtime_port == 27017
    assert module.settings.mongodb_root_username == ''
    assert module.settings.mongodb_root_password == ''
    assert module.settings.mongodb_auth_source == 'admin'


def test_settings_default_celery_urls_use_role_specific_redis_dbs(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_minimum_env(monkeypatch)
    monkeypatch.setenv('REDIS_HOST', 'redis-host')
    monkeypatch.setenv('REDIS_PORT', '6380')
    monkeypatch.setenv('REDIS_DB', '9')
    monkeypatch.setenv('REDIS_CELERY_BROKER_DB', '2')
    monkeypatch.setenv('REDIS_CELERY_RESULT_DB', '4')

    module = _load_backend_config_module('test_web_backend_runtime_settings_redis')

    assert module.settings.redis_db == 9
    assert module.settings.redis_celery_broker_db == 2
    assert module.settings.redis_celery_result_db == 4
    assert module.settings.default_celery_broker_url == 'redis://redis-host:6380/2'
    assert module.settings.default_celery_result_backend == 'redis://redis-host:6380/4'



def test_settings_exposes_role_specific_redis_db_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_minimum_env(monkeypatch)
    monkeypatch.setenv('REDIS_HOST', 'redis-host')
    monkeypatch.setenv('REDIS_PORT', '6380')
    monkeypatch.setenv('REDIS_DB', '9')
    monkeypatch.setenv('REDIS_APP_CACHE_DB', '3')
    monkeypatch.setenv('REDIS_MONITORING_DB', '4')
    monkeypatch.setenv('REDIS_TOOLING_DB', '5')

    module = _load_backend_config_module('test_web_backend_runtime_settings_role_fields')

    assert module.settings.redis_db == 9
    assert module.settings.redis_app_cache_db == 3
    assert module.settings.redis_monitoring_db == 4
    assert module.settings.redis_tooling_db == 5



def test_settings_celery_urls_fall_back_to_role_defaults_when_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_minimum_env(monkeypatch)
    monkeypatch.setenv('REDIS_HOST', 'redis-host')
    monkeypatch.setenv('REDIS_PORT', '6380')
    monkeypatch.setenv('REDIS_CELERY_BROKER_DB', '2')
    monkeypatch.setenv('REDIS_CELERY_RESULT_DB', '4')
    monkeypatch.delenv('CELERY_BROKER_URL', raising=False)
    monkeypatch.delenv('CELERY_RESULT_BACKEND', raising=False)

    module = _load_backend_config_module('test_web_backend_runtime_settings_celery_defaults')

    assert module.settings.celery_broker_url == 'redis://redis-host:6380/2'
    assert module.settings.celery_result_backend == 'redis://redis-host:6380/4'
