from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Mapping, Protocol
from uuid import uuid4

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_BACKEND_ROOT = PROJECT_ROOT / "web" / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(WEB_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(WEB_BACKEND_ROOT))

from src.utils.trading_runtime_config import (  # noqa: E402
    get_trading_miniqmt_live_bridge_poll_interval_seconds,
    get_trading_miniqmt_live_bridge_timeout_seconds,
    get_trading_qmt_bridge_contract_version,
    get_trading_qmt_bridge_token,
)
from web.backend.app.services.miniqmt_live_bridge import (  # noqa: E402
    BRIDGE_RESULT_PAYLOAD,
    BRIDGE_SUBMISSION_RECEIPT,
    MiniQMTLiveBridgeClient,
)
from web.backend.app.services.windows_bridge_adapter import MultiSourceBridgeAdapter  # noqa: E402

DEFAULT_BASE_URL_ENV = "TRADING_QMT_BRIDGE_BASE_URL"
DEFAULT_EXPECTED_PROVIDER_MODE = "mock"
DEFAULT_EXPECTED_ACCOUNT_SCOPE = "wsl-ubuntu-phase-a-acceptance"
DEFAULT_EXPECTED_SOURCE_NAME = "qmt/windows_reference_service"
DEFAULT_MOCK_OUTCOME = "acknowledgement"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "docs" / "reports" / "quality" / "windows-qmt-contract-acceptance"


@dataclass(slots=True)
class AcceptanceHarnessConfig:
    base_url: str
    bridge_token: str
    bridge_contract_version: str
    expected_provider_mode: str = DEFAULT_EXPECTED_PROVIDER_MODE
    expected_source_name: str | None = DEFAULT_EXPECTED_SOURCE_NAME
    expected_account_scope: str = DEFAULT_EXPECTED_ACCOUNT_SCOPE
    mock_outcome: str = DEFAULT_MOCK_OUTCOME
    mock_delay_seconds: float = 0.0
    timeout_seconds: float = 15.0
    poll_interval_seconds: float = 1.0
    allow_non_mock_provider_mode: bool = False


class LiveBridgeClientProtocol(Protocol):
    def submit_order(self, payload: Mapping[str, Any]) -> dict[str, Any]: ...

    def poll_task_result(
        self,
        task_id: str,
        *,
        timeout_seconds: float | None = None,
        poll_interval_seconds: float | None = None,
    ) -> dict[str, Any]: ...


HealthFetcher = Callable[[str, float], Awaitable[dict[str, Any]]]
BridgeClientFactory = Callable[[AcceptanceHarnessConfig], LiveBridgeClientProtocol]


def build_live_bridge_client(config: AcceptanceHarnessConfig) -> MiniQMTLiveBridgeClient:
    adapter = MultiSourceBridgeAdapter(
        {
            "providers": {"qmt": config.base_url},
            "bridge_token": config.bridge_token,
            "bridge_contract_version": config.bridge_contract_version,
            "timeout": config.timeout_seconds,
        }
    )
    return MiniQMTLiveBridgeClient(
        adapter,
        contract_version=config.bridge_contract_version,
        timeout_seconds=config.timeout_seconds,
        poll_interval_seconds=config.poll_interval_seconds,
    )


async def fetch_health_payload(base_url: str, timeout_seconds: float) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.get(f"{base_url.rstrip('/')}/health")
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, Mapping):
        raise ValueError("Windows qmt /health payload must be a JSON object")
    return dict(payload)


async def run_acceptance_harness(
    config: AcceptanceHarnessConfig,
    *,
    health_fetcher: HealthFetcher = fetch_health_payload,
    bridge_client_factory: BridgeClientFactory = build_live_bridge_client,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "ok": False,
        "stage": "initializing",
        "base_url": config.base_url,
        "expected": {
            "provider_mode": config.expected_provider_mode,
            "bridge_contract_version": config.bridge_contract_version,
            "source_name": config.expected_source_name,
            "account_scope": config.expected_account_scope,
            "mock_outcome": config.mock_outcome,
        },
        "stopped_before_execute": False,
        "health": None,
        "receipt": None,
        "result": None,
        "verified_fields": [],
        "issues": [],
    }

    try:
        health_payload = await health_fetcher(config.base_url, config.timeout_seconds)
    except Exception as exc:
        summary["stage"] = "health_probe_failed"
        summary["issues"] = [f"health probe failed: {exc}"]
        return summary

    summary["health"] = health_payload
    health_verified_fields, health_issues = _validate_health_payload(health_payload, config)
    summary["verified_fields"].extend(health_verified_fields)
    if health_issues:
        summary["stage"] = "blocked_before_execute"
        summary["stopped_before_execute"] = True
        summary["issues"] = health_issues
        return summary

    bridge_client = bridge_client_factory(config)
    submission_payload = _build_submission_payload(config)
    receipt = bridge_client.submit_order(submission_payload)
    summary["receipt"] = receipt

    receipt_verified_fields, receipt_issues = _validate_receipt_payload(receipt, config)
    summary["verified_fields"].extend(receipt_verified_fields)
    if receipt_issues:
        summary["stage"] = "receipt_validation_failed"
        summary["issues"] = receipt_issues
        return summary

    result = bridge_client.poll_task_result(
        receipt["task_id"],
        timeout_seconds=config.timeout_seconds,
        poll_interval_seconds=config.poll_interval_seconds,
    )
    summary["result"] = result

    result_verified_fields, result_issues = _validate_result_payload(
        result,
        config=config,
        expected_event_id=submission_payload["event_id"],
        expected_local_submission_id=submission_payload["local_submission_id"],
    )
    summary["verified_fields"].extend(result_verified_fields)
    if result_issues:
        summary["stage"] = "result_validation_failed"
        summary["issues"] = result_issues
        return summary

    summary["ok"] = True
    summary["stage"] = "completed"
    return summary


def _validate_health_payload(
    payload: Mapping[str, Any],
    config: AcceptanceHarnessConfig,
) -> tuple[list[str], list[str]]:
    verified_fields: list[str] = []
    issues: list[str] = []

    provider_mode = _extract_str(payload, "provider_mode")
    bridge_contract_version = _extract_str(payload, "bridge_contract_version")
    source_name = _extract_str(payload, "source_name")
    status = _extract_str(payload, "status")
    bridge_auth_configured = payload.get("bridge_auth_configured")

    if status is None:
        issues.append("health payload missing status")
    else:
        verified_fields.append("health.status")
        if status.lower() in {"offline", "failed", "error"}:
            issues.append(f"health status is not ready for acceptance: {status}")

    if provider_mode is None:
        issues.append("health payload missing provider_mode")
    else:
        verified_fields.append("health.provider_mode")
        if provider_mode != config.expected_provider_mode and not config.allow_non_mock_provider_mode:
            issues.append(
                "full execute/result smoke blocked because remote provider_mode is "
                f"{provider_mode!r}, expected {config.expected_provider_mode!r}"
            )

    if bridge_contract_version is None:
        issues.append("health payload missing bridge_contract_version")
    else:
        verified_fields.append("health.bridge_contract_version")
        if bridge_contract_version != config.bridge_contract_version:
            issues.append(
                "health bridge_contract_version mismatch: "
                f"expected {config.bridge_contract_version!r}, got {bridge_contract_version!r}"
            )

    if bridge_auth_configured is not True:
        issues.append("health payload does not confirm bridge_auth_configured=true")
    else:
        verified_fields.append("health.bridge_auth_configured")

    if source_name is None:
        issues.append("health payload missing source_name")
    else:
        verified_fields.append("health.source_name")
        if config.expected_source_name and source_name != config.expected_source_name:
            issues.append(
                f"health source_name mismatch: expected {config.expected_source_name!r}, got {source_name!r}"
            )

    return verified_fields, issues


def _validate_receipt_payload(
    payload: Mapping[str, Any],
    config: AcceptanceHarnessConfig,
) -> tuple[list[str], list[str]]:
    verified_fields: list[str] = []
    issues: list[str] = []

    if payload.get("contract_state") != BRIDGE_SUBMISSION_RECEIPT:
        issues.append(
            f"receipt contract_state mismatch: expected {BRIDGE_SUBMISSION_RECEIPT!r}, "
            f"got {payload.get('contract_state')!r}"
        )
        return verified_fields, issues

    verified_fields.append("receipt.contract_state")

    task_id = _extract_str(payload, "task_id")
    if task_id is None:
        issues.append("receipt missing task_id")
    else:
        verified_fields.append("receipt.task_id")

    receipt_timestamp = _extract_str(payload, "receipt_timestamp")
    if receipt_timestamp is None:
        issues.append("receipt missing receipt_timestamp")
    else:
        verified_fields.append("receipt.receipt_timestamp")

    source_name = _extract_str(payload, "source_name")
    if source_name is None:
        issues.append("receipt missing source_name")
    else:
        verified_fields.append("receipt.source_name")
        if config.expected_source_name and source_name != config.expected_source_name:
            issues.append(
                f"receipt source_name mismatch: expected {config.expected_source_name!r}, got {source_name!r}"
            )

    bridge_contract_version = _extract_str(payload, "bridge_contract_version")
    if bridge_contract_version is None:
        issues.append("receipt missing bridge_contract_version")
    else:
        verified_fields.append("receipt.bridge_contract_version")
        if bridge_contract_version != config.bridge_contract_version:
            issues.append(
                "receipt bridge_contract_version mismatch: "
                f"expected {config.bridge_contract_version!r}, got {bridge_contract_version!r}"
            )

    return verified_fields, issues


def _validate_result_payload(
    payload: Mapping[str, Any],
    *,
    config: AcceptanceHarnessConfig,
    expected_event_id: str,
    expected_local_submission_id: str,
) -> tuple[list[str], list[str]]:
    verified_fields: list[str] = []
    issues: list[str] = []

    if payload.get("contract_state") != BRIDGE_RESULT_PAYLOAD:
        issues.append(
            f"result contract_state mismatch: expected {BRIDGE_RESULT_PAYLOAD!r}, got {payload.get('contract_state')!r}"
        )
        return verified_fields, issues

    verified_fields.append("result.contract_state")

    for key in ("occurred_at", "source_name", "account_scope", "event_id", "bridge_contract_version"):
        if _extract_str(payload, key) is None:
            issues.append(f"result missing {key}")
        else:
            verified_fields.append(f"result.{key}")

    result_source_name = _extract_str(payload, "source_name")
    if config.expected_source_name and result_source_name and result_source_name != config.expected_source_name:
        issues.append(
            f"result source_name mismatch: expected {config.expected_source_name!r}, got {result_source_name!r}"
        )

    result_account_scope = _extract_str(payload, "account_scope")
    if result_account_scope and result_account_scope != config.expected_account_scope:
        issues.append(
            f"result account_scope mismatch: expected {config.expected_account_scope!r}, got {result_account_scope!r}"
        )

    result_contract_version = _extract_str(payload, "bridge_contract_version")
    if result_contract_version and result_contract_version != config.bridge_contract_version:
        issues.append(
            "result bridge_contract_version mismatch: "
            f"expected {config.bridge_contract_version!r}, got {result_contract_version!r}"
        )

    result_event_id = _extract_str(payload, "event_id")
    if result_event_id and result_event_id != expected_event_id:
        issues.append(f"result event_id mismatch: expected {expected_event_id!r}, got {result_event_id!r}")

    local_submission_id = _extract_str(payload, "local_submission_id")
    if local_submission_id and local_submission_id != expected_local_submission_id:
        issues.append(
            "result local_submission_id mismatch: "
            f"expected {expected_local_submission_id!r}, got {local_submission_id!r}"
        )
    elif local_submission_id is not None:
        verified_fields.append("result.local_submission_id")

    broker_event_type = _extract_str(payload, "broker_event_type")
    expected_event_type = _expected_broker_event_type(config.mock_outcome)
    if broker_event_type is None:
        issues.append("result missing broker_event_type")
    else:
        verified_fields.append("result.broker_event_type")
        if expected_event_type and broker_event_type != expected_event_type:
            issues.append(
                f"result broker_event_type mismatch: expected {expected_event_type!r}, got {broker_event_type!r}"
            )

    return verified_fields, issues


def _build_submission_payload(config: AcceptanceHarnessConfig) -> dict[str, Any]:
    run_id = uuid4().hex[:12]
    event_id = f"smoke-event-{run_id}"
    local_submission_id = f"smoke-submission-{run_id}"
    return {
        "order_id": f"smoke-order-{run_id}",
        "client_order_id": f"smoke-client-{run_id}",
        "local_submission_id": local_submission_id,
        "symbol": "000001",
        "quantity": 100,
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 10.5,
        "request_id": f"smoke-request-{run_id}",
        "portfolio_id": "acceptance-portfolio",
        "strategy_id": "acceptance-strategy",
        "actor_id": "ubuntu-wsl-acceptance",
        "source_id": "windows-qmt-contract-smoke",
        "account_scope": config.expected_account_scope,
        "event_id": event_id,
        "mock_outcome": config.mock_outcome,
        "mock_delay_seconds": config.mock_delay_seconds,
    }


def _expected_broker_event_type(mock_outcome: str) -> str | None:
    normalized = mock_outcome.strip().lower()
    if normalized in {"ack", "acknowledgement", "accepted"}:
        return "acknowledgement"
    if normalized in {"execution", "filled"}:
        return "execution"
    if normalized in {"reject", "rejected"}:
        return "reject"
    if normalized in {"cancel", "cancelled"}:
        return "cancel"
    return None


def _extract_str(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify a Windows qmt contract endpoint from WSL 上的 Ubuntu 24.04.4 LTS."
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help=f"Windows qmt agent base URL. Defaults to ${DEFAULT_BASE_URL_ENV}.",
    )
    parser.add_argument(
        "--bridge-token",
        default=None,
        help="Bearer token for the Windows qmt agent. Defaults to TRADING_QMT_BRIDGE_TOKEN.",
    )
    parser.add_argument(
        "--contract-version",
        default=get_trading_qmt_bridge_contract_version(),
        help="Expected bridge contract version.",
    )
    parser.add_argument(
        "--expected-provider-mode",
        default=DEFAULT_EXPECTED_PROVIDER_MODE,
        help="Expected safe provider mode for full smoke execution.",
    )
    parser.add_argument(
        "--expected-source-name",
        default=DEFAULT_EXPECTED_SOURCE_NAME,
        help="Expected source_name value echoed by the Windows qmt service.",
    )
    parser.add_argument(
        "--expected-account-scope",
        default=DEFAULT_EXPECTED_ACCOUNT_SCOPE,
        help="Account scope to send and verify during the smoke run.",
    )
    parser.add_argument(
        "--mock-outcome",
        default=DEFAULT_MOCK_OUTCOME,
        help="Mock outcome to request from the remote service.",
    )
    parser.add_argument(
        "--mock-delay-seconds",
        type=float,
        default=0.0,
        help="Requested mock pending delay before the result becomes terminal.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=get_trading_miniqmt_live_bridge_timeout_seconds(),
        help="Health and result polling timeout in seconds.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=get_trading_miniqmt_live_bridge_poll_interval_seconds(),
        help="Polling interval for deferred result retrieval.",
    )
    parser.add_argument(
        "--allow-non-mock-provider-mode",
        action="store_true",
        help="Override the default fail-closed provider_mode gate.",
    )
    parser.add_argument(
        "--summary-output",
        default=None,
        help="Optional path to persist the acceptance summary JSON artifact.",
    )
    parser.add_argument(
        "--report-dir",
        default=None,
        help="Optional directory that receives a timestamped summary JSON plus latest.json.",
    )
    return parser.parse_args(argv)


def build_config_from_args(args: argparse.Namespace) -> AcceptanceHarnessConfig:
    base_url = (args.base_url or "").strip() or _read_env(DEFAULT_BASE_URL_ENV)
    bridge_token = (args.bridge_token or "").strip() or (get_trading_qmt_bridge_token() or "")

    if not base_url:
        raise ValueError(
            f"Windows qmt base URL is required via --base-url or the {DEFAULT_BASE_URL_ENV} environment variable."
        )
    if not bridge_token:
        raise ValueError("TRADING_QMT_BRIDGE_TOKEN is required for contract acceptance.")

    return AcceptanceHarnessConfig(
        base_url=base_url.rstrip("/"),
        bridge_token=bridge_token,
        bridge_contract_version=str(args.contract_version).strip(),
        expected_provider_mode=str(args.expected_provider_mode).strip(),
        expected_source_name=str(args.expected_source_name).strip() if args.expected_source_name else None,
        expected_account_scope=str(args.expected_account_scope).strip(),
        mock_outcome=str(args.mock_outcome).strip(),
        mock_delay_seconds=float(args.mock_delay_seconds),
        timeout_seconds=float(args.timeout_seconds),
        poll_interval_seconds=float(args.poll_interval_seconds),
        allow_non_mock_provider_mode=bool(args.allow_non_mock_provider_mode),
    )


def _read_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        return ""
    return value.strip()


def write_summary_output(summary: Mapping[str, Any], output_path: str | Path) -> Path:
    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(dict(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target_path


def build_timestamped_summary_output_path(
    report_dir: str | Path,
    *,
    now: datetime | None = None,
) -> Path:
    timestamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    return Path(report_dir) / f"{timestamp}-windows-qmt-contract-acceptance.json"


def persist_summary_artifacts(
    summary: Mapping[str, Any],
    *,
    summary_output: str | Path | None = None,
    report_dir: str | Path | None = None,
) -> dict[str, str]:
    written_paths: dict[str, str] = {}
    if summary_output:
        written_paths["summary_output"] = str(write_summary_output(summary, summary_output))

    if report_dir:
        report_root = Path(report_dir)
        timestamped_path = build_timestamped_summary_output_path(report_root)
        latest_path = report_root / "latest.json"
        written_paths["report_artifact"] = str(write_summary_output(summary, timestamped_path))
        written_paths["latest"] = str(write_summary_output(summary, latest_path))

    return written_paths


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary_output = getattr(args, "summary_output", None)
    report_dir = getattr(args, "report_dir", None)
    try:
        config = build_config_from_args(args)
    except ValueError as exc:
        summary = {"ok": False, "stage": "configuration_invalid", "issues": [str(exc)]}
        artifacts = persist_summary_artifacts(summary, summary_output=summary_output, report_dir=report_dir)
        if artifacts:
            summary["artifacts"] = artifacts
        print(json.dumps(summary, indent=2))
        return 2

    summary = asyncio.run(run_acceptance_harness(config))
    artifacts = persist_summary_artifacts(summary, summary_output=summary_output, report_dir=report_dir)
    if artifacts:
        summary["artifacts"] = artifacts
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
