# WebSocket Real-Time Subscription Architecture Analysis

## Current Implementation Summary

### 1. Architecture Overview

The MyStocks backend implements a **dual-layer WebSocket architecture**:

1. **Socket.IO Layer** (`socketio_manager.py`) - Connection management, namespaces, event routing
2. **Application Layer** - Subscription management, room handling, message broadcasting

#### Key Components:

```
main.py (FastAPI + Socket.IO)
├── socketio_manager.py (Socket.IO Server)
│   ├── ConnectionManager (WebSocket connections)
│   ├── MySocketIONamespace (Event handlers)
│   └── MySocketIOManager (Server management)
├── room_manager.py (Room subscription)
├── services/
│   ├── room_management.py (Multi-room management)
│   ├── realtime_streaming_service.py (Market data streams)
│   ├── room_broadcast_service.py (Message broadcasting)
│   ├── room_socketio_adapter.py (Socket.IO + Room bridge)
│   ├── subscription_storage.py (Persistent storage)
│   └── room_permission_service.py (Access control)
└── models/
    └── websocket_message.py (Message format definitions)
```

---

## 2. Current WebSocket Implementation Details

### 2.1 Connection Management (`socketio_manager.py`)

**File Path:** `/opt/claude/mystocks_spec/web/backend/app/core/socketio_manager.py`

#### ConnectionManager Class
- **Purpose:** Track active WebSocket connections and room subscriptions
- **Key Methods:**
  - `add_connection(sid, user_id)` - Register new connection
  - `remove_connection(sid)` - Clean up on disconnect
  - `subscribe_to_room(sid, room)` - Add connection to room
  - `unsubscribe_from_room(sid, room)` - Remove connection from room
  - `get_room_members(room)` - Get all connections in a room

**Data Structures:**
```python
{
  "active_connections": {
    "sid_123": {
      "sid": "sid_123",
      "user_id": "user_001",
      "connected_at": datetime,
      "rooms": {"room_1", "room_2"},  # Can subscribe to multiple rooms
      "message_count": 42,
      "last_activity": datetime
    }
  },
  "user_connections": {
    "user_001": {"sid_123", "sid_456"}  # User can have multiple connections
  },
  "room_members": {
    "room_1": {"sid_123", "sid_124"}  # Room has multiple subscribers
  }
}
```

#### MySocketIONamespace Class
- **Purpose:** Handle Socket.IO events
- **Event Handlers:**
  - `on_connect` - Connection established → Restore buffered messages
  - `on_disconnect` - Connection lost → Cleanup subscriptions
  - `on_subscribe` - Subscribe to room
  - `on_unsubscribe` - Leave room
  - `on_ping` / `on_pong` - Heartbeat mechanism
  - `on_request` - Request-response pattern
  - `on_subscribe_market_stream` - Subscribe to stock symbol stream
  - `on_unsubscribe_market_stream` - Unsubscribe from stream
  - `on_stream_filter_update` - Update field filters for stream

#### MySocketIOManager Class
- **Purpose:** Main Socket.IO server wrapper
- **Key Methods:**
  - `emit_to_room(room, event, data)` - Broadcast to room
  - `emit_to_user(user_id, event, data)` - Broadcast to all user connections
  - `emit_to_sid(sid, event, data)` - Send to specific connection
  - `emit_stream_data(symbol, data)` - Broadcast market data
  - `get_stats()` - Connection statistics

---

### 2.2 Room Management - Two Different Implementations

#### IMPLEMENTATION A: Simple Room Manager (`core/room_manager.py`)
**File Path:** `/opt/claude/mystocks_spec/web/backend/app/core/room_manager.py`

- **Design:** Single room per connection
- **Constraint:** `member_to_room: Dict[str, str]` - Each connection maps to ONE room
- **Use Case:** Stock market data streaming (one symbol at a time)
- **Structure:**
```python
Room {
  name: str,
  room_id: str,
  members: Dict[sid, RoomMember],  # Track members
  metadata: Dict
}

RoomMember {
  sid: str,
  user_id: str,
  joined_at: datetime,
  message_count: int
}
```

#### IMPLEMENTATION B: Advanced Room Manager (`services/room_management.py`)
**File Path:** `/opt/claude/mystocks_spec/web/backend/app/services/room_management.py`

- **Design:** Multi-room support per user
- **Flexibility:** `user_rooms: Dict[str, Set[room_ids]]` - Users can join multiple rooms
- **Features:**
  - Room types: PUBLIC, PRIVATE, PROTECTED
  - Room status: ACTIVE, INACTIVE, ARCHIVED, CLOSED
  - Member roles: ADMIN, MODERATOR, MEMBER
  - Room metadata and capacity limits
- **Data Structure:**
```python
Room {
  id: str,
  name: str,
  type: RoomType,  # PUBLIC | PRIVATE | PROTECTED
  owner_id: str,
  status: RoomStatus,
  max_members: Optional[int],
  password: Optional[str],
  members: Dict[user_id, RoomMember],
  metadata: Dict,
  message_count: int,
  last_activity: datetime
}

RoomMember {
  user_id: str,
  username: str,
  is_admin: bool,
  is_moderator: bool,
  joined_at: datetime,
  metadata: Dict
}
```

---

### 2.3 Real-Time Streaming Service

**File Path:** `/opt/claude/mystocks_spec/web/backend/app/services/realtime_streaming_service.py`

**Purpose:** Manage market data streams by stock symbol

**Data Flow:**
```
TDengine (Market Data)
    ↓
StreamingService.subscribe(sid, symbol)
    ↓
MarketDataStream (per symbol)
    ├─ StreamSubscriber (per connection/user)
    │  └─ fields: Set (filtered fields)
    └─ Data Buffer (FIFO with dedup)
    ↓
socketio_manager.emit_stream_data(symbol)
    ↓
WebSocket client receives "stream_data" event
```

**Key Classes:**
```python
MarketDataStream {
  symbol: str,
  stream_id: str,
  subscribers: Dict[sid, StreamSubscriber],  # Per-symbol subscribers
  status: StreamStatus,
  data_buffer: List[StreamData],  # Recent messages
  seen_message_ids: Set,  # Deduplication
  messages_sent: int,
  messages_dropped: int
}

StreamSubscriber {
  sid: str,
  user_id: str,
  subscribed_at: datetime,
  fields: Set[str],  # Field filter
  last_message_id: str,
  messages_received: int
}

StreamData {
  message_id: str,
  symbol: str,
  timestamp: int,  # Unix ms
  data: Dict,
  version: int  # Dedup version
}
```

**Subscription Methods:**
- `subscribe(sid, symbol, user_id, fields)` - Subscribe to market stream
- `unsubscribe(sid, symbol)` - Unsubscribe from stream
- `update_fields(sid, symbol, fields)` - Filter fields
- `buffer_data(symbol, data)` - Buffer incoming data
- `get_buffered_data(symbol)` - Retrieve buffered data
- `broadcast_data(symbol, data)` - Notify subscribers

---

### 2.4 Message Broadcasting Service

**File Path:** `/opt/claude/mystocks_spec/web/backend/app/services/room_broadcast_service.py`

**Purpose:** Send messages to rooms with fallback to offline queue

**Features:**
- Broadcast to all room members
- Target specific roles (admin, moderator, member)
- Target specific users
- Offline message queue for disconnected users
- Delivery tracking and history

**Broadcast Methods:**
```python
broadcast_to_all(message, room_members)
broadcast_to_role(message, room_members, target_role)
broadcast_to_user(message, target_user_id)
broadcast_to_users(message, target_user_ids)
```

**Message Types:**
```python
class MessageType(Enum):
  TEXT = "text"
  NOTIFICATION = "notification"
  ALERT = "alert"
  SYSTEM = "system"
  DATA = "data"
```

**Offline Queue:**
- Per-user message queue (max 1000 messages)
- Auto-delivered when user reconnects
- FIFO with size-based eviction

---

### 2.5 Message Format Definitions

**File Path:** `/opt/claude/mystocks_spec/web/backend/app/models/websocket_message.py`

**Message Types:**

#### Request Message
```json
{
  "type": "request",
  "request_id": "req_1234567890",
  "action": "get_market_data",
  "payload": { "symbol": "600519", "data_type": "fund_flow" },
  "user_id": "user_001",
  "timestamp": 1699267200000,
  "trace_id": "trace_abc123"
}
```

#### Response Message
```json
{
  "type": "response",
  "request_id": "req_1234567890",
  "success": true,
  "data": { "symbol": "600519", "fund_flow": {...} },
  "timestamp": 1699267201500,
  "server_time": 1699267201500,
  "trace_id": "trace_abc123"
}
```

#### Stream Subscription
```json
{
  "type": "subscribe",
  "request_id": "sub_1234567890",
  "room": "market_600519",
  "user_id": "user_001",
  "timestamp": 1699267200000
}
```

#### Stream Data Broadcast
```json
{
  "event": "stream_data",
  "data": {
    "symbol": "600519",
    "data": { "price": 1850.50, "volume": 1000 },
    "timestamp": 1699267202000
  }
}
```

#### Heartbeat
```json
{
  "type": "ping",
  "timestamp": 1699267200000
}

// Response:
{
  "type": "pong",
  "timestamp": 1699267200500,
  "server_time": 1699267200500
}
```

---

### 2.6 Subscription Storage (Persistence)

**File Path:** `/opt/claude/mystocks_spec/web/backend/app/services/subscription_storage.py`

**Purpose:** Persist user subscriptions and alerts to PostgreSQL

**Database Tables:**
- `subscriptions` - User subscriptions
- `filter_expressions` - Filter logic
- `filter_conditions` - Individual conditions
- `alerts` - Generated alerts

**Features:**
- Subscription versioning
- Complex filter expression storage
- Alert persistence with priority/delivery methods
- User subscription queries
- Statistics and analytics

---

## 3. Multi-Room Subscription Implementation Status

### Current Limitations:

**1. In `socketio_manager.py` - ConnectionManager:**
```python
room_members: Dict[str, Set[str]]  # room_name -> set of sid
# Each sid can be in multiple rooms ✅
```

**2. In `core/room_manager.py` - Single Room per Connection:**
```python
member_to_room: Dict[str, str]  # sid -> room_name (ONE-TO-ONE)
# LIMITATION: Each connection limited to ONE room only ❌
```

**3. In `services/room_management.py` - Multi-Room Support:**
```python
user_rooms: Dict[str, Set[str]]  # user_id -> set of room_ids
# Supports multiple rooms per user ✅
# But operates at user level, not connection level
```

### Where Multi-Room Subscription Should Be Implemented:

#### 1. **Socket.IO Connection Manager Enhancement**
**File:** `web/backend/app/core/socketio_manager.py` (ConnectionManager)

**Current:**
```python
def subscribe_to_room(self, sid: str, room: str) -> bool:
    self.active_connections[sid]["rooms"].add(room)  # Already supports multiple
    if room not in self.room_members:
        self.room_members[room] = set()
    self.room_members[room].add(sid)
    return True
```

**Status:** ✅ **ALREADY SUPPORTS MULTIPLE ROOMS**
- `rooms: set()` in connection object allows multiple subscriptions
- `unsubscribe_from_room()` properly removes individual rooms
- `on_subscribe` and `on_unsubscribe` handlers can be called multiple times

#### 2. **Room Manager Upgrade Needed**
**File:** `web/backend/app/core/room_manager.py` (RoomManager)

**Current Issue:**
```python
member_to_room: Dict[str, str]  # ONE-TO-ONE MAPPING ❌
```

**Solution Needed:**
```python
member_to_room: Dict[str, Set[str]]  # ONE-TO-MANY MAPPING ✅
# Allow tracking which rooms a connection belongs to
```

#### 3. **Advanced Room Manager Already Ready**
**File:** `web/backend/app/services/room_management.py`

**Status:** ✅ **PRODUCTION READY FOR MULTI-ROOM**
- Full multi-room support per user
- User can join multiple rooms: `user_rooms: Dict[str, Set[str]]`
- Room capacity and type management
- Role-based access control

---

## 4. Data Flow for Different Subscription Patterns

### Pattern A: Market Data Stream Subscription
```
Client connects
  ↓
on_subscribe_market_stream(sid, {symbol, fields})
  ↓
streaming_service.subscribe(sid, symbol, user_id, fields)
  ↓
MarketDataStream.add_subscriber(sid, fields)
  ↓
[TDengine provides market data]
  ↓
socketio_manager.emit_stream_data(symbol, data)
  ↓
Broadcasting to all subscribers in "stream_{symbol}" room
  ↓
Client receives stream_data event
```

### Pattern B: Room-Based Messaging
```
Client connects
  ↓
on_subscribe(sid, {room: "room_123"})
  ↓
connection_manager.subscribe_to_room(sid, "room_123")
  ↓
Server broadcasts message
  ↓
socketio_manager.emit_to_room("room_123", event, data)
  ↓
All connections in room_123 receive message
```

### Pattern C: Multi-Room Subscription (PLANNED)
```
Client connects
  ↓
Subscribe to Room A
  ↓
Subscribe to Room B
  ↓
Subscribe to Room C (symbol stream)
  ↓
connection.rooms = {room_a, room_b, stream_C}
  ↓
Receive messages from any of 3 sources
```

---

## 5. Key Data Models Summary

### Connection Tracking
```
ConnectionManager.active_connections = {
  "sid_123": {
    "sid": "sid_123",
    "user_id": "user_001",
    "rooms": {"room_1", "room_2", "stream_600519"},  # Multiple rooms
    "message_count": 42,
    "last_activity": datetime
  }
}
```

### Room Subscription (Simple)
```
Room {
  name: "market_600519",
  members: {
    "sid_123": RoomMember,
    "sid_124": RoomMember
  }
}
```

### Room Subscription (Advanced)
```
Room {
  id: "room_001",
  type: "private",
  owner_id: "user_001",
  members: {
    "user_001": RoomMember(admin=true),
    "user_002": RoomMember(admin=false)
  },
  max_members: 100,
  status: "active"
}
```

### Market Stream
```
MarketDataStream {
  symbol: "600519",
  subscribers: {
    "sid_123": StreamSubscriber(fields={"price", "volume"}),
    "sid_124": StreamSubscriber(fields={"price"})
  },
  data_buffer: [StreamData, StreamData, ...],
  status: "active"
}
```

---

## 6. Message Broadcasting Mechanisms

### 1. Socket.IO Direct Broadcast
```python
# Broadcast to room
await sio.emit("stream_data", data, to="stream_600519")

# Broadcast to specific connection
await sio.emit("response", data, to="sid_123")

# Broadcast to all except sender
await sio.emit("message", data, to="room_1", skip_sid="sid_123")
```

### 2. Application-Level Routing
```python
# Through ConnectionManager
async def emit_to_room(room, event, data):
    sids = connection_manager.get_room_members(room)
    for sid in sids:
        await emit_to_sid(sid, event, data)

# Through streaming service
async def emit_stream_data(symbol, data):
    await sio.emit("stream_data", {...}, to=f"stream_{symbol}")
```

### 3. Fallback to Offline Queue
```python
def _deliver_message(user_id, message):
    for callback in delivery_callbacks:  # Try SocketIO
        if callback(user_id, message):
            return True
    # If offline, queue message
    offline_queue.enqueue(user_id, message)
    return False
```

---

## 7. Reconnection & Recovery

**File:** `web/backend/app/core/reconnection_manager.py`

**Features:**
- Buffer messages during disconnection
- Detect reconnection by SID
- Resend buffered messages on reconnect
- Track reconnection statistics

**Flow:**
```
Connection drops
  ↓
reconnection_manager.mark_disconnected(sid)
  ↓
Incoming messages buffered
  ↓
Client reconnects with same SID
  ↓
on_connect event triggers
  ↓
Get buffered messages
  ↓
Send all buffered messages to client
  ↓
mark_reconnected(sid)
```

---

## 8. Access Control & Permissions

**File:** `web/backend/app/services/room_permission_service.py`

**Features:**
- Role-based access control (RBAC)
- Room-level permissions
- User role enforcement
- Casbin integration for policy management

**Roles:**
```python
RoomRole {
  OWNER: Full control
  ADMIN: Management rights
  MODERATOR: Moderation rights
  MEMBER: Basic access
}

RoomPermission {
  READ: Can read room data
  WRITE: Can send messages
  DELETE: Can delete messages
  MANAGE_MEMBERS: Can add/remove members
  DELETE_ROOM: Can delete room
}
```

---

## 9. Statistics & Monitoring

### Connection Statistics
```python
socketio_manager.get_stats() → {
  "total_connections": 150,
  "total_users": 120,
  "total_rooms": 45,
  "reconnection": {...},
  "streaming": {...}
}
```

### Room Statistics
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

### Streaming Statistics
```python
streaming_service.get_stats() → {
  "active_streams": 25,
  "total_subscribers": 150,
  "total_messages": 50000,
  "total_dropped": 100
}
```

---

## 10. Implementation Readiness Assessment

### ✅ READY FOR PRODUCTION:
1. **Socket.IO Server** - Full implementation with ASGI support
2. **Connection Management** - Complete lifecycle handling
3. **Basic Room Subscription** - Working (single room per connection)
4. **Market Data Streaming** - Full implementation with deduplication
5. **Advanced Room Management** - Full multi-room support
6. **Message Broadcasting** - All patterns implemented
7. **Offline Message Queue** - Complete with auto-delivery
8. **Access Control** - RBAC with Casbin ready
9. **Reconnection Handling** - Full buffering and recovery
10. **Monitoring & Stats** - Comprehensive metrics

### ⚠️ NEEDS ENHANCEMENT:
1. **Multi-Room at Connection Level** - Use advanced RoomManager in services
2. **Connection-to-Multiple-Streams** - Currently works, needs testing
3. **Field Filtering** - Implemented, needs optimization
4. **Error Handling** - Need more specific error codes
5. **Load Testing** - Need stress tests for 1000+ concurrent connections

---

## 11. Key Integration Points

### For Multi-Room Implementation:
1. Replace `core/room_manager.py` with `services/room_management.py` 
2. Update `MySocketIONamespace` event handlers for multi-room awareness
3. Update connection lifecycle tracking for multiple room subscriptions
4. Integrate permission service with room access
5. Add multi-room test suite

### For Real-Time Features:
1. Connect `realtime_streaming_service` to market data sources
2. Implement field filtering strategy
3. Add rate limiting per connection
4. Optimize broadcast performance
5. Add circuit breaker for error scenarios

---

## Summary

The MyStocks WebSocket infrastructure provides:
- **Robust Socket.IO integration** with ASGI support
- **Dual subscription mechanisms**: Stream-based (market data) and Room-based (messaging)
- **Already supports multiple room subscriptions** at the Socket.IO layer
- **Advanced room management** with RBAC, capacity limits, and room types
- **Comprehensive message broadcasting** with offline queue fallback
- **Complete reconnection recovery** with message buffering
- **Production-ready monitoring** and statistics

**Next Steps for Full Multi-Room Support:**
1. Migrate to advanced RoomManager from services layer
2. Add comprehensive test coverage
3. Implement load testing (1000+ concurrent connections)
4. Optimize broadcasting for high throughput
5. Add distributed deployment support (Redis adapter for Socket.IO)

