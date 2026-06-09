# compatibility-inventory（Phase A 基线）

> **设计方案说明**:
> 本文件是架构设计、系统模型、功能结构、映射关系或规格方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、功能清单和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> 范围：主工作树源码路径；排除 `.claude` 下 historical nested tooling / docs / dist / node_modules / logs / coverage 噪声目录。
> 口径：Frontend 统计以 `files_with_matches` 的文件数计，不等同于行级 occurrences。

## 1) Frontend API 入口兼容层清单（`web/frontend/src`）

| Pattern | 匹配文件数 | 代表性调用方（示例） |
|---|---:|---|
| `services/api-client` | 1 | `web/frontend/src/services/WencaiQueryEngine.ts` |
| `api/apiClient` | 2 | `web/frontend/src/main.js`、`web/frontend/src/main-original.js` |
| `unifiedApiClient` | 21 | `web/frontend/src/services/menuDataFetcher.ts`、`web/frontend/src/composables/artdeco/useArtDecoApi.ts`、`web/frontend/src/services/dashboardService.ts`、`web/frontend/src/stores/trading.ts`、`web/frontend/src/components/market/FundFlowPanel.vue` |
| `services/httpClient` | 7 | `web/frontend/src/api/unifiedApiClient.ts`、`web/frontend/src/stores/auth.ts`、`web/frontend/src/stores/storeFactory.ts`、`web/frontend/src/composables/useMarketData.js` |
| `from '@/api'` / `from '@/api/*'` / `from '../api/*'` | 93 | `web/frontend/src/api/strategy.ts`、`web/frontend/src/api/trade.ts`、`web/frontend/src/api/user.ts`、`web/frontend/src/composables/useStrategy.ts`、`web/frontend/src/services/TradingApiManager.ts` |

### 关键证据片段（抽样）
- `web/frontend/src/services/WencaiQueryEngine.ts`: `import { apiClient } from '@/services/api-client'`
- `web/frontend/src/main.js`: `import { initializeSecurity } from './services/httpClient.js'`
- `web/frontend/src/main.js`: `import { ContractValidationError } from './api/unifiedApiClient.ts'`
- `web/frontend/src/services/httpClient.js`: `import { apiClient } from '@/api/apiClient'`
- `web/frontend/src/api/unifiedApiClient.ts`: `export const unifiedApiClient = apiClient`

### 观察结论
1. 入口并行结构明显：`@/api` barrel、`apiClient`、`unifiedApiClient`、`httpClient`、`services/api-client` 同时存在。
2. `httpClient.js` 已为兼容桥接层（含 deprecated/stub 语义），不应直接删除，需按 sunset 窗口下线。
3. canonical client 必须先决策再迁移（`src/api/apiClient` vs `src/services/api-client`）。

---

## 2) Backend legacy 文件清单（`web/backend/app`）

| Legacy 文件 | 后缀类型 | 运行链路引用扫描结果（backend/scripts/.github） | 初步动作 |
|---|---|---:|---|
| `web/backend/app/api/data_source_config.old.py` | `.old.py` | 0 | 删除候选（先做路由/动态导入复核） |
| `web/backend/app/api/technical_analysis.py.new` | `.new` | 0 | 删除候选 |
| `web/backend/app/api/mystocks_complete.py.bak` | `.bak` | 0 | 删除候选 |
| `web/backend/app/api/risk_management.py.bak` | `.bak` | 0 | 删除候选 |
| `web/backend/app/api/strategy_management.py.backup` | `.backup` | 0 | 删除候选 |
| `web/backend/app/api/data_source_config.py.backup` | `.backup` | 0 | 删除候选 |
| `web/backend/app/api/data.py.backup.20260130` | `.backup*` | 0 | 删除候选 |
| `web/backend/app/services/data_adapter.py.backup.20260130` | `.backup*` | 0 | 删除候选 |
| `web/backend/app/api/risk_management.py.backup.20260130` | `.backup*` | 0 | 删除候选 |

补充：`web/backend/app/api/__pycache__/data_source_config.old.cpython-312.pyc` 为构建产物，不纳入源码迁移对象。

---

## 3) Phase B 前置门槛（进入迁移前）

1. 冻结新增 API client 入口（避免迁移期继续发散）。
2. 完成 canonical client 决策（架构签字）。
3. 对 `httpClient` 与 `unifiedApiClient` 增加 sunset 注记和迁移窗口。
4. 执行一次关键链路基线回归（认证、请求错误包装、核心页面加载）。
