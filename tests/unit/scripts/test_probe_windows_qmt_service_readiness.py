from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = PROJECT_ROOT / "scripts" / "dev" / "probe_windows_qmt_service_readiness.py"
SPEC = importlib.util.spec_from_file_location("probe_windows_qmt_service_readiness", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


@pytest.mark.asyncio
async def test_run_readiness_probe_reports_l3_ready_for_kernel_phase_a_mock() -> None:
    config = MODULE.ReadinessProbeConfig(
        base_url="http://bridge.local",
        bridge_token="secret-token",
        bridge_contract_version="1",
        contract_profile="kernel-phase-a",
        expected_provider_mode="mock",
    )

    async def _health_fetcher(base_url: str, timeout_seconds: float) -> dict[str, object]:
        assert base_url == "http://bridge.local"
        return {
            "status": "online",
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "mock",
        }

    summary = await MODULE.run_readiness_probe(config, health_fetcher=_health_fetcher)

    assert summary["ok"] is True
    assert summary["status_label"] == "l3_acceptance_ready"
    assert summary["levels"]["l1_process_ready"]["passed"] is True
    assert summary["levels"]["l2_contract_ready"]["passed"] is True
    assert summary["levels"]["l3_acceptance_ready"]["passed"] is True
    assert summary["issues"] == []


@pytest.mark.asyncio
async def test_run_readiness_probe_reports_l2_only_when_local_token_missing() -> None:
    config = MODULE.ReadinessProbeConfig(
        base_url="http://bridge.local",
        bridge_token="",
        bridge_contract_version="1",
        contract_profile="kernel-phase-a",
        expected_provider_mode="mock",
    )

    async def _health_fetcher(base_url: str, timeout_seconds: float) -> dict[str, object]:
        return {
            "status": "online",
            "provider_mode": "mock",
            "bridge_contract_version": "1",
            "bridge_auth_configured": True,
            "source_name": "mock",
        }

    summary = await MODULE.run_readiness_probe(config, health_fetcher=_health_fetcher)

    assert summary["ok"] is False
    assert summary["status_label"] == "l2_contract_ready_only"
    assert summary["levels"]["l1_process_ready"]["passed"] is True
    assert summary["levels"]["l2_contract_ready"]["passed"] is True
    assert summary["levels"]["l3_acceptance_ready"]["passed"] is False
    assert "bridge token" in summary["issues"][0].lower()


@pytest.mark.asyncio
async def test_run_readiness_probe_reports_l1_only_when_health_disclosure_is_incomplete() -> None:
    config = MODULE.ReadinessProbeConfig(
        base_url="http://bridge.local",
        bridge_token="secret-token",
        bridge_contract_version="1",
        contract_profile="kernel-phase-a",
        expected_provider_mode="mock",
    )

    async def _health_fetcher(base_url: str, timeout_seconds: float) -> dict[str, object]:
        return {
            "status": "online",
            "provider_mode": "mock",
        }

    summary = await MODULE.run_readiness_probe(config, health_fetcher=_health_fetcher)

    assert summary["ok"] is False
    assert summary["status_label"] == "l1_process_ready_only"
    assert summary["levels"]["l1_process_ready"]["passed"] is True
    assert summary["levels"]["l2_contract_ready"]["passed"] is False
    assert summary["levels"]["l3_acceptance_ready"]["passed"] is False
    assert any("bridge_contract_version" in issue for issue in summary["issues"])


def test_main_writes_timestamped_and_latest_readiness_artifacts(tmp_path: Path, monkeypatch, capsys) -> None:
    report_dir = tmp_path / "reports"

    async def _fake_run_readiness_probe(*args, **kwargs) -> dict[str, object]:
        return {
            "ok": True,
            "status_label": "l3_acceptance_ready",
            "recommended_exit_code": 0,
            "summary_schema_version": 1,
            "runtime_environment": "wsl-ubuntu-24.04.4-lts",
            "generated_at": "2026-05-01T01:00:00+00:00",
            "levels": {
                "l1_process_ready": {"passed": True, "issues": [], "verified_fields": ["health.reachable"]},
                "l2_contract_ready": {"passed": True, "issues": [], "verified_fields": ["health.bridge_contract_version"]},
                "l3_acceptance_ready": {"passed": True, "issues": [], "verified_fields": ["local.bridge_token_configured"]},
            },
            "issues": [],
        }

    monkeypatch.setattr(MODULE, "run_readiness_probe", _fake_run_readiness_probe)

    exit_code = MODULE.main(
        [
            "--base-url",
            "http://bridge.local",
            "--bridge-token",
            "secret-token",
            "--report-dir",
            str(report_dir),
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status_label"] == "l3_acceptance_ready"
    assert Path(payload["artifacts"]["report_artifact"]).exists()
    assert Path(payload["artifacts"]["latest"]).exists()


def test_main_reports_configuration_invalid_when_base_url_is_missing(capsys) -> None:
    exit_code = MODULE.main([])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 2
    assert payload["status_label"] == "configuration_invalid"
    assert payload["levels"]["l1_process_ready"]["passed"] is False


def test_parse_args_accepts_reference_service_profile() -> None:
    args = MODULE.parse_args(
        [
            "--base-url",
            "http://bridge.local",
            "--contract-profile",
            "reference-service",
        ]
    )

    assert args.contract_profile == "reference-service"
