"""
Casbin权限管理集成 - Casbin RBAC Integration

Task 10: Casbin权限集成

功能特性:
- Casbin RBAC (Role-Based Access Control) 集成
- 动态权限管理
- 角色继承
- 资源级别权限控制
- 权限策略持久化

Author: Claude Code
Date: 2025-11-07
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import structlog
import os

try:
    import casbin
except ImportError:
    casbin = None

logger = structlog.get_logger()


@dataclass
class RoleDefinition:
    """角色定义"""

    name: str = ""
    description: str = ""
    permissions: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "permissions": list(self.permissions),
        }


@dataclass
class PermissionRule:
    """权限规则"""

    subject: str = ""
    object: str = ""
    action: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_list(self) -> List[str]:
        """转换为列表格式"""
        return [self.subject, self.object, self.action]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "subject": self.subject,
            "object": self.object,
            "action": self.action,
            "metadata": self.metadata,
        }


class CasbinManager:
    """Casbin权限管理器"""

    def __init__(self, model_path: Optional[str] = None, policy_path: Optional[str] = None):
        """初始化Casbin管理器

        Args:
            model_path: RBAC模型文件路径
            policy_path: 权限策略文件路径
        """
        self.model_path = model_path or self._get_default_model_path()
        self.policy_path = policy_path or self._get_default_policy_path()
        self.enforcer = None
        self.role_definitions: Dict[str, RoleDefinition] = {}
        self.policy_cache: Dict[str, List[str]] = {}

        # 统计
        self.total_enforce_calls = 0
        self.total_allow_decisions = 0
        self.total_deny_decisions = 0

        self._initialize_casbin()
        logger.info("✅ Casbin Manager initialized")

    def _get_default_model_path(self) -> str:
        """获取默认RBAC模型路径"""
        return os.path.join(os.path.dirname(__file__), "..", "..", "policies", "rbac_model.conf")

    def _get_default_policy_path(self) -> str:
        """获取默认权限策略路径"""
        return os.path.join(os.path.dirname(__file__), "..", "..", "policies", "rbac_policy.csv")

    def _initialize_casbin(self) -> None:
        """初始化Casbin enforcer"""
        if casbin is None:
            logger.warning("⚠️ python-casbin not installed, using basic enforcement")
            return

        try:
            # 确保模型文件存在
            if not os.path.exists(self.model_path):
                logger.warning(
                    "⚠️ Model file not found, creating default RBAC model",
                    model_path=self.model_path,
                )
                self._create_default_model_file()

            # 确保策略文件存在
            if not os.path.exists(self.policy_path):
                logger.warning(
                    "⚠️ Policy file not found, creating default policy file",
                    policy_path=self.policy_path,
                )
                self._create_default_policy_file()

            # 创建enforcer
            self.enforcer = casbin.Enforcer(self.model_path, self.policy_path)
            logger.info(
                "✅ Casbin enforcer initialized",
                model_path=self.model_path,
                policy_path=self.policy_path,
            )

        except Exception as e:
            logger.error(
                "❌ Failed to initialize Casbin enforcer",
                error=str(e),
            )
            self.enforcer = None

    def _create_default_model_file(self) -> None:
        """创建默认RBAC模型文件"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        model_content = """[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act || r.sub == "admin"
"""

        with open(self.model_path, "w") as f:
            f.write(model_content)

        logger.info("✅ Default RBAC model file created", path=self.model_path)

    def _create_default_policy_file(self) -> None:
        """创建默认权限策略文件"""
        os.makedirs(os.path.dirname(self.policy_path), exist_ok=True)

        policy_content = """p, admin, indicator, read
p, admin, indicator, write
p, admin, indicator, delete
p, admin, dashboard, read
p, admin, dashboard, write
p, admin, dashboard, delete
p, admin, user, read
p, admin, user, write
p, admin, user, delete
p, user, indicator, read
p, user, dashboard, read
p, vip, indicator, read
p, vip, indicator, write
p, vip, dashboard, read
p, vip, dashboard, write
p, guest, indicator, read

g, admin, admin
g, regular_admin, admin
g, vip_user, vip
g, regular_user, user
g, guest_user, guest
"""

        with open(self.policy_path, "w") as f:
            f.write(policy_content)

        logger.info("✅ Default policy file created", path=self.policy_path)

    def enforce(self, subject: str, resource: str, action: str) -> bool:
        """检查是否有权限

        Args:
            subject: 主体 (用户或角色)
            resource: 资源
            action: 操作

        Returns:
            是否有权限
        """
        self.total_enforce_calls += 1

        if self.enforcer is None:
            logger.warning(
                "⚠️ Casbin enforcer not available, denying access",
                subject=subject,
                resource=resource,
                action=action,
            )
            return False

        try:
            result = self.enforcer.enforce(subject, resource, action)
            if result:
                self.total_allow_decisions += 1
            else:
                self.total_deny_decisions += 1

            logger.debug(
                "Permission check",
                subject=subject,
                resource=resource,
                action=action,
                result=result,
            )
            return result

        except Exception as e:
            logger.error(
                "❌ Enforce failed",
                subject=subject,
                resource=resource,
                action=action,
                error=str(e),
            )
            return False

    def add_role(self, subject: str, action: str, resource: str) -> bool:
        """添加权限

        Args:
            subject: 主体 (用户或角色)
            action: 操作 (read, write, delete)
            resource: 资源

        Returns:
            是否成功添加
        """
        if self.enforcer is None:
            return False

        try:
            self.enforcer.add_policy(subject, resource, action)
            logger.info(
                "✅ Permission added",
                subject=subject,
                resource=resource,
                action=action,
            )
            return True

        except Exception as e:
            logger.error(
                "❌ Failed to add permission",
                subject=subject,
                resource=resource,
                action=action,
                error=str(e),
            )
            return False

    def remove_role(self, subject: str, action: str, resource: str) -> bool:
        """移除权限

        Args:
            subject: 主体
            action: 操作
            resource: 资源

        Returns:
            是否成功移除
        """
        if self.enforcer is None:
            return False

        try:
            self.enforcer.remove_policy(subject, resource, action)
            logger.info(
                "✅ Permission removed",
                subject=subject,
                resource=resource,
                action=action,
            )
            return True

        except Exception as e:
            logger.error(
                "❌ Failed to remove permission",
                subject=subject,
                resource=resource,
                action=action,
                error=str(e),
            )
            return False

    def add_role_inheritance(self, role1: str, role2: str) -> bool:
        """添加角色继承

        Args:
            role1: 上级角色
            role2: 下级角色

        Returns:
            是否成功
        """
        if self.enforcer is None:
            return False

        try:
            self.enforcer.add_grouping_policy(role1, role2)
            logger.info(
                "✅ Role inheritance added",
                role1=role1,
                role2=role2,
            )
            return True

        except Exception as e:
            logger.error(
                "❌ Failed to add role inheritance",
                role1=role1,
                role2=role2,
                error=str(e),
            )
            return False

    def add_permission(
        self,
        subject: str,
        resource: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """添加权限（支持元数据）

        Args:
            subject: 主体
            resource: 资源
            action: 操作
            metadata: 元数据

        Returns:
            是否成功
        """
        return self.add_role(subject, action, resource)

    def batch_add_permissions(self, permissions: List[PermissionRule]) -> int:
        """批量添加权限

        Args:
            permissions: 权限规则列表

        Returns:
            成功添加的数量
        """
        count = 0
        for perm in permissions:
            if self.add_role(perm.subject, perm.action, perm.object):
                count += 1

        logger.info("✅ Batch add permissions completed", count=count, total=len(permissions))
        return count

    def batch_remove_permissions(self, permissions: List[PermissionRule]) -> int:
        """批量移除权限

        Args:
            permissions: 权限规则列表

        Returns:
            成功移除的数量
        """
        count = 0
        for perm in permissions:
            if self.remove_role(perm.subject, perm.action, perm.object):
                count += 1

        logger.info("✅ Batch remove permissions completed", count=count, total=len(permissions))
        return count

    def get_policy(self) -> Optional[List[List[str]]]:
        """获取所有权限策略

        Returns:
            权限规则列表
        """
        if self.enforcer is None:
            return None

        try:
            return self.enforcer.get_policy()
        except Exception as e:
            logger.error("❌ Failed to get policy", error=str(e))
            return None

    def get_all_roles(self) -> List[str]:
        """获取所有角色

        Returns:
            角色列表
        """
        if self.enforcer is None:
            return []

        try:
            policies = self.enforcer.get_policy()
            roles = set()
            for policy in policies:
                if len(policy) > 0:
                    roles.add(policy[0])

            return list(roles)

        except Exception as e:
            logger.error("❌ Failed to get roles", error=str(e))
            return []

    def get_permissions_for_role(self, role: str) -> List[List[str]]:
        """获取角色的所有权限

        Args:
            role: 角色名

        Returns:
            权限规则列表
        """
        if self.enforcer is None:
            return []

        try:
            policies = self.enforcer.get_policy()
            return [p for p in policies if p[0] == role]

        except Exception as e:
            logger.error(
                "❌ Failed to get permissions for role",
                role=role,
                error=str(e),
            )
            return []

    def save_policy(self) -> bool:
        """保存权限策略到文件

        Returns:
            是否成功
        """
        if self.enforcer is None:
            return False

        try:
            self.enforcer.save_policy()
            logger.info("✅ Policy saved to file", path=self.policy_path)
            return True

        except Exception as e:
            logger.error(
                "❌ Failed to save policy",
                path=self.policy_path,
                error=str(e),
            )
            return False

    def reload_policy(self) -> bool:
        """重新加载权限策略

        Returns:
            是否成功
        """
        if self.enforcer is None:
            return False

        try:
            self.enforcer.load_policy()
            logger.info("✅ Policy reloaded")
            return True

        except Exception as e:
            logger.error("❌ Failed to reload policy", error=str(e))
            return False

    def get_stats(self) -> Dict[str, Any]:
        """获取管理器统计

        Returns:
            统计信息
        """
        return {
            "total_enforce_calls": self.total_enforce_calls,
            "total_allow_decisions": self.total_allow_decisions,
            "total_deny_decisions": self.total_deny_decisions,
            "total_policies": len(self.get_policy() or []),
            "total_roles": len(self.get_all_roles()),
            "model_path": self.model_path,
            "policy_path": self.policy_path,
        }


# 全局单例
_manager: Optional[CasbinManager] = None


def get_casbin_manager() -> CasbinManager:
    """获取Casbin管理器单例

    Returns:
        管理器实例
    """
    global _manager
    if _manager is None:
        _manager = CasbinManager()
    return _manager


def reset_casbin_manager() -> None:
    """重置管理器单例（仅用于测试）"""
    global _manager
    _manager = None
