from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping


MINIQMT_CHANNEL = "miniqmt"


class ExecutionTrackingEvidenceService:
    def __init__(
        self,
        *,
        submission_attempt_store: Any | None = None,
        divergence_store: Any | None = None,
        broker_correlation_store: Any | None = None,
        session_trigger_records: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> None:
        self.submission_attempt_store = submission_attempt_store
        self.divergence_store = divergence_store
        self.broker_correlation_store = broker_correlation_store
        self.session_trigger_records = session_trigger_records

    def load_records(
        self,
        *,
        account_id: str,
        order_id: str | None = None,
        bridge_task_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[dict[str, Any]]:
        records = self._load_attempt_records(page_size=page_size)
        if self.session_trigger_records is not None:
            records.extend(dict(record) for record in self.session_trigger_records.values())

        mapped = [self.map_record(record) for record in records]
        filtered = [record for record in mapped if record.get("account_id") == account_id]
        if order_id:
            filtered = [record for record in filtered if record.get("order_id") == order_id]
        if bridge_task_id:
            filtered = [record for record in filtered if record.get("bridge_task_id") == bridge_task_id]

        start = max(page - 1, 0) * page_size
        return filtered[start : start + page_size]

    def load_record_by_tracking_id(self, tracking_id: str) -> dict[str, Any] | None:
        records = self._load_attempt_records(page_size=100)
        if self.session_trigger_records is not None:
            records.extend(dict(record) for record in self.session_trigger_records.values())

        for record in records:
            mapped = self.map_record(record)
            if mapped.get("tracking_id") == tracking_id:
                return mapped
        return None

    def build_timeline(self, record: Mapping[str, Any]) -> list[dict[str, Any]]:
        occurred_at = str(record.get("requested_at") or _utc_now_iso())
        timeline = [
            {
                "event_type": "external_trigger_request",
                "occurred_at": occurred_at,
                "summary": "外部触发请求已记录，真实下单由外部程序处理",
                "evidence": {
                    "account_id": record.get("account_id"),
                    "order_id": record.get("order_id"),
                    "requested_by": record.get("requested_by"),
                    "client_request_id": record.get("client_request_id"),
                },
            }
        ]
        if record.get("bridge_task_id"):
            timeline.append(
                {
                    "event_type": "bridge_submission_receipt",
                    "occurred_at": occurred_at,
                    "summary": "miniQMT bridge 接收任务回执，不等于券商确认",
                    "evidence": {
                        "bridge_task_id": record.get("bridge_task_id"),
                        "receipt_status": record.get("receipt_status"),
                        "source_name": record.get("source_name"),
                    },
                }
            )
        if record.get("bridge_result_status"):
            timeline.append(
                {
                    "event_type": "bridge_task_terminal_result",
                    "occurred_at": occurred_at,
                    "summary": "bridge 任务已返回终态，但缺少 broker lifecycle identity 时仍需复核",
                    "evidence": {
                        "bridge_task_id": record.get("bridge_task_id"),
                        "result_status": record.get("bridge_result_status"),
                        "external_order_id": record.get("external_order_id"),
                    },
                }
            )
        if record.get("broker_state") == "broker_acknowledged":
            timeline.append(
                {
                    "event_type": "broker_lifecycle_identity",
                    "occurred_at": occurred_at,
                    "summary": "已关联 broker lifecycle identity",
                    "evidence": {
                        "external_order_id": record.get("external_order_id"),
                        "broker_event_type": record.get("broker_event_type"),
                        "source_name": record.get("source_name"),
                    },
                }
            )
        for incident in self._matching_divergence_incidents(record):
            timeline.append(
                {
                    "event_type": "live_bridge_review_incident",
                    "occurred_at": _as_str(incident.get("persisted_at")) or occurred_at,
                    "summary": _as_str(incident.get("reason_detail"))
                    or "miniQMT live bridge evidence requires operator review",
                    "evidence": {
                        "divergence_category": incident.get("divergence_category"),
                        "review_status": incident.get("review_status"),
                        "reason_code": incident.get("reason_code"),
                        "bridge_task_id": incident.get("bridge_task_id") or record.get("bridge_task_id"),
                        "local_submission_id": incident.get("local_submission_id"),
                    },
                }
            )
        return timeline

    def map_record(self, record: Mapping[str, Any]) -> dict[str, Any]:
        if "tracking_id" in record and "account_id" in record:
            return self._normalize_session_record(record)

        local_submission_id = _as_str(record.get("local_submission_id"))
        broker_state = resolve_broker_state(record)
        return {
            "tracking_id": f"attempt-{local_submission_id or _as_str(record.get('bridge_task_id')) or _as_str(record.get('order_id'))}",
            "account_id": _as_str(record.get("account_scope")) or "unscoped",
            "order_id": _as_str(record.get("order_id")) or "unknown",
            "symbol": _as_str(record.get("symbol")),
            "direction": _as_str(record.get("direction") or record.get("side") or "buy"),
            "quantity": _as_int(record.get("quantity")),
            "price": _as_decimal(record.get("price")),
            "requested_at": _as_str(record.get("updated_at")) or _utc_now_iso(),
            "channel": _as_str(record.get("broker_channel")) or MINIQMT_CHANNEL,
            "submission_status": _normalize_submission_status(record.get("submission_status")),
            "bridge_task_id": _as_str(record.get("bridge_task_id")),
            "receipt_status": _as_str(record.get("transport_status") or record.get("receipt_status")),
            "bridge_result_status": _as_str(record.get("bridge_result_status") or record.get("result_status")),
            "source_name": _as_str(record.get("source_name")),
            "external_order_id": _as_str(record.get("external_order_id")),
            "broker_event_type": _as_str(record.get("broker_event_type")),
            "broker_state": broker_state,
            "identity_status": "matched_broker_identity" if broker_state == "broker_acknowledged" else "missing_broker_identity",
            "reconciliation_status": _as_str(record.get("reconciliation_status")) or "not_imported",
            "raw_evidence": dict(record),
        }

    def _normalize_session_record(self, record: Mapping[str, Any]) -> dict[str, Any]:
        broker_state = resolve_broker_state(record)
        normalized = dict(record)
        normalized["broker_state"] = broker_state
        normalized["identity_status"] = (
            "matched_broker_identity" if broker_state == "broker_acknowledged" else "missing_broker_identity"
        )
        normalized.setdefault("reconciliation_status", "not_imported")
        return normalized

    def _load_attempt_records(self, *, page_size: int) -> list[dict[str, Any]]:
        if self.submission_attempt_store is None or not hasattr(self.submission_attempt_store, "fetch_recent"):
            return []
        return [dict(record) for record in self.submission_attempt_store.fetch_recent(limit=max(page_size, 100))]

    def _matching_divergence_incidents(self, record: Mapping[str, Any]) -> list[dict[str, Any]]:
        if self.divergence_store is None or not hasattr(self.divergence_store, "fetch_recent"):
            return []
        incidents = [dict(item) for item in self.divergence_store.fetch_recent(limit=100)]
        return [incident for incident in incidents if _incident_matches_record(incident, record)]


def resolve_broker_state(record: Mapping[str, Any]) -> str:
    if _as_str(record.get("external_order_id")) and _as_str(record.get("broker_event_type")):
        return "broker_acknowledged"
    return "review_required"


def _normalize_submission_status(value: Any) -> str:
    normalized = _as_str(value) or "submission_failed"
    if normalized in {"bridge_task_accepted", "broker_acknowledged", "submission_failed"}:
        return normalized
    return "submission_failed"


def _incident_matches_record(incident: Mapping[str, Any], record: Mapping[str, Any]) -> bool:
    if _as_str(incident.get("bridge_task_id")) and _as_str(incident.get("bridge_task_id")) == _as_str(
        record.get("bridge_task_id")
    ):
        return True
    if _as_str(incident.get("local_submission_id")) and _as_str(incident.get("local_submission_id")) in _as_str(
        record.get("tracking_id")
    ):
        return True
    if _as_str(incident.get("order_id")) and _as_str(incident.get("order_id")) == _as_str(record.get("order_id")):
        return True
    return False


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_int(value: Any) -> int:
    if value in (None, ""):
        return 0
    return int(value)


def _as_decimal(value: Any) -> Decimal:
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value))


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
