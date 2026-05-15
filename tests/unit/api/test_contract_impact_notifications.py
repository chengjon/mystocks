from __future__ import annotations

import os
import sys

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
