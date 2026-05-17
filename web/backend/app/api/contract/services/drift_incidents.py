"""In-process contract drift incident tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.api.contract.schemas import ValidationResult


@dataclass(frozen=True)
class ContractDriftIncident:
    """Recorded contract drift incident produced by validation."""

    kind: str
    severity: str
    path: str
    message: str
    suggestion: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


_contract_drift_incidents: list[ContractDriftIncident] = []


def record_contract_drift_incident(incident: ContractDriftIncident) -> None:
    """Append a contract drift incident to the in-process registry."""
    _contract_drift_incidents.append(incident)


def list_contract_drift_incidents() -> list[ContractDriftIncident]:
    """Return all recorded contract drift incidents in insertion order."""
    return list(_contract_drift_incidents)


def clear_contract_drift_incidents() -> None:
    """Clear recorded contract drift incidents."""
    _contract_drift_incidents.clear()


def record_contract_drift_incidents_from_validation_results(
    results: list[ValidationResult],
    *,
    source: str = "contract_validation",
) -> None:
    """Record drift incidents from breaking-change validation results."""
    for result in results:
        kind = _incident_kind_for(result)
        if kind is None:
            continue
        record_contract_drift_incident(
            ContractDriftIncident(
                kind=kind,
                severity=result.category,
                path=result.path or "",
                message=result.message,
                suggestion=result.suggestion,
                metadata={"source": source},
            )
        )


def record_contract_drift_incidents(results: list[ValidationResult]) -> None:
    """Record contract drift incidents from validator breaking-change results."""
    record_contract_drift_incidents_from_validation_results(results)


def _incident_kind_for(result: ValidationResult) -> str | None:
    if (result.path or "").startswith("paths.") and result.message.startswith("删除API端点"):
        return "endpoint_removed"
    if (result.path or "").startswith("components.schemas.") and result.message.startswith("删除Schema"):
        return "schema_removed"
    return None
