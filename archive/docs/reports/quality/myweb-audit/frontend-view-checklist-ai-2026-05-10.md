# Frontend View Checklist: `views/ai/*`

日期：2026-05-10

范围：`web/frontend/src/views/ai/*`

本批次目的：复核 AI 域当前 active routed 页面、view-local 支持资产、跨风险域复用关系，并修正此前只覆盖 `BatchAnalysis.vue` 的局部结论。AI 域当前属于 `router/index.ts` active route truth，但尚未进入 `layouts/MenuConfig.ts` 主侧栏菜单，因此不能按“未在菜单中”直接归档。

## 1. Truth Inputs

菜单 / 路由真相：

- `web/frontend/src/router/index.ts` 当前注册 `/ai` 路由组，并重定向到 `/ai/sentiment`。
- `/ai/sentiment` -> `@/views/ai/Sentiment.vue`。
- `/ai/ml` -> `@/views/ai/MlWorkbench.vue`。
- `/ai/batch` -> `@/views/ai/BatchAnalysis.vue`。
- `web/frontend/src/layouts/MenuConfig.ts` 当前 7 个侧栏主域不包含 AI 域；AI 页面状态应标记为 `active-routed/menu-pending`，不是 `dead route`。

配置 / 规格 / 功能树证据：

- `docs/FUNCTION_TREE.md` 将 `Sentiment.vue`、`MlWorkbench.vue`、`BatchAnalysis.vue` 列为 AI 与高级分析前端交互入口。
- `openspec/specs/ai-sentiment-workbench/spec.md` 要求 AI sentiment workbench 作为 canonical AI-domain sentiment workbench，并要求 `/risk/news` 复用该 orchestration。
- `openspec/specs/ai-batch-analysis/spec.md` 要求 `/api/v1/strategies/batch-analysis/*` 与 AI batch analysis workbench 提供批量分析 evidence surface，并明确输出不是自动交易、券商执行或生产调度完成。
- `web/frontend/src/config/pageConfig.ts` 当前仅登记 `ai-sentiment`，未完整登记 `ai-ml`、`ai-batch`；该文件是自动生成配置，不应覆盖 router truth。

历史 / guard 口径漂移：

- `docs/reports/quality/myweb-audit/frontend-view-inventory-correction-ai-batch-analysis-2026-05-10.md` 已把 `BatchAnalysis.vue` 从 stale `候选待审` 修正为 `canonical-active`。
- 该修正文档曾引用 `web/frontend/src/config/menu.config.js` 作为导航证据；本批次按当前治理规则收口为 `MenuConfig.ts` + `router/index.ts`。
- `web/frontend/tests/unit/config/ai-route-canonical-paths.spec.ts` 仍检查旧 `config/menu.config.js` 中的 AI path；这是 guard 口径漂移，不能作为 archive 依据，后续应单独收口到当前菜单真相。

直接测试 / E2E 守护：

- `web/frontend/src/views/ai/__tests__/Sentiment.spec.ts`
- `web/frontend/src/views/ai/__tests__/MlWorkbench.spec.ts`
- `web/frontend/src/views/ai/__tests__/BatchAnalysis.spec.ts`
- `web/frontend/tests/e2e/ai-sentiment-workbench.spec.ts`
- `web/frontend/tests/e2e/ai-ml-workbench.spec.ts`
- `web/frontend/tests/e2e/ai-batch-analysis.spec.ts`
- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts` 覆盖 `/ai/sentiment`。

## 2. Page Classification

| 页面 | 当前分类 | 路由状态 | 菜单状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- | --- |
| `views/ai/Sentiment.vue` | `canonical-active/menu-pending` | `/ai/sentiment` | 不在当前 `MenuConfig.ts` | AI 情感分析 canonical route owner | direct spec + E2E + OpenSpec | 排除归档审核 |
| `views/ai/MlWorkbench.vue` | `canonical-active/menu-pending` | `/ai/ml` | 不在当前 `MenuConfig.ts` | 模型训练 / 预测 canonical route owner | direct spec + E2E | 排除归档审核 |
| `views/ai/BatchAnalysis.vue` | `canonical-active/menu-pending` | `/ai/batch` | 不在当前 `MenuConfig.ts` | 批量分析 canonical route owner | direct spec + E2E + OpenSpec | 排除归档审核 |
| `views/ai/composables/useAiSentimentWorkbench.ts` | `shared-support-asset` | helper | n/a | AI sentiment + `/risk/news` 共享 orchestration | risk wrapper spec + direct specs | 保留，后续评估下沉共享层 |
| `views/ai/composables/useMlWorkbench.ts` | `canonical-support-asset` | helper | n/a | `MlWorkbench.vue` view-local composable | direct spec | 非 view，排除归档审核 |
| `views/ai/composables/useBatchAnalysisWorkbench.ts` | `canonical-support-asset` | helper | n/a | `BatchAnalysis.vue` view-local composable | direct spec + E2E | 非 view，排除归档审核 |
| `views/ai/components/AiSentimentHero.vue` | `canonical-support-asset` | component | n/a | `Sentiment.vue` 页面私有组件 | direct spec | 非 route view，随 owner 保留 |
| `views/ai/components/AiSentimentSummaryCards.vue` | `canonical-support-asset` | component | n/a | `Sentiment.vue` 页面私有指标卡组件 | direct spec | 非 route view，随 owner 保留 |
| `views/ai/components/AiSentimentWorkbenchPanels.vue` | `canonical-support-asset` | component | n/a | `Sentiment.vue` 页面私有工作区组件 | direct spec | 非 route view，随 owner 保留 |
| `views/ai/styles/SentimentWorkbench.scss` | `canonical-support-asset` | style | n/a | `Sentiment.vue` 页面样式资产 | style import | 非 view，排除归档审核 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面。

必须保留的页面：

- `Sentiment.vue`、`MlWorkbench.vue`、`BatchAnalysis.vue` 全部是当前 `router/index.ts` 的 active route owner，不能进入 archive flow。
- AI 域虽然不在当前 `MenuConfig.ts` 侧栏主菜单内，但这只说明产品导航状态待决，不等于页面死链或冗余。
- `BatchAnalysis.vue` 已由专门修正文档从 stale inventory 中移出；本批次继续确认其不应进入 redundant-page archive review。

需要后续收口的支持资产：

- `useAiSentimentWorkbench.ts` 当前同时服务 `Sentiment.vue` 与 `risk/News.vue`，按 `architecture/STANDARDS.md` 的 composable 规则，长期更适合评估下沉到共享 composable 层；但这属于后续 mutation / extraction 批次，不是本批次归档动作。
- `useMlWorkbench.ts`、`useBatchAnalysisWorkbench.ts` 目前分别只有一个 AI route owner 消费，保留在 `views/ai/composables/` 符合 view-local co-location 口径。
- `AiSentiment*` 三个组件只服务情感分析工作台，属于页面私有拆分资产，不应因非 route view 而进入冗余页面归档池。

禁止误判项：

- 不能用 `MenuConfig.ts` 未列出 AI 域直接判断 `views/ai/*` 可归档；router truth 和 OpenSpec / E2E 守护证明它们仍是 active routed 页面。
- 不能用旧 `config/menu.config.js` 继续证明当前主菜单结构；该文件只说明历史/兼容配置仍存在，后续 guard 应迁移到当前 `layouts/MenuConfig.ts` 口径。
- `advanced-analysis/*` 中的旧 batch / sentiment 静态壳已在单独批次登记，不应反向削弱 `views/ai/*` 的 canonical-active 地位。

## 4. Batch Conclusion

`views/ai/*` 当前应拆成三类治理：

- `canonical-active/menu-pending`：`Sentiment.vue`、`MlWorkbench.vue`、`BatchAnalysis.vue`，全部直接排除 archive flow。
- `canonical-support-asset`：`useMlWorkbench.ts`、`useBatchAnalysisWorkbench.ts`、`AiSentiment*` 组件、`SentimentWorkbench.scss`，随对应 active route owner 保留。
- `shared-support-asset`：`useAiSentimentWorkbench.ts`，已跨 AI 与 Risk 域复用，后续可作为共享 composable 下沉候选，但不能作为冗余文件清理。

本批次没有 `archive-approved` 页面。AI 域下一步治理不应是归档页面，而应先做产品/导航决策：将 AI 正式纳入 `MenuConfig.ts` 主菜单，或明确标为非主菜单实验/深链域，并同步修正仍依赖旧 `config/menu.config.js` 的 guard。
