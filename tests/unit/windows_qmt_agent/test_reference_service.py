from __future__ import annotations

from fastapi.testclient import TestClient

from scripts.windows_qmt_agent.app import create_app
from scripts.windows_qmt_agent.config import (
    PROVIDER_MODE_MINIQMT_SDK,
    PROVIDER_MODE_MOCK,
    WindowsQmtAgentSettings,
)
from scripts.windows_qmt_agent.service import BRIDGE_CONTRACT_VERSION_HEADER


def _build_settings(*, provider_mode: str = PROVIDER_MODE_MOCK) -> WindowsQmtAgentSettings:
    return WindowsQmtAgentSettings(
        node_name="WIN-QMT-REF-TEST",
        bridge_token="test-token",
        bridge_contract_version="1",
        provider_mode=provider_mode,
        source_name="qmt/windows_reference_service",
        host="127.0.0.1",
        port=8001,
        default_account_scope="wsl-ubuntu-paper-account",
        default_pending_delay_seconds=0.0,
        miniqmt_sdk_enabled=False,
    )


def _headers(token: str = "test-token", version: str = "1") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        BRIDGE_CONTRACT_VERSION_HEADER: version,
    }


def test_reference_service_rejects_invalid_authentication() -> None:
    client = TestClient(create_app(_build_settings()))

    response = client.post(
        "/api/v1/task/execute",
        headers=_headers(token="wrong-token"),
        json={"provider": "qmt", "method": "submit_order", "params": {"symbol": "000001"}},
    )

    assert response.status_code == 401
    assert response.json()["reason_code"] == "live_bridge_auth_failed"
    assert response.headers[BRIDGE_CONTRACT_VERSION_HEADER] == "1"


def test_reference_service_rejects_unsupported_contract_version() -> None:
    client = TestClient(create_app(_build_settings()))

    response = client.post(
        "/api/v1/task/execute",
        headers=_headers(version="2"),
        json={"provider": "qmt", "method": "submit_order", "params": {"symbol": "000001"}},
    )

    assert response.status_code == 409
    assert response.json()["reason_code"] == "live_bridge_unsupported_contract_version"


def test_reference_service_rejects_unsupported_provider_method_pair() -> None:
    client = TestClient(create_app(_build_settings()))

    response = client.post(
        "/api/v1/task/execute",
        headers=_headers(),
        json={"provider": "qmt", "method": "cancel_order", "params": {"order_id": "ord-1"}},
    )

    assert response.status_code == 405
    assert response.json()["reason_code"] == "live_bridge_unsupported_method"


def test_reference_service_mock_mode_creates_receipt_and_terminal_result() -> None:
    client = TestClient(create_app(_build_settings()))

    receipt_response = client.post(
        "/api/v1/task/execute",
        headers=_headers(),
        json={
            "provider": "qmt",
            "method": "submit_order",
            "params": {
                "client_order_id": "submission-0301",
                "account_scope": "sim-account-0301",
                "symbol": "000001",
            },
        },
    )

    assert receipt_response.status_code == 202
    receipt_payload = receipt_response.json()
    assert receipt_payload["status"] == "accepted"
    assert receipt_payload["provider_mode"] == "mock"

    result_response = client.get(
        f"/api/v1/task/result/{receipt_payload['task_id']}",
        headers=_headers(),
    )

    assert result_response.status_code == 200
    result_payload = result_response.json()
    assert result_payload["result_status"] == "completed"
    assert result_payload["provider_mode"] == "mock"
    assert result_payload["bridge_contract_version"] == "1"
    assert result_payload["source_name"] == "qmt/windows_reference_service"
    assert result_payload["result"]["status"] == "accepted"
    assert result_payload["result"]["account_scope"] == "sim-account-0301"
    assert result_payload["result"]["event_id"].startswith("mock-event-")
    assert result_payload["result"]["occurred_at"]
    assert result_payload["result"]["source_name"] == "qmt/windows_reference_service"


def test_reference_service_mock_mode_supports_pending_polling() -> None:
    client = TestClient(create_app(_build_settings()))

    receipt_response = client.post(
        "/api/v1/task/execute",
        headers=_headers(),
        json={
            "provider": "qmt",
            "method": "submit_order",
            "params": {
                "client_order_id": "submission-0302",
                "mock_delay_seconds": 60,
            },
        },
    )
    task_id = receipt_response.json()["task_id"]

    result_response = client.get(f"/api/v1/task/result/{task_id}", headers=_headers())

    assert result_response.status_code == 200
    payload = result_response.json()
    assert payload["status"] == "pending"
    assert payload["result_status"] == "pending"
    assert payload["provider_mode"] == "mock"


def test_reference_service_miniqmt_sdk_mode_fails_closed() -> None:
    client = TestClient(create_app(_build_settings(provider_mode=PROVIDER_MODE_MINIQMT_SDK)))

    receipt_response = client.post(
        "/api/v1/task/execute",
        headers=_headers(),
        json={"provider": "qmt", "method": "submit_order", "params": {"client_order_id": "submission-0303"}},
    )
    task_id = receipt_response.json()["task_id"]

    result_response = client.get(f"/api/v1/task/result/{task_id}", headers=_headers())

    assert result_response.status_code == 503
    payload = result_response.json()
    assert payload["reason_code"] == "live_bridge_unavailable"
    assert payload["provider_mode"] == "miniqmt_sdk"
