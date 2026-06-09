# MyStocks 健康端点收敛分析

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **来源**: `docs/reports/quality/backend-audit-2026-05-14.md` §五.5 深化
> **审计日期**: 2026-05-14
> **复核日期**: 2026-05-17
> **红线基准**: `architecture/STANDARDS.md` §一.5「必须提供 `/health/ready` 探针」
> **执行门禁**: 健康端点 canonical 变更、旧端点退役、OpenAPI 暴露面变化、监控/PM2/CI 探针切换均属于架构和运行面变更，实施前必须创建并通过 OpenSpec proposal/design/tasks 审批。

2026-05-17 复核摘要：

| 扫描项 | 当前数量 / 结论 |
|--------|------------------|
| `web/backend/app/**/*.py` 中 health-like route decorators | 46 |
| 代码中 `/health/readiness` 文本命中 | 0 |
| 代码中 `/health/services` 文本命中 | 1，位于 `api/health.py`，经 `router_registry.py` 的 `/api` prefix 暴露为 `/api/health/services` |
| 已确认就绪探针 | `GET /health/ready` 与 `GET /api/health/ready` |
| 已确认服务探针 | `GET /api/health/services` |

结论：当前阻塞点不是 `/health/ready` 缺失，而是健康端点候选过多、注册 prefix 复杂、领域 smoke 端点和系统探针职责混在一起。删除或改路径前必须先重导 route table、OpenAPI diff、监控/前端/测试消费者清单。

---

## 一、当前健康端点碎片化清单

### 1.1 Canonical 健康端点（已校准 2026-05-17）

> **事实来源**: `main.py` + `router_registry.py` + `health.py` 代码扫描

| Canonical 端点 | 定义位置 | 注册方式 | 功能 |
|---|---|---|---|
| `GET /health` | `main.py:637` | `@app.get` | Liveness probe（存活探针） |
| `GET /health/ready` | `main.py:673` | `@app.get` | Readiness probe（就绪探针） |
| `GET /api/health/ready` | `main.py:688` | 同 handler 双路由装饰器 | Readiness probe（兼容路径） |
| `GET /api/health/services` | `health.py` | `router_registry.py:97` prefix=`/api` | 服务依赖检查（PG/TDengine/MongoDB/disk/system） |
| `GET /api/health/detailed` | `health.py` | `router_registry.py:97` prefix=`/api` | 详细健康检查（执行 shell 脚本，需认证） |
| `GET /api/reports/health/{timestamp}` | `health.py` | `router_registry.py:97` prefix=`/api` | 读取历史健康报告 |

### 1.2 分散在各模块的健康端点候选（历史样本，需重导 route table）

下表是 2026-05-14 文档沉淀的历史样本。2026-05-17 装饰器级扫描发现 46 个 health-like route decorators，但其中哪些真实注册、哪些带 router prefix、哪些只是示例或内嵌 app，必须以当前 route table 和 OpenAPI diff 为准。

| # | 文件 | 端点 | 响应格式 |
|---|------|------|----------|
| 1 | `api/trade/routes.py` | `/api/v1/trade/health` | `APIResponse` |
| 2 | `api/signal_monitoring/signal_history_response.py` | `/signals/health` | 自定义 |
| 3 | `api/metrics.py` | `/api/health` | 自定义 |
| 4 | `api/monitoring_old/routes.py` | `/health` | 裸响应 |
| 5 | `api/technical/routes.py` | `/api/v1/technical/health` | 裸响应 |
| 6 | `api/wencai.py` | `/health` | 自定义 |
| 7 | `api/announcement/routes.py` | `/api/announcement/health` | 裸响应 |
| 8 | `api/stock_ratings_api.py` | `/health` | `UnifiedResponse` |
| 9 | `api/advanced_analysis_api.py` | `/health` | `UnifiedResponse` |
| 10 | `api/advanced_analysis.py` | `/health` | 自定义 |
| 11 | `api/multi_source.py` | `/health` + `/health/{type}` + `/refresh-health` | `List[DataSourceHealthResponse]` |
| 12 | `api/risk_v31/system.py` | `/health` | `Dict[str, Any]` |
| 13 | `api/system/system_health.py` | `/health` + `/adapters/health` | `APIResponse` |
| 14 | `api/system/get_system_architecture.py` | `/database/health` | 自定义 |
| 15 | `api/backup_recovery_secure/cleanup_old_backups.py` | `/health` | 自定义 |
| 16 | `api/algorithms/get_algorithms_module.py` | `/health` | `UnifiedResponse` |
| 17 | `api/signal_monitoring/get_signal_statistics.py` | `/strategies/{id}/health/detailed` | 自定模型 |
| 18 | `api/multi_source.py` | 额外 2 个 `/health` 端点 | 按 source_type

### 1.3 历史健康端点一览（非当前执行清单）

以下清单只能作为 route table 重导的输入，不得直接作为删除清单。

```
GET /api/health/services           ← api/health.py via /api prefix
GET /api/health/detailed           ← api/health.py via /api prefix
GET /api/reports/health/{timestamp} ← api/health.py via /api prefix
GET /health/ready                  ← main.py
GET /api/health/ready              ← main.py
---
GET /api/v1/trade/health           ← trade
GET /signals/health                ← signal_monitoring
GET /api/health                    ← metrics / monitoring_old
GET /api/v1/technical/health       ← technical
GET /api/wencai/health             ← wencai
GET /api/announcement/health       ← announcement (package)
GET /api/.../health                ← stock_ratings
GET /api/.../health                ← advanced_analysis_api
GET /api/.../health                ← advanced_analysis (flat)
GET /multi-source/health           ← multi_source
GET /multi-source/health/{type}    ← multi_source
POST /multi-source/refresh-health  ← multi_source
GET /api/.../health                ← backup_recovery_secure
GET /api/.../health                ← algorithms
GET /api/v1/risk/health            ← risk_v31
GET /api/health                    ← system/system_health
GET /api/adapters/health           ← system/system_health
GET /api/database/health           ← system/get_system_architecture
GET /strategies/{id}/health/detailed ← signal_monitoring
```

---

## 二、问题分析

### 2.1 响应格式不一致

| 格式 | 使用端点 |
|------|----------|
| `{"status":"ok","service":"xxx"}` 裸响应 | trade, technical, announcement, monitoring_old |
| `UnifiedResponse` 包装 | stock_ratings, advanced_analysis |
| 自定义结构 | signal_monitoring, metrics, wencai |

裸响应通过 `ResponseFormatMiddleware` 间接包装，但依赖中间件不如显式使用 `UnifiedResponse` 可靠。

### 2.2 功能重复

每个模块的健康检查仅 ping 自身服务状态，与 `health.py` 的系统级综合探针功能重叠。Kubernetes / 负载均衡器通常只需要一个就绪探针端点，多个分散端点增加配置复杂度。

### 2.3 与 STANDARDS.md 对齐

STANDARDS.md §一.5 要求：
> 必须提供 `/health/ready` 探针（校验 DB/Redis 连通性）

当前 `/health/ready` 与 `/api/health/ready` 已实现此功能；未在当前代码中确认旧 `readiness` 变体。各模块碎片端点仍需治理，但删除前必须先确认监控、PM2、CI、OpenAPI 和前端调用是否依赖旧路径。

---

## 三、收敛方案口径

### 3.1 目标状态

目标不是立即删除所有分散端点，而是先明确 canonical 健康入口、兼容路径和退场条件。删除任何健康端点前，必须完成代码路径判定、功能树判定和 OpenSpec 审批。

### 3.2 逐模块处理

| # | 模块 | 动作 | 理由 |
|---|------|------|------|
| 1 | trade | 待判定 `/health` 是否为公开健康探针或内部 smoke 入口 |
| 2 | signal_monitoring | 待判定 `/signals/health` + `/strategies/{id}/health/detailed` 是否被前端或监控使用 |
| 3 | metrics | 待判定 `/health` 与 Prometheus 端点职责是否重叠 |
| 4 | monitoring_old | 待 B 方案完成双判定后再决定是否退役 |
| 5 | technical | 待判定 `/health` 是否仍被 smoke tests 使用 |
| 6 | wencai | 待判定 `/health` 是否仍被 smoke tests 使用 |
| 7 | announcement | 待判定 `/health` 是否作为领域 smoke 入口保留 |
| 8 | stock_ratings | 待判定 `/health` 是否作为领域 smoke 入口保留 |
| 9 | advanced_analysis_api | 待判定 `/health` 是否作为领域 smoke 入口保留 |
| 10 | advanced_analysis (flat) | 待 C 方案确认 flat/package canonical 后再处理 |
| 11 | multi_source | 待判定 3 个 health/refresh-health 端点是否承担数据源状态刷新职责 |
| 12 | risk_v31 | 待 I 方案确认 v31 canonical 后再处理 |
| 13 | system/system_health | 待判定 `/health` + `/adapters/health` 是否仍被系统页或测试使用 |
| 14 | system/get_system_architecture | 待判定 `/database/health` 是否仍被系统架构页使用 |
| 15 | backup_recovery_secure | 待判定 `/health` 是否仍被 smoke tests 使用 |
| 16 | algorithms | 待判定 `/health` 是否仍被 smoke tests 使用 |
| 17 | signal_monitoring | 待判定 `/strategies/{id}/health/detailed` 是否仍有业务含义 |
| 18 | multi_source | 待判定 `/refresh-health` 是否承担主动刷新职责 |

### 3.3 增强 canonical 健康端点（OpenSpec 候选）

如需在 `health.py` 中新增各子模块状态子项，应作为 OpenSpec design 内容，通过读取 readiness 探针体系统一暴露：

```python
# health.py 增强
@router.get("/health/services")
async def system_services_health():
    return {
        "overall_status": "healthy",
        "services": {
            "postgresql": {...},
            "tdengine": {...},
            "redis": {...},
            "mongodb": {...},
            # 新增 — 子模块运行时状态
            "api_modules": {
                "trade": check_module_health("trade"),
                "technical": check_module_health("technical"),
                "announcement": check_module_health("announcement"),
                "wencai": check_module_health("wencai"),
                "signal_monitoring": check_module_health("signal_monitoring"),
                "advanced_analysis": check_module_health("advanced_analysis"),
            }
        }
    }
```

若某模块需要细粒度自检（如 wencai 的外部 API 连通性），可评估通过 `check_module_health()` 分发到各模块的内置 `health_check()` 方法。是否退役原独立端点必须先确认消费者和兼容期。

---

## 四、提案前收敛路线（不直接实施）

### Step 1: 重导当前 route table

先从 FastAPI app 或 OpenAPI 生成当前真实路由表，区分：

| 类型 | 示例 |
|------|------|
| 平台 liveness/readiness | `/health`、`/health/ready`、`/api/health/ready` |
| 系统服务探针 | `/api/health/services`、`/api/health/detailed` |
| 领域 smoke 端点 | trade、technical、announcement、wencai、risk、strategy 等各域 `/health` |
| 运维或指标端点 | metrics、Prometheus、SSE monitoring、adapter/database health |
| 示例或内嵌 app | `models/base_example.py`、`app_factory.py` 等需确认是否生产暴露 |

### Step 2: 建消费者矩阵

对每个 health-like 端点补齐监控、PM2、CI、E2E、前端、外部调用和文档引用。没有消费者清单前，不得删除或改路径。

### Step 3: OpenSpec 设计项

健康端点收敛 proposal/design/tasks 至少说明：

| 设计项 | 必填内容 |
|--------|----------|
| canonical endpoint | 平台级 readiness/liveness 和系统服务探针的最终路径 |
| compatibility | 旧端点保留期、重定向或 wrapper 策略 |
| OpenAPI diff | 新旧路径、响应模型和状态码变化 |
| runtime smoke | PM2、`/api/health/services`、`/health/ready`、`/api/health/ready` |
| consumer proof | 监控、前端、测试、CI、脚本调用清单 |
| rollback | 任一探针失败时恢复旧端点或暂停退役的条件 |

### Step 4: 审批后分批收敛

审批通过后，优先处理无消费者且功能重复的端点；领域 smoke 端点保留、迁移或聚合都必须保留兼容期和验收记录。`monitoring_old/` 仍交由 B 文档的残留文件双判定处理。

---

## 五、验收

| 检查项 | 通过标准 |
|--------|----------|
| route table | 已导出当前真实 route table，health-like 端点有 canonical / smoke / metrics / 示例分类 |
| OpenAPI diff | 删除、重命名、响应模型或状态码变化均有 diff 和兼容说明 |
| canonical 探针正常 | `curl http://localhost:8020/api/health/services` 返回 200 + healthy |
| 就绪探针正常 | `curl http://localhost:8020/health/ready` 或 `curl http://localhost:8020/api/health/ready` 返回 ready |
| 错误路径清零 | 当前代码不得新增 `/health/readiness`，文档如引用必须标记为历史误判 |
| 旧端点处理 | 若决定退役，需 OpenAPI diff、监控调用清单和兼容期说明，不得只以 404 为验收 |
| PM2 正常 | `pm2 status` 显示 online |

---

*前置文档: `docs/reports/quality/backend-audit-2026-05-14.md` §五.5*
