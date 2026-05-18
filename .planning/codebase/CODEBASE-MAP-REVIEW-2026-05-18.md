# MyStocks 代码库全局视野报告 (Codebase Map Review) — 修订版

> **生成日期**: 2026-05-18 (修订版)
> **分析工具**: gsd-map-codebase (全量刷新 + 实际测量)
> **基准对比**: v1.2 Lint & Test Zero (2026-04-10 已交付)
> **范围**: 全仓库（Python + TypeScript + 配置 + 测试）
>
> **使用说明**: 本文件是基于实际代码库遍历与 `ruff check` 实际执行生成的快照分析报告，非共享规则。当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`。
>
> **统计口径**: 常规文件/行数遍历排除 `.*` 隐藏目录、`__pycache__`、`node_modules`、`.venv`、`.git`、`archive/`。Python 统计 `.py` + `.pyi`；前端统计 `.ts` `.tsx` `.vue` `.js` `.mjs` `.scss` `.css`。备份文件 (.bak/.backup/.old) 独立扫描并单独标注，备份扫描不排除 `archive/`。
>
> **状态**: ✅ 已完成输入基线审核 — 可作为 issue 15 / future proposal 输入材料；本次审核不授权代码变更、旧文档替换、GitHub issue 创建或 OpenSpec proposal 创建。

---

## 目录

1. [技术栈总览 (STACK)](#1-技术栈总览-stack)
2. [架构全景 (ARCHITECTURE)](#2-架构全景-architecture)
3. [代码结构 (STRUCTURE)](#3-代码结构-structure)
4. [集成与数据流 (INTEGRATIONS)](#4-集成与数据流-integrations)
5. [代码规范与约定 (CONVENTIONS)](#5-代码规范与约定-conventions)
6. [Lint 实测结果](#6-lint-实测结果)
7. [测试现状 (TESTING)](#7-测试现状-testing)
8. [问题与关注点 (CONCERNS)](#8-问题与关注点-concerns)
9. [v1.2 后变化对比](#9-v12-后变化对比)
10. [建议路线（需独立评审，不由本报告授权）](#10-建议路线需独立评审不由本报告授权)

---

## 1. 技术栈总览 (STACK)

### 语言与运行时

| 层 | 语言 | 运行时 | 版本 |
|---|------|--------|------|
| 后端核心 | Python | CPython 3.12+ | FastAPI ≥0.104 |
| 后端 API | Python | Uvicorn | 端口 8020 |
| 前端 | TypeScript + Vue 3 | Vite 7.3 + Node.js 18+ | Vue 3.4+, Pinia 3.0 |
| 时序数据库 | SQL (TDengine) | TDengine 3.3+ | taospy ≥3.0 |
| 关系数据库 | SQL (PostgreSQL) | PostgreSQL 17+ TimescaleDB | psycopg2 + SQLAlchemy 2.0 |
| GPU (可选) | Python CUDA | PyTorch 2.1+, TensorFlow 2.15+ | src/gpu/ |

### 核心依赖

**后端 (pyproject.toml)**:
- 框架: FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0
- 数据: pandas 2.x, numpy, Redis 5.x, Celery 5.3
- 安全: python-jose, PyJWT, passlib[bcrypt]
- 异步: httpx, aiofiles, jinja2
- 可选: GPU (torch, tensorflow, cupy), 文档 (mkdocs)

**前端 (package.json)**:
- 核心: Vue 3, Pinia, Vue Router, Sass
- AI SDK: `ai` v6.0 (Kronos 推理集成)
- 验证: zod v4.3
- JSON渲染: @json-render/core + react (混合 React 组件)

**开发工具**:
- Python: pytest 7.4, ruff, black 23.x, isort 5.12, mypy 1.6, pylint 3.0, bandit 1.7
- 前端: Vitest 4.0, Playwright 1.57, Vite 7.3
- 部署: Docker, PM2 (ecosystem.test.config.js)
- 质量: pre-commit 3.5

### 配置入口

| 配置 | 位置 | 格式 |
|------|------|------|
| 环境变量 | `.env` / `.env.example` / `.env.data-sources.local` | dotenv |
| 后端设置 | `web/backend/app/core/config.py` | Pydantic Settings |
| 数据源注册 | `config/data_sources_registry.yaml` | YAML |
| Python lint | `pyproject.toml [tool.ruff]` | TOML |
| Python 类型 | `mypy.ini` | INI |
| Pytest | `pytest.ini` (优先) + `pyproject.toml [tool.pytest.ini_options]` | INI/TOML |
| 前端测试 | `vitest.config.mts` | TypeScript |
| E2E | `playwright.config.ts` | TypeScript |
| Pre-commit | `.pre-commit-config.yaml` | YAML |

---

## 2. 架构全景 (ARCHITECTURE)

### 高层分层

```
┌──────────────────────────────────────────┐
│  Frontend (Vue 3 + Pinia + TypeScript)    │  web/frontend/src/
│  前端源码统计                              │  1,180 文件 / ~243K LOC
├──────────────────────────────────────────┤
│  Backend API (FastAPI + Uvicorn)          │  web/backend/app/
│  API 路由 · services · core · middleware  │  548 .py 文件 / ~164K LOC
│  main.py — production ASGI/runtime entry  │
├──────────────────────────────────────────┤
│  Core Business (Python)                   │  src/  (web/backend/src/ → symlink)
│  适配器 · 算法 · 领域模型 · GPU · 监控   │  931 .py 文件 / ~203K LOC
│  UnifiedManager → 统一启动与协调          │
├──────────────────────────────────────────┤
│  Data Layer                               │
│  TDengine (时序) · PostgreSQL (关系)      │  src/data_access/ + src/database/
└──────────────────────────────────────────┘
```

### 架构模式

| 模式 | 位置 | 状态 |
|------|------|------|
| **Adapter Pattern** | `src/adapters/` (akshare, efinance, TDX, baostock, financial) | ✅ `src/` package duplication 已收敛；backend adapter lifecycle DI 仍待 #78 |
| **Factory Pattern** | `src/data_sources/factory.py`, `web/backend/app/services/data_source_factory/` | ✅ |
| **DDD (部分)** | `src/domain/` (72 files) → `src/application/` (36) → `src/infrastructure/` (29) | ⚠️ 部分实现 |
| **Repository Pattern** | `web/backend/app/repositories/` (12 files) | ✅ |
| **Middleware Chain** | `web/backend/app/middleware/` + `app/core/middleware/` | ✅ |

### 域边界 (来自 architecture/DOMAIN_BOUNDARIES.md)

1. **核心域** — `src/core/`: 生命周期、配置加载、数据库路由、统一入口
2. **数据访问域** — `src/data_access/`: TDengine/PostgreSQL 读写优化与去重
3. **业务服务域** — `src/services/` + `src/adapters/`: 量化任务与数据集成
4. **监控与质量域** — `src/monitoring/`: 系统稳定性、数据完整性、告警
5. **Web 与 API 域** — `web/backend/` + `web/frontend/`: 展示与外部交互

---

## 3. 代码结构 (STRUCTURE)

> **统计口径**: 遍历排除 `.*` 隐藏目录、`__pycache__`、`node_modules`、`.venv`、`.git`、`archive/`。

### Python 后端 (src/ — 931 文件, 203,290 行)

| 模块 | 文件数 | 行数 | 占比 | 说明 |
|------|--------|------|------|------|
| `gpu/` | 92 | 27,811 | 13.7% | GPU 加速计算 |
| `monitoring/` | 86 | 21,813 | 10.8% | 监控系统 |
| `adapters/` | 101 | 20,661 | 10.2% | 数据源适配器 |
| `core/` | 67 | 15,690 | 7.8% | 核心业务逻辑 |
| `advanced_analysis/` | 84 | 15,120 | 7.5% | 高级分析 |
| `ml_strategy/` | 38 | 12,718 | 6.3% | 机器学习策略 |
| `data_sources/` | 34 | 10,601 | 5.3% | 数据源管理 |
| `application/` | 36 | 7,422 | 3.7% | DDD 应用层 |
| `algorithms/` | 24 | 7,041 | 3.5% | 算法库 |
| `mock/` | 43 | 6,912 | 3.4% | Mock 数据 |
| `domain/` | 72 | 6,519 | 3.2% | DDD 领域模型 |
| `storage/` | 33 | 6,317 | 3.1% | 存储层 |
| `services/` | 44 | 6,210 | 3.1% | 业务服务 |
| `governance/` | 30 | 6,155 | 3.0% | 治理模块 |
| `data_access/` | 22 | 5,944 | 2.9% | 数据访问层 |
| `utils/` | 29 | 5,636 | 2.8% | 工具函数 |
| `database/` | 22 | 5,498 | 2.7% | 数据库管理 |
| `infrastructure/` | 29 | 3,657 | 1.8% | DDD 基础设施 |
| `interfaces/` | 12 | 2,790 | 1.4% | 接口/协议定义 |
| 其他 | 23 | 4,641 | 2.3% | visualization, trading, indicators 等 |

> `web/backend/src/` 是 `src/` 的 **symlink**，非独立副本。

### 前端 (web/frontend/src/ — 1,180 文件, 242,526 行)

> 常规前端统计不含 12 个备份文件 (.bak/.backup/.old)；备份文件见问题清单单独统计。

| 模块 | 说明 |
|------|------|
| `views/` (471 files) | 页面视图，26 个子域 |
| `components/` (185 files) | UI 组件 |
| `api/` (92 files) | API 客户端 + 类型 |
| `utils/` (66 files) | 工具函数 |
| `types/` (71 files) | TypeScript 类型定义 |
| `composables/` (26 files) | Vue Composables (src/composables/) |
| `services/` (28 files) | 前端服务层 |
| `stores/` (28 files) | Pinia 状态管理 |
| `layouts/` (25 files) | 布局组件 |
| `router/` (4 files) | 路由配置 |
| 其他 | styles, config, i18n, mock, workers 等 |

### 后端 API (web/backend/app/ — 548 .py 文件, 164,362 行)

| 模块 | 说明 |
|------|------|
| `api/` (194 files) | API 路由 |
| `services/` (152 files) | 业务服务层 |
| `core/` (77 files) | FastAPI 核心 |
| `backtest/` (27 files) | 回测引擎 |
| `models/` (21 files) | ORM 模型 |
| `schemas/` (16 files) | Pydantic schemas |
| `repositories/` (12 files) | Repository 模式 |
| 其他 | mock, adapters, middleware, tasks 等 |

### 测试

| 范围 | 文件数 | 行数 | 说明 |
|------|--------|------|------|
| `tests/` (test_*.py) | 654 | 165,518 | pytest 收集的测试文件 |
| `tests/` (所有 .py) | 817 | 197,810 | 含非测试框架文件 |
| `web/backend/tests/` (.py) | 178 | 45,009 | 后端 API 层测试 |
| 前端 .spec.ts | 183 | — | Vitest (STATE 记录 840 全通过) |

---

## 4. 集成与数据流 (INTEGRATIONS)

### 典型业务流路径

> 这是一条典型业务 API 流。控制面接口不完全服从这条路径：平台 liveness/readiness、service health/status summary、compat redirect、legacy raw endpoint 可能绕过 `UnifiedResponse`、保留 runtime redirect，或通过 `include_in_schema=False` 从 OpenAPI 中隐藏。

```
User Request → FastAPI Route (web/backend/app/api/)
    → Service Layer (web/backend/app/services/)
    → Core Business (src/ → web/backend/src/ symlink)
    → Adapter (src/adapters/) → External API (akshare/efinance/TDX)
    → Data Access (src/data_access/) → Database (TDengine/PostgreSQL)
    → UnifiedResponse → User
```

> 控制面例外需要单独建模：`GET /health` = platform liveness，`GET /health/ready` = canonical readiness，`GET /api/health/ready` = compatibility readiness，`GET /api/health/services` = system services health，`/health/readiness` intentionally absent，`/api/strategy-mgmt/{path:path}` runtime route 仍存在，且在 OpenAPI schema 中隐藏。

### 关键集成点

| 集成 | 路径 | 状态 |
|------|------|------|
| WebSocket 实时推送 | `web/backend/app/api/websocket.py` + 前端 `composables/useWebSocket*.ts` | ✅ |
| Socket.IO | `web/backend/app/core/_socketio_manager_singleton.py` | ⚠️ 兼容保留 (STATE 记录) |
| Health / readiness / services health / compat redirect | `GET /health`, `GET /health/ready`, `GET /api/health/ready`, `GET /api/health/services`, `/api/strategy-mgmt/{path:path}` (hidden) | ✅ 控制面接口独立建模，需按 probe taxonomy 与 OpenAPI 暴露策略单独治理 |
| Kronos AI 推理 | `@ai` SDK v6.0 (contract-first) | ✅ |
| GPU 加速 | `src/gpu/` (92 文件) | ✅ 可选 |
| Celery 任务队列 | 已配置 | ✅ |
| 监控告警 | `src/monitoring/` → Email/Webhook | ✅ |

> 兼容状态说明: `/api/strategy-mgmt/{path:path}` 保留运行时 redirect，runtime route 仍存在，但从 OpenAPI schema 隐藏；`/health/readiness` intentionally absent。`OpenAPI path count` 是基于 `app.openapi()`、当前 router 注册与 `include_in_schema=False` 策略生成的快照字段，必须随采集时点一起记录，不能单独当作静态真相源。

---

## 5. 代码规范与约定 (CONVENTIONS)

### Python 代码质量工具

| 工具 | 配置 | 关键参数 |
|------|------|----------|
| **Ruff** | `pyproject.toml [tool.ruff]` | line-length=120, target-version=py39 |
| **Black** | `pyproject.toml [tool.black]` | line-length=120 |
| **isort** | `pyproject.toml [tool.isort]` | profile=black |
| **mypy** | `mypy.ini` | strict 类型检查 |
| **pylint** | `.pylintrc` | 代码质量 |
| **bandit** | dev dependency | 安全扫描 |
| **pre-commit** | `.pre-commit-config.yaml` | 提交前自动检查 |

### 覆盖阈值配置冲突

> ⚠️ 存在双配置冲突，需治理：

| 配置文件 | cov-fail-under | 优先级 |
|----------|----------------|--------|
| `pyproject.toml [tool.pytest.ini_options]` | **80%** | 被 pytest.ini 覆盖 |
| `pytest.ini` (根目录) | **30%** | pytest 默认使用此配置 |
| `config/pyproject.toml` | 80% | 非活跃配置 |

**当前有效门禁**: 以 `pytest.ini` 的 **30%** 为准。`pyproject.toml` 的 80% 与 `pytest.ini` 的 30% 矛盾，需治理后统一。

### 架构红线 (来自 architecture/STANDARDS.md v3.1)

1. **方案先行 (Proposal-First)**: 架构变更必须先审批
2. **六步走战略**: 契约先行 → 单体骨架 → Mock 驱动 → 垂直切片 → 可观测性 → 自动化防护
3. **单一真相源**: 同职责只允许一个主实现
4. **迁移自带收口**: 任何重构必须明确退出条件
5. **禁止机械拆分**: 文件拆分按语义边界，不按体积
6. **清理需两层判定**: 代码路径 + 功能树同时确认

---

## 6. Lint 实测结果

> **执行命令**: `ruff check . --select F821 --output-format json`
> **执行时间**: 2026-05-18

### F821 (undefined-name) 分 Scope 结果

| Scope | F821 错误数 | 涉及文件数 | 状态 |
|-------|------------|-----------|------|
| `src/` | **0** | 0 | ✅ 清零 (v1.2 已验证) |
| `web/backend/app/` | **61** | 11 | ❌ 未修复 |
| `web/` (其他) | 11 | 5 | ❌ 未修复 |
| `tests/` | **291** | 37 | ❌ 未修复 |
| `scripts/` | **240** | 39 | ❌ 未修复 |
| other | 1 | 1 | ❌ |
| **TOTAL** | **604** | — | — |

**关键结论**:
- `src/` 范围内 F821 确认为 **0**，v1.2 收口保持有效。
- 但全仓库 F821 仍有 **604 个**，分布在 `tests/`(291)、`scripts/`(240)、`web/backend/app/`(61) 中。
- 此前报告书写的 "F821=0" 未限定 scope，构成事实错误。

### 非 F821 Ruff 错误

> 本次未重新执行全量 ruff。以下基于 v1.2 STATE 记录（历史快照）：

| 指标 | v1.2 收口记录 | 本次实测 |
|------|-------------|----------|
| F821 src/ | 0 | ✅ 0 (已确认) |
| F821 全仓库 | 未记录 | **604** (本次实测) |
| 非 F821 ruff | 47 | 未重新测量 |

---

## 7. 测试现状 (TESTING)

### 测试框架与规模

| 维度 | Python (pytest) | 前端 (Vitest) | E2E (Playwright) |
|------|-----------------|---------------|-------------------|
| 测试文件 | 654 test_*.py + 178 web/backend/tests/ | 183 .spec.ts | 已配置 |
| 配置 | `pytest.ini` (30%) + `pyproject.toml` (80%, 被覆盖) | `vitest.config.mts` | `playwright.config.ts` |
| 标记 | unit, integration, gpu, database, slow 等 | — | — |

### 测试执行状态

> **重要**: 以下区分 "历史记录" (STATE.md 记载) 与 "本次实测"。

| 指标 | 历史记录 (v1.2 STATE) | 本次实测 |
|------|----------------------|----------|
| 前端 Vitest 通过 | 840 tests, 全通过 ✅ | **未重新执行** |
| 前端 Vitest 文件数 | 231 files | **未重新执行** |
| Python pytest 通过 | 未记录 | **未执行** |
| Python 覆盖率 | 上次 0.16% (2026-01-03) | **未执行** |

> **注意**: 本报告的测试状态无法标注绿色通过，因为 `pytest`、`pytest --cov`、`vitest` 均未在本次分析中实际执行。

### 局部实测证据

以下结果是 `consolidate-backend-health-endpoints` 与当前 backend API workline 的局部证据（关键提交：`c62caa05e`；本轮复核 HEAD: `dc21371ba`），不等同于全量 pytest / coverage / Vitest / E2E 通过，但可支撑 health/status/OpenAPI taxonomy、消费者契约等价与控制面接口治理判断：

| 项 | 结果 |
|----|------|
| `pytest web/backend/tests/test_dashboard_data_source.py web/backend/tests/test_health_route_conflicts.py --no-cov -q` | 114 passed |
| `pytest web/backend/tests/test_performance_middleware_endpoint_labels.py --no-cov -q` | 3 passed |
| touched backend files `ruff check` | passed |
| OpenAPI targeted smoke | `duplicate_operation_id_warnings=0`, `paths=500`；`paths=500` 是基于 `app.openapi()`、当前 router 注册与 `include_in_schema=False` 策略的快照值 |

本轮同时暴露两个更具体的测试债务，不应被泛化为“tests 有 F821”：

| 测试债务 | 风险 |
|----------|------|
| `web/backend/tests/test_strategy_management_mock_configuration.py` 导入 `app.api.strategy_management.get_monitoring_db` 模块后 monkeypatch `module.settings` | 夹具目标与当前模块边界错位，后续 mock 配置测试应回到 canonical dependency seam |
| `web/backend/tests/test_week1_strategy_api.py::test_list_backtest_results_empty` 仍接受 legacy list shape 或 `items` shape | response shape 断言仍需和 canonical strategy/backtest contract 对齐 |

### 测试关注点

1. ⚠️ **Python 覆盖率未知**: `pytest --cov` 自 2026-01 以来未重新运行
2. ⚠️ **tests/ 目录含少量空子目录**: 如 `tests/cron/`, `tests/playwright-report/`, `tests/test-results/`, `tests/unit/infrastructure/backup_recovery/` — 可能为占位或生成产物目录
3. ⚠️ **测试目录名污染**: 部分目录以 `.py` 结尾 (如 `tests/test_xxx.py/`)
4. ⚠️ **F821 在 tests/ 中有 291 个**: 测试代码本身存在未定义名称

---

## 8. 问题与关注点 (CONCERNS)

### 🔴 P0 — 阻塞性问题

**无已确认的 P0 阻塞性问题。**

### 架构审查口径 (Matt Pocock skills)

本节按 Matt Pocock `improve-codebase-architecture` 口径重排问题优先级：优先看 **seam** 是否清晰、模块是否足够 **deep**、canonical 实现是否唯一、迁移是否有收口条件、测试面是否落在接口而不是实现细节上。F821、coverage、备份文件等质量/卫生问题仍保留，但不作为架构优先级排序的主要依据。

> **重要**: 以下架构项是候选问题清单，不定义新接口、不授权移动/删除/重命名文件。任何涉及 API、schema、composition root、service seam 的改动，都必须按 STANDARDS.md 与 OpenSpec Proposal-First 流程独立审批。

### Current Workline Delta (2026-05-18)

本节记录第三、第四条线对本报告的增量校准。它是事实快照与 issue 对齐表，不授权发布 issue、创建 OpenSpec proposal 或进入实现。

| Observation | GitHub issue / workline | Current state | Evidence artifact | Next gate |
|-------------|-------------------------|---------------|-------------------|-----------|
| Health/OpenAPI verification | `#31` health/OpenAPI workline | Done as local gate, not full test proof | `c62caa05e`; `test_health_route_conflicts.py` originally 112/112; OpenAPI targeted smoke `paths=500`, `duplicate_operation_id_warnings=0` | Keep as local evidence; full pytest/cov/Vitest/E2E remains unverified |
| Strategy path migration | GH #75 | Closed; URL migrated to canonical path, but post-review parser fix showed URL migration alone was insufficient | GH #75 comment cites commit `8d68ecc97`; current `dashboard_data_source.py` calls `/api/v1/strategy/strategies` with `user_id` and parses canonical `data.items` | Add consumer contract parity gate to every API migration closure |
| Orphan API triage | GH #76 | Closed as `0 actual dead-code orphan`; scanner still reports false positives | `docs/reports/quality/generated/backend-fullpath-route-table.json` reports `orphan_routes=16`, `orphan_files=[algorithms/_naive_bayes_router.py, algorithms/get_algorithms_module.py]`; GH #76 records both as false positives via package `__init__.py` import chains | Track scanner limitation; do not delete scanner-reported files without package/import-chain triage |
| Exception hierarchy | GH #77 | Open active backlog | Live review count at HEAD `dc21371ba`: `web/backend/app/api` has `raise HTTPException=100`, HTTPException import lines `6`, across `6` files | Continue per-file batches; regenerate live count before each batch and avoid stale `440` / `301` counts without commit + command |
| Adapter lifecycle DI | GH #78 | Open, `needs-triage`; OpenSpec lifecycle proposal required before implementation | Issue body: 6 adapter singletons, `app.state` lifecycle + `Depends()` target | Decide proposal/approval path before implementation |
| Service lifecycle DI | GH #79 | Open, `needs-triage`; depends on #78 pattern validation | Issue body: 12 service singletons, stateful lifecycle risk | Do after #78 and approved lifecycle proposal |

**Artifact freshness guard**: 当前 review verified HEAD 为 `dc21371ba`。`backend-fullpath-route-table.json` 的 `git_head` 仍为 `4327ddf22 fix(audit): trace include_router chains in route scanner, regenerate baseline`，`generated_at=2026-05-18T11:09:14.509706`，因此只能作为 stale-aware evidence 使用。后续引用 route table、HTTPException count、F821 count、GitNexus impact 或 OpenAPI path count 时，必须同时记录 `generated_at`、`git_head`、`current_head_checked_at_review` 与 `stale_if_head_mismatch`。

### 🟡 P1 — 高优先级

#### 1. Service seam 与 canonical service 未收口

| 文件/模块 | 观察 |
|----------|------|
| `web/backend/app/services/__init__.py` | `IntegratedServices` 同时承担服务聚合、懒加载、fallback 与 service locator 职责 |
| `web/backend/app/services/data_api_new.py` | 通过 `spec_from_file_location()` 按路径加载 `api/data/data_api_new.py` |
| `web/backend/app/api/data/data_api_new.py` | 定义 `DataApiService`，但被 service 层反向加载 |
| `web/backend/app/services/risk_management_new.py` | 仍通过 `services/__init__.py` 挂入 `IntegratedServices` |
| `web/backend/app/services/risk_management_2.py` | 存在扩展风险管理实现，但未进入 canonical 挂载路径 |
| `web/backend/app/services/data_adapter_new.py` | 新拆分适配器的聚合 facade，缺少清晰退出说明 |

**架构问题**: 这不是单纯 `_new` / `_2` 命名问题，而是 service seam 方向不清。Service 层反向按文件路径加载 API 层实现，调用方无法判断哪个模块是接口、哪个是迁移 shim、哪个是最终 canonical 实现。`IntegratedServices` 又把多个服务以全局聚合对象暴露，削弱了 locality：理解一个数据 API 或风险服务调用，需要同时看 API package、service shim、service registry 和旧命名模块。

**建议方向**: 先定义 `DataApiService` 与 risk management 的 canonical 服务入口，再决定 shim 是否保留。API route 应依赖 service seam，而不是 service 反向加载 API 文件。每个 shim 必须有 owner、退出条件和测试面。Singleton lifecycle 需要分两段承接：adapter singleton lifecycle 对应 GH #78，优先作为低风险 `Depends()` / `app.state` 迁移验证；service singleton lifecycle 对应 GH #79，依赖 #78 验证模式后再进入。

#### 2. API flat→package 迁移残留未进入问题清单

ADR-0002 已定义 **package 目录是 canonical 目标形态**，flat 文件只应作为有退出条件的过渡 shim。当前 `web/backend/app/api/` 仍存在 flat 文件与 package 目录同名的迁移残留：

| 同名域 | 风险 |
|--------|------|
| `algorithms` | flat/package 并存，canonical route 入口需确认 |
| `backup_recovery_secure` | flat/package 并存，router 注册与 import 路径需确认 |
| `indicators` | flat/package 并存，迁移退出条件需确认 |
| `signal_monitoring` | flat/package 并存，功能域入口需确认 |
| `stock_search` | flat/package 并存，旧入口是否仍承担兼容职责需确认 |
| `system` | flat/package 并存，VERSION_MAPPING / router_registry 需复核 |

**架构问题**: API 域入口不唯一会让 router registration truth 变弱，也会让测试和前端契约生成难以知道哪个路径是当前事实。GH #75 还证明：URL 迁到 canonical path 不等于迁移闭环，旧调用方传 `user_id`、canonical response 使用 `data.items` 时，caller parser 与 response shape 必须同步验证，否则会出现“issue 已关闭但运行时返回空数据”的假闭环。

**建议方向**: 每个同名域补一条 migration closure 记录：package 覆盖范围、flat 是否仍被 import、`docs/FUNCTION_TREE.md` / router_registry 状态、删除或保留条件。

**closure record 最小证据口径**:

| 证据项 | 说明 |
|--------|------|
| package 覆盖范围 | canonical package 目前覆盖哪些 route、service、schema 与测试入口 |
| flat 文件 import 状态 | flat 文件是否仍被 backend、tests、scripts、frontend contract 或动态注册引用 |
| router registry 状态 | `router_registry` / `VERSION_MAPPING` 是否仍把 flat 文件作为事实入口 |
| 功能树状态 | `docs/FUNCTION_TREE.md` 中对应功能节点是否标为有效、兼容保留、重复冗余、下线或待判定 |
| route table diff | FastAPI route table 的 added/removed/changed path、methods、endpoint module |
| OpenAPI diff | `app.openapi()` 的 path、operationId、schema exposure 变化 |
| 消费者矩阵 | 前端、测试、CI、脚本、监控、PM2/Docker 中的消费者路径 |
| 消费者契约等价 | path、query 参数、response shape、caller parser、OpenAPI examples 与最小回归测试必须同时对齐 |
| 退出条件 | 删除、保留、runtime-only shim 或 documented compat shim 的判定依据 |

#### 3. CSRF policy 存在重复 composition root

| 文件 | 观察 |
|------|------|
| `web/backend/app/main.py` | canonical runtime truth，定义 `CSRFTokenManager`、`csrf_manager`、middleware 与 `/api/csrf-token` |
| `web/backend/app/app_factory.py` | secondary composition root candidate / test factory / historical residue；也定义 `CSRFTokenManager`、`csrf_manager` 与 CSRF middleware |

**架构问题**: 这不是 `main.py` 行数问题，而是安全策略、token 生命周期、middleware 注册点在两个 composition root 形态中重复存在。测试面也会变模糊：测试应该覆盖 `main.py` 的 token manager，还是 `app_factory.py` 的 token manager？

**建议方向**: 先确认 `app_factory.py` 的角色：正式迁移目标、测试工厂，还是历史残留。随后再决定是否提取 CSRF module。不得仅以文件体积为依据拆分。

#### 4. Error contract canonicalization 未收口

| 项 | 当前快照 |
|----|----------|
| GH issue | #77 open: Consolidate backend exception types into canonical hierarchy |
| live count | 见下方固定字段块 |
| 涉及文件 | `announcement/routes.py`, `data_source_registry.py`, `ml.py`, `notification.py`, `strategy_mgmt.py`, `trade/routes.py` |

Live count at HEAD `dc21371ba`:

- raise HTTPException: 100
- HTTPException import lines: 6
- affected files: 6

**架构问题**: 这不是普通清理项，而是 error contract seam。裸 `HTTPException` 会绕过 canonical exception hierarchy，影响 API error response format、OpenAPI response examples、前端错误处理与测试断言。GH #77 body 中的 `440` 是 issue 创建时静态数；本文只把本轮 live count 作为当前快照，后续执行必须重新生成。

**建议方向**: 作为独立 API contract debt lane 承接，不并入 API flat→package migration closure。每个文件按小批次迁移，保持 status code 与中文 detail 不变，并用 canonical exception handler 的 response shape 做回归验证。

#### 5. Schema dual directory 影响 API contract seam

`web/backend/CONTEXT.md` 已记录 `app/schema/` 与 `app/schemas/` 并存：`app/schemas/` 是 business schema 的 canonical 位置，`app/schema/validation_models.py` 仍存在。

**架构问题**: Schema 是 API contract 的测试面。双目录会让请求/响应模型、校验模型、生成类型和导入路径的真相源不清。

**建议方向**: 将 `schema/validation_models.py` 合并到 `schemas/`，或记录它仍作为独立 seam 的原因，并定义退出条件。

#### 6. Orphan / scanner 口径必须三分

| 分类 | 判定口径 |
|------|----------|
| scanner-reported orphan | route scanner 没有从 `router_registry.py` / `include_router` 链追踪到的文件或 route |
| false positive due package/import chain | 不在 include_router 链上，但通过 package `__init__.py`、dynamic factory 或 registered parent module 可达 |
| actual deletion candidate | 无 route 注册、无 package/import-chain 消费者、无前端/测试/脚本消费者，并通过 STANDARDS.md 两层删除判定 |

**当前事实**: `docs/reports/quality/generated/backend-fullpath-route-table.json` 仍报告 `orphan_routes=16` 与 2 个 orphan files：`algorithms/_naive_bayes_router.py`、`algorithms/get_algorithms_module.py`。GH #76 已关闭为 `0 actual dead-code orphan`，原因是这两个文件为 package `__init__.py` import chain false positive。后续 agent 不得把 scanner 输出直接当作删除授权。

### 🟢 P2 — 中优先级

#### 7. `views/composables/` 需要按接口深度分类

`web/frontend/src/views/composables/` 中 10 个非测试 composable 的消费者分析：

| 文件 | 消费者数 | 分类建议 |
|------|----------|----------|
| `useTradingDashboard.ts` | 4 | 🟢 共享 composable |
| `tradingDashboardActions.ts` | 2 | 🟢 共享 composable |
| `usePhase4Dashboard.ts` | 1 (views/demo/) | 🟡 view-local (demo) |
| `usePyprofilingDemo.ts` | 1 (views/PyprofilingDemo.vue) | 🟡 view-local |
| `useTechnicalAnalysis.ts` | 1 (内部互引) | 🟡 内部引用链 |
| `useTechnicalAnalysis.shortcuts.ts` | 1 (内部互引) | 🟡 内部引用链 |
| `useTechnicalAnalysis.types.ts` | 1 (内部互引) | 🟡 内部引用链 |
| `useAnalysis.ts` | 0 | 🔴 无消费者 |
| `useEnhancedDashboard.ts` | 0 | 🔴 无消费者 |
| `useSettings.ts` | 0 | 🔴 无消费者 |

**架构问题**: 路径不是唯一判断标准。真正要看 composable 是否提供有深度的 interface：封装状态、生命周期、交互流程和错误处理的 composable 可以作为 deep module；只搬运函数、types、shortcuts 的文件可能是 shallow extraction。

**建议方向**: 按 deep/shallow 分类：共享状态型、view-local workflow 型、纯工具/类型、无消费者候选。无消费者候选仍需按 STANDARDS.md 两层删除判定处理。

#### 8. 全仓库 F821 与覆盖率配置是质量门禁问题

| 项 | 状态 |
|----|------|
| F821 | 全仓库 604；`src/` 为 0，`tests/` 291，`scripts/` 240，`web/backend/app/` 61 |
| 覆盖率配置 | `pyproject.toml` 写 `--cov-fail-under=80`，`pytest.ini` 写 `--cov-fail-under=30` |

**判断**: 这两项会影响交付门禁和质量基线，但不是本报告中的主要架构问题。应在架构 seam 收口之外独立治理。

#### 9. 核心文档与 codebase 文档过期

| 文档 | 问题 |
|------|------|
| `src/README.md` | 创建日期 2025-10-19；声称 "64+ 文件"，当前为 931 文件；TODO 与目录树过期 |
| `architecture/INDEX.md` | 最后更新 2026-02-02，文档计数未反映后续变更 |
| `.planning/codebase/` 旧 7 文档 | 最后 mapped 2026-04-05，仍报告已删除目录、旧 F821、旧 main 入口数量 |

#### 10. 前端备份文件是源码树卫生/迁移治理问题

`web/frontend/src/` 中 **12 个** `.bak` / `.backup` 文件 (共 ~523 KB)。经实际搜索，未发现任何非备份源文件通过 `import`、`require`、`import.meta.glob` 或 `require.context` 直接引用这些备份文件。主要问题是源码树卫生、归档策略和迁移退出条件，而非已验证的构建污染风险。

### ⚪ P3 — 低优先级

#### 11. 24 个 part*.py 文件存在于非 src/ 范围

| 位置 | 数量 | 示例 |
|------|------|------|
| `scripts/` | 6 | `scripts/dev/analysis/.../part1.py` |
| `tests/` | 12 | `tests/adapters/.../part1.py` |
| `web/backend/app/` | 6 | `web/backend/app/repositories/.../part1.py` |
| `src/` | **0** | — |

`src/` 范围内为 0（v1.0 已验证）。其余 24 个存在于 scripts/、tests/、web/backend/app/ 的子目录中。

#### 12. 其他低优先级

- `views/demo/` 仍存在 (12 项) — STATE.md 已记录为 "kept as reference code"
- 后端 services 80+ 个 .py 文件与 15+ 个子目录混合
- `src/monitoring/` 与 `monitoring-stack/` 命名不一致
- TODO 残留: src/ 中 16 个 (0 个 FIXME)

---

## 9. v1.2 后变化对比

### ✅ v1.0 → v1.2 已验证的修复 (src/ 范围)

| 问题 | v1.0 | 当前 | 验证方式 |
|------|------|------|----------|
| 适配器层重复 | ❌ | ✅ `src/interfaces/adapters/` 已删除 | 目录不存在 |
| 前端 case-conflict | ❌ 3 对 | ✅ 全部 lowercase | 仅 lowercase 存在 |
| 重复数据访问层 | ❌ 4 层 | ✅ `data_access_pkg`, `db_manager` 已删除 | 目录不存在 |
| 路由错位 | ❌ 24 废弃文件 | ✅ `src/routes/`, `src/api/` 已删除 | 目录不存在 |
| 根级 shim | ❌ 存在 | ✅ `core.py`, `data_access.py`, `monitoring.py` 已删除 | 文件不存在 |
| 前端多入口 | ❌ 8 个 main | ✅ 仅 `main-standard.ts` | 唯一入口 |
| `part*.py` in src/ | ❌ | ✅ **0 个 in src/** (全仓库 24 个) | 遍历验证 |
| `*_new.py` in src/ | ❌ | ✅ **0 个 in src/** (backend 仍有 5 个) | 遍历验证 |

### ⚠️ v1.2 遗留 + 新发现的问题

| 问题 | 状态 | 优先级 |
|------|------|--------|
| Service seam / canonical service 未收口 (`DataApiService`, risk management, `IntegratedServices`) | issue 15 决策输入；issue 1/14/15 前不新建实现 issue | P1 |
| API flat→package 迁移残留 (6 个同名域) | issue 14 evidence + issue 15 decision；先证据后决策 | P1 |
| CSRF policy 重复 composition root (`main.py` + `app_factory.py`) | 当前 3-issue package 未覆盖；未来独立 proposal candidate | P1 |
| Schema dual directory (`schema/` + `schemas/`) | 当前 3-issue package 未覆盖；未来 API contract proposal candidate | P1/P2 |
| Health/status endpoint taxonomy 与 probe consumer matrix | OpenSpec 28/29，剩余 4.7 stateful gate 待批准或 named equivalent | P1/P2 |
| PM2 integration workflow gate 未执行完整闭环 | 待显式批准或 approved named equivalent | P1/P2 |
| F821 全仓库 604 (src=0, tests=291, scripts=240, web/backend/app=61) | 未修复 | P2 |
| 覆盖率配置冲突 (80 vs 30) | 待治理 | P2 |
| `views/composables/` 需按接口深度分类 | 待审计 | P2 |
| `src/README.md` 过期 (2025-10) | 待更新 | P2 |
| `.planning/codebase/` 全过期 (2026-04-05) | 待刷新 | P2 |
| `architecture/INDEX.md` 过期 (2026-02-02) | 待更新 | P2 |
| 前端 .bak 文件 (12 个) | 未清理 | P2/P3 |
| part*.py 在 scripts/tests/backend (24 个) | 待审计 | P3 |

### OpenSpec Publication Alignment

本 codebase map 是输入材料，不是 issue publication plan，也不能绕过当前 backend OpenSpec 发布包形成新的实现 backlog。当前正式发布包为：

1. `01-approve-orchestration.md` — approval gate，`ready-for-human`
2. `14-build-shared-evidence-package.md` — C/E/F evidence-only，`needs-triage`
3. `15-decide-post-approval-plan.md` — human decision/design issue，`ready-for-human`

| Concern | Existing OpenSpec / issue package relationship | Publication disposition |
|---------|-----------------------------------------------|-------------------------|
| Service boundary / `IntegratedServices` | E/F evidence + issue 15 decision；GH #78/#79 lifecycle DI 是相关但独立的 approved-proposal path | issue 1 approval、issue 14 evidence package、issue 15 split decision 前，不创建新的 implementation issue；#78/#79 也不得绕过 OpenSpec lifecycle approval |
| API flat→package closure | C route/OpenAPI evidence + issue 14/15；GH #75 暴露 consumer contract parity gate | evidence first, decision later；closure record 必须覆盖 path、query、response shape、caller parser 与最小回归测试 |
| Error contract canonicalization | GH #77 已存在；不属于当前 3-issue publication package | active backlog；使用 live count 快照，不复用 stale `440` / `301` 口径 |
| CSRF composition root | 当前 3-issue package 未覆盖 | separate proposal candidate，需走独立 approval gate |
| Schema dual directory | 当前 3-issue package 未覆盖 | separate API contract proposal candidate，需走独立 approval gate |
| F821 / coverage | quality debt lane | 不属于 OpenSpec publication package |

Evidence-only 工作若落在 C/E/F scope 内，应路由到 issue 14；人工决策应路由到 issue 15，或由 issue 15 明确批准拆分后的未来决策项。P3 已解决的 announcement / strategy / risk canonical router 决策不得由本 codebase map 重新生成新 issue；若后续发现新证据，只能作为 evidence note 进入现有 approval / decision flow。

---

## 10. 建议路线（需独立评审，不由本报告授权）

> **重要**: 以下仅为观察项清单，不构成执行授权。任何涉及重命名、删除、提取模块的操作，必须按 STANDARDS.md "方案先行" 规则独立走 Proposal/Approval 流程。

### 建议后续动作

1. **Service seam 收口评审**: 先作为 issue 15 的人工决策输入，围绕 `DataApiService`、risk management、`IntegratedServices`、GH #78 adapter lifecycle DI 与 GH #79 service lifecycle DI 判断 canonical service 入口、shim 方向、lifecycle owner 和测试面；只有在 issue 1 approval 通过、issue 14 evidence package 完成、issue 15 明确是否拆分后，才决定是否创建额外 OpenSpec proposal；GH #78/#79 的实现还必须等待对应 lifecycle proposal 获批。
2. **API flat→package migration closure**: 对 `algorithms`、`backup_recovery_secure`、`indicators`、`signal_monitoring`、`stock_search`、`system` 六个同名域补齐 package 覆盖范围、flat shim 退出条件、router_registry / VERSION_MAPPING 状态。兼容层需分为 `active and documented`、`runtime-only hidden from schema`、`retired` 三种状态，不能把所有 shim 等同于应删除。每个域的 closure record 至少要包含：package 覆盖范围、flat 文件是否仍被 import、`docs/FUNCTION_TREE.md` 状态、`router_registry` / `VERSION_MAPPING` 状态、route table diff、OpenAPI diff、前端/测试消费者矩阵、path/query/response shape/caller parser/OpenAPI examples/minimal regression test 的消费者契约等价证据，以及删除或保留的退出条件。
3. **Control-plane endpoint governance closure**: 补齐 health/status taxonomy、OpenAPI schema exposure、PM2/CI/frontend probe consumer matrix，以及完整 PM2 stateful gate 或 approved named equivalent 的审批策略。
4. **CSRF composition root 决策**: 明确 `main.py` 与 `app_factory.py` 的关系，再决定 CSRF policy 是迁入单独 module、保留在 composition root，还是通过 FastAPI dependency seam 注入。
5. **Schema dual directory 收口**: 处理 `web/backend/app/schema/validation_models.py` 与 `web/backend/app/schemas/` 的 canonical contract 关系。
6. **Error contract canonicalization**: 将 GH #77 作为独立 API contract debt lane 承接，执行前按当前 HEAD 重新生成 `raise HTTPException` 与 import live count，并验证 canonical exception handler response shape。
7. **Issue / artifact freshness closure**: 对 GH #75-#79、route table、OpenAPI、HTTPException、F821 与 GitNexus impact 证据补齐 `generated_at`、`git_head`、`current_head_checked_at_review`、`stale_if_head_mismatch`。
8. **版本控制收口**: 若本文档仍是未跟踪文件并准备进入版本控制，建议使用干净路径级提交，只提交 `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md`，不要与源码或其他脏文件混合；替换旧 `.planning/codebase/` 文档前，必须先记录 adoption record：Reviewer、Approval timestamp、Documents replaced、Evidence artifacts used、artifact 是否已落盘/待补齐/豁免，以及“本次批准不授权代码变更”的显式声明。
9. **审计 views/composables/**: 按接口深度分类，而不只按消费者数量分类；区分共享状态型、view-local workflow 型、纯工具/类型、无消费者候选。
10. **统一 F821 与 coverage 质量基线**: 明确各 scope 的 F821 目标值，治理 `pytest.ini`(30%) 与 `pyproject.toml`(80%) 的覆盖率阈值冲突，并重新运行 pytest + coverage 获取真实基线。
11. **刷新文档**: 更新 `src/README.md`、`architecture/INDEX.md`、`.planning/codebase/` 7 文档，使其反映当前 canonical seam、控制面接口 taxonomy 与迁移状态。
12. **清理类事项后置**: `.bak/.backup` 与 `part*.py` 先按 STANDARDS.md 两层删除判定确认功能状态，再归档、删除或登记技术债。

### 本报告的定位

本报告是 **全局视野快照**，可用于：
- 替换 `.planning/codebase/` 下 7 个过期文档（审核通过后）
- 作为后续 `improve-codebase-architecture`、`gsd-audit-fix` 等深度审查的参考基线
- 作为 OpenSpec proposal / issue 15 决策输入材料，但不得直接开新的实现 issue
- 记录事实快照、风险候选与 evidence 链接；health/status/OpenAPI/PM2 等控制面执行证据应优先引用 [backend-health-status-implementation-boundary-2026-05-18.md](docs/reports/quality/backend-health-status-implementation-boundary-2026-05-18.md)、[backend-health-status-openapi-stabilization-2026-05-18.md](docs/reports/quality/backend-health-status-openapi-stabilization-2026-05-18.md)、[backend-health-status-residual-blockers-2026-05-18.md](docs/reports/quality/backend-health-status-residual-blockers-2026-05-18.md)
- 若用于替换旧 `.planning/codebase/` 文档，替换前必须先记录 adoption record：Reviewer、Approval timestamp、Documents replaced、Evidence artifacts used、Evidence Artifact Index 中各 artifact 的实际路径或“待补齐/豁免”状态、以及“本次批准不授权代码变更”的显式声明

### Adoption Review Record

| Field | Current value |
|---|---|
| Reviewer | Human maintainer in current review thread |
| Approval timestamp | 2026-05-18 20:02:23 CST |
| Decision | Approved as an input baseline for issue 15 / future proposal planning |
| Documents replaced | None |
| Evidence artifacts used | This report and targeted review against the current backend OpenSpec `01 -> 14 -> 15` publication package |
| Evidence artifacts still pending | See Evidence Artifact Index below |
| Authorization boundary | 不授权代码变更；不授权旧 `.planning/codebase/` 文档替换；不授权 GitHub issue 创建；不授权 OpenSpec proposal 创建；不授权实现工作 |
| Next gate | Before replacing old `.planning/codebase/` documents, record exact documents replaced and concrete evidence artifact paths |

本报告 **不能直接用于**:
- 授权重命名、删除或移动任何文件
- 作为修复路线的唯一依据
- 替代 STANDARDS.md 的 Proposal-First 流程
- 作为控制面接口执行状态的唯一事实源；执行状态仍以 OpenSpec tasks 与 `docs/reports/quality/` 下的具体 evidence 报告为准

---

## 附录 A: 数据采集方法

| 数据项 | 方法 | 排除条件 |
|--------|------|----------|
| Python 文件/行数 | `os.walk()` 遍历，UTF-8 逐行计数 | `.*` 隐藏目录、`__pycache__`、`node_modules`、`.venv`、`.git`、`archive/` |
| 前端文件/行数 | 同上，扩展名 `.ts` `.tsx` `.vue` `.js` `.mjs` `.scss` `.css` | 同上 |
| 测试文件计数 | `test_*.py` 前缀匹配（排除 `_test_` 为前缀的非测试辅助文件） | 同上 |
| F821 | `ruff check . --select F821 --output-format json` 实际执行 | — |
| part*.py | 全仓库 `os.walk()` 遍历 | `.*` 隐藏目录、`__pycache__`、`node_modules`、`.venv`、`.git` |
| 备份文件 | 文件名结尾匹配 `.bak` `.backup` `.old` 或含 `.backup.` | 独立扫描，不排除 `archive/` |
| 消费者分析 | 正则匹配 import/require 语句中的符号引用 | 排除自身和备份文件 |
| FastAPI route table | 遍历 `app.routes`，记录 final path、methods、`include_in_schema`、endpoint module | — |
| OpenAPI schema | `app.openapi()`，记录 path count、added/removed paths、duplicate operationId warnings | 必须标注采集时点与 `include_in_schema` 策略 |
| Probe consumer matrix | 扫描 `.github/workflows/`、`config/`、`scripts/`、PM2/Docker 配置中的 health/status URL | — |
| HTTPException live count | 遍历 `web/backend/app/api/**/*.py`，统计 `raise HTTPException`、HTTPException import lines 与文件列表 | 必须记录当前 HEAD；不得复用 issue body 中的旧静态 count |
| Artifact freshness | 对 route table、OpenAPI、F821、HTTPException、GitNexus impact 等生成物记录 `generated_at`、`git_head`、`current_head_checked_at_review`、`stale_if_head_mismatch` | HEAD 不一致时只能作为 stale-aware evidence |
| 前端 Vitest | 基于 STATE.md v1.2 历史记录 (未重新执行) | — |
| Pytest | 基于文件计数，未执行 `pytest --collect-only` 或 `pytest --cov` | — |

> `OpenAPI path count` 是快照字段。运行时兼容路由若设置 `include_in_schema=False`，可能导致 path count 变化但不代表运行时路由已删除。

### Evidence Artifact Index

以下 artifact 路径是 adoption record 前建议保留或补齐的可复核证据链，目前是建议清单，不代表这些证据包均已落盘；若对应文件尚未落盘，adoption record 必须明确标为“待补齐”或“豁免”，且不应把本报告视为已替代旧 `.planning/codebase/` 文档。

| Evidence | Command | Output artifact | Generated at / git_head | Current-head freshness | Notes |
|----------|---------|-----------------|-------------------------|------------------------|-------|
| F821 scope count | `ruff check . --select F821 --output-format json` | `.planning/codebase/generated/f821-scope-count-2026-05-18.json` | Pending unless artifact exists | Must record current HEAD at adoption | `src=0`, total=604；需保留原始 JSON 或 hash |
| File/LOC count | `os.walk()` file/LOC collector | `.planning/codebase/generated/file-loc-count-2026-05-18.json` | Pending unless artifact exists | Must record current HEAD at adoption | 排除隐藏目录、`archive/` 与生成目录的口径需写入 artifact |
| Route/OpenAPI snapshot | FastAPI route table + `app.openapi()` capture | `.planning/codebase/generated/route-openapi-snapshot-2026-05-18.json` or `docs/reports/quality/generated/backend-fullpath-route-table.json` | `backend-fullpath-route-table.json`: `generated_at=2026-05-18T11:09:14.509706`, `git_head=4327ddf22...` | Stale against review HEAD `dc21371ba`; set `stale_if_head_mismatch=true` | 记录 path count、`include_in_schema`、operationId duplicate warnings 与 route table diff；scanner false positives must be documented |
| HTTPException live count | `web/backend/app/api/**/*.py` scan for `raise HTTPException` and imports | `.planning/codebase/generated/http-exception-count-2026-05-18.json` | Review-time live count at HEAD `dc21371ba` | Fresh only for `dc21371ba`; regenerate after HEAD changes | Current snapshot: `raise HTTPException=100`, import lines `6`, files `6` |
| Probe consumer matrix | 扫描 `.github/workflows/`、`config/`、`scripts/`、PM2/Docker 配置 | `.planning/codebase/generated/probe-consumer-matrix-2026-05-18.json` | Pending unless artifact exists | Must record current HEAD at adoption | 记录 health/status URL 消费者与 probe owner |
| OpenSpec publication package | `docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md` | `docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md` | 2026-05-18 | Review against current 01 -> 14 -> 15 package | 记录发布顺序、labels 与 do-not-publish 决策；不授权额外 issue/proposal |

## 附录 B: 与旧 codebase/ 文档差异摘要

| 旧文档声称 (2026-04-05) | 本次实测 (2026-05-18) | 说明 |
|------------------------|----------------------|------|
| "908 test files" | 654 test_*.py | 旧统计含大量非测试文件 |
| "1,173 F821 errors" | 604 F821 (src=0) | src/ 已清零，其余 scope 仍有 |
| "8 main entry files" | 1 (main-standard.ts) | ✅ 已收敛 |
| "src/interfaces/adapters/ exists" | 已删除 | ✅ |
| "3 case-conflict pairs" | 0, 全部 lowercase | ✅ |
| "src/data_access_pkg exists" | 已删除 | ✅ |
| "src/routes/, src/api/ exist" | 已删除 | ✅ |
| "Root shims exist" | 已删除 | ✅ |
| "part*.py files exist" | 24 个 (0 in src/) | 旧报告未限定 scope |
| "0 F821 in src/" | ✅ 确认 0 | 但全仓库 604 |
| "66 mock files" | 43 (计数口径不同) | 需统一口径 |

---

> **状态**: ✅ **输入基线审核通过 (修订版)**
>
> 本修订版修正了初版中以下事实错误：
> - F821=0 → 分 scope: src=0, tests=291, scripts=240, web/backend/app=61
> - 架构审查优先级从“质量/卫生项在前”重排为“service seam、API flat/package、CSRF composition root、schema dual directory 在前”
> - 文件计数已按统一口径重新测量
> - part*.py 从 "0" 改为 "src/ 范围内 0，全仓库 24"
> - 覆盖率门禁从 "80%" 改为 "pytest.ini=30% 为当前有效，pyproject.toml=80% 存在冲突"
> - 前端备份文件从 11 改为 12，构建污染风险已降级
> - views/composables/ 从 "全部迁移" 改为按消费者分类
> - CSRFTokenManager 从 "按体积提取" 改为跨引用分析
> - 测试/前端状态区分"历史记录"与"本次实测"
>
> **本次审核仅批准本文档作为 issue 15 / future proposal 输入基线；不授权代码变更、旧文档替换、GitHub issue 创建或 OpenSpec proposal 创建。**
