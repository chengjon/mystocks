#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_ACTOR_CLI = "codex"
DEFAULT_GROUP_ID_TEMPLATE = "{project_name}_quality_gates"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_state(state_file: Path) -> dict[str, Any]:
    if not state_file.exists():
        return {"processed": [], "reports": []}
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return {"processed": [], "reports": []}
    if not isinstance(data, dict):
        return {"processed": [], "reports": []}
    if not isinstance(data.get("processed"), list):
        data["processed"] = []
    if not isinstance(data.get("reports"), list):
        data["reports"] = []
    return data


def save_state(state_file: Path, state: dict[str, Any]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    processed = state.get("processed", [])
    if isinstance(processed, list) and len(processed) > 2000:
        state["processed"] = processed[-1000:]
    reports = state.get("reports", [])
    if isinstance(reports, list) and len(reports) > 500:
        state["reports"] = reports[-200:]
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_report(state: dict[str, Any], report: dict[str, Any]) -> None:
    reports = state.setdefault("reports", [])
    if not isinstance(reports, list):
        reports = []
        state["reports"] = reports
    reports.append(report)


def resolve_actor_cli() -> str:
    actor_cli = os.environ.get("QUALITY_GATE_GRAPHITI_ACTOR_CLI", "").strip()
    if actor_cli:
        return actor_cli
    fallback = os.environ.get("GRAPHITI_CLOSEOUT_ACTOR_CLI", "").strip()
    if fallback:
        return fallback
    return DEFAULT_ACTOR_CLI


def resolve_group_id(project_root: Path) -> str:
    override = os.environ.get("QUALITY_GATE_GRAPHITI_GROUP_ID", "").strip()
    if override:
        return override

    template = os.environ.get("QUALITY_GATE_GRAPHITI_GROUP_ID_TEMPLATE", "").strip() or DEFAULT_GROUP_ID_TEMPLATE
    try:
        return template.format(project_name=project_root.name, project_root=str(project_root.resolve()))
    except Exception:
        return f"{project_root.name}_quality_gates"


def build_graphiti_command(project_root: Path) -> list[str]:
    override = os.environ.get("QUALITY_GATE_GRAPHITI_COMMAND", "").strip()
    if override:
        return shlex.split(override)
    legacy_override = os.environ.get("GRAPHITI_CLOSEOUT_COMMAND", "").strip()
    if legacy_override:
        return shlex.split(legacy_override)
    return [sys.executable, str(project_root / "scripts" / "runtime" / "coordctl.py")]


def default_state_file(project_root: Path, gate_kind: str) -> Path:
    override_dir = os.environ.get("QUALITY_GATE_GRAPHITI_STATE_DIR", "").strip()
    base_dir = Path(override_dir) if override_dir else Path(tempfile.gettempdir()) / "mystocks-quality-gate-closeout-state"
    return (base_dir / project_root.name / f"{gate_kind}.json").resolve()


def write_graphiti_closeout(project_root: Path, payload: dict[str, Any], *, max_wait_seconds: int) -> dict[str, Any]:
    command = build_graphiti_command(project_root)
    completed = subprocess.run(
        [
            *command,
            "graphiti",
            "remember",
            "--actor-cli",
            str(payload["actor_cli"]),
            "--group-id",
            str(payload["audit"]["group_id"]),
            "--name",
            str(payload["title"]),
            "--body",
            json.dumps(payload, ensure_ascii=False),
            "--max-wait-seconds",
            str(max_wait_seconds),
            "--output",
            "json",
        ],
        text=True,
        capture_output=True,
        cwd=project_root,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "graphiti command failed")
    result = json.loads(completed.stdout or "{}")
    if not result.get("episode_uuid") or not result.get("group_id"):
        raise RuntimeError("graphiti command returned incomplete durable metadata")
    return result


def _relative_path(project_root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(project_root.resolve()))
    except Exception:
        return str(path.resolve())


def _load_gate_artifacts(gate_kind: str, report_dir: Path) -> dict[str, Any]:
    if gate_kind == "frontend-runtime-gate":
        gate_json_path = report_dir / "frontend-runtime-gate.json"
        return {
            "summary_path": report_dir / "SUMMARY.md",
            "primary_json_path": gate_json_path,
            "artifacts": {
                "frontend_runtime_gate": load_json(gate_json_path),
                "baseline": load_json(report_dir / "tech-debt-baseline.current.json"),
            },
        }
    if gate_kind == "api-performance-gate":
        benchmark_path = report_dir / "benchmark.json"
        return {
            "summary_path": report_dir / "SUMMARY.md",
            "primary_json_path": benchmark_path,
            "artifacts": {
                "benchmark": load_json(benchmark_path),
                "metrics_summary": load_json(report_dir / "metrics-summary.json"),
            },
        }
    if gate_kind == "docker-runtime-smoke":
        docker_json_path = report_dir / "docker-runtime-smoke.json"
        return {
            "summary_path": report_dir / "SUMMARY.md",
            "primary_json_path": docker_json_path,
            "artifacts": {
                "docker_runtime": load_json(docker_json_path),
            },
        }
    if gate_kind == "monitoring-auth-performance-gate":
        benchmark_path = report_dir / "benchmark.json"
        return {
            "summary_path": report_dir / "SUMMARY.md",
            "primary_json_path": benchmark_path,
            "artifacts": {
                "benchmark": load_json(benchmark_path),
                "metrics_summary": load_json(report_dir / "metrics-summary.json"),
                "login_response": load_json(report_dir / "login-response.json"),
            },
        }
    raise ValueError(f"Unsupported gate kind: {gate_kind}")


def _frontend_gate_pass(payload: dict[str, Any]) -> bool:
    gate_json = payload["artifacts"]["frontend_runtime_gate"]
    online = set(gate_json.get("pm2_services_online", []))
    regression = gate_json.get("regression_e2e_counts", {})
    structural = gate_json.get("structural_gate_counts", {})
    accessibility = gate_json.get("accessibility_smoke_counts", {})
    current_errors = gate_json.get("current_frontend_type_errors")
    baseline_errors = gate_json.get("repo_frontend_type_error_baseline")
    return (
        {"mystocks-backend", "mystocks-frontend"}.issubset(online)
        and regression.get("failed", 1) == 0
        and structural.get("failed", 1) == 0
        and accessibility.get("failed", 1) == 0
        and isinstance(current_errors, int)
        and isinstance(baseline_errors, int)
        and current_errors <= baseline_errors
    )


def _api_gate_pass(payload: dict[str, Any]) -> bool:
    benchmark = payload["artifacts"]["benchmark"]
    metrics_summary = payload["artifacts"]["metrics_summary"]
    return bool(benchmark.get("slo_status", {}).get("compliant")) and metrics_summary.get("metrics_health", {}).get("status") == "healthy"


def _docker_gate_pass(payload: dict[str, Any]) -> bool:
    docker_runtime = payload["artifacts"]["docker_runtime"]
    checks = docker_runtime.get("checks", {})
    return (
        checks.get("backend_health") == "PASS"
        and checks.get("backend_readiness") == "PASS"
        and checks.get("frontend_index") == "PASS"
        and docker_runtime.get("metrics_health") == "healthy"
    )


def _monitoring_auth_gate_pass(payload: dict[str, Any]) -> bool:
    benchmark = payload["artifacts"]["benchmark"]
    metrics_summary = payload["artifacts"]["metrics_summary"]
    return bool(benchmark.get("slo_status", {}).get("compliant")) and metrics_summary.get("metrics_health", {}).get("status") == "healthy"


def gate_passes(gate_kind: str, payload: dict[str, Any]) -> bool:
    if gate_kind == "frontend-runtime-gate":
        return _frontend_gate_pass(payload)
    if gate_kind == "api-performance-gate":
        return _api_gate_pass(payload)
    if gate_kind == "docker-runtime-smoke":
        return _docker_gate_pass(payload)
    if gate_kind == "monitoring-auth-performance-gate":
        return _monitoring_auth_gate_pass(payload)
    return False


def gate_title(gate_kind: str) -> str:
    if gate_kind == "frontend-runtime-gate":
        return "Frontend Runtime Gate"
    if gate_kind == "api-performance-gate":
        return "API Performance Gate"
    if gate_kind == "docker-runtime-smoke":
        return "Docker Runtime Smoke"
    if gate_kind == "monitoring-auth-performance-gate":
        return "Monitoring Auth Performance Gate"
    return gate_kind


def build_verification_checks(gate_kind: str, payload: dict[str, Any]) -> list[str]:
    if gate_kind == "frontend-runtime-gate":
        gate_json = payload["artifacts"]["frontend_runtime_gate"]
        return [
            f"structural_gate={gate_json.get('structural_gate')}",
            f"type_errors={gate_json.get('current_frontend_type_errors')}",
            f"type_error_baseline={gate_json.get('repo_frontend_type_error_baseline')}",
            f"regression_e2e={gate_json.get('regression_e2e')}",
            f"regression_pytest={gate_json.get('regression_pytest')}",
            f"accessibility_smoke={gate_json.get('accessibility_smoke')}",
            f"pm2_services_online={','.join(gate_json.get('pm2_services_online', []))}",
        ]
    if gate_kind == "api-performance-gate":
        benchmark = payload["artifacts"]["benchmark"]
        metrics_summary = payload["artifacts"]["metrics_summary"]
        return [
            f"slo_compliant={benchmark.get('slo_status', {}).get('compliant')}",
            f"overall_p95_ms={benchmark.get('summary', {}).get('overall_p95_ms')}",
            f"business_p95_ms={benchmark.get('workload_classes', {}).get('business', {}).get('overall_p95_ms')}",
            f"infrastructure_p95_ms={benchmark.get('workload_classes', {}).get('infrastructure', {}).get('overall_p95_ms')}",
            f"metrics_health={metrics_summary.get('metrics_health', {}).get('status')}",
        ]
    if gate_kind == "monitoring-auth-performance-gate":
        benchmark = payload["artifacts"]["benchmark"]
        metrics_summary = payload["artifacts"]["metrics_summary"]
        login_response = payload["artifacts"]["login_response"]
        return [
            f"slo_compliant={benchmark.get('slo_status', {}).get('compliant')}",
            f"alert_rules_p95_ms={(benchmark.get('endpoints') or [{}])[0].get('p95_ms') if benchmark.get('endpoints') else None}",
            f"alerts_p95_ms={(benchmark.get('endpoints') or [{}, {}])[1].get('p95_ms') if len(benchmark.get('endpoints') or []) > 1 else None}",
            f"metrics_health={metrics_summary.get('metrics_health', {}).get('status')}",
            f"auth_user={(login_response.get('data') or {}).get('user', {}).get('username')}",
        ]
    docker_runtime = payload["artifacts"]["docker_runtime"]
    return [
        f"backend_health={docker_runtime.get('checks', {}).get('backend_health')}",
        f"backend_readiness={docker_runtime.get('checks', {}).get('backend_readiness')}",
        f"frontend_index={docker_runtime.get('checks', {}).get('frontend_index')}",
        f"metrics_health={docker_runtime.get('metrics_health')}",
        f"service_role={docker_runtime.get('service_role')}",
    ]


def build_payload(*, gate_kind: str, project_root: Path, report_dir: Path) -> dict[str, Any]:
    gate_payload = _load_gate_artifacts(gate_kind, report_dir)
    primary_json_path = gate_payload["primary_json_path"]
    primary_json = load_json(primary_json_path)
    generated_at = primary_json.get("generated_at") or datetime.now().astimezone().isoformat(timespec="seconds")
    run_id = report_dir.name
    title = gate_title(gate_kind)
    payload = {
        "event_type": f"quality_gate.closeout.{gate_kind}",
        "title": f"{title} {run_id}",
        "session_id": f"{gate_kind}:{run_id}",
        "actor_cli": resolve_actor_cli(),
        "project_root": str(project_root.resolve()),
        "summary": f"{title} PASS for {run_id}",
        "completion_phrase": f"{gate_kind} pass",
        "changed_files": [],
        "verification": {
            "machine_verified_checks": [],
            "generated_at": generated_at,
        },
        "request_context": {
            "report_dir": str(report_dir.resolve()),
            "summary_path": str(gate_payload["summary_path"].resolve()),
            "primary_json_path": str(primary_json_path.resolve()),
        },
        "gate": {
            "gate_kind": gate_kind,
            "gate_run_id": run_id,
            "generated_at": generated_at,
            "paths": {
                "report_dir": _relative_path(project_root, report_dir),
                "summary": _relative_path(project_root, gate_payload["summary_path"]),
                "primary_json": _relative_path(project_root, primary_json_path),
            },
        },
        "audit": {
            "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "group_id": resolve_group_id(project_root),
            "source": "quality_gate_script",
            "hook_name": "quality-gate-graphiti-closeout",
            "dedupe_key": f"{gate_kind}:{run_id}:{generated_at}",
        },
        "artifacts": gate_payload["artifacts"],
    }

    if gate_kind == "frontend-runtime-gate":
        payload["gate"]["canonical_service_urls"] = primary_json.get("service_urls", {})
    elif gate_kind == "api-performance-gate":
        payload["gate"]["canonical_service_urls"] = {
            "backend": primary_json.get("base_url", "http://localhost:8020"),
            "frontend": "http://localhost:3020",
        }
    elif gate_kind == "monitoring-auth-performance-gate":
        payload["gate"]["canonical_service_urls"] = {
            "backend": "http://localhost:8020",
            "frontend": "http://localhost:3020",
        }
    else:
        payload["gate"]["backup_smoke_service_urls"] = primary_json.get("service_urls", {})
        payload["gate"]["docker_runtime_service_role"] = primary_json.get("service_role")

    payload["verification"]["machine_verified_checks"] = build_verification_checks(gate_kind, payload)
    return payload


def process_closeout(
    *,
    gate_kind: str,
    project_root: Path,
    report_dir: Path,
    state_file: Path,
    max_wait_seconds: int,
) -> dict[str, Any]:
    payload = build_payload(gate_kind=gate_kind, project_root=project_root, report_dir=report_dir)
    state = load_state(state_file)
    dedupe_key = str(payload["audit"]["dedupe_key"])
    report = {
        "recorded_at": payload["audit"]["recorded_at"],
        "status": "failed",
        "session_id": payload["session_id"],
        "dedupe_key": dedupe_key,
        "summary": payload["summary"],
        "source": "quality_gate_script",
        "gate_kind": gate_kind,
        "report_dir": str(report_dir.resolve()),
    }

    processed = state.get("processed", [])
    if isinstance(processed, list) and dedupe_key in processed:
        report["status"] = "duplicate"
        report["group_id"] = payload["audit"]["group_id"]
        return {"status": "duplicate", "report": report, "state_file": str(state_file.resolve()), "group_id": payload["audit"]["group_id"]}

    if not gate_passes(gate_kind, payload):
        report["status"] = "skipped_non_pass"
        append_report(state, report)
        save_state(state_file, state)
        return {"status": "skipped_non_pass", "report": report, "state_file": str(state_file.resolve()), "group_id": payload["audit"]["group_id"]}

    try:
        result = write_graphiti_closeout(project_root, payload, max_wait_seconds=max_wait_seconds)
        processed_list = state.setdefault("processed", [])
        if isinstance(processed_list, list):
            processed_list.append(dedupe_key)
        report.update({"status": "completed", "episode_uuid": result.get("episode_uuid"), "group_id": result.get("group_id"), "ingest_status": result.get("ingest_status")})
        append_report(state, report)
        save_state(state_file, state)
        return {
            "status": "completed",
            "report": report,
            "state_file": str(state_file.resolve()),
            "episode_uuid": result.get("episode_uuid"),
            "group_id": result.get("group_id"),
            "ingest_status": result.get("ingest_status"),
        }
    except Exception as exc:
        report["error"] = str(exc)[:500]
        append_report(state, report)
        save_state(state_file, state)
        return {"status": "failed", "report": report, "state_file": str(state_file.resolve()), "group_id": payload["audit"]["group_id"], "error": report["error"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record a quality gate closeout into Graphiti.")
    parser.add_argument(
        "--gate-kind",
        choices=("frontend-runtime-gate", "api-performance-gate", "docker-runtime-smoke", "monitoring-auth-performance-gate"),
        required=True,
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--state-file", default=None)
    parser.add_argument("--max-wait-seconds", type=int, default=60)
    parser.add_argument("--output", choices=("json", "text"), default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        return 0

    result = process_closeout(
        gate_kind=args.gate_kind,
        project_root=project_root,
        report_dir=Path(args.report_dir).resolve(),
        state_file=(
            default_state_file(project_root, args.gate_kind)
            if not args.state_file
            else ((project_root / args.state_file).resolve() if not Path(args.state_file).is_absolute() else Path(args.state_file))
        ),
        max_wait_seconds=max(args.max_wait_seconds, 1),
    )

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status={result['status']}")
        report = result.get("report", {})
        if isinstance(report, dict):
            print(f"group_id={report.get('group_id') or result.get('group_id')}")
            print(f"episode_uuid={report.get('episode_uuid') or result.get('episode_uuid')}")
            print(f"summary={report.get('summary')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
