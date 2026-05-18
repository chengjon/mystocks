"""Notification planning for contract impact analysis."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from app.api.contract.services.impact_analyzer import ContractImpactAnalysis
from app.api.notification_models import RealTimeNotification


@dataclass(frozen=True)
class ContractImpactNotification:
    """Machine-readable notification generated from a contract impact analysis."""

    kind: str
    priority: str
    title: str
    message: str
    targets: list[str]
    action_required: bool
    action_url: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


class ContractImpactNotificationService:
    """Build governance notifications for actionable contract impact results."""

    action_url = "/system/api"

    def build_notifications(self, analysis: ContractImpactAnalysis) -> list[ContractImpactNotification]:
        """Return notification payloads when an impact analysis requires attention."""
        if analysis.summary.total_impacts == 0:
            return []

        priority = self._priority_for(analysis)
        action_required = self._requires_action(analysis)
        targets = self._targets_for(analysis)

        return [
            ContractImpactNotification(
                kind="contract_impact",
                priority=priority,
                title=f"Contract impact {analysis.from_version} -> {analysis.to_version}: {analysis.risk_level} risk",
                message=self._message_for(analysis),
                targets=targets,
                action_required=action_required,
                action_url=self.action_url if action_required else None,
                metadata={
                    "risk_level": analysis.risk_level,
                    "total_impacts": analysis.summary.total_impacts,
                    "breaking_impacts": analysis.summary.breaking_impacts,
                    "migration_effort": analysis.migration_effort.level,
                    "estimated_hours_min": analysis.migration_effort.estimated_hours_min,
                    "estimated_hours_max": analysis.migration_effort.estimated_hours_max,
                    "affected_clients": analysis.affected_clients,
                    "affected_endpoints": analysis.affected_endpoints,
                    "affected_schemas": analysis.affected_schemas,
                },
            )
        ]

    async def dispatch_notifications(
        self,
        notifications: list[ContractImpactNotification],
        *,
        connection_manager: Any | None = None,
    ) -> int:
        """Broadcast contract impact notifications through the existing realtime notification seam."""
        if not notifications:
            return 0

        manager = connection_manager
        if manager is None:
            from app.api.notification_support import connection_manager as default_connection_manager

            manager = default_connection_manager

        dispatched = 0
        for notification in notifications:
            await manager.broadcast_system_notification(self.to_realtime_notification(notification))
            dispatched += 1
        return dispatched

    def to_realtime_notification(self, notification: ContractImpactNotification) -> RealTimeNotification:
        notification_key = f"{notification.kind}:{notification.title}:{notification.message}"
        return RealTimeNotification(
            notification_id=f"contract-impact-{uuid.uuid5(uuid.NAMESPACE_URL, notification_key).hex}",
            user_id=0,
            type="system",
            title=notification.title,
            message=notification.message,
            data={
                "kind": notification.kind,
                "targets": notification.targets,
                "metadata": notification.metadata,
            },
            priority=notification.priority,
            action_required=notification.action_required,
            action_url=notification.action_url,
        )

    def _priority_for(self, analysis: ContractImpactAnalysis) -> str:
        if analysis.risk_level == "critical":
            return "urgent"
        if analysis.risk_level == "high" or analysis.migration_effort.level in {"high", "critical"}:
            return "high"
        if analysis.risk_level == "medium" or analysis.summary.breaking_impacts:
            return "normal"
        return "low"

    def _requires_action(self, analysis: ContractImpactAnalysis) -> bool:
        return (
            analysis.summary.breaking_impacts > 0
            or analysis.risk_level in {"high", "critical"}
            or analysis.migration_effort.level in {"high", "critical"}
        )

    def _targets_for(self, analysis: ContractImpactAnalysis) -> list[str]:
        targets = ["api-governance", *analysis.affected_clients]
        return sorted(set(targets), key=targets.index)

    def _message_for(self, analysis: ContractImpactAnalysis) -> str:
        return (
            f"{analysis.summary.total_impacts} impact(s), "
            f"{analysis.summary.breaking_impacts} breaking; "
            f"migration effort {analysis.migration_effort.level} "
            f"({analysis.migration_effort.estimated_hours_min}-"
            f"{analysis.migration_effort.estimated_hours_max}h)."
        )
