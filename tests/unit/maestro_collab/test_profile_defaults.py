from __future__ import annotations

from scripts.runtime.maestro_collab import build_parser
from src.services.maestro.profiles import mystocks


def test_mystocks_profile_exposes_collab_control_plane_defaults() -> None:
    defaults = mystocks.COLLAB_CONTROL_PLANE_DEFAULTS

    assert defaults["backend"] == "sqlite"
    assert defaults["mongo_db"] == "mystocks_coord"
    assert defaults["cutover_mode"] == "project-first"
    assert defaults["promote_new_tasks_to_mongo"] is True


def test_maestro_collab_parser_uses_profile_defaults_for_mongo_settings() -> None:
    args = build_parser().parse_args(["work", "list"])

    assert args.mongo_uri == mystocks.COLLAB_CONTROL_PLANE_DEFAULTS["mongo_uri"]
    assert args.mongo_db == mystocks.COLLAB_CONTROL_PLANE_DEFAULTS["mongo_db"]


def test_maestro_collab_parser_prefers_env_mongo_defaults(monkeypatch) -> None:
    monkeypatch.setenv("MAESTRO_COLLAB_MONGO_URI", "mongodb://coord-user:coord-pass@mongo-host:27017/admin?authSource=admin")
    monkeypatch.setenv("MAESTRO_COLLAB_MONGO_DB", "coord_runtime")

    args = build_parser().parse_args(["work", "list"])

    assert args.mongo_uri == "mongodb://coord-user:coord-pass@mongo-host:27017/admin?authSource=admin"
    assert args.mongo_db == "coord_runtime"
