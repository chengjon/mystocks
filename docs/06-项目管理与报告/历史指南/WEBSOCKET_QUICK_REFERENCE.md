# WebSocket Architecture - Quick Reference

## File Locations & Purposes

| File | Purpose | Key Class |
|------|---------|-----------|
| `web/backend/app/main.py` | FastAPI entry + Socket.IO integration | `app`, `socketio_manager` |
| `web/backend/app/core/socketio_manager.py` | WebSocket connection management | `ConnectionManager`, `MySocketIONamespace`, `MySocketIOManager` |
| `web/backend/app/core/room_manager.py` | Simple room management (single room/conn) | `Room`, `RoomManager` |
| `web/backend/app/services/room_management.py` | Advanced room management (multi-room) | `Room`, `RoomManager` |
| `web/backend/app/services/realtime_streaming_service.py` | Market data streams | `MarketDataStream`, `StreamingService` |
| `web/backend/app/services/room_broadcast_service.py` | Message broadcasting | `RoomBroadcaster`, `OfflineMessageQueue` |
| `web/backend/app/services/room_socketio_adapter.py` | Socket.IO + Room bridge | `RoomSocketIOAdapter` |
| `web/backend/app/services/subscription_storage.py` | PostgreSQL persistence | `SubscriptionStorage` |
| `web/backend/app/models/websocket_message.py` | Message format definitions | `WebSocketRequestMessage`, `WebSocketResponseMessage` |
| `web/backend/app/core/reconnection_manager.py` | Reconnection & message buffering | `ReconnectionManager` |
| `web/backend/app/core/connection_lifecycle.py` | Connection state machine | `ConnectionLifecycleManager` |
| `web/backend/app/services/room_permission_service.py` | RBAC & access control | `RoomPermissionManager`, `RoomAccessControl` |

---

## WebSocket Event Handlers

### Connection Lifecycle
```python
on_connect(sid, environ)        # Client connects
on_disconnect(sid)              # Client disconnects
```

### Room Operations
```python
on_subscribe(sid, data)         # Subscribe to room: {"room": "room_id"}
on_unsubscribe(sid, data)       # Unsubscribe from room: {"room": "room_id"}
```

### Market Data Streaming
```python
on_subscribe_market_stream(sid, data)           # Subscribe to symbol: {"symbol": "600519", "fields": [...]}
on_unsubscribe_market_stream(sid, data)         # Unsubscribe: {"symbol": "600519"}
on_stream_filter_update(sid, data)              # Update fields: {"symbol": "600519", "fields": [...]}
```

### Request-Response
```python
on_request(sid, data)           # Generic request: {"action": "...", "payload": {...}}
on_ping(sid, data)              # Heartbeat: {}
```

---

## Broadcasting Patterns

### Pattern 1: Direct Room Broadcast
```python
# Server sends to all in room
await socketio_manager.emit_to_room("room_id", "message", data)

# Client receives event: message
```

### Pattern 2: User Broadcast
```python
# Server sends to all user connections
await socketio_manager.emit_to_user("user_id", "notification", data)

# Client receives event: notification
```

### Pattern 3: Market Data Stream
```python
# Server sends to symbol subscribers
await socketio_manager.emit_stream_data("600519", data)

# Uses Socket.IO room: stream_600519
# Client receives event: stream_data
```

### Pattern 4: Offline Queue + Broadcast
```python
broadcaster.broadcast_to_all(message, room_members)
# If online: send via callback (Socket.IO)
# If offline: queue in offline_queue, deliver on reconnect
```

---

## Connection Architecture

### Per-Connection State
```python
active_connections[sid] = {
    "sid": "sid_123",
    "user_id": "user_001",
    "connected_at": datetime,
    "rooms": {"room_1", "room_2", "stream_600519"},  # MULTIPLE rooms
    "message_count": 42,
    "last_activity": datetime
}
```

### Room-to-Connection Mapping
```python
# Simple (core/room_manager.py)
member_to_room = {"sid_123": "room_1"}  # ONE-TO-ONE ❌

# Advanced (services/room_management.py)
user_rooms = {"user_001": {"room_1", "room_2"}}  # ONE-TO-MANY ✅
```

### Stream Subscription
```python
MarketDataStream[symbol].subscribers = {
    "sid_123": StreamSubscriber(fields={"price", "volume"}),
    "sid_124": StreamSubscriber(fields={"price"}),
}
```

---

## Message Format Examples

### Subscribe to Room
```json
{
  "event": "subscribe",
  "data": {
    "room": "market_update_room"
  }
}
```

### Subscribe to Market Stream
```json
{
  "event": "subscribe_market_stream",
  "data": {
    "symbol": "600519",
    "fields": ["price", "volume", "timestamp"]
  }
}
```

### Receive Stream Data
```json
{
  "event": "stream_data",
  "data": {
    "symbol": "600519",
    "data": {
      "price": 1850.50,
      "volume": 1000,
      "timestamp": 1699267202000
    }
  }
}
```

### Generic Request
```json
{
  "event": "request",
  "data": {
    "request_id": "req_123",
    "action": "get_fund_flow",
    "payload": {
      "symbol": "600519",
      "timeframe": "1d"
    }
  }
}
```

### Heartbeat (Ping/Pong)
```json
// Client sends:
{ "event": "ping", "data": {} }

// Server responds:
{ "event": "pong", "data": {"server_time": 1699267202000} }
```

---

## Key Statistics Available

### Connection Stats
```python
socketio_manager.get_stats() → {
  "total_connections": 150,
  "total_users": 120,
  "total_rooms": 45,
  "namespace": "/",
  "reconnection": {...},
  "streaming": {...}
}
```

### Room Stats
```python
room_manager.get_stats() → {
  "total_rooms": 45,
  "active_rooms": 42,
  "total_members": 320,
  "total_users": 120,
  "rooms_created": 500,
  "rooms_deleted": 455,
  "total_join_events": 3200,
  "total_leave_events": 2880
}
```

### Streaming Stats
```python
streaming_service.get_stats() → {
  "active_streams": 25,
  "total_subscribers": 150,
  "total_messages_sent": 50000,
  "total_messages_dropped": 100
}
```

---

## Multi-Room Status

### Current Implementation

| Component | Multi-Room Support | Status |
|-----------|-------------------|--------|
| Socket.IO ConnectionManager | ✅ Yes | WORKS - `rooms: set()` |
| core/room_manager.py | ❌ No | ONE-TO-ONE mapping only |
| services/room_management.py | ✅ Yes | PRODUCTION READY |
| Streaming Service | ✅ Yes | Per-symbol subscriptions |
| Broadcasting Service | ✅ Yes | All patterns supported |

### What Works Out-of-Box
1. A client can subscribe to multiple rooms via `on_subscribe` (multiple times)
2. A client can subscribe to multiple market streams simultaneously
3. A connection can receive from multiple broadcast sources
4. Offline queue handles messages from all subscriptions

### What Needs Implementation
1. Upgrade core/room_manager.py to support true multi-room
2. Add UI for multi-room subscription management
3. Load test with 1000+ concurrent connections
4. Optimize broadcast performance for many rooms

---

## Integration Checklist

### For Multi-Room Support
- [ ] Replace core/room_manager.py with services version
- [ ] Update MySocketIONamespace event handlers
- [ ] Add room permission checks
- [ ] Test multiple room subscriptions
- [ ] Add load testing suite

### For Market Data Streaming
- [ ] Connect to TDengine data source
- [ ] Implement field filtering optimization
- [ ] Add rate limiting per connection
- [ ] Add circuit breaker for errors
- [ ] Stress test 1000+ subscribers per symbol

### For Production
- [ ] Add Redis adapter for distributed Socket.IO
- [ ] Implement horizontal scaling
- [ ] Add monitoring/alerting
- [ ] Set up log aggregation
- [ ] Add performance profiling

---

## Common Operations

### Server-Side Broadcast
```python
# Broadcast to room
await socketio_manager.emit_to_room("room_id", "event", {"data": "..."})

# Broadcast to user (all connections)
await socketio_manager.emit_to_user("user_id", "event", {"data": "..."})

# Send to specific connection
await socketio_manager.emit_to_sid("sid_123", "event", {"data": "..."})

# Broadcast market data
await socketio_manager.emit_stream_data("600519", {"price": 1850.50})
```

### Client-Side Subscribe
```javascript
// Subscribe to room
socket.emit("subscribe", { room: "room_id" });

// Subscribe to market stream
socket.emit("subscribe_market_stream", {
  symbol: "600519",
  fields: ["price", "volume"]
});

// Listen for broadcasts
socket.on("stream_data", (data) => {
  console.log("Market data:", data);
});

// Heartbeat
socket.emit("ping", {});
socket.on("pong", (data) => {
  console.log("Server time:", data.server_time);
});
```

---

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| `AUTH_REQUIRED` | Not authenticated | Login first |
| `INVALID_SYMBOL` | Stock code invalid | Use 6-digit code |
| `ROOM_NOT_FOUND` | Room doesn't exist | Create room or use valid ID |
| `SUBSCRIPTION_FAILED` | Can't subscribe | Check permissions |
| `PERMISSION_DENIED` | Insufficient access | Request higher role |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait before retry |
| `INTERNAL_ERROR` | Server error | Contact support |

---

## Performance Considerations

### Connection Limits
- Per-connection: Unlimited rooms (Socket.IO layer)
- Per-room: Design for 10K+ members
- Per-symbol: Design for 10K+ subscribers

### Message Throughput
- Market data: 100-1000 msg/sec per symbol
- Broadcasting: Depends on room size
- Offline queue: Max 1000 messages per user

### Memory Usage
- Per connection: ~1-2 KB
- Per room: ~10-50 KB (metadata)
- Per stream: ~100 KB (buffer + subscribers)

### Optimization Tips
1. Use field filtering to reduce data size
2. Batch broadcasts when possible
3. Implement exponential backoff for retries
4. Use compression for large payloads
5. Monitor memory usage per stream

---

## Testing

### Unit Tests
```bash
cd web/backend
pytest tests/test_socketio_manager.py
pytest tests/test_room_management.py
pytest tests/test_realtime_streaming_service.py
pytest tests/test_room_broadcast_service.py
```

### Integration Tests
```bash
pytest tests/test_socketio_streaming_integration.py
pytest tests/test_room_socketio_adapter.py
```

### Stress Testing
```bash
# Load test (1000 concurrent connections)
python scripts/stress_test_connection_pools.py
```

---

## Useful Debug Commands

### Check Connection Status
```python
from app.core.socketio_manager import get_socketio_manager
manager = get_socketio_manager()
print(manager.get_stats())
```

### Check Room Members
```python
from app.services.room_management import get_room_manager
rm = get_room_manager()
room = rm.get_room("room_id")
print(room.get_members())
```

### Check Stream Subscribers
```python
from app.services.realtime_streaming_service import get_streaming_service
ss = get_streaming_service()
stream = ss.get_stream("600519")
print(f"Subscribers: {len(stream.subscribers)}")
```

### Monitor Broadcasting
```python
from app.services.room_broadcast_service import get_broadcaster
bc = get_broadcaster()
print(bc.get_stats())
```

---

## References

- **Main Documentation**: `WEBSOCKET_ARCHITECTURE_ANALYSIS.md`
- **Socket.IO Docs**: https://python-socketio.readthedocs.io/
- **FastAPI + Socket.IO**: https://fastapi.tiangolo.com/ (ASGI)
- **PostgreSQL**: https://www.postgresql.org/docs/

