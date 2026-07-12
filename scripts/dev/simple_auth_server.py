#!/usr/bin/env python3
"""简单的认证API服务器 - 用于E2E测试"""

import hashlib
import os
import time
from datetime import datetime, timedelta

import jwt
import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# 创建FastAPI应用
app = FastAPI(title="MyStocks Auth API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT密钥
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-e2e-testing-only")
JWT_ALGORITHM = "HS256"

# 测试用户数据库
TEST_USERS = {
    "admin": {
        "password": hashlib.md5(b"admin123").hexdigest(),
        "role": "admin",
        "username": "admin",
    },
    "user": {
        "password": hashlib.md5(b"user123").hexdigest(),
        "role": "user",
        "username": "user",
    },
}


# ==================== 数据模型 ====================


class LoginRequest(BaseModel):
    username: str
    password: str


class APIResponse(BaseModel):
    success: bool
    code: int
    message: str
    data: dict | None
    timestamp: str
    request_id: str
    errors: dict | None = None


# ==================== 辅助函数 ====================


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """创建JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def make_response(success: bool, code: int, message: str, data: dict = None) -> dict:
    """创建标准响应"""
    return {
        "success": success,
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": f"test-{int(time.time())}",
        "errors": None,
    }


# ==================== 健康检查 ====================


@app.get("/health")
async def health_check():
    """健康检查"""
    return make_response(
        True,
        200,
        "系统健康检查完成",
        {
            "service": "mystocks-web-api",
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
        },
    )


# ==================== 认证API ====================


@app.post("/api/auth/login")
async def login(request: LoginRequest, response: Response):
    """用户登录"""
    username = request.username
    password = request.password

    # 验证用户
    user = TEST_USERS.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 验证密码
    password_hash = hashlib.md5(password.encode()).hexdigest()
    if user["password"] != password_hash:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 生成token
    token_data = {
        "sub": username,
        "role": user["role"],
        "username": user["username"],
    }
    access_token = create_access_token(token_data)

    # 返回响应
    return make_response(
        True,
        200,
        "登录成功",
        {
            "token": access_token,
            "user": {
                "username": user["username"],
                "role": user["role"],
            },
        },
    )


@app.post("/api/auth/logout")
async def logout():
    """用户登出"""
    return make_response(True, 200, "登出成功", None)


@app.get("/api/auth/me")
async def get_current_user():
    """获取当前用户信息"""
    return make_response(
        True,
        200,
        "获取用户信息成功",
        {
            "username": "admin",
            "role": "admin",
        },
    )


# ==================== 其他API ====================


@app.get("/api/system/status")
async def system_status():
    """系统状态"""
    return make_response(
        True,
        200,
        "获取系统状态成功",
        {
            "status": "running",
            "uptime": time.time(),
        },
    )


# ==================== 主程序 ====================

if __name__ == "__main__":
    backend_port = int(os.getenv("BACKEND_PORT", "8020"))
    print("🚀 启动简单认证API服务器...")
    print(f"📍 地址: http://localhost:{backend_port}")
    print("👥 测试账号:")
    print("   - admin / admin123")
    print("   - user / user123")
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=backend_port,
        log_level="info",
    )
