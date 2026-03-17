"""
旧版数据源配置路由的 reload 与生命周期辅助实现。
"""

from fastapi import HTTPException

from app.core.responses import BusinessCode, create_unified_error_response


async def reload_config_impl(current_user: str, manager_factory):
    """执行配置热重载。"""
    try:
        manager = manager_factory()
        result = manager.reload_config(changed_by=current_user)
        return {
            "success": True,
            "message": "配置热重载成功",
            "old_count": result["old_count"],
            "new_count": result["new_count"],
            "duration": result["duration"],
            "reloaded_at": result["reloaded_at"],
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"配置热重载失败: {str(error)}")


async def startup_event_impl() -> None:
    """API 启动事件。"""
    print("✅ 数据源配置CRUD API已启动")


async def shutdown_event_impl() -> None:
    """API 关闭事件。"""
    print("👋 数据源配置CRUD API已关闭")


def get_current_user_impl() -> str:
    """获取当前用户。"""
    return "system"


def handle_config_error_impl(error: str, request_id=None):
    """构造统一配置错误响应。"""
    if "already exists" in error:
        return create_unified_error_response(
            code=BusinessCode.CONFLICT,
            message="数据源配置已存在",
            error_code="DUPLICATE_ENDPOINT",
            request_id=request_id,
        )
    if "not found" in error:
        return create_unified_error_response(
            code=BusinessCode.NOT_FOUND,
            message="数据源配置不存在",
            error_code="ENDPOINT_NOT_FOUND",
            request_id=request_id,
        )
    return create_unified_error_response(
        code=BusinessCode.INTERNAL_ERROR,
        message=error,
        error_code="CONFIG_ERROR",
        request_id=request_id,
    )
