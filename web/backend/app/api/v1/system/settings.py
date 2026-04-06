"""
系统级配置 API

为 System-Config 的 general / security 分段提供唯一的系统级读写契约。
真实持久化统一落在 PostgreSQL `system_config` 表，不引入第二套配置真相源。
"""

from __future__ import annotations

import json
from typing import Any, Literal, Protocol, cast

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.responses import UnifiedResponse, create_unified_success_response
from src.monitoring.infrastructure._postgresql_async_v3_singleton import get_postgres_async

SectionName = Literal["general", "security"]


class GeneralSettingsPayload(BaseModel):
    """系统通用配置"""

    backend_url: str = Field("http://localhost:8020", min_length=1, max_length=200, description="系统默认后端地址")
    max_backtest_jobs: int = Field(4, ge=1, le=64, description="回测最大并发任务数")
    default_slippage_percent: float = Field(0.05, ge=0, le=10, description="默认滑点百分比")
    fee_rate_bps: float = Field(2.5, ge=0, le=1000, description="默认手续费万分比")


class SecuritySettingsPayload(BaseModel):
    """系统安全配置"""

    session_timeout_minutes: int = Field(120, ge=5, le=1440, description="会话超时时间，单位分钟")
    mfa_required: bool = Field(False, description="是否强制多因子认证")
    ip_allowlist_enabled: bool = Field(False, description="是否启用 IP 白名单")
    password_policy_level: Literal["standard", "strict"] = Field("standard", description="密码策略等级")


class SystemSettingsRepository(Protocol):
    async def read_section(self, section: SectionName) -> dict[str, Any]:
        ...

    async def write_section(self, section: SectionName, payload: dict[str, Any]) -> dict[str, Any]:
        ...


GENERAL_SETTINGS_EXAMPLES = {
    "default_trading_defaults": {
        "summary": "系统通用默认参数",
        "value": GeneralSettingsPayload().model_dump(mode="json"),
    }
}

SECURITY_SETTINGS_EXAMPLES = {
    "strict_security_defaults": {
        "summary": "更严格的系统安全参数",
        "value": SecuritySettingsPayload(
            session_timeout_minutes=90,
            mfa_required=True,
            ip_allowlist_enabled=True,
            password_policy_level="strict",
        ).model_dump(mode="json"),
    }
}

SYSTEM_SETTINGS_ERROR_RESPONSES = {
    503: {
        "description": "System settings are temporarily unavailable because the canonical system_config repository cannot be reached.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "system_config repository unavailable",
                }
            }
        },
    }
}


def _success_response_spec(description: str, example: Any) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


GENERAL_SETTINGS_READ_RESPONSES = {
    **SYSTEM_SETTINGS_ERROR_RESPONSES,
    **_success_response_spec(
        "系统通用设置读取结果",
        {
            "success": True,
            "code": 200,
            "message": "获取系统通用设置成功",
            "data": GeneralSettingsPayload().model_dump(mode="json"),
            "timestamp": "2026-04-07T08:00:00Z",
            "request_id": "req-system-settings-general-read-001",
            "errors": None,
        },
    ),
}

GENERAL_SETTINGS_UPDATE_RESPONSES = {
    **SYSTEM_SETTINGS_ERROR_RESPONSES,
    **_success_response_spec(
        "系统通用设置更新结果",
        {
            "success": True,
            "code": 200,
            "message": "更新系统通用设置成功",
            "data": GeneralSettingsPayload().model_dump(mode="json"),
            "timestamp": "2026-04-07T08:00:00Z",
            "request_id": "req-system-settings-general-write-001",
            "errors": None,
        },
    ),
}

SECURITY_SETTINGS_READ_RESPONSES = {
    **SYSTEM_SETTINGS_ERROR_RESPONSES,
    **_success_response_spec(
        "系统安全设置读取结果",
        {
            "success": True,
            "code": 200,
            "message": "获取系统安全设置成功",
            "data": SecuritySettingsPayload().model_dump(mode="json"),
            "timestamp": "2026-04-07T08:00:00Z",
            "request_id": "req-system-settings-security-read-001",
            "errors": None,
        },
    ),
}

SECURITY_SETTINGS_UPDATE_RESPONSES = {
    **SYSTEM_SETTINGS_ERROR_RESPONSES,
    **_success_response_spec(
        "系统安全设置更新结果",
        {
            "success": True,
            "code": 200,
            "message": "更新系统安全设置成功",
            "data": SecuritySettingsPayload(
                session_timeout_minutes=90,
                mfa_required=True,
                ip_allowlist_enabled=True,
                password_policy_level="strict",
            ).model_dump(mode="json"),
            "timestamp": "2026-04-07T08:00:00Z",
            "request_id": "req-system-settings-security-write-001",
            "errors": None,
        },
    ),
}

SECTION_MODELS = {
    "general": GeneralSettingsPayload,
    "security": SecuritySettingsPayload,
}

SECTION_FIELD_SPECS: dict[SectionName, dict[str, dict[str, Any]]] = {
    "general": {
        "backend_url": {
            "type": "string",
            "default": "http://localhost:8020",
            "description": "系统默认后端地址",
            "is_sensitive": False,
        },
        "max_backtest_jobs": {
            "type": "integer",
            "default": 4,
            "description": "回测最大并发任务数",
            "is_sensitive": False,
        },
        "default_slippage_percent": {
            "type": "float",
            "default": 0.05,
            "description": "默认滑点百分比",
            "is_sensitive": False,
        },
        "fee_rate_bps": {
            "type": "float",
            "default": 2.5,
            "description": "默认手续费万分比",
            "is_sensitive": False,
        },
    },
    "security": {
        "session_timeout_minutes": {
            "type": "integer",
            "default": 120,
            "description": "会话超时时间，单位分钟",
            "is_sensitive": False,
        },
        "mfa_required": {
            "type": "boolean",
            "default": False,
            "description": "是否强制多因子认证",
            "is_sensitive": False,
        },
        "ip_allowlist_enabled": {
            "type": "boolean",
            "default": False,
            "description": "是否启用 IP 白名单",
            "is_sensitive": False,
        },
        "password_policy_level": {
            "type": "string",
            "default": "standard",
            "description": "密码策略等级",
            "is_sensitive": False,
        },
    },
}

router = APIRouter(
    prefix="/system/settings",
    tags=["System Settings"],
)


class PostgresSystemSettingsRepository:
    """直接使用 PostgreSQL system_config 表的最薄仓储层。"""

    def __init__(self, postgres_access: Any | None = None) -> None:
        self._postgres_access = postgres_access or get_postgres_async()
        self._is_readonly_storage_value: bool | int | None = None

    def _require_pool(self) -> Any:
        is_connected = getattr(self._postgres_access, "is_connected", lambda: False)
        pool = getattr(self._postgres_access, "pool", None)
        if not is_connected() or pool is None:
            raise RuntimeError("system_config repository unavailable")
        return pool

    async def _resolve_is_readonly_storage_value(self, pool: Any) -> bool | int:
        if self._is_readonly_storage_value is not None:
            return self._is_readonly_storage_value

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT data_type, udt_name
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'system_config'
                  AND column_name = 'is_readonly'
                """
            )

        data_type = str(row["data_type"]).lower() if row and row["data_type"] is not None else ""
        udt_name = str(row["udt_name"]).lower() if row and row["udt_name"] is not None else ""

        if data_type == "boolean" or udt_name == "bool":
            self._is_readonly_storage_value = False
        elif data_type in {"smallint", "integer", "bigint"} or udt_name in {"int2", "int4", "int8"}:
            self._is_readonly_storage_value = 0
        else:
            self._is_readonly_storage_value = False

        return self._is_readonly_storage_value

    async def read_section(self, section: SectionName) -> dict[str, Any]:
        pool = self._require_pool()
        await self._ensure_defaults(section, pool)

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT config_key, config_value, config_type
                FROM system_config
                WHERE config_group = $1
                ORDER BY config_key
                """,
                section,
            )

        values = {
            row["config_key"]: self._deserialize_value(row["config_value"], row["config_type"])
            for row in rows
        }
        model_cls = SECTION_MODELS[section]
        return cast(dict[str, Any], model_cls(**values).model_dump(mode="json"))

    async def write_section(self, section: SectionName, payload: dict[str, Any]) -> dict[str, Any]:
        pool = self._require_pool()
        model_cls = SECTION_MODELS[section]
        normalized = cast(dict[str, Any], model_cls(**payload).model_dump(mode="json"))
        readonly_storage_value = await self._resolve_is_readonly_storage_value(pool)

        async with pool.acquire() as conn:
            async with conn.transaction():
                for key, spec in SECTION_FIELD_SPECS[section].items():
                    value = normalized[key]
                    serialized_value = self._serialize_value(value, spec["type"])
                    update_status = await conn.execute(
                        """
                        UPDATE system_config
                        SET config_value = $1,
                            config_type = $2,
                            description = $3,
                            is_sensitive = $4,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE config_group = $5 AND config_key = $6
                        """,
                        serialized_value,
                        spec["type"],
                        spec["description"],
                        spec["is_sensitive"],
                        section,
                        key,
                    )
                    if update_status.endswith("0"):
                        await conn.execute(
                            """
                            INSERT INTO system_config
                            (config_group, config_key, config_value, config_type, description, is_sensitive, is_readonly, created_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            """,
                            section,
                            key,
                            serialized_value,
                            spec["type"],
                            spec["description"],
                            spec["is_sensitive"],
                            readonly_storage_value,
                        )

        return normalized

    async def _ensure_defaults(self, section: SectionName, pool: Any) -> None:
        readonly_storage_value = await self._resolve_is_readonly_storage_value(pool)

        async with pool.acquire() as conn:
            async with conn.transaction():
                for key, spec in SECTION_FIELD_SPECS[section].items():
                    existing_row = await conn.fetchval(
                        """
                        SELECT 1
                        FROM system_config
                        WHERE config_group = $1 AND config_key = $2
                        LIMIT 1
                        """,
                        section,
                        key,
                    )
                    if existing_row is None:
                        await conn.execute(
                            """
                            INSERT INTO system_config
                            (config_group, config_key, config_value, config_type, description, is_sensitive, is_readonly, created_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            """,
                            section,
                            key,
                            self._serialize_value(spec["default"], spec["type"]),
                            spec["type"],
                            spec["description"],
                            spec["is_sensitive"],
                            readonly_storage_value,
                        )

    @staticmethod
    def _serialize_value(value: Any, config_type: str) -> str:
        if config_type == "boolean":
            return "true" if bool(value) else "false"
        if config_type == "integer":
            return str(int(value))
        if config_type == "float":
            return str(float(value))
        if config_type == "json":
            return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        return str(value)

    @staticmethod
    def _deserialize_value(value: str, config_type: str) -> Any:
        if config_type == "boolean":
            return value.lower() == "true"
        if config_type == "integer":
            return int(value)
        if config_type == "float":
            return float(value)
        if config_type == "json":
            return json.loads(value)
        return value


def get_system_settings_repository() -> SystemSettingsRepository:
    return PostgresSystemSettingsRepository()


def _raise_unavailable(exc: RuntimeError) -> None:
    raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get(
    "/general",
    response_model=UnifiedResponse[GeneralSettingsPayload],
    summary="Get General System Settings",
    description="Read the canonical system-scoped general settings from the PostgreSQL system_config truth.",
    responses=GENERAL_SETTINGS_READ_RESPONSES,
)
async def get_general_settings(
    repository: SystemSettingsRepository = Depends(get_system_settings_repository),
) -> UnifiedResponse[GeneralSettingsPayload]:
    try:
        data = await repository.read_section("general")
    except RuntimeError as exc:
        _raise_unavailable(exc)

    payload = GeneralSettingsPayload(**data)
    return create_unified_success_response(data=payload, message="获取系统通用设置成功")


@router.post(
    "/general",
    response_model=UnifiedResponse[GeneralSettingsPayload],
    summary="Update General System Settings",
    description="Persist the canonical system-scoped general settings into the PostgreSQL system_config truth.",
    responses=GENERAL_SETTINGS_UPDATE_RESPONSES,
)
async def update_general_settings(
    payload: GeneralSettingsPayload = Body(..., openapi_examples=GENERAL_SETTINGS_EXAMPLES),
    repository: SystemSettingsRepository = Depends(get_system_settings_repository),
) -> UnifiedResponse[GeneralSettingsPayload]:
    try:
        saved = await repository.write_section("general", payload.model_dump(mode="json"))
    except RuntimeError as exc:
        _raise_unavailable(exc)

    return create_unified_success_response(
        data=GeneralSettingsPayload(**saved),
        message="更新系统通用设置成功",
    )


@router.get(
    "/security",
    response_model=UnifiedResponse[SecuritySettingsPayload],
    summary="Get Security System Settings",
    description="Read the canonical system-scoped security settings from the PostgreSQL system_config truth.",
    responses=SECURITY_SETTINGS_READ_RESPONSES,
)
async def get_security_settings(
    repository: SystemSettingsRepository = Depends(get_system_settings_repository),
) -> UnifiedResponse[SecuritySettingsPayload]:
    try:
        data = await repository.read_section("security")
    except RuntimeError as exc:
        _raise_unavailable(exc)

    payload = SecuritySettingsPayload(**data)
    return create_unified_success_response(data=payload, message="获取系统安全设置成功")


@router.post(
    "/security",
    response_model=UnifiedResponse[SecuritySettingsPayload],
    summary="Update Security System Settings",
    description="Persist the canonical system-scoped security settings into the PostgreSQL system_config truth.",
    responses=SECURITY_SETTINGS_UPDATE_RESPONSES,
)
async def update_security_settings(
    payload: SecuritySettingsPayload = Body(..., openapi_examples=SECURITY_SETTINGS_EXAMPLES),
    repository: SystemSettingsRepository = Depends(get_system_settings_repository),
) -> UnifiedResponse[SecuritySettingsPayload]:
    try:
        saved = await repository.write_section("security", payload.model_dump(mode="json"))
    except RuntimeError as exc:
        _raise_unavailable(exc)

    return create_unified_success_response(
        data=SecuritySettingsPayload(**saved),
        message="更新系统安全设置成功",
    )


__all__ = [
    "GeneralSettingsPayload",
    "PostgresSystemSettingsRepository",
    "SecuritySettingsPayload",
    "SystemSettingsRepository",
    "get_system_settings_repository",
    "router",
]
