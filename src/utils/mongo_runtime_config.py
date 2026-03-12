from __future__ import annotations

import os
from typing import Any, Dict, Tuple


DEFAULT_MONGODB_HOST = 'localhost'
DEFAULT_MONGODB_PORT = 27017
DEFAULT_MONGODB_DATABASE = 'mystocks'
DEFAULT_MONGODB_AUTH_SOURCE = 'admin'


def _normalize_secret(value: str | None) -> str | None:
    if value is None or value == '':
        return None
    return value


def _split_legacy_host_port(raw_value: str | None) -> Tuple[str | None, int | None]:
    if not raw_value:
        return None, None
    if ':' not in raw_value:
        return raw_value, None
    host, port = raw_value.rsplit(':', 1)
    return host.strip() or None, int(port)


def get_mongo_host(default: str = DEFAULT_MONGODB_HOST) -> str:
    if os.getenv('MONGODB_HOST'):
        return os.getenv('MONGODB_HOST', default)
    host, _ = _split_legacy_host_port(os.getenv('MONGODB_IP'))
    return host or default


def get_mongo_port(default: int = DEFAULT_MONGODB_PORT) -> int:
    if os.getenv('MONGODB_PORT'):
        return int(os.getenv('MONGODB_PORT', str(default)))
    _, port = _split_legacy_host_port(os.getenv('MONGODB_IP'))
    return port or default


def get_mongo_username() -> str | None:
    return os.getenv('MONGODB_ROOT_USERNAME') or os.getenv('USERNAME') or None


def get_mongo_password() -> str | None:
    return _normalize_secret(os.getenv('MONGODB_ROOT_PASSWORD') or os.getenv('PASSWORD'))


def get_mongo_database(default: str = DEFAULT_MONGODB_DATABASE) -> str:
    return os.getenv('MONGODB_DATABASE', default)


def get_mongo_auth_source(default: str = DEFAULT_MONGODB_AUTH_SOURCE) -> str:
    return os.getenv('MONGODB_AUTH_SOURCE', default)


def get_mongo_connection_kwargs(*, server_selection_timeout_ms: int | None = None) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {
        'host': get_mongo_host(),
        'port': get_mongo_port(),
        'username': get_mongo_username(),
        'password': get_mongo_password(),
        'authSource': get_mongo_auth_source(),
    }
    if server_selection_timeout_ms is not None:
        kwargs['serverSelectionTimeoutMS'] = server_selection_timeout_ms
    return kwargs
