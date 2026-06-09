# MyStocks API Flat→Package 迁移路线图

> **历史文档说明**:
> 本文件是 API flat/package 迁移审计快照和方案草案，不是当前路由契约或迁移实施指令。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、`web/backend/app/router_registry.py`、`web/backend/app/api/VERSION_MAPPING.py` 与当前代码为准。

> **来源**: `docs/reports/quality/backend-audit-2026-05-14.md` §四.1 深化
> **审计日期**: 2026-05-14
> **复核日期**: 2026-05-16
> **事实源**: `router_registry.py` + `VERSION_MAPPING.py` + 实际代码
> **执行门禁**: 本文涉及 API 路由、OpenAPI 暴露面和兼容 import 面，实施前必须创建并通过 OpenSpec proposal/design/tasks 审批。

---

## 一、现状全景

### 1.1 路由注册总览

`router_registry.py` 是目前的路由注册事实源。以下是各功能域的注册情况：

| 功能域 | flat 文件 | package 目录 | 当前注册/依赖事实 | 状态 |
|--------|-----------|--------------|------------------|------|
| 市场数据 | `market.py`，约 0KB shim；`market_v2.py`，约 18KB | `market/`，5 个 `.py` | `router_registry.py` 的 `router_modules["market"]` 指向 `market.router` | 需判定 shim 是否仍承担兼容职责 |
| 公告 | `announcement.py`，约 17KB | `announcement/`，2 个 `.py` | `router_modules["announcement"]` 已使用 `announcement.router`；另有直接 `include_router(announcement.router, prefix="/api")` | 存在双前缀暴露风险，需端点级对比 |
| 策略 | `strategy.py`，约 25KB；`strategy_management.py`，约 0KB shim；`strategy_mgmt.py`，约 28KB | `strategy_management/`，6 个 `.py` | `strategy` 通过 VERSION_MAPPING 注册；`strategy_management.router` 另行直接注册 | 多入口，需 H 文档继续重测 |
| 风控 | `risk_management.py`，约 1KB shim；`risk_management_core.py`，约 6KB；`risk_management_v31.py`，约 1KB facade | `risk/`，6 个 `.py`；`risk_v31/`，3 个 `.py` | `router_registry.py` 当前直接 `include_router(risk.router)` | 多入口，需 I 文档继续重测 |
| 监控 | `monitoring.py`，约 21KB；`monitoring_analysis.py`，约 27KB；`monitoring_watchlists.py`，约 39KB | 无 `monitoring/` package；存在 `monitoring_old/`，2 个 `.py` | `monitoring` 通过 VERSION_MAPPING 注册；`monitoring_analysis` 和 `monitoring_watchlists` 另行注册 | 需先判定旧目录与 flat 模块职责 |
| 数据 | 无 `data.py` flat | `data/`，13 个 `.py` | 当前已是 package 形态 | 不应再按 flat-to-package 迁移处理 |
| 交易 | 无 `trade.py` flat | `trade/`，5 个 `.py` | 当前已是 package 形态 | 不应再按 flat-to-package 迁移处理 |
| 技术分析 | 无 `technical.py` flat | `technical/`，2 个 `.py` | 当前已是 package 形态 | 不应再按 flat-to-package 迁移处理 |
| 系统 | `system.py`，约 0KB shim | `system/`，4 个 `.py` | 当前存在 shim 与 package | 需判定 shim 是否仍承担兼容职责 |
| 指标 | `indicators.py` 存在；`indicator_registry.py` 也直接注册 | 未发现 `indicators/` package | 不是同名 flat/package 迁移，需单独判定 |
| 认证 | `auth.py`，约 27KB | 无 `auth/` package | 仍是 flat 主实现 | 不属于本轮迁移候选 |

### 1.2 Flat 文件角色分类

| 类型 | 特征 | 代表文件 | 数量 |
|------|------|----------|------|
| **完整实现** | 包含 `router = APIRouter()` + 业务端点定义 | `announcement.py`, `strategy.py`, `strategy_mgmt.py`, `monitoring*.py` | 待端点级对比 |
| **兼容 shim / facade** | 文件很小，重导出或代理 package router | `market.py`, `strategy_management.py`, `risk_management.py`, `risk_management_v31.py`, `system.py` | 待兼容面判定 |
| **已 package 化域** | 当前没有同名 flat 主实现 | `data/`, `trade/`, `technical/` | 不应继续纳入 flat-to-package 清理实施计划 |
| **旧目录候选** | 目录名带 `_old`，内部仍定义 router | `monitoring_old/` | 待功能树判定 |

---

## 二、逐域详情

### 2.1 公告域（高风险 — 双前缀暴露待核验）

```
api/
├── announcement.py          # flat: 16KB, 完整 API（/fetch /list /today /important /monitor-rules 等）
└── announcement/
    ├── __init__.py           # 从 routes.py 重导出 router
    └── routes.py             # package: 27KB, 完整 API（与 flat 高度重复）
```

**注册情况**:
1. `announcement.router` (flat) 通过 VERSION_MAPPING 以 `/api/v1/announcement` 注册
2. `announcement.router` (package) 通过 `include_router` 以 `/api` + `/announcement` = `/api/announcement` 再注册

**问题**: 当前既通过 VERSION_MAPPING 进入 `/api/v1/announcement`，又通过直接 `include_router(announcement.router, prefix="/api")` 暴露 `/api/announcement`。是否为同一批端点、是否存在对外兼容依赖，需要用 route table 和 OpenAPI diff 验证。

**处理要求**: 先做端点级对比和消费者扫描；只有 OpenSpec 明确 canonical、兼容期和回滚条件后，才能调整注册或退役其中一个入口。

### 2.2 市场数据域（🟡 中等 — 兼容 shim）

```
api/
├── market.py                # flat: 1 行 `from market import *` — 纯兼容 shim
└── market/
    ├── __init__.py           # 导出所有 market_data_request 函数 + router
    ├── market_data_request.py # 主路由实现
    ├── market_request_models.py
    ├── _market_heatmap_router.py
    └── health_check.py
```

**注册情况**: `market.py` 是薄 shim，但当前写法为 `from market import *`，需要确认运行时是否解析到预期 package，不能只按文件大小判定。

**问题**: 当前 `router_modules["market"]` 指向 `market.router`。若直接切到 `app.api.market.router`，可能改变 import 解析、异常路径或 OpenAPI 暴露顺序。

**处理要求**: 先补 import 面扫描、运行时导入测试和兼容期说明；若要改变注册入口，进入 OpenSpec。

### 2.3 策略管理域（高风险 — 多入口待 H 文档重测）

```
api/
├── strategy.py              # flat: 23KB, 完整 API（/strategies /definitions /run/single /run/batch /results 等）
├── strategy_management.py   # flat: 1 行 `from strategy_management import *` — 兼容 shim
├── strategy_mgmt.py         # flat: 完整 API 的另一套实现（/strategies /import /export /backtest）
└── strategy_management/
    ├── __init__.py           # 导出 get_monitoring_db 等
    ├── get_monitoring_db.py  # 主路由实现
    ├── get_backtest_result.py
    ├── _strategy_management_task_tail.py
    ├── backtest_status_contract.py
    └── monitoring_adapter.py
```

**当前复核**:
- `strategy.router` 通过 VERSION_MAPPING 注册。
- `strategy_management.router` 在 `router_registry.py` 中另行直接注册。
- `strategy_mgmt.py` 仍存在，是否仍被注册需由 H 文档结合当前 `router_registry.py` 和前端调用继续重测。

**问题**: 这里不是单纯 flat-to-package 迁移，而是策略域 canonical 决策。不同入口可能服务不同前端页面、测试或历史 API。

**处理要求**: 交给 H 文档先补 router_registry 事实、前端消费者和测试引用；canonical 选择必须进入 OpenSpec。

### 2.4 风控域（高风险 — 多入口待 I 文档重测）

```
api/
├── risk_management.py       # flat: 完整 API
├── risk_management_core.py  # flat: 核心逻辑 API
├── risk_management_v31.py   # flat: v3.1 版 API
├── risk/                    # package
└── risk_v31/                # package (v3.1)
```

**当前复核**: `router_registry.py` 当前直接 `include_router(risk.router)`，`risk_management.py` 更像兼容 shim，`risk_management_core.py` 与 `risk_management_v31.py` 仍需判定是否被导入、测试或外部调用依赖。

**处理要求**: 交给 I 文档先补 router_registry 事实、风险域消费者和兼容期判定；canonical 选择必须进入 OpenSpec。

### 2.5 监控域（中风险 — flat 主实现与旧目录并存）

```
api/
├── monitoring.py            # flat: 主监控 API
├── monitoring_analysis.py   # flat: 分析 API
├── monitoring_watchlists.py # flat: 自选股监控
├── monitoring_old/          # 旧目录，内部仍定义 router
└── (无 monitoring/ package) # ⚠️ 仍未从 flat 迁移到 package
```

**处理要求**: `monitoring_old/` 不能只凭目录名退役。先确认 route table、测试引用和功能树状态；若要创建 `monitoring/` package 或改变 endpoint 暴露面，进入 OpenSpec。

---

## 三、迁移优先级矩阵

| 域 | 当前问题 | 风险 | 下一步 | OpenSpec |
|----|----------|------|--------|----------|
| 公告 | 可能存在双前缀暴露 | 中 | route table + OpenAPI diff | 必须 |
| 策略 | 多入口 canonical 不明 | 高 | H 文档先重测 router_registry、前端调用和测试引用 | 必须 |
| 风控 | 多入口 canonical 不明 | 高 | I 文档先重测 router_registry、导入面和测试引用 | 必须 |
| 监控 | flat 主实现与 `monitoring_old/` 并存 | 中 | 判定 `monitoring_old/` 功能树状态；若创建 package 则进入提案 | 条件触发 |
| 市场 | 0KB shim 与 package 并存 | 低到中 | 判定 shim 兼容面和运行时 import 解析 | 条件触发 |
| 系统 | 0KB shim 与 package 并存 | 低到中 | 判定 shim 兼容面和运行时 import 解析 | 条件触发 |
| 数据/交易/技术分析 | 当前已是 package 形态 | 低 | 从本迁移计划中移出，只保留验收扫描 | 不需要 |
| 认证/指标/TDX | 当前不是同名 flat/package 并存 | 低 | 不纳入本迁移批次 | 不需要 |

---

## 四、分阶段实施路线（仅限提案前复核）

### Phase 1: 判定兼容 shim（1 天，低风险）

先判定纯兼容 shim 是否仍被测试、文档、运行时字符串或外部调用依赖。只有补齐代码路径判定、功能树判定和兼容期说明后，才能把 `router_registry.py` 变更登记为候选任务。

| 动作 | 说明 |
|------|------|
| 判定 `api/market.py` | 确认是否仅 1 行 `from market import *`，并扫描所有 import 面 |
| 判定 `api/strategy_management.py` | 确认是否仅 1 行 `from strategy_management import *`，并扫描所有 import 面 |
| 形成候选动作 | 若确需改变 `router_registry.py`，先写入 OpenSpec tasks，不在本文直接执行 |

**验收**: 先完成 import 面扫描、route table 快照和 OpenAPI diff；若进入实施，再按 OpenSpec tasks 执行 pytest 与 PM2 smoke。

### Phase 2: 判定 `monitoring_old/`（0.5 天，低到中风险）

确认 `monitoring_old/` 是否仍被注册、测试、文档或外部调用依赖。只有功能树状态明确为重复冗余或正式下线，才可进入后续清理批次。

### Phase 3: 监控域 package 化提案（1 天，中风险）

```
api/monitoring/              # 新建
├── __init__.py               # 重导出
├── routes.py                 # ← monitoring.py 内容
├── analysis.py               # ← monitoring_analysis.py 内容
└── watchlists.py             # ← monitoring_watchlists.py 内容
```

若需要创建 `monitoring/` package，必须先提交 OpenSpec proposal/design/tasks，明确 endpoint 保持策略、兼容期和回滚条件。本文不直接要求移动文件或调整 flat 入口。

### Phase 4: 公告域收敛提案（1 天，中风险）

1. 对比 `announcement.py` vs `announcement/routes.py` 功能差异
2. 生成 route table 和 OpenAPI diff，确认两个前缀是否都需保留
3. 在 OpenSpec 中声明 canonical、兼容路径和回滚触发条件
4. 审批后再调整 `VERSION_MAPPING` 或 `router_registry.py`

### Phase 5: 交易/技术分析/数据/系统/指标双注册消除（2 天，中风险）

当前 `data/`、`trade/`、`technical/` 已是 package 形态，不应继续按统一模板处理。对 `system.py` 这类 shim，先判定兼容面；对 `indicators.py`、`metrics.py` 等非同名 package 情况，另行按功能域治理。

### Phase 6: 策略域收敛（3 天，高风险）

需要先由 H 文档完成事实重测，再进入 OpenSpec。不得在本文中直接决定 canonical。

### Phase 7: 风控域收敛（2 天，高风险）

需要先由 I 文档完成事实重测，再进入 OpenSpec。不得在本文中直接决定是否合并为单一 `risk/` package。

---

## 五、当前 `router_registry.py` 事实与候选动作

```python
def register_api_routes(app, *, use_mock_apis, logger):
    router_modules = {
        "market": market.router,
        "strategy": strategy.router,
        "trade": trade.router,
        "trading_runtime": trading_runtime.router,
        "monitoring": monitoring.router,
        "technical": technical_analysis.router,
        "data": data.router,
        "system": system.router,
        "indicators": indicators.router,
        "tdx": tdx.router,
        "announcement": announcement.router,
    }

    for key, config in VERSION_MAPPING.items():
        if key in router_modules:
            app.include_router(router_modules[key], prefix=config["prefix"], tags=config["tags"])

    app.include_router(auth_compat.compat_router, prefix="/api/auth", tags=["auth-compat"])
    app.include_router(akshare_market.router)
    app.include_router(data_quality.router, prefix="/api", tags=["data-quality"])
    app.include_router(metrics.router, prefix="/api", tags=["metrics"])
```

当前事实说明：

1. `market`、`strategy`、`announcement`、`monitoring`、`data`、`system`、`indicators`、`tdx`、`trade` 都由 `router_modules` 进入 `VERSION_MAPPING` 循环。
2. `strategy_management.router`、`risk.router`、`sse_endpoints.router`、`industry_concept_analysis.router`、`akshare_market.router` 等还以独立 `include_router` 方式存在。
3. `announcement` 仍同时存在 `VERSION_MAPPING` 和额外 `include_router(announcement.router, prefix="/api")` 的双前缀暴露风险。
4. `market.py`、`strategy_management.py`、`system.py`、`risk_management.py` 这类小文件需先按 shim/facade 判定，再决定是否允许进入提案。

## 六、需要先进入 OpenSpec 的候选动作

| 候选动作 | 当前状态 | OpenSpec |
|----------|----------|----------|
| 调整 `announcement` 路由暴露面 | 需要 route table 与 OpenAPI diff | 必须 |
| 改写 `market.py` 或 `strategy_management.py` 的 shim 行为 | 需要先判定兼容期和消费者 | 必须 |
| 退役 `monitoring_old/` | 需要先确认注册、测试和运行时字符串 | 条件触发 |
| 统一 `risk/` 与 `risk_v31/` canonical | 需要先重测风控域 | 必须 |
| 统一 `data/`、`trade/`、`technical/` 的迁移叙事 | 它们已是 package 形态 | 不需要 |

## 七、当前迁移结论

1. 这份文档仍然说明“flat/package 混杂”这个大问题，但不能再把所有域简单归类为同一种 flat 入口处理模板。
2. `data`、`trade`、`technical` 已经 package 化，不应继续列入本轮 flat-to-package 清理实施计划。
3. `market`、`strategy_management`、`system`、`risk_management` 更像兼容 shim / facade，处理前必须先判定兼容面。
4. `announcement` 是当前最像“需要 OpenSpec 的路由暴露面调整”的候选，但仍要先做 route table、OpenAPI 和消费者扫描。
5. `monitoring_old/` 需要 H/G 这类文档先重测，不应在本文件直接下退役结论。

*前置文档: `docs/reports/quality/backend-audit-2026-05-14.md` §四.1*
