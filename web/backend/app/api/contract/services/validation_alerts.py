"""Realtime alerting for contract validation failures."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from app.api.contract.schemas import ContractValidateResponse
from app.api.notification_models import RealTimeNotification


@dataclass(frozen=True)
class ContractValidationAlert:
    """Machine-readable alert generated from failed contract validation."""

    kind: str
    priority: str
    title: str
    message: str
    targets: list[str]
    action_required: bool
    action_url: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


class ContractValidationAlertService:
    """Build and dispatch governance alerts for failed contract validation results."""

    action_url = "/system/api"

    def build_alerts(self, validation: ContractValidateResponse) -> list[ContractValidationAlert]:
        """Return alert payloads only when validation fails."""
        if validation.valid:
            return []

        error_paths = [
            result.path
            for result in validation.results
            if result.category == "error" and result.path is not None
        ]

        return [
            ContractValidationAlert(
                kind="contract_validation_failure",
                priority="high",
                title="Contract validation failed",
                message=(
                    f"{validation.error_count} error(s), "
                    f"{validation.warning_count} warning(s) found during contract validation."
                ),
                targets=["api-governance"],
                action_required=True,
                action_url=self.action_url,
                metadata={
                    "error_count": validation.error_count,
                    "warning_count": validation.warning_count,
                    "result_count": len(validation.results),
                    "error_paths": error_paths,
                },
            )
        ]

    async def dispatch_alerts(
        self,
        alerts: list[ContractValidationAlert],
        *,
        connection_manager: Any | None = None,
    ) -> int:
        """Broadcast validation failure alerts through the existing realtime notification channel."""
        if not alerts:
            return 0

        manager = connection_manager
        if manager is None:
            from app.api.notification_support import connection_manager as default_connection_manager

            manager = default_connection_manager

        dispatched = 0
        for alert in alerts:
            await manager.broadcast_system_notification(self.to_realtime_notification(alert))
            dispatched += 1
        return dispatched

    def to_realtime_notification(self, alert: ContractValidationAlert) -> RealTimeNotification:
        alert_key = f"{alert.kind}:{alert.title}:{alert.message}:{alert.metadata}"
        return RealTimeNotification(
            notification_id=f"contract-validation-{uuid.uuid5(uuid.NAMESPACE_URL, alert_key).hex}",
            user_id=0,
            type="system",
            title=alert.title,
            message=alert.message,
            data={
                "kind": alert.kind,
                "targets": alert.targets,
                "metadata": alert.metadata,
            },
            priority=alert.priority,
            action_required=alert.action_required,
            action_url=alert.action_url,
        )
