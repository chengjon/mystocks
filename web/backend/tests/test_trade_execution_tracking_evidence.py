from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class FakeSubmissionAttemptStore:
    def __init__(self, records: list[dict]):
        self.records = records

    def fetch_recent(self, limit: int = 100) -> list[dict]:
        return self.records[:limit]

    def get_by_bridge_task_id(self, bridge_task_id: str, *, broker_channel: str | None = None) -> dict | None:
        for record in self.records:
            if record.get("bridge_task_id") != bridge_task_id:
                continue
            if broker_channel is not None and record.get("broker_channel") != broker_channel:
                continue
            return dict(record)
        return None


class FakeDivergenceStore:
    def __init__(self, records: list[dict]):
        self.records = records

    def fetch_recent(self, limit: int = 100) -> list[dict]:
        return self.records[:limit]


def test_miniqmt_submission_attempt_maps_to_execution_tracking_record():
    from app.services.trade.execution_tracking_evidence import ExecutionTrackingEvidenceService

    service = ExecutionTrackingEvidenceService(
        submission_attempt_store=FakeSubmissionAttemptStore(
            [
                {
                    "order_id": "order-101",
                    "local_submission_id": "local-101",
                    "broker_channel": "miniqmt",
                    "account_scope": "backtest:7",
                    "session_scope": "session-101",
                    "submission_status": "bridge_task_accepted",
                    "transport_status": "accepted",
                    "bridge_task_id": "bridge-task-101",
                    "external_order_id": None,
                    "source_name": "miniqmt/windows_bridge",
                    "updated_at": "2026-05-09T09:30:00+00:00",
                    "raw_response": {"task_id": "bridge-task-101"},
                }
            ]
        )
    )

    records = service.load_records(account_id="backtest:7", page=1, page_size=20)

    assert len(records) == 1
    record = records[0]
    assert record["tracking_id"] == "attempt-local-101"
    assert record["account_id"] == "backtest:7"
    assert record["order_id"] == "order-101"
    assert record["bridge_task_id"] == "bridge-task-101"
    assert record["receipt_status"] == "accepted"
    assert record["source_name"] == "miniqmt/windows_bridge"
    assert record["broker_state"] == "review_required"
    assert record["identity_status"] == "missing_broker_identity"


def test_bridge_only_terminal_result_remains_review_required():
    from app.services.trade.execution_tracking_evidence import ExecutionTrackingEvidenceService

    service = ExecutionTrackingEvidenceService(
        submission_attempt_store=FakeSubmissionAttemptStore(
            [
                {
                    "order_id": "order-202",
                    "local_submission_id": "local-202",
                    "broker_channel": "miniqmt",
                    "account_scope": "backtest:7",
                    "submission_status": "bridge_task_accepted",
                    "transport_status": "accepted",
                    "bridge_task_id": "bridge-task-202",
                    "bridge_result_status": "success",
                    "external_order_id": None,
                    "broker_event_type": None,
                    "source_name": "miniqmt/windows_bridge",
                    "updated_at": "2026-05-09T09:31:00+00:00",
                }
            ]
        )
    )

    record = service.load_records(account_id="backtest:7", bridge_task_id="bridge-task-202")[0]
    timeline = service.build_timeline(record)

    assert record["broker_state"] == "review_required"
    assert record["identity_status"] == "missing_broker_identity"
    assert [event["event_type"] for event in timeline] == [
        "external_trigger_request",
        "bridge_submission_receipt",
        "bridge_task_terminal_result",
    ]


def test_broker_identity_and_lifecycle_event_can_mark_acknowledged():
    from app.services.trade.execution_tracking_evidence import ExecutionTrackingEvidenceService

    service = ExecutionTrackingEvidenceService(
        submission_attempt_store=FakeSubmissionAttemptStore(
            [
                {
                    "order_id": "order-303",
                    "local_submission_id": "local-303",
                    "broker_channel": "miniqmt",
                    "account_scope": "backtest:7",
                    "submission_status": "broker_acknowledged",
                    "transport_status": "accepted",
                    "bridge_task_id": "bridge-task-303",
                    "external_order_id": "broker-order-303",
                    "broker_event_type": "order_acknowledged",
                    "source_name": "miniqmt/windows_bridge",
                    "updated_at": "2026-05-09T09:32:00+00:00",
                }
            ]
        )
    )

    record = service.load_records(account_id="backtest:7", order_id="order-303")[0]
    timeline = service.build_timeline(record)

    assert record["broker_state"] == "broker_acknowledged"
    assert record["identity_status"] == "matched_broker_identity"
    assert [event["event_type"] for event in timeline] == [
        "external_trigger_request",
        "bridge_submission_receipt",
        "broker_lifecycle_identity",
    ]


def test_live_bridge_review_incident_is_added_to_timeline_without_acknowledgement():
    from app.services.trade.execution_tracking_evidence import ExecutionTrackingEvidenceService

    service = ExecutionTrackingEvidenceService(
        submission_attempt_store=FakeSubmissionAttemptStore(
            [
                {
                    "order_id": "order-404",
                    "local_submission_id": "local-404",
                    "broker_channel": "miniqmt",
                    "account_scope": "backtest:7",
                    "submission_status": "bridge_task_accepted",
                    "transport_status": "accepted",
                    "bridge_task_id": "bridge-task-404",
                    "source_name": "miniqmt/windows_bridge",
                    "updated_at": "2026-05-09T09:33:00+00:00",
                }
            ]
        ),
        divergence_store=FakeDivergenceStore(
            [
                {
                    "divergence_category": "live_bridge_timeout",
                    "review_status": "review_required",
                    "order_id": "order-404",
                    "local_submission_id": "local-404",
                    "bridge_task_id": "bridge-task-404",
                    "reason_code": "bridge_result_timeout",
                    "reason_detail": "miniQMT live bridge result did not reach a terminal state",
                    "persisted_at": "2026-05-09T09:34:00+00:00",
                }
            ]
        ),
    )

    record = service.load_records(account_id="backtest:7", order_id="order-404")[0]
    timeline = service.build_timeline(record)

    assert record["broker_state"] == "review_required"
    assert timeline[-1]["event_type"] == "live_bridge_review_incident"
    assert timeline[-1]["evidence"]["divergence_category"] == "live_bridge_timeout"
