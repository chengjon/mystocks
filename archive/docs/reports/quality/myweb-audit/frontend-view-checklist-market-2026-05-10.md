# Frontend View Checklist: `views/market/*`

日期：2026-05-10

范围：`web/frontend/src/views/market/*`

本批次目的：复核市场域目录中活跃 canonical 页面、兼容薄包装页面、legacy 静态壳页面的边界，防止把仍由路由、包装层、数据 helper 或测试守护的页面误判为可归档冗余页。

## 1. Truth Inputs

菜单 / 路由真相：

- `web/frontend/src/router/index.ts` 当前仍以动态导入注册 `/market/realtime`、`/market/lhb`、`/market/technical`。
- `web/frontend/src/layouts/MenuConfig.ts` 与菜单审计口径仍将 `market` 作为正式业务域之一。

运行引用与包装层：

- `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue` 复用 `@/views/market/Realtime.vue`。
- `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue` 复用 `@/views/market/Technical.vue`。
- `web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` 复用 `@/views/market/LHB.vue`。
- `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue` 复用 `@/views/market/marketKlineData`。

历史治理证据：

- `secondary-batch-37`：`market/CapitalFlow.vue`、`market/Concepts.vue` 已降为 canonical 数据域页面的兼容薄包装。
- `secondary-batch-38`：`market/Auction.vue`、`market/Etf.vue` 已降为 honest static shell。
- `secondary-batch-39`：`MarketData.vue`、`market/MarketDataView.vue` 已降为 honest static shell。
- `secondary-batch-41`：`market/Tdx.vue` 已降为 honest static shell。

直接测试守护：

- `web/frontend/src/views/market/__tests__/Realtime.spec.ts`
- `web/frontend/src/views/market/__tests__/LHB.spec.ts`
- `web/frontend/src/views/market/__tests__/Technical.spec.ts`
- `web/frontend/src/views/market/__tests__/CapitalFlow.spec.ts`
- `web/frontend/src/views/market/__tests__/Concepts.spec.ts`
- `web/frontend/src/views/market/__tests__/Auction.spec.ts`
- `web/frontend/src/views/market/__tests__/Etf.spec.ts`
- `web/frontend/src/views/market/__tests__/MarketDataView.spec.ts`
- `web/frontend/src/views/market/__tests__/Tdx.spec.ts`

## 2. Page Classification

| 页面 | 当前分类 | 路由状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `views/market/Realtime.vue` | `canonical-active` | `/market/realtime` | 实时行情 canonical 页面 | 直接 spec + ArtDeco tab 引用 | 排除归档审核 |
| `views/market/LHB.vue` | `canonical-active` | `/market/lhb` | 龙虎榜 canonical 页面 | 直接 spec + DragonTiger wrapper 引用 | 排除归档审核 |
| `views/market/Technical.vue` | `canonical-active` | `/market/technical` | K 线 / 技术分析 canonical 页面 | 直接 spec + MarketKLine wrapper 引用 | 排除归档审核 |
| `views/market/marketRealtimeData.ts` | `canonical-support-asset` | helper | 实时行情数据转换 / 口径资产 | 由 active 页面使用 | 非 view，排除归档审核 |
| `views/market/dragonTigerData.ts` | `canonical-support-asset` | helper | 龙虎榜数据转换 / 口径资产 | node tests + active 页面使用 | 非 view，排除归档审核 |
| `views/market/marketKlineData.ts` | `canonical-support-asset` | helper | K 线数据转换 / 口径资产 | node tests + detail wrapper 使用 | 非 view，排除归档审核 |
| `views/market/CapitalFlow.vue` | `compat-retained` | legacy wrapper | 薄包装到 `views/data/FundFlow.vue` | `CapitalFlow.spec.ts` 明确守护委派关系 | 不归档，待兼容面退役决策 |
| `views/market/Concepts.vue` | `compat-retained` | legacy wrapper | 薄包装到 `views/data/Concepts.vue` | `Concepts.spec.ts` 明确守护委派关系 | 不归档，待兼容面退役决策 |
| `views/market/Auction.vue` | `candidate-review` | dead route | honest static shell，无一对一 canonical owner | `Auction.spec.ts` 守护静态壳事实 | 不归档，需先迁移/退役守护 |
| `views/market/Etf.vue` | `candidate-review` | dead route | honest static shell，无一对一 canonical owner | `Etf.spec.ts` 守护静态壳事实 | 不归档，需先迁移/退役守护 |
| `views/market/MarketDataView.vue` | `candidate-review` | dead route | nested market-data 聚合静态壳 | `MarketDataView.spec.ts` 守护静态壳事实 | 不归档，需先迁移/退役守护 |
| `views/market/Tdx.vue` | `candidate-review` | dead route | honest static shell，无 verified canonical owner | `Tdx.spec.ts` 守护静态壳事实 | 不归档，需先迁移/退役守护 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面。

必须保留的页面：

- `Realtime.vue`、`LHB.vue`、`Technical.vue` 是当前市场域 canonical 业务页，且仍由路由和 ArtDeco 包装层使用。
- `CapitalFlow.vue`、`Concepts.vue` 是明确的兼容薄包装，删除前必须先确认旧入口不再被文档、测试、用户书签或兼容路径使用。

暂不归档的候选页面：

- `Auction.vue`、`Etf.vue`、`MarketDataView.vue`、`Tdx.vue` 虽然不是当前主路由入口，但它们已经被历史批次治理为 honest static shell，并有直接测试守护。
- 这些页面没有隐藏 live snapshot 或 selector-owned 执行态，但仍承担“缺少一对一 canonical truth 时不展示伪实况”的审计边界。
- 若后续要归档，必须先完成测试迁移或删除审批，并给出 successor 或 `no-successor-needed` 的明确理由。

禁止误判项：

- `market/marketKlineData.ts`、`market/dragonTigerData.ts`、`market/marketRealtimeData.ts` 是支持 active market 页面的共享资产，不进入 view 冗余页清理。
- `/detail/*` 对 K 线能力的引用需要按 source-aware guard map 判断，不得把 `marketKlineData` 当作孤立 helper。

## 4. Batch Conclusion

`views/market/*` 当前应拆成三类治理：

- `canonical-active`：`Realtime.vue`、`LHB.vue`、`Technical.vue`，直接排除 archive flow。
- `compat-retained`：`CapitalFlow.vue`、`Concepts.vue`，保留到兼容入口退役条件明确。
- `candidate-review`：`Auction.vue`、`Etf.vue`、`MarketDataView.vue`、`Tdx.vue`，仅可继续登记为候选，不满足 archive-approved 条件。

本批次没有文件进入 `archive-approved`。后续治理动作应优先处理候选静态壳的测试与文档守护迁移，而不是按“未路由”机械移动。
