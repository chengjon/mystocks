from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = PROJECT_ROOT / "scripts" / "dev" / "summarize_windows_qmt_acceptance_reports.py"
SPEC = importlib.util.spec_from_file_location("summarize_windows_qmt_acceptance_reports", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_build_report_status_returns_green_status_without_comparison(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    latest_summary_path = report_dir / "latest.json"
    latest_summary_path.parent.mkdir(parents=True, exist_ok=True)
    latest_summary_path.write_text(
        json.dumps(
            {
                "ok": True,
                "stage": "completed",
                "generated_at": "2026-04-30T12:00:00+00:00",
                "runtime_environment": "wsl-ubuntu-24.04.4-lts",
                "issues": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    status = MODULE.build_report_status(report_dir)

    assert status["status_label"] == "acceptance_passed_no_baseline"
    assert status["recommended_exit_code"] == 0
    assert status["summary_path"] == str(latest_summary_path)
    assert status["comparison_ok"] is None


def test_build_report_status_returns_drift_status_with_latest_comparison(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    latest_summary_path = report_dir / "latest.json"
    latest_comparison_path = report_dir / "latest-comparison.md"
    latest_summary_path.parent.mkdir(parents=True, exist_ok=True)
    latest_comparison_path.write_text("# drift\n", encoding="utf-8")
    latest_summary_path.write_text(
        json.dumps(
            {
                "ok": True,
                "stage": "completed",
                "generated_at": "2026-04-30T12:00:00+00:00",
                "runtime_environment": "wsl-ubuntu-24.04.4-lts",
                "issues": [],
                "comparison": {
                    "ok": False,
                    "baseline_path": "/tmp/baseline.json",
                    "mismatches": [
                        {
                            "path": "result.source_name",
                            "expected": "qmt/other-source",
                            "actual": "qmt/windows_reference_service",
                        }
                    ],
                    "latest_markdown_output": str(latest_comparison_path),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    status = MODULE.build_report_status(report_dir)

    assert status["status_label"] == "contract_drift_detected"
    assert status["recommended_exit_code"] == 3
    assert status["comparison_ok"] is False
    assert status["comparison_markdown_path"] == str(latest_comparison_path)
    assert status["mismatch_count"] == 1


def test_main_json_mode_returns_report_missing_status(tmp_path: Path, capsys) -> None:
    report_dir = tmp_path / "reports"

    exit_code = MODULE.main(["--report-dir", str(report_dir), "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 2
    assert payload["status_label"] == "report_missing"
    assert payload["recommended_exit_code"] == 2
