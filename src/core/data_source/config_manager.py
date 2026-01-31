"""
数据源配置管理器

提供数据源配置的版本管理、CRUD操作、批量操作和热重载功能。

核心功能:
- 配置版本控制（创建、更新、删除、回滚）
- 批量操作支持
- 配置热重载
- 配置验证和迁移

Author: Claude Code (Main CLI)
Date: 2026-01-09
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ConfigVersion:
    """配置版本信息"""

    endpoint_name: str
    version: int
    config_snapshot: Dict[str, Any]
    change_type: str  # create, update, delete, restore
    changed_by: str
    changed_at: datetime
    change_summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigChangeResult:
    """配置变更结果"""

    success: bool
    endpoint_name: str
    version: Optional[int] = None
    message: str = ""
    error: Optional[str] = None


@dataclass
class BatchOperationResult:
    """批量操作结果"""

    total: int
    succeeded: int
    failed: int
    results: List[ConfigChangeResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class ConfigManager:
    """
    数据源配置管理器

    职责:
    1. 管理数据源配置的生命周期（CRUD）
    2. 维护配置版本历史
    3. 支持配置回滚
    4. 执行批量操作
    5. 触发配置热重载

    使用示例:
    >>> manager = ConfigManager()
    >>> # 创建数据源
    >>> result = manager.create_endpoint(
    ...     endpoint_name="new_source",
    ...     source_name="test",
    ...     data_category="DAILY_KLINE",
    ...     priority=5
    ... )
    >>> # 更新数据源
    >>> result = manager.update_endpoint(
    ...     endpoint_name="new_source",
    ...     updates={"priority": 1}
    ... )
    >>> # 回滚到版本1
    >>> result = manager.rollback_to_version(
    ...     endpoint_name="new_source",
    ...     target_version=1
    ... )
    """

    def __init__(self, yaml_config_path: str = "config/data_sources_registry.yaml", postgresql_access=None):
        """
        初始化配置管理器

        Args:
            yaml_config_path: YAML配置文件路径
            postgresql_access: PostgreSQL访问实例（可选）
        """
        self.yaml_config_path = Path(yaml_config_path)
        self.postgresql_access = postgresql_access

        # 线程锁（保护配置操作）
        self.lock = threading.RLock()

        # 配置缓存（endpoint_name -> config）
        self.config_cache: Dict[str, Dict[str, Any]] = {}

        # 版本缓存（endpoint_name -> List[ConfigVersion]）
        self.version_cache: Dict[str, List[ConfigVersion]] = {}

        # 热重载回调函数列表
        self.reload_callbacks = []

        # 加载初始配置
        self._load_configs()

    def _load_configs(self):
        """从YAML文件加载配置"""
        try:
            with open(self.yaml_config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if config_data and "data_sources" in config_data:
                self.config_cache = config_data["data_sources"]
                logger.info("Loaded {len(self.config_cache)} data source configurations")
            else:
                logger.warning("No data sources found in {self.yaml_config_path}")
                self.config_cache = {}

        except FileNotFoundError:
            logger.error("Configuration file not found: {self.yaml_config_path}")
            self.config_cache = {}
        except Exception as e:
            logger.error("Failed to load configuration: %(e)s")
            self.config_cache = {}

    def create_endpoint(
        self,
        endpoint_name: str,
        source_name: str,
        source_type: str,
        data_category: str,
        parameters: Dict[str, Any],
        test_parameters: Dict[str, Any],
        priority: int = 5,
        description: str = "",
        changed_by: str = "system",
        **kwargs,
    ) -> ConfigChangeResult:
        """
        创建新的数据源配置

        Args:
            endpoint_name: 端点名称（唯一标识）
            source_name: 数据源名称
            source_type: 数据源类型
            data_category: 数据分类
            parameters: 参数定义
            test_parameters: 测试参数
            priority: 优先级（1-10，数字越小优先级越高）
            description: 描述
            changed_by: 变更人
            **kwargs: 其他配置字段

        Returns:
            ConfigChangeResult: 操作结果

        Raises:
            ValueError: 如果端点已存在
            ValidationError: 如果配置验证失败
        """
        with self.lock:
            # 检查端点是否已存在
            if endpoint_name in self.config_cache:
                return ConfigChangeResult(
                    success=False, endpoint_name=endpoint_name, error=f"Endpoint '{endpoint_name}' already exists"
                )

            # 创建配置对象
            config = {
                "endpoint_name": endpoint_name,
                "source_name": source_name,
                "source_type": source_type,
                "data_category": data_category,
                "parameters": parameters,
                "test_parameters": test_parameters,
                "priority": priority,
                "description": description,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                **kwargs,
            }

            # 验证配置
            self._validate_config(config)

            # 添加到缓存
            self.config_cache[endpoint_name] = config

            # 保存到YAML
            self._save_to_yaml()

            # 记录版本
            self._record_version(
                endpoint_name=endpoint_name,
                config=config,
                change_type="create",
                changed_by=changed_by,
                change_summary=f"Created endpoint '{endpoint_name}'",
            )

            # 记录审计日志
            self._record_audit_log(
                endpoint_name=endpoint_name, action="create", actor=changed_by, request_body=config, response_status=201
            )

            logger.info("Created endpoint: %(endpoint_name)s")

            return ConfigChangeResult(
                success=True,
                endpoint_name=endpoint_name,
                version=1,
                message=f"Endpoint '{endpoint_name}' created successfully",
            )

    def update_endpoint(
        self, endpoint_name: str, updates: Dict[str, Any], changed_by: str = "system"
    ) -> ConfigChangeResult:
        """
        更新数据源配置

        Args:
            endpoint_name: 端点名称
            updates: 要更新的字段
            changed_by: 变更人

        Returns:
            ConfigChangeResult: 操作结果

        Raises:
            ValueError: 如果端点不存在
            ValidationError: 如果配置验证失败
        """
        with self.lock:
            # 检查端点是否存在
            if endpoint_name not in self.config_cache:
                return ConfigChangeResult(
                    success=False, endpoint_name=endpoint_name, error=f"Endpoint '{endpoint_name}' not found"
                )

            # 获取当前配置
            current_config = self.config_cache[endpoint_name].copy()

            # 记录变更前的值
            changed_fields = []
            previous_values = {}

            # 应用更新
            for key, value in updates.items():
                if key in current_config and current_config[key] != value:
                    previous_values[key] = current_config[key]
                    changed_fields.append(key)
                current_config[key] = value

            if not changed_fields:
                return ConfigChangeResult(success=True, endpoint_name=endpoint_name, message="No changes detected")

            # 更新时间戳
            current_config["updated_at"] = datetime.now().isoformat()

            # 验证配置
            self._validate_config(current_config)

            # 更新缓存
            self.config_cache[endpoint_name] = current_config

            # 保存到YAML
            self._save_to_yaml()

            # 获取新版本号
            next_version = self._get_next_version(endpoint_name)

            # 记录版本
            self._record_version(
                endpoint_name=endpoint_name,
                config=current_config,
                change_type="update",
                changed_by=changed_by,
                change_summary=f"Updated fields: {', '.join(changed_fields)}",
                metadata={"changed_fields": changed_fields, "previous_values": previous_values},
            )

            # 记录审计日志
            self._record_audit_log(
                endpoint_name=endpoint_name,
                action="update",
                actor=changed_by,
                request_body=updates,
                response_status=200,
                metadata={"changed_fields": changed_fields},
            )

            logger.info("Updated endpoint: %(endpoint_name)s, version: %(next_version)s")

            return ConfigChangeResult(
                success=True,
                endpoint_name=endpoint_name,
                version=next_version,
                message=f"Endpoint '{endpoint_name}' updated successfully (version {next_version})",
            )

    def delete_endpoint(self, endpoint_name: str, changed_by: str = "system") -> ConfigChangeResult:
        """
        删除数据源配置

        Args:
            endpoint_name: 端点名称
            changed_by: 变更人

        Returns:
            ConfigChangeResult: 操作结果

        Raises:
            ValueError: 如果端点不存在
        """
        with self.lock:
            # 检查端点是否存在
            if endpoint_name not in self.config_cache:
                return ConfigChangeResult(
                    success=False, endpoint_name=endpoint_name, error=f"Endpoint '{endpoint_name}' not found"
                )

            # 获取当前配置
            current_config = self.config_cache[endpoint_name]

            # 从缓存删除
            del self.config_cache[endpoint_name]

            # 保存到YAML
            self._save_to_yaml()

            # 获取新版本号
            next_version = self._get_next_version(endpoint_name)

            # 记录版本（软删除）
            self._record_version(
                endpoint_name=endpoint_name,
                config=current_config,
                change_type="delete",
                changed_by=changed_by,
                change_summary=f"Deleted endpoint '{endpoint_name}'",
            )

            # 记录审计日志
            self._record_audit_log(
                endpoint_name=endpoint_name,
                action="delete",
                actor=changed_by,
                request_body={"endpoint_name": endpoint_name},
                response_status=204,
            )

            logger.info("Deleted endpoint: %(endpoint_name)s")

            return ConfigChangeResult(
                success=True,
                endpoint_name=endpoint_name,
                version=next_version,
                message=f"Endpoint '{endpoint_name}' deleted successfully",
            )

    def get_endpoint(self, endpoint_name: str) -> Optional[Dict[str, Any]]:
        """
        获取数据源配置

        Args:
            endpoint_name: 端点名称

        Returns:
            配置字典，如果不存在返回None
        """
        with self.lock:
            return self.config_cache.get(endpoint_name)

    def list_endpoints(
        self, data_category: Optional[str] = None, source_type: Optional[str] = None, status: Optional[str] = "active"
    ) -> List[Dict[str, Any]]:
        """
        列出数据源配置

        Args:
            data_category: 过滤：数据分类
            source_type: 过滤：数据源类型
            status: 过滤：状态（active, maintenance, deprecated）

        Returns:
            配置列表
        """
        with self.lock:
            endpoints = []

            for endpoint_name, config in self.config_cache.items():
                # 应用过滤条件
                if data_category and config.get("data_category") != data_category:
                    continue
                if source_type and config.get("source_type") != source_type:
                    continue
                if status and config.get("status") != status:
                    continue

                endpoints.append(config)

            # 按优先级排序
            endpoints.sort(key=lambda x: x.get("priority", 999))

            return endpoints

    def rollback_to_version(
        self, endpoint_name: str, target_version: int, changed_by: str = "system"
    ) -> ConfigChangeResult:
        """
        回滚配置到指定版本

        Args:
            endpoint_name: 端点名称
            target_version: 目标版本号
            changed_by: 变更人

        Returns:
            ConfigChangeResult: 操作结果

        Raises:
            ValueError: 如果版本不存在
        """
        with self.lock:
            # 获取版本历史
            versions = self.version_cache.get(endpoint_name, [])

            if not versions:
                return ConfigChangeResult(
                    success=False, endpoint_name=endpoint_name, error=f"No version history found for '{endpoint_name}'"
                )

            # 查找目标版本
            target_config_snapshot = None
            for version_info in versions:
                if version_info.version == target_version:
                    target_config_snapshot = version_info.config_snapshot
                    break

            if not target_config_snapshot:
                return ConfigChangeResult(
                    success=False,
                    endpoint_name=endpoint_name,
                    error=f"Version {target_version} not found for '{endpoint_name}'",
                )

            # 恢复配置
            self.config_cache[endpoint_name] = target_config_snapshot.copy()
            self.config_cache[endpoint_name]["updated_at"] = datetime.now().isoformat()

            # 保存到YAML
            self._save_to_yaml()

            # 获取新版本号
            next_version = self._get_next_version(endpoint_name)

            # 记录版本
            self._record_version(
                endpoint_name=endpoint_name,
                config=self.config_cache[endpoint_name],
                change_type="restore",
                changed_by=changed_by,
                change_summary=f"Restored to version {target_version}",
                metadata={"restored_from_version": target_version},
            )

            # 记录审计日志
            self._record_audit_log(
                endpoint_name=endpoint_name,
                action="rollback",
                actor=changed_by,
                request_body={"target_version": target_version},
                response_status=200,
                metadata={"restored_from_version": target_version},
            )

            logger.info("Rolled back endpoint: %(endpoint_name)s to version %(target_version)s")

            return ConfigChangeResult(
                success=True,
                endpoint_name=endpoint_name,
                version=next_version,
                message=f"Rolled back to version {target_version} successfully",
            )

    def get_version_history(self, endpoint_name: str, limit: int = 10) -> List[ConfigVersion]:
        """
        获取版本历史

        Args:
            endpoint_name: 端点名称
            limit: 返回数量限制

        Returns:
            版本列表（倒序）
        """
        with self.lock:
            versions = self.version_cache.get(endpoint_name, [])

            # 按版本号倒序排列
            versions = sorted(versions, key=lambda v: v.version, reverse=True)

            return versions[:limit]

    def reload_config(self, changed_by: str = "system") -> Dict[str, Any]:
        """
        热重载配置

        重新从YAML文件加载配置，并通知所有注册的回调函数。

        Args:
            changed_by: 变更人

        Returns:
            重载结果统计
        """
        with self.lock:
            start_time = datetime.now()

            # 记录重载前的配置数量
            old_count = len(self.config_cache)

            # 重新加载配置
            self._load_configs()

            # 触发所有回调函数
            for callback in self.reload_callbacks:
                try:
                    callback(self.config_cache)
                except Exception as e:
                    logger.error("Reload callback failed: %(e)s")

            duration = (datetime.now() - start_time).total_seconds()

            # 记录审计日志
            self._record_audit_log(
                endpoint_name="*",
                action="reload",
                actor=changed_by,
                request_body={},
                response_status=200,
                execution_time_ms=int(duration * 1000),
                metadata={"old_count": old_count, "new_count": len(self.config_cache), "duration_seconds": duration},
            )

            logger.info("Configuration reloaded: %(old_count)s -> {len(self.config_cache)} endpoints")

            return {
                "success": True,
                "old_count": old_count,
                "new_count": len(self.config_cache),
                "duration": duration,
                "reloaded_at": datetime.now().isoformat(),
            }

    def register_reload_callback(self, callback):
        """
        注册配置重载回调函数

        Args:
            callback: 回调函数，接收config_cache参数
        """
        if callback not in self.reload_callbacks:
            self.reload_callbacks.append(callback)
            logger.info("Registered reload callback: {callback.__name__")

    # ========== Private Methods ==========

    def _validate_config(self, config: Dict[str, Any]):
        """验证配置"""
        required_fields = ["endpoint_name", "source_name", "source_type", "data_category"]

        missing_fields = [f for f in required_fields if f not in config]

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # 验证优先级
        if "priority" in config:
            priority = config["priority"]
            if not isinstance(priority, int) or priority < 1 or priority > 10:
                raise ValueError(f"Priority must be an integer between 1 and 10, got {priority}")

        # 验证数据分类
        if config.get("data_category") not in [
            "DAILY_KLINE",
            "MINUTE_KLINE",
            "REALTIME_QUOTE",
            "FINANCIAL_DATA",
            "REFERENCE_DATA",
        ]:
            logger.warning("Unknown data_category: {config.get('data_category')")

    def _save_to_yaml(self):
        """保存配置到YAML文件"""
        try:
            with open(self.yaml_config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    {"data_sources": self.config_cache},
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            logger.debug("Saved configuration to {self.yaml_config_path}")
        except Exception as e:
            logger.error("Failed to save configuration: %(e)s")
            raise

    def _record_version(
        self,
        endpoint_name: str,
        config: Dict[str, Any],
        change_type: str,
        changed_by: str,
        change_summary: str = "",
        metadata: Dict[str, Any] = None,
    ):
        """
        记录配置版本

        Args:
            endpoint_name: 端点名称
            config: 配置快照
            change_type: 变更类型
            changed_by: 变更人
            change_summary: 变更摘要
            metadata: 元数据
        """
        version_info = ConfigVersion(
            endpoint_name=endpoint_name,
            version=self._get_next_version(endpoint_name),
            config_snapshot=config.copy(),
            change_type=change_type,
            changed_by=changed_by,
            changed_at=datetime.now(),
            change_summary=change_summary,
            metadata=metadata or {},
        )

        # 添加到版本缓存
        if endpoint_name not in self.version_cache:
            self.version_cache[endpoint_name] = []

        self.version_cache[endpoint_name].append(version_info)

        # 如果有PostgreSQL连接，保存到数据库
        if self.postgresql_access:
            self._save_version_to_db(version_info)

    def _get_next_version(self, endpoint_name: str) -> int:
        """获取下一个版本号"""
        versions = self.version_cache.get(endpoint_name, [])
        return max([v.version for v in versions], default=0) + 1

    def _save_version_to_db(self, version_info: ConfigVersion):
        """保存版本到PostgreSQL数据库"""
        if not self.postgresql_access:
            return

        try:
            query = """
            INSERT INTO data_source_versions (
                endpoint_name, version, config_snapshot,
                change_type, changed_by, change_summary, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            """

            self.postgresql_access.execute_query(
                query,
                (
                    version_info.endpoint_name,
                    version_info.version,
                    version_info.config_snapshot,
                    version_info.change_type,
                    version_info.changed_by,
                    version_info.change_summary,
                    version_info.metadata,
                ),
            )

            logger.debug("Saved version to database: {version_info.endpoint_name} v{version_info.version")

        except Exception as e:
            logger.error("Failed to save version to database: %(e)s")
            # 不抛出异常，允许继续操作

    def _record_audit_log(
        self,
        endpoint_name: str,
        action: str,
        actor: str,
        request_body: Any = None,
        response_status: int = 200,
        error_message: str = None,
        execution_time_ms: int = None,
        metadata: Dict[str, Any] = None,
    ):
        """
        记录审计日志

        Args:
            endpoint_name: 端点名称
            action: 操作类型
            actor: 操作人
            request_body: 请求体
            response_status: 响应状态码
            error_message: 错误消息
            execution_time_ms: 执行时间（毫秒）
            metadata: 元数据
        """
        # 如果有PostgreSQL连接，保存到数据库
        if self.postgresql_access:
            try:
                query = """
                INSERT INTO data_source_audit_log (
                    endpoint_name, action, actor, timestamp,
                    request_body, response_status, error_message,
                    execution_time_ms, metadata
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                )
                """

                self.postgresql_access.execute_query(
                    query,
                    (
                        endpoint_name,
                        action,
                        actor,
                        datetime.now(),
                        request_body,
                        response_status,
                        error_message,
                        execution_time_ms,
                        metadata,
                    ),
                )

                logger.debug("Saved audit log: %(action)s on %(endpoint_name)s")

            except Exception as e:
                logger.error("Failed to save audit log: %(e)s")
                # 不抛出异常，允许继续操作
