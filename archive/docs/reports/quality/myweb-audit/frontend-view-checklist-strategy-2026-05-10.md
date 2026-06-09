# Frontend View Checklist: `views/strategy/*`

日期：2026-05-10

范围：`web/frontend/src/views/strategy/*`

本批次目的：复核策略域目录中当前路由入口、GPU 监控页、兼容薄包装页和旧二级 workbench 静态壳的边界，避免把仍承担 canonical route 或兼容职责的页面按“未路由”误归档。

## 1. Truth Inputs

菜单 / 路由真相：

- `web/frontend/src/layouts/MenuConfig.ts` 当前策略菜单包含 `/strategy/repo`、`/strategy/parameters`、`/strategy/signals`、`/strategy/backtest`、`/strategy/gpu`、`/strategy/opt`、`/strategy/pos`。
- `web/frontend/src/router/index.ts` 当前动态导入：
- `/strategy/repo` -> `@/views/strategy/List.vue`
- `/strategy/parameters` -> `@/views/strategy/Parameters.vue`
- `/strategy/backtest` -> `@/views/strategy/Backtest.vue`
- `/strategy/gpu` -> `@/views/strategy/BacktestGPU.vue`
- `/strategy/opt` -> `@/views/strategy/Optimization.vue`
- `/strategy/signals` 与 `/strategy/pos` 使用 `artdeco-pages` 下的 canonical tab，不属于本目录冗余页。

配置 / 运行引用：

- `web/frontend/src/config/pageConfig.ts` 仍登记 `strategy-gpu` 对应 `BacktestGPU.vue`。
- `BacktestGPU.vue` 使用同目录 `composables/useBacktestGPU.ts`、`composables/gpuMonitorData.ts` 和 `styles/BacktestGPU.scss`。
- `List.vue`、`Parameters.vue`、`Backtest.vue`、`Optimization.vue` 是当前路由入口，但实际委派到 `artdeco-pages/strategy-tabs/*` canonical tab。

直接测试守护：

- `web/frontend/src/views/strategy/__tests__/StrategyList.spec.ts` 守护 `StrategyList.vue` 兼容委派到 `List.vue`。
- `web/frontend/src/views/strategy/__tests__/LegacyStrategyWorkbench.spec.ts` 守护 `BatchScan.vue`、`ResultsQuery.vue`、`SingleRun.vue`、`StatsAnalysis.vue` 降级为 honest static shell。
- `web/frontend/src/views/strategy/composables/__tests__/useBacktestGPU.spec.ts` 守护 GPU 页面 composable 不把部分同步误报为完整同步。
- `web/frontend/src/views/strategy/composables/__node_tests__/gpuMonitorData.test.ts` 守护 GPU payload 映射和未知状态口径。

## 2. Page Classification

| 页面 | 当前分类 | 路由状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `views/strategy/List.vue` | `canonical-route-wrapper` | `/strategy/repo` | 路由入口，委派到 `ArtDecoStrategyManagement.vue` | route + wrapper 引用 | 排除归档审核 |
| `views/strategy/Parameters.vue` | `canonical-route-wrapper` | `/strategy/parameters` | 路由入口，委派到 `StrategyParametersTab.vue` | route 引用 | 排除归档审核 |
| `views/strategy/Backtest.vue` | `canonical-route-wrapper` | `/strategy/backtest` | 路由入口，委派到 `ArtDecoBacktestAnalysis.vue` | route 引用 | 排除归档审核 |
| `views/strategy/Optimization.vue` | `canonical-route-wrapper` | `/strategy/opt` | 路由入口，委派到 `ArtDecoStrategyOptimization.vue` | route 引用 | 排除归档审核 |
| `views/strategy/BacktestGPU.vue` | `canonical-active` | `/strategy/gpu` | GPU 监控读取页，直接使用同目录 composable 和样式 | route + pageConfig + composable tests | 排除归档审核 |
| `views/strategy/composables/useBacktestGPU.ts` | `canonical-support-asset` | helper | GPU 页面本地 composable | direct spec | 非 view，排除归档审核 |
| `views/strategy/composables/gpuMonitorData.ts` | `canonical-support-asset` | helper | GPU payload 映射与未知状态口径 | node tests | 非 view，排除归档审核 |
| `views/strategy/styles/BacktestGPU.scss` | `canonical-support-asset` | style | GPU 页面样式资产 | `BacktestGPU.vue` 引用 | 非 view，排除归档审核 |
| `views/strategy/StrategyList.vue` | `compat-retained` | legacy wrapper | 兼容薄包装到 `List.vue` | `StrategyList.spec.ts` 守护 | 不归档，待兼容面退役决策 |
| `views/strategy/BatchScan.vue` | `candidate-review` | dead route | honest static shell，无 verified canonical execution owner | `LegacyStrategyWorkbench.spec.ts` 守护 | 不归档，需先迁移/退役守护 |
| `views/strategy/ResultsQuery.vue` | `candidate-review` | dead route | honest static shell，无 verified canonical result-query owner | `LegacyStrategyWorkbench.spec.ts` 守护 | 不归档，需先迁移/退役守护 |
| `views/strategy/SingleRun.vue` | `candidate-review` | dead route | honest static shell，无 verified canonical single-run owner | `LegacyStrategyWorkbench.spec.ts` 守护 | 不归档，需先迁移/退役守护 |
| `views/strategy/StatsAnalysis.vue` | `candidate-review` | dead route | honest static shell，无 verified canonical stats owner | `LegacyStrategyWorkbench.spec.ts` 守护 | 不归档，需先迁移/退役守护 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面。

必须保留的页面：

- `List.vue`、`Parameters.vue`、`Backtest.vue`、`Optimization.vue` 是当前 `/strategy/*` 路由入口，即使自身只是 wrapper，也不能按冗余页处理。
- `BacktestGPU.vue` 是 `/strategy/gpu` 活跃页面，并且它的 composable 已有 GPU 状态、性能快照、部分同步和未知状态测试守护。
- `StrategyList.vue` 是旧入口兼容薄包装，已有测试明确要求它委派到 canonical repo owner；删除前必须先确认兼容入口退役条件。

暂不归档的候选页面：

- `BatchScan.vue`、`ResultsQuery.vue`、`SingleRun.vue`、`StatsAnalysis.vue` 已经降级为 static shell，不再展示旧执行态、旧查询表格或旧统计指标。
- 这些页面没有当前 route import，但仍被 `LegacyStrategyWorkbench.spec.ts` 作为“不得展示伪执行态”的审计边界守护。
- 后续若要归档，必须先迁移或删除该守护用例，并给出 successor 或 `no-successor-needed` 的明确理由。

禁止误判项：

- `BacktestGPU.vue` 当前只接入 GPU 状态与性能快照读取链路，不代表它是 demo 或可丢弃页面。
- `useBacktestGPU.ts` 和 `gpuMonitorData.ts` 是 view-local canonical support assets，符合 `architecture/STANDARDS.md` 对单消费者 composable co-location 的口径。
- `StrategyList.vue` 与 `List.vue` 名称相近，但职责不同：前者是 legacy 兼容 wrapper，后者是当前 `/strategy/repo` 路由入口。

## 4. Batch Conclusion

`views/strategy/*` 当前应拆成四类治理：

- `canonical-route-wrapper`：`List.vue`、`Parameters.vue`、`Backtest.vue`、`Optimization.vue`，直接排除 archive flow。
- `canonical-active`：`BacktestGPU.vue`，保留为策略 GPU 监控页面。
- `compat-retained`：`StrategyList.vue`，保留到兼容入口退役条件明确。
- `candidate-review`：`BatchScan.vue`、`ResultsQuery.vue`、`SingleRun.vue`、`StatsAnalysis.vue`，仅登记为候选，不满足 archive-approved 条件。

本批次没有文件进入 `archive-approved`。后续治理动作应先决定 legacy strategy workbench 静态壳是否仍需要作为审计 guard 存在，再考虑归档移动。
