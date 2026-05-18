from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "web", "backend"))

from app.api.contract.services.impact_analyzer import ContractImpactAnalyzer
from app.api.contract.services.impact_notifications import ContractImpactNotificationService


def test_contract_impact_notification_requires_action_for_breaking_endpoint() -> None:
    from_spec = {
        "paths": {
            "/api/v1/market/quotes": {
                "get": {
                    "operationId": "getMarketQuotes",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        }
    }
    to_spec = {"paths": {}}

    analysis = ContractImpactAnalyzer().analyze_specs(from_spec, to_spec, "1.0.0", "2.0.0")

    notifications = ContractImpactNotificationService().build_notifications(analysis)

    assert len(notifications) == 1
    notification = notifications[0]
    assert notification.kind == "contract_impact"
    assert notification.priority == "urgent"
    assert notification.action_required is True
    assert notification.targets == ["api-governance", "market"]
    assert notification.action_url == "/system/api"
    assert "1.0.0 -> 2.0.0" in notification.title
    assert notification.metadata["risk_level"] == "critical"
    assert notification.metadata["breaking_impacts"] == 1
    assert notification.metadata["migration_effort"] == "high"


def test_contract_impact_notification_suppresses_noop_analysis() -> None:
    spec = {
        "paths": {
            "/api/v1/market/quotes": {
                "get": {
                    "operationId": "getMarketQuotes",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        }
    }

    analysis = ContractImpactAnalyzer().analyze_specs(spec, spec, "1.0.0", "1.0.0")

    assert ContractImpactNotificationService().build_notifications(analysis) == []


@pytest.mark.asyncio
async def test_contract_impact_notification_dispatches_realtime_system_notification() -> None:
    class FakeConnectionManager:
        def __init__(self) -> None:
            self.broadcasts = []

        async def broadcast_system_notification(self, notification) -> None:
            self.broadcasts.append(notification)

    from_spec = {
        "paths": {
            "/api/v1/market/quotes": {
                "get": {
                    "operationId": "getMarketQuotes",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        }
    }
    to_spec = {"paths": {}}
    service = ContractImpactNotificationService()
    manager = FakeConnectionManager()
    analysis = ContractImpactAnalyzer().analyze_specs(from_spec, to_spec, "1.0.0", "2.0.0")
    notifications = service.build_notifications(analysis)

    await service.dispatch_notifications(notifications, connection_manager=manager)

    assert len(manager.broadcasts) == 1
    realtime_notification = manager.broadcasts[0]
    assert realtime_notification.type == "system"
    assert realtime_notification.priority == "urgent"
    assert realtime_notification.action_required is True
    assert realtime_notification.action_url == "/system/api"
    assert realtime_notification.data["kind"] == "contract_impact"
    assert realtime_notification.data["targets"] == ["api-governance", "market"]
