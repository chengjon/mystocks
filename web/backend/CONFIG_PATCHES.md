# 问财功能配置补丁

## 📋 需要修改的文件补丁

本文档提供具体的代码补丁，用于更新现有配置文件以集成问财功能。

---

## 1. 更新 app/main.py

### 在导入部分添加

**位置**: 文件开头的导入部分

```python
# 现有导入
from app.api import (
    auth,
    data,
    indicators,
    market,
    metrics,
    system,
    tasks,
    tdx,
)

# ✅ 添加以下行
from app.api import wencai
```

### 在路由注册部分添加

**位置**: 在所有 `app.include_router()` 调用后

```python
# 现有路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(market.router, tags=["market"])
app.include_router(metrics.router, tags=["metrics"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(tdx.router, tags=["tdx"])

# ✅ 添加以下行
app.include_router(wencai.router)  # 包含前缀 /api/market/wencai
```

---

## 2. 更新 app/core/config.py

### 在 Settings 类中添加

**位置**: `class Settings(BaseSettings):` 内部，在其他配置项后

```python
class Settings(BaseSettings):
    # ... 现有配置项 ...

    # ========== 问财API配置 ==========
    WENCAI_TIMEOUT: int = Field(
        default=30,
        env="WENCAI_TIMEOUT",
        description="问财API请求超时时间（秒）"
    )
    WENCAI_RETRY_COUNT: int = Field(
        default=3,
        env="WENCAI_RETRY_COUNT",
        description="问财API请求失败重试次数"
    )
    WENCAI_DEFAULT_PAGES: int = Field(
        default=1,
        env="WENCAI_DEFAULT_PAGES",
        description="问财API默认获取页数"
    )
    WENCAI_AUTO_REFRESH: bool = Field(
        default=True,
        env="WENCAI_AUTO_REFRESH",
        description="是否启用自动刷新"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True
```

---

## 3. 更新 celeryconfig.py

### 在 beat_schedule 字典中添加

**位置**: `beat_schedule = { ... }` 内部

```python
from celery.schedules import crontab

beat_schedule = {
    # ... 现有任务 ...

    # ========== 问财定时任务 ==========
    'wencai-refresh-all-daily': {
        'task': 'wencai.scheduled_refresh_all',
        'schedule': crontab(hour=9, minute=0),  # 每天 09:00
        'args': (1,),  # pages=1
        'kwargs': {'active_only': True},
        'options': {
            'expires': 3600,  # 任务1小时后过期
        }
    },

    'wencai-cleanup-old-data-daily': {
        'task': 'wencai.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # 每天 02:00
        'args': (30,),  # days=30，保留30天数据
        'kwargs': {'dry_run': False},
        'options': {
            'expires': 7200,  # 任务2小时后过期
        }
    },

    # 可选：每小时获取统计信息
    'wencai-stats-hourly': {
        'task': 'wencai.stats',
        'schedule': crontab(minute=0),  # 每小时的0分
        'options': {
            'expires': 3600,
        }
    },
}
```

---

## 4. 更新 app/models/__init__.py

### 添加问财模型导入

**位置**: 文件中的导入部分

```python
# 现有导入
from app.models.market_data import FundFlow, ETFData, ChipRaceData, LongHuBangData

# ✅ 添加以下行
from app.models.wencai_data import WencaiQuery

__all__ = [
    "FundFlow",
    "ETFData",
    "ChipRaceData",
    "LongHuBangData",
    "WencaiQuery",  # 添加这行
]
```

---

## 5. 更新 .env （可选）

### 添加问财配置

**位置**: `.env` 文件末尾

```env
# ========== 问财API配置 ==========
WENCAI_TIMEOUT=30
WENCAI_RETRY_COUNT=3
WENCAI_DEFAULT_PAGES=1
WENCAI_AUTO_REFRESH=true
```

**注意**: 这些配置是可选的，使用默认值也可以。

---

## 6. 配置文件检查清单

部署前确认：

- [ ] ✅ `app/main.py` - 添加了 `from app.api import wencai`
- [ ] ✅ `app/main.py` - 添加了 `app.include_router(wencai.router)`
- [ ] ✅ `app/core/config.py` - 添加了 WENCAI_* 配置项
- [ ] ✅ `celeryconfig.py` - 添加了问财定时任务
- [ ] ✅ `app/models/__init__.py` - 导入了 WencaiQuery
- [ ] ✅ `.env` - 添加了环境变量（可选）

---

## 7. 验证配置

### Python 导入测试

```python
# 运行以下代码验证配置
python3 << EOF
try:
    from app.api import wencai
    from app.services.wencai_service import WencaiService
    from app.core.config import settings
    print("✅ 配置验证通过")
    print(f"WENCAI_TIMEOUT: {settings.WENCAI_TIMEOUT}")
    print(f"WENCAI_RETRY_COUNT: {settings.WENCAI_RETRY_COUNT}")
except Exception as e:
    print(f"❌ 配置验证失败: {e}")
EOF
```

---

## 8. 完整的配置示例

### main.py 完整示例

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# 导入所有路由
from app.api import (
    auth,
    data,
    indicators,
    market,
    metrics,
    system,
    tasks,
    tdx,
    wencai,  # ✅ 添加
)

# 创建应用
app = FastAPI(
    title="MyStocks Web API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(market.router, tags=["market"])
app.include_router(metrics.router, tags=["metrics"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(tdx.router, tags=["tdx"])
app.include_router(wencai.router)  # ✅ 添加，已包含prefix

# 健康检查
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### config.py 完整示例

```python
# app/core/config.py
from pydantic import BaseSettings, Field
from typing import List

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "MyStocks Web API"
    APP_VERSION: str = "1.0.0"

    # 数据库配置
    MYSQL_DATABASE_URL: str = Field(..., env="MYSQL_DATABASE_URL")
    POSTGRESQL_DATABASE_URL: str = Field(..., env="POSTGRESQL_DATABASE_URL")
    TDENGINE_DATABASE_URL: str = Field(..., env="TDENGINE_DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # ... 其他现有配置 ...

    # ========== 问财API配置 ==========
    WENCAI_TIMEOUT: int = Field(
        default=30,
        env="WENCAI_TIMEOUT",
        description="问财API请求超时时间（秒）"
    )
    WENCAI_RETRY_COUNT: int = Field(
        default=3,
        env="WENCAI_RETRY_COUNT",
        description="问财API请求失败重试次数"
    )
    WENCAI_DEFAULT_PAGES: int = Field(
        default=1,
        env="WENCAI_DEFAULT_PAGES",
        description="问财API默认获取页数"
    )
    WENCAI_AUTO_REFRESH: bool = Field(
        default=True,
        env="WENCAI_AUTO_REFRESH",
        description="是否启用自动刷新"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## 9. 故障排查

### 导入错误: ModuleNotFoundError: No module named 'app.api.wencai'

**解决**:
```bash
# 检查文件是否存在
ls -la app/api/wencai.py

# 检查权限
chmod 644 app/api/wencai.py

# 重新启动应用
systemctl restart mystocks-backend
```

### 配置错误: AttributeError: 'Settings' object has no attribute 'WENCAI_TIMEOUT'

**解决**:
```bash
# 检查config.py中的配置
grep WENCAI app/core/config.py

# 如果缺失，手动添加配置项
```

### Celery任务找不到: No module named 'app.tasks.wencai_tasks'

**解决**:
```bash
# 检查文件是否存在
ls -la app/tasks/wencai_tasks.py

# 检查celeryconfig.py中的任务引用
grep wencai celeryconfig.py

# 重启Celery
systemctl restart celery-worker
systemctl restart celery-beat
```

---

## 10. 测试验证

### 1. 检查API是否可访问

```bash
# 健康检查
curl http://localhost:8000/api/market/wencai/health

# 应该返回: {"status":"healthy","service":"wencai","version":"1.0.0"}
```

### 2. 查看API文档

访问 `http://localhost:8000/api/docs`，应该能看到 `/api/market/wencai/*` 的所有端点

### 3. 测试Celery任务

```bash
# 查看活跃任务
celery -A app.celery_app inspect active

# 查看定时任务配置
celery -A app.celery_app beat --help
```

---

**配置补丁完成！** ✅

按照上述步骤更新配置文件后，即可部署问财功能。
