"""Monitoring alert-rule use-case service."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from app.models.monitoring import AlertRuleCreate, AlertRuleResponse, AlertRuleType, AlertRuleUpdate


class MonitoringAlertRuleSource(Protocol):
    """Persistence-facing alert-rule operations used by the API service."""

    def get_alert_rule_payloads(
        self,
        *,
        rule_type: str | None = None,
        is_active: bool | None = None,
    ) -> list[Any]:
        """Return serialized alert-rule payloads."""

    def create_alert_rule(self, rule_data: dict[str, Any]) -> Any:
        """Create an alert rule and return the stored model."""

    def update_alert_rule(self, rule_id: int, updates: dict[str, Any]) -> Any:
        """Update an alert rule and return the stored model."""

    def delete_alert_rule(self, rule_id: int) -> bool:
        """Delete an alert rule."""


class MonitoringAlertRuleService:
    """Application-level alert-rule orchestration for monitoring routes."""

    def __init__(
        self,
        alert_rule_source: MonitoringAlertRuleSource,
        *,
        runtime_fallback_enabled: Callable[[], bool],
        runtime_rules_loader: Callable[[], list[AlertRuleResponse]],
    ) -> None:
        self._alert_rule_source = alert_rule_source
        self._runtime_fallback_enabled = runtime_fallback_enabled
        self._runtime_rules_loader = runtime_rules_loader

    def list_rules(
        self,
        *,
        rule_type: AlertRuleType | str | None = None,
        is_active: bool | None = None,
    ) -> list[Any]:
        """List alert-rule payloads, using runtime fixtures only when explicitly enabled."""
        normalized_rule_type = rule_type.value if isinstance(rule_type, AlertRuleType) else rule_type

        try:
            return self._alert_rule_source.get_alert_rule_payloads(
                rule_type=normalized_rule_type,
                is_active=is_active,
            )
        except Exception:
            if self._runtime_fallback_enabled():
                return self._runtime_rules_loader()
            raise

    def create_rule(self, rule: AlertRuleCreate) -> AlertRuleResponse:
        """Create an alert rule and normalize the response schema."""
        created_rule = self._alert_rule_source.create_alert_rule(rule.model_dump())
        return AlertRuleResponse.model_validate(created_rule)

    def update_rule(self, rule_id: int, updates: AlertRuleUpdate) -> AlertRuleResponse:
        """Update an alert rule and normalize the response schema."""
        updated_rule = self._alert_rule_source.update_alert_rule(
            rule_id,
            updates.model_dump(exclude_unset=True),
        )
        return AlertRuleResponse.model_validate(updated_rule)

    def delete_rule(self, rule_id: int) -> dict[str, Any]:
        """Delete an alert rule and preserve the legacy route payload."""
        success = self._alert_rule_source.delete_alert_rule(rule_id)
        return {"success": success, "message": "告警规则已删除"}
