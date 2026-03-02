#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MODEL_DIR = Path("/opt/claude/mystocks_spec/.config/opencode/model")
CATALOG_PATH = MODEL_DIR / "model-catalog.json"
PROJECT_OPENCODE_PATH = Path("/opt/claude/mystocks_spec/opencode.json")
GLOBAL_OPENCODE_PATH = Path.home() / ".config/opencode/opencode.json"
OMO_PATH = Path("/opt/claude/mystocks_spec/.config/oh-my-opencode.noco.json")

MODEL_MAIN_FILE_REF = "{file:/opt/claude/mystocks_spec/.config/opencode/model/main.model}"
MODEL_SMALL_FILE_REF = "{file:/opt/claude/mystocks_spec/.config/opencode/model/small.model}"
FUCAI_BASE_URL_FILE_REF = "{file:/opt/claude/mystocks_spec/.config/opencode/model/fucai.base_url}"
FUCAI_API_KEY_FILE_REF = "{file:/opt/claude/mystocks_spec/.config/opencode/model/fucai.api_key}"

AGENT_MODEL_FILE_REFS = {
    "sisyphus": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.sisyphus.model}",
    "oracle": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.oracle.model}",
    "librarian": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.librarian.model}",
    "explore": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.explore.model}",
    "frontend": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.frontend.model}",
    "document_writer": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.document_writer.model}",
    "multimodal_looker": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.multimodal_looker.model}",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_file_ref(file_ref: str) -> Path:
    """Resolve {file:/path/to/file} references used by OpenCode."""
    if not file_ref.startswith("{file:") or not file_ref.endswith("}"):
        raise ValueError(f"Unsupported file ref: {file_ref}")
    raw_path = file_ref[len("{file:") : -1]
    if raw_path.startswith("~/"):
        return Path(raw_path).expanduser()
    return Path(raw_path)


def write_model_ref_file(file_ref: str, value: str) -> None:
    path = parse_file_ref(file_ref)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.strip() + "\n", encoding="utf-8")


def join_csv(values: list[str]) -> str:
    return ",".join(v.strip() for v in values if v and v.strip())


def sync_catalog_to_env_file(catalog: dict[str, Any]) -> None:
    defaults = catalog.get("defaults", {})
    external = catalog.get("external_models", {})
    omo_agents = catalog.get("omo_agents", {})

    catalog_path = CATALOG_PATH
    env_path = catalog_path.parent / "model-stack.env"

    lines = [
        "# OpenCode default model selection",
        f"OPENCODE_DEFAULT_MODEL={defaults.get('main_model', '')}",
        f"OPENCODE_SMALL_MODEL={defaults.get('small_model', '')}",
        f"FUCAI_BASE_URL={defaults.get('fucai_base_url', '')}",
        "",
        "# OpenCode free models (ordered)",
        f"OPENCODE_FREE_MODELS={join_csv(catalog.get('opencode_free_models', []))}",
        "",
        "# External endpoint models (ordered, GEMINI excluded, fucai groups)",
        f"FUCAI_GPT_MODELS={join_csv(external.get('fucai-gpt', []))}",
        f"FUCAI_CLAUDE_MODELS={join_csv(external.get('fucai-claude', []))}",
        f"FUCAI_MINI_MODELS={join_csv(external.get('fucai-mini', []))}",
        f"FUCAI_MODELS={join_csv(external.get('fucai', []))}",
        "",
        "# oh-my-opencode agents (ordered by priority)",
        f"OMO_AGENT_SISYPHUS={omo_agents.get('sisyphus', '')}",
        f"OMO_AGENT_ORACLE={omo_agents.get('oracle', '')}",
        f"OMO_AGENT_LIBRARIAN={omo_agents.get('librarian', '')}",
        f"OMO_AGENT_EXPLORE={omo_agents.get('explore', '')}",
        f"OMO_AGENT_FRONTEND={omo_agents.get('frontend', '')}",
        f"OMO_AGENT_DOCUMENT_WRITER={omo_agents.get('document_writer', '')}",
        f"OMO_AGENT_MULTIMODAL_LOOKER={omo_agents.get('multimodal_looker', '')}",
    ]
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_catalog_to_ref_files(catalog: dict[str, Any]) -> None:
    defaults = catalog.get("defaults", {})
    omo_agents = catalog.get("omo_agents", {})

    if "main_model" in defaults:
        write_model_ref_file(MODEL_MAIN_FILE_REF, str(defaults["main_model"]))
    if "small_model" in defaults:
        write_model_ref_file(MODEL_SMALL_FILE_REF, str(defaults["small_model"]))
    base_url = defaults.get("fucai_base_url")
    if base_url:
        write_model_ref_file(FUCAI_BASE_URL_FILE_REF, str(base_url))
    if "fucai_api_key" in defaults:
        write_model_ref_file(FUCAI_API_KEY_FILE_REF, str(defaults["fucai_api_key"]))

    for agent_name, model in omo_agents.items():
        if agent_name in AGENT_MODEL_FILE_REFS:
            write_model_ref_file(AGENT_MODEL_FILE_REFS[agent_name], str(model))


def infer_model_entry(model_id: str) -> dict[str, Any]:
    lowered = model_id.lower()
    entry: dict[str, Any] = {"name": model_id}

    if any(keyword in lowered for keyword in ["thinking", "codex", "deepseek-r1"]):
        entry["thinking"] = True

    if any(keyword in lowered for keyword in ["vl", "imagine", "vision", "image", "video"]):
        entry["attachment"] = True

    return entry


def build_models(model_ids: list[str]) -> dict[str, dict[str, Any]]:
    models: dict[str, dict[str, Any]] = {}
    for model_id in model_ids:
        models[model_id] = infer_model_entry(model_id)
    return models


def upsert_provider(config: dict[str, Any], provider_id: str, npm: str, set_cache_key: bool = False) -> None:
    providers = config.setdefault("provider", {})
    provider = providers.setdefault(provider_id, {})
    provider["npm"] = npm
    provider["name"] = provider_id

    options: dict[str, Any] = {
        "baseURL": FUCAI_BASE_URL_FILE_REF,
        "apiKey": FUCAI_API_KEY_FILE_REF,
        "timeout": 300000,
    }
    if set_cache_key:
        options["setCacheKey"] = True
    provider["options"] = options


def apply_provider_models(config: dict[str, Any], catalog: dict[str, Any]) -> None:
    upsert_provider(config, "fucai", "@ai-sdk/openai-compatible")
    upsert_provider(config, "fucai-gpt", "@ai-sdk/openai", set_cache_key=True)
    upsert_provider(config, "fucai-claude", "@ai-sdk/anthropic")
    upsert_provider(config, "fucai-mini", "@ai-sdk/openai-compatible")

    external = catalog["external_models"]
    config["provider"]["fucai"]["models"] = build_models(external.get("fucai", []))
    config["provider"]["fucai-gpt"]["models"] = build_models(external.get("fucai-gpt", []))
    config["provider"]["fucai-claude"]["models"] = build_models(external.get("fucai-claude", []))
    config["provider"]["fucai-mini"]["models"] = build_models(external.get("fucai-mini", []))

    # Remove legacy provider groups to prevent merge contamination.
    for legacy in ["cpap", "cpap-oai", "cpap-claude", "cpap-gemini", "cpap-mini", "google"]:
        config["provider"].pop(legacy, None)


def apply_common(config: dict[str, Any], catalog: dict[str, Any]) -> None:
    config["enabled_providers"] = catalog.get(
        "enabled_providers", ["opencode", "fucai", "fucai-gpt", "fucai-claude", "fucai-mini"]
    )
    config["model"] = MODEL_MAIN_FILE_REF
    config["small_model"] = MODEL_SMALL_FILE_REF
    apply_provider_models(config, catalog)


def apply_omo_specific(config: dict[str, Any], catalog: dict[str, Any]) -> None:
    omo = config.setdefault("oh_my_opencode", {})
    agents = omo.setdefault("agents", {})
    omo_agents = catalog.get("omo_agents", {})

    # Keep existing descriptions/capabilities while externalizing model bindings.
    for agent_name, model_ref in AGENT_MODEL_FILE_REFS.items():
        agent = agents.setdefault(agent_name, {})
        agent["model"] = model_ref

    background_task = omo.setdefault("background_task", {})
    background_task["providerConcurrency"] = {
        "opencode": 12,
        "fucai": 8,
        "fucai-gpt": 4,
        "fucai-claude": 4,
        "fucai-mini": 6,
    }

    model_concurrency: dict[str, int] = {}
    for model in catalog["opencode_free_models"]:
        model_concurrency[model] = 10

    # Prefer selected OMO agents for external model concurrency budget.
    for model_ref in sorted(set(str(v) for v in omo_agents.values())):
        if model_ref.startswith("fucai-claude/"):
            model_concurrency[model_ref] = 2
        elif model_ref.startswith("fucai-gpt/"):
            model_concurrency[model_ref] = 2
        elif model_ref.startswith("fucai-mini/"):
            model_concurrency[model_ref] = 3
        elif model_ref.startswith("fucai/"):
            # Keep heavyweight xAI-compatible models conservative by default.
            model_concurrency[model_ref] = 2

    background_task["modelConcurrency"] = model_concurrency

    # Ensure no GEMINI/legacy-group references remain in OMO agent bindings.
    for agent in agents.values():
        model = str(agent.get("model", ""))
        lowered = model.lower()
        if "gemini" in lowered or lowered.startswith("cpap"):
            agent["model"] = AGENT_MODEL_FILE_REFS["librarian"]


def main() -> None:
    catalog = load_json(CATALOG_PATH)
    sync_catalog_to_ref_files(catalog)
    sync_catalog_to_env_file(catalog)

    # Generate project-level config (higher precedence than global config).
    if GLOBAL_OPENCODE_PATH.exists():
        opencode_config = load_json(GLOBAL_OPENCODE_PATH)
    else:
        opencode_config = {"$schema": "https://opencode.ai/config.json"}
    apply_common(opencode_config, catalog)
    write_json(PROJECT_OPENCODE_PATH, opencode_config)

    omo_config = load_json(OMO_PATH)
    apply_common(omo_config, catalog)
    apply_omo_specific(omo_config, catalog)
    write_json(OMO_PATH, omo_config)


if __name__ == "__main__":
    main()
