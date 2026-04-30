from __future__ import annotations

import importlib.util
import json
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


def test_main_writes_summary_output_artifact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_path = tmp_path / "acceptance-summary.json"
    output_metadata = {
        "summary_schema_version": 1,
        "runtime_environment": "wsl-ubuntu-24.04.4-lts",
        "generated_at": "2026-04-30T12:00:00+00:00",
    }
    expected_summary = {
        "ok": True,
        "stage": "completed",
        "issues": [],
        "verified_fields": ["health.status"],
        **output_metadata,
        "artifacts": {
            "summary_output": str(output_path),
        },
    }

    monkeypatch.setattr(
        MODULE,
        "parse_args",
        lambda argv=None: type(
            "Args",
            (),
            {
                "summary_output": str(output_path),
            },
        )(),
    )
    monkeypatch.setattr(
        MODULE,
        "build_config_from_args",
        lambda args: MODULE.AcceptanceHarnessConfig(
            base_url="http://bridge.local",
            bridge_token="secret-token",
            bridge_contract_version="1",
        ),
    )

    async def _run_acceptance_harness(config: object) -> dict[str, object]:
        return dict(expected_summary)

    monkeypatch.setattr(MODULE, "run_acceptance_harness", _run_acceptance_harness)
    monkeypatch.setattr(MODULE, "build_output_metadata", lambda now=None: dict(output_metadata))

    exit_code = MODULE.main([])

    assert exit_code == 0
    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8")) == expected_summary


def test_persist_summary_artifacts_writes_timestamped_and_latest_reports(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    summary = {
        "ok": True,
        "stage": "completed",
        "summary_schema_version": 1,
        "runtime_environment": "wsl-ubuntu-24.04.4-lts",
        "generated_at": "2026-04-30T12:00:00+00:00",
    }
    report_dir = tmp_path / "reports"
    fixed_report_path = report_dir / "20260430T120000Z-windows-qmt-contract-acceptance.json"

    monkeypatch.setattr(
        MODULE,
        "build_timestamped_summary_output_path",
        lambda path: fixed_report_path,
    )

    artifacts = MODULE.persist_summary_artifacts(summary, report_dir=report_dir)

    assert artifacts == {
        "report_artifact": str(fixed_report_path),
        "latest": str(report_dir / "latest.json"),
    }
    expected_summary = {
        **summary,
        "artifacts": artifacts,
    }
    assert json.loads(fixed_report_path.read_text(encoding="utf-8")) == expected_summary
    assert json.loads((report_dir / "latest.json").read_text(encoding="utf-8")) == expected_summary


def test_main_compare_with_baseline_passes_for_matching_contract_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "acceptance-summary.json"
    baseline_path = tmp_path / "baseline.json"
    output_metadata = {
        "summary_schema_version": 1,
        "runtime_environment": "wsl-ubuntu-24.04.4-lts",
        "generated_at": "2026-04-30T12:00:00+00:00",
    }
    raw_summary = {
        "ok": True,
        "stage": "completed",
        "expected": {
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "mock_outcome": "acknowledgement",
        },
        "health": {
            "status": "online",
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "qmt/windows_reference_service",
        },
        "receipt": {
            "contract_state": MODULE.BRIDGE_SUBMISSION_RECEIPT,
            "task_id": "old-task-id-ignored",
            "receipt_timestamp": "2026-04-29T15:00:00+00:00",
            "source_name": "qmt/windows_reference_service",
            "bridge_contract_version": "1",
        },
        "result": {
            "contract_state": MODULE.BRIDGE_RESULT_PAYLOAD,
            "task_id": "old-task-id-ignored",
            "occurred_at": "2026-04-29T15:00:01+00:00",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "event_id": "old-event-id-ignored",
            "bridge_contract_version": "1",
            "local_submission_id": "old-submission-id-ignored",
            "broker_event_type": "acknowledgement",
        },
        "issues": [],
        "verified_fields": ["health.status"],
    }
    baseline_payload = {
        **raw_summary,
        "generated_at": "2026-04-29T10:00:00+00:00",
        "artifacts": {"summary_output": "/tmp/older-summary.json"},
    }
    baseline_path.write_text(json.dumps(baseline_payload, indent=2), encoding="utf-8")

    monkeypatch.setattr(
        MODULE,
        "parse_args",
        lambda argv=None: type(
            "Args",
            (),
            {
                "summary_output": str(output_path),
                "report_dir": None,
                "compare_with": str(baseline_path),
            },
        )(),
    )
    monkeypatch.setattr(
        MODULE,
        "build_config_from_args",
        lambda args: MODULE.AcceptanceHarnessConfig(
            base_url="http://bridge.local",
            bridge_token="secret-token",
            bridge_contract_version="1",
        ),
    )

    async def _run_acceptance_harness(config: object) -> dict[str, object]:
        return dict(raw_summary)

    monkeypatch.setattr(MODULE, "run_acceptance_harness", _run_acceptance_harness)
    monkeypatch.setattr(MODULE, "build_output_metadata", lambda now=None: dict(output_metadata))

    exit_code = MODULE.main([])

    persisted_summary = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert persisted_summary["comparison"]["ok"] is True
    assert persisted_summary["comparison"]["baseline_path"] == str(baseline_path)
    assert persisted_summary["comparison"]["mismatches"] == []


def test_resolve_compare_with_path_uses_standard_latest_baseline_when_requested(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"

    resolved = MODULE.resolve_compare_with_path(
        compare_with=None,
        compare_with_latest_baseline=True,
        report_dir=report_dir,
    )

    assert resolved == str(report_dir / "baselines" / "latest-baseline.json")


def test_resolve_compare_with_path_prefers_explicit_path_over_standard_latest_baseline(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    explicit_baseline_path = tmp_path / "manual-baseline.json"

    resolved = MODULE.resolve_compare_with_path(
        compare_with=str(explicit_baseline_path),
        compare_with_latest_baseline=True,
        report_dir=report_dir,
    )

    assert resolved == str(explicit_baseline_path)


def test_main_compare_with_baseline_fails_for_contract_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "acceptance-summary.json"
    baseline_path = tmp_path / "baseline.json"
    output_metadata = {
        "summary_schema_version": 1,
        "runtime_environment": "wsl-ubuntu-24.04.4-lts",
        "generated_at": "2026-04-30T12:00:00+00:00",
    }
    raw_summary = {
        "ok": True,
        "stage": "completed",
        "expected": {
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "mock_outcome": "acknowledgement",
        },
        "health": {
            "status": "online",
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "qmt/windows_reference_service",
        },
        "receipt": {
            "contract_state": MODULE.BRIDGE_SUBMISSION_RECEIPT,
            "task_id": "current-task-id-ignored",
            "receipt_timestamp": "2026-04-29T15:00:00+00:00",
            "source_name": "qmt/windows_reference_service",
            "bridge_contract_version": "1",
        },
        "result": {
            "contract_state": MODULE.BRIDGE_RESULT_PAYLOAD,
            "task_id": "current-task-id-ignored",
            "occurred_at": "2026-04-29T15:00:01+00:00",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "event_id": "current-event-id-ignored",
            "bridge_contract_version": "1",
            "local_submission_id": "current-submission-id-ignored",
            "broker_event_type": "acknowledgement",
        },
        "issues": [],
        "verified_fields": ["health.status"],
    }
    baseline_payload = {
        **raw_summary,
        "result": {
            **raw_summary["result"],
            "source_name": "qmt/other-source",
        },
    }
    baseline_path.write_text(json.dumps(baseline_payload, indent=2), encoding="utf-8")

    monkeypatch.setattr(
        MODULE,
        "parse_args",
        lambda argv=None: type(
            "Args",
            (),
            {
                "summary_output": str(output_path),
                "report_dir": None,
                "compare_with": str(baseline_path),
            },
        )(),
    )
    monkeypatch.setattr(
        MODULE,
        "build_config_from_args",
        lambda args: MODULE.AcceptanceHarnessConfig(
            base_url="http://bridge.local",
            bridge_token="secret-token",
            bridge_contract_version="1",
        ),
    )

    async def _run_acceptance_harness(config: object) -> dict[str, object]:
        return dict(raw_summary)

    monkeypatch.setattr(MODULE, "run_acceptance_harness", _run_acceptance_harness)
    monkeypatch.setattr(MODULE, "build_output_metadata", lambda now=None: dict(output_metadata))

    exit_code = MODULE.main([])

    persisted_summary = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 3
    assert persisted_summary["comparison"]["ok"] is False
    assert persisted_summary["comparison"]["baseline_path"] == str(baseline_path)
    assert persisted_summary["comparison"]["mismatches"] == [
        {
            "path": "result.source_name",
            "expected": "qmt/other-source",
            "actual": "qmt/windows_reference_service",
        }
    ]


def test_main_compare_with_latest_baseline_uses_standard_baseline_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_dir = tmp_path / "reports"
    output_path = tmp_path / "acceptance-summary.json"
    baseline_path = report_dir / "baselines" / "latest-baseline.json"
    output_metadata = {
        "summary_schema_version": 1,
        "runtime_environment": "wsl-ubuntu-24.04.4-lts",
        "generated_at": "2026-04-30T12:00:00+00:00",
    }
    raw_summary = {
        "ok": True,
        "stage": "completed",
        "expected": {
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "mock_outcome": "acknowledgement",
        },
        "health": {
            "status": "online",
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "qmt/windows_reference_service",
        },
        "receipt": {
            "contract_state": MODULE.BRIDGE_SUBMISSION_RECEIPT,
            "task_id": "old-task-id-ignored",
            "receipt_timestamp": "2026-04-29T15:00:00+00:00",
            "source_name": "qmt/windows_reference_service",
            "bridge_contract_version": "1",
        },
        "result": {
            "contract_state": MODULE.BRIDGE_RESULT_PAYLOAD,
            "task_id": "old-task-id-ignored",
            "occurred_at": "2026-04-29T15:00:01+00:00",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "event_id": "old-event-id-ignored",
            "bridge_contract_version": "1",
            "local_submission_id": "old-submission-id-ignored",
            "broker_event_type": "acknowledgement",
        },
        "issues": [],
        "verified_fields": ["health.status"],
    }
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(json.dumps(raw_summary, indent=2), encoding="utf-8")

    monkeypatch.setattr(
        MODULE,
        "parse_args",
        lambda argv=None: type(
            "Args",
            (),
            {
                "summary_output": str(output_path),
                "report_dir": str(report_dir),
                "compare_with": None,
                "compare_with_latest_baseline": True,
                "comparison_markdown_output": None,
            },
        )(),
    )
    monkeypatch.setattr(
        MODULE,
        "build_config_from_args",
        lambda args: MODULE.AcceptanceHarnessConfig(
            base_url="http://bridge.local",
            bridge_token="secret-token",
            bridge_contract_version="1",
        ),
    )

    async def _run_acceptance_harness(config: object) -> dict[str, object]:
        return dict(raw_summary)

    monkeypatch.setattr(MODULE, "run_acceptance_harness", _run_acceptance_harness)
    monkeypatch.setattr(MODULE, "build_output_metadata", lambda now=None: dict(output_metadata))

    exit_code = MODULE.main([])

    persisted_summary = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert persisted_summary["comparison"]["ok"] is True
    assert persisted_summary["comparison"]["baseline_path"] == str(baseline_path)


def test_main_writes_comparison_markdown_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "acceptance-summary.json"
    baseline_path = tmp_path / "baseline.json"
    markdown_path = tmp_path / "comparison-summary.md"
    output_metadata = {
        "summary_schema_version": 1,
        "runtime_environment": "wsl-ubuntu-24.04.4-lts",
        "generated_at": "2026-04-30T12:00:00+00:00",
    }
    raw_summary = {
        "ok": True,
        "stage": "completed",
        "expected": {
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "mock_outcome": "acknowledgement",
        },
        "health": {
            "status": "online",
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "qmt/windows_reference_service",
        },
        "receipt": {
            "contract_state": MODULE.BRIDGE_SUBMISSION_RECEIPT,
            "task_id": "current-task-id-ignored",
            "receipt_timestamp": "2026-04-29T15:00:00+00:00",
            "source_name": "qmt/windows_reference_service",
            "bridge_contract_version": "1",
        },
        "result": {
            "contract_state": MODULE.BRIDGE_RESULT_PAYLOAD,
            "task_id": "current-task-id-ignored",
            "occurred_at": "2026-04-29T15:00:01+00:00",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "event_id": "current-event-id-ignored",
            "bridge_contract_version": "1",
            "local_submission_id": "current-submission-id-ignored",
            "broker_event_type": "acknowledgement",
        },
        "issues": [],
        "verified_fields": ["health.status"],
    }
    baseline_payload = {
        **raw_summary,
        "result": {
            **raw_summary["result"],
            "source_name": "qmt/other-source",
        },
    }
    baseline_path.write_text(json.dumps(baseline_payload, indent=2), encoding="utf-8")

    monkeypatch.setattr(
        MODULE,
        "parse_args",
        lambda argv=None: type(
            "Args",
            (),
            {
                "summary_output": str(output_path),
                "report_dir": None,
                "compare_with": str(baseline_path),
                "comparison_markdown_output": str(markdown_path),
            },
        )(),
    )
    monkeypatch.setattr(
        MODULE,
        "build_config_from_args",
        lambda args: MODULE.AcceptanceHarnessConfig(
            base_url="http://bridge.local",
            bridge_token="secret-token",
            bridge_contract_version="1",
        ),
    )

    async def _run_acceptance_harness(config: object) -> dict[str, object]:
        return dict(raw_summary)

    monkeypatch.setattr(MODULE, "run_acceptance_harness", _run_acceptance_harness)
    monkeypatch.setattr(MODULE, "build_output_metadata", lambda now=None: dict(output_metadata))

    exit_code = MODULE.main([])

    persisted_summary = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 3
    assert markdown_path.exists()
    assert persisted_summary["comparison"]["markdown_output"] == str(markdown_path)
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# Windows qmt Contract Comparison Summary" in markdown
    assert f"- Baseline: `{baseline_path}`" in markdown
    assert "| `result.source_name` | `qmt/other-source` | `qmt/windows_reference_service` |" in markdown


def test_main_report_dir_auto_writes_standard_comparison_markdown_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_dir = tmp_path / "reports"
    baseline_path = tmp_path / "baseline.json"
    output_metadata = {
        "summary_schema_version": 1,
        "runtime_environment": "wsl-ubuntu-24.04.4-lts",
        "generated_at": "2026-04-30T12:00:00+00:00",
    }
    raw_summary = {
        "ok": True,
        "stage": "completed",
        "expected": {
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "mock_outcome": "acknowledgement",
        },
        "health": {
            "status": "online",
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "qmt/windows_reference_service",
        },
        "receipt": {
            "contract_state": MODULE.BRIDGE_SUBMISSION_RECEIPT,
            "task_id": "current-task-id-ignored",
            "receipt_timestamp": "2026-04-29T15:00:00+00:00",
            "source_name": "qmt/windows_reference_service",
            "bridge_contract_version": "1",
        },
        "result": {
            "contract_state": MODULE.BRIDGE_RESULT_PAYLOAD,
            "task_id": "current-task-id-ignored",
            "occurred_at": "2026-04-29T15:00:01+00:00",
            "source_name": "qmt/windows_reference_service",
            "account_scope": "paper-account-01",
            "event_id": "current-event-id-ignored",
            "bridge_contract_version": "1",
            "local_submission_id": "current-submission-id-ignored",
            "broker_event_type": "acknowledgement",
        },
        "issues": [],
        "verified_fields": ["health.status"],
    }
    baseline_payload = {
        **raw_summary,
        "result": {
            **raw_summary["result"],
            "source_name": "qmt/other-source",
        },
    }
    baseline_path.write_text(json.dumps(baseline_payload, indent=2), encoding="utf-8")

    fixed_summary_path = report_dir / "20260430T120000Z-windows-qmt-contract-acceptance.json"
    fixed_markdown_path = report_dir / "20260430T120000Z-windows-qmt-contract-comparison.md"

    monkeypatch.setattr(
        MODULE,
        "parse_args",
        lambda argv=None: type(
            "Args",
            (),
            {
                "summary_output": None,
                "report_dir": str(report_dir),
                "compare_with": str(baseline_path),
                "comparison_markdown_output": None,
            },
        )(),
    )
    monkeypatch.setattr(
        MODULE,
        "build_config_from_args",
        lambda args: MODULE.AcceptanceHarnessConfig(
            base_url="http://bridge.local",
            bridge_token="secret-token",
            bridge_contract_version="1",
        ),
    )

    async def _run_acceptance_harness(config: object) -> dict[str, object]:
        return dict(raw_summary)

    monkeypatch.setattr(MODULE, "run_acceptance_harness", _run_acceptance_harness)
    monkeypatch.setattr(MODULE, "build_output_metadata", lambda now=None: dict(output_metadata))
    monkeypatch.setattr(MODULE, "build_timestamped_summary_output_path", lambda path: fixed_summary_path)
    monkeypatch.setattr(MODULE, "build_timestamped_comparison_markdown_output_path", lambda path: fixed_markdown_path)

    exit_code = MODULE.main([])

    latest_summary_path = report_dir / "latest.json"
    latest_markdown_path = report_dir / "latest-comparison.md"
    persisted_summary = json.loads(latest_summary_path.read_text(encoding="utf-8"))
    assert exit_code == 3
    assert persisted_summary["comparison"]["markdown_output"] == str(fixed_markdown_path)
    assert persisted_summary["comparison"]["latest_markdown_output"] == str(latest_markdown_path)
    assert fixed_markdown_path.exists()
    assert latest_markdown_path.exists()
