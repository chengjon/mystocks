from __future__ import annotations

import json
from pathlib import Path

from scripts.opencode import sync_opencode_model_catalog as sync


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _minimal_catalog() -> dict:
    return {
        "external_models": {
            "fucai": [],
            "fucai-gpt": [],
            "fucai-claude": [],
            "fucai-mini": [],
        }
    }


def test_apply_common_sets_server_port_default_when_missing() -> None:
    config: dict = {}

    sync.apply_common(config, _minimal_catalog())

    assert config["server"]["port"] == 11000


def test_apply_common_guards_invalid_server_port_with_default() -> None:
    config: dict = {"server": {"port": "invalid"}}

    sync.apply_common(config, _minimal_catalog())

    assert config["server"]["port"] == 11000


def test_apply_common_keeps_valid_server_port() -> None:
    config: dict = {"server": {"port": 12000}}

    sync.apply_common(config, _minimal_catalog())

    assert config["server"]["port"] == 12000


def test_main_updates_model_files_from_catalog(tmp_path: Path, monkeypatch) -> None:
    model_defaults_dir = tmp_path / "model_defaults"
    model_defaults_dir.mkdir(parents=True)

    catalog_path = model_defaults_dir / "model-catalog.json"
    project_opencode_path = tmp_path / "opencode.json"
    global_opencode_path = tmp_path / "global-opencode.json"
    omo_path = tmp_path / "oh-my-opencode.noco.json"

    main_model_file = model_defaults_dir / "main.model"
    small_model_file = model_defaults_dir / "small.model"
    base_url_file = model_defaults_dir / "fucai.base_url"
    api_key_file = model_defaults_dir / "fucai.api_key"

    main_model_file.write_text("cpap-oai/old-main\n", encoding="utf-8")
    small_model_file.write_text("opencode/old-small\n", encoding="utf-8")
    base_url_file.write_text("https://old.example/v1\n", encoding="utf-8")
    api_key_file.write_text("old-key\n", encoding="utf-8")

    agent_files = {
        "sisyphus": model_defaults_dir / "omo.sisyphus.model",
        "oracle": model_defaults_dir / "omo.oracle.model",
        "librarian": model_defaults_dir / "omo.librarian.model",
        "explore": model_defaults_dir / "omo.explore.model",
        "frontend": model_defaults_dir / "omo.frontend.model",
        "document_writer": model_defaults_dir / "omo.document_writer.model",
        "multimodal_looker": model_defaults_dir / "omo.multimodal_looker.model",
    }
    for agent_file in agent_files.values():
        agent_file.write_text("cpap-oai/old-agent\n", encoding="utf-8")

    catalog = {
        "defaults": {
            "main_model": "fucai-claude/claude-opus-4-6",
            "small_model": "opencode/glm-4.7-free",
            "fucai_base_url": "https://fucaixie.xyz/v1",
            "fucai_api_key": "sk-test-fucai",
        },
        "enabled_providers": ["opencode", "fucai", "fucai-gpt", "fucai-claude", "fucai-mini"],
        "opencode_free_models": ["opencode/glm-4.7-free"],
        "external_models": {
            "fucai": ["grok-4.20-beta"],
            "fucai-gpt": ["gpt-5.3-codex", "gpt-5.3"],
            "fucai-claude": ["claude-opus-4-6", "claude-opus-4-5"],
            "fucai-mini": ["MiniMax 2.5"],
        },
        "omo_agents": {
            "sisyphus": "fucai-claude/claude-opus-4-6",
            "oracle": "fucai-gpt/gpt-5.3-codex",
            "librarian": "fucai-claude/claude-opus-4-5",
            "explore": "fucai/grok-4.20-beta",
            "frontend": "fucai-gpt/gpt-5.3",
            "document_writer": "fucai-gpt/gpt-5.3",
            "multimodal_looker": "fucai/grok-4-heavy",
        },
    }
    _write_json(catalog_path, catalog)

    _write_json(
        global_opencode_path,
        {
            "$schema": "https://opencode.ai/config.json",
            "provider": {"cpap-gemini": {"name": "cpap-gemini", "models": {"gemini-3-pro": {"name": "gemini"}}}},
        },
    )

    _write_json(
        omo_path,
        {
            "$schema": "https://opencode.ai/config.json",
            "provider": {},
            "oh_my_opencode": {
                "agents": {
                    "sisyphus": {"description": "planner"},
                }
            },
        },
    )

    monkeypatch.setattr(sync, "CATALOG_PATH", catalog_path)
    monkeypatch.setattr(sync, "PROJECT_OPENCODE_PATH", project_opencode_path)
    monkeypatch.setattr(sync, "GLOBAL_OPENCODE_PATH", global_opencode_path)
    monkeypatch.setattr(sync, "OMO_PATH", omo_path)
    monkeypatch.setattr(sync, "MODEL_MAIN_FILE_REF", f"{{file:{main_model_file}}}")
    monkeypatch.setattr(sync, "MODEL_SMALL_FILE_REF", f"{{file:{small_model_file}}}")
    monkeypatch.setattr(sync, "FUCAI_BASE_URL_FILE_REF", f"{{file:{base_url_file}}}")
    monkeypatch.setattr(sync, "FUCAI_API_KEY_FILE_REF", f"{{file:{api_key_file}}}")
    monkeypatch.setattr(
        sync,
        "AGENT_MODEL_FILE_REFS",
        {name: f"{{file:{path}}}" for name, path in agent_files.items()},
    )

    sync.main()

    assert main_model_file.read_text(encoding="utf-8").strip() == "fucai-claude/claude-opus-4-6"
    assert small_model_file.read_text(encoding="utf-8").strip() == "opencode/glm-4.7-free"
    assert base_url_file.read_text(encoding="utf-8").strip() == "https://fucaixie.xyz/v1"
    assert api_key_file.read_text(encoding="utf-8").strip() == "sk-test-fucai"

    assert agent_files["sisyphus"].read_text(encoding="utf-8").strip() == "fucai-claude/claude-opus-4-6"
    assert agent_files["oracle"].read_text(encoding="utf-8").strip() == "fucai-gpt/gpt-5.3-codex"
    assert agent_files["multimodal_looker"].read_text(encoding="utf-8").strip() == "fucai/grok-4-heavy"

    project = json.loads(project_opencode_path.read_text(encoding="utf-8"))
    assert project["server"]["port"] == 11000

    omo = json.loads(omo_path.read_text(encoding="utf-8"))
    assert omo["oh_my_opencode"]["agents"]["oracle"]["model"] == f"{{file:{agent_files['oracle']}}}"
