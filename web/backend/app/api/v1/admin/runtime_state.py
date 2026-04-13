from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


@dataclass
class AuditLogEntry:
    log_id: str
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AdminRuntimeStore:
    def __init__(self) -> None:
        self.audit_logs: list[AuditLogEntry] = []
        self._seeded = False

    def reset(self) -> None:
        self.audit_logs.clear()
        self._seeded = False

    def seed(self) -> None:
        if self._seeded:
            return
        now = datetime.now(timezone.utc)
        self.audit_logs.extend(
            [
                AuditLogEntry(
                    log_id="audit_seed_001",
                    user_id="admin",
                    action="LOGIN",
                    resource_type="auth",
                    resource_id="session_admin",
                    details={"status": "success"},
                    ip_address="127.0.0.1",
                    user_agent="seed/runtime",
                    timestamp=now,
                ),
                AuditLogEntry(
                    log_id="audit_seed_002",
                    user_id="system",
                    action="UPDATE",
                    resource_type="configuration",
                    resource_id="risk_limits",
                    details={"field": "max_drawdown", "value": "0.05"},
                    ip_address="127.0.0.1",
                    user_agent="seed/runtime",
                    timestamp=now,
                ),
            ]
        )
        self._seeded = True

    def add_log(
        self,
        *,
        user_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any],
        ip_address: str = "127.0.0.1",
        user_agent: str = "mystocks-v1-runtime",
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            log_id=f"audit_{uuid4().hex[:12]}",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.audit_logs.append(entry)
        return entry


runtime_store = AdminRuntimeStore()
