from __future__ import annotations

from pathlib import Path

import yaml


def test_contract_validation_alert_rules_cover_failures_and_drift() -> None:
    rules_path = Path(__file__).resolve().parents[3] / "config" / "monitoring" / "rules" / "mystocks-alerts.yml"

    data = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    alerts = {
        rule["alert"]: rule
        for group in data["groups"]
        for rule in group.get("rules", [])
        if "alert" in rule
    }

    failure_alert = alerts["ContractValidationFailureDetected"]
    drift_alert = alerts["ContractDriftIncidentDetected"]

    assert "mystocks_contract_validation_total" in failure_alert["expr"]
    assert 'result="failure"' in failure_alert["expr"]
    assert failure_alert["labels"]["severity"] == "warning"

    assert "mystocks_contract_drift_incidents_total" in drift_alert["expr"]
    assert drift_alert["labels"]["severity"] == "critical"
