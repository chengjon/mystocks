from __future__ import annotations

from datetime import datetime
import logging
from unittest.mock import MagicMock, patch

from src.monitoring.monitoring_database import MonitoringDatabase


def test_log_operation_uses_connection_context_manager_without_fallback(caplog) -> None:
    mock_conn_manager = MagicMock()
    mock_pool = MagicMock()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn_manager.get_postgresql_connection.return_value = mock_pool
    mock_pool.getconn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    with patch("src.monitoring.monitoring_database_methods.part1.DatabaseConnectionManager", return_value=mock_conn_manager):
        monitoring_db = MonitoringDatabase()

    with caplog.at_level(logging.WARNING):
        result = monitoring_db.log_operation(
            operation_type="RISK_CALCULATION",
            classification="DERIVED_DATA",
            target_database="PostgreSQL",
            table_name="risk_metrics",
            record_count=1,
            operation_status="SUCCESS",
            execution_time_ms=5,
        )

    assert result is True
    mock_conn.commit.assert_called_once()
    mock_pool.putconn.assert_called_once_with(mock_conn)
    assert not any("记录操作日志失败" in record.message for record in caplog.records)


def test_log_operation_recovers_when_operation_logs_month_partition_is_missing(caplog) -> None:
    mock_conn_manager = MagicMock()
    mock_pool = MagicMock()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    partition_error = Exception('no partition of relation "operation_logs" found for row')

    mock_conn_manager.get_postgresql_connection.return_value = mock_pool
    mock_pool.getconn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = [partition_error, None, None]

    with patch("src.monitoring.monitoring_database_methods.part1.DatabaseConnectionManager", return_value=mock_conn_manager):
        monitoring_db = MonitoringDatabase()

    with caplog.at_level(logging.WARNING):
        result = monitoring_db.log_operation(
            operation_type="RISK_CALCULATION",
            classification="DERIVED_DATA",
            target_database="PostgreSQL",
            table_name="risk_metrics",
            record_count=1,
            operation_status="SUCCESS",
            execution_time_ms=5,
        )

    expected_partition_name = datetime.now().strftime("operation_logs_%Y_%m")

    assert result is True
    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_called_once()
    assert mock_cursor.execute.call_count == 3
    assert "INSERT INTO operation_logs" in mock_cursor.execute.call_args_list[0].args[0]
    assert expected_partition_name in mock_cursor.execute.call_args_list[1].args[0]
    assert "PARTITION OF operation_logs" in mock_cursor.execute.call_args_list[1].args[0]
    assert "INSERT INTO operation_logs" in mock_cursor.execute.call_args_list[2].args[0]
    assert not any("记录操作日志失败" in record.message for record in caplog.records)
