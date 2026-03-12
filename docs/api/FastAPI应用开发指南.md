# FastAPI应用开发指南
## 步骤清晰 • 重点突出 • 举例明确

本文档基于FastAPI官方源码分析，提供实用的FastAPI应用开发指导，帮助其他项目快速使用FastAPI开发相关功能。

---

## 📋 目录

1. [项目初始化](#1-项目初始化)
2. [核心应用结构](#2-核心应用结构)
3. [数据模型与验证](#3-数据模型与验证)
4. [路由系统](#4-路由系统)
5. [依赖注入](#5-依赖注入)
6. [异步编程](#6-异步编程)
7. [错误处理](#7-错误处理)
8. [安全认证](#8-安全认证)
9. [测试策略](#9-测试策略)
10. [部署配置](#10-部署配置)

---

## 1. 项目初始化

### 步骤 1.1: 创建项目结构

```
my_api_project/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI应用入口
│   ├── config.py        # 配置管理
│   ├── models/          # Pydantic数据模型
│   ├── routers/         # API路由
│   ├── dependencies.py  # 依赖注入
│   ├── middleware/      # 自定义中间件
│   └── database.py      # 数据库连接
├── tests/               # 测试用例
├── requirements.txt     # 依赖列表
└── .env                # 环境变量
```

### 步骤 1.2: 安装核心依赖

```bash
# 基础依赖
pip install "fastapi[standard]" uvicorn[standard]

# 数据库相关
pip install sqlalchemy asyncpg alembic

# 认证相关
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

# 测试相关
pip install pytest pytest-asyncio httpx
```

### 步骤 1.3: 基础配置文件

```python
# config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "My API"
    app_version: str = "1.0.0"
    debug: bool = False

    # 数据库配置
    database_url: str = "postgresql+asyncpg://user:pass@localhost/db"

    # 安全配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS配置
    allowed_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 2. 核心应用结构

### 步骤 2.1: 主应用文件

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .config import settings
from .routers import users, items
from .database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    await init_db()
    yield
    # 关闭时执行（如果需要）

# 创建FastAPI实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由模块
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
```

### 步骤 2.2: 数据库连接配置

```python
# database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=0
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 基础模型类
class Base(DeclarativeBase):
    pass

# 依赖注入：获取数据库会话
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 初始化数据库
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

---

## 3. 数据模型与验证

### 步骤 3.1: Pydantic模型定义

```python
# models/user.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")

class UserCreate(UserBase):
    """创建用户模型"""
    password: str = Field(..., min_length=8, description="密码")

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v

class UserUpdate(BaseModel):
    """更新用户模型"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str

class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
```

### 步骤 3.2: 数据库模型定义

```python
# models/database.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
```

---

## 4. 路由系统

### 步骤 4.1: 用户路由模块

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db_session
from ..models.user import UserCreate, UserUpdate, UserResponse, UserLogin
from ..models.database import User
from ..services.auth import AuthService, get_current_user
from ..services.user import UserService

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    注册新用户

    - **email**: 用户邮箱（必须唯一）
    - **username**: 用户名（必须唯一，3-50字符）
    - **password**: 密码（至少8位，包含大小写字母和数字）
    """
    service = UserService(db)

    # 检查用户是否已存在
    existing_user = await service.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 创建用户
    user = await service.create_user(user_data)
    return user

@router.post("/login")
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db_session)
):
    """
    用户登录

    返回JWT访问令牌
    """
    auth_service = AuthService(db)
    result = await auth_service.authenticate(login_data.username, login_data.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {
        "access_token": result["access_token"],
        "token_type": "bearer",
        "expires_in": result["expires_in"]
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """更新当前用户信息"""
    service = UserService(db)
    updated_user = await service.update_user(current_user.id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return updated_user

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    获取用户列表（管理员权限）

    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    """
    # 这里可以添加管理员权限检查
    service = UserService(db)
    users = await service.get_users(skip=skip, limit=limit)
    return users
```

### 步骤 4.2: 物品路由模块

```python
# routers/items.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db_session
from ..models.item import ItemCreate, ItemUpdate, ItemResponse, ItemQuery
from ..services.auth import get_current_user
from ..services.item import ItemService
from ..models.database import User

router = APIRouter()

@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    创建新物品

    需要认证用户
    """
    service = ItemService(db)
    item = await service.create_item(item_data, owner_id=current_user.id)
    return item

@router.get("/", response_model=List[ItemResponse])
async def get_items(
    q: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
    max_price: Optional[float] = Query(None, ge=0, description="最高价格"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    获取物品列表

    支持多种筛选和排序选项
    """
    query_params = ItemQuery(
        q=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit
    )

    service = ItemService(db)
    items = await service.get_items(query_params)
    return items

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取指定物品详情"""
    service = ItemService(db)
    item = await service.get_item_by_id(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )

    return item

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """更新物品信息（仅所有者）"""
    service = ItemService(db)

    # 检查权限
    item = await service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )

    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此物品"
        )

    updated_item = await service.update_item(item_id, item_update)
    return updated_item

@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """删除物品（仅所有者）"""
    service = ItemService(db)

    # 检查权限
    item = await service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )

    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此物品"
        )

    await service.delete_item(item_id)
```

---

## 5. 依赖注入

### 步骤 5.1: 认证依赖

```python
# services/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from passlib.context import CryptContext

from ..database import get_db_session
from ..config import settings
from ..models.database import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    async def authenticate(self, username: str, password: str) -> Optional[dict]:
        """用户认证"""
        # 这里简化了实际逻辑，实际应该查询数据库
        if username == "admin" and password == "password":
            access_token = self.create_access_token(data={"sub": username})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.access_token_expire_minutes * 60
            }
        return None

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        """获取当前用户"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        # 实际应该从数据库查询用户
        user = await self._get_user_by_username(username)
        if user is None:
            raise credentials_exception

        return user

    async def _get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户（示例）"""
        # 实际实现应该查询数据库
        if username == "admin":
            return User(id=1, username=username, email="admin@example.com", is_active=True)
        return None

# 全局依赖：获取当前用户
get_current_user = AuthService(None).get_current_user

# 管理员权限依赖
async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """获取管理员用户"""
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user
```

### 步骤 5.2: 业务服务依赖

```python
# dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from .database import get_db_session
from .services.user import UserService
from .services.item import ItemService

# 用户服务依赖
async def get_user_service(db: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(db)

# 物品服务依赖
async def get_item_service(db: AsyncSession = Depends(get_db_session)) -> ItemService:
    return ItemService(db)

# 分页参数依赖
class PaginationParams:
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100
    ):
        self.skip = max(0, skip)
        self.limit = min(1000, max(1, limit))

# 搜索参数依赖
class SearchParams:
    def __init__(
        self,
        q: str = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        self.q = q
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()

        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "desc"
```

---

## 6. 异步编程

### 步骤 6.1: 异步服务层

```python
# services/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from ..models.user import UserCreate, UserUpdate, UserResponse
from ..models.database import User
from .auth import AuthService

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth = AuthService(db)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """创建用户"""
        # 密码哈希
        hashed_password = self.auth.get_password_hash(user_data.password)

        # 创建数据库记录
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        return UserResponse.from_orm(db_user)

    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        """更新用户信息"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        # 更新字段
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        await self.db.commit()
        await self.db.refresh(db_user)

        return UserResponse.from_orm(db_user)

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """获取用户列表"""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        users = result.scalars().all()
        return [UserResponse.from_orm(user) for user in users]
```

### 步骤 6.2: 异步任务处理

```python
# services/background.py
import asyncio
from typing import Callable, Any
from fastapi import BackgroundTasks
import aiofiles
import logging

logger = logging.getLogger(__name__)

class BackgroundTaskService:
    def __init__(self):
        self.tasks = []

    def send_welcome_email(self, email: str, username: str):
        """发送欢迎邮件（后台任务）"""
        # 模拟邮件发送
        logger.info(f"发送欢迎邮件给 {email}")
        # 实际可以集成邮件服务API

    def generate_user_report(self, user_id: int):
        """生成用户报告（后台任务）"""
        # 模拟耗时操作
        logger.info(f"开始为用户 {user_id} 生成报告")

        # 这里可以执行数据库查询、文件操作等
        asyncio.sleep(2)  # 模拟耗时操作

        # 保存报告到文件
        report_content = f"用户 {user_id} 的报告内容..."

        # 异步文件写入
        async def save_report():
            async with aiofiles.open(f"reports/user_{user_id}_report.txt", "w") as f:
                await f.write(report_content)

        # 在新的事件循环中执行异步操作
        asyncio.run(save_report())
        logger.info(f"用户 {user_id} 报告生成完成")

    def cleanup_old_files(self):
        """清理旧文件（维护任务）"""
        logger.info("开始清理旧文件")
        # 实际的文件清理逻辑

# 在路由中使用后台任务
async def register_user_with_welcome(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """注册用户并发送欢迎邮件"""
    service = UserService(db)
    bg_service = BackgroundTaskService()

    # 创建用户
    user = await service.create_user(user_data)

    # 添加后台任务
    background_tasks.add_task(
        bg_service.send_welcome_email,
        user.email,
        user.username
    )
    background_tasks.add_task(
        bg_service.generate_user_report,
        user.id
    )

    return user
```

---

## 7. 错误处理

### 步骤 7.1: 自定义异常处理器

```python
# exceptions/handlers.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    """自定义API异常基类"""
    def __init__(self, message: str, status_code: int = 500, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)

class NotFoundError(APIException):
    """资源未找到异常"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource}未找到"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, 404)

class PermissionError(APIException):
    """权限不足异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, 403)

class ValidationError(APIException):
    """数据验证异常"""
    def __init__(self, message: str, detail: str = None):
        super().__init__(message, 422, detail)

def setup_exception_handlers(app: FastAPI):
    """设置异常处理器"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """处理HTTP异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求验证异常"""
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "请求数据验证失败",
                "detail": exc.errors(),
                "body": exc.body,
                "status_code": 422,
                "path": request.url.path
            }
        )

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """处理自定义API异常"""
        logger.error(f"API异常: {exc.message} - 路径: {request.url.path}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "detail": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理未捕获的通用异常"""
        logger.error(f"未处理的异常: {str(exc)} - 路径: {request.url.path}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "服务器内部错误",
                "detail": str(exc) if app.debug else "请联系管理员",
                "status_code": 500,
                "path": request.url.path
            }
        )
```

### 步骤 7.2: 在主应用中使用异常处理器

```python
# main.py（更新）
from .exceptions.handlers import setup_exception_handlers

# 创建FastAPI实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 设置异常处理器
setup_exception_handlers(app)
```

---

## 8. 安全认证

### 步骤 8.1: 完整的认证流程

```python
# security/password.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

# security/jwt.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ..config import settings

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise ValueError("无效的令牌")
```

### 步骤 8.2: 权限控制系统

```python
# security/permissions.py
from enum import Enum
from typing import List, Set
from fastapi import HTTPException, status

class Permission(Enum):
    """权限枚举"""
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    READ_ITEMS = "read:items"
    WRITE_ITEMS = "write:items"
    DELETE_ITEMS = "delete:items"
    ADMIN = "admin"

class Role:
    """角色定义"""
    ADMIN: Set[Permission] = {
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_ITEMS,
        Permission.WRITE_ITEMS,
        Permission.DELETE_ITEMS,
        Permission.ADMIN
    }

    USER: Set[Permission] = {
        Permission.READ_ITEMS,
        Permission.WRITE_ITEMS
    }

    GUEST: Set[Permission] = {
        Permission.READ_ITEMS
    }

def check_permissions(user_permissions: List[Permission], required_permissions: List[Permission]):
    """检查用户权限"""
    user_perms_set = set(user_permissions)
    required_perms_set = set(required_permissions)

    if not required_perms_set.issubset(user_perms_set):
        missing_perms = required_perms_set - user_perms_set
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，缺少权限: {', '.join(p.value for p in missing_perms)}"
        )

# 权限依赖装饰器
def require_permissions(permissions: List[Permission]):
    """权限检查依赖"""
    def dependency(current_user = Depends(get_current_user)):
        # 这里简化了逻辑，实际应该查询用户的角色和权限
        if current_user.username == "admin":
            user_permissions = list(Role.ADMIN)
        else:
            user_permissions = list(Role.USER)

        check_permissions(user_permissions, permissions)
        return current_user

    return dependency

# 使用示例
@router.get("/admin/users")
async def get_users_admin(
    current_user: User = Depends(require_permissions([Permission.READ_USERS]))
):
    """需要用户读取权限"""
    pass
```

---

## 9. 测试策略

### 步骤 9.1: 测试配置

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db_session
from app.config import settings

# 测试数据库URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """创建测试数据库会话"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session

@pytest.fixture
async def client(test_session):
    """创建测试客户端"""

    # 覆盖数据库依赖
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # 清理依赖覆盖
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123",
        "full_name": "Test User"
    }

@pytest.fixture
def sample_item_data():
    """示例物品数据"""
    return {
        "name": "Test Item",
        "description": "This is a test item",
        "price": 99.99,
        "category": "electronics"
    }
```

### 步骤 9.2: API测试用例

```python
# tests/test_users.py
import pytest
from httpx import AsyncClient

class TestUsersAPI:
    """用户API测试"""

    async def test_register_user_success(self, client: AsyncClient, sample_user_data):
        """测试用户注册成功"""
        response = await client.post("/api/v1/users/register", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()

        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert data["full_name"] == sample_user_data["full_name"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # 确保密码不返回

    async def test_register_duplicate_email(self, client: AsyncClient, sample_user_data):
        """测试重复邮箱注册"""
        # 第一次注册
        await client.post("/api/v1/users/register", json=sample_user_data)

        # 第二次注册相同邮箱
        response = await client.post("/api/v1/users/register", json=sample_user_data)

        assert response.status_code == 400
        assert "邮箱已被注册" in response.json()["detail"]

    async def test_register_invalid_email(self, client: AsyncClient):
        """测试无效邮箱注册"""
        invalid_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "TestPass123"
        }

        response = await client.post("/api/v1/users/register", json=invalid_data)
        assert response.status_code == 422

    async def test_login_success(self, client: AsyncClient, sample_user_data):
        """测试登录成功"""
        # 先注册用户
        await client.post("/api/v1/users/register", json=sample_user_data)

        # 登录
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }

        response = await client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """测试登录凭据无效"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }

        response = await client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 401

    async def test_get_current_user(self, client: AsyncClient, sample_user_data):
        """测试获取当前用户信息"""
        # 注册并登录
        await client.post("/api/v1/users/register", json=sample_user_data)

        login_response = await client.post("/api/v1/users/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 获取当前用户信息
        response = await client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """测试未授权获取当前用户信息"""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401

# tests/test_items.py
class TestItemsAPI:
    """物品API测试"""

    async def test_create_item_success(self, client: AsyncClient, sample_user_data, sample_item_data):
        """测试创建物品成功"""
        # 注册并登录
        await client.post("/api/v1/users/register", json=sample_user_data)

        login_response = await client.post("/api/v1/users/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 创建物品
        response = await client.post("/api/v1/items/", json=sample_item_data, headers=headers)

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == sample_item_data["name"]
        assert data["description"] == sample_item_data["description"]
        assert data["price"] == sample_item_data["price"]
        assert data["category"] == sample_item_data["category"]
        assert "id" in data
        assert "created_at" in data

    async def test_get_items_with_filters(self, client: AsyncClient):
        """测试带筛选条件的物品列表"""
        response = await client.get("/api/v1/items/?category=electronics&min_price=50")

        assert response.status_code == 200
        data = response.json()

        # 验证返回的是列表
        assert isinstance(data, list)
```

---

## 10. 部署配置

### 步骤 10.1: 生产环境配置

```python
# config/production.py
from pydantic_settings import BaseSettings
from typing import List

class ProductionSettings(BaseSettings):
    # 应用配置
    app_name: str = "Production API"
    debug: bool = False
    log_level: str = "INFO"

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # 数据库配置
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 30

    # 安全配置
    secret_key: str  # 必须从环境变量获取
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS配置
    allowed_origins: List[str] = ["https://yourdomain.com"]

    # Redis配置（用于缓存和会话）
    redis_url: str = "redis://localhost:6379/1"

    # 监控配置
    enable_metrics: bool = True
    metrics_port: int = 9090

    class Config:
        env_file = ".env.production"

# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
USER app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8020/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 步骤 10.2: Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8020"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/myapi
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapi
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

### 步骤 10.3: 启动脚本

```bash
#!/bin/bash
# scripts/start.sh

set -e

echo "启动FastAPI应用..."

# 检查环境变量
if [ -z "$SECRET_KEY" ]; then
    echo "错误: 必须设置SECRET_KEY环境变量"
    exit 1
fi

# 数据库迁移
echo "执行数据库迁移..."
alembic upgrade head

# 启动应用
echo "启动API服务器..."
exec uvicorn app.main:app \
    --host ${HOST:-0.0.0.0} \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-4} \
    --log-level ${LOG_LEVEL:-info}
```

---

## 🚀 快速开始模板

### 一键项目创建

```bash
# 1. 克隆模板
git clone https://github.com/your-repo/fastapi-template.git my-new-api
cd my-new-api

# 2. 设置环境变量
cp .env.example .env
# 编辑.env文件，设置必要的环境变量

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
alembic upgrade head

# 5. 启动开发服务器
uvicorn app.main:app --reload

# 6. 访问API文档
# http://localhost:8020/docs
```

### 核心特性总结

✅ **类型安全**: 基于Pydantic的强类型验证
✅ **异步支持**: 原生async/await支持
✅ **自动文档**: OpenAPI/Swagger自动生成
✅ **依赖注入**: 灵活的依赖管理系统
✅ **安全认证**: JWT、OAuth2等安全方案
✅ **测试友好**: 内置测试工具和模式
✅ **性能优化**: 高性能异步处理
✅ **生产就绪**: 完整的部署配置

---

## 📚 延伸阅读

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Pydantic文档](https://pydantic-docs.helpmanual.io/)
- [SQLAlchemy异步文档](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Uvicorn部署指南](https://www.uvicorn.org/deployment/)

---

**本指南基于FastAPI源码深度分析，提供了生产级别的开发模式和最佳实践。遵循这些步骤，可以快速构建高质量、可维护的FastAPI应用。**
