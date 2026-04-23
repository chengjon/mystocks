from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from scripts.runtime import record_quality_gate_closeout as closeout


def test_default_state_file_uses_tmp_scoped_path(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("QUALITY_GATE_GRAPHITI_STATE_DIR", raising=False)

    state_file = closeout.default_state_file(tmp_path, "frontend-runtime-gate")

    assert state_file.name == "frontend-runtime-gate.json"
    assert "mystocks-quality-gate-closeout-state" in str(state_file)
    assert tmp_path.name in str(state_file)


def test_build_payload_for_frontend_runtime_gate(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports/analysis/frontend-runtime-gate/20260423-112949"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "frontend-runtime-gate.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-04-23T03:38:31.647071+00:00",
                "service_urls": {"backend": "http://localhost:8020", "frontend": "http://localhost:3020"},
                "structural_gate": "14 passed (5.6s)",
                "structural_gate_counts": {"passed": 14, "failed": 0, "skipped": 0},
                "regression_e2e": "E2E Summary: passed=44 failed=0 skipped=0",
                "regression_e2e_counts": {"passed": 44, "failed": 0, "skipped": 0},
                "regression_pytest": "Pytest Summary: passed=46 failed=0 skipped=18",
                "accessibility_smoke": "4 passed (18.3s)",
                "accessibility_smoke_counts": {"passed": 4, "failed": 0, "skipped": 0},
                "pm2_services_online": ["mystocks-backend", "mystocks-frontend"],
                "current_frontend_type_errors": 0,
                "repo_frontend_type_error_baseline": 0,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (report_dir / "tech-debt-baseline.current.json").write_text(json.dumps({"frontend_type_errors": 0}) + "\n", encoding="utf-8")
    (report_dir / "SUMMARY.md").write_text("# Frontend Runtime Baseline\n", encoding="utf-8")

    payload = closeout.build_payload(gate_kind="frontend-runtime-gate", project_root=tmp_path, report_dir=report_dir)

    assert payload["event_type"] == "quality_gate.closeout.frontend-runtime-gate"
    assert payload["gate"]["canonical_service_urls"]["backend"] == "http://localhost:8020"
    assert "pm2_services_online=mystocks-backend,mystocks-frontend" in payload["verification"]["machine_verified_checks"]
    assert closeout.gate_passes("frontend-runtime-gate", payload) is True


def test_process_closeout_skips_non_pass_api_gate(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports/analysis/api-performance-gate/20260423-115543"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-04-23T11:56:01.216318",
                "base_url": "http://localhost:8020",
                "slo_status": {"compliant": False, "violations": ["p95 exceeded"]},
                "summary": {"overall_p95_ms": 352.1},
                "workload_classes": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (report_dir / "metrics-summary.json").write_text(json.dumps({"metrics_health": {"status": "degraded"}, "prometheus_snapshot": {}}) + "\n", encoding="utf-8")
    (report_dir / "SUMMARY.md").write_text("# API Performance Baseline\n", encoding="utf-8")

    state_file = tmp_path / ".claude/quality-gate-closeout-state.json"
    result = closeout.process_closeout(
        gate_kind="api-performance-gate",
        project_root=tmp_path,
        report_dir=report_dir,
        state_file=state_file,
        max_wait_seconds=10,
    )

    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert result["status"] == "skipped_non_pass"
    assert state["reports"][-1]["gate_kind"] == "api-performance-gate"
    assert state["processed"] == []


def test_quality_gate_closeout_script_runs_with_external_graphiti_command_for_docker(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports/analysis/docker-runtime-smoke/20260423-180247"
    args_path = tmp_path / "graphiti-args.json"
    fake_command = tmp_path / "fake_coordctl.sh"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "docker-runtime-smoke.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-04-23T18:02:47+08:00",
                "service_urls": {"backend": "http://localhost:8021", "frontend": "http://localhost:3021"},
                "service_role": "backup_smoke",
                "checks": {"backend_health": "PASS", "backend_readiness": "PASS", "frontend_index": "PASS"},
                "metrics_health": "healthy",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (report_dir / "SUMMARY.md").write_text("# Docker Runtime Smoke\n", encoding="utf-8")

    fake_command.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                f"python -c 'import json,sys; open({json.dumps(str(args_path))}, \"w\", encoding=\"utf-8\").write(json.dumps(sys.argv[1:], ensure_ascii=False))' \"$@\"",
                "cat <<'EOF'",
                '{"server_status":"ok","ingest_status":"completed","episode_uuid":"ep-quality-gate-1","group_id":"mystocks_spec_quality_gates"}',
                "EOF",
            ]
        ),
        encoding="utf-8",
    )
    fake_command.chmod(0o755)

    env = os.environ.copy()
    env["QUALITY_GATE_GRAPHITI_COMMAND"] = str(fake_command)
    env["QUALITY_GATE_GRAPHITI_GROUP_ID"] = "mystocks_spec_quality_gates"
    env["QUALITY_GATE_GRAPHITI_STATE_DIR"] = str(tmp_path / "state")

    completed = subprocess.run(
        [
            "python",
            "scripts/runtime/record_quality_gate_closeout.py",
            "--gate-kind",
            "docker-runtime-smoke",
            "--project-root",
            str(tmp_path),
            "--report-dir",
            str(report_dir),
            "--output",
            "json",
        ],
        cwd=Path(__file__).resolve().parents[3],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    args = json.loads(args_path.read_text(encoding="utf-8"))
    graphiti_payload = json.loads(args[args.index("--body") + 1])

    assert payload["status"] == "completed"
    assert payload["episode_uuid"] == "ep-quality-gate-1"
    assert payload["state_file"].endswith(f"/{tmp_path.name}/docker-runtime-smoke.json")
    assert args[:2] == ["graphiti", "remember"]
    assert graphiti_payload["event_type"] == "quality_gate.closeout.docker-runtime-smoke"
    assert graphiti_payload["gate"]["backup_smoke_service_urls"]["frontend"] == "http://localhost:3021"
