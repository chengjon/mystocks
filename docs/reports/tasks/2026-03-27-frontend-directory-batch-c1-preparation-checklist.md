# 2026-03-27 Frontend Directory Batch C1：试点页迁移准备清单

> 范围：只覆盖 Batch C 选定的 3 个试点页，不直接迁移。
>
> 试点页：
> 1. [MarketRealtimeTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue)
> 2. [MarketKLineTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue)
> 3. [DragonTigerAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue)

## 1. 试点目标

本批次的目标不是立即移动文件，而是为后续真正迁移准备一套最小、精确、可验证的执行清单。

必须保证：

- 路由 URL 不变
- 只迁移页面及其最小本地依赖
- 不抽离 `src/shared`
- 不把其它 market/data 页混进来

## 2. 当前文件与目标路径

| 路由名 | 当前文件 | 目标文件 |
|---|---|---|
| `market-realtime` | `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue` | `web/frontend/src/views/market/Realtime.vue` |
| `market-technical` | `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue` | `web/frontend/src/views/market/Technical.vue` |
| `market-lhb` | `web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` | `web/frontend/src/views/market/LHB.vue` |

## 3. 最小本地依赖清单

### 3.1 `market-realtime`

- 页面文件：
  - `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue`
- 本地相对依赖：
  - `web/frontend/src/views/artdeco-pages/market-tabs/marketRealtimeData.ts`

### 3.2 `market-technical`

- 页面文件：
  - `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue`
- 本地相对依赖：
  - `web/frontend/src/views/artdeco-pages/market-tabs/marketKlineData.ts`

### 3.3 `market-lhb`

- 页面文件：
  - `web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue`
- 本地相对依赖：
  - `web/frontend/src/views/artdeco-pages/market-data-tabs/dragonTigerData.ts`

## 4. 受影响的路由与配置文件

后续真正迁移时，至少要同步改这些文件：

### 路由

- [router/index.ts](/opt/claude/mystocks_spec/web/frontend/src/router/index.ts)
  - `market-realtime`
  - `market-technical`
  - `market-lhb`

### 配置

- [pageConfig.ts](/opt/claude/mystocks_spec/web/frontend/src/config/pageConfig.ts)
  - `component: 'MarketRealtimeTab.vue'`
  - `component: 'MarketKLineTab.vue'`
  - `component: 'DragonTigerAnalysis.vue'`

说明：
- `pageConfig` 当前以组件名字符串为主，不一定要改配置值本身
- 但实施前必须确认迁移后是否仍保持原组件名，或需要同步更新生成逻辑

## 5. 已知测试覆盖

### 路由/E2E

- [market-data.spec.ts](/opt/claude/mystocks_spec/web/frontend/tests/e2e/market-data.spec.ts)
  - 覆盖 `/market/realtime`
  - 覆盖 `/market/technical`
- [kline-chart.spec.ts](/opt/claude/mystocks_spec/web/frontend/tests/e2e/kline-chart.spec.ts)
  - 覆盖 `/market/technical`
- [menu-navigation-fixed.spec.ts](/opt/claude/mystocks_spec/web/frontend/tests/e2e/critical/menu-navigation-fixed.spec.ts)
  - 覆盖 `/dashboard -> /market/realtime`

### 单元/节点测试

- [marketRealtimeData.test.ts](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketRealtimeData.test.ts)
- [marketKlineData.test.ts](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts)
- [dragonTigerData.test.ts](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/__node_tests__/dragonTigerData.test.ts)
- [MarketKLineTab.spec.ts](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/__tests__/MarketKLineTab.spec.ts)

## 6. C1 实施时的精确动作

### Step 1：移动页面文件

1. `MarketRealtimeTab.vue` -> `views/market/Realtime.vue`
2. `MarketKLineTab.vue` -> `views/market/Technical.vue`
3. `DragonTigerAnalysis.vue` -> `views/market/LHB.vue`

### Step 2：移动最小本地依赖

1. `marketRealtimeData.ts`
2. `marketKlineData.ts`
3. `dragonTigerData.ts`

### Step 3：修正相对 import

每个页面迁移后，都要把相对依赖改成与新路径匹配。

### Step 4：更新路由 import 落点

只改 3 条路由：

- `market-realtime`
- `market-technical`
- `market-lhb`

### Step 5：核对配置与测试

- 核对 `pageConfig.ts` 与生成逻辑
- 更新所有引用旧绝对路径的测试或配置

## 7. 必须执行的验证门禁

### 最小门禁

1. `git diff --check`
2. `npm run lint`
3. `npm run test:e2e:stable`
4. `npx playwright test --config playwright.config.js --project=chromium tests/e2e/market-data.spec.ts`
5. `npx playwright test --config playwright.config.js --project=chromium tests/e2e/kline-chart.spec.ts`

### 补充门禁

如涉及组件名/配置变化，再加：

1. `tests/unit/config/pageConfig.test.ts`
2. 对应 node tests：
   - `marketRealtimeData.test.ts`
   - `marketKlineData.test.ts`
   - `dragonTigerData.test.ts`

## 8. 明确不在 C1 内做的事情

- 不迁移 `ArtDecoIndustryAnalysis.vue`
- 不迁移 `MarketConceptTab.vue`
- 不迁移 `FundFlowAnalysis.vue`
- 不迁移 `ArtDecoDataAnalysis.vue`
- 不抽 `src/shared`
- 不改 `artdeco-pages` 以外的其它 market/data 目录
- 不处理任何冻结页

## 9. 建议提交边界

如果后续执行 C1，建议最少拆成 2 个提交：

### Commit 1

- 页面与最小依赖文件移动
- 路由落点更新

### Commit 2

- 测试与配置修正
- 仅在确实需要时再补

## 10. 下一步审批口径

如果继续推进目录治理，建议下一步审批为：

`同意执行 Batch C1：3 个 market/data 试点页迁移`
