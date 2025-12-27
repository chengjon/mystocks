"""
房间消息广播服务测试

Tests for Room Message Broadcasting Service

Task 9: 多房间订阅扩展

Author: Claude Code
Date: 2025-11-07
"""

from app.services.room_broadcast_service import (
    MessageType,
    BroadcastTarget,
    RoomMessage,
    BroadcastTask,
    OfflineMessageQueue,
    RoomBroadcaster,
    get_broadcaster,
    reset_broadcaster,
)


class TestMessageType:
    """Test message types"""

    def test_text_message_type(self):
        """Test text message type"""
        assert MessageType.TEXT == "text"

    def test_notification_message_type(self):
        """Test notification message type"""
        assert MessageType.NOTIFICATION == "notification"

    def test_alert_message_type(self):
        """Test alert message type"""
        assert MessageType.ALERT == "alert"

    def test_system_message_type(self):
        """Test system message type"""
        assert MessageType.SYSTEM == "system"

    def test_data_message_type(self):
        """Test data message type"""
        assert MessageType.DATA == "data"


class TestBroadcastTarget:
    """Test broadcast targets"""

    def test_all_target(self):
        """Test all target"""
        assert BroadcastTarget.ALL == "all"

    def test_role_target(self):
        """Test role target"""
        assert BroadcastTarget.ROLE == "role"

    def test_user_target(self):
        """Test user target"""
        assert BroadcastTarget.USER == "user"

    def test_users_target(self):
        """Test users target"""
        assert BroadcastTarget.USERS == "users"


class TestRoomMessage:
    """Test room messages"""

    def test_message_creation(self):
        """Test creating a message"""
        message = RoomMessage(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Hello World",
        )
        assert message.room_id == "room_1"
        assert message.sender_id == "user_1"
        assert message.sender_name == "Alice"
        assert message.content == "Hello World"
        assert message.message_type == MessageType.TEXT

    def test_message_with_metadata(self):
        """Test message with metadata"""
        metadata = {"priority": "high", "tags": ["urgent"]}
        message = RoomMessage(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Important",
            metadata=metadata,
        )
        assert message.metadata == metadata

    def test_message_to_dict(self):
        """Test message serialization"""
        message = RoomMessage(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Test",
            message_type=MessageType.NOTIFICATION,
        )
        msg_dict = message.to_dict()
        assert msg_dict["room_id"] == "room_1"
        assert msg_dict["sender_id"] == "user_1"
        assert msg_dict["sender_name"] == "Alice"
        assert msg_dict["content"] == "Test"
        assert msg_dict["message_type"] == "notification"

    def test_message_has_unique_id(self):
        """Test message gets unique ID"""
        msg1 = RoomMessage(room_id="room_1", sender_id="user_1", sender_name="Alice", content="msg1")
        msg2 = RoomMessage(room_id="room_1", sender_id="user_1", sender_name="Alice", content="msg2")
        assert msg1.id != msg2.id


class TestOfflineMessageQueue:
    """Test offline message queue"""

    def test_queue_initialization(self):
        """Test queue initialization"""
        queue = OfflineMessageQueue()
        assert queue.max_queue_size == 1000

    def test_enqueue_message(self):
        """Test enqueue message"""
        queue = OfflineMessageQueue()
        message = RoomMessage(room_id="room_1", sender_id="user_1", sender_name="Alice", content="msg")
        result = queue.enqueue("user_2", message)
        assert result is True
        assert queue.get_queue_size("user_2") == 1

    def test_dequeue_messages(self):
        """Test dequeue messages"""
        queue = OfflineMessageQueue()
        msg1 = RoomMessage(room_id="room_1", sender_id="user_1", sender_name="Alice", content="msg1")
        msg2 = RoomMessage(room_id="room_1", sender_id="user_1", sender_name="Alice", content="msg2")
        queue.enqueue("user_2", msg1)
        queue.enqueue("user_2", msg2)

        messages = queue.dequeue("user_2", 1)
        assert len(messages) == 1
        assert messages[0].id == msg1.id
        assert queue.get_queue_size("user_2") == 1

    def test_dequeue_multiple_messages(self):
        """Test dequeue multiple messages"""
        queue = OfflineMessageQueue()
        for i in range(5):
            msg = RoomMessage(
                room_id="room_1",
                sender_id="user_1",
                sender_name="Alice",
                content=f"msg{i}",
            )
            queue.enqueue("user_2", msg)

        messages = queue.dequeue("user_2", 3)
        assert len(messages) == 3
        assert queue.get_queue_size("user_2") == 2

    def test_queue_size_limit(self):
        """Test queue size limit"""
        queue = OfflineMessageQueue(max_queue_size=5)
        for i in range(10):
            msg = RoomMessage(
                room_id="room_1",
                sender_id="user_1",
                sender_name="Alice",
                content=f"msg{i}",
            )
            queue.enqueue("user_2", msg)

        assert queue.get_queue_size("user_2") == 5

    def test_clear_queue(self):
        """Test clear queue"""
        queue = OfflineMessageQueue()
        msg = RoomMessage(room_id="room_1", sender_id="user_1", sender_name="Alice", content="msg")
        queue.enqueue("user_2", msg)
        assert queue.get_queue_size("user_2") == 1

        result = queue.clear_queue("user_2")
        assert result is True
        assert queue.get_queue_size("user_2") == 0

    def test_clear_nonexistent_queue(self):
        """Test clear non-existent queue"""
        queue = OfflineMessageQueue()
        result = queue.clear_queue("user_nonexistent")
        assert result is False

    def test_dequeue_empty_queue(self):
        """Test dequeue from empty queue"""
        queue = OfflineMessageQueue()
        messages = queue.dequeue("user_nonexistent")
        assert messages == []

    def test_queue_stats(self):
        """Test queue statistics"""
        queue = OfflineMessageQueue()
        msg = RoomMessage(room_id="room_1", sender_id="user_1", sender_name="Alice", content="msg")
        queue.enqueue("user_1", msg)
        queue.enqueue("user_2", msg)

        stats = queue.get_stats()
        assert stats["users_with_offline_messages"] == 2
        assert stats["total_offline_messages"] == 2


class TestBroadcasterInitialization:
    """Test broadcaster initialization"""

    def test_broadcaster_creation(self):
        """Test creating broadcaster"""
        broadcaster = RoomBroadcaster()
        assert broadcaster is not None
        assert len(broadcaster.delivery_callbacks) == 0

    def test_register_delivery_callback(self):
        """Test registering delivery callback"""
        broadcaster = RoomBroadcaster()

        def callback(user_id: str, message: RoomMessage) -> bool:
            return True

        broadcaster.register_delivery_callback(callback)
        assert len(broadcaster.delivery_callbacks) == 1


class TestMessageSending:
    """Test message sending"""

    def test_send_text_message(self):
        """Test sending text message"""
        broadcaster = RoomBroadcaster()
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Hello",
        )
        assert message.room_id == "room_1"
        assert message.content == "Hello"
        assert message.message_type == MessageType.TEXT
        assert broadcaster.total_messages_sent == 1

    def test_send_notification_message(self):
        """Test sending notification"""
        broadcaster = RoomBroadcaster()
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Alert",
            message_type=MessageType.NOTIFICATION,
        )
        assert message.message_type == MessageType.NOTIFICATION

    def test_send_message_with_metadata(self):
        """Test sending message with metadata"""
        broadcaster = RoomBroadcaster()
        metadata = {"priority": "high"}
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Urgent",
            metadata=metadata,
        )
        assert message.metadata == metadata


class TestBroadcastToAll:
    """Test broadcast to all members"""

    def test_broadcast_to_all_with_callback(self):
        """Test broadcast to all with delivery callback"""
        broadcaster = RoomBroadcaster()
        delivered = []

        def callback(user_id: str, message: RoomMessage) -> bool:
            delivered.append(user_id)
            return True

        broadcaster.register_delivery_callback(callback)
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Hello all",
        )

        room_members = ["user_2", "user_3", "user_4"]
        result = broadcaster.broadcast_to_all(message, room_members)

        assert result is True
        assert len(delivered) == 3
        assert broadcaster.total_messages_delivered == 3

    def test_broadcast_to_all_partial_failure(self):
        """Test broadcast with partial delivery failure"""
        broadcaster = RoomBroadcaster()
        delivery_attempts = 0

        def callback(user_id: str, message: RoomMessage) -> bool:
            nonlocal delivery_attempts
            delivery_attempts += 1
            return user_id != "user_3"  # Fail for user_3

        broadcaster.register_delivery_callback(callback)
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Hello",
        )

        room_members = ["user_2", "user_3", "user_4"]
        result = broadcaster.broadcast_to_all(message, room_members)

        assert result is False
        assert broadcaster.total_messages_delivered == 2
        assert broadcaster.total_delivery_failures == 1


class TestBroadcastToRole:
    """Test broadcast to role"""

    def test_broadcast_to_role(self):
        """Test broadcast to role"""
        broadcaster = RoomBroadcaster()
        delivered = []

        def callback(user_id: str, message: RoomMessage) -> bool:
            delivered.append(user_id)
            return True

        broadcaster.register_delivery_callback(callback)
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Admin notice",
        )

        room_members = {
            "user_1": "owner",
            "user_2": "admin",
            "user_3": "member",
            "user_4": "admin",
        }
        result = broadcaster.broadcast_to_role(message, room_members, "admin")

        assert result is True
        assert len(delivered) == 2
        assert "user_2" in delivered
        assert "user_4" in delivered


class TestBroadcastToUser:
    """Test broadcast to single user"""

    def test_broadcast_to_user(self):
        """Test broadcast to single user"""
        broadcaster = RoomBroadcaster()
        delivered = []

        def callback(user_id: str, message: RoomMessage) -> bool:
            delivered.append(user_id)
            return True

        broadcaster.register_delivery_callback(callback)
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Personal msg",
        )

        result = broadcaster.broadcast_to_user(message, "user_2")

        assert result is True
        assert len(delivered) == 1
        assert delivered[0] == "user_2"


class TestBroadcastToUsers:
    """Test broadcast to users list"""

    def test_broadcast_to_users(self):
        """Test broadcast to users list"""
        broadcaster = RoomBroadcaster()
        delivered = []

        def callback(user_id: str, message: RoomMessage) -> bool:
            delivered.append(user_id)
            return True

        broadcaster.register_delivery_callback(callback)
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Team msg",
        )

        target_users = ["user_2", "user_3", "user_4"]
        result = broadcaster.broadcast_to_users(message, target_users)

        assert result is True
        assert len(delivered) == 3


class TestOfflineMessaging:
    """Test offline message handling"""

    def test_offline_message_storage(self):
        """Test messages go to offline queue on failure"""
        broadcaster = RoomBroadcaster()

        def callback(user_id: str, message: RoomMessage) -> bool:
            return False  # Always fail

        broadcaster.register_delivery_callback(callback)
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Offline msg",
        )

        broadcaster.broadcast_to_user(message, "user_2")

        # Check offline queue
        offline_msgs = broadcaster.get_offline_messages("user_2")
        assert len(offline_msgs) == 1
        assert offline_msgs[0].content == "Offline msg"

    def test_get_offline_messages(self):
        """Test getting offline messages"""
        broadcaster = RoomBroadcaster()

        def callback(user_id: str, message: RoomMessage) -> bool:
            return False

        broadcaster.register_delivery_callback(callback)

        for i in range(5):
            message = broadcaster.send_message(
                room_id="room_1",
                sender_id="user_1",
                sender_name="Alice",
                content=f"msg_{i}",
            )
            broadcaster.broadcast_to_user(message, "user_2")

        # Get messages
        offline_msgs = broadcaster.get_offline_messages("user_2", count=3)
        assert len(offline_msgs) == 3

        # Check remaining
        offline_msgs = broadcaster.get_offline_messages("user_2")
        assert len(offline_msgs) == 2


class TestBroadcastHistory:
    """Test broadcast history"""

    def test_broadcast_history_recorded(self):
        """Test broadcast is recorded in history"""
        broadcaster = RoomBroadcaster()

        def callback(user_id: str, message: RoomMessage) -> bool:
            return True

        broadcaster.register_delivery_callback(callback)
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="msg",
        )

        broadcaster.broadcast_to_all(message, ["user_2", "user_3"])

        history = broadcaster.get_broadcast_history("room_1")
        assert len(history) >= 1
        assert history[-1].room_id == "room_1"
        assert history[-1].delivered_count == 2

    def test_broadcast_history_limit(self):
        """Test broadcast history size limit"""
        broadcaster = RoomBroadcaster()

        def callback(user_id: str, message: RoomMessage) -> bool:
            return True

        broadcaster.register_delivery_callback(callback)

        # Create many broadcasts
        for i in range(12000):
            message = broadcaster.send_message(
                room_id="room_1",
                sender_id="user_1",
                sender_name="Alice",
                content=f"msg_{i}",
            )
            broadcaster.broadcast_to_all(message, ["user_2"])

        assert len(broadcaster.broadcast_history) <= broadcaster.max_history


class TestBroadcasterStats:
    """Test broadcaster statistics"""

    def test_get_stats(self):
        """Test getting broadcaster stats"""
        broadcaster = RoomBroadcaster()

        def callback(user_id: str, message: RoomMessage) -> bool:
            return True

        broadcaster.register_delivery_callback(callback)
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="msg",
        )
        broadcaster.broadcast_to_all(message, ["user_2", "user_3"])

        stats = broadcaster.get_stats()
        assert stats["total_messages_sent"] == 1
        assert stats["total_messages_delivered"] == 2
        assert stats["delivery_callbacks_registered"] == 1

    def test_stats_track_failures(self):
        """Test stats track delivery failures"""
        broadcaster = RoomBroadcaster()

        def callback(user_id: str, message: RoomMessage) -> bool:
            return user_id != "user_3"

        broadcaster.register_delivery_callback(callback)
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="msg",
        )
        broadcaster.broadcast_to_all(message, ["user_2", "user_3", "user_4"])

        stats = broadcaster.get_stats()
        assert stats["total_delivery_failures"] == 1


class TestBroadcasterSingleton:
    """Test broadcaster singleton"""

    def test_get_broadcaster_singleton(self):
        """Test getting broadcaster singleton"""
        reset_broadcaster()
        broadcaster1 = get_broadcaster()
        broadcaster2 = get_broadcaster()
        assert broadcaster1 is broadcaster2

    def test_reset_broadcaster(self):
        """Test resetting broadcaster"""
        reset_broadcaster()
        broadcaster1 = get_broadcaster()
        reset_broadcaster()
        broadcaster2 = get_broadcaster()
        assert broadcaster1 is not broadcaster2


class TestBroadcastTask:
    """Test broadcast task"""

    def test_broadcast_task_creation(self):
        """Test creating broadcast task"""
        message = RoomMessage(room_id="room_1", sender_id="user_1", sender_name="Alice", content="msg")
        task = BroadcastTask(
            room_id="room_1",
            message=message,
            target_type=BroadcastTarget.ALL,
        )
        assert task.room_id == "room_1"
        assert task.target_type == BroadcastTarget.ALL

    def test_broadcast_task_to_dict(self):
        """Test task serialization"""
        message = RoomMessage(room_id="room_1", sender_id="user_1", sender_name="Alice", content="msg")
        task = BroadcastTask(
            room_id="room_1",
            message=message,
            target_type=BroadcastTarget.ROLE,
            target_value="admin",
            delivered_count=5,
        )
        task_dict = task.to_dict()
        assert task_dict["room_id"] == "room_1"
        assert task_dict["target_type"] == "role"
        assert task_dict["target_value"] == "admin"
        assert task_dict["delivered_count"] == 5


class TestIntegrationScenarios:
    """Test integration scenarios"""

    def test_complete_broadcast_workflow(self):
        """Test complete broadcast workflow"""
        broadcaster = RoomBroadcaster()
        successful_deliveries = []

        def callback(user_id: str, message: RoomMessage) -> bool:
            success = user_id != "offline_user"
            if success:
                successful_deliveries.append(user_id)
            return success

        broadcaster.register_delivery_callback(callback)

        # Send message
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="Hello room",
        )

        # Broadcast to all
        members = ["user_2", "user_3", "offline_user"]
        broadcaster.broadcast_to_all(message, members)

        # Check delivered
        assert len(successful_deliveries) == 2
        assert broadcaster.total_messages_delivered == 2
        assert broadcaster.total_delivery_failures == 1

        # Check offline messages
        offline = broadcaster.get_offline_messages("offline_user")
        assert len(offline) == 1

    def test_multi_room_broadcast(self):
        """Test broadcasting to multiple rooms"""
        broadcaster = RoomBroadcaster()

        def callback(user_id: str, message: RoomMessage) -> bool:
            return True

        broadcaster.register_delivery_callback(callback)

        # Send to room 1
        msg1 = broadcaster.send_message(
            room_id="room_1",
            sender_id="user_1",
            sender_name="Alice",
            content="room_1 msg",
        )
        broadcaster.broadcast_to_all(msg1, ["user_2"])

        # Send to room 2
        msg2 = broadcaster.send_message(
            room_id="room_2",
            sender_id="user_3",
            sender_name="Bob",
            content="room_2 msg",
        )
        broadcaster.broadcast_to_all(msg2, ["user_4"])

        # Check histories
        history1 = broadcaster.get_broadcast_history("room_1")
        history2 = broadcaster.get_broadcast_history("room_2")

        assert len(history1) >= 1
        assert len(history2) >= 1

    def test_role_based_notification(self):
        """Test role-based notification system"""
        broadcaster = RoomBroadcaster()
        admins_notified = []

        def callback(user_id: str, message: RoomMessage) -> bool:
            if message.message_type == MessageType.NOTIFICATION:
                admins_notified.append(user_id)
            return True

        broadcaster.register_delivery_callback(callback)

        # Send admin notification
        message = broadcaster.send_message(
            room_id="room_1",
            sender_id="system",
            sender_name="System",
            content="Admin alert",
            message_type=MessageType.NOTIFICATION,
        )

        room_members = {
            "user_1": "owner",
            "user_2": "admin",
            "user_3": "member",
            "user_4": "admin",
        }
        broadcaster.broadcast_to_role(message, room_members, "admin")

        assert len(admins_notified) == 2
