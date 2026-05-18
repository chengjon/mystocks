"""
OpenAPI 配置模块
OpenAPI Configuration Module

为FastAPI应用提供增强的OpenAPI/Swagger文档配置:
- API元数据和版本信息
- 标签分组和描述
- 通用响应示例
- 安全方案定义

Author: Claude Code
Date: 2025-11-06
"""

import os
from copy import deepcopy
from typing import Any, Dict

from fastapi import FastAPI

from app.openapi_metadata import API_METADATA, COMMON_RESPONSES, OPENAPI_TAGS, SECURITY_SCHEMES

def get_openapi_config() -> Dict[str, Any]:
    """
    获取OpenAPI配置

    Returns:
        OpenAPI配置字典，用于FastAPI app初始化
    """
    return {
        **API_METADATA,
        "openapi_tags": OPENAPI_TAGS,
        "swagger_ui_parameters": {
            "defaultModelsExpandDepth": 2,
            "defaultModelExpandDepth": 2,
            "docExpansion": "list",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "syntaxHighlight.theme": "monokai",
            # 使用国内可访问的 CDN 镜像（解决 cdn.jsdelivr.net 被墙问题）
            "swagger_js_url": "https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.10.0/swagger-ui-bundle.js",
            "swagger_css_url": "https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.10.0/swagger-ui.css",
        },
        "swagger_ui_oauth2_redirect_url": "/api/docs/oauth2-redirect",
    }


def get_openapi_schema_extra() -> Dict[str, Any]:
    """
    获取OpenAPI Schema扩展配置

    Returns:
        OpenAPI Schema扩展配置（servers, security等）
    """
    backend_port = os.getenv("BACKEND_PORT", "").strip()
    backend_backup_port = os.getenv("BACKEND_BACKUP_PORT", "").strip()
    servers = []

    if backend_port:
        servers.append({"url": f"http://localhost:{backend_port}", "description": "本地开发环境"})
        servers.append({"url": f"http://127.0.0.1:{backend_port}", "description": "本地开发环境 (127.0.0.1)"})

    if backend_backup_port and backend_backup_port != backend_port:
        servers.append({"url": f"http://localhost:{backend_backup_port}", "description": "本地备用环境"})

    servers.append(
        {
            "url": "https://api.mystocks.com",
            "description": "生产环境 (需要HTTPS)",
        }
    )

    return {
        "servers": servers,
        "components": {
            "securitySchemes": SECURITY_SCHEMES,
            "responses": COMMON_RESPONSES,
        },
        "security": [
            {"Bearer": []},  # 默认需要JWT Token
            {"CSRFToken": []},  # 修改操作需要CSRF Token
        ],
    }


def _merge_openapi_schema(base_schema: Dict[str, Any], extra_schema: Dict[str, Any]) -> Dict[str, Any]:
    """递归合并额外 OpenAPI 配置，保留 FastAPI 自动生成的 schema 内容。"""
    for key, value in extra_schema.items():
        if isinstance(value, dict) and isinstance(base_schema.get(key), dict):
            _merge_openapi_schema(base_schema[key], value)
            continue

        base_schema[key] = deepcopy(value)

    return base_schema


def _ensure_schema_description(schema: Dict[str, Any], description: str) -> None:
    """仅在 schema 未声明 description 时补充兜底描述。"""
    if schema and not schema.get("description"):
        schema["description"] = description


def _ensure_property_descriptions(schema: Dict[str, Any], descriptions: Dict[str, str]) -> None:
    """为自动生成但未携带描述的字段补充契约说明。"""
    properties = schema.get("properties", {})
    for field_name, description in descriptions.items():
        field_schema = properties.get(field_name)
        if isinstance(field_schema, dict) and not field_schema.get("description"):
            field_schema["description"] = description


def _ensure_json_success_example(operation: Dict[str, Any], example: Dict[str, Any]) -> None:
    """为缺失成功响应示例的 legacy operation 补充 JSON 示例。"""
    responses = operation.setdefault("responses", {})
    response = responses.setdefault("200", {"description": "Successful response"})
    content = response.setdefault("content", {})
    json_content = content.setdefault("application/json", {})
    if "example" not in json_content and "examples" not in json_content:
        json_content["example"] = example


def _ensure_request_body_example(operation: Dict[str, Any], example: Dict[str, Any]) -> None:
    """为缺失请求体示例的 legacy operation 补充 JSON 示例。"""
    request_body = operation.get("requestBody")
    if not isinstance(request_body, dict):
        return

    json_content = request_body.get("content", {}).get("application/json")
    if isinstance(json_content, dict) and "example" not in json_content and "examples" not in json_content:
        json_content["example"] = example


def _ensure_error_response(operation: Dict[str, Any]) -> None:
    """为未声明错误响应的 legacy operation 补充统一 500 示例。"""
    responses = operation.setdefault("responses", {})
    if any(str(status_code).startswith(("4", "5")) for status_code in responses):
        return

    responses["500"] = {
        "description": "请求处理失败。",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "code": 500,
                    "message": "request processing failed",
                    "data": None,
                }
            }
        },
    }


def _ensure_parameter_description(operation: Dict[str, Any], parameter_name: str, description: str) -> None:
    """为自动生成但缺失说明的路径或查询参数补充描述。"""
    for parameter in operation.get("parameters", []):
        if isinstance(parameter, dict) and parameter.get("name") == parameter_name and not parameter.get("description"):
            parameter["description"] = description


def _patch_legacy_operation_metadata(schema: Dict[str, Any]) -> None:
    """补齐少量历史端点的 OpenAPI 元数据，避免旧路由拖低契约门禁。"""
    paths = schema.get("paths", {})
    if not isinstance(paths, dict):
        return

    strategy_mgmt_example = {
        "success": True,
        "code": 200,
        "message": "strategy management proxy response",
        "data": {"path": "strategies", "status": "forwarded"},
    }
    for method in ("get", "put", "patch", "delete", "post"):
        operation = paths.get("/api/strategy-mgmt/{path}", {}).get(method)
        if isinstance(operation, dict):
            operation.setdefault("summary", "Strategy management compatibility proxy")
            operation["description"] = operation.get("description") or (
                "Compatibility proxy for strategy-management sub-routes retained during route migration."
            )
            _ensure_parameter_description(operation, "path", "Strategy-management sub-route path to forward.")
            _ensure_json_success_example(operation, strategy_mgmt_example)
            _ensure_error_response(operation)

    chart_operation = paths.get("/api/v1/strategy/backtest/results/{backtest_id}/chart-data", {}).get("get")
    if isinstance(chart_operation, dict):
        _ensure_json_success_example(
            chart_operation,
            {
                "success": True,
                "code": 200,
                "message": "Backtest chart data loaded",
                "data": {"backtest_id": "bt-001", "series": []},
            },
        )

    backup_success_example = {
        "success": True,
        "data": {"status": "accepted", "operation_id": "backup-op-001"},
        "message": "backup recovery operation accepted",
    }
    backup_request_examples = {
        "/api/backup-recovery/backup/tdengine/full": {"description": "nightly tdengine full backup", "tags": ["nightly"]},
        "/api/backup-recovery/backup/tdengine/incremental": {
            "since_backup_id": "tdengine-full-001",
            "description": "incremental backup",
        },
        "/api/backup-recovery/backup/postgresql/full": {
            "include_tables": ["orders", "positions"],
            "compression_level": 6,
            "description": "postgresql full backup",
        },
        "/api/backup-recovery/recovery/tdengine/full": {
            "backup_id": "tdengine-full-001",
            "dry_run": True,
            "force": False,
        },
        "/api/backup-recovery/recovery/tdengine/pitr": {
            "target_time": "2026-05-18T08:00:00+08:00",
            "target_tables": ["ticks"],
        },
        "/api/backup-recovery/recovery/postgresql/full": {
            "backup_id": "postgresql-full-001",
            "dry_run": True,
            "drop_existing": False,
        },
        "/api/backup-recovery/scheduler/control": {"action": "status", "force": False},
        "/api/backup-recovery/cleanup/old-backups": {
            "retention_days": 30,
            "database": "postgresql",
            "dry_run": True,
        },
    }
    backup_paths = [
        "/api/backup-recovery/backup/tdengine/full",
        "/api/backup-recovery/backup/tdengine/incremental",
        "/api/backup-recovery/backup/postgresql/full",
        "/api/backup-recovery/backups",
        "/api/backup-recovery/recovery/tdengine/full",
        "/api/backup-recovery/recovery/tdengine/pitr",
        "/api/backup-recovery/recovery/postgresql/full",
        "/api/backup-recovery/recovery/objectives",
        "/api/backup-recovery/scheduler/control",
        "/api/backup-recovery/scheduler/jobs",
        "/api/backup-recovery/integrity/verify/{backup_id}",
        "/api/backup-recovery/cleanup/old-backups",
        "/api/backup-recovery/health",
    ]
    for path_name in backup_paths:
        for method_name, operation in paths.get(path_name, {}).items():
            if method_name not in {"get", "post", "put", "patch", "delete"} or not isinstance(operation, dict):
                continue

            _ensure_json_success_example(operation, backup_success_example)
            _ensure_error_response(operation)
            _ensure_parameter_description(operation, "backup_id", "Backup file identifier to verify.")
            request_example = backup_request_examples.get(path_name)
            if request_example:
                _ensure_request_body_example(operation, request_example)


def _patch_legacy_schema_property_descriptions(schemas: Dict[str, Dict[str, Any]]) -> None:
    """补齐历史策略/回测 schema 中遗留的字段描述。"""
    patches = {
        "BacktestResult": {
            "performance": "Backtest performance metrics such as return, drawdown and risk ratios.",
            "status": "Backtest execution status.",
        },
        "BacktestResultSummary": {"status": "Backtest execution status."},
        "StrategyConfig": {
            "strategy_type": "Strategy implementation type.",
            "status": "Strategy lifecycle status.",
        },
        "StrategyCreateRequest": {"strategy_type": "Strategy implementation type requested for creation."},
        "TaskConfig": {"priority": "Task scheduling priority."},
    }
    for schema_name, property_descriptions in patches.items():
        target_schema = schemas.get(schema_name)
        if isinstance(target_schema, dict):
            _ensure_property_descriptions(target_schema, property_descriptions)


def _patch_autogenerated_request_schemas(schemas: Dict[str, Dict[str, Any]]) -> None:
    """补齐 FastAPI 自动生成请求体 schema 的描述。"""
    compat_login_schema = schemas.get("Body_compat_login_api_auth_login_post")
    if isinstance(compat_login_schema, dict):
        _ensure_schema_description(compat_login_schema, "兼容历史 /api/auth/login 表单登录请求体。")

    oauth_login_schema = schemas.get("Body_login_for_access_token_api_v1_auth_login_post")
    if isinstance(oauth_login_schema, dict):
        _ensure_schema_description(oauth_login_schema, "OAuth2 密码模式登录请求体。")
        _ensure_property_descriptions(
            oauth_login_schema,
            {
                "grant_type": "OAuth2 授权类型，密码模式固定为 password。",
                "username": "登录用户名。",
                "password": "登录密码。",
                "scope": "OAuth2 授权范围，多个 scope 以空格分隔。",
                "client_id": "客户端 ID，供受信任客户端接入时透传。",
                "client_secret": "客户端密钥，供受信任客户端接入时透传。",
            },
        )

    reconciliation_import_schema = schemas.get(
        "Body_import_reconciliation_csv_api_v1_trade_reconciliation_import_post"
    )
    if isinstance(reconciliation_import_schema, dict):
        _ensure_schema_description(reconciliation_import_schema, "交易对账 CSV 导入的 multipart/form-data 请求体。")


def _patch_validation_error_schemas(schemas: Dict[str, Dict[str, Any]]) -> None:
    """补齐 FastAPI 默认校验错误 schema 的描述。"""
    validation_error_schema = schemas.get("ValidationError")
    if isinstance(validation_error_schema, dict):
        _ensure_schema_description(validation_error_schema, "单个请求校验错误条目。")
        _ensure_property_descriptions(
            validation_error_schema,
            {
                "loc": "校验失败字段的位置路径。",
                "msg": "人类可读的校验失败消息。",
                "type": "校验错误类型标识。",
            },
        )

    http_validation_error_schema = schemas.get("HTTPValidationError")
    if isinstance(http_validation_error_schema, dict):
        _ensure_schema_description(http_validation_error_schema, "请求参数或请求体校验失败时返回的错误响应。")
        _ensure_property_descriptions(
            http_validation_error_schema,
            {
                "detail": "请求校验失败的详细错误列表。",
            },
        )


def _patch_unified_response_schemas(schemas: Dict[str, Dict[str, Any]]) -> None:
    """为 Pydantic 泛型实例化后丢失描述的统一响应 schema 补充说明。"""
    for schema_name, schema in schemas.items():
        if not schema_name.startswith("UnifiedResponse_") or not isinstance(schema, dict):
            continue

        title = schema.get("title", "")
        if title == "UnifiedResponse[NoneType]":
            description = "统一 API 响应包装器，无业务数据载荷，仅返回状态与元信息。"
        else:
            payload_name = title.removeprefix("UnifiedResponse[").removesuffix("]") or "业务数据"
            description = (
                f"统一 API 响应包装器，data 字段承载 {payload_name}，"
                "同时返回 success、code、message、timestamp、request_id 与 errors 元信息。"
            )

        _ensure_schema_description(schema, description)


def _patch_openapi_generated_schema_descriptions(schema: Dict[str, Any]) -> Dict[str, Any]:
    """在 FastAPI 自动生成后，对缺失的 schema description 做契约级兜底。"""
    schemas = schema.get("components", {}).get("schemas", {})
    if not isinstance(schemas, dict):
        return schema

    _patch_autogenerated_request_schemas(schemas)
    _patch_validation_error_schemas(schemas)
    _patch_unified_response_schemas(schemas)
    _patch_legacy_schema_property_descriptions(schemas)
    _patch_legacy_operation_metadata(schema)
    return schema


def install_openapi_schema_extra(app: FastAPI) -> None:
    """给 FastAPI 实例挂接 schema 扩展，避免 servers/security 配置丢失。"""
    original_openapi = app.openapi

    def custom_openapi():
        if app.openapi_schema is not None:
            return app.openapi_schema

        schema = original_openapi()
        merged_schema = _merge_openapi_schema(schema, get_openapi_schema_extra())
        app.openapi_schema = _patch_openapi_generated_schema_descriptions(merged_schema)
        return app.openapi_schema

    app.openapi = custom_openapi
