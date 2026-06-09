# MyStocks 风控域代码结构治理

> **历史文档说明**:
> 本文件是风控域 API / service 结构治理草案，不是当前可直接执行的删除、移动或 router_registry 修改指令。
> 若需确认当前共享规则、审批门禁和实现状态，请优先以 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、当前代码与最近一次验证结果为准。

> **来源**: `docs/reports/quality/backend-audit-2026-05-14.md` §八.04 深化
> **审计日期**: 2026-05-14
> **复核日期**: 2026-05-17
> **执行门禁**: 风控域 canonical router、OpenAPI 暴露面、shim/compat 退役、service 版本合并和测试/前端路径变化均属于架构级变更，实施前必须创建并通过 OpenSpec proposal/design/tasks 审批。

2026-05-17 复核摘要：

| 扫描项 | 当前数量 / 结论 |
|--------|------------------|
| `api/risk_management.py` | 存在，37 行，兼容 shim 候选 |
| `api/risk_management_core.py` | 存在，159 行，核心 API 候选 |
| `api/risk_management_v31.py` | 存在，22 行，v31 兼容候选 |
| `api/risk_management.py.bak` | 不存在 |
| `api/risk/` package | 6 个 `.py` 文件 |
| `api/risk_v31/` package | 3 个 `.py` 文件 |
| `services/risk_management_new.py` | 存在，297 行 |
| `services/risk_management_2.py` | 存在，643 行 |
| `services/risk_management/` package | 6 个 `.py` 文件 |
| `router_registry.py` 中 risk 注册 | 仅 `from .api import risk` + `app.include_router(risk.router)` |
| 代码/测试/前端/脚本中 `risk_management` 文本引用 | 108 |
| 代码/测试/前端/脚本中 `app.api.risk` 文本引用 | 32 |
| 代码/测试/前端/脚本中 `/api/v1/risk` 文本引用 | 45 |
| 代码/测试/前端/脚本中 `/api/risk` 文本引用 | 54 |
| 代码/测试/前端/脚本中 `/risk/` 文本引用 | 168 |

结论：风控域当前是“canonical `risk` package + 多个 legacy API/service 版本 + 高引用消费者”并存。不能把它简化成“删除旧 API、保留一个 service”这种单线方案。后续必须先做 endpoint inventory、OpenAPI diff、消费者矩阵和兼容职责判定。


---

## 一、现状

风控域不是单纯“多几个旧文件”，而是 canonical package、兼容 shim、legacy API、legacy service 和版本化子包并存的混合态。

### 1.1 文件清单

```
web/backend/app/api/
├── risk_management.py       # flat: 兼容 shim 候选
├── risk_management_core.py  # flat: 核心风控 API 候选
├── risk_management_v31.py   # flat: v3.1 版兼容候选
├── risk/                    # package: 风控路由包
│   ├── __init__.py
│   ├── v31.py
│   ├── _shared.py
│   ├── metrics.py
│   ├── stop_loss.py
│   └── alerts.py
└── risk_v31/                # package: v3.1 风控路由包（3 个 .py 文件）
    ├── system.py
    ├── stop_loss.py
    └── alerts.py

web/backend/app/services/
├── risk_management_new.py   # 新版风控服务
├── risk_management_2.py     # 风控服务第 2 版
├── risk_management/         # package: 风控服务包（6 个 .py 文件）
│   └── ...

web/backend/app/schemas/
├── risk_schemas.py           # 风控 Schema 定义
```

### 1.2 路由注册情况

在 `router_registry.py` 中：

```python
# 2026-05-17 复核：当前可见 from .api import risk 与 app.include_router(risk.router)
```

旧版审计认为 `risk_management.py`、`risk_management_core.py`、`risk_management_v31.py` 在 `router_registry.py` 的 import 列表中被引用。2026-05-17 复核未在当前 `router_registry.py` 中确认这些 import。它们仍可能被测试、文档、运行时字符串或直接 import 使用，因此需另行扫描。

---

## 二、问题

### 2.1 API 层：canonical package + legacy shim + legacy API

| 文件 | 疑似用途 | 问题 |
|------|----------|------|
| `risk_management.py` | 兼容 shim 候选 | 目前更像转发层，不应当作主 API 直接删除 |
| `risk_management_core.py` | legacy 风控 API 候选 | 需要 endpoint inventory 和 consumer 清单 |
| `risk_management_v31.py` | v3.1 兼容候选 | 与 `risk/v31.py` + `risk_v31/` package 三处并存 |

### 2.2 Service 层：三个版本同时存在

| 文件 | 状态 |
|------|------|
| `services/risk_management_new.py` | 新版，标记 `_new` 无退出条件 |
| `services/risk_management_2.py` | 第 2 版，与 `_new` 关系不明 |
| `services/risk_management/` | package，当前最像 canonical，但仍需 consumer 与测试验证 |

三个 service 版本的差异和职责分工不明，违反了 STANDARDS.md §三.1「同一职责只允许一个主实现」。

### 2.3 版本管理混乱

`v31` 同时以 flat 文件（`risk_management_v31.py`）和 package（`risk_v31/`）存在。若 v31 是当前版本，则 `risk_management.py` 和 `risk/` 是否已废弃需要明确。

---

## 三、目标架构口径

```
web/backend/app/api/risk/        # 保留为 canonical package（已存在 6 文件）
├── __init__.py
├── alerts.py                    # 告警路由（已有）
├── stop_loss.py                 # 止损路由（已有）
├── metrics.py                   # 风控指标（已有）
├── v31.py                       # V3.1 版路由（已有）
├── _shared.py                   # 共享逻辑（已有）
└── schemas.py                   # ← risk_schemas.py 迁移进来

web/backend/app/services/risk_management/  # canonical 候选，需验证后再确认
```

### 3.1 API 收敛（OpenSpec 候选）

- 先判定 `risk_management.py` 是 shim、兼容导出还是仍承担运行时职责
- 先判定 `risk_management_core.py` 是否只是 legacy facade，还是仍有独立 consumer
- 先判定 `risk_v31/` 与 `risk_management_v31.py` 的 import 解析和 consumer 关系
- 再决定 `risk/` package 是否是唯一 canonical API

### 3.2 Service 收敛（OpenSpec 候选）

- 确认 `services/risk_management/` 是否真是 canonical
- 对比 `risk_management_new.py` 和 `risk_management_2.py` 的差异
- 将差异功能合并到 canonical service 之前，先补 consumer / test / import smoke
- 对 `_new` 和 `_2` 版本补双判定表，确认 canonical service 后再决定是否退场

---

## 四、提案前治理路线（不直接实施）

### Step 1: 确认活跃路由

先从 `router_registry.py`、OpenAPI 和测试/前端调用中确认当前真正暴露的 risk 端点，不得沿用旧版审计的假定注册列表。

### Step 2: 建消费者矩阵

把 `risk_management`、`risk_management_core`、`risk_management_v31`、`risk_v31/`、`risk_management_new.py`、`risk_management_2.py` 的引用分成代码、测试、前端、脚本和文档五类。

### Step 3: OpenSpec 设计项

风控域治理 proposal/design/tasks 至少说明：

| 设计项 | 必填内容 |
|--------|----------|
| canonical endpoint | 最终保留的 risk router、prefix 和 response model |
| endpoint parity | legacy API、v31 package 和 shim 的端点对比 |
| compatibility | shim、旧 prefix、前端路径和测试路径兼容期 |
| OpenAPI diff | 新旧路径、状态码和 schema 差异 |
| tests | import smoke、前端 API 调用、风控 CRUD、v31 smoke 和 mock 开关 |
| rollback | 任一 consumer 或 smoke 失败时恢复旧 router 或暂停退役 |

### Step 4: 审批后再更新 router_registry.py

审批通过前不得修改 router_registry、VERSION_MAPPING、前端 API base path、mock router 或 service canonical 路径。

---

## 五、删除清单

| 候选对象 | 当前处理要求 |
|----------|--------------|
| `api/risk_management.py` | 先确认是否只是 shim 或兼容导出，再决定保留/退役 |
| `api/risk_management_core.py` | 先确认是否仍有独立 consumer 或只是 legacy facade |
| `api/risk_management_v31.py` | 先确认 v31 能力是否仍需独立路径或可并入 canonical router |
| `api/risk_v31/` | 先确认 package 是否仍承担 v31 兼容职责 |
| `services/risk_management_new.py` | 先确认 canonical service 和调用方 |
| `services/risk_management_2.py` | 先确认 canonical service 和调用方 |

---

*前置文档: `docs/reports/quality/backend-audit-2026-05-14.md` §八.04*
