"""
安全认证和权限管理
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import bcrypt
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

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
        password_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        # 记录错误但不抛出异常
        print(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """生成密码哈希 - 使用纯bcrypt"""
    # bcrypt has a 72-byte password length limit, truncate if necessary
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

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

# 预先计算密码哈希,避免每次请求时重新计算
# admin123 的哈希
ADMIN_PASSWORD_HASH = "$2b$12$JzXL46bSlDVnMJlDvkV7q.u5gY6pVEYNV18otWdH8FwHD3uRcV1ia"
# user123 的哈希
USER_PASSWORD_HASH = "$2b$12$8aBh8ytBXEX0B0okxvYqPO428xzvnJlnA6c.q/ua6BS6z33ZP3WnK"

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    验证用户身份

    这里应该连接数据库查询用户信息
    暂时使用模拟数据
    """
    # TODO: 实现数据库查询逻辑
    # 临时模拟用户数据 - 使用预先计算好的密码哈希
    users_db = {
        "admin": {
            "id": 1,
            "username": "admin",
            "email": "admin@mystocks.com",
            "hashed_password": ADMIN_PASSWORD_HASH,
            "role": "admin",
            "is_active": True
        },
        "user": {
            "id": 2,
            "username": "user",
            "email": "user@mystocks.com",
            "hashed_password": USER_PASSWORD_HASH,
            "role": "user",
            "is_active": True
        }
    }

    user = users_db.get(username)
    if not user:
        return None

    user_in_db = UserInDB(**user)

    if not verify_password(password, user_in_db.hashed_password):
        return None

    return user_in_db

def check_permission(user_role: str, required_role: str) -> bool:
    """检查用户权限"""
    role_hierarchy = {
        "user": 0,
        "admin": 1
    }

    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前用户
    依赖注入，用于路由保护
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception

    # TODO: 从数据库查询用户信息
    # 临时模拟用户数据
    users_db = {
        "admin": {
            "id": 1,
            "username": "admin",
            "email": "admin@mystocks.com",
            "role": "admin",
            "is_active": True
        },
        "user": {
            "id": 2,
            "username": "user",
            "email": "user@mystocks.com",
            "role": "user",
            "is_active": True
        }
    }

    user_data = users_db.get(token_data.username)
    if user_data is None:
        raise credentials_exception

    return User(**user_data)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user