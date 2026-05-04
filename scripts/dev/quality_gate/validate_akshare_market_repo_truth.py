#!/usr/bin/env python3
"""Validate AkShare market expansion repo-truth against local function availability."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.dev.quality_gate.collect_akshare_market_function_availability import collect_availability
except ModuleNotFoundError:
    from collect_akshare_market_function_availability import collect_availability

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = PROJECT_ROOT / "reports/analysis/akshare-market-repo-truth-gate.json"
DEFAULT_TASKS_PATH = PROJECT_ROOT / "openspec/changes/expand-akshare-data-sources/tasks.md"
DEFAULT_REPO_TRUTH_PATH = PROJECT_ROOT / "docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md"
DEFAULT_REGISTRY_PATH = PROJECT_ROOT / "config/data_sources_registry.yaml"
DEFAULT_ADAPTER_PATH = PROJECT_ROOT / "src/adapters/akshare/market_adapter/stock_sentiment.py"
DEFAULT_ROUTE_PATH = PROJECT_ROOT / "web/backend/app/api/akshare_market/sentiment_monitor.py"
DEFAULT_UNIT_TEST_PATH = PROJECT_ROOT / "tests/unit/adapters/test_akshare_stock_sentiment_incremental.py"
DEFAULT_BACKEND_TEST_PATH = PROJECT_ROOT / "tests/backend/test_akshare_market_additional_routes.py"
DEFAULT_API_FILE_TEST_PATH = PROJECT_ROOT / "tests/api/file_tests/test_akshare_market_api.py"
TASK_LINE_PATTERN = re.compile(r"^- \[(?P<checked>[ xX])\] (?P<task_id>6\.\d+)\s")

DEFAULT_MANIFEST = [
    {
        "task_id": "6.1",
        "function_name": "stock_hot_follow_xq",
        "registry_key": "akshare_stock_hot_follow_xq",
        "adapter_method": "get_stock_hot_follow_xq",
        "route_fragment": "/stock/hot-follow/xq",
        "unit_test_token": "test_get_stock_hot_follow_xq_normalizes_columns",
        "backend_test_token": "test_stock_hot_follow_xq_route_returns_success_payload",
        "api_test_token": "test_stock_hot_follow_xq_endpoint",
    },
    {
        "task_id": "6.2",
        "function_name": "stock_board_change_em",
        "registry_key": "akshare_stock_board_change_em",
        "adapter_method": "get_stock_board_change_em",
        "route_fragment": "/board/change/em",
        "unit_test_token": "test_get_stock_board_change_em_normalizes_columns",
        "backend_test_token": "test_board_change_em_route_returns_success_payload",
        "api_test_token": "test_board_change_em_endpoint",
    },
    {
        "task_id": "6.3",
        "function_name": "stock_news_main_em",
        "registry_key": "akshare_stock_news_main_em",
        "adapter_method": "get_stock_news_main_em",
        "route_fragment": "/stock/news-main/em",
        "unit_test_token": "test_get_stock_news_main_em",
        "backend_test_token": "/api/akshare/market/stock/news-main/em",
        "api_test_token": "test_stock_news_main_em_endpoint",
        "lifecycle": "excluded",
        "expected_resolution_status": "missing",
    },
    {
        "task_id": "6.4",
        "function_name": "stock_zt_pool_em",
        "registry_key": "akshare_stock_zt_pool_em",
        "adapter_method": "get_stock_zt_pool_em",
        "route_fragment": "/stock/zt-pool/em",
        "unit_test_token": "test_get_stock_zt_pool_em_normalizes_columns",
        "backend_test_token": "test_stock_zt_pool_em_route_returns_success_payload",
        "api_test_token": "test_stock_zt_pool_em_endpoint",
    },
    {
        "task_id": "6.5",
        "function_name": "stock_dt_pool_em",
        "registry_key": "akshare_stock_dt_pool_em",
        "adapter_method": "get_stock_dt_pool_em",
        "route_fragment": "/stock/dt-pool/em",
        "unit_test_token": "test_get_stock_dt_pool_em",
        "backend_test_token": "/api/akshare/market/stock/dt-pool/em",
        "api_test_token": "test_stock_dt_pool_em_endpoint",
    },
    {
        "task_id": "6.6",
        "function_name": "stock_strong_pool_em",
        "registry_key": "akshare_stock_strong_pool_em",
        "adapter_method": "get_stock_strong_pool_em",
        "route_fragment": "/stock/strong-pool/em",
        "unit_test_token": "test_get_stock_strong_pool_em",
        "backend_test_token": "/api/akshare/market/stock/strong-pool/em",
        "api_test_token": "test_stock_strong_pool_em_endpoint",
    },
    {
        "task_id": "6.7",
        "function_name": "stock_weak_pool_em",
        "registry_key": "akshare_stock_weak_pool_em",
        "adapter_method": "get_stock_weak_pool_em",
        "route_fragment": "/stock/weak-pool/em",
        "unit_test_token": "test_get_stock_weak_pool_em",
        "backend_test_token": "/api/akshare/market/stock/weak-pool/em",
        "api_test_token": "test_stock_weak_pool_em_endpoint",
        "lifecycle": "retired",
        "expected_resolution_status": "retired",
    },
    {
        "task_id": "6.8",
        "function_name": "stock_changes_em",
        "registry_key": "akshare_stock_changes_em",
        "adapter_method": "get_stock_changes_em",
        "route_fragment": "/stock/changes/em",
        "unit_test_token": "test_get_stock_changes_em_normalizes_columns",
        "backend_test_token": "test_stock_changes_em_route_returns_success_payload",
        "api_test_token": "test_stock_changes_em_endpoint",
    },
    {
        "task_id": "6.9",
        "function_name": "stock_new_em",
        "registry_key": "akshare_stock_new_em",
        "adapter_method": "get_stock_new_em",
        "route_fragment": "/stock/new/em",
        "unit_test_token": "test_get_stock_new_em",
        "backend_test_token": "/api/akshare/market/stock/new/em",
        "api_test_token": "test_stock_new_em_endpoint",
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return DEFAULT_MANIFEST
    payload = load_json(path)
    if not isinstance(payload, list):
        raise ValueError("manifest JSON must be a list")
    return payload


def parse_task_checks(text: str) -> dict[str, bool]:
    result: dict[str, bool] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if "akshare." not in stripped:
            continue
        match = TASK_LINE_PATTERN.match(stripped)
        if match is None:
            continue
        checked = match.group("checked").lower() == "x"
        task_id = match.group("task_id")
        result[task_id] = checked
    return result


def parse_repo_truth_rows(text: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("| 6."):
            continue
        parts = [part.strip() for part in stripped.split("|")[1:-1]]
        if len(parts) < 5:
            continue
        task_id = parts[0]
        function_name = parts[1].strip("`")
        rows[function_name] = {"task_id": task_id, "status": parts[-1]}
    return rows


def build_availability_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for item in payload.get("functions", []):
        name = item.get("name")
        if isinstance(name, str) and isinstance(item, dict):
            index[name] = item
    return index


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else (PROJECT_ROOT / path)


def validate_function(
    item: dict[str, str],
    availability: dict[str, dict[str, Any]],
    task_checks: dict[str, bool],
    repo_truth_rows: dict[str, dict[str, str]],
    registry_text: str,
    adapter_text: str,
    route_text: str,
    unit_test_text: str,
    backend_test_text: str,
    api_test_text: str,
) -> dict[str, Any]:
    function_name = item["function_name"]
    task_id = item["task_id"]
    lifecycle = item.get("lifecycle", "active")
    availability_row = availability.get(function_name)
    violations: list[dict[str, str]] = []
    if availability_row is None:
        violations.append({"kind": "availability", "message": f"availability report missing function {function_name}"})
        available = False
        resolution_status = None
    else:
        available = bool(availability_row.get("available"))
        resolution_status = availability_row.get("resolution_status")

    if lifecycle == "retired":
        expected_task_checked = True
        expected_status_fragment = "已下线/上游移除"
        artifact_expectation = False
        if available:
            violations.append({"kind": "availability", "message": f"retired function {function_name} unexpectedly reported available"})
        expected_resolution_status = item.get("expected_resolution_status")
        if expected_resolution_status is not None and resolution_status != expected_resolution_status:
            violations.append(
                {
                    "kind": "availability",
                    "message": f"resolution_status for retired function {function_name} is '{resolution_status}', expected '{expected_resolution_status}'",
                }
            )
    elif lifecycle == "excluded":
        expected_task_checked = True
        expected_status_fragment = "已排除/不在当前 scope"
        artifact_expectation = False
        if available:
            violations.append({"kind": "availability", "message": f"excluded function {function_name} unexpectedly reported available"})
        expected_resolution_status = item.get("expected_resolution_status")
        if expected_resolution_status is not None and resolution_status != expected_resolution_status:
            violations.append(
                {
                    "kind": "availability",
                    "message": f"resolution_status for excluded function {function_name} is '{resolution_status}', expected '{expected_resolution_status}'",
                }
            )
    else:
        expected_task_checked = available
        expected_status_fragment = "已实现" if available else "未检出同名函数"
        artifact_expectation = available

    task_checked = task_checks.get(task_id)
    if task_checked is None:
        violations.append({"kind": "openspec", "message": f"OpenSpec task {task_id} not found"})
    elif task_checked != expected_task_checked:
        violations.append(
            {
                "kind": "openspec",
                "message": f"OpenSpec task {task_id} checked={task_checked} expected={expected_task_checked}",
            }
        )

    repo_truth_row = repo_truth_rows.get(function_name)
    if repo_truth_row is None:
        violations.append({"kind": "repo_truth", "message": f"repo-truth row missing for {function_name}"})
        repo_truth_status = None
    else:
        repo_truth_status = repo_truth_row["status"]
        if expected_status_fragment not in repo_truth_status:
            violations.append(
                {
                    "kind": "repo_truth",
                    "message": f"repo-truth status for {function_name} is '{repo_truth_status}', expected fragment '{expected_status_fragment}'",
                }
            )

    artifact_states = {
        "registry": item["registry_key"] in registry_text,
        "adapter": item["adapter_method"] in adapter_text,
        "route": item["route_fragment"] in route_text,
        "unit_test": item["unit_test_token"] in unit_test_text,
        "backend_test": item["backend_test_token"] in backend_test_text,
        "api_test": item["api_test_token"] in api_test_text,
    }
    for key, present in artifact_states.items():
        if present != artifact_expectation:
            violations.append(
                {
                    "kind": key,
                    "message": f"{key} presence for {function_name} is {present}, expected {artifact_expectation}",
                }
            )

    return {
        "task_id": task_id,
        "function_name": function_name,
        "lifecycle": lifecycle,
        "available": available,
        "resolution_status": resolution_status,
        "repo_truth_status": repo_truth_status,
        "task_checked": task_checked,
        "artifact_states": artifact_states,
        "pass": not violations,
        "violations": violations,
    }


def validate_repo_truth(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    manifest = load_manifest(args.manifest_json)
    if args.availability_report is not None:
        availability_payload = load_json(resolve_path(args.availability_report))
        availability_exit_code = 0
    else:
        availability_payload, availability_exit_code = collect_availability(
            module_name="akshare",
            function_names=[item["function_name"] for item in manifest],
        )

    task_checks = parse_task_checks(read_text(resolve_path(args.tasks_path)))
    repo_truth_rows = parse_repo_truth_rows(read_text(resolve_path(args.repo_truth_path)))
    registry_text = read_text(resolve_path(args.registry_path))
    adapter_text = read_text(resolve_path(args.adapter_path))
    route_text = read_text(resolve_path(args.route_path))
    unit_test_text = read_text(resolve_path(args.unit_test_path))
    backend_test_text = read_text(resolve_path(args.backend_test_path))
    api_test_text = read_text(resolve_path(args.api_file_test_path))
    availability_index = build_availability_index(availability_payload)

    function_reports = [
        validate_function(
            item=item,
            availability=availability_index,
            task_checks=task_checks,
            repo_truth_rows=repo_truth_rows,
            registry_text=registry_text,
            adapter_text=adapter_text,
            route_text=route_text,
            unit_test_text=unit_test_text,
            backend_test_text=backend_test_text,
            api_test_text=api_test_text,
        )
        for item in manifest
    ]

    violations = [
        {
            "task_id": report["task_id"],
            "function_name": report["function_name"],
            "kind": violation["kind"],
            "message": violation["message"],
        }
        for report in function_reports
        for violation in report["violations"]
    ]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric_version": "v1",
        "report_type": "akshare_market_repo_truth_gate",
        "project_root": str(PROJECT_ROOT),
        "availability_report": availability_payload,
        "pass": availability_payload.get("import_ok", False) and not violations,
        "summary": {
            "tracked_count": len(function_reports),
            "passed_count": sum(1 for item in function_reports if item["pass"]),
            "failed_count": sum(1 for item in function_reports if not item["pass"]),
            "violation_count": len(violations),
        },
        "functions": function_reports,
        "violations": violations,
    }
    exit_code = 0 if payload["pass"] and availability_exit_code == 0 else 1
    return payload, exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate AkShare market repo-truth against local availability")
    parser.add_argument("--manifest-json", type=Path, help="Optional manifest override for testing or custom subsets")
    parser.add_argument("--availability-report", type=Path, help="Optional precomputed availability JSON")
    parser.add_argument("--tasks-path", type=Path, default=DEFAULT_TASKS_PATH)
    parser.add_argument("--repo-truth-path", type=Path, default=DEFAULT_REPO_TRUTH_PATH)
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--adapter-path", type=Path, default=DEFAULT_ADAPTER_PATH)
    parser.add_argument("--route-path", type=Path, default=DEFAULT_ROUTE_PATH)
    parser.add_argument("--unit-test-path", type=Path, default=DEFAULT_UNIT_TEST_PATH)
    parser.add_argument("--backend-test-path", type=Path, default=DEFAULT_BACKEND_TEST_PATH)
    parser.add_argument("--api-file-test-path", type=Path, default=DEFAULT_API_FILE_TEST_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload, exit_code = validate_repo_truth(args)
    output_path = resolve_path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
