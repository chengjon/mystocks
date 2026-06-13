#!/usr/bin/env python3
"""Collect a machine-readable frontend PM2 runtime gate snapshot from existing artifacts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPO_BASELINE_PATH = PROJECT_ROOT / "reports" / "analysis" / "tech-debt-baseline.json"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(_read_text(path))


def _extract_first(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def _extract_counts(line: str | None) -> dict[str, int]:
    counts = {"passed": 0, "failed": 0, "skipped": 0}
    if not line:
        return counts
    for label in counts:
        match = re.search(rf"{label}\s*=\s*(\d+)", line)
        if not match:
            match = re.search(rf"(\d+)\s+{label}", line)
        if match:
            counts[label] = int(match.group(1))
    return counts


def _parse_pm2_status_lines(regression_log_text: str) -> list[dict[str, str]]:
    lines = []
    capture = False
    for raw_line in regression_log_text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("PM2 Status:"):
            capture = True
            continue
        if capture and line.startswith("Frontend: http://localhost:3020 | Backend: http://localhost:8020"):
            break
        if capture and "mystocks-" in line and "│" in line:
            match = re.search(r"mystocks-[a-z-]+", line)
            status_match = re.search(r"\b(online|stopped|errored|launching)\b", line)
            if match and status_match:
                lines.append(
                    {
                        "name": match.group(0),
                        "status": status_match.group(1),
                        "raw": line,
                    }
                )
    return lines


def build_frontend_runtime_gate_payload(
    *,
    type_ceiling_log: str,
    pm2_gate_log: str,
    regression_log: str,
    axe_log: str,
    current_baseline: dict[str, Any],
    repo_baseline: dict[str, Any],
) -> dict[str, Any]:
    structural_gate = _extract_first(r"^\s*([0-9]+\s+passed.*)$", pm2_gate_log)
    regression_e2e = _extract_first(r"^(E2E Summary:\s*.+)$", regression_log)
    regression_pytest = _extract_first(r"^(Pytest Summary:\s*.+)$", regression_log)
    type_ceiling = _extract_first(r"^(\[type-ceiling\].+)$", type_ceiling_log)
    accessibility_smoke = _extract_first(r"([0-9]+\s+passed.*)", axe_log)
    pm2_status = _parse_pm2_status_lines(regression_log)

    frontend_url = "http://localhost:3020"
    backend_url = "http://localhost:8020"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric_version": "v1",
        "service_urls": {
            "backend": backend_url,
            "frontend": frontend_url,
        },
        "structural_gate": structural_gate,
        "structural_gate_counts": _extract_counts(structural_gate),
        "type_ceiling": type_ceiling,
        "regression_e2e": regression_e2e,
        "regression_e2e_counts": _extract_counts(regression_e2e),
        "regression_pytest": regression_pytest,
        "regression_pytest_counts": _extract_counts(regression_pytest),
        "accessibility_smoke": accessibility_smoke,
        "accessibility_smoke_counts": _extract_counts(accessibility_smoke),
        "pm2_status": pm2_status,
        "pm2_services_online": [item["name"] for item in pm2_status if item["status"] == "online"],
        "current_frontend_type_errors": current_baseline.get("frontend_type_errors"),
        "repo_frontend_type_error_baseline": repo_baseline.get("frontend_type_errors"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect frontend PM2 runtime gate snapshot from logs")
    parser.add_argument("--type-ceiling-log", required=True, type=Path)
    parser.add_argument("--pm2-gate-log", required=True, type=Path)
    parser.add_argument("--regression-log", required=True, type=Path)
    parser.add_argument("--axe-log", required=True, type=Path)
    parser.add_argument("--current-tech-debt-baseline", required=True, type=Path)
    parser.add_argument("--repo-tech-debt-baseline", type=Path, default=REPO_BASELINE_PATH)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    payload = build_frontend_runtime_gate_payload(
        type_ceiling_log=_read_text(args.type_ceiling_log.resolve()),
        pm2_gate_log=_read_text(args.pm2_gate_log.resolve()),
        regression_log=_read_text(args.regression_log.resolve()),
        axe_log=_read_text(args.axe_log.resolve()),
        current_baseline=_read_json(args.current_tech_debt_baseline.resolve()),
        repo_baseline=_read_json(args.repo_tech_debt_baseline.resolve()),
    )

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[frontend-runtime-gate] written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
