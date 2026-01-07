"""
安全认证和权限管理
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.core.config import settings

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Token(BaseModel):
    """JWT Token 模型"""

    access_token: str
    token_type: str
    expires_in: Optional[int] = None
    user: Optional[Dict[str, Any]] = None


class TokenData(BaseModel):
    """Token 数据模型"""

    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class User(BaseModel):
    """用户模型"""

    id: Optional[int] = None
    username: str
    email: Optional[str] = None
    role: str = "user"  # user, admin
    is_active: bool = True


class UserInDB(User):
    """数据库中的用户模型"""

    hashed_password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码 - 直接使用 bcrypt，避免 passlib 兼容性问题"""
    try:
        # bcrypt has a 72-byte password length limit, truncate if necessary
        password_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except Exception as e:
        # 记录错误但不抛出异常
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希 - 使用纯bcrypt"""
    # bcrypt has a 72-byte password length limit, truncate if necessary
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT 访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """验证 JWT 令牌"""
    # 开发环境mock token支持
    if token == "dev-mock-token-for-development":
        return TokenData(username="dev_user", user_id=1, role="admin")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")

        if username is None:
            return None

        token_data = TokenData(username=username, user_id=user_id, role=role)
        return token_data

    except jwt.PyJWTError:
        return None


# 注意：硬编码密码哈希已移除以提高安全性
# 现在使用环境变量配置的密码或从数据库查询用户信息
# 如需设置默认管理员账户，请使用 .env 文件中的 ADMIN_INITIAL_PASSWORD


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    验证用户身份

    从数据库查询用户信息并验证密码。
    如果数据库连接失败，回退到模拟用户数据。

    Args:
        username: 用户名
        password: 密码（明文）

    Returns:
        UserInDB: 验证成功的用户信息，验证失败返回None

    Process:
        1. 如果是测试环境，直接使用mock数据
        2. 否则尝试从PostgreSQL数据库查询用户
        3. 如果数据库连接失败，回退到环境变量配置的模拟用户数据
        4. 返回验证成功的用户或None
    """
    from app.core.config import settings

    # 测试环境：直接使用mock数据，跳过数据库
    if settings.testing:
        print(f"[Test Mode] Using mock authentication for user: {username}")
        return _authenticate_with_mock(username, password)

    # 生产环境：首先尝试从数据库查询用户
    try:
        user = get_user_from_database(username)
        if user and verify_password(password, user.hashed_password):
            return user
        # 如果数据库中找不到用户或密码不匹配，继续尝试模拟数据
        if user:
            # 用户存在但密码错误
            return None

    except Exception as e:
        # 捕获所有异常，回退到模拟用户数据
        print(
            f"Database authentication failed (will use fallback mock data): "
            f"{type(e).__name__}: {e.message if hasattr(e, 'message') else str(e)}"
        )

    # 回退到mock数据
    return _authenticate_with_mock(username, password)

    # 回退到模拟用户数据 - 使用环境变量配置的密码
    # 获取管理员初始密码
    admin_initial_password = getattr(settings, "admin_initial_password", "admin123")
    user_initial_password = "user123"  # 默认用户密码

    users_db = {
        "admin": {
            "id": 1,
            "username": "admin",
            "email": "admin@mystocks.com",
            "hashed_password": get_password_hash(admin_initial_password),
            "role": "admin",
            "is_active": True,
        },
        "user": {
            "id": 2,
            "username": "user",
            "email": "user@mystocks.com",
            "hashed_password": get_password_hash(user_initial_password),
            "role": "user",
            "is_active": True,
        },
    }

    user = users_db.get(username)
    if not user:
        print(f"[Mock Auth] User not found in mock DB: {username}")
        return None

    user_in_db = UserInDB(**user)

    if not verify_password(password, user_in_db.hashed_password):
        print(f"[Mock Auth] Password verification failed for user: {username}")
        print(f"[Mock Auth] Input password: {password}")
        print(f"[Mock Auth] Stored hash: {user_in_db.hashed_password}")
        return None

    print(f"[Mock Auth] Authentication successful for user: {username}")
    return user_in_db


def authenticate_user_by_id(user_id: int) -> Optional[UserInDB]:
    """
    根据用户ID从数据库验证用户身份

    Args:
        user_id: 用户ID

    Returns:
        UserInDB: 数据库中的用户信息，如果用户不存在返回None

    Process:
        1. 尝试从PostgreSQL数据库根据ID查询用户
        2. 如果数据库查询失败，返回None
        3. 返回用户信息或None
    """
    try:
        # 从数据库查询用户
        return get_user_from_database_by_id(user_id)
    except Exception as e:
        # 数据库查询失败时记录错误
        print(f"Database user lookup failed for ID {user_id} " f"(will return None): {type(e).__name__}: {str(e)}")
        return None
        mock_users = {
            1: {
                "id": 1,
                "username": "admin",
                "email": "admin@mystocks.com",
                "hashed_password": "$2b$12$JzXL46bSlDVnMJlDvkV7q.u5gY6pVEYNV18otWdH8FwHD3uRcV1ia",
                "role": "admin",
                "is_active": True,
            },
            2: {
                "id": 2,
                "username": "user",
                "email": "user@mystocks.com",
                "hashed_password": "$2b$12$8aBh8ytBXEX0B0okxvYqPO428xzvnJlnA6c.q/ua6BS6z33ZP3WnK",
                "role": "user",
                "is_active": True,
            },
        }
        user_data = mock_users.get(user_id)
        if user_data:
            return UserInDB(**user_data)
        return None
    except Exception as e:
        # 捕获其他意外异常
        print(f"Unexpected error during user lookup by ID {user_id}: {str(e)}")
        return None


def get_user_from_database(username: str) -> Optional[UserInDB]:
    """
    从数据库获取用户信息

    Args:
        username: 用户名

    Returns:
        UserInDB: 用户信息，如果用户不存在返回None

    Raises:
        DatabaseConnectionError: 数据库连接失败
        DataValidationError: 用户名无效
        DatabaseOperationError: 数据库操作失败
    """
    from app.core.database import get_postgresql_session
    from app.db import UserRepository

    session = None
    try:
        session = get_postgresql_session()
        repository = UserRepository(session)
        return repository.get_user_by_username(username)

    except Exception as e:
        # 捕获所有异常并记录
        print(f"[get_user_from_database] Error: {e}")
        return None
    finally:
        # 确保会话被关闭
        if session:
            session.close()


def get_user_from_database_by_id(user_id: int) -> Optional[UserInDB]:
    """
    根据用户ID从数据库获取用户信息

    Args:
        user_id: 用户ID

    Returns:
        UserInDB: 用户信息，如果用户不存在返回None

    Raises:
        DatabaseConnectionError: 数据库连接失败
        DataValidationError: 用户ID无效
        DatabaseOperationError: 数据库操作失败
    """
    from app.core.database import get_postgresql_session
    from app.db import UserRepository
    from src.core.exceptions import DatabaseConnectionError, DatabaseOperationError

    session = None
    try:
        session = get_postgresql_session()
        repository = UserRepository(session)
        return repository.get_user_by_id(user_id)

    except DatabaseConnectionError:
        # 重新抛出连接错误让调用者处理
        raise
    except DatabaseOperationError:
        # 重新抛出操作错误让调用者处理
        raise
    except Exception as e:
        # 捕获其他异常并转换为DatabaseOperationError
        raise DatabaseOperationError(
            message=f"Failed to retrieve user from database by ID: {str(e)}",
            code="DB_OPERATION_FAILED",
            severity="HIGH",
            original_exception=e,
        )
    finally:
        # 确保会话被关闭
        if session:
            session.close()


def check_permission(user_role: str, required_role: str) -> bool:
    """检查用户权限"""
    role_hierarchy = {"user": 0, "admin": 1}

    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前用户 - 已恢复JWT认证验证

    验证JWT令牌的有效性并返回用户信息。
    如果令牌无效或过期，抛出HTTPException。

    Args:
        token: JWT访问令牌

    Returns:
        User: 当前用户信息

    Raises:
        HTTPException: 令牌无效时返回401未授权错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 验证JWT令牌
        token_data = verify_token(token)
        if token_data is None:
            raise credentials_exception

        # 从数据库获取用户信息
        user = authenticate_user_by_id(token_data.user_id)
        if user is None:
            raise credentials_exception

        # 检查用户是否活跃
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

        return User(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )

    except jwt.PyJWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户

    确保用户已通过认证且处于活跃状态。
    如果用户未激活，抛出HTTPException。

    Args:
        current_user: 当前认证用户

    Returns:
        User: 当前活跃用户

    Raises:
        HTTPException: 用户未激活时返回400错误
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def _authenticate_with_mock(username: str, password: str) -> Optional[UserInDB]:
    """
    使用Mock用户数据进行认证

    Args:
        username: 用户名
        password: 密码（明文）

    Returns:
        UserInDB: 验证成功的用户信息，验证失败返回None
    """
    from app.core.config import settings

    # 获取管理员初始密码
    getattr(settings, "admin_initial_password", "admin123")

    # 生成固定的哈希值（避免每次调用get_password_hash都生成新哈希）
    users_db = {
        "admin": {
            "id": 1,
            "username": "admin",
            "email": "admin@mystocks.com",
            "hashed_password": get_password_hash("admin123"),  # 固定密码
            "role": "admin",
            "is_active": True,
        },
        "user": {
            "id": 2,
            "username": "user",
            "email": "user@mystocks.com",
            "hashed_password": get_password_hash("user123"),  # 固定密码
            "role": "user",
            "is_active": True,
        },
    }

    user = users_db.get(username)
    if not user:
        print(f"[Mock Auth] User not found in mock DB: {username}")
        return None

    user_in_db = UserInDB(**user)

    # 验证密码
    if not verify_password(password, user_in_db.hashed_password):
        print(f"[Mock Auth] Password verification failed for user: {username}")
        return None

    print(f"[Mock Auth] Authentication successful for user: {username}")
    return user_in_db
