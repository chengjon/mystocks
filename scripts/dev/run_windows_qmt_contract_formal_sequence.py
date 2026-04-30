from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = PROJECT_ROOT / "docs" / "reports" / "quality" / "windows-qmt-contract-acceptance"
DEFAULT_RUNTIME_ENVIRONMENT = "wsl-ubuntu-24.04.4-lts"
DEFAULT_CONTRACT_PROFILE = "kernel-phase-a"
DEFAULT_EXPECTED_PROVIDER_MODE = "mock"
DEFAULT_EXPECTED_ACCOUNT_SCOPE = "wsl-ubuntu-phase-a-acceptance"
DEFAULT_MOCK_OUTCOME = "acknowledgement"
FORMAL_SEQUENCE_SCHEMA_VERSION = 1
DEFAULT_BASE_URL_ENV = "TRADING_QMT_BRIDGE_BASE_URL"
DEFAULT_LATEST_SEQUENCE_FILENAME = "latest-formal-sequence.json"
SCRIPT_MODULE_CACHE: dict[str, Any] = {}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the formal Windows qmt contract acceptance sequence from WSL 上的 Ubuntu 24.04.4 LTS."
    )
    parser.add_argument("--base-url", default=None, help=f"Windows qmt service base URL. Defaults to ${DEFAULT_BASE_URL_ENV}.")
    parser.add_argument("--bridge-token", default=None, help="Optional Bearer token override.")
    parser.add_argument("--contract-version", default=None, help="Optional expected bridge contract version override.")
    parser.add_argument(
        "--contract-profile",
        default=DEFAULT_CONTRACT_PROFILE,
        choices=("reference-service", "kernel-phase-a"),
        help="Formal sequence contract profile. Defaults to kernel-phase-a for external miniQMT v1 alignment.",
    )
    parser.add_argument(
        "--expected-provider-mode",
        default=DEFAULT_EXPECTED_PROVIDER_MODE,
        help="Expected safe provider mode for full smoke execution.",
    )
    parser.add_argument("--expected-source-name", default=None, help="Optional explicit source_name expectation override.")
    parser.add_argument(
        "--expected-account-scope",
        default=DEFAULT_EXPECTED_ACCOUNT_SCOPE,
        help="Account scope to send and verify during the smoke run.",
    )
    parser.add_argument("--mock-outcome", default=DEFAULT_MOCK_OUTCOME, help="Requested mock outcome for the remote service.")
    parser.add_argument("--mock-delay-seconds", type=float, default=0.0, help="Requested mock pending delay before terminal result.")
    parser.add_argument("--timeout-seconds", type=float, default=None, help="Optional end-to-end timeout override.")
    parser.add_argument("--poll-interval-seconds", type=float, default=None, help="Optional polling interval override.")
    parser.add_argument(
        "--allow-non-mock-provider-mode",
        action="store_true",
        help="Override the default fail-closed provider_mode gate during contract verification.",
    )
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR), help="Directory for acceptance and formal sequence artifacts.")
    parser.add_argument("--compare-with", default=None, help="Optional explicit baseline JSON path for contract comparison.")
    parser.add_argument(
        "--compare-with-latest-baseline",
        action="store_true",
        help="Resolve the standard <report-dir>/baselines/latest-baseline.json path automatically.",
    )
    parser.add_argument(
        "--freeze-baseline",
        action="store_true",
        help="After verification and summary, run the explicit baseline freeze step.",
    )
    parser.add_argument(
        "--baseline-dir",
        default=None,
        help="Optional explicit baseline output directory used by the freeze step.",
    )
    return parser.parse_args(argv)


def _load_script_module(script_name: str, module_name: str) -> Any:
    cached = SCRIPT_MODULE_CACHE.get(module_name)
    if cached is not None:
        return cached
    module_path = PROJECT_ROOT / "scripts" / "dev" / script_name
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load helper script module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    SCRIPT_MODULE_CACHE[module_name] = module
    return module


def build_verify_command(args: argparse.Namespace) -> list[str]:
    command = [
        "verify",
        "windows-qmt",
        "--report-dir",
        str(getattr(args, "report_dir")),
        "--contract-profile",
        str(getattr(args, "contract_profile")),
        "--expected-provider-mode",
        str(getattr(args, "expected_provider_mode")),
        "--expected-account-scope",
        str(getattr(args, "expected_account_scope")),
        "--mock-outcome",
        str(getattr(args, "mock_outcome")),
    ]
    if getattr(args, "base_url", None):
        command.extend(["--base-url", str(getattr(args, "base_url"))])
    if getattr(args, "bridge_token", None):
        command.extend(["--bridge-token", str(getattr(args, "bridge_token"))])
    if getattr(args, "contract_version", None):
        command.extend(["--contract-version", str(getattr(args, "contract_version"))])
    if getattr(args, "expected_source_name", None):
        command.extend(["--expected-source-name", str(getattr(args, "expected_source_name"))])
    if float(getattr(args, "mock_delay_seconds", 0.0)) > 0:
        command.extend(["--mock-delay-seconds", str(getattr(args, "mock_delay_seconds"))])
    if getattr(args, "timeout_seconds", None) is not None:
        command.extend(["--timeout-seconds", str(getattr(args, "timeout_seconds"))])
    if getattr(args, "poll_interval_seconds", None) is not None:
        command.extend(["--poll-interval-seconds", str(getattr(args, "poll_interval_seconds"))])
    if bool(getattr(args, "allow_non_mock_provider_mode", False)):
        command.append("--allow-non-mock-provider-mode")
    if getattr(args, "compare_with", None):
        command.extend(["--compare-with", str(getattr(args, "compare_with"))])
    if bool(getattr(args, "compare_with_latest_baseline", False)):
        command.append("--compare-with-latest-baseline")
    return command


def build_summarize_command(args: argparse.Namespace) -> list[str]:
    return [
        "summarize",
        "windows-qmt",
        "--report-dir",
        str(getattr(args, "report_dir")),
        "--json",
    ]


def build_freeze_command(args: argparse.Namespace) -> list[str]:
    command = [
        "freeze",
        "windows-qmt",
        "--report-dir",
        str(getattr(args, "report_dir")),
    ]
    if getattr(args, "baseline_dir", None):
        command.extend(["--baseline-dir", str(getattr(args, "baseline_dir"))])
    return command


def _dispatch_command(command: list[str]) -> tuple[Any, list[str]]:
    prefix = tuple(command[:2])
    argv = command[2:]
    if prefix == ("verify", "windows-qmt"):
        return _load_script_module("verify_windows_qmt_agent_contract.py", "verify_windows_qmt_agent_contract"), argv
    if prefix == ("summarize", "windows-qmt"):
        return _load_script_module(
            "summarize_windows_qmt_acceptance_reports.py",
            "summarize_windows_qmt_acceptance_reports",
        ), argv
    if prefix == ("freeze", "windows-qmt"):
        return _load_script_module(
            "freeze_windows_qmt_acceptance_baseline.py",
            "freeze_windows_qmt_acceptance_baseline",
        ), argv
    raise ValueError(f"unsupported formal sequence command: {command}")


def run_step_command(command: list[str]) -> tuple[int, dict[str, Any]]:
    module, argv = _dispatch_command(command)
    stdout_buffer = io.StringIO()
    with contextlib.redirect_stdout(stdout_buffer):
        exit_code = int(module.main(argv))
    raw_output = stdout_buffer.getvalue().strip()
    if not raw_output:
        return exit_code, {"raw_output": "", "issues": ["step produced no stdout payload"]}
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        payload = {"raw_output": raw_output}
    if isinstance(payload, Mapping):
        return exit_code, dict(payload)
    return exit_code, {"raw_output": raw_output}


def run_preflight(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    resolved_base_url = str(getattr(args, "base_url") or os.getenv(DEFAULT_BASE_URL_ENV, "")).strip() or None
    report_dir = Path(str(getattr(args, "report_dir")))
    report_dir.mkdir(parents=True, exist_ok=True)
    issues: list[str] = []
    if resolved_base_url is None:
        issues.append(f"base_url is required; provide --base-url or set {DEFAULT_BASE_URL_ENV}")

    payload = {
        "status_label": "completed" if not issues else "configuration_invalid",
        "recommended_exit_code": 0 if not issues else 2,
        "resolved_base_url": resolved_base_url,
        "report_dir": str(report_dir),
        "contract_profile": str(getattr(args, "contract_profile")),
        "compare_requested": bool(getattr(args, "compare_with", None) or getattr(args, "compare_with_latest_baseline", False)),
        "freeze_requested": bool(getattr(args, "freeze_baseline", False)),
        "issues": issues,
    }
    return int(payload["recommended_exit_code"]), payload


def build_compare_step(args: argparse.Namespace, verify_exit_code: int, verify_payload: Mapping[str, Any]) -> dict[str, Any]:
    compare_requested = bool(getattr(args, "compare_with", None) or getattr(args, "compare_with_latest_baseline", False))
    if not compare_requested:
        return {
            "name": "compare",
            "exit_code": 0,
            "status_label": "skipped",
        }

    comparison_payload = verify_payload.get("comparison")
    comparison = comparison_payload if isinstance(comparison_payload, Mapping) else None
    if comparison is not None:
        comparison_ok = comparison.get("ok") is True
        return {
            "name": "compare",
            "exit_code": 0 if comparison_ok else 3,
            "status_label": "completed" if comparison_ok else "contract_drift_detected",
            "baseline_path": comparison.get("baseline_path"),
            "mismatch_count": len(comparison.get("mismatches", [])) if isinstance(comparison.get("mismatches"), list) else 0,
        }

    if verify_payload.get("ok") is not True:
        return {
            "name": "compare",
            "exit_code": verify_exit_code if verify_exit_code else 1,
            "status_label": "skipped_due_to_verify_failure",
        }

    return {
        "name": "compare",
        "exit_code": 2,
        "status_label": "comparison_unavailable",
    }


def build_step(
    name: str,
    *,
    exit_code: int,
    status_label: str,
    command: list[str] | None = None,
) -> dict[str, Any]:
    payload = {
        "name": name,
        "exit_code": exit_code,
        "status_label": status_label,
    }
    if command:
        payload["command"] = list(command)
    return payload


def build_output_metadata(*, now: datetime | None = None) -> dict[str, Any]:
    return {
        "formal_sequence_schema_version": FORMAL_SEQUENCE_SCHEMA_VERSION,
        "runtime_environment": DEFAULT_RUNTIME_ENVIRONMENT,
        "generated_at": (now or datetime.now(timezone.utc)).isoformat(),
    }


def write_json_output(payload: Mapping[str, Any], output_path: str | Path) -> Path:
    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target_path


def build_timestamped_manifest_output_path(report_dir: str | Path, *, now: datetime | None = None) -> Path:
    timestamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    return Path(report_dir) / f"{timestamp}-windows-qmt-contract-formal-sequence.json"


def persist_sequence_manifest(manifest: Mapping[str, Any], *, report_dir: str | Path, now: datetime | None = None) -> dict[str, str]:
    report_root = Path(report_dir)
    manifest_output = build_timestamped_manifest_output_path(report_root, now=now)
    latest_output = report_root / DEFAULT_LATEST_SEQUENCE_FILENAME
    write_json_output(manifest, manifest_output)
    write_json_output(manifest, latest_output)
    return {
        "manifest_output": str(manifest_output),
        "latest_manifest_output": str(latest_output),
    }


def determine_exit_code(*codes: int) -> int:
    return max(codes) if codes else 0


def determine_status_label(exit_code: int) -> str:
    if exit_code == 0:
        return "formal_sequence_completed"
    if exit_code == 3:
        return "formal_sequence_contract_drift"
    return "formal_sequence_failed"


def build_manifest(
    args: argparse.Namespace,
    *,
    preflight_payload: Mapping[str, Any],
    preflight_exit_code: int,
    steps: list[dict[str, Any]],
    verify_payload: Mapping[str, Any] | None = None,
    summary_payload: Mapping[str, Any] | None = None,
    freeze_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    exit_code = determine_exit_code(
        preflight_exit_code,
        *(int(step.get("exit_code", 0)) for step in steps if step.get("name") != "preflight"),
    )
    manifest = {
        "status_label": determine_status_label(exit_code),
        "recommended_exit_code": exit_code,
        "base_url": preflight_payload.get("resolved_base_url"),
        "report_dir": str(getattr(args, "report_dir")),
        "expected": {
            "contract_profile": str(getattr(args, "contract_profile")),
            "compare_with_latest_baseline": bool(getattr(args, "compare_with_latest_baseline", False)),
            "compare_with": getattr(args, "compare_with", None),
            "freeze_baseline": bool(getattr(args, "freeze_baseline", False)),
        },
        "preflight": dict(preflight_payload),
        "steps": steps,
    }
    if verify_payload is not None:
        manifest["verify"] = dict(verify_payload)
    if summary_payload is not None:
        manifest["summary"] = dict(summary_payload)
    if freeze_payload is not None:
        manifest["freeze"] = dict(freeze_payload)
    manifest.update(build_output_metadata())
    return manifest


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    preflight_exit_code, preflight_payload = run_preflight(args)
    steps: list[dict[str, Any]] = [
        build_step(
            "preflight",
            exit_code=preflight_exit_code,
            status_label=str(preflight_payload.get("status_label")),
        )
    ]

    verify_payload: dict[str, Any] | None = None
    summary_payload: dict[str, Any] | None = None
    freeze_payload: dict[str, Any] | None = None

    if preflight_exit_code == 0:
        verify_command = build_verify_command(args)
        verify_exit_code, verify_payload = run_step_command(verify_command)
        steps.append(
            build_step(
                "verify",
                exit_code=verify_exit_code,
                status_label="completed" if verify_exit_code == 0 else "failed",
                command=verify_command,
            )
        )

        compare_step = build_compare_step(args, verify_exit_code, verify_payload)
        steps.append(compare_step)

        summarize_command = build_summarize_command(args)
        summarize_exit_code, summary_payload = run_step_command(summarize_command)
        steps.append(
            build_step(
                "summarize",
                exit_code=summarize_exit_code,
                status_label="completed" if summarize_exit_code == 0 else "failed",
                command=summarize_command,
            )
        )

        if bool(getattr(args, "freeze_baseline", False)):
            freeze_command = build_freeze_command(args)
            freeze_exit_code, freeze_payload = run_step_command(freeze_command)
            steps.append(
                build_step(
                    "freeze",
                    exit_code=freeze_exit_code,
                    status_label="completed" if freeze_exit_code == 0 else "failed",
                    command=freeze_command,
                )
            )

    manifest = build_manifest(
        args,
        preflight_payload=preflight_payload,
        preflight_exit_code=preflight_exit_code,
        steps=steps,
        verify_payload=verify_payload,
        summary_payload=summary_payload,
        freeze_payload=freeze_payload,
    )
    artifacts = persist_sequence_manifest(manifest, report_dir=str(getattr(args, "report_dir")))
    manifest["artifacts"] = artifacts
    persist_sequence_manifest(manifest, report_dir=str(getattr(args, "report_dir")))
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return int(manifest["recommended_exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
