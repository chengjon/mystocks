# 问财功能部署快速指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 🚀 5分钟快速部署

本指南将指导你快速部署问财股票筛选功能到MyStocks Web后端。

---

## 📋 部署前检查

### 步骤1: 运行部署前检查

```bash
cd /opt/claude/mystocks_spec/web/backend
bash scripts/pre_deployment_check.sh
```

**检查内容**:
- ✅ 所有必要文件是否存在
- ✅ Python依赖是否已安装
- ✅ MySQL连接是否正常
- ✅ 现有配置是否正确

---

## 🔧 配置更新（10分钟）

### 步骤2: 更新配置文件

根据 `CONFIG_PATCHES.md` 中的补丁，更新以下文件：

#### 2.1 更新 app/main.py

在导入部分添加：
```python
from app.api import wencai
```

在路由注册部分添加（在最后）：
```python
app.include_router(wencai.router)
```

#### 2.2 更新 app/core/config.py

在 `Settings` 类中添加：
```python
WENCAI_TIMEOUT: int = Field(default=30, env="WENCAI_TIMEOUT")
WENCAI_RETRY_COUNT: int = Field(default=3, env="WENCAI_RETRY_COUNT")
WENCAI_DEFAULT_PAGES: int = Field(default=1, env="WENCAI_DEFAULT_PAGES")
WENCAI_AUTO_REFRESH: bool = Field(default=True, env="WENCAI_AUTO_REFRESH")
```

#### 2.3 更新 celeryconfig.py

在 `beat_schedule` 字典中添加：
```python
'wencai-refresh-all-daily': {
    'task': 'wencai.scheduled_refresh_all',
    'schedule': crontab(hour=9, minute=0),
    'args': (1,),
},

'wencai-cleanup-old-data-daily': {
    'task': 'wencai.cleanup_old_data',
    'schedule': crontab(hour=2, minute=0),
    'args': (30,),
},
```

#### 2.4 更新 app/models/__init__.py

添加导入：
```python
from app.models.wencai_data import WencaiQuery

__all__ = [..., "WencaiQuery"]
```

---

## 🗄️ 数据库初始化（5分钟）

### 步骤3: 执行数据库迁移

```bash
# 方式A: 使用mysql命令
mysql -u root -p < migrations/wencai_init.sql

# 方式B: 在MySQL客户端中
mysql -u root -p
USE your_database_name;
SOURCE migrations/wencai_init.sql;
```

**验证**:
```sql
-- 检查是否成功
SELECT COUNT(*) FROM wencai_queries;
-- 应该返回: 9
```

---

## 🔄 重启服务（5分钟）

### 步骤4: 重启服务

```bash
# 重启FastAPI后端
systemctl restart mystocks-backend

# 重启Celery worker
systemctl restart celery-worker

# 重启Celery beat
systemctl restart celery-beat
```

**验证服务状态**:
```bash
systemctl status mystocks-backend
systemctl status celery-worker
systemctl status celery-beat
```

---

## ✅ 部署验证（5分钟）

### 步骤5: 验证部署

#### 5.1 API健康检查

```bash
curl http://localhost:8000/api/market/wencai/health
```

**预期响应**:
```json
{
  "status": "healthy",
  "service": "wencai",
  "version": "1.0.0"
}
```

#### 5.2 获取查询列表

```bash
curl http://localhost:8000/api/market/wencai/queries
```

**预期响应**: 包含9个查询的列表

#### 5.3 运行自动化测试

```bash
bash scripts/test_wencai_api.sh
```

#### 5.4 查看Swagger API文档

访问: `http://localhost:8000/api/docs`

应该能看到所有 `/api/market/wencai/*` 端点

---

## 📊 完整部署命令

### 一键部署（自动化）

```bash
cd /opt/claude/mystocks_spec/web/backend

# 1. 运行部署前检查
bash scripts/pre_deployment_check.sh

# 2. 运行自动化部署脚本
bash scripts/deploy_wencai.sh

# 3. 重启服务
systemctl restart mystocks-backend
systemctl restart celery-worker
systemctl restart celery-beat

# 4. 运行测试
bash scripts/test_wencai_api.sh
```

### 手动部署（分步）

```bash
# 步骤1: 检查
bash scripts/pre_deployment_check.sh

# 步骤2: 手动更新配置（参考CONFIG_PATCHES.md）
# 编辑 app/main.py
# 编辑 app/core/config.py
# 编辑 celeryconfig.py
# 编辑 app/models/__init__.py

# 步骤3: 数据库迁移
mysql -u root -p < migrations/wencai_init.sql

# 步骤4: 重启服务
systemctl restart mystocks-backend
systemctl restart celery-worker
systemctl restart celery-beat

# 步骤5: 测试
curl http://localhost:8000/api/market/wencai/health
bash scripts/test_wencai_api.sh
```

---

## 🐛 故障排查

### 问题1: 导入错误

**错误信息**: `ModuleNotFoundError: No module named 'app.api.wencai'`

**解决**:
```bash
# 检查文件
ls -la app/api/wencai.py

# 检查配置
grep "from app.api import wencai" app/main.py
```

### 问题2: 配置错误

**错误信息**: `AttributeError: 'Settings' object has no attribute 'WENCAI_TIMEOUT'`

**解决**:
```bash
# 检查是否添加了配置
grep WENCAI app/core/config.py

# 根据CONFIG_PATCHES.md添加缺失的配置
```

### 问题3: 数据库错误

**错误信息**: `Table 'wencai.wencai_queries' doesn't exist`

**解决**:
```bash
# 检查迁移脚本
mysql -u root -p -e "SHOW TABLES LIKE 'wencai%';"

# 重新执行迁移
mysql -u root -p < migrations/wencai_init.sql
```

### 问题4: Celery任务找不到

**错误信息**: `Error: No module named 'app.tasks.wencai_tasks'`

**解决**:
```bash
# 检查任务文件
ls -la app/tasks/wencai_tasks.py

# 重启Celery
systemctl restart celery-worker
systemctl restart celery-beat
```

---

## 📚 参考文档

| 文档 | 说明 |
|------|------|
| [CONFIG_PATCHES.md](web/backend/CONFIG_PATCHES.md) | 详细的配置补丁 |
| [WENCAI_CONFIG_UPDATE_GUIDE.md](web/backend/WENCAI_CONFIG_UPDATE_GUIDE.md) | 配置更新指南 |
| [docs/WENCAI_IMPLEMENTATION_COMPLETE.md](docs/WENCAI_IMPLEMENTATION_COMPLETE.md) | 完整实施报告 |
| [docs/WENCAI_INTEGRATION_QUICKREF.md](docs/WENCAI_INTEGRATION_QUICKREF.md) | 快速参考 |

---

## ✨ 部署完成清单

部署完成后，确认以下事项：

- [ ] ✅ 所有配置文件已更新
- [ ] ✅ 数据库迁移已执行
- [ ] ✅ 所有服务已重启
- [ ] ✅ API健康检查通过
- [ ] ✅ 所有测试通过
- [ ] ✅ Swagger文档可访问
- [ ] ✅ Celery任务正常运行

---

## 🎯 下一步

### 立即可以使用的功能

✅ 7个API端点 - 立即可用
✅ 9个预定义查询 - 立即可用
✅ 定时自动刷新 - 每日9:00
✅ 自动清理旧数据 - 每日2:00

### 后续优化（可选）

- [ ] 添加单元测试
- [ ] Redis缓存集成
- [ ] 前端UI页面开发
- [ ] 性能监控和优化

---

## 📞 需要帮助？

1. **查看文档**: `/opt/claude/mystocks_spec/docs/WENCAI_INTEGRATION_INDEX.md`
2. **查看配置指南**: `/opt/claude/mystocks_spec/web/backend/CONFIG_PATCHES.md`
3. **运行检查脚本**: `bash scripts/pre_deployment_check.sh`
4. **查看日志**: `tail -f /var/log/mystocks/backend.log`

---

**部署时间**: 约20-30分钟
**难度**: ⭐⭐☆☆☆ (简单)
**完成日期**: 2025-10-17

祝部署顺利！🚀
