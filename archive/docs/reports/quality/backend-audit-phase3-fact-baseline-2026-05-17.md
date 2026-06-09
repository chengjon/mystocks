# MyStocks 后端审计事实基线 (Phase 2.5 Freeze)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **冻结日期**: 2026-05-17
> **Git 分支**: `wip/root-dirty-20260403`
> **最新提交**: `4efd1c7f2 feat(contract): track validation drift incidents`
> **用途**: Phase 3 Issues 的唯一事实引用来源

---

## 〇、扫描方法

所有数字通过以下命令生成（可复现）：

```bash
# Core 文件数
find web/backend/app/core -name "*.py" -not -path "*__pycache__*" | wc -l

# Core 行数
find web/backend/app/core -name "*.py" -not -path "*__pycache__*" -exec cat {} + | wc -l

# API flat 文件（排除 __init__.py, VERSION_MAPPING.py, _*.py helpers）
find web/backend/app/api -maxdepth 1 -name "*.py" -not -name "__init__.py" -not -name "VERSION_MAPPING.py" -not -name "_*.py" | wc -l

# API package 目录
find web/backend/app/api -maxdepth 2 -name "__init__.py" -not -path "*/app/api/__init__.py" -exec dirname {} \; | sort -u

# Singleton 总量
grep -rn "global _\w\+" web/backend/app/ --include="*.py" | wc -l

# Singleton 去重变量名
grep -rn "global _\w\+" web/backend/app/ --include="*.py" | sed 's/.*global \(_\w\+\).*/\1/' | sort -u | wc -l
```

**Include 规则**: `web/backend/app/` 下所有 `.py` 文件
**Exclude 规则**: `__pycache__/`、`_*.py` helpers（仅 flat 文件计数时排除）

---

## 一、Core 目录

| 指标 | 数值 |
|------|------|
| Python 文件 | **77** |
| 总行数 | **26,500** |

异常处理相关文件（6 个）:
- `app/core/exception_handler.py`
- `app/core/exception_handlers.py`
- `app/core/global_exception_handlers.py`
- `app/core/exceptions.py`
- `app/core/error_codes.py`
- `app/core/error_handling.py`

校验相关文件（5 个）:
- `app/core/validation.py`
- `app/core/validators.py`
- `app/core/validation_messages.py`
- `app/core/strategy_validator.py`
- `app/core/data_validator.py`

已子目录化的域:
- `cache/` (7 文件)
- `logging/` (3 文件: `__init__.py`, `structured.py`, `tracing.py`)
- `middleware/` (1 文件: `performance.py`)

---

## 二、Singleton

| 指标 | 数值 |
|------|------|
| `global _xxx` 语句总数 | **142** |
| 去重变量名 | **91** |

按层分布:

| 层 | 语句数 | 说明 |
|----|--------|------|
| `app/core/` | 69 | 基础设施：database, cache, socketio, security |
| `app/services/` | 49 | 业务服务：strategy, market_data, watchlist |
| `app/api/` | 15 | API 层辅助：realtime_mtm, dashboard, monitoring |
| `app/adapters/` | 5 | 外部适配器：eastmoney, tqlex, akshare, cninfo |
| `app/tasks/` | 2 | 异步任务 |
| `app/strategies/` | 1 | 策略注册 |
| `app/utils/` | 1 | 风控工具 |

高频变量名（同一变量在 get/set 函数中各出现一次）:

| 变量名 | 出现次数 | 文件 |
|--------|---------|------|
| `_manager` | 5 | cache_manager, casbin 等 |
| `_room_manager` | 4 | room_management, room_manager |
| `_performance_manager` | 4 | database, socketio |
| `_cache_manager` | 4 | cache/factory, cache/stats |
| `_adapter` | 4 | realtime_mtm, room_socketio |
| `_indicator_registry` | 3 | services, api, services/indicators |

**注意**: 142 语句包含同一变量在 getter/setter 中的重复声明。91 个去重变量更接近实际 singleton 实例数。

---

## 三、API 层

| 指标 | 数值 |
|------|------|
| Flat .py 文件（排除 helpers） | **71** |
| Package 目录（含 `__init__.py`） | **18** |
| 重叠域（flat + package 并存） | **10** |

重叠域清单:

| 域 | Flat 文件 | Package 目录 |
|----|----------|-------------|
| algorithms | `algorithms.py` | `algorithms/` (5 files) |
| announcement | `announcement.py` | `announcement/` (2 files) |
| backup_recovery_secure | `backup_recovery_secure.py` | `backup_recovery_secure/` (4 files) |
| indicators | `indicators.py` | `indicators/` (4 files) |
| market | `market.py` | `market/` (5 files) |
| multi_source | `multi_source.py` | `multi_source/` (2 files) |
| signal_monitoring | `signal_monitoring.py` | `signal_monitoring/` (4 files) |
| stock_search | `stock_search.py` | `stock_search/` (6 files) |
| strategy_management | `strategy_management.py` | `strategy_management/` (6 files) |
| system | `system.py` | `system/` (4 files) |

额外策略域入口（不在 overlap 清单中，但属于策略域混乱）:
- `strategy.py` — flat，通过 VERSION_MAPPING 注册
- `strategy_mgmt.py` — flat，直接注册

额外风控域入口:
- `risk_management.py` — flat
- `risk_management_core.py` — flat
- `risk_management_v31.py` — flat
- `risk/` — package (6 files)
- `risk_v31/` — package (3 files) — 注意：risk_v31 同时有 flat 和 package

**Bug**: `announcement` 在 `router_registry.py` 中被注册两次:
- 第 78 行: via VERSION_MAPPING prefix `/api/v1/announcement`
- 第 96 行: 直接注册 prefix `/api`

前端和测试全部使用 `/api/announcement/*`（来自第 96 行），`/api/v1/announcement/*` 几乎无消费者。

---

## 四、残留文件

| 类别 | 当前数量 | 说明 |
|------|---------|------|
| `.bak` / `.backup` / `.old.py` | **0** | Phase 1 已清理 |
| `_new.py` 过渡文件 | **4** | 见下表 |
| `monitoring_old/` 目录 | **1** (2 files) | `routes.py` + `__init__.py` |
| `auth_compat.py` | **1** | 有测试引用，不可直接删除 |
| Schema 双目录 | **2 dirs** | `app/schema/` (2 files) + `app/schemas/` (16+ files) |

`_new.py` 文件清单:
1. `app/services/data_adapter_new.py`
2. `app/services/data_api_new.py`
3. `app/services/risk_management_new.py`
4. `app/api/data/data_api_new.py`

---

## 五、健康端点

Canonical 端点（3 组，`main.py` 定义）:
- `GET /health` — liveness probe
- `GET /health/ready` — readiness probe
- `GET /api/health/ready` — readiness compat

Canonical 端点（`health.py` via router_registry）:
- `GET /api/health/services`
- `GET /api/health/detailed`
- `GET /api/reports/health/{ts}`

碎片健康端点（`@router.get("/health")` 或类似，11 个）:

| 文件 | 路径模式 |
|------|---------|
| `api/risk_v31/system.py` | `/health` |
| `api/system/system_health.py` | `/health` |
| `api/monitoring_old/routes.py` | `/health` |
| `api/technical/routes.py` | `/health` |
| `api/stock_ratings_api.py` | `/health` |
| `api/advanced_analysis_api.py` | `/health` |
| `api/multi_source.py` | `/health` + `/health/{type}` |
| `api/advanced_analysis.py` | `/health` |
| `api/backup_recovery_secure/cleanup_old_backups.py` | `/health` |
| `api/algorithms/get_algorithms_module.py` | `/health` |
| (announcement, wencai, signal_monitoring 等域另有 health 端点) |

---

## 六、与 Phase 2 报告的偏差说明

| 指标 | Phase 2 报告 | 本次基线 | 差异原因 |
|------|------------|---------|---------|
| Core 文件数 | 75 | **77** | Phase 2 后新增文件或扫描范围差异 |
| Singleton 语句 | 118 | **142** | Phase 2 统计范围不含 tasks/strategies/utils 层；同变量 getter/setter 重复计数 |
| Singleton 去重 | — | **91** | 新增去重指标 |
| API flat 文件 | 64 | **71** | Phase 2 排除了更多 helper 文件 |
| API package 目录 | 20 | **18** | Phase 2 含 `v1/` 等非独立 package |

**Phase 3 Issues 必须引用本基线文件的数字，不使用 Phase 2 报告的数字。**

---

*基线工具: `find`, `grep -rn`, `wc -l`, `sort | uniq -c`*
*基线环境: WSL2 Linux 6.6.87.2, Python 3.12+, git worktree*
