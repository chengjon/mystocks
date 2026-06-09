# Frontend View Checklist: `views/data/*`

日期：2026-05-10

范围：`web/frontend/src/views/data/*`

本批次目的：复核数据分析域目录是否存在未路由冗余页，并确认同目录数据 helper 属于 active support assets，避免把已经迁入正式业务域的页面按历史 ArtDeco 嵌入层误判为可归档对象。

## 1. Truth Inputs

菜单 / 路由真相：

- `web/frontend/src/layouts/MenuConfig.ts` 当前数据分析菜单包含 `/data/industry`、`/data/indicator`、`/data/concept`、`/data/fund-flow`。
- `web/frontend/src/router/index.ts` 当前动态导入：
- `/data/industry` -> `@/views/data/Industry.vue`。
- `/data/concept` -> `@/views/data/Concepts.vue`。
- `/data/fund-flow` -> `@/views/data/FundFlow.vue`。
- `/data/indicator` -> `@/views/data/Advanced.vue`。

配置 / 历史迁移证据：

- `web/frontend/src/config/pageConfig.ts` 仍登记 `data-industry`、`data-concept`、`data-fund-flow`、`data-indicator`。
- `openspec/changes/restructure-frontend-directory/tasks.md` 明确 `data` 4 页已切到 `views/data/*`，并将 `Industry.vue`、`Concepts.vue`、`FundFlow.vue`、`Advanced.vue` 作为 repo-truth route owner。
- `docs/FUNCTION_TREE.md` 将 `views/data/FundFlow.vue`、`views/data/Advanced.vue` 等列为市场数据、指标分析能力入口。

直接测试守护：

- `web/frontend/src/views/data/__tests__/Industry.spec.ts`
- `web/frontend/src/views/data/__tests__/Concepts.spec.ts`
- `web/frontend/src/views/data/__tests__/FundFlow.spec.ts`
- `web/frontend/src/views/data/__tests__/Advanced.spec.ts`
- 历史 guard map 还记录 `web/frontend/tests/unit/views/data-advanced-cutover.spec.ts`、`data-advanced-screening-truth.spec.ts`、`data-indicator-details.spec.ts`、`data-concept-refresh-fallback.spec.ts`、`data-fund-flow-partial-state.spec.ts`、`data-industry-refresh-fallback.spec.ts` 等外部守护引用。

## 2. Page Classification

| 页面 | 当前分类 | 路由状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `views/data/Industry.vue` | `canonical-active` | `/data/industry` | 板块动向 active route | direct spec + historical manifests | 排除归档审核 |
| `views/data/Concepts.vue` | `canonical-active` | `/data/concept` | 概念动向 active route | direct spec + market legacy wrapper 引用 | 排除归档审核 |
| `views/data/FundFlow.vue` | `canonical-active` | `/data/fund-flow` | 资金流向 active route | direct spec + market legacy wrapper 引用 | 排除归档审核 |
| `views/data/Advanced.vue` | `canonical-active` | `/data/indicator` | 指标分析 active route | direct spec + top-level `IndicatorLibrary.vue` wrapper 引用 | 排除归档审核 |
| `views/data/industryAnalysisData.ts` | `canonical-support-asset` | helper | `Industry.vue` 数据归一化与板块口径资产 | `Industry.vue:111` page import + historical tests | 非 view，排除归档审核 |
| `views/data/marketConceptData.ts` | `canonical-support-asset` | helper | `Concepts.vue` 请求与概念行归一化资产 | `Concepts.vue:6` page import + historical tests | 非 view，排除归档审核 |
| `views/data/fundFlowPageData.ts` | `canonical-support-asset` | helper | `FundFlow.vue` 资金流展示与排行口径资产 | `FundFlow.vue:159` page import + historical tests | 非 view，排除归档审核 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面，也未发现 `views/data/*` 目录内的 `candidate-review` Vue 页面。

必须保留的页面：

- `Industry.vue`、`Concepts.vue`、`FundFlow.vue`、`Advanced.vue` 全部是当前 router truth，不能进入 archive flow。
- `Advanced.vue` 的文件名与菜单名 `/data/indicator` 不完全一致，但当前路由和 pageConfig 明确它是指标分析主入口。
- `Concepts.vue`、`FundFlow.vue` 同时被 `views/market/Concepts.vue`、`views/market/CapitalFlow.vue` 兼容 wrapper 引用，是跨域兼容链路的 canonical target。
- `Advanced.vue` 同时被顶层 `views/IndicatorLibrary.vue` 兼容 wrapper 引用，是指标库旧入口的 canonical target。

必须保留的支持资产：

- `industryAnalysisData.ts`、`marketConceptData.ts`、`fundFlowPageData.ts` 是各 active route 的 view-local support asset，不是孤立未用文件。
- 这些 helper 属于页面本地数据口径与转换层，符合当前 view-local co-location 口径，不应被提前下沉或机械合并。

禁止误判项：

- 旧文档中出现的 `artdeco-pages/market-data-tabs/*` 是历史迁移来源，不应覆盖当前 `views/data/*` repo truth。
- `data-indicator` 路由名不等于 `Advanced.vue` 文件名，但不能因此把 `Advanced.vue` 归为 legacy 或未路由。
- `views/data/*` 本批次没有 archive candidate，因此无需进入 successor / no-successor-needed 审核。

## 4. Batch Conclusion

`views/data/*` 当前应拆成两类治理：

- `canonical-active`：`Industry.vue`、`Concepts.vue`、`FundFlow.vue`、`Advanced.vue`，全部直接排除 archive flow。
- `canonical-support-asset`：`industryAnalysisData.ts`、`marketConceptData.ts`、`fundFlowPageData.ts`，保留为 active route 本地数据资产。

本批次没有文件进入 `archive-approved`，也没有 `candidate-review` 页面需要继续拆解。后续治理应保持 `views/data/*` 作为正式业务域基线，不再把历史 ArtDeco 迁移来源当作当前目录事实。
