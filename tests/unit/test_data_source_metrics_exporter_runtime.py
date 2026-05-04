import socket
import threading
import time

from prometheus_client import generate_latest

from src.monitoring.data_source_metrics import DataSourceMetricsExporter, start_metrics_server


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_start_metrics_server_keeps_process_alive_and_exposes_metrics():
    port = _find_free_port()
    server_thread = threading.Thread(target=start_metrics_server, kwargs={"port": port}, daemon=True)
    server_thread.start()

    deadline = time.time() + 5
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except OSError as exc:
            last_error = exc
            time.sleep(0.1)
    else:
        raise AssertionError(f"metrics server did not bind port {port}: {last_error}")

    assert server_thread.is_alive()


def test_metrics_exporter_normalizes_nan_info_metadata_before_exposition():
    exporter = DataSourceMetricsExporter.get_instance()
    endpoint_name = "test.nan.description"

    exporter.init_source_metrics(
        endpoint_name=endpoint_name,
        source_name="test_source",
        data_category="TEST_DATA",
        description=float("nan"),
        priority=1,
        classification_level=2,
    )

    payload = generate_latest().decode("utf-8")

    assert 'endpoint_name="test.nan.description"' in payload
