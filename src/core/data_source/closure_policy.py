from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

LEGACY_DATA_CATEGORY_ALIASES = {
    "REALTIME_QUOTES": "realtime_quote",
    "DAILY_KLINE": "daily_kline",
    "FINANCIAL_DATA": "financial_data",
    "TECHNICAL_INDICATORS": "technical_indicators",
    "NEWS_DATA": "news_data",
}


@dataclass(frozen=True)
class RegistryClosurePolicy:
    """Compatibility policy for moving legacy priority semantics to runtime routing."""

    runtime_truth_source: str
    yaml_registry_role: str
    legacy_priority_role: str
    source_order_by_category: Mapping[str, tuple[str, ...]]
    remote_runtime_entries: tuple[str, ...]
    retired_paths: tuple[str, ...] = ()
    compatibility_wrappers_retained: bool = True

    def fallback_sources_for_data_category(self, data_category: str) -> tuple[str, ...]:
        category_key = LEGACY_DATA_CATEGORY_ALIASES.get(data_category.strip().upper(), data_category.strip().lower())
        return self.source_order_by_category.get(
            category_key,
            self.source_order_by_category.get("default", ()),
        )

    def route_policy_for_entry(self, entry: Mapping[str, Any]) -> dict[str, Any]:
        remote_runtime = entry.get("remote_runtime")
        remote_runtime = remote_runtime if isinstance(remote_runtime, Mapping) else {}
        data_category = _text(entry.get("data_category"))
        return {
            "primary_source": _text(entry.get("source_name")),
            "data_category": data_category,
            "runtime_transport": _text(remote_runtime.get("transport")),
            "route_path": _text(remote_runtime.get("route_path")),
            "fetch_path": _text(remote_runtime.get("fetch_path")),
            "fallback_seed_sources": self.fallback_sources_for_data_category(data_category),
        }


def build_registry_closure_policy(
    *,
    registry: Mapping[str, Any],
    adapter_priority_config: Mapping[str, Any],
) -> RegistryClosurePolicy:
    data_sources = registry.get("data_sources")
    data_sources = data_sources if isinstance(data_sources, Mapping) else {}
    return RegistryClosurePolicy(
        runtime_truth_source="openstock_runtime",
        yaml_registry_role="seed_or_fallback",
        legacy_priority_role="fallback_seed",
        source_order_by_category=_normalize_priority_config(adapter_priority_config),
        remote_runtime_entries=tuple(
            name
            for name, entry in data_sources.items()
            if isinstance(entry, Mapping) and _text(entry.get("source_type")) == "remote_runtime"
        ),
    )


def _normalize_priority_config(
    adapter_priority_config: Mapping[str, Any],
) -> dict[str, tuple[str, ...]]:
    normalized: dict[str, tuple[str, ...]] = {}
    for category, sources in adapter_priority_config.items():
        if isinstance(sources, list | tuple):
            normalized[str(category)] = tuple(_text(source) for source in sources)
    return normalized


def _text(value: Any) -> str:
    return str(value or "").strip()
