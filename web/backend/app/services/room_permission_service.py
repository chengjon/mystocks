"""
房间权限控制服务 - Room Permission Control Service

Task 9: 多房间订阅扩展

功能特性:
- 基于Casbin的角色访问控制 (RBAC)
- 房间级别的权限管理
- 权限验证和授权
- 权限缓存和性能优化

Author: Claude Code
Date: 2025-11-07
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum
import structlog

try:
    import casbin
except ImportError:
    casbin = None

logger = structlog.get_logger()


class RoomRole(str, Enum):
    """房间角色"""

    OWNER = "owner"  # 房间主人
    ADMIN = "admin"  # 管理员
    MODERATOR = "moderator"  # 版主
    MEMBER = "member"  # 普通成员
    GUEST = "guest"  # 访客


class RoomPermission(str, Enum):
    """房间权限"""

    # 访问权限
    VIEW = "view"  # 查看房间
    JOIN = "join"  # 加入房间
    LEAVE = "leave"  # 离开房间
    LIST_MEMBERS = "list_members"  # 列出成员

    # 发言权限
    SEND_MESSAGE = "send_message"  # 发送消息
    EDIT_MESSAGE = "edit_message"  # 编辑消息
    DELETE_MESSAGE = "delete_message"  # 删除消息
    MENTION_ALL = "mention_all"  # @所有人

    # 管理权限
    INVITE_MEMBER = "invite_member"  # 邀请成员
    KICK_MEMBER = "kick_member"  # 踢出成员
    CHANGE_MEMBER_ROLE = "change_member_role"  # 更改成员角色
    MANAGE_ROOM_INFO = "manage_room_info"  # 管理房间信息
    MANAGE_PERMISSIONS = "manage_permissions"  # 管理权限
    DELETE_ROOM = "delete_room"  # 删除房间


@dataclass
class RolePermissionMapping:
    """角色权限映射"""

    role: RoomRole
    permissions: Set[RoomPermission]

    def has_permission(self, permission: RoomPermission) -> bool:
        """检查是否有权限"""
        return permission in self.permissions


class RoomPermissionManager:
    """房间权限管理器"""

    def __init__(self, use_casbin: bool = False):
        """初始化权限管理器

        Args:
            use_casbin: 是否使用Casbin，如果为False则使用内置权限映射
        """
        self.use_casbin = use_casbin and casbin is not None
        self.enforcer = None
        self.permission_cache: Dict[str, Dict[str, bool]] = {}
        self.role_permissions: Dict[RoomRole, Set[RoomPermission]] = {}
        self._init_default_permissions()

        if self.use_casbin:
            self._init_casbin()

        logger.info(
            "✅ Room Permission Manager initialized",
            use_casbin=self.use_casbin,
        )

    def _init_default_permissions(self) -> None:
        """初始化默认权限映射"""
        # 房间主人 - 所有权限
        self.role_permissions[RoomRole.OWNER] = {
            RoomPermission.VIEW,
            RoomPermission.JOIN,
            RoomPermission.LEAVE,
            RoomPermission.LIST_MEMBERS,
            RoomPermission.SEND_MESSAGE,
            RoomPermission.EDIT_MESSAGE,
            RoomPermission.DELETE_MESSAGE,
            RoomPermission.MENTION_ALL,
            RoomPermission.INVITE_MEMBER,
            RoomPermission.KICK_MEMBER,
            RoomPermission.CHANGE_MEMBER_ROLE,
            RoomPermission.MANAGE_ROOM_INFO,
            RoomPermission.MANAGE_PERMISSIONS,
            RoomPermission.DELETE_ROOM,
        }

        # 管理员 - 除删除房间外的所有权限
        self.role_permissions[RoomRole.ADMIN] = {
            RoomPermission.VIEW,
            RoomPermission.JOIN,
            RoomPermission.LEAVE,
            RoomPermission.LIST_MEMBERS,
            RoomPermission.SEND_MESSAGE,
            RoomPermission.EDIT_MESSAGE,
            RoomPermission.DELETE_MESSAGE,
            RoomPermission.MENTION_ALL,
            RoomPermission.INVITE_MEMBER,
            RoomPermission.KICK_MEMBER,
            RoomPermission.CHANGE_MEMBER_ROLE,
            RoomPermission.MANAGE_ROOM_INFO,
            RoomPermission.MANAGE_PERMISSIONS,
        }

        # 版主 - 发言和基础管理权限
        self.role_permissions[RoomRole.MODERATOR] = {
            RoomPermission.VIEW,
            RoomPermission.JOIN,
            RoomPermission.LEAVE,
            RoomPermission.LIST_MEMBERS,
            RoomPermission.SEND_MESSAGE,
            RoomPermission.EDIT_MESSAGE,
            RoomPermission.DELETE_MESSAGE,
            RoomPermission.MENTION_ALL,
            RoomPermission.KICK_MEMBER,
            RoomPermission.INVITE_MEMBER,
        }

        # 普通成员 - 基础权限
        self.role_permissions[RoomRole.MEMBER] = {
            RoomPermission.VIEW,
            RoomPermission.JOIN,
            RoomPermission.LEAVE,
            RoomPermission.LIST_MEMBERS,
            RoomPermission.SEND_MESSAGE,
            RoomPermission.EDIT_MESSAGE,
            RoomPermission.MENTION_ALL,
        }

        # 访客 - 最小权限
        self.role_permissions[RoomRole.GUEST] = {
            RoomPermission.VIEW,
            RoomPermission.LIST_MEMBERS,
        }

    def _init_casbin(self) -> None:
        """初始化Casbin"""
        try:
            # 创建RBAC模型
            model_text = """
[request_definition]
r = sub, dom, obj, act

[policy_definition]
p = sub, dom, obj, act

[role_definition]
g = _, _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub, r.dom) && r.dom == p.dom && r.obj == p.obj && r.act == p.act || r.sub == "admin"
"""

            # 创建adapter（使用内存存储）
            casbin.FileAdapter(":memory:")

            # 创建enforcer
            self.enforcer = casbin.Enforcer(model_text, None)

            logger.info("✅ Casbin enforcer initialized")
        except Exception as e:
            logger.error("❌ Failed to initialize Casbin", error=str(e))
            self.use_casbin = False

    def check_permission(
        self,
        user_id: str,
        room_id: str,
        permission: RoomPermission,
        user_role: RoomRole,
    ) -> bool:
        """检查用户在房间中是否有权限

        Args:
            user_id: 用户ID
            room_id: 房间ID
            permission: 权限
            user_role: 用户角色

        Returns:
            是否有权限
        """
        # 检查缓存
        cache_key = f"{user_id}:{room_id}:{permission.value}"
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]

        # 计算权限
        result = False

        if self.use_casbin and self.enforcer:
            try:
                result = self.enforcer.enforce(user_id, room_id, room_id, permission.value)
            except Exception as e:
                logger.warning(
                    "⚠️ Casbin enforce failed, using default permissions",
                    error=str(e),
                )
                result = self._check_default_permission(user_role, permission)
        else:
            result = self._check_default_permission(user_role, permission)

        # 缓存结果
        self.permission_cache[cache_key] = result
        return result

    def _check_default_permission(self, user_role: RoomRole, permission: RoomPermission) -> bool:
        """使用默认权限映射检查权限"""
        if user_role not in self.role_permissions:
            return False
        return permission in self.role_permissions[user_role]

    def add_role_permission(self, role: RoomRole, permission: RoomPermission) -> bool:
        """为角色添加权限

        Args:
            role: 角色
            permission: 权限

        Returns:
            是否成功添加
        """
        if role not in self.role_permissions:
            self.role_permissions[role] = set()

        self.role_permissions[role].add(permission)
        self._clear_cache()

        logger.info("✅ Permission added", role=role.value, permission=permission.value)
        return True

    def remove_role_permission(self, role: RoomRole, permission: RoomPermission) -> bool:
        """从角色移除权限

        Args:
            role: 角色
            permission: 权限

        Returns:
            是否成功移除
        """
        if role not in self.role_permissions:
            return False

        self.role_permissions[role].discard(permission)
        self._clear_cache()

        logger.info("✅ Permission removed", role=role.value, permission=permission.value)
        return True

    def get_role_permissions(self, role: RoomRole) -> Set[RoomPermission]:
        """获取角色的所有权限

        Args:
            role: 角色

        Returns:
            权限集合
        """
        return self.role_permissions.get(role, set()).copy()

    def _clear_cache(self) -> None:
        """清空权限缓存"""
        self.permission_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取管理器统计"""
        return {
            "use_casbin": self.use_casbin,
            "cache_size": len(self.permission_cache),
            "roles_defined": len(self.role_permissions),
            "total_permissions": sum(len(perms) for perms in self.role_permissions.values()),
        }


class RoomAccessControl:
    """房间访问控制"""

    def __init__(self, permission_manager: RoomPermissionManager):
        """初始化访问控制

        Args:
            permission_manager: 权限管理器
        """
        self.permission_manager = permission_manager
        self.access_log: List[Dict[str, Any]] = []
        logger.info("✅ Room Access Control initialized")

    def can_join_room(self, user_id: str, room_id: str, user_role: RoomRole) -> bool:
        """检查用户是否可以加入房间

        Args:
            user_id: 用户ID
            room_id: 房间ID
            user_role: 用户角色

        Returns:
            是否可以加入
        """
        has_permission = self.permission_manager.check_permission(user_id, room_id, RoomPermission.JOIN, user_role)

        if has_permission:
            self._log_access("join", user_id, room_id, True)
        else:
            self._log_access("join", user_id, room_id, False)

        return has_permission

    def can_send_message(self, user_id: str, room_id: str, user_role: RoomRole) -> bool:
        """检查用户是否可以发送消息

        Args:
            user_id: 用户ID
            room_id: 房间ID
            user_role: 用户角色

        Returns:
            是否可以发送
        """
        has_permission = self.permission_manager.check_permission(
            user_id, room_id, RoomPermission.SEND_MESSAGE, user_role
        )
        self._log_access("send_message", user_id, room_id, has_permission)
        return has_permission

    def can_delete_message(self, user_id: str, room_id: str, message_owner: str, user_role: RoomRole) -> bool:
        """检查用户是否可以删除消息

        Args:
            user_id: 用户ID
            room_id: 房间ID
            message_owner: 消息所有者
            user_role: 用户角色

        Returns:
            是否可以删除
        """
        # 消息所有者或有DELETE_MESSAGE权限
        if user_id == message_owner:
            return True

        return self.permission_manager.check_permission(user_id, room_id, RoomPermission.DELETE_MESSAGE, user_role)

    def can_kick_member(self, user_id: str, room_id: str, target_user_id: str, user_role: RoomRole) -> bool:
        """检查用户是否可以踢出成员

        Args:
            user_id: 用户ID
            room_id: 房间ID
            target_user_id: 目标用户ID
            user_role: 用户角色

        Returns:
            是否可以踢出
        """
        # 不能踢出自己
        if user_id == target_user_id:
            self._log_access("kick_member", user_id, room_id, False)
            return False

        has_permission = self.permission_manager.check_permission(
            user_id, room_id, RoomPermission.KICK_MEMBER, user_role
        )
        self._log_access("kick_member", user_id, room_id, has_permission)
        return has_permission

    def can_change_role(self, user_id: str, room_id: str, user_role: RoomRole) -> bool:
        """检查用户是否可以更改其他用户的角色

        Args:
            user_id: 用户ID
            room_id: 房间ID
            user_role: 用户角色

        Returns:
            是否可以更改
        """
        return self.permission_manager.check_permission(user_id, room_id, RoomPermission.CHANGE_MEMBER_ROLE, user_role)

    def can_delete_room(self, user_id: str, room_id: str, user_role: RoomRole) -> bool:
        """检查用户是否可以删除房间

        Args:
            user_id: 用户ID
            room_id: 房间ID
            user_role: 用户角色

        Returns:
            是否可以删除
        """
        return self.permission_manager.check_permission(user_id, room_id, RoomPermission.DELETE_ROOM, user_role)

    def _log_access(self, action: str, user_id: str, room_id: str, success: bool) -> None:
        """记录访问日志"""
        self.access_log.append(
            {
                "action": action,
                "user_id": user_id,
                "room_id": room_id,
                "success": success,
            }
        )

    def get_access_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取访问日志

        Args:
            limit: 限制条数

        Returns:
            访问日志列表
        """
        return self.access_log[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """获取访问控制统计"""
        return {
            "total_access_logs": len(self.access_log),
            "permission_manager_stats": self.permission_manager.get_stats(),
        }


# 全局单例
_permission_manager: Optional[RoomPermissionManager] = None
_access_control: Optional[RoomAccessControl] = None


def get_permission_manager(use_casbin: bool = False) -> RoomPermissionManager:
    """获取权限管理器单例

    Args:
        use_casbin: 是否使用Casbin

    Returns:
        权限管理器实例
    """
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = RoomPermissionManager(use_casbin=use_casbin)
    return _permission_manager


def get_access_control() -> RoomAccessControl:
    """获取访问控制单例

    Returns:
        访问控制实例
    """
    global _access_control
    if _access_control is None:
        _access_control = RoomAccessControl(get_permission_manager())
    return _access_control


def reset_permission_manager() -> None:
    """重置权限管理器单例（仅用于测试）"""
    global _permission_manager
    _permission_manager = None


def reset_access_control() -> None:
    """重置访问控制单例（仅用于测试）"""
    global _access_control
    _access_control = None
