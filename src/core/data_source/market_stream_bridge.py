from __future__ import annotations

from typing import Any, Mapping

OPENSTOCK_MARKET_STREAM_MESSAGE_TYPES = (
    "subscribe",
    "unsubscribe",
    "snapshot",
    "quote.update",
    "heartbeat",
    "error",
)


def bridge_openstock_market_message(
    message: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Map openstock market stream messages to existing MyStocks ws-events events."""
    message_type = str(message.get("type") or "")
    if message_type in {"subscribe", "unsubscribe"}:
        return []
    if message_type == "snapshot":
        return [_bridge_snapshot(message)]
    if message_type == "quote.update":
        return [_bridge_quote_update(message)]
    if message_type == "heartbeat":
        return [_bridge_heartbeat(message)]
    if message_type == "error":
        return [_bridge_error(message)]
    return []


def _bridge_snapshot(message: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": "market.data.update",
        "channels": ["events:market"],
        "payload": {
            "source": "openstock",
            "request_id": _text(message.get("request_id")),
            "quotes": list(message.get("quotes") or []),
            "provider": _text(message.get("source")),
            "endpoint_name": _text(message.get("endpoint_name")),
            "quality_flags": list(message.get("quality_flags") or []),
        },
    }


def _bridge_quote_update(message: Mapping[str, Any]) -> dict[str, Any]:
    quote = dict(message.get("quote") or {})
    symbol = _text(quote.get("symbol"))
    channels = ["events:market"]
    if symbol:
        channels.append(f"events:market:{symbol}")

    return {
        "type": "market.price.update",
        "channels": channels,
        "payload": {
            "source": "openstock",
            "request_id": _text(message.get("request_id")),
            "quote": quote,
            "provider": _text(message.get("source")),
            "endpoint_name": _text(message.get("endpoint_name")),
            "quality_flags": list(message.get("quality_flags") or []),
        },
    }


def _bridge_heartbeat(message: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": "openstock.heartbeat",
        "channels": ["events:system"],
        "payload": {
            "source": "openstock",
            "request_id": _text(message.get("request_id")),
            "stream": _text(message.get("stream")),
            "ts": _text(message.get("ts")),
        },
    }


def _bridge_error(message: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": "openstock.error",
        "channels": ["events:system"],
        "payload": {
            "source": "openstock",
            "request_id": _text(message.get("request_id")),
            "stream": _text(message.get("stream")),
            "code": _text(message.get("code")),
            "message": _text(message.get("message")),
        },
    }


def _text(value: Any) -> str:
    return str(value or "")
