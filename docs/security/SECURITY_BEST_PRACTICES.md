# MyStocks 项目安全最佳实践指南

## 概述

本文档为MyStocks量化交易数据管理系统提供安全开发最佳实践，旨在提升系统安全性，保护敏感数据，防范常见安全威胁。

---

## 1. 敏感数据管理

### 1.1 环境变量安全

#### ✅ 正确做法
```python
# 使用环境变量管理敏感信息
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'your-secret-key')

# 验证必需的环境变量
required_vars = ['DATABASE_PASSWORD', 'API_SECRET_KEY']
for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")
```

#### ❌ 错误做法
```python
# 硬编码敏感信息
DATABASE_PASSWORD = "password123"  # 不安全
API_SECRET_KEY = "sk-1234567890abcdef"  # 不安全
```

### 1.2 配置文件安全

#### 敏感文件命名规范
- `.env.example` - 环境变量模板（无真实值）
- `.env.local` - 本地开发环境（不被版本控制）
- `.env.production` - 生产环境（加密存储）

#### Git忽略规则
```gitignore
# 环境变量文件
.env
.env.local
.env.production
*.key
*.pem
*.p12
*.p8

# 配置文件
config.json
secrets.yml
secrets.yaml

# 数据库文件
*.db
*.sqlite
*.sqlite3
```

---

## 2. 数据库安全

### 2.1 连接安全

#### ✅ 正确做法
```python
# 使用连接池和SSL
import asyncpg
import ssl

ssl_context = ssl.create_default_context(cafile="/path/to/ca-certificates.crt")
conn = await asyncpg.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    ssl=ssl_context
)
```

#### ❌ 错误做法
```python
# 不安全的数据库连接
conn = sqlite3.connect("database.db")  # 无密码保护
```

### 2.2 SQL注入防护

#### ✅ 正确做法
```python
# 使用参数化查询
query = "SELECT * FROM stocks WHERE symbol = $1"
result = await conn.fetch(query, symbol)

# 使用ORM
stocks = await Stock.filter(symbol=symbol)
```

#### ❌ 错误做法
```python
# SQL注入风险
query = f"SELECT * FROM stocks WHERE symbol = '{symbol}'"  # 不安全
cursor.execute(query)
```

---

## 3. API安全

### 3.1 输入验证

#### ✅ 正确做法
```python
from pydantic import BaseModel, validator
from typing import Optional

class StockQuery(BaseModel):
    symbol: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    @validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z0-9]{6}$', v):
            raise ValueError('Invalid symbol format')
        return v

@app.get("/stocks/{symbol}")
async def get_stock_data(symbol: str, query: StockQuery):
    return await stock_service.get_data(symbol, query.start_date, query.end_date)
```

### 3.2 认证和授权

#### JWT Token安全
```python
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

async def verify_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## 4. 加密和密码学

### 4.1 密码存储

#### ✅ 正确做法
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

### 4.2 数据加密

#### AES加密
```python
from cryptography.fernet import Fernet

def encrypt_data(data: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()
```

---

## 5. 网络安全

### 5.1 HTTPS配置

#### ✅ 正确做法
```python
# 强制HTTPS重定向
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.mystocks.com"]
)
```

### 5.2 CORS配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mystocks.com", "https://www.mystocks.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 6. 日志安全

### 6.1 日志脱敏

```python
import logging

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # 脱敏敏感信息
        if hasattr(record, 'message'):
            record.message = self.mask_sensitive_data(record.message)
        return True

    def mask_sensitive_data(self, text):
        # 脱敏API密钥
        text = re.sub(r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                     r'api_key: "***MASKED***"', text, flags=re.IGNORECASE)
        return text

# 应用过滤器
logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())
```

### 6.2 日志安全配置

```python
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
}
```

---

## 7. 依赖安全管理

### 7.1 依赖版本固定

#### requirements.txt
```txt
# 固定具体版本
fastapi==0.114.0
uvicorn==0.30.0
pydantic==2.8.2
psycopg2-binary==2.9.9
cryptography==41.0.0
```

### 7.2 依赖安全扫描

```bash
# 定期运行安全扫描
pip install safety bandit
safety check
bandit -r src/
```

---

## 8. 错误处理安全

### 8.1 安全错误信息

#### ✅ 正确做法
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 500:
        # 生产环境不暴露详细错误
        error_id = str(uuid.uuid4())
        logger.error(f"Internal error [{error_id}]: {exc.detail}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "error_id": error_id}
        )
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
```

#### ❌ 错误做法
```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # 不安全的错误处理
    return {"error": f"Database connection failed: {exc}", "traceback": traceback.format_exc()}
```

---

## 9. 文件上传安全

### 9.1 文件验证

```python
import aiofiles
from pathlib import Path

ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.json'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/upload")
async def upload_file(file: UploadFile):
    # 检查文件扩展名
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    # 检查文件大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # 安全保存文件
    file_path = Path(f"uploads/{uuid.uuid4()}{file_extension}")
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    return {"filename": file.filename, "saved_as": str(file_path)}
```

---

## 10. 监控和审计

### 10.1 安全事件监控

```python
import structlog

logger = structlog.get_logger()

def log_security_event(event_type: str, user_id: str, details: dict = None):
    """记录安全事件"""
    logger.info(
        "security_event",
        event_type=event_type,
        user_id=user_id,
        ip_address=details.get('ip_address') if details else None,
        user_agent=details.get('user_agent') if details else None,
        timestamp=datetime.utcnow().isoformat()
    )

# 使用示例
log_security_event("failed_login", user_id="user123", details={"ip_address": "192.168.1.100"})
```

### 10.2 访问日志记录

```python
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        "request_completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 4),
        client_ip=request.client.host
    )

    return response
```

---

## 11. 部署安全

### 11.1 生产环境配置

#### Docker安全配置
```dockerfile
# 使用非root用户运行应用
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 移除开发依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y pip
```

#### Nginx安全配置
```nginx
server {
    listen 443 ssl http2;
    server_name mystocks.com;

    # SSL配置
    ssl_certificate /etc/ssl/certs/mystocks.crt;
    ssl_certificate_key /etc/ssl/private/mystocks.key;

    # 安全头部
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 隐藏Nginx版本
    server_tokens off;
}
```

---

## 12. 安全检查清单

### 部署前检查
- [ ] 所有敏感信息使用环境变量管理
- [ ] 数据库连接使用SSL加密
- [ ] API接口实现输入验证
- [ ] 使用参数化查询防止SQL注入
- [ ] 实现适当的认证和授权机制
- [ ] 配置HTTPS和SSL/TLS
- [ ] 设置安全的CORS策略
- [ ] 配置安全的HTTP头
- [ ] 实现日志脱敏
- [ ] 运行依赖安全扫描
- [ ] 检查文件上传安全
- [ ] 配置安全监控和告警

### 定期检查
- [ ] 更新依赖包版本
- [ ] 运行安全漏洞扫描
- [ ] 审查访问日志
- [ ] 检查备份文件安全
- [ ] 测试安全控制措施
- [ ] 评估权限管理
- [ ] 检查敏感数据存储
- [ ] 验证网络配置

---

## 13. 应急响应

### 安全事件处理流程
1. **立即响应**
   - 隔离受影响系统
   - 保护现场证据
   - 通知相关人员

2. **评估影响**
   - 确定事件范围
   - 评估数据泄露风险
   - 分析攻击向量

3. **实施修复**
   - 修复安全漏洞
   - 加强安全控制
   - 恢复系统正常

4. **事后总结**
   - 分析事件原因
   - 更新安全策略
   - 改进防护措施

---

## 14. 工具和资源

### 推荐安全工具
- **静态分析**: Bandit, Semgrep
- **依赖扫描**: Safety, pip-audit
- **密码学**: Cryptography库
- **认证**: Authlib, PyJWT
- **加密**: PyCryptodome
- **输入验证**: Pydantic, Marshmallow

### 安全资源
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Python安全**: https://python-security.readthedocs.io/
- **FastAPI安全**: https://fastapi.tiangolo.com/tutorial/security/

---

**文档版本**: v1.0
**更新日期**: 2025-11-14
**维护者**: MyStocks开发团队
**审核状态**: 已审核
