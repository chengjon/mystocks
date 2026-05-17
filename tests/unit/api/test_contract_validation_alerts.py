from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "web", "backend"))

from app.api.contract.schemas import ContractValidateResponse, ValidationResult
from app.api.contract.services.validation_alerts import ContractValidationAlertService


def _invalid_validation_response() -> ContractValidateResponse:
    return ContractValidateResponse(
        valid=False,
        error_count=1,
        warning_count=1,
        results=[
            ValidationResult(
                valid=False,
                category="error",
                path="paths./api/example.get.responses.200",
                message="缺少响应Schema",
                suggestion="为 200 响应补充 schema",
            ),
            ValidationResult(
                valid=False,
                category="warning",
                path="info.description",
                message="建议补充API描述",
            ),
        ],
    )


def test_contract_validation_alert_builds_high_priority_alert_for_invalid_contract() -> None:
    alerts = ContractValidationAlertService().build_alerts(_invalid_validation_response())

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.kind == "contract_validation_failure"
    assert alert.priority == "high"
    assert alert.action_required is True
    assert alert.action_url == "/system/api"
    assert alert.targets == ["api-governance"]
    assert alert.metadata["error_count"] == 1
    assert alert.metadata["warning_count"] == 1
    assert alert.metadata["error_paths"] == ["paths./api/example.get.responses.200"]


def test_contract_validation_alert_suppresses_valid_contract() -> None:
    response = ContractValidateResponse(valid=True, error_count=0, warning_count=1, results=[])

    assert ContractValidationAlertService().build_alerts(response) == []


@pytest.mark.asyncio
async def test_contract_validation_alert_dispatches_realtime_system_notification() -> None:
    class FakeConnectionManager:
        def __init__(self) -> None:
            self.broadcasts = []

        async def broadcast_system_notification(self, notification) -> None:
            self.broadcasts.append(notification)

    service = ContractValidationAlertService()
    manager = FakeConnectionManager()
    alerts = service.build_alerts(_invalid_validation_response())

    await service.dispatch_alerts(alerts, connection_manager=manager)

    assert len(manager.broadcasts) == 1
    realtime_notification = manager.broadcasts[0]
    assert realtime_notification.type == "system"
    assert realtime_notification.priority == "high"
    assert realtime_notification.action_required is True
    assert realtime_notification.action_url == "/system/api"
    assert realtime_notification.data["kind"] == "contract_validation_failure"
    assert realtime_notification.data["targets"] == ["api-governance"]
