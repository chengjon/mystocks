from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from scripts.runtime.trading_cash_reservations import build_parser, main
from src.application.trading.cash_reservation import SqlitePortfolioCashReservationStore
from src.application.trading.decision_audit import SqliteTradingDecisionAuditSink
from src.application.trading.order_state_evidence import SqliteTradingOrderStateStore


def test_cli_builds_expected_list_arguments() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--sqlite-path",
            "reservations.sqlite3",
            "--output",
            "json",
            "list",
            "--scope",
            "stale",
            "--portfolio-id",
            "portfolio-1",
            "--max-age-seconds",
            "3600",
        ]
    )

    assert args.sqlite_path == "reservations.sqlite3"
    assert args.output == "json"
    assert args.command == "list"
    assert args.scope == "stale"
    assert args.portfolio_id == "portfolio-1"
    assert args.max_age_seconds == 3600


def test_cli_lists_stale_reservations_as_json(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "reservations.sqlite3"
    store = SqlitePortfolioCashReservationStore(sqlite_path)
    store.upsert(
        "portfolio-1",
        "order-stale-1",
        1200.0,
        updated_at=(datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
    )
    store.upsert(
        "portfolio-1",
        "order-fresh-1",
        800.0,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    assert main(
        [
            "--sqlite-path",
            str(sqlite_path),
            "--output",
            "json",
            "list",
            "--scope",
            "stale",
            "--max-age-seconds",
            "86400",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] == 1
    assert payload["reservations"][0]["order_id"] == "order-stale-1"
    assert payload["reservations"][0]["portfolio_id"] == "portfolio-1"
    assert payload["reservations"][0]["reserved_notional"] == 1200.0


def test_cli_auto_releases_stale_reservation_without_second_approver(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "reservations.sqlite3"
    audit_jsonl_path = tmp_path / "trading-audit.jsonl"
    audit_sqlite_path = tmp_path / "trading-audit.sqlite3"
    store = SqlitePortfolioCashReservationStore(sqlite_path)
    store.upsert(
        "portfolio-1",
        "order-1",
        900.0,
        updated_at=(datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
    )

    assert main(
        [
            "--sqlite-path",
            str(sqlite_path),
            "--output",
            "json",
            "release",
            "--order-id",
            "order-1",
            "--actor-id",
            "ops-user",
            "--reason",
            "stale_reservation_auto_cleanup",
            "--stale-age-seconds",
            "86400",
            "--audit-jsonl-path",
            str(audit_jsonl_path),
            "--audit-sqlite-path",
            str(audit_sqlite_path),
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["released"] is True
    assert payload["order_id"] == "order-1"
    assert payload["actor_id"] == "ops-user"
    assert payload["approval_mode"] == "auto_release"
    assert payload["review_required"] is False
    assert payload["approved_by"] is None
    assert store.get_order_reservation("order-1") is None

    audit_records = SqliteTradingDecisionAuditSink(audit_sqlite_path).fetch_recent(limit=10)
    assert audit_records[0]["decision_outcome"] == "manual_reservation_release"
    assert audit_records[0]["decision_reason"] == "stale_reservation_auto_cleanup"
    assert audit_records[0]["actor_id"] == "ops-user"
    assert audit_records[0]["approval_mode"] == "auto_release"
    assert audit_records[0]["review_required"] is False
    assert audit_records[0]["approved_by"] is None
    assert audit_records[0]["order_id"] == "order-1"


def test_cli_returns_error_when_fresh_release_requires_review(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "reservations.sqlite3"
    audit_jsonl_path = tmp_path / "trading-audit.jsonl"
    audit_sqlite_path = tmp_path / "trading-audit.sqlite3"
    store = SqlitePortfolioCashReservationStore(sqlite_path)
    store.upsert("portfolio-1", "order-fresh-1", 900.0)

    assert main(
        [
            "--sqlite-path",
            str(sqlite_path),
            "--output",
            "json",
            "release",
            "--order-id",
            "order-fresh-1",
            "--actor-id",
            "ops-user",
            "--stale-age-seconds",
            "86400",
            "--audit-jsonl-path",
            str(audit_jsonl_path),
            "--audit-sqlite-path",
            str(audit_sqlite_path),
        ]
    ) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["released"] is False
    assert payload["message"] == "manual_review_required_for_non_stale_reservation"
    assert payload["actor_id"] == "ops-user"
    assert payload["approval_mode"] == "review_required"
    assert payload["review_required"] is True
    assert store.get_order_reservation("order-fresh-1") is not None

    audit_records = SqliteTradingDecisionAuditSink(audit_sqlite_path).fetch_recent(limit=10)
    assert audit_records[0]["decision_outcome"] == "manual_reservation_release_review_required"
    assert audit_records[0]["decision_reason"] == "manual_review_required_for_non_stale_reservation"
    assert audit_records[0]["actor_id"] == "ops-user"
    assert audit_records[0]["approval_mode"] == "review_required"
    assert audit_records[0]["review_required"] is True
    assert audit_records[0]["order_id"] == "order-fresh-1"


def test_cli_allows_single_operator_override_for_fresh_reservation(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "reservations.sqlite3"
    audit_jsonl_path = tmp_path / "trading-audit.jsonl"
    audit_sqlite_path = tmp_path / "trading-audit.sqlite3"
    store = SqlitePortfolioCashReservationStore(sqlite_path)
    store.upsert("portfolio-1", "order-1", 900.0)

    assert main(
        [
            "--sqlite-path",
            str(sqlite_path),
            "--output",
            "json",
            "release",
            "--order-id",
            "order-1",
            "--actor-id",
            "ops-user",
            "--allow-single-operator",
            "--reason",
            "single_operator_override_after_local_review",
            "--audit-jsonl-path",
            str(audit_jsonl_path),
            "--audit-sqlite-path",
            str(audit_sqlite_path),
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["released"] is True
    assert payload["approval_mode"] == "single_operator_with_audit"
    assert payload["review_required"] is True
    assert payload["actor_id"] == "ops-user"
    assert payload["approved_by"] is None
    assert store.get_order_reservation("order-1") is None

    audit_records = SqliteTradingDecisionAuditSink(audit_sqlite_path).fetch_recent(limit=10)
    assert audit_records[0]["decision_outcome"] == "manual_reservation_release"
    assert audit_records[0]["decision_reason"] == "single_operator_override_after_local_review"
    assert audit_records[0]["actor_id"] == "ops-user"
    assert audit_records[0]["approval_mode"] == "single_operator_with_audit"
    assert audit_records[0]["review_required"] is True
    assert audit_records[0]["approved_by"] is None


def test_cli_can_release_fresh_reservation_with_dual_control(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "reservations.sqlite3"
    audit_jsonl_path = tmp_path / "trading-audit.jsonl"
    audit_sqlite_path = tmp_path / "trading-audit.sqlite3"
    store = SqlitePortfolioCashReservationStore(sqlite_path)
    store.upsert("portfolio-1", "order-1", 900.0)

    assert main(
        [
            "--sqlite-path",
            str(sqlite_path),
            "--output",
            "json",
            "release",
            "--order-id",
            "order-1",
            "--actor-id",
            "ops-user",
            "--approved-by",
            "risk-manager",
            "--reason",
            "manual_clear_after_review",
            "--approval-note",
            "reviewed_against_local_ledger",
            "--audit-jsonl-path",
            str(audit_jsonl_path),
            "--audit-sqlite-path",
            str(audit_sqlite_path),
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["released"] is True
    assert payload["order_id"] == "order-1"
    assert payload["actor_id"] == "ops-user"
    assert payload["approval_mode"] == "dual_control"
    assert payload["review_required"] is True
    assert payload["approved_by"] == "risk-manager"
    assert store.get_order_reservation("order-1") is None

    audit_records = SqliteTradingDecisionAuditSink(audit_sqlite_path).fetch_recent(limit=10)
    assert audit_records[0]["decision_outcome"] == "manual_reservation_release"
    assert audit_records[0]["decision_reason"] == "manual_clear_after_review"
    assert audit_records[0]["actor_id"] == "ops-user"
    assert audit_records[0]["approval_mode"] == "dual_control"
    assert audit_records[0]["review_required"] is True
    assert audit_records[0]["approved_by"] == "risk-manager"
    assert audit_records[0]["approval_note"] == "reviewed_against_local_ledger"
    assert audit_records[0]["order_id"] == "order-1"


def test_cli_auto_releases_fresh_reservation_when_order_state_is_terminal(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "reservations.sqlite3"
    order_state_sqlite_path = tmp_path / "trading-order-state.sqlite3"
    audit_jsonl_path = tmp_path / "trading-audit.jsonl"
    audit_sqlite_path = tmp_path / "trading-audit.sqlite3"
    store = SqlitePortfolioCashReservationStore(sqlite_path)
    order_state_store = SqliteTradingOrderStateStore(order_state_sqlite_path)
    store.upsert("portfolio-1", "order-1", 900.0)
    order_state_store.upsert("portfolio-1", "order-1", "000001", "FILLED")

    assert main(
        [
            "--sqlite-path",
            str(sqlite_path),
            "--output",
            "json",
            "release",
            "--order-id",
            "order-1",
            "--actor-id",
            "ops-user",
            "--order-state-sqlite-path",
            str(order_state_sqlite_path),
            "--audit-jsonl-path",
            str(audit_jsonl_path),
            "--audit-sqlite-path",
            str(audit_sqlite_path),
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["released"] is True
    assert payload["approval_mode"] == "terminal_order_state_auto_release"
    assert payload["review_required"] is False
    assert store.get_order_reservation("order-1") is None

    audit_records = SqliteTradingDecisionAuditSink(audit_sqlite_path).fetch_recent(limit=10)
    assert audit_records[0]["decision_outcome"] == "manual_reservation_release"
    assert audit_records[0]["approval_mode"] == "terminal_order_state_auto_release"
    assert audit_records[0]["review_required"] is False
    assert audit_records[0]["order_state_status"] == "FILLED"


def test_cli_requires_review_when_order_state_is_active(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "reservations.sqlite3"
    order_state_sqlite_path = tmp_path / "trading-order-state.sqlite3"
    audit_jsonl_path = tmp_path / "trading-audit.jsonl"
    audit_sqlite_path = tmp_path / "trading-audit.sqlite3"
    store = SqlitePortfolioCashReservationStore(sqlite_path)
    order_state_store = SqliteTradingOrderStateStore(order_state_sqlite_path)
    store.upsert("portfolio-1", "order-1", 900.0)
    order_state_store.upsert("portfolio-1", "order-1", "000001", "SUBMITTED")

    assert main(
        [
            "--sqlite-path",
            str(sqlite_path),
            "--output",
            "json",
            "release",
            "--order-id",
            "order-1",
            "--actor-id",
            "ops-user",
            "--order-state-sqlite-path",
            str(order_state_sqlite_path),
            "--audit-jsonl-path",
            str(audit_jsonl_path),
            "--audit-sqlite-path",
            str(audit_sqlite_path),
        ]
    ) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["released"] is False
    assert payload["message"] == "active_order_state_requires_review"
    assert payload["approval_mode"] == "review_required"
    assert payload["review_required"] is True
    assert store.get_order_reservation("order-1") is not None

    audit_records = SqliteTradingDecisionAuditSink(audit_sqlite_path).fetch_recent(limit=10)
    assert audit_records[0]["decision_outcome"] == "manual_reservation_release_review_required"
    assert audit_records[0]["decision_reason"] == "active_order_state_requires_review"
    assert audit_records[0]["order_state_status"] == "SUBMITTED"


def test_cli_returns_error_when_release_target_does_not_exist(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "reservations.sqlite3"
    audit_jsonl_path = tmp_path / "trading-audit.jsonl"
    audit_sqlite_path = tmp_path / "trading-audit.sqlite3"

    assert main(
        [
            "--sqlite-path",
            str(sqlite_path),
            "--output",
            "json",
            "release",
            "--order-id",
            "missing-order",
            "--actor-id",
            "ops-user",
            "--audit-jsonl-path",
            str(audit_jsonl_path),
            "--audit-sqlite-path",
            str(audit_sqlite_path),
        ]
    ) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["released"] is False
    assert payload["message"] == "reservation_not_found"
    assert payload["actor_id"] == "ops-user"
    assert payload["approved_by"] is None

    audit_records = SqliteTradingDecisionAuditSink(audit_sqlite_path).fetch_recent(limit=10)
    assert audit_records[0]["decision_outcome"] == "manual_reservation_release_not_found"
    assert audit_records[0]["decision_reason"] == "reservation_not_found"
    assert audit_records[0]["actor_id"] == "ops-user"
    assert audit_records[0]["approved_by"] is None
    assert audit_records[0]["order_id"] == "missing-order"


def test_cli_rejects_release_when_actor_and_approver_are_the_same(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "reservations.sqlite3"
    audit_jsonl_path = tmp_path / "trading-audit.jsonl"
    audit_sqlite_path = tmp_path / "trading-audit.sqlite3"
    store = SqlitePortfolioCashReservationStore(sqlite_path)
    store.upsert("portfolio-1", "order-1", 900.0)

    assert main(
        [
            "--sqlite-path",
            str(sqlite_path),
            "--output",
            "json",
            "release",
            "--order-id",
            "order-1",
            "--actor-id",
            "ops-user",
            "--approved-by",
            "ops-user",
            "--audit-jsonl-path",
            str(audit_jsonl_path),
            "--audit-sqlite-path",
            str(audit_sqlite_path),
        ]
    ) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["released"] is False
    assert payload["message"] == "approval_requires_distinct_reviewer"
    assert payload["actor_id"] == "ops-user"
    assert payload["approved_by"] == "ops-user"
    assert store.get_order_reservation("order-1") is not None

    audit_records = SqliteTradingDecisionAuditSink(audit_sqlite_path).fetch_recent(limit=10)
    assert audit_records[0]["decision_outcome"] == "manual_reservation_release_approval_rejected"
    assert audit_records[0]["decision_reason"] == "approval_requires_distinct_reviewer"
    assert audit_records[0]["actor_id"] == "ops-user"
    assert audit_records[0]["approved_by"] == "ops-user"
