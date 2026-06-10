from __future__ import annotations

from src.core.data_source.market_stream_bridge import (
    OPENSTOCK_MARKET_STREAM_MESSAGE_TYPES,
    bridge_openstock_market_message,
)


def test_openstock_market_stream_message_types_are_declared():
    assert OPENSTOCK_MARKET_STREAM_MESSAGE_TYPES == (
        "subscribe",
        "unsubscribe",
        "snapshot",
        "quote.update",
        "heartbeat",
        "error",
    )


def test_snapshot_message_bridges_to_existing_ws_events_market_channel():
    events = bridge_openstock_market_message(
        {
            "type": "snapshot",
            "stream": "market",
            "request_id": "req-stream",
            "quotes": [{"symbol": "000001", "name": "平安银行", "price": 10.5}],
            "source": "akshare",
            "endpoint_name": "akshare.stock_zh_a_spot",
            "quality_flags": [],
        }
    )

    assert events == [
        {
            "type": "market.data.update",
            "channels": ["events:market"],
            "payload": {
                "source": "openstock",
                "request_id": "req-stream",
                "quotes": [{"symbol": "000001", "name": "平安银行", "price": 10.5}],
                "provider": "akshare",
                "endpoint_name": "akshare.stock_zh_a_spot",
                "quality_flags": [],
            },
        }
    ]


def test_quote_update_message_bridges_to_market_and_symbol_channels():
    events = bridge_openstock_market_message(
        {
            "type": "quote.update",
            "stream": "market",
            "request_id": "req-stream",
            "quote": {"symbol": "000001", "name": "平安银行", "price": 10.5},
            "source": "akshare",
            "endpoint_name": "akshare.stock_zh_a_spot",
            "quality_flags": [],
        }
    )

    assert events == [
        {
            "type": "market.price.update",
            "channels": ["events:market", "events:market:000001"],
            "payload": {
                "source": "openstock",
                "request_id": "req-stream",
                "quote": {"symbol": "000001", "name": "平安银行", "price": 10.5},
                "provider": "akshare",
                "endpoint_name": "akshare.stock_zh_a_spot",
                "quality_flags": [],
            },
        }
    ]


def test_heartbeat_and_error_messages_bridge_to_system_channel():
    assert bridge_openstock_market_message(
        {"type": "heartbeat", "stream": "market", "request_id": "req-stream", "ts": "2026-06-10T00:00:00Z"}
    ) == [
        {
            "type": "openstock.heartbeat",
            "channels": ["events:system"],
            "payload": {
                "source": "openstock",
                "request_id": "req-stream",
                "stream": "market",
                "ts": "2026-06-10T00:00:00Z",
            },
        }
    ]

    assert bridge_openstock_market_message(
        {
            "type": "error",
            "stream": "market",
            "request_id": "req-error",
            "code": "unsupported_message_type",
            "message": "Unsupported message type: invalid",
        }
    ) == [
        {
            "type": "openstock.error",
            "channels": ["events:system"],
            "payload": {
                "source": "openstock",
                "request_id": "req-error",
                "stream": "market",
                "code": "unsupported_message_type",
                "message": "Unsupported message type: invalid",
            },
        }
    ]


def test_control_messages_do_not_broadcast_to_ws_events_consumers():
    assert bridge_openstock_market_message({"type": "subscribe", "request_id": "req-stream"}) == []
    assert bridge_openstock_market_message({"type": "unsubscribe", "request_id": "req-stream"}) == []
