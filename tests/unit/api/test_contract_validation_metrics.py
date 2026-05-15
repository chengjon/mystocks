from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3] / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.api.contract.services import validator as validator_module
from app.api.contract.services.validation_metrics import record_contract_validation
from app.api.prometheus_exporter import prometheus_registry


def _sample_value(metric_name: str, labels: dict[str, str] | None = None) -> float:
    expected_labels = labels or {}
    for metric in prometheus_registry.collect():
        for sample in metric.samples:
            if sample.name != metric_name:
                continue
            if all(sample.labels.get(key) == value for key, value in expected_labels.items()):
                return float(sample.value)
    return 0.0


def test_contract_validation_metric_records_success_and_failure_results() -> None:
    success_before = _sample_value("mystocks_contract_validation_total", {"result": "success"})
    failure_before = _sample_value("mystocks_contract_validation_total", {"result": "failure"})

    record_contract_validation(valid=True)
    record_contract_validation(valid=False)

    assert _sample_value("mystocks_contract_validation_total", {"result": "success"}) == success_before + 1
    assert _sample_value("mystocks_contract_validation_total", {"result": "failure"}) == failure_before + 1


def test_contract_validation_success_rate_gauge_tracks_process_rate() -> None:
    record_contract_validation(valid=True)

    success_rate = _sample_value("mystocks_contract_validation_success_rate")

    assert 0 < success_rate <= 1


def test_contract_validator_records_validation_metric(monkeypatch) -> None:
    recorded: list[bool] = []
    monkeypatch.setattr(validator_module, "PRANCE_AVAILABLE", False)
    monkeypatch.setattr(validator_module, "record_contract_validation", lambda valid: recorded.append(valid))

    response = validator_module.ContractValidator.validate(
        {
            "openapi": "3.0.0",
            "info": {"title": "Contract Metrics Test", "version": "1.0.0"},
            "paths": {},
        },
        check_breaking_changes=False,
    )

    assert response.valid is True
    assert recorded == [True]
