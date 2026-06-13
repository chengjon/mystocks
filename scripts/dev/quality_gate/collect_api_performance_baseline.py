#!/usr/bin/env python3
"""Collect a machine-readable API performance baseline from a benchmark artifact."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "analysis" / "api-performance-baseline.json"
DEFAULT_SOURCE = PROJECT_ROOT / "reports" / "analysis" / "api-performance-gate" / "20260423-115543" / "benchmark.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _endpoint_key(item: dict[str, Any]) -> str:
    return f"{item.get('method', 'GET')} {item.get('endpoint', '')}".strip()


def build_api_performance_baseline(benchmark_payload: dict[str, Any], benchmark_path: Path) -> dict[str, Any]:
    endpoints = benchmark_payload.get("endpoints", [])
    endpoint_map = {
        _endpoint_key(item): {
            "endpoint": item.get("endpoint"),
            "method": item.get("method"),
            "p95_ms": item.get("p95_ms"),
            "avg_ms": item.get("avg_ms"),
            "error_rate_percent": item.get("error_rate_percent"),
            "status_codes": item.get("status_codes", {}),
        }
        for item in endpoints
    }
    slowest = max(endpoints, key=lambda item: float(item.get("p95_ms", 0.0)), default=None)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric_version": "v1",
        "source_benchmark_json": str(benchmark_path.resolve()),
        "source_generated_at": benchmark_payload.get("generated_at"),
        "base_url": benchmark_payload.get("base_url"),
        "concurrent_users": benchmark_payload.get("concurrent_users"),
        "iterations": benchmark_payload.get("iterations"),
        "slo_status": "COMPLIANT" if benchmark_payload.get("slo_status", {}).get("compliant") else "NON-COMPLIANT",
        "endpoint_count": benchmark_payload.get("summary", {}).get("endpoint_count", len(endpoints)),
        "overall_avg_ms": benchmark_payload.get("summary", {}).get("overall_avg_ms"),
        "overall_p95_ms": benchmark_payload.get("summary", {}).get("overall_p95_ms"),
        "workload_classes": benchmark_payload.get("workload_classes", {}),
        "slowest_endpoint": {
            "key": _endpoint_key(slowest) if slowest else None,
            "p95_ms": slowest.get("p95_ms") if slowest else None,
            "error_rate_percent": slowest.get("error_rate_percent") if slowest else None,
        },
        "endpoints": endpoint_map,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect API performance baseline from benchmark.json")
    parser.add_argument(
        "--benchmark-json",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Path to benchmark.json source artifact",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON path",
    )
    args = parser.parse_args()

    benchmark_path = args.benchmark_json.resolve()
    benchmark_payload = _read_json(benchmark_path)
    baseline = build_api_performance_baseline(benchmark_payload, benchmark_path)

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[api-performance-baseline] written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
