from __future__ import annotations

import os
from typing import Any, Dict


DEFAULT_MONGO_HOST = "localhost"
DEFAULT_MONGO_PORT = 27017
DEFAULT_MONGO_DATABASE = "mystocks"
DEFAULT_MONGO_AUTH_SOURCE = "admin"


def _normalize_secret(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    return value


def _parse_legacy_host_port(value: str | None) -> tuple[str | None, int | None]:
    if not value:
        return None, None

    if ":" not in value:
        return value, None

    host, port = value.rsplit(":", 1)
    if not host:
        host = DEFAULT_MONGO_HOST

    try:
        return host, int(port)
    except ValueError:
        return host, DEFAULT_MONGO_PORT


def get_mongo_host(default: str = DEFAULT_MONGO_HOST) -> str:
    env_host = os.getenv("MONGODB_HOST")
    if env_host:
        return env_host

    legacy_host, _ = _parse_legacy_host_port(os.getenv("MONGODB_IP"))
    return legacy_host or default


def get_mongo_port(default: int = DEFAULT_MONGO_PORT) -> int:
    env_port = os.getenv("MONGODB_PORT")
    if env_port:
        return int(env_port)

    _, legacy_port = _parse_legacy_host_port(os.getenv("MONGODB_IP"))
    return legacy_port or default


def get_mongo_username() -> str | None:
    return _normalize_secret(os.getenv("MONGODB_ROOT_USERNAME") or os.getenv("USERNAME"))


def get_mongo_password() -> str | None:
    return _normalize_secret(os.getenv("MONGODB_ROOT_PASSWORD") or os.getenv("PASSWORD"))


def get_mongo_database(default: str = DEFAULT_MONGO_DATABASE) -> str:
    return os.getenv("MONGODB_DATABASE", default)


def get_mongo_auth_source(default: str = DEFAULT_MONGO_AUTH_SOURCE) -> str:
    return os.getenv("MONGODB_AUTH_SOURCE", default)


def get_mongo_connection_kwargs(server_selection_timeout_ms: int | None = None) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {
        "host": get_mongo_host(),
        "port": get_mongo_port(),
        "authSource": get_mongo_auth_source(),
    }

    username = get_mongo_username()
    password = get_mongo_password()
    if username is not None:
        kwargs["username"] = username
    if password is not None:
        kwargs["password"] = password
    if server_selection_timeout_ms is not None:
        kwargs["serverSelectionTimeoutMS"] = server_selection_timeout_ms

    return kwargs
