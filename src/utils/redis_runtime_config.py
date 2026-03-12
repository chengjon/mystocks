from __future__ import annotations

import os
from typing import Any, Dict


REDIS_ROLE_DEFAULTS = {
    'app_cache': 1,
    'monitoring_events': 0,
    'tooling_maintenance': 0,
    'celery_broker': 0,
    'celery_result': 1,
}

REDIS_ROLE_ENV_VARS = {
    'app_cache': 'REDIS_APP_CACHE_DB',
    'monitoring_events': 'REDIS_MONITORING_DB',
    'tooling_maintenance': 'REDIS_TOOLING_DB',
    'celery_broker': 'REDIS_CELERY_BROKER_DB',
    'celery_result': 'REDIS_CELERY_RESULT_DB',
}


DEFAULT_REDIS_HOST = 'localhost'
DEFAULT_REDIS_PORT = 6379


def _normalize_secret(value: str | None) -> str | None:
    if value is None or value == '':
        return None
    return value


def get_redis_db_for_role(role: str) -> int:
    """Resolve the Redis DB number for a logical runtime role."""
    if role not in REDIS_ROLE_DEFAULTS:
        raise ValueError(f'Unsupported redis role: {role}')

    role_env = REDIS_ROLE_ENV_VARS[role]
    if role_env in os.environ:
        return int(os.environ[role_env])

    if 'REDIS_DB' in os.environ:
        return int(os.environ['REDIS_DB'])

    return REDIS_ROLE_DEFAULTS[role]


def get_redis_host(default: str = DEFAULT_REDIS_HOST) -> str:
    return os.getenv('REDIS_HOST', default)


def get_redis_port(default: int = DEFAULT_REDIS_PORT) -> int:
    return int(os.getenv('REDIS_PORT', str(default)))


def get_redis_password() -> str | None:
    return _normalize_secret(os.getenv('REDIS_PASSWORD'))


def get_redis_connection_kwargs(role: str, *, decode_responses: bool = True) -> Dict[str, Any]:
    return {
        'host': get_redis_host(),
        'port': get_redis_port(),
        'db': get_redis_db_for_role(role),
        'password': get_redis_password(),
        'decode_responses': decode_responses,
    }
