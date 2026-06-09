# MyStocks 策略管理域代码结构治理

> **历史文档说明**:
> 本文件是策略域 API 结构治理草案，不是当前可直接执行的删除、移动或 router_registry 修改指令。
> 若需确认当前共享规则、审批门禁和实现状态，请优先以 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、当前代码与最近一次验证结果为准。

> **来源**: `docs/reports/quality/backend-audit-2026-05-14.md` §八.03 深化
> **审计日期**: 2026-05-14
> **复核日期**: 2026-05-17
> **执行门禁**: 策略域 canonical router、OpenAPI 暴露面、兼容 shim、测试/前端路径和旧文件退役均属于架构级变更，实施前必须创建并通过 OpenSpec proposal/design/tasks 审批。

2026-05-17 复核摘要：

| 扫描项 | 当前数量 / 结论 |
|--------|------------------|
| `api/strategy.py` | 存在，约 25KB / 742 行 |
| `api/strategy_mgmt.py` | 存在，约 29KB / 863 行 |
| `api/strategy_management.py` | 存在，101 bytes / 3 行，兼容 shim 候选 |
| `api/strategy_management/` | 存在，6 个 `.py` 文件 |
| `router_registry.py` 中 strategy 相关注册 | `VERSION_MAPPING["strategy"]`、`strategy_mgmt.router`、`strategy_management.router`、`strategy_list_mock.router` |
| 直接 `strategy_management.router` include | 当前确认 1 处，不是同一 router 双 include |
| 代码/测试/前端/脚本中 `/api/v1/strategy` 文本引用 | 84 |
| 代码/测试/前端/脚本中 `/api/strategy` 文本引用 | 120 |
| 代码/测试/前端/脚本中 `/strategies` 文本引用 | 155 |

结论：策略域确实多入口、多实现、多消费者并存，但不能用“内容已合并”作为删除依据。后续必须先做 endpoint inventory、OpenAPI diff、前端/测试消费者矩阵和兼容 shim 设计。

---

## 一、现状

策略管理域是后端代码结构最混乱的功能域。当前有 **4 套入口 + 3 套实现**：

### 1.1 文件清单

```
web/backend/app/api/
├── strategy.py              # flat: 23KB, 完整 API（/definitions /run/single /run/batch /results 等）
├── strategy_mgmt.py         # flat: 另一套完整 API（/strategies /import /export /backtest）
├── strategy_management.py   # flat: 1 行兼容 shim `from strategy_management import *`
├── strategy_list_mock.py    # flat: Mock 策略列表
└── strategy_management/     # package: 6 个 .py 文件
    ├── __init__.py           # 导出 router + get_xxx 函数
    ├── get_monitoring_db.py  # 主路由实现
    ├── get_backtest_result.py # 回测结果查询
    ├── backtest_status_contract.py
    ├── _strategy_management_task_tail.py
    └── monitoring_adapter.py

web/backend/app/services/
├── strategy_service.py      # 策略服务（被 strategy.py 使用）

web/backend/app/schemas/
├── strategy_schemas.py      # 策略 Schema 定义
```

### 1.2 路由注册情况

在 `router_registry.py` 中，2026-05-17 复核看到的当前状态为：

- `strategy.router` 通过 `VERSION_MAPPING["strategy"]` 注册到 `/api/v1/strategy`
- `strategy_mgmt.router` 直接注册，tags 为 `strategy-mgmt`
- `strategy_management.router` 直接注册一次，当前未确认同一 router 被 include 两次
- `strategy_list_mock.router` 直接注册一次
- 未确认同一个 `strategy_management.router` 在当前 `router_registry.py` 中被 include 两次

以下历史描述保留为旧风险线索，不得直接作为当前删除依据：

```python
# 1. strategy.py → /api/v1/strategy（通过 VERSION_MAPPING）
"strategy": strategy.router

# 2. strategy_mgmt.py → /api/strategy-mgmt（直接 include_router）
app.include_router(strategy_mgmt.router, tags=["strategy-mgmt"])

# 3. strategy_management.py (flat shim / package import 解析需确认) → 直接 include
app.include_router(strategy_management.router)

# 4. strategy_list_mock.py → mock 策略列表
app.include_router(strategy_list_mock.router)
```

### 1.3 服务层

`services/strategy_service.py` 是业务逻辑层，被 `strategy.py` 调用。`strategy_mgmt.py` 和 `strategy_management/` 是否有自己的 service 层需确认。

---

## 二、问题

### 2.1 三套 API 各有不同的端点集

| 端点 | `strategy.py` | `strategy_mgmt.py` | `strategy_management/` |
|------|:---:|:---:|:---:|
| `/definitions` | ✅ | ❌ | ❌ |
| `/run/single` | ✅ | ❌ | ❌ |
| `/run/batch` | ✅ | ❌ | ❌ |
| `/results` | ✅ | ❌ | ❌ |
| `/matched-stocks` | ✅ | ❌ | ❌ |
| `/stats/summary` | ✅ | ❌ | ❌ |
| `/strategies` | ❌ | ✅ | ✅ |
| `/import` | ❌ | ✅ | ❌ |
| `/export` | ❌ | ✅ | ❌ |
| `/backtest` | ❌ | ✅ | ✅ |
| `/models` | ❌ | ❌ | ✅ |
| `/train` | ❌ | ❌ | ✅ |

三个入口服务于不同的功能子集，没有一个是完整的。前端需要知道哪个端点去哪个路径。

### 2.2 双注册的 strategy_management

`strategy_management.py` (flat shim) 和 `strategy_management/` (package) 的导入解析关系需要重新核验。旧版审计曾认为同一组端点被注册两遍，但 2026-05-15 复核未在当前 `router_registry.py` 中确认同一 router 两次 include。

### 2.3 文件命名语义不清

- `strategy.py` — "策略执行 API"（run / results / matched-stocks）
- `strategy_mgmt.py` — "策略管理 API"（CRUD / import / export / backtest）
- `strategy_management/` — "策略管理拆分包"（CRUD / models / train / backtest）

`strategy_mgmt.py` 和 `strategy_management/` 名称仅差一个下划线，但功能有重叠也有差异。

---

## 三、目标架构口径

### 3.1 统一 Package 结构

```
web/backend/app/api/strategy/
├── __init__.py               # 重导出 router
├── routes.py                 # 所有端点（合并三套实现）
├── schemas.py                # ← strategy_schemas.py 迁移
└── service.py                # ← strategy_service.py 迁移（或保留在 services/）
```

### 3.2 端点全集

合并后 `routes.py` 应包含以下完整端点集：

| 端点 | 来源 | 说明 |
|------|------|------|
| `GET /definitions` | strategy.py | 策略定义列表 |
| `POST /run/single` | strategy.py | 单股策略执行 |
| `POST /run/batch` | strategy.py | 批量策略执行 |
| `GET /results` | strategy.py | 策略执行结果查询 |
| `GET /matched-stocks` | strategy.py | 匹配股票列表 |
| `GET /stats/summary` | strategy.py | 策略统计摘要 |
| `GET /strategies` | strategy_mgmt.py / strategy_management/ | 策略 CRUD |
| `POST /strategies` | strategy_mgmt.py | 创建策略 |
| `PUT /strategies/{id}` | strategy_mgmt.py | 更新策略 |
| `DELETE /strategies/{id}` | strategy_mgmt.py | 删除策略 |
| `POST /import` | strategy_mgmt.py | 导入策略 |
| `GET /export` | strategy_mgmt.py | 导出策略 |
| `POST /backtest` | strategy_mgmt.py / strategy_management/ | 执行回测 |
| `GET /backtest/status/{id}` | strategy_management/ | 回测状态查询 |
| `GET /backtest/result/{id}` | strategy_management/ | 回测结果查询 |
| `GET /models` | strategy_management/ | 模型列表 |
| `POST /models/train` | strategy_management/ | 训练模型 |
| `GET /models/train/status/{id}` | strategy_management/ | 训练状态 |

### 3.3 路由注册简化（OpenSpec 候选）

目标不是立即把所有入口删成一个，而是先定义 canonical strategy API、兼容入口和退役条件：

| 当前入口 | 当前事实 | 处理方向 |
|----------|----------|----------|
| `VERSION_MAPPING["strategy"]` / `strategy.router` | 当前注册到 `/api/v1/strategy` | 作为 canonical 候选之一，需与前端路径和 OpenAPI 对齐 |
| `strategy_mgmt.router` | 当前直接 include，tags 为 `strategy-mgmt` | 判定是否承载 CRUD/import/export/backtest 独有端点 |
| `strategy_management.router` | 当前直接 include 一次 | 判定 flat shim 与 package router 的 import 解析关系 |
| `strategy_list_mock.router` | 当前直接 include | 判定 mock 配置、测试和前端是否仍使用 |

任何路由删除、prefix 变化或 response model 变化都必须先进入 OpenSpec，并提供兼容期和 rollback。

---

## 四、提案前治理路线（不直接实施）

### Step 1: 端点全集确认

逐文件对比三套实现的端点定义，确认无遗漏。特别注意：
- `strategy.py` 使用的 `strategy_service.py` 是否被其他模块依赖
- `strategy_mgmt.py` 中 `/import` `/export` 功能的完整性
- `strategy_management/get_monitoring_db.py` 中模型训练和回测的异步任务链路

### Step 2: 建消费者矩阵

把 `/api/v1/strategy`、`/api/strategy`、`/strategies`、`strategy_management`、`strategy_mgmt` 等引用分成代码、测试、前端、脚本和文档五类。代码、测试、前端、脚本引用必须进入兼容判断，文档引用只作为迁移说明输入。

### Step 3: OpenSpec 设计项

策略域治理 proposal/design/tasks 至少说明：

| 设计项 | 必填内容 |
|--------|----------|
| canonical endpoint | 最终保留的 strategy API prefix、router 和 response model |
| endpoint parity | `strategy.py`、`strategy_mgmt.py`、`strategy_management/` 的端点对比 |
| compatibility | shim、旧 prefix、mock router 和前端路径兼容期 |
| OpenAPI diff | 新旧路径、方法、状态码和 schema 差异 |
| tests | import smoke、前端 API 调用、策略 CRUD、回测、模型训练和 mock 开关 |
| rollback | 任一 consumer 或 smoke 失败时恢复旧 router 或暂停退役 |

### Step 4: 判定旧文件

对 `strategy.py`、`strategy_mgmt.py`、`strategy_management.py`（shim）、`strategy_management/`（package）逐一补代码路径判定、功能树判定、测试引用清单和兼容职责。只有 OpenSpec 审批后才能删除或改路径。

### Step 5: 审批后更新 router_registry.py + VERSION_MAPPING

审批通过前不得修改 router_registry、VERSION_MAPPING、前端 API base path 或 mock router 注册。

---

## 五、删除清单

策略域收敛后，以下对象只能作为删除候选，不能直接删除：

| 候选对象 | 当前处理要求 |
|----------|--------------|
| `api/strategy.py` (23KB) | 先确认端点是否已完整迁入 canonical package，并跑 OpenAPI diff |
| `api/strategy_mgmt.py` | 先确认 `/import`、`/export`、`/backtest` 是否有 canonical 对应 |
| `api/strategy_management.py` | 先确认是否仍承担兼容 import 或 router 暴露职责 |
| `api/strategy_management/` (6 个 `.py` 文件) | 先确认 package 内容是否已迁入并有测试覆盖 |
| `api/strategy_list_mock.py` | 先确认 mock 配置、测试和前端是否仍引用 |

---

*前置文档: `docs/reports/quality/backend-audit-2026-05-14.md` §八.03*
