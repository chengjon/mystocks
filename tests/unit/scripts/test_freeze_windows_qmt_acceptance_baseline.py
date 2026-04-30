from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = PROJECT_ROOT / "scripts" / "dev" / "freeze_windows_qmt_acceptance_baseline.py"


def _load_module():
    assert MODULE_PATH.exists()
    spec = importlib.util.spec_from_file_location("freeze_windows_qmt_acceptance_baseline", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_main_freezes_latest_summary_into_baseline_artifacts(tmp_path: Path, capsys) -> None:
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
                "expected": {"provider_mode": "mock"},
                "issues": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    module = _load_module()
    exit_code = module.main(["--report-dir", str(report_dir)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    latest_baseline_path = report_dir / "baselines" / "latest-baseline.json"
    assert exit_code == 0
    assert payload["status_label"] == "baseline_frozen"
    assert Path(payload["latest_baseline_path"]) == latest_baseline_path
    assert latest_baseline_path.exists()
    frozen_payload = json.loads(latest_baseline_path.read_text(encoding="utf-8"))
    assert frozen_payload["ok"] is True
    assert frozen_payload["stage"] == "completed"
    assert frozen_payload["baseline_schema_version"] == 1
    assert frozen_payload["baseline_kind"] == "windows_qmt_contract_acceptance"
    assert frozen_payload["frozen_from_summary_path"] == str(latest_summary_path)


def test_main_returns_missing_status_when_source_summary_is_absent(tmp_path: Path, capsys) -> None:
    module = _load_module()
    report_dir = tmp_path / "reports"

    exit_code = module.main(["--report-dir", str(report_dir)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 2
    assert payload["status_label"] == "source_summary_missing"
    assert payload["recommended_exit_code"] == 2


def test_main_rejects_non_green_acceptance_summary(tmp_path: Path, capsys) -> None:
    report_dir = tmp_path / "reports"
    latest_summary_path = report_dir / "latest.json"
    latest_summary_path.parent.mkdir(parents=True, exist_ok=True)
    latest_summary_path.write_text(
        json.dumps(
            {
                "ok": False,
                "stage": "result_validation_failed",
                "issues": ["result missing event_id"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    module = _load_module()
    exit_code = module.main(["--report-dir", str(report_dir)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 1
    assert payload["status_label"] == "source_summary_ineligible"
    assert payload["recommended_exit_code"] == 1
    assert "acceptance summary is not eligible for baseline freeze" in payload["issues"][0]
    assert not (report_dir / "baselines" / "latest-baseline.json").exists()
