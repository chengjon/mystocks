from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = PROJECT_ROOT / "docs" / "reports" / "quality" / "windows-qmt-contract-acceptance"


def _extract_str(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _load_json_object(path: Path) -> Mapping[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    if not isinstance(payload, Mapping):
        return None
    return payload


def build_report_status(report_dir: str | Path) -> dict[str, Any]:
    report_root = Path(report_dir)
    summary_path = report_root / "latest.json"
    summary = _load_json_object(summary_path)
    if summary is None:
        return {
            "status_label": "report_missing",
            "recommended_exit_code": 2,
            "report_dir": str(report_root),
            "summary_path": str(summary_path),
            "acceptance_ok": None,
            "comparison_ok": None,
            "stage": None,
            "issues": ["latest acceptance summary is missing or invalid"],
            "mismatch_count": 0,
            "comparison_markdown_path": None,
            "baseline_path": None,
        }

    acceptance_ok = summary.get("ok") is True
    stage = _extract_str(summary, "stage")
    runtime_environment = _extract_str(summary, "runtime_environment")
    generated_at = _extract_str(summary, "generated_at")
    issues = summary.get("issues")
    normalized_issues = list(issues) if isinstance(issues, list) else []

    comparison_payload = summary.get("comparison")
    comparison = comparison_payload if isinstance(comparison_payload, Mapping) else None
    comparison_ok = comparison.get("ok") if comparison else None
    mismatch_list = comparison.get("mismatches") if comparison else None
    mismatch_count = len(mismatch_list) if isinstance(mismatch_list, list) else 0
    comparison_markdown_path = None
    baseline_path = None
    if comparison:
        comparison_markdown_path = _extract_str(comparison, "latest_markdown_output") or _extract_str(
            comparison, "markdown_output"
        )
        baseline_path = _extract_str(comparison, "baseline_path")

    if acceptance_ok is not True:
        status_label = "acceptance_failed"
        recommended_exit_code = 1
    elif comparison_ok is False:
        status_label = "contract_drift_detected"
        recommended_exit_code = 3
    elif comparison_ok is True:
        status_label = "acceptance_passed_with_baseline_match"
        recommended_exit_code = 0
    else:
        status_label = "acceptance_passed_no_baseline"
        recommended_exit_code = 0

    return {
        "status_label": status_label,
        "recommended_exit_code": recommended_exit_code,
        "report_dir": str(report_root),
        "summary_path": str(summary_path),
        "acceptance_ok": acceptance_ok,
        "comparison_ok": comparison_ok if isinstance(comparison_ok, bool) else None,
        "stage": stage,
        "runtime_environment": runtime_environment,
        "generated_at": generated_at,
        "issues": normalized_issues,
        "issue_count": len(normalized_issues),
        "mismatch_count": mismatch_count,
        "comparison_markdown_path": comparison_markdown_path,
        "baseline_path": baseline_path,
    }


def render_report_status_text(status: Mapping[str, Any]) -> str:
    lines = [
        "Windows qmt acceptance latest report",
        f"status_label: {status.get('status_label')}",
        f"recommended_exit_code: {status.get('recommended_exit_code')}",
        f"summary_path: {status.get('summary_path')}",
        f"stage: {status.get('stage')}",
        f"acceptance_ok: {status.get('acceptance_ok')}",
        f"comparison_ok: {status.get('comparison_ok')}",
        f"mismatch_count: {status.get('mismatch_count')}",
    ]
    comparison_markdown_path = status.get("comparison_markdown_path")
    if comparison_markdown_path:
        lines.append(f"comparison_markdown_path: {comparison_markdown_path}")
    baseline_path = status.get("baseline_path")
    if baseline_path:
        lines.append(f"baseline_path: {baseline_path}")
    issue_count = status.get("issue_count", 0)
    if issue_count:
        lines.append("issues:")
        for issue in status.get("issues", []):
            lines.append(f"  - {issue}")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize the latest Windows qmt acceptance artifacts from WSL 上的 Ubuntu 24.04.4 LTS."
    )
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory containing latest.json and optional latest-comparison.md artifacts.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of the default text summary.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    status = build_report_status(getattr(args, "report_dir"))
    if bool(getattr(args, "json", False)):
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print(render_report_status_text(status), end="")
    return int(status.get("recommended_exit_code", 2))


if __name__ == "__main__":
    raise SystemExit(main())
