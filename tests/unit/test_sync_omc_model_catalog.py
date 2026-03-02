from __future__ import annotations

import json
from pathlib import Path

from scripts.opencode import sync_omc_model_catalog as sync


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_sync_omc_models_generates_project_config_and_refs(tmp_path: Path, monkeypatch) -> None:
    model_dir = tmp_path / "model"
    model_dir.mkdir(parents=True)

    catalog_path = model_dir / "model-catalog.json"
    project_omc_path = tmp_path / ".claude" / "omc.jsonc"
    user_omc_path = tmp_path / ".config" / "claude-omc" / "config.jsonc"
    claude_settings_path = tmp_path / ".claude-home" / "settings.json"
    env_path = model_dir / "omc-model-stack.env"

    tier_files = {
        "LOW": model_dir / "omc.tier.low.model",
        "MEDIUM": model_dir / "omc.tier.medium.model",
        "HIGH": model_dir / "omc.tier.high.model",
    }
    agent_files = {
        "omc": model_dir / "omc.agent.omc.model",
        "architect": model_dir / "omc.agent.architect.model",
        "planner": model_dir / "omc.agent.planner.model",
        "critic": model_dir / "omc.agent.critic.model",
        "analyst": model_dir / "omc.agent.analyst.model",
        "coordinator": model_dir / "omc.agent.coordinator.model",
        "executor": model_dir / "omc.agent.executor.model",
        "researcher": model_dir / "omc.agent.researcher.model",
        "document-specialist": model_dir / "omc.agent.document-specialist.model",
        "explore": model_dir / "omc.agent.explore.model",
        "frontendEngineer": model_dir / "omc.agent.frontendEngineer.model",
        "documentWriter": model_dir / "omc.agent.documentWriter.model",
        "multimodalLooker": model_dir / "omc.agent.multimodalLooker.model",
    }

    catalog = {
        "defaults": {
            "main_model": "fucai-claude/claude-opus-4-6",
            "small_model": "opencode/glm-4.7-free",
            "fucai_base_url": "https://fucaixie.example.com/v1",
            "fucai_api_key": "sk-test-fucai",
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
    _write_json(project_omc_path, {"features": {"parallelExecution": False}})
    _write_json(
        claude_settings_path,
        {
            "enabledPlugins": {"oh-my-claudecode@omc": True},
            "env": {"KEEP_ME": "1", "ANTHROPIC_DEFAULT_SONNET_MODEL": "kiro-claude-sonnet-4-6-agentic"},
        },
    )

    monkeypatch.setattr(sync, "CATALOG_PATH", catalog_path)
    monkeypatch.setattr(sync, "PROJECT_OMC_PATH", project_omc_path)
    monkeypatch.setattr(sync, "USER_OMC_PATH", user_omc_path)
    monkeypatch.setattr(sync, "OMC_ENV_PATH", env_path)
    monkeypatch.setattr(sync, "TIER_MODEL_FILES", tier_files)
    monkeypatch.setattr(sync, "AGENT_MODEL_FILES", agent_files)
    monkeypatch.setattr(
        sync,
        "parse_args",
        lambda: type(
            "Args",
            (),
            {
                "catalog": str(catalog_path),
                "project_config": str(project_omc_path),
                "user_config": str(user_omc_path),
                "write_user_config": True,
                "claude_settings": str(claude_settings_path),
                "skip_claude_settings": False,
            },
        )(),
    )

    sync.main()

    project_config = json.loads(project_omc_path.read_text(encoding="utf-8"))
    user_config = json.loads(user_omc_path.read_text(encoding="utf-8"))

    assert project_config["features"]["parallelExecution"] is False
    assert project_config["agents"]["executor"]["model"] == "fucai-gpt/gpt-5.3-codex"
    assert project_config["agents"]["explore"]["model"] == "fucai/grok-4.20-beta"
    assert project_config["routing"]["tierModels"] == {
        "LOW": "fucai/grok-4.20-beta",
        "MEDIUM": "fucai-gpt/gpt-5.3-codex",
        "HIGH": "fucai-claude/claude-opus-4-6",
    }

    assert user_config["agents"]["documentWriter"]["model"] == "fucai-gpt/gpt-5.3"
    assert user_config["agents"]["multimodalLooker"]["model"] == "fucai/grok-4-heavy"

    assert tier_files["LOW"].read_text(encoding="utf-8").strip() == "fucai/grok-4.20-beta"
    assert tier_files["MEDIUM"].read_text(encoding="utf-8").strip() == "fucai-gpt/gpt-5.3-codex"
    assert tier_files["HIGH"].read_text(encoding="utf-8").strip() == "fucai-claude/claude-opus-4-6"
    assert agent_files["researcher"].read_text(encoding="utf-8").strip() == "fucai-claude/claude-opus-4-5"

    env = env_path.read_text(encoding="utf-8")
    assert "OMC_MODEL_HIGH=fucai-claude/claude-opus-4-6" in env
    assert "OMC_AGENT_EXECUTOR=fucai-gpt/gpt-5.3-codex" in env

    claude_settings = json.loads(claude_settings_path.read_text(encoding="utf-8"))
    claude_env = claude_settings["env"]
    assert claude_settings["enabledPlugins"]["oh-my-claudecode@omc"] is True
    assert claude_env["KEEP_ME"] == "1"
    assert claude_env["ANTHROPIC_DEFAULT_OPUS_MODEL"] == "claude-opus-4-6"
    assert claude_env["ANTHROPIC_DEFAULT_SONNET_MODEL"] == "gpt-5.3-codex"
    assert claude_env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] == "grok-4.20-beta"
    assert claude_env["CLAUDE_CODE_SUBAGENT_MODEL"] == "gpt-5.3-codex"
    assert claude_env["OMC_MODEL_HIGH"] == "fucai-claude/claude-opus-4-6"
    assert claude_env["OMC_MODEL_MEDIUM"] == "fucai-gpt/gpt-5.3-codex"
    assert claude_env["OMC_MODEL_LOW"] == "fucai/grok-4.20-beta"
    assert claude_env["ANTHROPIC_BASE_URL"] == "https://fucaixie.example.com"
    assert claude_env["ANTHROPIC_AUTH_TOKEN"] == "sk-test-fucai"
