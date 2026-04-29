from __future__ import annotations

import os
from pathlib import Path


DEFAULT_TRADING_RUNTIME_DIR = Path("var/log/trading")
DEFAULT_TRADING_DECISION_AUDIT_JSONL_PATH = DEFAULT_TRADING_RUNTIME_DIR / "trading-decision-audit.jsonl"
DEFAULT_TRADING_DECISION_AUDIT_SQLITE_PATH = DEFAULT_TRADING_RUNTIME_DIR / "trading-decision-audit.sqlite3"
DEFAULT_TRADING_CASH_RESERVATION_SQLITE_PATH = DEFAULT_TRADING_RUNTIME_DIR / "trading-cash-reservations.sqlite3"
DEFAULT_TRADING_BROKER_ORDER_CORRELATION_SQLITE_PATH = DEFAULT_TRADING_RUNTIME_DIR / "trading-broker-order-correlation.sqlite3"
DEFAULT_TRADING_BROKER_SUBMISSION_ATTEMPT_SQLITE_PATH = (
    DEFAULT_TRADING_RUNTIME_DIR / "trading-broker-submission-attempt.sqlite3"
)
DEFAULT_TRADING_BROKER_LIFECYCLE_EVENT_SQLITE_PATH = DEFAULT_TRADING_RUNTIME_DIR / "trading-broker-lifecycle-event.sqlite3"
DEFAULT_TRADING_BROKER_DIVERGENCE_SQLITE_PATH = DEFAULT_TRADING_RUNTIME_DIR / "trading-broker-divergence.sqlite3"
DEFAULT_TRADING_ORDER_STATE_SQLITE_PATH = DEFAULT_TRADING_RUNTIME_DIR / "trading-order-state.sqlite3"
DEFAULT_TRADING_STALE_CASH_RESERVATION_MAX_AGE_SECONDS = 86400
DEFAULT_TRADING_QMT_BRIDGE_CONTRACT_VERSION = "1"
DEFAULT_TRADING_MINIQMT_LIVE_BRIDGE_TIMEOUT_SECONDS = 15.0
DEFAULT_TRADING_MINIQMT_LIVE_BRIDGE_POLL_INTERVAL_SECONDS = 1.0


def get_trading_runtime_dir(default: str | Path = DEFAULT_TRADING_RUNTIME_DIR) -> Path:
    configured = os.getenv("TRADING_RUNTIME_DIR")
    return Path(configured) if configured else Path(default)


def get_trading_decision_audit_jsonl_path(default: str | Path = DEFAULT_TRADING_DECISION_AUDIT_JSONL_PATH) -> Path:
    configured = os.getenv("TRADING_DECISION_AUDIT_JSONL_PATH")
    if configured:
        return Path(configured)
    return get_trading_runtime_dir() / Path(default).name


def get_trading_decision_audit_sqlite_path(default: str | Path = DEFAULT_TRADING_DECISION_AUDIT_SQLITE_PATH) -> Path:
    configured = os.getenv("TRADING_DECISION_AUDIT_SQLITE_PATH")
    if configured:
        return Path(configured)
    return get_trading_runtime_dir() / Path(default).name


def get_trading_cash_reservation_sqlite_path(
    default: str | Path = DEFAULT_TRADING_CASH_RESERVATION_SQLITE_PATH,
) -> Path:
    configured = os.getenv("TRADING_CASH_RESERVATION_SQLITE_PATH")
    if configured:
        return Path(configured)
    return get_trading_runtime_dir() / Path(default).name


def get_trading_broker_order_correlation_sqlite_path(
    default: str | Path = DEFAULT_TRADING_BROKER_ORDER_CORRELATION_SQLITE_PATH,
) -> Path:
    configured = os.getenv("TRADING_BROKER_ORDER_CORRELATION_SQLITE_PATH")
    if configured:
        return Path(configured)
    return get_trading_runtime_dir() / Path(default).name


def get_trading_broker_submission_attempt_sqlite_path(
    default: str | Path = DEFAULT_TRADING_BROKER_SUBMISSION_ATTEMPT_SQLITE_PATH,
) -> Path:
    configured = os.getenv("TRADING_BROKER_SUBMISSION_ATTEMPT_SQLITE_PATH")
    if configured:
        return Path(configured)
    return get_trading_runtime_dir() / Path(default).name


def get_trading_broker_lifecycle_event_sqlite_path(
    default: str | Path = DEFAULT_TRADING_BROKER_LIFECYCLE_EVENT_SQLITE_PATH,
) -> Path:
    configured = os.getenv("TRADING_BROKER_LIFECYCLE_EVENT_SQLITE_PATH")
    if configured:
        return Path(configured)
    return get_trading_runtime_dir() / Path(default).name


def get_trading_broker_divergence_sqlite_path(
    default: str | Path = DEFAULT_TRADING_BROKER_DIVERGENCE_SQLITE_PATH,
) -> Path:
    configured = os.getenv("TRADING_BROKER_DIVERGENCE_SQLITE_PATH")
    if configured:
        return Path(configured)
    return get_trading_runtime_dir() / Path(default).name


def get_trading_order_state_sqlite_path(
    default: str | Path = DEFAULT_TRADING_ORDER_STATE_SQLITE_PATH,
) -> Path:
    configured = os.getenv("TRADING_ORDER_STATE_SQLITE_PATH")
    if configured:
        return Path(configured)
    return get_trading_runtime_dir() / Path(default).name


def get_trading_stale_cash_reservation_max_age_seconds(
    default: int = DEFAULT_TRADING_STALE_CASH_RESERVATION_MAX_AGE_SECONDS,
) -> int:
    return int(os.getenv("TRADING_STALE_CASH_RESERVATION_MAX_AGE_SECONDS", str(default)))


def get_trading_qmt_bridge_token() -> str | None:
    configured = os.getenv("TRADING_QMT_BRIDGE_TOKEN") or os.getenv("QMT_BRIDGE_TOKEN")
    if configured is None:
        return None
    normalized = configured.strip()
    return normalized or None


def get_trading_qmt_bridge_contract_version(
    default: str = DEFAULT_TRADING_QMT_BRIDGE_CONTRACT_VERSION,
) -> str:
    configured = os.getenv("TRADING_QMT_BRIDGE_CONTRACT_VERSION")
    if configured:
        normalized = configured.strip()
        if normalized:
            return normalized
    return str(default)


def get_trading_miniqmt_live_bridge_timeout_seconds(
    default: float = DEFAULT_TRADING_MINIQMT_LIVE_BRIDGE_TIMEOUT_SECONDS,
) -> float:
    return float(os.getenv("TRADING_MINIQMT_LIVE_BRIDGE_TIMEOUT_SECONDS", str(default)))


def get_trading_miniqmt_live_bridge_poll_interval_seconds(
    default: float = DEFAULT_TRADING_MINIQMT_LIVE_BRIDGE_POLL_INTERVAL_SECONDS,
) -> float:
    return float(os.getenv("TRADING_MINIQMT_LIVE_BRIDGE_POLL_INTERVAL_SECONDS", str(default)))
