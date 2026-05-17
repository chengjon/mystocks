from __future__ import annotations

import os
import sys

from prometheus_client import generate_latest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "web", "backend"))

from app.api.contract.services.drift_incidents import (
    ContractDriftIncident,
    clear_contract_drift_incidents,
    list_contract_drift_incidents,
    record_contract_drift_incident,
)
from app.api.prometheus_exporter import prometheus_registry
from app.api.contract.services.validator import ContractValidator


def test_contract_validation_records_drift_incident_for_removed_endpoint() -> None:
    clear_contract_drift_incidents()
    old_spec = {
        "openapi": "3.1.0",
        "info": {"title": "Market API", "version": "1.0.0"},
        "paths": {"/api/v1/market/quotes": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    new_spec = {
        "openapi": "3.1.0",
        "info": {"title": "Market API", "version": "2.0.0"},
        "paths": {},
    }

    response = ContractValidator.validate(new_spec, check_breaking_changes=True, compare_to_spec=old_spec)

    incidents = list_contract_drift_incidents()
    assert response.warning_count >= 1
    assert len(incidents) == 1
    incident = incidents[0]
    assert incident.kind == "endpoint_removed"
    assert incident.severity == "warning"
    assert incident.path == "paths./api/v1/market/quotes"
    assert "删除API端点" in incident.message
    assert incident.metadata["source"] == "contract_validation"


def test_contract_validation_does_not_record_drift_without_baseline_comparison() -> None:
    clear_contract_drift_incidents()
    spec = {
        "openapi": "3.1.0",
        "info": {"title": "Market API", "version": "1.0.0"},
        "paths": {"/api/v1/market/quotes": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }

    ContractValidator.validate(spec, check_breaking_changes=True, compare_to_spec=None)

    assert list_contract_drift_incidents() == []


def test_recording_drift_incident_exports_prometheus_counter() -> None:
    record_contract_drift_incident(
        ContractDriftIncident(
            kind="unit_probe",
            severity="warning",
            path="/api/contracts",
            message="Unit probe drift incident",
        )
    )

    metrics = generate_latest(prometheus_registry).decode("utf-8")

    assert 'mystocks_contract_drift_incidents_total{kind="unit_probe",severity="warning"}' in metrics
