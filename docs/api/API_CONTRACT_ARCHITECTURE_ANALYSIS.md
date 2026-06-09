# MyStocks API 契约架构分析

> **当前口径**:
> 本文档已在 `2026-04-24` 依据当前仓库代码重新整理。此前围绕 `api-contract-sync-manager` 的外部化设想不再作为当前实现口径；当前项目的契约体系以仓库内 FastAPI 注册链路和导出的 OpenAPI 工件为准。

## 1. 当前契约真相源

根据 `architecture/STANDARDS.md`，当前 API 契约唯一事实来源是：

1. FastAPI 路由实现
2. Pydantic Schema / response model
3. 由运行时路由导出的 `/openapi.json`

Markdown 说明、手工统计表、前端自定义类型都只能作为派生材料，不能与上述三者并列为真相源。

## 2. 当前运行时契约架构

### 2.1 路由实现层

主要实现位于：

- `web/backend/app/api/*.py`
- `web/backend/app/api/*/routes.py`
- `web/backend/app/api/v1/*`

### 2.2 路由注册层

当前存在三层运行时真相，不能只看其中一层：

| 层 | 作用 | 文件 |
|----|------|------|
| 版本前缀治理 | 声明哪些 canonical router 走版本化挂载 | `web/backend/app/api/VERSION_MAPPING.py` |
| 运行时总注册入口 | 把 router 真正挂到 FastAPI app 上 | `web/backend/app/router_registry.py` |
| v1 聚合面 | 聚合一部分 active `/api/v1/*` 领域路由 | `web/backend/app/api/v1/router.py` |

结论：

- `VERSION_MAPPING.py` 不是全部 API 的唯一注册入口
- 当前运行时路径必须同时核对 `VERSION_MAPPING.py`、`router_registry.py`、`api/v1/router.py`

### 2.3 契约治理与校验层

仓库内已存在 API 契约治理能力，不依赖外部 manager：

| 能力 | 入口 |
|------|------|
| 契约版本管理 | `/api/contracts/versions` |
| 契约差异对比 | `/api/contracts/diff` |
| 契约校验 | `/api/contracts/validate` |
| 契约同步 | `/api/contracts/sync` |
| OpenAPI 导出脚本 | `scripts/generate_openapi.py` |
| 前端类型生成 | `scripts/generate_frontend_types.py` |

### 2.4 文档与前端派生层

派生产物包括：

- `docs/api/openapi.json`
- `web/frontend/src/api/types/*`
- API 统计和映射类 Markdown 文档

这些文件必须从当前运行时契约重新生成或重新核对，不能手工长期漂移。

## 3. 2026-04-24 当次复核结果

通过 `python scripts/generate_openapi.py --output /tmp/mystocks_openapi_current.json` 重新导出后，当前后端契约规模为：

| 指标 | 当前值 | 口径 |
|------|--------|------|
| Paths | `455` | OpenAPI `paths` 数量 |
| Operations | `493` | `GET/POST/PUT/DELETE/PATCH` 总数 |
| GET | `313` | 当前导出结果 |
| POST | `143` | 当前导出结果 |
| PUT | `13` | 当前导出结果 |
| DELETE | `22` | 当前导出结果 |
| PATCH | `2` | 当前导出结果 |

这意味着旧文档中把“469 个端点”写成当前事实的说法已经失效，必须按重新导出的结果更新。

## 4. API 变更的正确流程

### 4.1 新增或调整版本化 API

1. 在 `web/backend/app/api/...` 中实现或修改 router
2. 若属于 registry-managed versioned route，更新 `web/backend/app/api/VERSION_MAPPING.py`
3. 确认 `web/backend/app/router_registry.py` 已注册
4. 如属 `api/v1` 聚合面，再核对 `web/backend/app/api/v1/router.py`
5. 重新生成 OpenAPI
6. 同步 `docs/api/openapi.json`
7. 运行 `scripts/generate_frontend_types.py`

### 4.2 文档更新要求

- 统计类文档必须带生成日期和统计口径
- “可用/阻塞”必须基于当前 OpenAPI 或真实运行验证
- 历史分析可以保留，但必须明确标为历史快照

## 5. 当前 API 管理结论

- 当前仓库已经具备内建的契约管理、版本管理与同步入口
- 真实治理重点不在“再引入一套外部 contract manager”，而在“避免 Markdown、前端 wrapper、OpenAPI 快照三者漂移”
- 本轮 API 管理核对中，真正需要优先收口的是：
  - 文档统计口径过期
  - 前端兼容封装仍引用已不存在的技术分析路径
  - `docs/api/openapi.json` 需要与当前代码重新同步

## 6. 页面级 route truth 收口原则

本轮前端 API 管理进一步暴露出一个高频漂移源：`route meta.api`、页面首屏真实请求、E2E 页面契约三者不一致。

当前收口原则如下：

1. `route meta.api` 必须优先表达“入页即请求”的首屏主 API，而不是整页所有接口的抽象合集。
2. 若页面首屏会并行触发多个接口，应只选一个当前最稳定、最能代表页面主职责的读接口作为 `meta.api`。
3. 若某接口只在用户动作后触发，例如 `Strategy-Backtest` 的 `run/status/result` 链，则不应把它写成该页面的首屏 `meta.api`。
4. `pageConfig.ts`、路由定义、E2E 页面契约必须同批同步，避免出现“路由已改、测试和文档还停在旧口径”的并行真相源。

本轮已收正的代表性页面包括：

- `Data-Industry`: `/api/akshare_market/boards` -> `/api/v2/market/sector/fund-flow?sector_type=行业`
- `Data-FundFlow`: `/api/akshare/market/fund-flow` -> `/api/akshare/market/fund-flow/hsgt-summary`
- `Strategy-Backtest`: `/api/v1/strategy/backtest` -> `/api/v1/strategy/strategies`

交易域边界补充：

- 当前条线只维护交易相关读接口的契约真相，例如 `/api/v1/trade/positions`、`/api/v1/trade/signals`
- 交易功能实现和写操作链路不在本轮范围内，避免把“接口存在”误写成“交易功能已完成”
