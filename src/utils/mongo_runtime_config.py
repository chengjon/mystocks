from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Dict, Tuple
from urllib.parse import quote_plus, urlparse

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure


DEFAULT_MONGODB_HOST = "localhost"
DEFAULT_MONGODB_PORT = 27017
DEFAULT_MONGODB_DATABASE = "mystocks"
DEFAULT_MONGODB_AUTH_SOURCE = "admin"


def _normalize_secret(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    return value


def _split_legacy_host_port(raw_value: str | None) -> Tuple[str | None, int | None]:
    if not raw_value:
        return None, None
    if ":" not in raw_value:
        return raw_value, None
    host, port = raw_value.rsplit(":", 1)
    return host.strip() or None, int(port)


def get_mongo_host(default: str = DEFAULT_MONGODB_HOST) -> str:
    if os.getenv("MONGODB_HOST"):
        return os.getenv("MONGODB_HOST", default)
    host, _ = _split_legacy_host_port(os.getenv("MONGODB_IP"))
    return host or default


def get_mongo_port(default: int = DEFAULT_MONGODB_PORT) -> int:
    if os.getenv("MONGODB_PORT"):
        return int(os.getenv("MONGODB_PORT", str(default)))
    _, port = _split_legacy_host_port(os.getenv("MONGODB_IP"))
    return port or default


def get_mongo_username() -> str | None:
    return os.getenv("MONGODB_ROOT_USERNAME") or None


def get_mongo_password() -> str | None:
    return _normalize_secret(os.getenv("MONGODB_ROOT_PASSWORD"))


def get_mongo_database(default: str = DEFAULT_MONGODB_DATABASE) -> str:
    return os.getenv("MONGODB_DATABASE", default)


def get_mongo_auth_source(default: str = DEFAULT_MONGODB_AUTH_SOURCE) -> str:
    return os.getenv("MONGODB_AUTH_SOURCE", default)


def get_mongo_connection_uri() -> str | None:
    for key in ("MAESTRO_COLLAB_MONGO_URI", "COLLAB_MONGO_URI", "MONGODB_URI", "MONGO_URI"):
        value = os.getenv(key)
        if value:
            return value
    return None


def get_runtime_mongo_uri_default(default: str) -> str:
    return get_mongo_connection_uri() or default


def get_runtime_mongo_db_default(default: str) -> str:
    return os.getenv("MAESTRO_COLLAB_MONGO_DB", default)


def get_effective_runtime_mongo_uri(mongo_uri: str | None, *, default_database: str = "admin") -> str:
    if mongo_uri:
        return inject_local_docker_auth_into_uri(mongo_uri)
    return inject_local_docker_auth_into_uri(build_mongo_connection_uri(default_database=default_database))


def build_mongo_connection_uri(*, default_database: str = "admin") -> str:
    explicit_uri = get_mongo_connection_uri()
    if explicit_uri:
        return explicit_uri

    host = get_mongo_host()
    port = get_mongo_port()
    username = get_mongo_username()
    password = get_mongo_password()
    auth_source = get_mongo_auth_source()

    auth_prefix = ""
    if username:
        auth_prefix = quote_plus(username)
        if password:
            auth_prefix = f"{auth_prefix}:{quote_plus(password)}"
        auth_prefix = f"{auth_prefix}@"

    return f"mongodb://{auth_prefix}{host}:{port}/{default_database}?authSource={quote_plus(auth_source)}"


def read_local_docker_mongo_env(container_name: str = "mystocks-mongodb") -> dict[str, str]:
    try:
        result = subprocess.run(
            ["docker", "inspect", container_name, "--format", "{{json .Config.Env}}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return {}

    if result.returncode != 0 or not result.stdout.strip():
        return {}

    try:
        env_entries = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}

    if not isinstance(env_entries, list):
        return {}

    env_map: dict[str, str] = {}
    for entry in env_entries:
        if not isinstance(entry, str) or "=" not in entry:
            continue
        key, value = entry.split("=", 1)
        env_map[key] = value
    return env_map


def inject_local_docker_auth_into_uri(mongo_uri: str, *, container_name: str = "mystocks-mongodb") -> str:
    parsed = urlparse(mongo_uri)
    if parsed.username or parsed.password:
        return mongo_uri
    if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        return mongo_uri

    env_map = read_local_docker_mongo_env(container_name=container_name)
    username = env_map.get("MONGO_INITDB_ROOT_USERNAME")
    password = env_map.get("MONGO_INITDB_ROOT_PASSWORD")
    if not username or not password:
        return mongo_uri

    hostname = parsed.hostname or "localhost"
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    port = f":{parsed.port}" if parsed.port else ""
    netloc = f"{quote_plus(username)}:{quote_plus(password)}@{hostname}{port}"
    return parsed._replace(netloc=netloc).geturl()


def merge_local_docker_auth_into_connection_kwargs(
    kwargs: Dict[str, Any],
    *,
    container_name: str = "mystocks-mongodb",
) -> Dict[str, Any]:
    host = str(kwargs.get("host") or "")
    username = kwargs.get("username")
    password = kwargs.get("password")

    if username or password:
        return kwargs
    if host.startswith("mongodb://"):
        return kwargs
    if host not in {"localhost", "127.0.0.1", "::1"}:
        return kwargs

    env_map = read_local_docker_mongo_env(container_name=container_name)
    docker_username = env_map.get("MONGO_INITDB_ROOT_USERNAME")
    docker_password = env_map.get("MONGO_INITDB_ROOT_PASSWORD")
    if not docker_username or not docker_password:
        return kwargs

    return {
        **kwargs,
        "username": docker_username,
        "password": docker_password,
        "authSource": str(kwargs.get("authSource") or "admin"),
    }


def is_mongo_auth_error(error: Exception) -> bool:
    if not isinstance(error, OperationFailure):
        return False

    code_name = str((error.details or {}).get("codeName", "")).lower()
    message = str(error).lower()
    return (
        error.code in {13, 18}
        or code_name in {"unauthorized", "authenticationfailed"}
        or any(fragment in message for fragment in ("requires authentication", "authentication failed"))
    )


def build_mongo_auth_runtime_error(subject: str) -> RuntimeError:
    return RuntimeError(
        f"{subject} requires writable credentials. "
        "Provide --mongo-uri, set MAESTRO_COLLAB_MONGO_URI/COLLAB_MONGO_URI/MONGODB_URI/MONGO_URI, "
        "or ensure the local mystocks-mongodb Docker container is reachable."
    )


def build_runtime_mongo_client(
    mongo_uri: str | None,
    *,
    server_selection_timeout_ms: int = 3000,
) -> MongoClient:
    if mongo_uri:
        return MongoClient(inject_local_docker_auth_into_uri(mongo_uri))

    kwargs = merge_local_docker_auth_into_connection_kwargs(
        get_mongo_connection_kwargs(server_selection_timeout_ms=server_selection_timeout_ms)
    )
    return MongoClient(**kwargs)


def build_project_runtime_mongo_client(
    project_root,
    mongo_uri: str | None,
    *,
    server_selection_timeout_ms: int = 3000,
) -> MongoClient:
    if mongo_uri is None:
        load_dotenv(project_root / ".env", override=False)
    return build_runtime_mongo_client(mongo_uri, server_selection_timeout_ms=server_selection_timeout_ms)


def get_mongo_connection_kwargs(*, server_selection_timeout_ms: int | None = None) -> Dict[str, Any]:
    mongo_uri = get_mongo_connection_uri()
    if mongo_uri:
        kwargs: Dict[str, Any] = {
            "host": mongo_uri,
        }
    else:
        kwargs = {
            "host": get_mongo_host(),
            "port": get_mongo_port(),
            "username": get_mongo_username(),
            "password": get_mongo_password(),
            "authSource": get_mongo_auth_source(),
        }
    if server_selection_timeout_ms is not None:
        kwargs["serverSelectionTimeoutMS"] = server_selection_timeout_ms
    return kwargs
