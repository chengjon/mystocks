from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Awaitable, Callable, Mapping

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_BACKEND_ROOT = PROJECT_ROOT / "web" / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(WEB_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(WEB_BACKEND_ROOT))

from src.utils.trading_runtime_config import (  # noqa: E402
    get_trading_miniqmt_live_bridge_timeout_seconds,
    get_trading_qmt_bridge_contract_version,
    get_trading_qmt_bridge_token,
)

DEFAULT_BASE_URL_ENV = "TRADING_QMT_BRIDGE_BASE_URL"
DEFAULT_RUNTIME_ENVIRONMENT = "wsl-ubuntu-24.04.4-lts"
DEFAULT_CONTRACT_PROFILE = "kernel-phase-a"
REFERENCE_SERVICE_CONTRACT_PROFILE = "reference-service"
DEFAULT_EXPECTED_PROVIDER_MODE = "mock"
DEFAULT_REFERENCE_SOURCE_NAME = "qmt/windows_reference_service"
KERNEL_PHASE_A_CONTRACT_PROFILE = "kernel-phase-a"
SUMMARY_SCHEMA_VERSION = 1
DEFAULT_REPORT_DIR = PROJECT_ROOT / "docs" / "reports" / "quality" / "windows-qmt-contract-acceptance" / "readiness"


@dataclass(slots=True)
class ReadinessProbeConfig:
    base_url: str
    bridge_token: str
    bridge_contract_version: str
    contract_profile: str = DEFAULT_CONTRACT_PROFILE
    expected_provider_mode: str = DEFAULT_EXPECTED_PROVIDER_MODE
    expected_source_name: str | None = None
    timeout_seconds: float = 15.0


HealthFetcher = Callable[[str, float], Awaitable[dict[str, Any]]]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe Windows qmt / miniQMT service readiness from WSL 上的 Ubuntu 24.04.4 LTS."
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help=f"Windows qmt service base URL. Defaults to ${DEFAULT_BASE_URL_ENV}.",
    )
    parser.add_argument(
        "--bridge-token",
        default=get_trading_qmt_bridge_token(),
        help="Optional Bearer token override. Used only for local readiness disclosure, not for remote execution.",
    )
    parser.add_argument(
        "--contract-version",
        default=get_trading_qmt_bridge_contract_version(),
        help="Expected bridge contract version.",
    )
    parser.add_argument(
        "--contract-profile",
        default=DEFAULT_CONTRACT_PROFILE,
        choices=(REFERENCE_SERVICE_CONTRACT_PROFILE, KERNEL_PHASE_A_CONTRACT_PROFILE),
        help="Readiness contract profile. Defaults to kernel-phase-a for external miniQMT v1 alignment.",
    )
    parser.add_argument(
        "--expected-provider-mode",
        default=DEFAULT_EXPECTED_PROVIDER_MODE,
        help="Expected provider mode for the upcoming local acceptance run.",
    )
    parser.add_argument(
        "--expected-source-name",
        default=None,
        help="Optional explicit expected source_name override.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=get_trading_miniqmt_live_bridge_timeout_seconds(),
        help="Health probe timeout in seconds.",
    )
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory for readiness artifacts.",
    )
    return parser.parse_args(argv)


async def fetch_health_payload(base_url: str, timeout_seconds: float) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.get(f"{base_url.rstrip('/')}/health")
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, Mapping):
        raise ValueError("Windows qmt /health payload must be a JSON object")
    return dict(payload)


async def run_readiness_probe(
    config: ReadinessProbeConfig,
    *,
    health_fetcher: HealthFetcher = fetch_health_payload,
) -> dict[str, Any]:
    expected_source_name = resolve_expected_source_name(config)
    summary: dict[str, Any] = {
        "ok": False,
        "status_label": "not_ready",
        "recommended_exit_code": 1,
        "summary_schema_version": SUMMARY_SCHEMA_VERSION,
        "runtime_environment": DEFAULT_RUNTIME_ENVIRONMENT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": config.base_url,
        "expected": {
            "contract_profile": config.contract_profile,
            "provider_mode": config.expected_provider_mode,
            "bridge_contract_version": config.bridge_contract_version,
            "source_name": expected_source_name,
        },
        "local_config": {
            "base_url_configured": bool(str(config.base_url).strip()),
            "bridge_token_configured": bool(str(config.bridge_token).strip()),
        },
        "health": None,
        "levels": {
            "l1_process_ready": {"passed": False, "verified_fields": [], "issues": []},
            "l2_contract_ready": {"passed": False, "verified_fields": [], "issues": []},
            "l3_acceptance_ready": {"passed": False, "verified_fields": [], "issues": []},
        },
        "issues": [],
    }

    try:
        health_payload = await health_fetcher(config.base_url, config.timeout_seconds)
    except Exception as exc:
        l1_issues = [f"health probe failed: {exc}"]
        summary["health"] = None
        summary["levels"]["l1_process_ready"]["issues"] = l1_issues
        summary["issues"] = l1_issues
        return summary

    summary["health"] = health_payload
    summary["levels"]["l1_process_ready"]["passed"] = True
    summary["levels"]["l1_process_ready"]["verified_fields"] = ["health.reachable", "health.json_object"]

    l2_verified, l2_issues = _evaluate_l2_contract_readiness(health_payload, config)
    summary["levels"]["l2_contract_ready"]["verified_fields"] = l2_verified
    summary["levels"]["l2_contract_ready"]["issues"] = l2_issues
    summary["levels"]["l2_contract_ready"]["passed"] = not l2_issues

    l3_verified, l3_issues = _evaluate_l3_acceptance_readiness(health_payload, config, expected_source_name)
    summary["levels"]["l3_acceptance_ready"]["verified_fields"] = l3_verified
    summary["levels"]["l3_acceptance_ready"]["issues"] = l3_issues
    summary["levels"]["l3_acceptance_ready"]["passed"] = not l3_issues and not l2_issues

    if summary["levels"]["l3_acceptance_ready"]["passed"]:
        summary["ok"] = True
        summary["status_label"] = "l3_acceptance_ready"
        summary["recommended_exit_code"] = 0
        summary["issues"] = []
        return summary

    if summary["levels"]["l2_contract_ready"]["passed"]:
        summary["status_label"] = "l2_contract_ready_only"
        summary["issues"] = list(l3_issues)
        return summary

    if summary["levels"]["l1_process_ready"]["passed"]:
        summary["status_label"] = "l1_process_ready_only"
        summary["issues"] = list(l2_issues)
        return summary

    summary["status_label"] = "not_ready"
    summary["issues"] = list(summary["levels"]["l1_process_ready"]["issues"])
    return summary


def _evaluate_l2_contract_readiness(
    health_payload: Mapping[str, Any],
    config: ReadinessProbeConfig,
) -> tuple[list[str], list[str]]:
    verified_fields: list[str] = []
    issues: list[str] = []

    status = _extract_str(health_payload, "status")
    if status is None:
        issues.append("health payload missing status")
    else:
        verified_fields.append("health.status")
        if status.lower() in {"offline", "failed", "error"}:
            issues.append(f"health status is not ready for acceptance: {status}")

    provider_mode = _extract_str(health_payload, "provider_mode")
    if provider_mode is None:
        issues.append("health payload missing provider_mode")
    else:
        verified_fields.append("health.provider_mode")

    bridge_contract_version = _extract_str(health_payload, "bridge_contract_version")
    if bridge_contract_version is None:
        issues.append("health payload missing bridge_contract_version")
    else:
        verified_fields.append("health.bridge_contract_version")
        if bridge_contract_version != config.bridge_contract_version:
            issues.append(
                "health bridge_contract_version mismatch: "
                f"expected {config.bridge_contract_version!r}, got {bridge_contract_version!r}"
            )

    if health_payload.get("bridge_auth_configured") is not True:
        issues.append("health payload does not confirm bridge_auth_configured=true")
    else:
        verified_fields.append("health.bridge_auth_configured")

    source_name = _extract_str(health_payload, "source_name")
    if source_name is None:
        issues.append("health payload missing source_name")
    else:
        verified_fields.append("health.source_name")

    return verified_fields, issues


def _evaluate_l3_acceptance_readiness(
    health_payload: Mapping[str, Any],
    config: ReadinessProbeConfig,
    expected_source_name: str | None,
) -> tuple[list[str], list[str]]:
    verified_fields: list[str] = []
    issues: list[str] = []

    if not str(config.bridge_token).strip():
        issues.append("local bridge token is not configured")
    else:
        verified_fields.append("local.bridge_token_configured")

    provider_mode = _extract_str(health_payload, "provider_mode")
    if provider_mode is None:
        issues.append("health payload missing provider_mode for readiness confirmation")
    elif provider_mode != config.expected_provider_mode:
        issues.append(
            "health provider_mode mismatch for planned acceptance run: "
            f"expected {config.expected_provider_mode!r}, got {provider_mode!r}"
        )
    else:
        verified_fields.append("health.expected_provider_mode")

    source_name = _extract_str(health_payload, "source_name")
    if expected_source_name:
        if source_name is None:
            issues.append("health payload missing source_name for readiness confirmation")
        elif source_name != expected_source_name:
            issues.append(
                f"health source_name mismatch: expected {expected_source_name!r}, got {source_name!r}"
            )
        else:
            verified_fields.append("health.expected_source_name")

    return verified_fields, issues


def resolve_expected_source_name(config: ReadinessProbeConfig) -> str | None:
    if config.expected_source_name:
        normalized = str(config.expected_source_name).strip()
        if normalized:
            return normalized
    if config.contract_profile == KERNEL_PHASE_A_CONTRACT_PROFILE:
        if str(config.expected_provider_mode).strip().lower() == "mock":
            return "mock"
        return "live"
    return DEFAULT_REFERENCE_SOURCE_NAME


def _extract_str(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _build_configuration_invalid_summary(args: argparse.Namespace) -> dict[str, Any]:
    base_url = str(getattr(args, "base_url", None) or os.getenv(DEFAULT_BASE_URL_ENV, "")).strip()
    issues: list[str] = []
    if not base_url:
        issues.append(f"base_url is required; provide --base-url or set {DEFAULT_BASE_URL_ENV}")

    return {
        "ok": False,
        "status_label": "configuration_invalid",
        "recommended_exit_code": 2,
        "summary_schema_version": SUMMARY_SCHEMA_VERSION,
        "runtime_environment": DEFAULT_RUNTIME_ENVIRONMENT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url or None,
        "expected": {
            "contract_profile": str(getattr(args, "contract_profile")),
            "provider_mode": str(getattr(args, "expected_provider_mode")),
            "bridge_contract_version": str(getattr(args, "contract_version")),
            "source_name": str(getattr(args, "expected_source_name")) if getattr(args, "expected_source_name", None) else None,
        },
        "local_config": {
            "base_url_configured": bool(base_url),
            "bridge_token_configured": bool(str(getattr(args, "bridge_token", "")).strip()),
        },
        "health": None,
        "levels": {
            "l1_process_ready": {"passed": False, "verified_fields": [], "issues": list(issues)},
            "l2_contract_ready": {"passed": False, "verified_fields": [], "issues": []},
            "l3_acceptance_ready": {"passed": False, "verified_fields": [], "issues": []},
        },
        "issues": issues,
    }


def _persist_summary(summary: dict[str, Any], report_dir: Path) -> dict[str, str]:
    report_dir.mkdir(parents=True, exist_ok=True)
    generated_at_raw = str(summary.get("generated_at") or datetime.now(timezone.utc).isoformat())
    timestamp = _to_artifact_timestamp(generated_at_raw)
    report_artifact = report_dir / f"{timestamp}-windows-qmt-service-readiness.json"
    latest_path = report_dir / "latest.json"
    encoded = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    report_artifact.write_text(encoded, encoding="utf-8")
    latest_path.write_text(encoded, encoding="utf-8")
    return {
        "report_artifact": str(report_artifact),
        "latest": str(latest_path),
    }


def _to_artifact_timestamp(value: str) -> str:
    normalized = value.strip()
    if normalized.endswith("Z"):
        dt = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    else:
        dt = datetime.fromisoformat(normalized)
    dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report_dir = Path(str(getattr(args, "report_dir")))
    base_url = str(getattr(args, "base_url") or os.getenv(DEFAULT_BASE_URL_ENV, "")).strip()

    if not base_url:
        summary = _build_configuration_invalid_summary(args)
        summary["artifacts"] = _persist_summary(summary, report_dir)
        print(json.dumps(summary, ensure_ascii=False))
        return int(summary["recommended_exit_code"])

    config = ReadinessProbeConfig(
        base_url=base_url,
        bridge_token=str(getattr(args, "bridge_token") or ""),
        bridge_contract_version=str(getattr(args, "contract_version")),
        contract_profile=str(getattr(args, "contract_profile")),
        expected_provider_mode=str(getattr(args, "expected_provider_mode")),
        expected_source_name=getattr(args, "expected_source_name"),
        timeout_seconds=float(getattr(args, "timeout_seconds")),
    )
    summary = asyncio.run(run_readiness_probe(config))
    summary["artifacts"] = _persist_summary(summary, report_dir)
    print(json.dumps(summary, ensure_ascii=False))
    return int(summary["recommended_exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
