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
            "gmn": [],
            "glm": [],
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
    model_dir = tmp_path / "model"
    model_dir.mkdir(parents=True)

    catalog_path = model_dir / "model-catalog.json"
    project_opencode_path = tmp_path / "opencode.json"
    global_opencode_path = tmp_path / "global-opencode.json"
    omo_path = tmp_path / "oh-my-opencode.noco.json"

    main_model_file = model_dir / "main.model"
    small_model_file = model_dir / "small.model"
    gmn_base_url_file = model_dir / "gmn.base_url"
    glm_base_url_file = model_dir / "glm.base_url"
    glm_api_key_file = model_dir / "glm.api_key"

    main_model_file.write_text("legacy/main\n", encoding="utf-8")
    small_model_file.write_text("legacy/small\n", encoding="utf-8")
    gmn_base_url_file.write_text("https://old-gmn.example/v1\n", encoding="utf-8")
    glm_base_url_file.write_text("https://old-glm.example/v1\n", encoding="utf-8")
    glm_api_key_file.write_text("glm-test-key\n", encoding="utf-8")

    agent_files = {
        "sisyphus": model_dir / "omo.sisyphus.model",
        "oracle": model_dir / "omo.oracle.model",
        "librarian": model_dir / "omo.librarian.model",
        "explore": model_dir / "omo.explore.model",
        "frontend": model_dir / "omo.frontend.model",
        "document_writer": model_dir / "omo.document_writer.model",
        "multimodal_looker": model_dir / "omo.multimodal_looker.model",
    }
    for agent_file in agent_files.values():
        agent_file.write_text("legacy/agent\n", encoding="utf-8")

    catalog = {
        "defaults": {
            "main_model": "gmn/gpt-5.4",
            "small_model": "glm/glm-5",
            "gmn_base_url": "https://gmn.chuangzuoli.com/v1",
            "glm_base_url": "https://open.bigmodel.cn/api/coding/paas/v4",
        },
        "enabled_providers": ["opencode", "gmn", "glm"],
        "opencode_free_models": [
            "opencode/big-pickle",
            "opencode/gpt-5-nano",
            "opencode/minimax-m2.5-free",
        ],
        "external_models": {
            "gmn": ["gpt-5.4"],
            "glm": ["glm-5"],
        },
        "omo_agents": {
            "sisyphus": "gmn/gpt-5.4",
            "oracle": "gmn/gpt-5.4",
            "librarian": "glm/glm-5",
            "explore": "glm/glm-5",
            "frontend": "gmn/gpt-5.4",
            "document_writer": "glm/glm-5",
            "multimodal_looker": "gmn/gpt-5.4",
        },
    }
    _write_json(catalog_path, catalog)

    _write_json(
        global_opencode_path,
        {
            "$schema": "https://opencode.ai/config.json",
            "provider": {"legacy-provider": {"name": "legacy-provider"}},
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
    monkeypatch.setattr(sync, "GMN_BASE_URL_FILE_REF", f"{{file:{gmn_base_url_file}}}")
    monkeypatch.setattr(sync, "GLM_BASE_URL_FILE_REF", f"{{file:{glm_base_url_file}}}")
    monkeypatch.setattr(sync, "HOME_GLM_API_KEY_FILE_REF", f"{{file:{model_dir / 'missing-glm-key'}}}")
    monkeypatch.setattr(sync, "LOCAL_GLM_API_KEY_FILE_REF", f"{{file:{glm_api_key_file}}}")
    monkeypatch.setattr(
        sync,
        "AGENT_MODEL_FILE_REFS",
        {name: f"{{file:{path}}}" for name, path in agent_files.items()},
    )

    sync.main()

    assert main_model_file.read_text(encoding="utf-8").strip() == "gmn/gpt-5.4"
    assert small_model_file.read_text(encoding="utf-8").strip() == "glm/glm-5"
    assert gmn_base_url_file.read_text(encoding="utf-8").strip() == "https://gmn.chuangzuoli.com/v1"
    assert glm_base_url_file.read_text(encoding="utf-8").strip() == "https://open.bigmodel.cn/api/coding/paas/v4"

    assert agent_files["sisyphus"].read_text(encoding="utf-8").strip() == "gmn/gpt-5.4"
    assert agent_files["librarian"].read_text(encoding="utf-8").strip() == "glm/glm-5"

    project = json.loads(project_opencode_path.read_text(encoding="utf-8"))
    assert project["server"]["port"] == 11000
    assert sorted(project["provider"].keys()) == ["glm", "gmn", "opencode"]
    assert project["provider"]["gmn"]["npm"] == "@ai-sdk/openai"
    assert project["provider"]["glm"]["npm"] == "@ai-sdk/openai-compatible"
    assert project["provider"]["glm"]["options"]["apiKey"] == f"{{file:{glm_api_key_file}}}"
    assert "legacy-provider" not in project["provider"]

    omo = json.loads(omo_path.read_text(encoding="utf-8"))
    assert omo["oh_my_opencode"]["agents"]["oracle"]["model"] == f"{{file:{agent_files['oracle']}}}"
