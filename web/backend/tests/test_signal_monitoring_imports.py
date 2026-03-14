from app.api.signal_monitoring import ActiveSignalItem
from app.api.signal_monitoring.signal_history_response_schemas import ActiveSignalItem as SchemaActiveSignalItem


def test_signal_monitoring_exports_active_signal_item():
    assert ActiveSignalItem is SchemaActiveSignalItem
