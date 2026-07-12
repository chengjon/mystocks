#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path("/opt/claude/mystocks_spec")
MODEL_DIR = REPO_ROOT / ".config/opencode/model"
CATALOG_PATH = MODEL_DIR / "model-catalog.json"
PROJECT_OMC_PATH = REPO_ROOT / ".claude/omc.jsonc"
USER_OMC_PATH = Path.home() / ".config/claude-omc/config.jsonc"
OMC_ENV_PATH = MODEL_DIR / "omc-model-stack.env"
CLAUDE_SETTINGS_PATH = Path.home() / ".claude/settings.json"

TIER_MODEL_FILES = {
    "LOW": MODEL_DIR / "omc.tier.low.model",
    "MEDIUM": MODEL_DIR / "omc.tier.medium.model",
    "HIGH": MODEL_DIR / "omc.tier.high.model",
}

AGENT_MODEL_FILES = {
    "omc": MODEL_DIR / "omc.agent.omc.model",
    "architect": MODEL_DIR / "omc.agent.architect.model",
    "planner": MODEL_DIR / "omc.agent.planner.model",
    "critic": MODEL_DIR / "omc.agent.critic.model",
    "analyst": MODEL_DIR / "omc.agent.analyst.model",
    "coordinator": MODEL_DIR / "omc.agent.coordinator.model",
    "executor": MODEL_DIR / "omc.agent.executor.model",
    "researcher": MODEL_DIR / "omc.agent.researcher.model",
    "document-specialist": MODEL_DIR / "omc.agent.document-specialist.model",
    "explore": MODEL_DIR / "omc.agent.explore.model",
    "frontendEngineer": MODEL_DIR / "omc.agent.frontendEngineer.model",
    "documentWriter": MODEL_DIR / "omc.agent.documentWriter.model",
    "multimodalLooker": MODEL_DIR / "omc.agent.multimodalLooker.model",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def merge_dict(target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = dict(target)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def resolve_omo_models(catalog: dict[str, Any]) -> dict[str, str]:
    defaults = catalog.get("defaults", {})
    omo_agents = catalog.get("omo_agents", {})

    main_model = str(defaults.get("main_model", "")).strip()
    small_model = str(defaults.get("small_model", "")).strip()

    sisyphus = str(omo_agents.get("sisyphus", main_model)).strip()
    oracle = str(omo_agents.get("oracle", sisyphus)).strip()
    librarian = str(omo_agents.get("librarian", sisyphus)).strip()
    explore = str(omo_agents.get("explore", small_model or oracle or sisyphus)).strip()
    frontend = str(omo_agents.get("frontend", oracle)).strip()
    document_writer = str(omo_agents.get("document_writer", frontend)).strip()
    multimodal_looker = str(omo_agents.get("multimodal_looker", explore)).strip()

    return {
        "sisyphus": sisyphus,
        "oracle": oracle,
        "librarian": librarian,
        "explore": explore,
        "frontend": frontend,
        "document_writer": document_writer,
        "multimodal_looker": multimodal_looker,
    }


def build_omc_agent_models(omo_models: dict[str, str]) -> dict[str, str]:
    return {
        "omc": omo_models["sisyphus"],
        "planner": omo_models["sisyphus"],
        "coordinator": omo_models["sisyphus"],
        "architect": omo_models["oracle"],
        "critic": omo_models["oracle"],
        "analyst": omo_models["oracle"],
        "executor": omo_models["oracle"],
        "researcher": omo_models["librarian"],
        "document-specialist": omo_models["librarian"],
        "explore": omo_models["explore"],
        "frontendEngineer": omo_models["frontend"],
        "documentWriter": omo_models["document_writer"],
        "multimodalLooker": omo_models["multimodal_looker"],
    }


def build_tier_models(omo_models: dict[str, str]) -> dict[str, str]:
    return {
        "LOW": omo_models["explore"],
        "MEDIUM": omo_models["oracle"],
        "HIGH": omo_models["sisyphus"],
    }


def build_patch(omc_agents: dict[str, str], tier_models: dict[str, str]) -> dict[str, Any]:
    agents_patch: dict[str, Any] = {}
    for agent_name, model_name in omc_agents.items():
        agents_patch[agent_name] = {"model": model_name}

    return {
        "agents": agents_patch,
        "routing": {
            "enabled": True,
            "defaultTier": "MEDIUM",
            "tierModels": tier_models,
        },
    }


def update_config(config_path: Path, patch: dict[str, Any]) -> None:
    existing: dict[str, Any]
    if config_path.exists():
        existing = load_json(config_path)
    else:
        existing = {}
    write_json(config_path, merge_dict(existing, patch))


def write_reference_files(omc_agents: dict[str, str], tier_models: dict[str, str]) -> None:
    for tier, model_name in tier_models.items():
        write_text(TIER_MODEL_FILES[tier], model_name)
    for agent_name, model_name in omc_agents.items():
        if agent_name in AGENT_MODEL_FILES:
            write_text(AGENT_MODEL_FILES[agent_name], model_name)


def write_env_file(omc_agents: dict[str, str], tier_models: dict[str, str]) -> None:
    lines = [
        "# OMC model selection (generated from model-catalog.json)",
        f"OMC_MODEL_LOW={tier_models['LOW']}",
        f"OMC_MODEL_MEDIUM={tier_models['MEDIUM']}",
        f"OMC_MODEL_HIGH={tier_models['HIGH']}",
        "",
        "# Team member model mapping (OMC agents)",
        f"OMC_AGENT_OMC={omc_agents['omc']}",
        f"OMC_AGENT_PLANNER={omc_agents['planner']}",
        f"OMC_AGENT_COORDINATOR={omc_agents['coordinator']}",
        f"OMC_AGENT_ARCHITECT={omc_agents['architect']}",
        f"OMC_AGENT_CRITIC={omc_agents['critic']}",
        f"OMC_AGENT_ANALYST={omc_agents['analyst']}",
        f"OMC_AGENT_EXECUTOR={omc_agents['executor']}",
        f"OMC_AGENT_RESEARCHER={omc_agents['researcher']}",
        f"OMC_AGENT_DOCUMENT_SPECIALIST={omc_agents['document-specialist']}",
        f"OMC_AGENT_EXPLORE={omc_agents['explore']}",
        f"OMC_AGENT_FRONTEND_ENGINEER={omc_agents['frontendEngineer']}",
        f"OMC_AGENT_DOCUMENT_WRITER={omc_agents['documentWriter']}",
        f"OMC_AGENT_MULTIMODAL_LOOKER={omc_agents['multimodalLooker']}",
    ]
    write_text(OMC_ENV_PATH, "\n".join(lines))


def strip_provider_prefix(model_ref: str) -> str:
    model_ref = model_ref.strip()
    if "/" in model_ref:
        return model_ref.split("/", 1)[1].strip()
    return model_ref


def normalize_claude_base_url(base_url: str) -> str:
    base_url = base_url.strip().rstrip("/")
    if base_url.endswith("/v1"):
        return base_url[: -len("/v1")]
    return base_url


def extract_default_endpoint(defaults: dict[str, Any]) -> tuple[str, str]:
    base_url = ""
    api_key = ""

    for key in ("gmn_base_url", "glm_base_url"):
        value = str(defaults.get(key, "")).strip()
        if value:
            base_url = value
            break
    if not base_url:
        for key, value in defaults.items():
            if key.endswith("_base_url"):
                text = str(value).strip()
                if text:
                    base_url = text
                    break

    for key in ("gmn_api_key", "glm_api_key"):
        value = str(defaults.get(key, "")).strip()
        if value:
            api_key = value
            break
    if not api_key:
        for key, value in defaults.items():
            if key.endswith("_api_key"):
                text = str(value).strip()
                if text:
                    api_key = text
                    break

    return base_url, api_key


def build_claude_env_updates(
    defaults: dict[str, Any],
    omc_agents: dict[str, str],
    tier_models: dict[str, str],
) -> dict[str, str]:
    high = strip_provider_prefix(tier_models["HIGH"])
    medium = strip_provider_prefix(tier_models["MEDIUM"])
    low = strip_provider_prefix(tier_models["LOW"])
    subagent = strip_provider_prefix(omc_agents["executor"])

    updates = {
        # Claude Code model aliases (used by model="opus"/"sonnet"/"haiku")
        "ANTHROPIC_DEFAULT_OPUS_MODEL": high,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": medium,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": low,
        # Backward compatibility aliases
        "ANTHROPIC_MODEL": high,
        "ANTHROPIC_REASONING_MODEL": high,
        "CLAUDE_CODE_SUBAGENT_MODEL": subagent,
        # OMC tier defaults read by oh-my-claudecode config loader
        "OMC_MODEL_HIGH": tier_models["HIGH"],
        "OMC_MODEL_MEDIUM": tier_models["MEDIUM"],
        "OMC_MODEL_LOW": tier_models["LOW"],
    }

    base_url, api_key = extract_default_endpoint(defaults)
    if base_url:
        updates["ANTHROPIC_BASE_URL"] = normalize_claude_base_url(base_url)
    if api_key:
        updates["ANTHROPIC_AUTH_TOKEN"] = api_key

    return updates


def update_claude_settings(
    settings_path: Path,
    defaults: dict[str, Any],
    omc_agents: dict[str, str],
    tier_models: dict[str, str],
) -> None:
    existing: dict[str, Any]
    if settings_path.exists():
        existing = load_json(settings_path)
    else:
        existing = {}

    env = existing.get("env")
    if not isinstance(env, dict):
        env = {}

    env_updates = build_claude_env_updates(defaults, omc_agents, tier_models)
    env.update(env_updates)
    existing["env"] = env
    write_json(settings_path, existing)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync OMC models from model-catalog.json omo_agents.")
    parser.add_argument(
        "--catalog",
        default=str(CATALOG_PATH),
        help="Path to model-catalog.json",
    )
    parser.add_argument(
        "--project-config",
        default=str(PROJECT_OMC_PATH),
        help="Path to project OMC config (.claude/omc.jsonc)",
    )
    parser.add_argument(
        "--user-config",
        default=str(USER_OMC_PATH),
        help="Path to user OMC config (~/.config/claude-omc/config.jsonc)",
    )
    parser.add_argument(
        "--write-user-config",
        action="store_true",
        help="Also update user-level OMC config file",
    )
    parser.add_argument(
        "--claude-settings",
        default=str(CLAUDE_SETTINGS_PATH),
        help="Path to Claude Code settings.json",
    )
    parser.add_argument(
        "--skip-claude-settings",
        action="store_true",
        help="Skip syncing model aliases to Claude Code settings.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog_path = Path(args.catalog)
    project_config_path = Path(args.project_config)
    user_config_path = Path(args.user_config)
    claude_settings_path = Path(args.claude_settings)

    catalog = load_json(catalog_path)
    defaults = catalog.get("defaults", {})
    omo_models = resolve_omo_models(catalog)
    omc_agents = build_omc_agent_models(omo_models)
    tier_models = build_tier_models(omo_models)
    patch = build_patch(omc_agents, tier_models)

    update_config(project_config_path, patch)
    if args.write_user_config:
        update_config(user_config_path, patch)

    write_reference_files(omc_agents, tier_models)
    write_env_file(omc_agents, tier_models)
    if not args.skip_claude_settings:
        try:
            update_claude_settings(claude_settings_path, defaults, omc_agents, tier_models)
        except PermissionError as exc:
            print(f"Warning: could not update Claude settings at {claude_settings_path}: {exc}")


if __name__ == "__main__":
    main()
