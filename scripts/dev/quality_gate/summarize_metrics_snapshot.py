#!/usr/bin/env python3
"""Summarize a Prometheus metrics snapshot into a compact JSON report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


LABEL_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:\\.|[^"])*)"')


def parse_labels(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}

    labels: dict[str, str] = {}
    for key, value in LABEL_RE.findall(raw):
        labels[key] = value
    return labels


def parse_metrics_text(text: str) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            metric_with_labels, raw_value = line.rsplit(maxsplit=1)
        except ValueError:
            continue

        try:
            value = float(raw_value)
        except ValueError:
            continue

        if "{" in metric_with_labels and metric_with_labels.endswith("}"):
            name, raw_labels = metric_with_labels.split("{", 1)
            raw_labels = raw_labels[:-1]
        else:
            name = metric_with_labels
            raw_labels = None

        metrics.append(
            {
                "name": name,
                "labels": parse_labels(raw_labels),
                "value": value,
            }
        )
    return metrics


def build_snapshot(
    metrics_text: str,
    health_payload: dict[str, Any],
    baseline_metrics_text: str | None = None,
) -> dict[str, Any]:
    metrics = parse_metrics_text(metrics_text)
    baseline_metrics = parse_metrics_text(baseline_metrics_text) if baseline_metrics_text else []

    def values_for(name: str) -> list[dict[str, Any]]:
        return [item for item in metrics if item["name"] == name]

    def baseline_values_for(name: str) -> list[dict[str, Any]]:
        return [item for item in baseline_metrics if item["name"] == name]

    def sum_metric(name: str) -> float:
        return round(sum(item["value"] for item in values_for(name)), 4)

    def max_metric(name: str) -> float:
        selected = values_for(name)
        if not selected:
            return 0.0
        return round(max(item["value"] for item in selected), 4)

    def keyed_metric_map(items: list[dict[str, Any]]) -> dict[tuple[str, tuple[tuple[str, str], ...]], float]:
        return {
            (
                item["name"],
                tuple(sorted(item["labels"].items())),
            ): item["value"]
            for item in items
        }

    def diff_sum_metric(name: str) -> float:
        current_total = round(sum(item["value"] for item in values_for(name)), 4)
        baseline_total = round(sum(item["value"] for item in baseline_values_for(name)), 4)
        return round(max(current_total - baseline_total, 0.0), 4)

    api_health = {
        item["labels"].get("service", "unknown"): item["value"]
        for item in values_for("mystocks_api_health_status")
    }
    db_connections = {
        item["labels"].get("database", "unknown"): item["value"]
        for item in values_for("mystocks_db_connections_active")
    }
    slow_request_endpoints = sorted(
        [
            {
                "endpoint": item["labels"].get("endpoint", "unknown"),
                "method": item["labels"].get("method", "unknown"),
                "count": round(item["value"], 4),
            }
            for item in values_for("slow_http_requests_total")
            if item["value"] > 0
        ],
        key=lambda item: (-item["count"], item["method"], item["endpoint"]),
    )
    baseline_map = keyed_metric_map(baseline_metrics)
    slow_request_endpoints_delta = sorted(
        [
            {
                "endpoint": item["labels"].get("endpoint", "unknown"),
                "method": item["labels"].get("method", "unknown"),
                "count": round(
                    max(
                        item["value"]
                        - baseline_map.get(
                            (item["name"], tuple(sorted(item["labels"].items()))),
                            0.0,
                        ),
                        0.0,
                    ),
                    4,
                ),
            }
            for item in values_for("slow_http_requests_total")
            if item["value"]
            - baseline_map.get(
                (item["name"], tuple(sorted(item["labels"].items()))),
                0.0,
            )
            > 0
        ],
        key=lambda item: (-item["count"], item["method"], item["endpoint"]),
    )

    cache_hits = sum_metric("mystocks_cache_hits_total")
    cache_misses = sum_metric("mystocks_cache_misses_total")
    cache_total = cache_hits + cache_misses
    cache_hit_ratio = round(cache_hits / cache_total, 4) if cache_total else None

    return {
        "metrics_health": health_payload,
        "prometheus_snapshot": {
            "http_requests_total": sum_metric("http_requests_total"),
            "http_requests_total_delta": diff_sum_metric("http_requests_total"),
            "slow_http_requests_total": sum_metric("slow_http_requests_total"),
            "slow_http_requests_total_delta": diff_sum_metric("slow_http_requests_total"),
            "active_requests_max": max_metric("http_requests_active"),
            "requests_in_progress_max": max_metric("http_requests_in_progress"),
            "process_resident_memory_bytes": max_metric("process_resident_memory_bytes"),
            "process_cpu_seconds_total": max_metric("process_cpu_seconds_total"),
            "cache_hits_total": cache_hits,
            "cache_misses_total": cache_misses,
            "cache_hit_ratio": cache_hit_ratio,
            "api_health_status": api_health,
            "db_connections_active": db_connections,
            "slow_request_endpoints": slow_request_endpoints,
            "slow_request_endpoints_delta": slow_request_endpoints_delta,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a Prometheus metrics snapshot")
    parser.add_argument("--metrics-file", required=True, help="Path to raw /metrics output")
    parser.add_argument("--baseline-metrics-file", help="Optional path to raw /metrics output captured before the run")
    parser.add_argument("--health-file", required=True, help="Path to /api/metrics/health JSON output")
    parser.add_argument("--output", required=True, help="Path to output JSON report")
    args = parser.parse_args()

    metrics_text = Path(args.metrics_file).read_text(encoding="utf-8")
    baseline_metrics_text = (
        Path(args.baseline_metrics_file).read_text(encoding="utf-8") if args.baseline_metrics_file else None
    )
    health_payload = json.loads(Path(args.health_file).read_text(encoding="utf-8"))
    snapshot = build_snapshot(metrics_text, health_payload, baseline_metrics_text=baseline_metrics_text)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
