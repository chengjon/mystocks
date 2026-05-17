# MyStocks 后端架构深度分析报告

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **来源**: Phase 2 架构深度分析（基于 mattpocock/skills `/zoom-out` + `/improve-codebase-architecture` 方法论）
> **分析日期**: 2026-05-16
> **范围**: `web/backend/` Core 目录、Singleton 模式、API 迁移状态

---

## 一、Core 目录功能域分析

### 1.1 总量

| 指标 | 数值 |
|------|------|
| Python 文件 | 75 |
| 总行数 | 26,429 |
| Singleton 实例 | 45 |
| 重复文件组 | 5 组（exception ×3, validation ×3, cache 散落, database_performance ×2, tdengine ×2） |

### 1.2 按功能域分布

| 功能域 | 文件数 | 行数 | 状态 |
|--------|--------|------|------|
| database | 10 | 4,168 | 需子目录化 |
| cache | 12 | 3,959 | 部分子目录化（根级仍有 5 文件） |
| security | 6 | 2,470 | 需子目录化 |
| exception | 6 | 2,483 | 有 3 个重叠文件需合并 |
| socketio | 6 | 2,200 | 需子目录化 |
| other（未分类） | 21 | 6,429 | 最大类别，需逐个归类 |
| sse | 2 | 1,109 | 需子目录化 |
| monitoring | 3 | 836 | 含 middleware 子目录 |
| validation | 3 | 960 | 有 3 个重叠文件需合并 |
| logging | 3 | 480 | 已子目录化 ✅ |
| config | 1 | 313 | 保留根级 |
| event | 1 | 420 | 可归入 core/ 或独立 |

### 1.3 重复文件详解

**异常处理 ×3**:
- `exception_handler.py` (503 行) — 注册全局异常处理器
- `exception_handlers.py` — 功能重叠
- `global_exception_handlers.py` (449 行) — 功能重叠

**校验 ×3**:
- `validation.py` (266 行)
- `validators.py` (461 行)
- `validation_messages.py` (233 行)

**缓存 ×12**（根级 5 + 子目录 7）:
- 根级: `cache_manager.py`, `cache_utils.py`, `cache_eviction.py`, `cache_integration.py`, `cache_prewarming.py`
- 子目录: `cache/core.py`, `cache/factory.py`, `cache/fetch_write.py`, `cache/multi_level.py`, `cache/decorators.py`, `cache/batch_ops.py`, `cache/stats_health.py`

**数据库性能 ×2**:
- `database_performance.py` (310 行)
- `database_performance_monitor.py` (412 行)

**TDengine ×2**:
- `tdengine_manager.py` (561 行)
- `tdengine_pool.py` (421 行)

### 1.4 Core 内部依赖热点

被其他 Core 文件引用最多的模块：

| 模块 | 被引用次数 | 角色 |
|------|-----------|------|
| `config` | 10 | 基础配置 |
| `adapter_factory` | 6 | 适配器工厂 |
| `database` | 4 | 数据库连接 |
| `cache_manager` | 4 | 缓存管理 |
| `redis_client` | 3 | Redis 连接 |
| `logger` | 3 | 日志门面 |
| `responses` | 1 | 响应模型 |

`config` 是基础层中依赖最深的模块，任何 Core 重构必须从 config 开始确认无破坏。

---

## 二、Singleton 模式全量分析

### 2.1 分布

| 层 | Singleton 数量 | 代表 |
|----|---------------|------|
| `app/core/` | 45 | database, cache, socketio, security |
| `app/services/` | 35 | strategy, watchlist, market_data |
| `app/adapters/` | 5 | eastmoney, tqlex, akshare, cninfo |
| `app/api/` | 12 | realtime_mtm, dashboard, monitoring |
| 其他 | 21 | tasks, strategies, utils |
| **总计** | **118** | |

### 2.2 生命周期

**结论**: 所有 118 个 singleton 均为 **per-app** 生命周期（应用启动时 lazy init，运行期间不变）。

无 per-request 或 per-session 变体。这意味着迁移到 FastAPI `Depends()` 的风险较低 — 保持 singleton 语义的同时获得测试覆盖能力。

### 2.3 循环依赖风险

通过 Core 内部引用分析，`config` → `adapter_factory` → 具体服务 是主要初始化链。未发现循环引用，但以下链路较长：

```
config → database_factory → database → cache_manager → cache_integration
```

5 层深度。如果 `cache_integration` 反向引用 `config`，将形成循环。当前代码未观察到此问题，但重构时需注意。

---

## 三、API Flat/Package 迁移状态

### 3.1 总量

| 类型 | 数量 |
|------|------|
| Flat 文件（排除 helper/schema） | 64 |
| Package 目录 | 20 |
| 重叠域（同时存在 flat + package） | 10 |
| Flat-only 域 | 54 |
| Package-only 域 | 10 |

### 3.2 已发现 Bug: announcement 双注册

`router_registry.py` 中 `announcement` 被注册两次：
- 第 78 行: `router_modules["announcement"] = announcement.router` → via VERSION_MAPPING prefix `/api/v1/announcement`
- 第 96 行: `app.include_router(announcement.router, prefix="/api", tags=["announcement"])`

同一 router 模块被注册到两个不同前缀，导致路由重复。

### 3.3 策略域混乱度最高

| 文件 | 类型 | 注册方式 |
|------|------|----------|
| `strategy.py` | flat | VERSION_MAPPING → `/api/v1/strategy` |
| `strategy_management.py` | flat | `router_registry.py:126` 直接注册 |
| `strategy_mgmt.py` | flat | `router_registry.py:103` 直接注册 |
| `strategy_management/` | package (6 files) | 未在 router_registry 直接注册 |

3 个 flat 文件 + 1 个 package 目录，功能边界不清。

### 3.4 风控域次高

| 文件 | 类型 |
|------|------|
| `risk_management.py` | flat |
| `risk_management_core.py` | flat |
| `risk_management_v31.py` | flat |
| `risk/` | package (6 files) |
| `risk_v31/` | package (3 files) |

5 个入口 + 2 个 package 目录。

### 3.5 迁移路径

见 `docs/architecture/0002-api-flat-to-package-migration.md`

---

## 四、深化机会清单（Deepening Opportunities）

按优先级排序：

| # | 机会 | 影响 | 复杂度 | 前置条件 |
|---|------|------|--------|----------|
| D-1 | 修复 announcement 双注册 bug | 高（路由冲突） | 低 | 无 |
| D-2 | 合并 Core exception ×3 → 1 canonical | 中 | 中 | OpenSpec |
| D-3 | 合并 Core validation ×3 → 1 canonical | 中 | 低 | 无 |
| D-4 | Core cache 根级文件移入 cache/ 子目录 | 中 | 中 | GitNexus impact |
| D-5 | Core database 文件提取 database/ 子目录 | 中 | 高 | GitNexus impact |
| D-6 | 低复杂度域 flat→package 收口 (7 域) | 中 | 低-中 | 逐域双判定 |
| D-7 | market 域 flat→package 收口 | 中 | 中 | market.py vs market/ 功能对比 |
| D-8 | 策略域 3 flat 收敛到 1 canonical | 高 | 高 | OpenSpec |
| D-9 | 风控域 5 入口收敛 | 高 | 高 | OpenSpec |
| D-10 | Core singleton→Depends (database 层) | 中 | 中 | D-5 后 |
| D-11 | Services singleton→Depends | 中 | 高 | D-10 后 |
| D-12 | 健康端点 18 碎片收敛 | 中 | 中 | 路由表重测 |

---

## 五、架构决策记录（ADR）索引

| ADR | 主题 | 位置 |
|-----|------|------|
| 0001 | Core 目录按职责拆分子目录 | `docs/architecture/0001-core-directory-restructure.md` |
| 0002 | API Flat→Package 迁移策略 | `docs/architecture/0002-api-flat-to-package-migration.md` |
| 0003 | Singleton 到 FastAPI Depends 迁移路径 | `docs/architecture/0003-singleton-to-di-migration.md` |

---

*前置文档: `docs/reports/quality/backend-audit-2026-05-14.md`*
*分析方法: mattpocock/skills `/zoom-out` + `/improve-codebase-architecture`*
