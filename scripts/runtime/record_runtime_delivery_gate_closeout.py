#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_ACTOR_CLI = "codex"
DEFAULT_GROUP_ID_TEMPLATE = "{project_name}_runtime_delivery_gates"


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
    actor_cli = os.environ.get("RUNTIME_GATE_GRAPHITI_ACTOR_CLI", "").strip()
    if actor_cli:
        return actor_cli
    fallback = os.environ.get("GRAPHITI_CLOSEOUT_ACTOR_CLI", "").strip()
    if fallback:
        return fallback
    return DEFAULT_ACTOR_CLI


def resolve_group_id(project_root: Path) -> str:
    override = os.environ.get("RUNTIME_GATE_GRAPHITI_GROUP_ID", "").strip()
    if override:
        return override

    template = os.environ.get("RUNTIME_GATE_GRAPHITI_GROUP_ID_TEMPLATE", "").strip() or DEFAULT_GROUP_ID_TEMPLATE
    try:
        return template.format(project_name=project_root.name, project_root=str(project_root.resolve()))
    except Exception:
        return f"{project_root.name}_runtime_delivery_gates"


def build_graphiti_command(project_root: Path) -> list[str]:
    override = os.environ.get("RUNTIME_GATE_GRAPHITI_COMMAND", "").strip()
    if override:
        return shlex.split(override)
    legacy_override = os.environ.get("GRAPHITI_CLOSEOUT_COMMAND", "").strip()
    if legacy_override:
        return shlex.split(legacy_override)
    return [sys.executable, str(project_root / "scripts" / "runtime" / "coordctl.py")]


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


def build_verification_checks(manifest: dict[str, Any], runtime_summary: dict[str, Any]) -> list[str]:
    checks: list[str] = []
    if runtime_summary.get("overall_gate_status"):
        checks.append(f"overall_gate_status={runtime_summary['overall_gate_status']}")
    if manifest.get("runtime_observability_drift_pass") is not None:
        checks.append(f"runtime_observability_drift_pass={manifest['runtime_observability_drift_pass']}")
    if manifest.get("api_performance_drift_pass") is not None:
        checks.append(f"api_performance_drift_pass={manifest['api_performance_drift_pass']}")
    if manifest.get("monitoring_rule_metric_reference_pass") is not None:
        checks.append(f"monitoring_rule_metric_reference_pass={manifest['monitoring_rule_metric_reference_pass']}")
    if manifest.get("backend_runtime_dependency_pass") is not None:
        checks.append(f"backend_runtime_dependency_pass={manifest['backend_runtime_dependency_pass']}")
    if manifest.get("container_deployment_contract_pass") is not None:
        checks.append(f"container_deployment_contract_pass={manifest['container_deployment_contract_pass']}")
    if manifest.get("deployment_env_contract_pass") is not None:
        checks.append(f"deployment_env_contract_pass={manifest['deployment_env_contract_pass']}")
    if manifest.get("docker_runtime_service_role"):
        checks.append(f"docker_runtime_service_role={manifest['docker_runtime_service_role']}")
    return checks


def build_payload(
    *,
    project_root: Path,
    manifest_path: Path,
    runtime_summary_path: Path,
    gate_summary_path: Path | None,
    manifest: dict[str, Any],
    runtime_summary: dict[str, Any],
) -> dict[str, Any]:
    actor_cli = resolve_actor_cli()
    group_id = resolve_group_id(project_root)
    gate_run_id = manifest_path.resolve().parent.name
    generated_at = manifest.get("generated_at") or runtime_summary.get("generated_at") or ""
    summary = (
        f"Runtime delivery gate {runtime_summary.get('overall_gate_status') or manifest.get('overall_gate_status') or 'UNKNOWN'} "
        f"for {gate_run_id}"
    )

    return {
        "event_type": "runtime.delivery_gate_closeout",
        "title": f"Runtime Delivery Gate {gate_run_id}",
        "session_id": f"runtime-delivery-gate:{gate_run_id}",
        "actor_cli": actor_cli,
        "project_root": str(project_root.resolve()),
        "summary": summary[:180],
        "completion_phrase": "runtime delivery gate pass",
        "changed_files": [],
        "verification": {
            "machine_verified_checks": build_verification_checks(manifest, runtime_summary),
            "generated_at": generated_at,
            "overall_gate_status": runtime_summary.get("overall_gate_status") or manifest.get("overall_gate_status"),
            "docker_runtime_service_role": manifest.get("docker_runtime_service_role"),
        },
        "request_context": {
            "manifest_path": str(manifest_path.resolve()),
            "runtime_summary_path": str(runtime_summary_path.resolve()),
            "gate_summary_path": None if gate_summary_path is None else str(gate_summary_path.resolve()),
        },
        "gate": {
            "gate_kind": "full_runtime_delivery_gate",
            "gate_run_id": gate_run_id,
            "generated_at": generated_at,
            "canonical_service_urls": {
                "backend": "http://localhost:8020",
                "frontend": "http://localhost:3020",
            },
            "backup_smoke_service_urls": {
                "backend": "http://localhost:8021",
                "frontend": "http://localhost:3021",
            },
            "docker_runtime_service_role": manifest.get("docker_runtime_service_role"),
            "docker_runtime_service_url_roles": manifest.get("docker_runtime_service_url_roles"),
            "paths": {
                "manifest": _relative_path(project_root, manifest_path),
                "runtime_summary_json": _relative_path(project_root, runtime_summary_path),
                "gate_summary": _relative_path(project_root, gate_summary_path),
            },
        },
        "audit": {
            "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "group_id": group_id,
            "source": "runtime_delivery_gate_script",
            "hook_name": "runtime-delivery-gate-graphiti-closeout",
            "dedupe_key": f"runtime-delivery-gate:{gate_run_id}:{generated_at or 'unknown'}",
        },
    }


def process_closeout(
    *,
    project_root: Path,
    manifest_path: Path,
    runtime_summary_path: Path,
    gate_summary_path: Path | None,
    state_file: Path,
    max_wait_seconds: int,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    runtime_summary = load_json(runtime_summary_path)
    state = load_state(state_file)

    payload = build_payload(
        project_root=project_root,
        manifest_path=manifest_path,
        runtime_summary_path=runtime_summary_path,
        gate_summary_path=gate_summary_path,
        manifest=manifest,
        runtime_summary=runtime_summary,
    )
    dedupe_key = str(payload["audit"]["dedupe_key"])
    report = {
        "recorded_at": payload["audit"]["recorded_at"],
        "status": "failed",
        "session_id": payload["session_id"],
        "dedupe_key": dedupe_key,
        "summary": payload["summary"],
        "source": "runtime_delivery_gate_script",
        "manifest_path": str(manifest_path.resolve()),
        "runtime_summary_path": str(runtime_summary_path.resolve()),
        "gate_summary_path": None if gate_summary_path is None else str(gate_summary_path.resolve()),
    }

    processed = state.get("processed", [])
    if isinstance(processed, list) and dedupe_key in processed:
        report["status"] = "duplicate"
        report["group_id"] = payload["audit"]["group_id"]
        return {
            "status": "duplicate",
            "report": report,
            "state_file": str(state_file.resolve()),
            "group_id": payload["audit"]["group_id"],
        }

    overall_gate_status = str(runtime_summary.get("overall_gate_status") or manifest.get("overall_gate_status") or "").upper()
    if overall_gate_status != "PASS":
        report["status"] = "skipped_non_pass"
        report["overall_gate_status"] = overall_gate_status or None
        append_report(state, report)
        save_state(state_file, state)
        return {
            "status": "skipped_non_pass",
            "report": report,
            "state_file": str(state_file.resolve()),
            "group_id": payload["audit"]["group_id"],
        }

    try:
        result = write_graphiti_closeout(project_root, payload, max_wait_seconds=max_wait_seconds)
        processed_list = state.setdefault("processed", [])
        if isinstance(processed_list, list):
            processed_list.append(dedupe_key)
        report.update(
            {
                "status": "completed",
                "episode_uuid": result.get("episode_uuid"),
                "group_id": result.get("group_id"),
                "ingest_status": result.get("ingest_status"),
            }
        )
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
        return {
            "status": "failed",
            "report": report,
            "state_file": str(state_file.resolve()),
            "group_id": payload["audit"]["group_id"],
            "error": report["error"],
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record a full runtime delivery gate closeout into Graphiti.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifest-path", required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--gate-summary-path", default=None)
    parser.add_argument("--state-file", default=".claude/runtime-delivery-gate-closeout-state.json")
    parser.add_argument("--max-wait-seconds", type=int, default=60)
    parser.add_argument("--output", choices=("json", "text"), default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        return 0

    result = process_closeout(
        project_root=project_root,
        manifest_path=Path(args.manifest_path).resolve(),
        runtime_summary_path=Path(args.summary_json).resolve(),
        gate_summary_path=None if not args.gate_summary_path else Path(args.gate_summary_path).resolve(),
        state_file=(project_root / args.state_file).resolve() if not Path(args.state_file).is_absolute() else Path(args.state_file),
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
