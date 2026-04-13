from __future__ import annotations

import ast
import asyncio
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_main_lifespan_initializes_risk_management_system() -> None:
    main_path = PROJECT_ROOT / "web/backend/app/main.py"
    tree = ast.parse(main_path.read_text(encoding="utf-8"))

    lifespan_fn = next(
        node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "lifespan"
    )

    call_names = {
        node.func.id
        for node in ast.walk(lifespan_fn)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert "initialize_risk_management_system" in call_names


def test_stop_loss_execution_service_can_build_default_order_service(monkeypatch) -> None:
    from src.governance.risk_management.services import stop_loss_execution_service as module

    sentinel_order_service = object()
    created_with: list[object] = []

    class FakeStopLossExecutionService:
        def __init__(self, order_service):
            created_with.append(order_service)

    monkeypatch.setattr(module, "_stop_loss_execution_service", None)
    monkeypatch.setattr(module, "_build_default_order_service", lambda: sentinel_order_service)
    monkeypatch.setattr(module, "StopLossExecutionService", FakeStopLossExecutionService)

    service = module.get_stop_loss_execution_service()

    assert isinstance(service, FakeStopLossExecutionService)
    assert created_with == [sentinel_order_service]


def test_v31_alert_endpoints_use_runtime_notification_manager_even_without_feature_flag(monkeypatch) -> None:
    from web.backend.app.api.risk import alerts as module

    class FakeNotificationManager:
        async def send_risk_alert(self, **kwargs):
            return {"sent": True, "payload": kwargs}

        def get_alert_statistics(self):
            return {"total_alerts_sent": 1}

    monkeypatch.setattr(module, "ENHANCED_RISK_FEATURES_AVAILABLE", False)
    monkeypatch.setattr(module, "get_risk_alert_notification_manager", lambda: FakeNotificationManager())

    send_result = asyncio.run(module.send_risk_alert({"alert_type": "drawdown", "severity": "warning"}))
    stats_result = asyncio.run(module.get_alert_statistics())

    assert send_result["sent"] is True
    assert stats_result["total_alerts_sent"] == 1


def test_v31_rule_endpoints_use_runtime_rule_engine_even_without_feature_flag(monkeypatch) -> None:
    from web.backend.app.api.risk import alerts as module

    class FakeAlertContext:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeSeverity:
        value = "warning"

    class FakeResult:
        rule_id = "rule-1"
        severity = FakeSeverity()
        actions = [{"type": "notify"}]
        evaluation_details = {"matched": True}

    class FakeRuleEngine:
        async def evaluate_rules(self, context):
            return [FakeResult()]

        def add_rule(self, rule):
            return True

        def remove_rule(self, rule_id):
            return True

        def get_rule_statistics(self):
            return {"total_rules": 1}

    monkeypatch.setattr(module, "ENHANCED_RISK_FEATURES_AVAILABLE", False)
    monkeypatch.setattr(module, "AlertContext", FakeAlertContext)
    monkeypatch.setattr(module, "get_alert_rule_engine", lambda: FakeRuleEngine())

    evaluation = asyncio.run(module.evaluate_alert_rules({"metrics": {"drawdown": 0.12}}))
    added = asyncio.run(
        module.add_alert_rule(
            {
                "rule_id": "rule-1",
                "name": "回撤预警",
                "description": "desc",
                "conditions": [],
                "actions": [{"type": "notify"}],
            }
        )
    )
    removed = asyncio.run(module.remove_alert_rule("rule-1"))
    stats = asyncio.run(module.get_rule_statistics())

    assert evaluation[0]["rule_id"] == "rule-1"
    assert added["success"] is True
    assert removed["success"] is True
    assert stats["total_rules"] == 1


def test_v31_stop_loss_history_endpoints_use_runtime_history_service_even_without_feature_flag(monkeypatch) -> None:
    from web.backend.app.api.risk import stop_loss as module

    class FakeHistoryService:
        async def get_strategy_performance(self, **kwargs):
            return {"total_trades": 2, "filters": kwargs}

        async def get_strategy_recommendations(self, strategy_type, symbol):
            return {"strategy_type": strategy_type, "symbol": symbol, "recommendations": ["keep"]}

    monkeypatch.setattr(module, "ENHANCED_RISK_FEATURES_AVAILABLE", False)
    monkeypatch.setattr(module, "get_stop_loss_history_service", lambda: FakeHistoryService())

    performance = asyncio.run(
        module.get_stop_loss_performance(strategy_type="volatility_adaptive", symbol="600519.SH", days=30)
    )
    recommendations = asyncio.run(
        module.get_stop_loss_recommendations(strategy_type="volatility_adaptive", symbol="600519.SH")
    )

    assert performance["total_trades"] == 2
    assert recommendations["recommendations"] == ["keep"]


def test_v31_stop_loss_execution_endpoints_use_runtime_execution_service_even_without_feature_flag(monkeypatch) -> None:
    from web.backend.app.api.risk import stop_loss as module

    class FakeExecutionService:
        async def add_position_monitoring(self, **kwargs):
            return {"success": True, "position_id": kwargs["position_id"]}

        async def update_position_price(self, **kwargs):
            return {"checked": True, "position_id": kwargs["position_id"]}

        async def remove_position_monitoring(self, position_id):
            return True

        async def get_monitoring_status(self, position_id=None):
            if position_id:
                return {"found": True, "position_id": position_id}
            return {"total_positions": 1}

        async def batch_update_prices(self, price_updates):
            return {"total_checked": len(price_updates)}

    monkeypatch.setattr(module, "ENHANCED_RISK_FEATURES_AVAILABLE", False)
    monkeypatch.setattr(module, "get_stop_loss_execution_service", lambda: FakeExecutionService())

    added = asyncio.run(
        module.add_stop_loss_position(
            {"symbol": "600519.SH", "position_id": "pos-1", "entry_price": 100.0, "quantity": 10}
        )
    )
    updated = asyncio.run(module.update_stop_loss_price({"position_id": "pos-1", "current_price": 95.0}))
    status = asyncio.run(module.get_stop_loss_status("pos-1"))
    overview = asyncio.run(module.get_stop_loss_overview())
    batch = asyncio.run(module.batch_update_stop_loss_prices({"price_updates": {"600519.SH": 95.0}}))
    removed = asyncio.run(module.remove_stop_loss_position("pos-1"))

    assert added["success"] is True
    assert updated["checked"] is True
    assert status["found"] is True
    assert overview["total_positions"] == 1
    assert batch["total_checked"] == 1
    assert removed["success"] is True


def test_v31_active_alerts_reads_runtime_alert_history(monkeypatch) -> None:
    from web.backend.app.api.risk import alerts as module

    class FakeAlertService:
        alert_history = {
            "600519.SH_unknown_warning": [
                {"risk_level": "warning", "timestamp": datetime(2026, 4, 13, 12, 0, 0)},
                {"risk_level": "warning", "timestamp": datetime(2026, 4, 13, 12, 5, 0)},
            ]
        }

    class FakeCore:
        alert_service = FakeAlertService()

    monkeypatch.setattr(module, "RISK_MANAGEMENT_V31_AVAILABLE", True)
    monkeypatch.setattr(module, "_acknowledged_v31_alerts", {})
    monkeypatch.setattr(module, "get_risk_management_core", lambda: FakeCore())

    payload = asyncio.run(module.get_active_alerts_v31())

    assert payload["data"]["total"] == 1
    assert payload["data"]["alerts"][0]["alert_key"] == "600519.SH_unknown_warning"
    assert payload["data"]["alerts"][0]["trigger_count"] == 2


def test_v31_acknowledge_alert_uses_runtime_active_alert_registry(monkeypatch) -> None:
    from web.backend.app.api.risk import alerts as module

    class FakeAlertService:
        alert_history = {
            "600519.SH_unknown_warning": [
                {"risk_level": "warning", "timestamp": datetime(2026, 4, 13, 12, 5, 0)}
            ]
        }

    class FakeCore:
        alert_service = FakeAlertService()

    monkeypatch.setattr(module, "RISK_MANAGEMENT_V31_AVAILABLE", True)
    monkeypatch.setattr(module, "_acknowledged_v31_alerts", {})
    monkeypatch.setattr(module, "get_risk_management_core", lambda: FakeCore())

    payload = asyncio.run(
        module.acknowledge_alert_v31(1, {"action_taken": "reduced_position", "feedback": "trimmed 20%"})
    )

    assert payload["data"]["alert_id"] == 1
    assert payload["data"]["status"] == "acknowledged"
    assert module._acknowledged_v31_alerts[1]["feedback"] == "trimmed 20%"
