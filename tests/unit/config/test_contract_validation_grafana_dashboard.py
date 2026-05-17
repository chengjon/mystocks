from __future__ import annotations

import json
from pathlib import Path


def test_contract_validation_grafana_dashboard_tracks_validation_and_drift_metrics() -> None:
    dashboard_path = (
        Path(__file__).resolve().parents[3]
        / "config"
        / "monitoring-stack"
        / "provisioning"
        / "dashboards"
        / "contract-validation-dashboard.json"
    )

    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    expressions = [
        target["expr"]
        for panel in dashboard["panels"]
        for target in panel.get("targets", [])
        if target.get("expr")
    ]

    assert dashboard["uid"] == "mystocks-contract-validation-v1"
    assert dashboard["title"] == "MyStocks - Contract Validation Governance"
    assert "contract-management" in dashboard["tags"]
    assert any("mystocks_contract_validation_success_rate" in expr for expr in expressions)
    assert any('mystocks_contract_validation_total{result="success"}' in expr for expr in expressions)
    assert any('mystocks_contract_validation_total{result="failure"}' in expr for expr in expressions)
    assert any("mystocks_contract_drift_incidents_total" in expr for expr in expressions)
    assert any("mystocks_contract_drift_incidents_open" in expr for expr in expressions)
