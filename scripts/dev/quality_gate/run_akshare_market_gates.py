#!/usr/bin/env python3
"""Run the AkShare market availability probe and repo-truth gate as a single entrypoint."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:
    from scripts.dev.quality_gate.collect_akshare_market_function_availability import (
        CANONICAL_FUNCTIONS,
        collect_availability,
    )
    from scripts.dev.quality_gate.validate_akshare_market_repo_truth import validate_repo_truth
    from scripts.dev.quality_gate.validate_akshare_market_repo_truth import (
        DEFAULT_ADAPTER_PATH,
        DEFAULT_API_FILE_TEST_PATH,
        DEFAULT_BACKEND_TEST_PATH,
        DEFAULT_REGISTRY_PATH,
        DEFAULT_REPO_TRUTH_PATH,
        DEFAULT_ROUTE_PATH,
        DEFAULT_TASKS_PATH,
        DEFAULT_UNIT_TEST_PATH,
    )
except ModuleNotFoundError:
    from collect_akshare_market_function_availability import CANONICAL_FUNCTIONS, collect_availability
    from validate_akshare_market_repo_truth import validate_repo_truth
    from validate_akshare_market_repo_truth import (
        DEFAULT_ADAPTER_PATH,
        DEFAULT_API_FILE_TEST_PATH,
        DEFAULT_BACKEND_TEST_PATH,
        DEFAULT_REGISTRY_PATH,
        DEFAULT_REPO_TRUTH_PATH,
        DEFAULT_ROUTE_PATH,
        DEFAULT_TASKS_PATH,
        DEFAULT_UNIT_TEST_PATH,
    )


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports" / "analysis" / "akshare-market-gates"


def _resolve_output_path(path: Path | None, output_dir: Path, filename: str) -> Path:
    if path is None:
        return output_dir / filename
    return path if path.is_absolute() else (output_dir / path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AkShare market availability and repo-truth gates together")
    parser.add_argument("--module", default="akshare", help="Python module to inspect; defaults to akshare")
    parser.add_argument(
        "--function",
        action="append",
        dest="functions",
        help="Function/attribute to probe; repeatable. Defaults to the tracked AkShare market set.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for generated reports")
    parser.add_argument("--availability-output", type=Path, help="Optional availability report path override")
    parser.add_argument("--repo-truth-output", type=Path, help="Optional repo-truth report path override")
    parser.add_argument("--summary-output", type=Path, help="Optional combined summary report path override")
    parser.add_argument("--manifest-json", type=Path, help="Optional manifest override for testing or custom subsets")
    parser.add_argument("--tasks-path", type=Path, default=DEFAULT_TASKS_PATH)
    parser.add_argument("--repo-truth-path", type=Path, default=DEFAULT_REPO_TRUTH_PATH)
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--adapter-path", type=Path, default=DEFAULT_ADAPTER_PATH)
    parser.add_argument("--route-path", type=Path, default=DEFAULT_ROUTE_PATH)
    parser.add_argument("--unit-test-path", type=Path, default=DEFAULT_UNIT_TEST_PATH)
    parser.add_argument("--backend-test-path", type=Path, default=DEFAULT_BACKEND_TEST_PATH)
    parser.add_argument("--api-file-test-path", type=Path, default=DEFAULT_API_FILE_TEST_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else (PROJECT_ROOT / args.output_dir)
    availability_output = _resolve_output_path(
        args.availability_output, output_dir, "akshare-market-function-availability.json"
    )
    repo_truth_output = _resolve_output_path(args.repo_truth_output, output_dir, "akshare-market-repo-truth-gate.json")
    summary_output = _resolve_output_path(args.summary_output, output_dir, "akshare-market-gates-summary.json")

    function_names = args.functions or CANONICAL_FUNCTIONS
    availability_payload, availability_exit_code = collect_availability(args.module, function_names)
    _write_json(availability_output, availability_payload)

    validator_args = SimpleNamespace(
        manifest_json=args.manifest_json,
        availability_report=availability_output,
        tasks_path=args.tasks_path,
        repo_truth_path=args.repo_truth_path,
        registry_path=args.registry_path,
        adapter_path=args.adapter_path,
        route_path=args.route_path,
        unit_test_path=args.unit_test_path,
        backend_test_path=args.backend_test_path,
        api_file_test_path=args.api_file_test_path,
        output=repo_truth_output,
    )
    repo_truth_payload, repo_truth_exit_code = validate_repo_truth(validator_args)
    _write_json(repo_truth_output, repo_truth_payload)

    availability_summary = availability_payload.get("summary", {})
    repo_truth_summary = repo_truth_payload.get("summary", {})
    summary_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric_version": "v1",
        "report_type": "akshare_market_gate_bundle",
        "project_root": str(PROJECT_ROOT),
        "module": args.module,
        "functions": function_names,
        "availability_report_path": str(availability_output),
        "repo_truth_report_path": str(repo_truth_output),
        "availability_exit_code": availability_exit_code,
        "repo_truth_exit_code": repo_truth_exit_code,
        "pass": availability_exit_code == 0 and repo_truth_exit_code == 0,
        "summary": {
            "tracked_count": availability_summary.get("tracked_count", repo_truth_summary.get("tracked_count", 0)),
            "available_count": availability_summary.get("available_count", 0),
            "missing_count": availability_summary.get("missing_count", 0),
            "repo_truth_passed_count": repo_truth_summary.get("passed_count", 0),
            "repo_truth_failed_count": repo_truth_summary.get("failed_count", 0),
            "repo_truth_violation_count": repo_truth_summary.get("violation_count", len(repo_truth_payload.get("violations", []))),
        },
    }
    _write_json(summary_output, summary_payload)
    print(json.dumps(summary_payload, ensure_ascii=False, indent=2))
    return 0 if summary_payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
