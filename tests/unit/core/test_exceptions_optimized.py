"""Focused tests for the current custom exception contracts."""

from __future__ import annotations

from src.core.exceptions import (
    ConnectionError,
    DataSourceException,
    DataSourceQueryError,
    DataValidationError,
    DatabaseConnectionError,
    MyStocksException,
)


def test_data_source_exception_uses_default_code_and_inherits_base_contract() -> None:
    exc = DataSourceException("source failed", details={"source": "demo"})

    assert isinstance(exc, MyStocksException)
    assert exc.error_code == "DATA_SOURCE_ERROR"
    assert exc.status_code == 503
    assert exc.details["source"] == "demo"
    assert str(exc) == "source failed"


def test_data_validation_error_keeps_custom_context_and_medium_severity() -> None:
    exc = DataValidationError(
        "price",
        -1,
        ">= 0",
        details={"symbol": "600519"},
    )

    assert exc.error_code == "DATA_VALIDATION_ERROR"
    assert exc.status_code == 400
    payload = exc.to_dict()
    assert payload["error"] == "DataValidationError"
    assert payload["details"] == {"symbol": "600519"}
    assert "field 'price'" in payload["message"]


def test_database_connection_error_accepts_details_without_constructor_conflicts() -> None:
    exc = DatabaseConnectionError("database unavailable", details={"db": "postgresql"})

    assert exc.error_code == "DATABASE_CONNECTION_ERROR"
    assert exc.status_code == 503
    assert exc.details == {"db": "postgresql"}
    assert exc.to_dict()["error_code"] == "DATABASE_CONNECTION_ERROR"


def test_data_source_query_error_formats_message_with_context() -> None:
    exc = DataSourceQueryError(
        "demo-source",
        "symbol=000001",
        details="timeout",
    )

    assert exc.error_code == "DATA_SOURCE_QUERY_ERROR"
    assert exc.status_code == 500
    assert "demo-source" in exc.message
    assert "symbol=000001" in exc.message
    assert "timeout" in exc.message


def test_connection_error_uses_network_override_without_duplicate_kwargs() -> None:
    exc = ConnectionError("api.example.com", port=443, details={"protocol": "https"})

    assert exc.error_code == "CONNECTION_ERROR"
    assert exc.status_code == 503
    assert exc.details == {"protocol": "https"}
    assert "api.example.com:443" in exc.message
