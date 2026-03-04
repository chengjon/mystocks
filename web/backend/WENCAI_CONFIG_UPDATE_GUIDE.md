# 问财功能配置更新指南

## 📋 需要修改的文件

本指南说明如何将问财功能集成到现有的MyStocks Web后端。

---

## 1. 更新主应用 (app/main.py)

### 添加问财路由

在现有路由配置后添加：

```python
# 在文件开头导入
from app.api import wencai

# 在路由配置部分添加
app.include_router(wencai.router)
```

**完整示例**:
```python
# app/main.py
from fastapi import FastAPI
from app.api import data, auth, market, tdx, indicators, wencai  # 添加wencai

app = FastAPI(
    title="MyStocks Web API",
    version="1.0.0",
    docs_url="/api/docs"
)

# 现有路由
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(market.router, tags=["market"])
# ... 其他路由

# 添加问财路由
app.include_router(wencai.router)  # 已经包含prefix="/api/market/wencai"
```

---

## 2. 更新配置 (app/core/config.py)

### 添加问财配置项

在`Settings`类中添加：

```python
class Settings(BaseSettings):
    # ... 现有配置

    # ========== 问财API配置 ==========
    WENCAI_TIMEOUT: int = Field(
        default=30,
        description="问财API请求超时时间（秒）"
    )
    WENCAI_RETRY_COUNT: int = Field(
        default=3,
        description="问财API请求失败重试次数"
    )
    WENCAI_DEFAULT_PAGES: int = Field(
        default=1,
        description="默认获取页数"
    )
    WENCAI_AUTO_REFRESH: bool = Field(
        default=True,
        description="是否启用自动刷新"
    )
```

### 添加环境变量 (.env)

在`.env`文件中添加（可选，使用默认值）：

```env
# 问财API配置
WENCAI_TIMEOUT=30
WENCAI_RETRY_COUNT=3
WENCAI_DEFAULT_PAGES=1
WENCAI_AUTO_REFRESH=true
```

---

## 3. 更新Celery配置 (celeryconfig.py)

### 方式A: 直接合并到beat_schedule

```python
from celery.schedules import crontab

beat_schedule = {
    # ... 现有任务

    # 问财每日刷新（09:00）
    'wencai-refresh-all-daily': {
        'task': 'wencai.scheduled_refresh_all',
        'schedule': crontab(hour=9, minute=0),
        'args': (1,),  # pages=1
        'kwargs': {'active_only': True},
    },

    # 问财数据清理（02:00）
    'wencai-cleanup-old-data-daily': {
        'task': 'wencai.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),
        'args': (30,),  # 保留30天
        'kwargs': {'dry_run': False},
    },
}
```

### 方式B: 使用单独的配置文件

```python
# celeryconfig.py
from celeryconfig_wencai import WENCAI_BEAT_SCHEDULE

beat_schedule = {
    # ... 现有任务
}

# 合并问财任务
beat_schedule.update(WENCAI_BEAT_SCHEDULE)
```

---

## 4. 更新数据库模型注册 (app/models/__init__.py)

确保问财模型被导入：

```python
# app/models/__init__.py
from app.models.market_data import FundFlow, ETFData, ChipRaceData, LongHuBangData
from app.models.wencai_data import WencaiQuery  # 添加这行

__all__ = [
    "FundFlow",
    "ETFData",
    "ChipRaceData",
    "LongHuBangData",
    "WencaiQuery",  # 添加这行
]
```

---

## 5. 执行数据库迁移

### 方式A: 直接执行SQL脚本

```bash
# 方法1: 使用mysql命令
mysql -u root -p < /opt/claude/mystocks_spec/web/backend/migrations/wencai_init.sql

# 方法2: 在MySQL客户端中执行
mysql -u root -p
USE your_database_name;
SOURCE /opt/claude/mystocks_spec/web/backend/migrations/wencai_init.sql;
```

### 方式B: 使用Python脚本

创建 `scripts/init_wencai_db.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""初始化问财数据库"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def init_wencai_database():
    """执行问财数据库初始化"""
    engine = create_engine(settings.MYSQL_DATABASE_URL)

    with open('migrations/wencai_init.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()

    with engine.connect() as conn:
        # 分割并执行每个SQL语句
        statements = sql_script.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()

    print("✅ 问财数据库初始化完成")

if __name__ == "__main__":
    init_wencai_database()
```

执行：
```bash
cd /opt/claude/mystocks_spec/web/backend
python scripts/init_wencai_db.py
```

---

## 6. 验证配置

### 6.1 检查导入是否正确

```python
# test_imports.py
try:
    from app.api import wencai
    from app.services.wencai_service import WencaiService
    from app.adapters.wencai_adapter import WencaiDataSource
    from app.models.wencai_data import WencaiQuery
    from app.tasks import wencai_tasks
    print("✅ 所有导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
```

### 6.2 检查数据库表

```sql
-- 检查wencai_queries表
SELECT COUNT(*) FROM wencai_queries;
-- 应该返回9条记录

-- 查看所有查询
SELECT query_name, description, is_active FROM wencai_queries;
```

### 6.3 测试API端点

```bash
# 健康检查
curl http://localhost:8020/api/market/wencai/health

# 获取查询列表
curl http://localhost:8020/api/market/wencai/queries

# 查看API文档
open http://localhost:8020/api/docs
```

---

## 7. 重启服务

### 重启FastAPI后端

```bash
# 使用systemd
systemctl restart mystocks-backend

# 或使用uvicorn
pkill -f uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload
```

### 重启Celery服务

```bash
# 重启worker
systemctl restart celery-worker
# 或
pkill -f "celery worker"
celery -A app.celery_app worker -l info &

# 重启beat (定时任务)
systemctl restart celery-beat
# 或
pkill -f "celery beat"
celery -A app.celery_app beat -l info &
```

---

## 8. 故障排查

### 问题1: 导入错误 (ModuleNotFoundError)

**症状**: `ModuleNotFoundError: No module named 'app.api.wencai'`

**解决**:
```bash
# 检查文件是否存在
ls -la app/api/wencai.py

# 检查Python路径
python -c "import sys; print(sys.path)"

# 重新安装依赖
pip install -r requirements.txt
```

### 问题2: 数据库连接失败

**症状**: `sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL server...`

**解决**:
```python
# 检查配置
from app.core.config import settings
print(settings.MYSQL_DATABASE_URL)

# 测试连接
mysql -h <host> -u <user> -p
```

### 问题3: Celery任务不执行

**症状**: 定时任务未触发

**解决**:
```bash
# 检查Celery beat状态
celery -A app.celery_app inspect active

# 检查调度配置
celery -A app.celery_app beat -l debug

# 查看日志
tail -f /var/log/celery/beat.log
tail -f /var/log/celery/worker.log
```

### 问题4: API返回500错误

**症状**: `Internal Server Error`

**解决**:
```bash
# 查看后端日志
tail -f /var/log/mystocks/backend.log

# 启用调试模式
uvicorn app.main:app --reload --log-level debug

# 检查具体错误
curl -v http://localhost:8020/api/market/wencai/queries
```

---

## 9. 完整性检查清单

部署前确认：

- [ ] `app/main.py` - 添加了wencai路由
- [ ] `app/core/config.py` - 添加了WENCAI_*配置
- [ ] `celeryconfig.py` - 添加了定时任务
- [ ] `app/models/__init__.py` - 导入了WencaiQuery
- [ ] `.env` - 添加了环境变量（可选）
- [ ] 数据库迁移 - 执行了wencai_init.sql
- [ ] 服务重启 - 重启了backend和celery
- [ ] API测试 - 所有端点正常响应
- [ ] Celery测试 - 任务能够正常执行

---

## 10. 配置模板文件

### main.py 配置片段

```python
# 完整的路由配置示例
from app.api import (
    auth,
    data,
    indicators,
    market,
    metrics,
    system,
    tasks,
    tdx,
    wencai,  # 新增
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
app.include_router(wencai.router)  # 新增，已包含prefix
```

### config.py 配置片段

```python
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # ... 现有配置 ...

    # 问财API配置
    WENCAI_TIMEOUT: int = Field(30, env="WENCAI_TIMEOUT")
    WENCAI_RETRY_COUNT: int = Field(3, env="WENCAI_RETRY_COUNT")
    WENCAI_DEFAULT_PAGES: int = Field(1, env="WENCAI_DEFAULT_PAGES")
    WENCAI_AUTO_REFRESH: bool = Field(True, env="WENCAI_AUTO_REFRESH")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## 📚 相关文档

- **Phase 1完成报告**: [WENCAI_PHASE1_COMPLETED.md](../../docs/WENCAI_PHASE1_COMPLETED.md)
- **完整规划**: [WENCAI_INTEGRATION_PLAN.md](../../docs/WENCAI_INTEGRATION_PLAN.md)
- **快速参考**: [WENCAI_INTEGRATION_QUICKREF.md](../../docs/WENCAI_INTEGRATION_QUICKREF.md)

---

**更新日期**: 2025-10-17
**文档版本**: 1.0.0
