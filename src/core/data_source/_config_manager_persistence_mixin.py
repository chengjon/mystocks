"""
ConfigManager 持久化与版本管理辅助实现。
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ConfigVersion:
    """配置版本信息"""

    endpoint_name: str
    version: int
    config_snapshot: Dict[str, Any]
    change_type: str
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


class ConfigManagerPersistenceMixin:
    """ConfigManager 的持久化/版本辅助方法。"""

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """验证配置"""
        required_fields = ["endpoint_name", "source_name", "source_type", "data_category"]
        missing_fields = [field_name for field_name in required_fields if field_name not in config]

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        if "priority" in config:
            priority = config["priority"]
            if not isinstance(priority, int) or priority < 1 or priority > 10:
                raise ValueError(f"Priority must be an integer between 1 and 10, got {priority}")

        if config.get("data_category") not in [
            "DAILY_KLINE",
            "MINUTE_KLINE",
            "REALTIME_QUOTE",
            "FINANCIAL_DATA",
            "REFERENCE_DATA",
        ]:
            logger.warning("Unknown data_category: {config.get('data_category')}")

    def _save_to_yaml(self) -> None:
        """保存配置到 YAML 文件"""
        try:
            with open(self.yaml_config_path, "w", encoding="utf-8") as handle:
                yaml.dump(
                    {"data_sources": self.config_cache},
                    handle,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            logger.debug("Saved configuration to {self.yaml_config_path}")
        except Exception:
            logger.error("Failed to save configuration: %(e)s")
            raise

    def _record_version(
        self,
        endpoint_name: str,
        config: Dict[str, Any],
        change_type: str,
        changed_by: str,
        change_summary: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """记录配置版本"""
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

        if endpoint_name not in self.version_cache:
            self.version_cache[endpoint_name] = []

        self.version_cache[endpoint_name].append(version_info)

        if self.postgresql_access:
            self._save_version_to_db(version_info)

    def _get_next_version(self, endpoint_name: str) -> int:
        """获取下一个版本号"""
        versions = self.version_cache.get(endpoint_name, [])
        return max([version.version for version in versions], default=0) + 1

    def _save_version_to_db(self, version_info: ConfigVersion) -> None:
        """保存版本到 PostgreSQL"""
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

            logger.debug("Saved version to database: {version_info.endpoint_name} v{version_info.version}")
        except Exception:
            logger.error("Failed to save version to database: %(e)s")

    def _record_audit_log(
        self,
        endpoint_name: str,
        action: str,
        actor: str,
        request_body: Any = None,
        response_status: int = 200,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """记录审计日志"""
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
            except Exception:
                logger.error("Failed to save audit log: %(e)s")
