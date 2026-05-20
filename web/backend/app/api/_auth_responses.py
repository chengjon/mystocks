"""Response specs extracted from auth."""

from typing import Any
from app.openapi_config import COMMON_RESPONSES

def _success_response_spec(status_code: int, description: str, example: object) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _error_response_spec(status_code: int, description: str, example: dict) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


AUTH_LOGOUT_RESPONSES = {
    **_success_response_spec(200, "用户登出成功", {"message": "登出成功", "success": True}),
}

AUTH_LOGIN_RESPONSES = {
    **_success_response_spec(
        200,
        "用户登录成功并返回访问令牌",
        {
            "success": True,
            "data": {
                "token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 7200,
                "user": {"id": 1, "username": "trader_admin", "email": "admin@example.com", "role": "admin"},
            },
            "message": "登录成功",
            "timestamp": "2026-04-05T12:00:00Z",
            "request_id": "req-auth-login-001",
        },
    ),
}

AUTH_ME_RESPONSES = {
    **_success_response_spec(
        200,
        "当前登录用户信息",
        {"id": 1, "username": "trader_admin", "email": "admin@example.com", "role": "admin", "is_active": True},
    ),
}

AUTH_REFRESH_RESPONSES = {
    **_success_response_spec(
        200,
        "访问令牌刷新成功",
        {"access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer", "expires_in": 7200},
    ),
}

AUTH_REGISTER_RESPONSES = {
    **_error_response_spec(409, "用户名或邮箱已存在", {"detail": "用户名已存在", "error_code": "USER_ALREADY_EXISTS"}),
    **_success_response_spec(
        201,
        "用户注册成功",
        {
            "success": True,
            "data": {
                "id": 3,
                "username": "john_doe",
                "email": "john@example.com",
                "role": "user",
                "is_active": True,
            },
            "message": "User registered successfully",
            "timestamp": "2026-04-05T12:00:00Z",
            "request_id": "req-auth-register-001",
        },
    ),
}

AUTH_RESET_REQUEST_RESPONSES = {
    **_success_response_spec(
        200,
        "密码重置请求已受理",
        {
            "success": True,
            "data": None,
            "message": "If the email exists, a password reset link has been sent",
            "timestamp": "2026-04-05T12:00:00Z",
            "request_id": "req-auth-reset-001",
        },
    ),
}

AUTH_RESET_CONFIRM_RESPONSES = {
    **_error_response_spec(
        400,
        "密码重置令牌无效或已过期",
        {"detail": "Invalid or expired reset token", "error_code": "INVALID_RESET_TOKEN"},
    ),
    **_success_response_spec(
        200,
        "密码重置成功",
        {
            "success": True,
            "data": None,
            "message": "Password reset successfully",
            "timestamp": "2026-04-05T12:00:00Z",
            "request_id": "req-auth-reset-confirm-001",
        },
    ),
}

AUTH_USERS_RESPONSES = {
    **_success_response_spec(
        200,
        "用户列表查询成功",
        {
            "users": [
                {
                    "id": 1,
                    "username": "trader_admin",
                    "email": "admin@example.com",
                    "role": "admin",
                    "is_active": True,
                },
                {
                    "id": 2,
                    "username": "market_viewer",
                    "email": "viewer@example.com",
                    "role": "user",
                    "is_active": True,
                },
            ],
            "total": 2,
        },
    ),
}

AUTH_CSRF_RESPONSES = {
    **_success_response_spec(
        200,
        "CSRF 令牌生成成功",
        {
            "success": True,
            "data": {
                "token": "csrf-token-example",
                "token_type": "csrf",
                "expires_in": 3600,
            },
            "message": "CSRF token generated successfully",
            "timestamp": "2026-04-07T03:45:00Z",
            "request_id": "req-auth-csrf-001",
        },
    ),
}
