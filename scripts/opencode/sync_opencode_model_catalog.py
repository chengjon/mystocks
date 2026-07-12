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
GMN_BASE_URL_FILE_REF = "{file:/opt/claude/mystocks_spec/.config/opencode/model/gmn.base_url}"
GLM_BASE_URL_FILE_REF = "{file:/opt/claude/mystocks_spec/.config/opencode/model/glm.base_url}"
GMN_API_KEY_FILE_REF = "{file:~/.config/opencode/secrets/gmn_key}"
HOME_GLM_API_KEY_FILE_REF = "{file:~/.config/opencode/secrets/glm_key}"
LOCAL_GLM_API_KEY_FILE_REF = "{file:/opt/claude/mystocks_spec/.config/opencode/model/glm.api_key}"

AGENT_MODEL_FILE_REFS = {
    "sisyphus": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.sisyphus.model}",
    "oracle": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.oracle.model}",
    "librarian": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.librarian.model}",
    "explore": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.explore.model}",
    "frontend": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.frontend.model}",
    "document_writer": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.document_writer.model}",
    "multimodal_looker": "{file:/opt/claude/mystocks_spec/.config/opencode/model/omo.multimodal_looker.model}",
}

GMN_MODEL_DEFS: dict[str, dict[str, Any]] = {
    "gpt-5-codex": {
        "name": "GPT-5 Codex",
        "limit": {"context": 400000, "output": 128000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}},
    },
    "gpt-5.1-codex": {
        "name": "GPT-5.1 Codex",
        "limit": {"context": 400000, "output": 128000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}},
    },
    "gpt-5.1-codex-max": {
        "name": "GPT-5.1 Codex Max",
        "limit": {"context": 400000, "output": 128000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}},
    },
    "gpt-5.1-codex-mini": {
        "name": "GPT-5.1 Codex Mini",
        "limit": {"context": 400000, "output": 128000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}},
    },
    "gpt-5.2": {
        "name": "GPT-5.2",
        "limit": {"context": 400000, "output": 128000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}, "xhigh": {}},
    },
    "gpt-5.4": {
        "name": "GPT-5.4",
        "limit": {"context": 1050000, "output": 128000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}, "xhigh": {}},
    },
    "gpt-5.3-codex-spark": {
        "name": "GPT-5.3 Codex Spark",
        "limit": {"context": 128000, "output": 32000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}, "xhigh": {}},
    },
    "gpt-5.3-codex": {
        "name": "GPT-5.3 Codex",
        "limit": {"context": 400000, "output": 128000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}, "xhigh": {}},
    },
    "gpt-5.2-codex": {
        "name": "GPT-5.2 Codex",
        "limit": {"context": 400000, "output": 128000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}, "xhigh": {}},
    },
    "codex-mini-latest": {
        "name": "Codex Mini",
        "limit": {"context": 200000, "output": 100000},
        "options": {"store": False},
        "variants": {"low": {}, "medium": {}, "high": {}},
    },
}

GLM_MODEL_DEFS: dict[str, dict[str, Any]] = {
    "glm-5": {
        "name": "GLM-5",
        "thinking": True,
    },
}

MAIN_PLUGIN_LIST = [
    "oh-my-opencode@3.11.2",
    "@tarquinen/opencode-dcp@latest",
    "opencode-antigravity-auth@1.6.0",
]

OMO_PLUGIN_LIST = [
    "oh-my-opencode@3.11.2",
    "@tarquinen/opencode-dcp@latest",
]

OMO_XHIGH_MODEL = "gmn/gpt-5.4"
OMO_XHIGH_VARIANT = "xhigh"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_file_ref(file_ref: str) -> Path:
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


def resolve_glm_api_key_file_ref() -> str:
    # Prefer the standard global secret location when it already exists.
    if parse_file_ref(HOME_GLM_API_KEY_FILE_REF).exists():
        return HOME_GLM_API_KEY_FILE_REF
    return LOCAL_GLM_API_KEY_FILE_REF


def join_csv(values: list[str]) -> str:
    return ",".join(v.strip() for v in values if v and v.strip())


def sync_catalog_to_env_file(catalog: dict[str, Any]) -> None:
    defaults = catalog.get("defaults", {})
    external = catalog.get("external_models", {})
    omo_agents = catalog.get("omo_agents", {})

    env_path = CATALOG_PATH.parent / "model-stack.env"
    lines = [
        "# OpenCode default model selection",
        f"OPENCODE_DEFAULT_MODEL={defaults.get('main_model', '')}",
        f"OPENCODE_SMALL_MODEL={defaults.get('small_model', '')}",
        f"GMN_BASE_URL={defaults.get('gmn_base_url', '')}",
        f"GLM_BASE_URL={defaults.get('glm_base_url', '')}",
        "",
        "# OpenCode free models (ordered)",
        f"OPENCODE_FREE_MODELS={join_csv(catalog.get('opencode_free_models', []))}",
        "",
        "# External endpoint models (ordered)",
        f"GMN_MODELS={join_csv(external.get('gmn', []))}",
        f"GLM_MODELS={join_csv(external.get('glm', []))}",
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
    if "gmn_base_url" in defaults:
        write_model_ref_file(GMN_BASE_URL_FILE_REF, str(defaults["gmn_base_url"]))
    if "glm_base_url" in defaults:
        write_model_ref_file(GLM_BASE_URL_FILE_REF, str(defaults["glm_base_url"]))

    for agent_name, model in omo_agents.items():
        if agent_name in AGENT_MODEL_FILE_REFS:
            write_model_ref_file(AGENT_MODEL_FILE_REFS[agent_name], str(model))


def infer_model_entry(model_id: str) -> dict[str, Any]:
    lowered = model_id.lower()
    entry: dict[str, Any] = {"name": model_id}

    if any(keyword in lowered for keyword in ["thinking", "codex", "glm-5"]):
        entry["thinking"] = True

    if any(keyword in lowered for keyword in ["vl", "imagine", "vision", "image", "video"]):
        entry["attachment"] = True

    return entry


def build_models(provider_id: str, model_ids: list[str]) -> dict[str, dict[str, Any]]:
    models: dict[str, dict[str, Any]] = {}
    provider_defs = {"gmn": GMN_MODEL_DEFS, "glm": GLM_MODEL_DEFS}.get(provider_id, {})
    for model_id in model_ids:
        models[model_id] = dict(provider_defs.get(model_id, infer_model_entry(model_id)))
    return models


def provider_file_refs(provider_id: str) -> tuple[str, str]:
    if provider_id == "gmn":
        return GMN_BASE_URL_FILE_REF, GMN_API_KEY_FILE_REF
    if provider_id == "glm":
        return GLM_BASE_URL_FILE_REF, resolve_glm_api_key_file_ref()
    raise ValueError(f"Unsupported provider: {provider_id}")


def desired_omo_variant(model_name: str) -> str | None:
    if model_name == OMO_XHIGH_MODEL:
        return OMO_XHIGH_VARIANT
    return None


def build_provider_configs(catalog: dict[str, Any]) -> dict[str, Any]:
    external = catalog.get("external_models", {})
    providers: dict[str, Any] = {}
    provider_packages = {
        # GPT/Codex models behind gmn now require the OpenAI Responses API.
        "gmn": "@ai-sdk/openai",
        "glm": "@ai-sdk/openai-compatible",
    }

    for provider_id in ("gmn", "glm"):
        base_url_ref, api_key_ref = provider_file_refs(provider_id)
        providers[provider_id] = {
            "npm": provider_packages[provider_id],
            "name": provider_id,
            "options": {
                "baseURL": base_url_ref,
                "apiKey": api_key_ref,
                "timeout": 300000,
            },
            "models": build_models(provider_id, external.get(provider_id, [])),
        }

    providers["opencode"] = {
        "whitelist": [
            model.split("/", 1)[1] for model in catalog.get("opencode_free_models", []) if model.startswith("opencode/")
        ],
    }
    return providers


def apply_common(config: dict[str, Any], catalog: dict[str, Any], plugin_list: list[str] | None = None) -> None:
    config["enabled_providers"] = catalog["enabled_providers"]
    config["model"] = MODEL_MAIN_FILE_REF
    config["small_model"] = MODEL_SMALL_FILE_REF
    config["provider"] = build_provider_configs(catalog)
    if plugin_list is not None:
        config["plugin"] = plugin_list


def apply_omo_specific(config: dict[str, Any], catalog: dict[str, Any]) -> None:
    omo = config.setdefault("oh_my_opencode", {})
    agents = omo.setdefault("agents", {})
    omo_agents = catalog.get("omo_agents", {})

    for agent_name, model_ref in AGENT_MODEL_FILE_REFS.items():
        agent = agents.setdefault(agent_name, {})
        agent["model"] = model_ref
        desired_variant = desired_omo_variant(str(omo_agents.get(agent_name, "")))
        if desired_variant is None:
            agent.pop("variant", None)
        else:
            agent["variant"] = desired_variant

    background_task = omo.setdefault("background_task", {})
    background_task["providerConcurrency"] = {
        "opencode": 12,
        "gmn": 4,
        "glm": 6,
    }

    model_concurrency: dict[str, int] = {}
    for model in catalog.get("opencode_free_models", []):
        model_concurrency[model] = 10

    for model_ref in sorted(set(str(v) for v in omo_agents.values())):
        if model_ref.startswith("gmn/"):
            model_concurrency[model_ref] = 2
        elif model_ref.startswith("glm/"):
            model_concurrency[model_ref] = 4

    background_task["modelConcurrency"] = model_concurrency

    for agent in agents.values():
        model = str(agent.get("model", ""))
        if not model or model.startswith("{file:"):
            continue
        if not (model.startswith("gmn/") or model.startswith("glm/") or model.startswith("opencode/")):
            agent["model"] = AGENT_MODEL_FILE_REFS["librarian"]


def main() -> None:
    catalog = load_json(CATALOG_PATH)
    sync_catalog_to_ref_files(catalog)
    sync_catalog_to_env_file(catalog)

    if GLOBAL_OPENCODE_PATH.exists():
        opencode_config = load_json(GLOBAL_OPENCODE_PATH)
    else:
        opencode_config = {"$schema": "https://opencode.ai/config.json"}
    apply_common(opencode_config, catalog, MAIN_PLUGIN_LIST)
    write_json(PROJECT_OPENCODE_PATH, opencode_config)

    omo_config = load_json(OMO_PATH)
    apply_common(omo_config, catalog, OMO_PLUGIN_LIST)
    apply_omo_specific(omo_config, catalog)
    write_json(OMO_PATH, omo_config)


if __name__ == "__main__":
    main()
