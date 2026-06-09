# Notes: code-simplifier 全仓精简分析摘录

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


## Source
- 分析来源：`code-simplifier:code-simplifier` 子代理（只读扫描）
- 分析范围：backend / frontend / scripts / docs / config / tests
- 说明：以下为规划输入，不代表已实施修改。

## 关键发现（按模块）

### 1) Frontend API 层存在并行入口（高优先级）
- `web/frontend/src/api/unifiedApiClient.ts`
  - 存在 `unifiedApiClient = apiClient` 形式的桥接导出与别名导出。
- `web/frontend/src/api/index.ts`
  - 同时暴露 `request = apiClient` 与多组兼容分组 API。
- `web/frontend/src/services/httpClient.js`
  - 存在 deprecated 警告与兼容 stub。
- `web/frontend/src/services/api-client` 调用链路已存在（当前检索到 `web/frontend/src/services/WencaiQueryEngine.ts` 仍在引用），说明 canonical 入口需“先决策后迁移”。

结论：P0 不应直接假设唯一入口为 `src/api/apiClient`；应先在 `src/api/apiClient` 与 `src/services/api-client` 间完成 canonical 决策，再推进统一迁移与 sunset。

### 2) Backend legacy 文件并存（高优先级）
- `.old.py`：`web/backend/app/api/data_source_config.old.py`
- `.new`：`web/backend/app/api/technical_analysis.py.new`
- `.bak`：`web/backend/app/api/mystocks_complete.py.bak`、`web/backend/app/api/risk_management.py.bak`
- `.backup*`：`web/backend/app/api/strategy_management.py.backup`、`web/backend/app/api/data_source_config.py.backup`、`web/backend/app/api/data.py.backup.20260130`、`web/backend/app/services/data_adapter.py.backup.20260130`、`web/backend/app/api/risk_management.py.backup.20260130`

结论：清理范围需扩展为 `.old/.new/.bak/.backup*` 全量治理；必须先做运行链路引用扫描，再执行迁移/删除。

### 3) Scripts 历史兼容入口较多（中优先级）
- 多脚本存在“兼容入口”或历史用途残留，建议按 runtime/dev/archive 分层。

### 4) Docs 历史迁移报告较重（中优先级）
- `docs/code_quality/*` 中历史阶段性报告较多，主线文档可降噪并统一索引。

### 5) Tests 存在兼容性断言负担（中优先级）
- 部分测试主要验证 legacy 兼容属性，建议与核心回归测试分层管理。

## 风险记录
1. 兼容入口删除风险：外部脚本/CI/运维命令可能仍依赖旧路径。
2. 前端行为等价风险：鉴权、CSRF、错误包装在不同客户端封装下可能不一致。
3. 后端路由隐式依赖风险：自动发现/注册链可能引用旧文件。
4. 门禁口径不一致风险：若验收未对齐 baseline/PM2/E2E，可能出现“文档通过但实际不可发布”。
5. stylelint 执行口径风险：当前 `package.json` 含 stylelint 依赖但无显式脚本，直接设为硬门禁会造成执行口径不完整。

## 规划约束
- 本阶段仅规划，不做代码删除。
- 执行阶段必须先做“引用扫描 + 迁移观测 + 回归验证”。

## Phase A 基线快照（主工作树，排除 `.claude` 下 historical nested tooling / docs / dist / node_modules / logs / coverage）

### A. Frontend API 入口使用分布（`web/frontend/src`）
> 口径：以下计数为 `files_with_matches` 的**文件数**（用于迁移优先级），不是精确行级 occurrence。

| Pattern | 匹配文件数 | 代表性调用方（示例） |
|---|---:|---|
| `services/api-client` | 1 | `web/frontend/src/services/WencaiQueryEngine.ts` |
| `api/apiClient` | 2 | `web/frontend/src/main.js`、`web/frontend/src/main-original.js` |
| `unifiedApiClient` | 21 | `web/frontend/src/services/menuDataFetcher.ts`、`web/frontend/src/composables/artdeco/useArtDecoApi.ts`、`web/frontend/src/services/dashboardService.ts`、`web/frontend/src/stores/trading.ts`、`web/frontend/src/components/market/FundFlowPanel.vue` |
| `services/httpClient` | 7 | `web/frontend/src/api/unifiedApiClient.ts`、`web/frontend/src/stores/auth.ts`、`web/frontend/src/stores/storeFactory.ts`、`web/frontend/src/composables/useMarketData.js` |
| `from '@/api'` / `from '@/api/*'` / `from '../api/*'` | 93 | `web/frontend/src/api/strategy.ts`、`web/frontend/src/api/trade.ts`、`web/frontend/src/api/user.ts`、`web/frontend/src/composables/useStrategy.ts`、`web/frontend/src/services/TradingApiManager.ts` |

结论：当前前端存在“barrel import（`@/api`）+ 多客户端符号并存（`apiClient/unifiedApiClient/httpClient/services/api-client`）”的并行入口形态，需先做 canonical 决策再迁移。

### B. Backend legacy 文件清单（`web/backend/app`）

| Legacy 文件 | 发现方式 | 运行链路引用扫描结果（backend/scripts/.github） | 初步动作 |
|---|---|---|---|
| `web/backend/app/api/data_source_config.old.py` | `*.old*` | 0 | 删除候选（先做一次路由/动态导入复核） |
| `web/backend/app/api/technical_analysis.py.new` | `*.new` | 0 | 删除候选 |
| `web/backend/app/api/mystocks_complete.py.bak` | `*.bak` | 0 | 删除候选 |
| `web/backend/app/api/risk_management.py.bak` | `*.bak` | 0 | 删除候选 |
| `web/backend/app/api/strategy_management.py.backup` | `*.backup*` | 0 | 删除候选 |
| `web/backend/app/api/data_source_config.py.backup` | `*.backup*` | 0 | 删除候选 |
| `web/backend/app/api/data.py.backup.20260130` | `*.backup*` | 0 | 删除候选 |
| `web/backend/app/services/data_adapter.py.backup.20260130` | `*.backup*` | 0 | 删除候选 |
| `web/backend/app/api/risk_management.py.backup.20260130` | `*.backup*` | 0 | 删除候选 |

补充：`web/backend/app/api/__pycache__/data_source_config.old.cpython-312.pyc` 属构建产物，不作为源码迁移对象。

### C. Phase A 迁移优先顺序（按风险）
1. 高风险：`web/frontend/src/services/httpClient.js`（兼容层 + 认证/错误包装链路）
2. 中高风险：`web/frontend/src/api/unifiedApiClient.ts`（桥接导出，调用面广）
3. 中风险：`web/frontend/src/services/WencaiQueryEngine.ts`（`services/api-client` 单点入口）
4. 中风险：`web/frontend/src/services/TradingApiManager.ts`、`web/frontend/src/composables/useStrategy.ts`（`@/api` barrel 依赖）
5. 低风险：backend `.old/.new/.bak/.backup*`（当前扫描无运行链路引用，满足“零引用可删”前置）
