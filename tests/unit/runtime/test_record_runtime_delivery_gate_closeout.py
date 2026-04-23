from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from scripts.runtime import record_runtime_delivery_gate_closeout as closeout


def test_build_payload_uses_runtime_delivery_gate_contract(tmp_path: Path) -> None:
    project_root = tmp_path
    manifest_path = project_root / "reports/analysis/runtime-delivery-gate/20260423-212355/runtime-delivery-gate-manifest.json"
    runtime_summary_path = project_root / "reports/analysis/runtime-delivery-gate/20260423-212355/runtime-quality-summary/summary.json"
    gate_summary_path = project_root / "reports/analysis/runtime-delivery-gate/20260423-212355/SUMMARY.md"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_summary_path.parent.mkdir(parents=True, exist_ok=True)
    gate_summary_path.parent.mkdir(parents=True, exist_ok=True)

    payload = closeout.build_payload(
        project_root=project_root,
        manifest_path=manifest_path,
        runtime_summary_path=runtime_summary_path,
        gate_summary_path=gate_summary_path,
        manifest={
            "generated_at": "2026-04-23T21:23:55+08:00",
            "overall_gate_status": "PASS",
            "runtime_observability_drift_pass": True,
            "api_performance_drift_pass": True,
            "monitoring_rule_metric_reference_pass": True,
            "backend_runtime_dependency_pass": True,
            "container_deployment_contract_pass": True,
            "deployment_env_contract_pass": True,
            "docker_runtime_service_role": "backup_smoke",
            "docker_runtime_service_url_roles": {"backend": "backup_smoke", "frontend": "backup_smoke"},
        },
        runtime_summary={
            "generated_at": "2026-04-23T21:23:55+08:00",
            "overall_gate_status": "PASS",
        },
    )

    assert payload["event_type"] == "runtime.delivery_gate_closeout"
    assert payload["title"] == "Runtime Delivery Gate 20260423-212355"
    assert payload["session_id"] == "runtime-delivery-gate:20260423-212355"
    assert payload["completion_phrase"] == "runtime delivery gate pass"
    assert payload["verification"]["overall_gate_status"] == "PASS"
    assert "container_deployment_contract_pass=True" in payload["verification"]["machine_verified_checks"]
    assert payload["gate"]["docker_runtime_service_role"] == "backup_smoke"
    assert payload["gate"]["canonical_service_urls"]["backend"] == "http://localhost:8020"
    assert payload["gate"]["backup_smoke_service_urls"]["frontend"] == "http://localhost:3021"
    assert payload["audit"]["source"] == "runtime_delivery_gate_script"
    assert payload["audit"]["hook_name"] == "runtime-delivery-gate-graphiti-closeout"


def test_process_closeout_skips_non_pass_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    runtime_summary_path = tmp_path / "summary.json"
    state_file = tmp_path / ".claude/runtime-delivery-gate-closeout-state.json"

    manifest_path.write_text(json.dumps({"overall_gate_status": "FAIL"}) + "\n", encoding="utf-8")
    runtime_summary_path.write_text(json.dumps({"overall_gate_status": "FAIL"}) + "\n", encoding="utf-8")

    result = closeout.process_closeout(
        project_root=tmp_path,
        manifest_path=manifest_path,
        runtime_summary_path=runtime_summary_path,
        gate_summary_path=None,
        state_file=state_file,
        max_wait_seconds=10,
    )

    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert result["status"] == "skipped_non_pass"
    assert state["reports"][-1]["status"] == "skipped_non_pass"
    assert state["processed"] == []


def test_runtime_delivery_gate_closeout_script_runs_with_external_graphiti_command(tmp_path: Path) -> None:
    manifest_path = tmp_path / "reports/analysis/runtime-delivery-gate/20260423-212355/runtime-delivery-gate-manifest.json"
    runtime_summary_path = tmp_path / "reports/analysis/runtime-delivery-gate/20260423-212355/runtime-quality-summary/summary.json"
    gate_summary_path = tmp_path / "reports/analysis/runtime-delivery-gate/20260423-212355/SUMMARY.md"
    args_path = tmp_path / "graphiti-args.json"
    fake_command = tmp_path / "fake_coordctl.sh"

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_summary_path.parent.mkdir(parents=True, exist_ok=True)
    gate_summary_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-23T21:23:55+08:00",
                "overall_gate_status": "PASS",
                "runtime_observability_drift_pass": True,
                "api_performance_drift_pass": True,
                "monitoring_rule_metric_reference_pass": True,
                "backend_runtime_dependency_pass": True,
                "container_deployment_contract_pass": True,
                "deployment_env_contract_pass": True,
                "docker_runtime_service_role": "backup_smoke",
                "docker_runtime_service_url_roles": {"backend": "backup_smoke", "frontend": "backup_smoke"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    runtime_summary_path.write_text(
        json.dumps({"generated_at": "2026-04-23T21:23:55+08:00", "overall_gate_status": "PASS"}) + "\n",
        encoding="utf-8",
    )
    gate_summary_path.write_text("# Full Runtime Delivery Gate\n", encoding="utf-8")

    fake_command.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                f"python -c 'import json,sys; open({json.dumps(str(args_path))}, \"w\", encoding=\"utf-8\").write(json.dumps(sys.argv[1:], ensure_ascii=False))' \"$@\"",
                "cat <<'EOF'",
                '{"server_status":"ok","ingest_status":"completed","episode_uuid":"ep-runtime-gate-1","group_id":"mystocks_spec_runtime_delivery_gates"}',
                "EOF",
            ]
        ),
        encoding="utf-8",
    )
    fake_command.chmod(0o755)

    env = os.environ.copy()
    env["RUNTIME_GATE_GRAPHITI_COMMAND"] = str(fake_command)
    env["RUNTIME_GATE_GRAPHITI_GROUP_ID"] = "mystocks_spec_runtime_delivery_gates"

    completed = subprocess.run(
        [
            "python",
            "scripts/runtime/record_runtime_delivery_gate_closeout.py",
            "--project-root",
            str(tmp_path),
            "--manifest-path",
            str(manifest_path),
            "--summary-json",
            str(runtime_summary_path),
            "--gate-summary-path",
            str(gate_summary_path),
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
    state_path = tmp_path / ".claude/runtime-delivery-gate-closeout-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))

    assert payload["status"] == "completed"
    assert payload["episode_uuid"] == "ep-runtime-gate-1"
    assert args[:2] == ["graphiti", "remember"]
    assert graphiti_payload["event_type"] == "runtime.delivery_gate_closeout"
    assert graphiti_payload["audit"]["hook_name"] == "runtime-delivery-gate-graphiti-closeout"
    assert state["reports"][-1]["status"] == "completed"
