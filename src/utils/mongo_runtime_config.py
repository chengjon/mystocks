from __future__ import annotations

import os
from typing import Any, Dict, Tuple
from urllib.parse import quote_plus


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
    return os.getenv('MONGODB_ROOT_USERNAME') or None


def get_mongo_password() -> str | None:
    return _normalize_secret(os.getenv('MONGODB_ROOT_PASSWORD'))


def get_mongo_database(default: str = DEFAULT_MONGODB_DATABASE) -> str:
    return os.getenv('MONGODB_DATABASE', default)


def get_mongo_auth_source(default: str = DEFAULT_MONGODB_AUTH_SOURCE) -> str:
    return os.getenv('MONGODB_AUTH_SOURCE', default)


def get_mongo_connection_uri() -> str | None:
    for key in ('MAESTRO_COLLAB_MONGO_URI', 'COLLAB_MONGO_URI', 'MONGODB_URI', 'MONGO_URI'):
        value = os.getenv(key)
        if value:
            return value
    return None


def build_mongo_connection_uri(*, default_database: str = 'admin') -> str:
    explicit_uri = get_mongo_connection_uri()
    if explicit_uri:
        return explicit_uri

    host = get_mongo_host()
    port = get_mongo_port()
    username = get_mongo_username()
    password = get_mongo_password()
    auth_source = get_mongo_auth_source()

    auth_prefix = ''
    if username:
        auth_prefix = quote_plus(username)
        if password:
            auth_prefix = f'{auth_prefix}:{quote_plus(password)}'
        auth_prefix = f'{auth_prefix}@'

    return f'mongodb://{auth_prefix}{host}:{port}/{default_database}?authSource={quote_plus(auth_source)}'


def get_mongo_connection_kwargs(*, server_selection_timeout_ms: int | None = None) -> Dict[str, Any]:
    mongo_uri = get_mongo_connection_uri()
    if mongo_uri:
        kwargs: Dict[str, Any] = {
            'host': mongo_uri,
        }
    else:
        kwargs = {
            'host': get_mongo_host(),
            'port': get_mongo_port(),
            'username': get_mongo_username(),
            'password': get_mongo_password(),
            'authSource': get_mongo_auth_source(),
        }
    if server_selection_timeout_ms is not None:
        kwargs['serverSelectionTimeoutMS'] = server_selection_timeout_ms
    return kwargs
