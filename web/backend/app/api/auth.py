"""
认证相关 API
"""

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.config import settings
from app.core.responses import create_success_response
from app.core.security import (
    User,
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_token,
)


# Pydantic schemas for request validation
class UserRegisterRequest(BaseModel):
    """User registration request schema"""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    role: str = Field(default="user", pattern="^(user|admin)$", description="User role")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not v.isalnum() and "_" not in v:
            raise ValueError("Username must be alphanumeric or contain underscores")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(BaseModel):
    """User response schema"""

    id: int
    username: str
    email: str
    role: str
    is_active: bool


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""

    email: EmailStr = Field(..., description="Email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


router = APIRouter()
security = HTTPBearer()

# User database now backed by PostgreSQL via security.py
# The authenticate_user() and get_user_from_database() functions
# handle database queries with automatic fallback to mock data
# if the database is unavailable.


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    获取当前用户 - 恢复认证验证
    验证 JWT token 并返回授权用户信息
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # 验证 JWT token
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username: str = token_data.username
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从安全模块获取用户信息（数据库或模拟数据）
    from app.core.security import authenticate_user_by_id

    user_in_db = authenticate_user_by_id(token_data.user_id)
    if user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = User(
        id=user_in_db.id,
        username=user_in_db.username,
        email=user_in_db.email,
        role=user_in_db.role,
        is_active=user_in_db.is_active,
    )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户 - 验证用户活跃状态
    检查用户是否处于活跃状态
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    用户登录获取访问令牌
    支持 OAuth2 标准的 form data 格式
    返回 APIResponse 格式以匹配前端期望
    """
    # 验证用户身份
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires,
    )

    # 返回 APIResponse 格式，使用 "token" 而不是 "access_token" 以匹配前端期望
    return create_success_response(
        data={
            "token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {"username": user.username, "email": user.email, "role": user.role},
        },
        message="登录成功",
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    用户登出
    """
    # 在实际应用中，可以将 token 加入黑名单
    return {"message": "登出成功", "success": True}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前用户信息
    """
    return current_user


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    刷新访问令牌
    """
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": current_user.username,
            "user_id": current_user.id,
            "role": current_user.role,
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.get("/users")
async def get_users(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    获取用户列表（仅管理员）
    从PostgreSQL数据库获取所有活跃用户
    """
    if not check_permission(current_user.role, "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    try:
        from app.core.database import get_postgresql_session
        from app.db import UserRepository
        from src.core.exceptions import DatabaseConnectionError, DatabaseOperationError

        session = get_postgresql_session()
        try:
            repository = UserRepository(session)
            users_list = repository.get_all_users()

            users = []
            for user in users_list:
                user_info = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    # 不返回密码哈希
                }
                users.append(user_info)

            return {"users": users, "total": len(users)}

        finally:
            session.close()

    except (DatabaseConnectionError, DatabaseOperationError) as e:
        # 数据库查询失败时返回错误响应
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to retrieve users: {str(e)}",
        )
    except Exception as e:
        # 捕获其他异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}",
        )


def check_permission(user_role: str, required_role: str) -> bool:
    """
    检查用户权限
    """
    role_hierarchy = {"user": 0, "admin": 1}

    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)


# SECURITY FIX 1.2: CSRF Token获取端点
@router.get("/csrf/token")
async def get_csrf_token():
    """
    获取CSRF保护令牌 - v1版本 (标准化端点)

    用于防止跨站请求伪造（CSRF）攻击。
    前端应该在发送修改请求（POST/PUT/PATCH/DELETE）时，
    在X-CSRF-Token请求头中包含此令牌。

    **响应示例**:
    ```json
    {
        "code": "SUCCESS",
        "message": "CSRF token generated successfully",
        "data": {
            "token": "...base64-encoded-token...",
            "token_type": "csrf",
            "expires_in": 3600
        },
        "timestamp": 1733318400.123
    }
    ```

    **使用示例**:
    ```javascript
    // 获取CSRF token
    const response = await fetch('/api/v1/auth/csrf/token');
    const { data } = await response.json();
    const csrfToken = data.token;

    // 发送受保护的请求
    fetch('/api/v1/data', {
        method: 'POST',
        headers: {
            'X-CSRF-Token': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ... })
    });
    ```

    **错误码**:
    - SUCCESS: Token生成成功
    - INTERNAL_SERVER_ERROR: Token生成失败

    **HTTP状态码**:
    - 200: 成功获取token
    - 500: 服务器错误

    **Rate Limit**: 无限制（CSRF token获取不计入速率限制）
    """
    from app.main import csrf_manager

    try:
        # 生成新的CSRF token
        token = csrf_manager.generate_token()

        return create_success_response(
            data={
                "token": token,
                "token_type": "csrf",
                "expires_in": csrf_manager.token_timeout,
            },
            message="CSRF token generated successfully",
        )
    except Exception as e:
        return create_success_response(
            data=None,
            message=f"Failed to generate CSRF token: {str(e)}",
            code="INTERNAL_SERVER_ERROR",
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest):
    """
    用户注册

    创建新用户账户。要求：
    - 用户名: 3-50字符，仅允许字母、数字、下划线
    - 邮箱: 有效的邮箱地址（唯一）
    - 密码: 最少8字符，必须包含大小写字母和数字
    - 角色: user 或 admin（默认: user）

    **请求示例**:
    ```json
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecurePass123",
        "role": "user"
    }
    ```

    **响应示例**:
    ```json
    {
        "code": "SUCCESS",
        "message": "User registered successfully",
        "data": {
            "id": 3,
            "username": "john_doe",
            "email": "john@example.com",
            "role": "user",
            "is_active": true
        },
        "timestamp": 1733318400.123
    }
    ```

    **错误码**:
    - SUCCESS: 注册成功
    - USERNAME_EXISTS: 用户名已存在
    - EMAIL_EXISTS: 邮箱已被注册
    - INVALID_USERNAME: 用户名格式无效
    - INVALID_EMAIL: 邮箱格式无效
    - INVALID_PASSWORD: 密码强度不足

    **HTTP状态码**:
    - 201: 注册成功
    - 400: 请求数据无效
    - 409: 用户名或邮箱已存在
    - 500: 服务器错误
    """
    from app.core.database import get_postgresql_session
    from app.db import UserRepository
    from src.core.exceptions import (
        DatabaseConnectionError,
        DatabaseOperationError,
        DataValidationError,
    )

    session = None
    try:
        session = get_postgresql_session()
        repository = UserRepository(session)

        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create user in database
        new_user = repository.create_user(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True,
        )

        # Log user registration
        repository.log_user_action(
            user_id=new_user.id,
            action="user_registered",
            details={"username": new_user.username, "email": new_user.email},
        )

        # Return response without password
        return create_success_response(
            data=UserResponse(
                id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                role=new_user.role,
                is_active=new_user.is_active,
            ).dict(),
            message="User registered successfully",
        )

    except DataValidationError as e:
        # Validation errors (invalid input format)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )

    except DatabaseOperationError as e:
        # Database operation errors (duplicate username/email)
        if e.code in ["USERNAME_EXISTS", "EMAIL_EXISTS"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=e.message,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.message,
            )

    except (DatabaseConnectionError, DatabaseOperationError) as e:
        # Database connection errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {e.message if hasattr(e, 'message') else str(e)}",
        )

    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during registration: {str(e)}",
        )

    finally:
        if session:
            session.close()


@router.post("/reset-password/request")
async def request_password_reset(request: PasswordResetRequest):
    """
    请求密码重置

    发送密码重置链接到用户邮箱。

    **请求示例**:
    ```json
    {
        "email": "user@example.com"
    }
    ```

    **响应示例**:
    ```json
    {
        "code": "SUCCESS",
        "message": "If the email exists, a password reset link has been sent",
        "data": null,
        "timestamp": 1733318400.123
    }
    ```

    **注意**: 无论邮箱是否存在，都返回成功消息（防止邮箱枚举攻击）

    **错误码**:
    - SUCCESS: 请求已处理（不表示邮箱存在）
    - INTERNAL_SERVER_ERROR: 服务器错误

    **HTTP状态码**:
    - 200: 请求已处理
    - 500: 服务器错误
    """
    from app.core.database import get_postgresql_session
    from app.db import UserRepository
    from src.core.exceptions import DatabaseConnectionError, DatabaseOperationError

    session = None
    try:
        session = get_postgresql_session()
        repository = UserRepository(session)

        # Check if user exists (but don't reveal whether they exist)
        user = repository.get_user_by_email(request.email)

        if user:
            # Generate password reset token (valid for 1 hour)
            from app.core.security import create_access_token

            reset_token = create_access_token(
                data={"sub": user.username, "user_id": user.id, "purpose": "password_reset"},
                expires_delta=timedelta(hours=1),
            )

            # Log password reset request
            repository.log_user_action(
                user_id=user.id,
                action="password_reset_requested",
                details={"email": user.email},
            )

            # TODO: Send email with reset token
            # For now, just log the token (in production, send via email)
            print(f"Password reset token for {user.email}: {reset_token}")

        # Always return success (to prevent email enumeration)
        return create_success_response(
            data=None,
            message="If the email exists, a password reset link has been sent",
        )

    except (DatabaseConnectionError, DatabaseOperationError) as e:
        # Database errors still return success message
        print(f"Database error during password reset request: {str(e)}")
        return create_success_response(
            data=None,
            message="If the email exists, a password reset link has been sent",
        )

    except Exception as e:
        # Unexpected errors
        print(f"Unexpected error during password reset request: {str(e)}")
        return create_success_response(
            data=None,
            message="If the email exists, a password reset link has been sent",
        )

    finally:
        if session:
            session.close()


@router.post("/reset-password/confirm")
async def confirm_password_reset(reset_data: PasswordResetConfirm):
    """
    确认密码重置

    使用重置令牌设置新密码。

    **请求示例**:
    ```json
    {
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "new_password": "NewSecurePass123"
    }
    ```

    **响应示例**:
    ```json
    {
        "code": "SUCCESS",
        "message": "Password reset successfully",
        "data": null,
        "timestamp": 1733318400.123
    }
    ```

    **错误码**:
    - SUCCESS: 密码重置成功
    - INVALID_TOKEN: 重置令牌无效或已过期
    - INTERNAL_SERVER_ERROR: 服务器错误

    **HTTP状态码**:
    - 200: 重置成功
    - 400: 令牌无效
    - 500: 服务器错误
    """
    from app.core.security import verify_token
    from app.core.database import get_postgresql_session
    from sqlalchemy import text

    session = None
    try:
        # Verify reset token
        token_data = verify_token(reset_data.token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        # Check if token is for password reset
        if not hasattr(token_data, "purpose") or getattr(token_data, "purpose", None) != "password_reset":
            # For backward compatibility, check if 'purpose' is in payload
            import jwt

            try:
                payload = jwt.decode(reset_data.token, settings.secret_key, algorithms=[settings.algorithm])
                if payload.get("purpose") != "password_reset":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid token purpose",
                    )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token",
                )

        # Get user from token
        user_id = token_data.user_id
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload",
            )

        # Update password in database
        session = get_postgresql_session()
        hashed_password = get_password_hash(reset_data.new_password)

        update_query = text(
            """
            UPDATE users
            SET hashed_password = :hashed_password
            WHERE id = :user_id
            """
        )

        session.execute(update_query, {"user_id": user_id, "hashed_password": hashed_password})
        session.commit()

        # Log password reset
        log_query = text(
            """
            INSERT INTO user_audit_log (user_id, action, details)
            VALUES (:user_id, :action, :details)
            """
        )
        session.execute(
            log_query,
            {
                "user_id": user_id,
                "action": "password_reset_completed",
                "details": {"method": "token_reset"},
            },
        )
        session.commit()

        return create_success_response(
            data=None,
            message="Password reset successfully",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        if session:
            session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}",
        )

    finally:
        if session:
            session.close()
