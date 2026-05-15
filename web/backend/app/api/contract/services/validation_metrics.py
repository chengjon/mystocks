"""Prometheus metrics for API contract validation."""

from __future__ import annotations

from prometheus_client import Counter, Gauge

from app.api.prometheus_exporter import prometheus_registry


contract_validation_total = Counter(
    "mystocks_contract_validation_total",
    "Total API contract validation runs",
    ["result"],
    registry=prometheus_registry,
)

contract_validation_success_rate = Gauge(
    "mystocks_contract_validation_success_rate",
    "API contract validation success rate in the current process",
    registry=prometheus_registry,
)

_contract_validation_counts = {"success": 0, "failure": 0}


def record_contract_validation(valid: bool) -> None:
    """记录契约验证成功率指标。"""
    result = "success" if valid else "failure"
    contract_validation_total.labels(result=result).inc()
    _contract_validation_counts[result] += 1

    total = _contract_validation_counts["success"] + _contract_validation_counts["failure"]
    contract_validation_success_rate.set(_contract_validation_counts["success"] / total if total else 0)
