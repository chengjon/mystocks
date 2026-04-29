from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = PROJECT_ROOT / "scripts" / "dev" / "verify_windows_qmt_agent_contract.py"
SPEC = importlib.util.spec_from_file_location("verify_windows_qmt_agent_contract", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class _StubLiveBridgeClient:
    def __init__(self, receipt: dict[str, object], result: dict[str, object]) -> None:
        self.receipt = receipt
        self.result = result
        self.submissions: list[dict[str, object]] = []
        self.poll_calls: list[dict[str, object]] = []

    def submit_order(self, payload: dict[str, object]) -> dict[str, object]:
        self.submissions.append(dict(payload))
        return dict(self.receipt)

    def poll_task_result(
        self,
        task_id: str,
        *,
        timeout_seconds: float | None = None,
        poll_interval_seconds: float | None = None,
    ) -> dict[str, object]:
        self.poll_calls.append(
            {
                "task_id": task_id,
                "timeout_seconds": timeout_seconds,
                "poll_interval_seconds": poll_interval_seconds,
            }
        )
        return dict(self.result)


@pytest.mark.asyncio
async def test_acceptance_harness_succeeds_for_mock_contract() -> None:
    config = MODULE.AcceptanceHarnessConfig(
        base_url="http://bridge.local",
        bridge_token="secret-token",
        bridge_contract_version="1",
        expected_provider_mode="mock",
        expected_source_name="qmt/windows_reference_service",
        expected_account_scope="paper-account-01",
        mock_outcome="acknowledgement",
        timeout_seconds=5.0,
        poll_interval_seconds=0.1,
    )
    receipt = {
        "contract_state": MODULE.BRIDGE_SUBMISSION_RECEIPT,
        "task_id": "bridge-task-0501",
        "receipt_timestamp": "2026-04-29T15:00:00+00:00",
        "source_name": "qmt/windows_reference_service",
        "bridge_contract_version": "1",
    }
    result = {
        "contract_state": MODULE.BRIDGE_RESULT_PAYLOAD,
        "task_id": "bridge-task-0501",
        "occurred_at": "2026-04-29T15:00:01+00:00",
        "source_name": "qmt/windows_reference_service",
        "account_scope": "paper-account-01",
        "event_id": "smoke-event-fixed",
        "bridge_contract_version": "1",
        "local_submission_id": "smoke-submission-fixed",
        "broker_event_type": "acknowledgement",
    }
    stub_client = _StubLiveBridgeClient(receipt=receipt, result=result)

    async def _health_fetcher(base_url: str, timeout_seconds: float) -> dict[str, object]:
        assert base_url == "http://bridge.local"
        assert timeout_seconds == 5.0
        return {
            "status": "online",
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "qmt/windows_reference_service",
        }

    def _client_factory(_: object) -> _StubLiveBridgeClient:
        return stub_client

    def _fixed_submission_payload(_: object) -> dict[str, object]:
        return {
            "local_submission_id": "smoke-submission-fixed",
            "event_id": "smoke-event-fixed",
            "account_scope": "paper-account-01",
            "mock_outcome": "acknowledgement",
        }

    original_builder = MODULE._build_submission_payload
    MODULE._build_submission_payload = _fixed_submission_payload
    try:
        summary = await MODULE.run_acceptance_harness(
            config,
            health_fetcher=_health_fetcher,
            bridge_client_factory=_client_factory,
        )
    finally:
        MODULE._build_submission_payload = original_builder

    assert summary["ok"] is True
    assert summary["stage"] == "completed"
    assert summary["issues"] == []
    assert summary["verified_fields"]
    assert stub_client.submissions == [
        {
            "local_submission_id": "smoke-submission-fixed",
            "event_id": "smoke-event-fixed",
            "account_scope": "paper-account-01",
            "mock_outcome": "acknowledgement",
        }
    ]
    assert stub_client.poll_calls[0]["task_id"] == "bridge-task-0501"


@pytest.mark.asyncio
async def test_acceptance_harness_fails_closed_when_provider_mode_is_not_mock() -> None:
    config = MODULE.AcceptanceHarnessConfig(
        base_url="http://bridge.local",
        bridge_token="secret-token",
        bridge_contract_version="1",
        expected_provider_mode="mock",
        expected_source_name="qmt/windows_reference_service",
        expected_account_scope="paper-account-01",
    )
    stub_client = _StubLiveBridgeClient(receipt={}, result={})

    async def _health_fetcher(base_url: str, timeout_seconds: float) -> dict[str, object]:
        return {
            "status": "online",
            "provider_mode": "miniqmt_sdk",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "qmt/windows_reference_service",
        }

    def _client_factory(_: object) -> _StubLiveBridgeClient:
        return stub_client

    summary = await MODULE.run_acceptance_harness(
        config,
        health_fetcher=_health_fetcher,
        bridge_client_factory=_client_factory,
    )

    assert summary["ok"] is False
    assert summary["stage"] == "blocked_before_execute"
    assert summary["stopped_before_execute"] is True
    assert "provider_mode" in summary["issues"][0]
    assert stub_client.submissions == []
    assert stub_client.poll_calls == []


@pytest.mark.asyncio
async def test_acceptance_harness_reports_missing_canonical_result_fields() -> None:
    config = MODULE.AcceptanceHarnessConfig(
        base_url="http://bridge.local",
        bridge_token="secret-token",
        bridge_contract_version="1",
        expected_provider_mode="mock",
        expected_source_name="qmt/windows_reference_service",
        expected_account_scope="paper-account-01",
        mock_outcome="acknowledgement",
    )
    receipt = {
        "contract_state": MODULE.BRIDGE_SUBMISSION_RECEIPT,
        "task_id": "bridge-task-0503",
        "receipt_timestamp": "2026-04-29T15:00:00+00:00",
        "source_name": "qmt/windows_reference_service",
        "bridge_contract_version": "1",
    }
    result = {
        "contract_state": MODULE.BRIDGE_RESULT_PAYLOAD,
        "task_id": "bridge-task-0503",
        "occurred_at": "2026-04-29T15:00:01+00:00",
        "source_name": "qmt/windows_reference_service",
        "account_scope": "paper-account-01",
        "bridge_contract_version": "1",
        "local_submission_id": "smoke-submission-fixed",
        "broker_event_type": "acknowledgement",
    }
    stub_client = _StubLiveBridgeClient(receipt=receipt, result=result)

    async def _health_fetcher(base_url: str, timeout_seconds: float) -> dict[str, object]:
        return {
            "status": "online",
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "qmt/windows_reference_service",
        }

    def _client_factory(_: object) -> _StubLiveBridgeClient:
        return stub_client

    def _fixed_submission_payload(_: object) -> dict[str, object]:
        return {
            "local_submission_id": "smoke-submission-fixed",
            "event_id": "smoke-event-fixed",
            "account_scope": "paper-account-01",
            "mock_outcome": "acknowledgement",
        }

    original_builder = MODULE._build_submission_payload
    MODULE._build_submission_payload = _fixed_submission_payload
    try:
        summary = await MODULE.run_acceptance_harness(
            config,
            health_fetcher=_health_fetcher,
            bridge_client_factory=_client_factory,
        )
    finally:
        MODULE._build_submission_payload = original_builder

    assert summary["ok"] is False
    assert summary["stage"] == "result_validation_failed"
    assert "result missing event_id" in summary["issues"]
