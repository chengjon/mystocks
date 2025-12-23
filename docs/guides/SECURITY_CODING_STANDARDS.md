# MyStocks 安全编码标准

## 概述

本文档定义了 MyStocks 项目的安全编码标准和最佳实践。所有开发人员必须遵循这些标准以确保应用的安全性。

## 核心原则

### 1. 最小权限原则
- 只授予必要的权限
- 默认拒绝，明确允许
- 定期审查权限分配

### 2. 防御性编程
- 验证所有输入
- 使用安全的数据结构
- 实现错误处理机制

### 3. 安全默认设置
- 使用安全的默认配置
- 禁用不必要的服务
- 定期更新安全设置

## Python 编码标准

### 1. 输入验证

```python
# ✅ 正确：严格验证
def validate_symbol(symbol: str) -> bool:
    if not symbol or len(symbol) > 10:
        return False
    return symbol.isalnum() and symbol.isupper()

# ❌ 错误：直接使用用户输入
def process_symbol(symbol):
    # 没有验证就直接使用
    query = f"SELECT * FROM stocks WHERE symbol = '{symbol}'"
    execute_query(query)
```

### 2. SQL 安全

```python
# ✅ 正确：使用参数化查询
from psycopg2 import sql

def get_stock_data(symbol: str):
    query = sql.SQL("SELECT * FROM stocks WHERE symbol = %s")
    cursor.execute(query, [symbol])

# ✅ 正确：使用 ORM
def get_stock_orm(symbol: str):
    return Stock.query.filter(Stock.symbol == symbol).first()

# ❌ 错误：字符串格式化
def get_stock_unsafe(symbol: str):
    query = "SELECT * FROM stocks WHERE symbol = '{}'".format(symbol)
    cursor.execute(query)
```

### 3. 命令注入防护

```python
# ✅ 正确：白名单验证
ALLOWED_COMMANDS = ['validate', 'check', 'list']

def safe_command(cmd: str, *args):
    if cmd not in ALLOWED_COMMANDS:
        raise ValueError(f"Command {cmd} not allowed")

    # 安全执行
    subprocess.run([cmd] + list(args), check=True)

# ❌ 错误：直接执行用户输入
def unsafe_command(user_input):
    subprocess.run(user_input, shell=True)  # 危险！
```

### 4. 密码处理

```python
# ✅ 正确：使用 bcrypt
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ❌ 错误：使用明文或弱哈希
import hashlib

def weak_hash(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()  # 不安全！
```

### 5. 文件操作安全

```python
# ✅ 正确：限制文件路径
import os
from pathlib import Path

def safe_file_upload(filename: str, content: bytes):
    # 验证文件名
    if not filename.isalnum() and '_' not in filename:
        raise ValueError("Invalid filename")

    # 限制目录
    upload_dir = Path("/uploads")
    filepath = upload_dir / filename

    # 防止路径遍历
    if not str(filepath).startswith(str(upload_dir)):
        raise ValueError("Invalid file path")

    # 写入文件
    with open(filepath, 'wb') as f:
        f.write(content)

# ❌ 错误：路径遍历漏洞
def unsafe_file_upload(filename, content):
    with open(filename, 'wb') as f:  # 危险！
        f.write(content)
```

### 6. 错误处理

```python
# ✅ 正确：不泄露敏感信息
import logging

def process_request(request_data):
    try:
        # 处理逻辑
        result = sensitive_operation(request_data)
        return result
    except Exception as e:
        # 记录详细错误到日志
        logging.error(f"Processing failed: {str(e)}")
        # 向用户返回通用错误
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# ❌ 错误：泄露敏感信息
def unsafe_process(request_data):
    try:
        result = sensitive_operation(request_data)
        return result
    except Exception as e:
        # 向用户返回内部错误详情
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"  # 泄露信息！
        )
```

## JavaScript/TypeScript 编码标准

### 1. XSS 防护

```typescript
// ✅ 正确：使用模板字符串
function sanitizeInput(input: string): string {
    return input
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function renderUserContent(content: string) {
    const safeContent = sanitizeInput(content);
    return `<div>${safeContent}</div>`;
}

// ✅ 正确：使用 DOM 操作 API
function createSafeElement(text: string): HTMLElement {
    const div = document.createElement('div');
    div.textContent = text;  // 自动转义
    return div;
}

// ❌ 错误：innerHTML 直接赋值
function unsafeRender(text: string): void {
    document.getElementById('output').innerHTML = text;  // XSS 风险！
}
```

### 2. API 安全

```typescript
// ✅ 正确：实施 CORS 策略
const corsOptions = {
  origin: ['https://mystocks.com', 'https://app.mystocks.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400
};

app.use(cors(corsOptions));

// ✅ 正确：实施速率限制
import rateLimit from 'express-rate-limit';

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 5, // 限制每个 IP 5 次尝试
  message: 'Too many authentication attempts'
});

app.post('/api/auth/login', authLimiter, loginHandler);
```

### 3. JWT 安全

```typescript
// ✅ 正确：安全的 JWT 配置
import jwt from 'jsonwebtoken';

const jwtOptions = {
  expiresIn: '24h',
  algorithm: 'HS256' as const,
  issuer: 'mystocks-api',
  audience: 'mystocks-clients'
};

function generateToken(payload: any): string {
  return jwt.sign(payload, process.env.JWT_SECRET!, jwtOptions);
}

function verifyToken(token: string): any {
  return jwt.verify(token, process.env.JWT_SECRET!, jwtOptions);
}

// ❌ 错误：不安全的 JWT 配置
function unsafeGenerateToken(payload: any): string {
  return jwt.sign(payload, process.env.JWT_SECRET!, {
    expiresIn: '7d'  // 过期时间过长
  });
}
```

## 数据库安全

### 1. 连接安全

```python
# ✅ 正确：使用 SSL 连接
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mystocks',
        'USER': 'mystocks_user',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'db.example.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
            'sslrootcert': '/path/to/ca-cert.pem'
        }
    }
}
```

### 2. ORM 使用

```python
# ✅ 正确：使用 Django ORM
from django.db import models
from django.core.validators import RegexValidator

class Stock(models.Model):
    symbol = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(r'^[A-Z]{1,10}$', 'Invalid stock symbol')
        ],
        unique=True
    )
    # 其他字段...

    @classmethod
    def get_by_symbol(cls, symbol: str):
        return cls.objects.get(symbol=symbol)

# ❌ 锕误：直接 SQL 操作
def get_stock_unsafe(symbol: str):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM stocks WHERE symbol = '%s'" % symbol)
    return cursor.fetchone()
```

## Web 安全

### 1. HTTP 头设置

```python
# ✅ 正确：安全 HTTP 头
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://trusted.cdn.com; "
        "style-src 'self' 'unsafe-inline' https://trusted.cdn.com; "
        "img-src 'self' data: https://images.cdn.com; "
        "font-src 'self' https://fonts.cdn.com; "
        "connect-src 'self' https://api.mystocks.com"
    )

    # 其他安全头
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=()"

    return response
```

### 2. CSRF 保护

```python
# ✅ 正确：CSRF 保护
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# 强制 HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

# 受信任的主机
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["mystocks.com", "*.mystocks.com", "localhost"]
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mystocks.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 密码策略

### 1. 密码复杂性要求

```python
import re

def validate_password_strength(password: str) -> bool:
    """验证密码强度"""
    if len(password) < 12:
        return False

    # 至少一个大写字母
    if not re.search(r'[A-Z]', password):
        return False

    # 至少一个小写字母
    if not re.search(r'[a-z]', password):
        return False

    # 至少一个数字
    if not re.search(r'\d', password):
        return False

    # 至少一个特殊字符
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True

# 密码历史检查
def check_password_history(user_id: int, new_password: str) -> bool:
    """检查密码是否在历史中"""
    old_passwords = get_user_password_history(user_id)
    password_hash = hash_password(new_password)

    return password_hash not in old_passwords
```

### 2. 会话管理

```python
# ✅ 正确：安全的会话配置
SESSION_SETTINGS = {
    'session_cookie_name': 'mystocks_session',
    'session_cookie_httponly': True,
    'session_cookie_secure': True,  # 仅 HTTPS
    'session_cookie_samesite': 'Lax',
    'session_lifetime': 3600,  # 1 小时
    'session_regeneration_interval': 600,  # 10 分钟
    'session_key_prefix': 'mystocks:',
}

# ✅ 正确：会话固定防护
def regenerate_session_on_login(user_id: int):
    session = get_session()
    session.regenerate()  # 重新生成 session ID
    session['user_id'] = user_id
    session['ip_address'] = request.remote_addr
    session['user_agent'] = request.headers.get('User-Agent')
```

## 测试安全

### 1. 单元测试中的安全测试

```python
import pytest
from unittest.mock import patch
from src.security.validators import validate_email

def test_email_validation():
    # 有效邮箱
    assert validate_email("test@example.com") == True

    # 无效邮箱
    assert validate_email("invalid-email") == False
    assert validate_email("") == False
    assert validate_email("not-an-email@") == False

def test_sql_injection_protection():
    # 确保查询使用参数化
    with patch('src.database.execute_query') as mock_execute:
        mock_execute.return_value = []
        get_user_by_username("admin' OR 1=1--")

        # 验证查询使用了参数化
        mock_execute.assert_called_once()
        args, kwargs = mock_execute.call_args
        assert "' OR 1=1--" not in args[0]  # SQL 注入被阻止
```

### 2. 集成安全测试

```python
def test_authentication_bypass():
    """测试认证绕过攻击"""
    # 登录获取 token
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "correct_password"
    })

    token = response.json()["access_token"]

    # 尝试使用无效 token
    response = client.get("/api/admin/users", headers={
        "Authorization": f"Bearer invalid_token"
    })

    assert response.status_code == 401

def test_rate_limiting():
    """测试速率限制"""
    # 多次尝试失败登录
    for i in range(6):
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "wrong_password"
        })

        if i >= 5:  # 第5次后应该被限制
            assert response.status_code == 429
```

## 安全审计清单

### 1. 代码审查清单

- [ ] 所有用户输入是否经过验证？
- [ ] 是否使用参数化查询？
- [ ] 密码是否安全存储？
- [ ] 是否实现适当的访问控制？
- [ ] 错误信息是否不泄露敏感信息？
- [ ] 是否使用 HTTPS？
- [ ] 安全头是否正确设置？
- [ ] 是否实施 CSRF 保护？
- [ ] 文件上传是否安全？
- [ ] 会话管理是否安全？

### 2. 部署安全清单

- [ ] 生产环境禁用调试模式
- [ ] 所有依赖项是否已更新？
- [ ] 环境变量是否安全？
- [ ] 服务器是否配置安全？
- [ ] 是否配置了监控和日志？
- [ ] 是否有备份和恢复计划？
- [ ] 是否进行了安全测试？

## 工具和检查

### 1. 自动化检查

```bash
# Bandit 扫描
bandit -r src/ -f json -o bandit-report.json

# Safety 检查
safety check --json --output safety-report.json

# Semgrep 扫描
semgrep --config auto --json -o semgrep-report.json src/
```

### 2. 预提交钩子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: bandit-scan
        name: Bandit security scan
        entry: bandit
        language: python
        files: \.py$
        args: [-r, -f, json, -o, bandit-report.json]
      - id: safety-check
        name: Safety dependency check
        entry: safety
        language: python
        args: [check, --json]
        pass_filenames: false
      - id: semgrep
        name: Semgrep security scan
        entry: semgrep
        language: python
        args: [--config, auto, --json]
```

## 违规处理

### 1. 严重违规（Critical/High）
- 立即修复
- 代码审查
- 安全培训
- 记录违规

### 2. 中等违规（Medium）
- 1 周内修复
- 代码审查
- 记录违规

### 3. 轻微违规（Low）
- 记录违规
- 下次版本修复

## 持续改进

### 1. 定期审查
- 每月审查安全标准
- 更新工具和检查
- 分享最佳实践

### 2. 威胁情报
- 跟踪安全公告
- 参与安全社区
- 定期更新防御措施

### 3. 安全培训
- 新员工入职培训
- 定期安全意识培训
- 漏洞响应演练