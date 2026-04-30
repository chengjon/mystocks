from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = PROJECT_ROOT / "scripts" / "dev" / "run_windows_qmt_contract_formal_sequence.py"


def _load_module():
    assert MODULE_PATH.exists()
    spec = importlib.util.spec_from_file_location("run_windows_qmt_contract_formal_sequence", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_main_runs_no_baseline_formal_sequence(tmp_path: Path, monkeypatch, capsys) -> None:
    report_dir = tmp_path / "reports"
    verify_summary = {
        "ok": True,
        "stage": "completed",
        "runtime_environment": "wsl-ubuntu-24.04.4-lts",
        "generated_at": "2026-04-30T12:00:00+00:00",
        "artifacts": {
            "report_artifact": str(report_dir / "20260430T120000Z-windows-qmt-contract-acceptance.json"),
            "latest": str(report_dir / "latest.json"),
        },
    }
    summarize_payload = {
        "status_label": "acceptance_passed_no_baseline",
        "recommended_exit_code": 0,
        "summary_path": str(report_dir / "latest.json"),
    }
    freeze_payload = {
        "status_label": "baseline_frozen",
        "recommended_exit_code": 0,
    }

    module = _load_module()

    def _fake_run_step(command):
        if command[:2] == ["verify", "windows-qmt"]:
            return 0, verify_summary
        if command[:2] == ["summarize", "windows-qmt"]:
            return 0, summarize_payload
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module, "run_step_command", _fake_run_step)
    monkeypatch.setattr(module, "build_freeze_command", lambda args: ["freeze", "windows-qmt"])
    monkeypatch.setattr(module, "build_verify_command", lambda args: ["verify", "windows-qmt"])
    monkeypatch.setattr(module, "build_summarize_command", lambda args: ["summarize", "windows-qmt"])

    exit_code = module.main(
        [
            "--base-url",
            "http://windows-host:8001",
            "--report-dir",
            str(report_dir),
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["status_label"] == "formal_sequence_completed"
    assert payload["recommended_exit_code"] == 0
    assert payload["steps"][0]["name"] == "preflight"
    assert payload["steps"][1]["name"] == "verify"
    assert payload["steps"][2]["name"] == "compare"
    assert payload["steps"][2]["status_label"] == "skipped"
    assert payload["steps"][3]["name"] == "summarize"
    assert "freeze" not in [step["name"] for step in payload["steps"]]
    assert payload["verify"]["ok"] is True
    assert payload["summary"]["status_label"] == "acceptance_passed_no_baseline"
    assert payload["expected"]["contract_profile"] == "kernel-phase-a"
    assert payload["report_dir"] == str(report_dir)
    assert Path(payload["artifacts"]["latest_manifest_output"]).exists()
    assert Path(payload["artifacts"]["manifest_output"]).exists()


def test_main_runs_baseline_compare_formal_sequence(tmp_path: Path, monkeypatch, capsys) -> None:
    report_dir = tmp_path / "reports"
    compare_path = report_dir / "baselines" / "latest-baseline.json"
    verify_summary = {
        "ok": True,
        "stage": "completed",
        "comparison": {
            "ok": True,
            "baseline_path": str(compare_path),
        },
        "artifacts": {
            "latest": str(report_dir / "latest.json"),
        },
    }
    summarize_payload = {
        "status_label": "acceptance_passed_with_baseline_match",
        "recommended_exit_code": 0,
        "summary_path": str(report_dir / "latest.json"),
        "baseline_path": str(compare_path),
    }

    module = _load_module()

    issued_commands: list[list[str]] = []

    def _fake_run_step(command):
        issued_commands.append(list(command))
        if command[:2] == ["verify", "windows-qmt"]:
            return 0, verify_summary
        if command[:2] == ["summarize", "windows-qmt"]:
            return 0, summarize_payload
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module, "run_step_command", _fake_run_step)

    exit_code = module.main(
        [
            "--base-url",
            "http://windows-host:8001",
            "--report-dir",
            str(report_dir),
            "--compare-with-latest-baseline",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["status_label"] == "formal_sequence_completed"
    verify_command = issued_commands[0]
    assert "--compare-with-latest-baseline" in verify_command
    assert payload["steps"][2]["name"] == "compare"
    assert payload["steps"][2]["status_label"] == "completed"
    assert payload["verify"]["comparison"]["ok"] is True
    assert payload["summary"]["status_label"] == "acceptance_passed_with_baseline_match"


def test_main_runs_freeze_after_successful_formal_sequence(tmp_path: Path, monkeypatch, capsys) -> None:
    report_dir = tmp_path / "reports"
    verify_summary = {
        "ok": True,
        "stage": "completed",
        "artifacts": {
            "latest": str(report_dir / "latest.json"),
        },
    }
    summarize_payload = {
        "status_label": "acceptance_passed_no_baseline",
        "recommended_exit_code": 0,
        "summary_path": str(report_dir / "latest.json"),
    }
    freeze_payload = {
        "status_label": "baseline_frozen",
        "recommended_exit_code": 0,
        "latest_baseline_path": str(report_dir / "baselines" / "latest-baseline.json"),
    }

    module = _load_module()

    def _fake_run_step(command):
        if command[:2] == ["verify", "windows-qmt"]:
            return 0, verify_summary
        if command[:2] == ["summarize", "windows-qmt"]:
            return 0, summarize_payload
        if command[:2] == ["freeze", "windows-qmt"]:
            return 0, freeze_payload
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module, "run_step_command", _fake_run_step)
    monkeypatch.setattr(module, "build_verify_command", lambda args: ["verify", "windows-qmt"])
    monkeypatch.setattr(module, "build_summarize_command", lambda args: ["summarize", "windows-qmt"])
    monkeypatch.setattr(module, "build_freeze_command", lambda args: ["freeze", "windows-qmt"])

    exit_code = module.main(
        [
            "--base-url",
            "http://windows-host:8001",
            "--report-dir",
            str(report_dir),
            "--freeze-baseline",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["status_label"] == "formal_sequence_completed"
    assert payload["freeze"]["status_label"] == "baseline_frozen"
    assert payload["steps"][-1]["name"] == "freeze"


def test_main_reports_freeze_refusal_when_acceptance_is_not_successful(tmp_path: Path, monkeypatch, capsys) -> None:
    report_dir = tmp_path / "reports"
    verify_summary = {
        "ok": False,
        "stage": "result_validation_failed",
        "issues": ["result missing event_id"],
        "artifacts": {
            "latest": str(report_dir / "latest.json"),
        },
    }
    summarize_payload = {
        "status_label": "acceptance_failed",
        "recommended_exit_code": 1,
        "summary_path": str(report_dir / "latest.json"),
    }
    freeze_payload = {
        "status_label": "source_summary_ineligible",
        "recommended_exit_code": 1,
        "issues": ["acceptance summary is not eligible for baseline freeze; expected ok=true and stage=completed"],
    }

    module = _load_module()

    def _fake_run_step(command):
        if command[:2] == ["verify", "windows-qmt"]:
            return 1, verify_summary
        if command[:2] == ["summarize", "windows-qmt"]:
            return 1, summarize_payload
        if command[:2] == ["freeze", "windows-qmt"]:
            return 1, freeze_payload
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module, "run_step_command", _fake_run_step)
    monkeypatch.setattr(module, "build_verify_command", lambda args: ["verify", "windows-qmt"])
    monkeypatch.setattr(module, "build_summarize_command", lambda args: ["summarize", "windows-qmt"])
    monkeypatch.setattr(module, "build_freeze_command", lambda args: ["freeze", "windows-qmt"])

    exit_code = module.main(
        [
            "--base-url",
            "http://windows-host:8001",
            "--report-dir",
            str(report_dir),
            "--freeze-baseline",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 1
    assert payload["status_label"] == "formal_sequence_failed"
    assert payload["freeze"]["status_label"] == "source_summary_ineligible"
    assert payload["steps"][-1]["name"] == "freeze"
