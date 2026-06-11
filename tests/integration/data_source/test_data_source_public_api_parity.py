from __future__ import annotations

from pathlib import Path

import yaml

from src.core.data_source.closure_policy import build_registry_closure_policy


def _load_yaml(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def test_legacy_adapter_priority_is_translated_to_registry_seed_policy():
    policy = build_registry_closure_policy(
        registry=_load_yaml("config/data_sources_registry.yaml"),
        adapter_priority_config=_load_yaml("config/adapter_priority_config.yaml"),
    )

    assert policy.runtime_truth_source == "openstock_runtime"
    assert policy.yaml_registry_role == "seed_or_fallback"
    assert policy.legacy_priority_role == "fallback_seed"
    assert policy.fallback_sources_for_data_category("REALTIME_QUOTES") == (
        "tdx",
        "customer",
        "akshare",
    )
    assert policy.fallback_sources_for_data_category("DAILY_KLINE") == (
        "tdx",
        "akshare",
        "baostock",
    )
    assert policy.fallback_sources_for_data_category("UNKNOWN_CATEGORY") == (
        "tdx",
        "akshare",
        "baostock",
        "tushare",
        "financial",
        "customer",
        "byapi",
    )


def test_openstock_registry_entry_keeps_remote_contract_and_legacy_fallback_seed():
    registry = _load_yaml("config/data_sources_registry.yaml")
    policy = build_registry_closure_policy(
        registry=registry,
        adapter_priority_config=_load_yaml("config/adapter_priority_config.yaml"),
    )
    entry = registry["data_sources"]["openstock_akshare_realtime_quotes"]

    route_policy = policy.route_policy_for_entry(entry)

    assert "openstock_akshare_realtime_quotes" in policy.remote_runtime_entries
    assert route_policy == {
        "primary_source": "openstock",
        "data_category": "REALTIME_QUOTES",
        "runtime_transport": "rest",
        "route_path": "/routing/best",
        "fetch_path": "/data/fetch",
        "fallback_seed_sources": ("tdx", "customer", "akshare"),
    }


def test_yaml_registry_remains_seed_fallback_and_does_not_claim_runtime_ownership():
    policy = build_registry_closure_policy(
        registry=_load_yaml("config/data_sources_registry.yaml"),
        adapter_priority_config=_load_yaml("config/adapter_priority_config.yaml"),
    )

    assert policy.runtime_truth_source != "yaml_registry"
    assert policy.yaml_registry_role == "seed_or_fallback"
    assert policy.retired_paths == ()
    assert policy.compatibility_wrappers_retained is True
