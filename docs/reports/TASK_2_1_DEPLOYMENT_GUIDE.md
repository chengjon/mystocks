# Task 2.1: TDengine 缓存服务 - 部署指南

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**任务**: TDengine 服务搭建与验证
**状态**: ✅ 就绪部署
**完成时间**: 2025-11-06

---

## 📋 完成清单

- [x] Docker Compose 配置文件 (`docker-compose.tdengine.yml`)
- [x] TDengineManager 核心类 (`web/backend/app/core/tdengine_manager.py`)
- [x] 完整集成测试 (`web/backend/tests/test_tdengine_manager.py`)
- [x] 部署验证脚本 (`verify_tdengine_deployment.py`)
- [x] 缓存监控脚本 (`monitor_cache_stats.py`)
- [x] 实现计划文档 (`TASK_2_IMPLEMENTATION_PLAN.md`)

---

## 🚀 快速开始

### 前置条件

```bash
# 1. 安装 Docker 和 Docker Compose
# macOS: brew install docker docker-compose
# Linux: apt-get install docker docker-compose
# Windows: 下载 Docker Desktop

# 2. 安装 Python 依赖
pip install taospy structlog pyyaml

# 3. 确保 PostgreSQL 已安装 (可选)
# 本配置包含独立的 PostgreSQL 容器
```

### 部署步骤

```bash
# 1. 启动 TDengine 和 PostgreSQL 容器
docker-compose -f docker-compose.tdengine.yml up -d

# 2. 验证部署
python verify_tdengine_deployment.py

# 3. 运行集成测试
pytest web/backend/tests/test_tdengine_manager.py -v

# 4. 启动监控
python monitor_cache_stats.py
```

---

## 🏗️ 架构组件

### 1. Docker Compose 配置 (`docker-compose.tdengine.yml`)

**TDengine 服务**:
- 镜像: `tdengine/tdengine:3.0.4.0`
- 端口: `6030-6039` (多协议支持)
- 存储: 持久化卷 `tdengine_data`
- 日志: 持久化卷 `tdengine_logs`
- 网络: 共享网络 `mystocks_network`
- 健康检查: 自动重启失败容器

**PostgreSQL 服务**:
- 镜像: `postgres:15-alpine`
- 端口: `5438`
- 用户: `postgres`
- 密码: `your-postgresql-password`
- 存储: 持久化卷 `postgres_data`

### 2. TDengineManager 类 (`web/backend/app/core/tdengine_manager.py`)

**核心功能**:

```python
# 初始化
manager = TDengineManager()
manager.initialize()

# 写入缓存
manager.write_cache(
    symbol="000001",
    data_type="fund_flow",
    timeframe="1d",
    data={"main_net_inflow": 1000000}
)

# 读取缓存
data = manager.read_cache(
    symbol="000001",
    data_type="fund_flow"
)

# 获取统计
stats = manager.get_cache_stats()

# 清理过期数据 (>7天)
manager.clear_expired_cache(days=7)

# 健康检查
manager.health_check()
```

**数据库表结构**:

```sql
-- 市场数据缓存表 (超表模式)
CREATE TABLE market_data_cache (
    ts TIMESTAMP,
    symbol VARCHAR(10),
    data_type VARCHAR(20),
    timeframe VARCHAR(10),
    data NCHAR(1024),
    hit_count BIGINT DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) TAGS (symbol VARCHAR(10), data_type VARCHAR(20))

-- 缓存统计表
CREATE TABLE cache_stats (
    ts TIMESTAMP,
    total_requests BIGINT,
    cache_hits BIGINT,
    cache_misses BIGINT,
    hit_rate FLOAT
)

-- 热点数据表
CREATE TABLE hot_symbols (
    ts TIMESTAMP,
    symbol VARCHAR(10),
    access_count BIGINT,
    last_access TIMESTAMP
) TAGS (symbol VARCHAR(10))
```

### 3. 集成测试套件 (`web/backend/tests/test_tdengine_manager.py`)

**测试覆盖**:

| 类别 | 测试项 | 数量 |
|------|--------|------|
| 连接 | 连接成功/失败、健康检查 | 4 |
| 初始化 | 数据库创建、表创建、单例 | 4 |
| 写入 | 简单数据、复杂数据、多符号 | 5 |
| 读取 | 读取成功、不存在数据、时间窗口、命中计数 | 4 |
| 过期清理 | TTL清理、自定义保留期 | 3 |
| 统计 | 统计获取、空缓存、有数据 | 3 |
| 错误处理 | 特殊字符、大数据、多连接 | 4 |
| **总计** | | **27 测试用例** |

**运行测试**:

```bash
# 运行所有测试
pytest web/backend/tests/test_tdengine_manager.py -v

# 运行特定测试类
pytest web/backend/tests/test_tdengine_manager.py::TestCacheWriteOperations -v

# 运行特定测试
pytest web/backend/tests/test_tdengine_manager.py::TestCacheWriteOperations::test_write_cache_simple -v

# 显示详细输出和性能信息
pytest web/backend/tests/test_tdengine_manager.py -vv --tb=short --durations=10
```

### 4. 部署验证脚本 (`verify_tdengine_deployment.py`)

**验证项**:

- Docker 安装和运行状态
- TDengine 容器状态
- PostgreSQL 容器状态
- TDengine 连接性
- TDengineManager 功能
- 数据库初始化
- 缓存读写操作

**运行验证**:

```bash
python verify_tdengine_deployment.py

# 输出示例:
# ✅ Docker installed: Docker version 24.0.0
# ✅ Docker daemon is running
# ✅ TDengine container is running: Up 2 minutes
# ✅ TDengineManager connection successful
# ✅ Database initialization successful
# ✅ Table 'market_data_cache' exists and accessible
# ✅ Cache write operation successful
# ✅ Cache read operation successful
#
# 🎉 All checks passed! TDengine is ready for use.
```

### 5. 缓存监控脚本 (`monitor_cache_stats.py`)

**监控指标**:

- 总缓存记录数
- 不同符号数量
- 缓存命中率 (目标 ≥80%)
- 热点符号排名
- 系统正常运行时间

**运行监控**:

```bash
# 实时监控 (5秒刷新一次)
python monitor_cache_stats.py

# 指定更新间隔
python monitor_cache_stats.py --interval 10

# 只运行一次
python monitor_cache_stats.py --once

# 输出示例:
# ======================================================================
#   Cache Statistics - 2025-11-06 14:30:45
# ======================================================================
#
#   📊 Cache Overview:
#     Total Records:   1,234
#     Unique Symbols:  256
#     Timestamp:       2025-11-06T14:30:45.123456
#
#   ⏱️  Uptime:        0:15:30
#
#   ✅ Cache Hit Rate:   85.3%
#
#   🔥 Hot Symbols (Top 10):
#     1. 000001 - Accesses: 542 - Last: 2025-11-06T14:30:42
#     2. 000858 - Accesses: 438 - Last: 2025-11-06T14:30:40
#    ...
```

---

## 📊 性能指标

### 目标值

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 缓存命中率 | ≥ 80% | 表示有效的缓存利用率 |
| 单次查询延迟 | < 100ms | P99延迟 |
| 写入吞吐量 | > 10k ops/sec | 在单机配置下 |
| 数据保留期 | 7 天 | TTL自动清理 |
| 容器启动时间 | < 30s | 健康检查通过 |

### 验证性能

```bash
# 编写性能测试脚本
python tests/test_cache_performance.py

# 监控系统资源
docker stats mystocks_tdengine
```

---

## 🔧 配置管理

### 环境变量 (`.env`)

```bash
# TDengine 配置
TDENGINE_HOST=127.0.0.1
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=your-tdengine-password
TDENGINE_DATABASE=mystocks_cache

# PostgreSQL 配置 (用于其他数据)
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your-postgresql-password
POSTGRESQL_DATABASE=mystocks

# 缓存配置
CACHE_TTL_DAYS=7
CACHE_CLEANUP_INTERVAL=86400  # 1 天 (秒)
CACHE_HIT_RATE_TARGET=0.8     # 80%
```

### Docker 容器配置

**TDengine 性能参数** (docker-compose.yml):

```yaml
environment:
  TAOS_MAXROWS: "4096"        # 最大行数
  TAOS_MINROWS: "100"         # 最小行数
  TAOS_KEEP: "30"             # 数据保留时间 (天)
  TAOS_CACHE_SIZE: "16"       # 缓存大小 (MB)
  TAOS_WAL_LEVEL: "1"         # WAL级别
  TAOS_WAL_FSYNC_PERIOD: "3000" # WAL同步间隔 (毫秒)
```

---

## 🛠️ 故障排除

### 问题 1: 容器启动失败

```bash
# 检查日志
docker-compose -f docker-compose.tdengine.yml logs tdengine

# 重启容器
docker-compose -f docker-compose.tdengine.yml restart tdengine

# 完全重建
docker-compose -f docker-compose.tdengine.yml down -v
docker-compose -f docker-compose.tdengine.yml up -d
```

### 问题 2: 连接失败

```bash
# 验证容器是否运行
docker ps | grep mystocks_tdengine

# 检查端口是否开放
netstat -an | grep 6030

# 测试连接
docker exec -it mystocks_tdengine taos

# 如果需要重新安装驱动
pip install --upgrade taospy
```

### 问题 3: 性能低下

```bash
# 检查容器资源使用
docker stats mystocks_tdengine

# 检查数据库大小
docker exec -it mystocks_tdengine bash
# 在容器内: du -sh /var/lib/taos

# 清理过期数据
python -c "
from web.backend.app.core.tdengine_manager import TDengineManager
mgr = TDengineManager()
mgr.initialize()
deleted = mgr.clear_expired_cache(days=7)
print(f'Deleted {deleted} expired records')
"
```

### 问题 4: 磁盘空间不足

```bash
# 检查卷大小
docker volume inspect mystocks_tdengine_data

# 扩展卷 (Docker容积驱动)
# 注意: 无法直接扩展Docker卷，需要迁移数据

# 临时方案: 清理旧数据
python -c "
from web.backend.app.core.tdengine_manager import TDengineManager
mgr = TDengineManager()
mgr.initialize()
mgr.clear_expired_cache(days=1)  # 只保留1天数据
"
```

---

## 📈 下一步计划

### Subtask 2.2: 缓存读写逻辑集成
- 创建API端点 (`/api/cache/*`)
- 集成 UnifiedMarketDataService
- 实现自动缓存更新机制
- 性能优化 (批量操作、异步写入)

### Subtask 2.3: TTL 淘汰策略
- 自动清理任务 (定时器)
- LRU 淘汰算法
- 管理员手动清理接口
- 淘汰规则配置

### Subtask 2.4: 缓存预热和监控
- 启动时数据预加载
- 缓存命中率监控
- 热点数据识别和预加载
- 可视化监控仪表板

---

## 📚 相关文档

- [Task 2 Implementation Plan](TASK_2_IMPLEMENTATION_PLAN.md) - 完整计划
- [TDengineManager API 文档](web/backend/app/core/tdengine_manager.py) - 代码文档
- [测试用例](web/backend/tests/test_tdengine_manager.py) - 集成测试
- [项目架构](CLAUDE.md) - 整体架构说明

---

## ✅ 验收清单

- [x] TDengine 容器正常启动
- [x] 数据库连接成功
- [x] 表结构创建完成
- [x] 缓存写入功能验证
- [x] 缓存读取功能验证
- [x] TTL清理机制验证
- [x] 集成测试全部通过 (27/27)
- [x] 部署验证脚本完成
- [x] 监控脚本完成
- [x] 文档完整

---

## 📞 支持

遇到问题? 查看:

1. **部署错误**: 运行 `verify_tdengine_deployment.py`
2. **测试失败**: 运行 `pytest -v` 查看详细日志
3. **性能问题**: 运行 `monitor_cache_stats.py` 监控指标
4. **Docker问题**: 检查 `docker logs` 和 `docker stats`

---

*生成时间: 2025-11-06*
*状态: ✅ 就绪部署*
*下一步: Subtask 2.2 - 缓存读写逻辑集成*
