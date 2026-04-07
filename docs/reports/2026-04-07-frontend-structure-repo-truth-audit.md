# Frontend Structure Repo Truth Audit

> **使用说明**:
> 本文件记录 2026-04-07 针对前端结构收敛 Phase 3 的一次 repo-truth 审计结论。
> 当前共享规则与删除/迁移门禁仍以 `architecture/STANDARDS.md` 为准；本文件用于后续批次执行前的事实对齐，不替代审批。

**Generated:** 2026-04-07  
**Branch observed:** `wip/root-dirty-20260403`

---

## 1. Audit Scope

本次审计只回答三个问题：

1. 当前前端真实入口是什么
2. 当前主路由实际指向哪些页面目录
3. `views/` 下遗留目录哪些仍在活跃链路中，哪些暂时只有残留/测试证据

---

## 2. Current Truth

### 2.1 Frontend Entry Truth

当前实际前端入口已经不是 `TBD`，而是：

- `web/frontend/index.html` 直接加载 `/src/main-standard.ts`
- `web/frontend/src/main-standard.ts` 挂载 `App.vue` 并使用 `./router/index.ts`
- `web/frontend/vite.config.mts` 采用标准 Vite SPA 配置，未声明替代 HTML 入口或 Rollup `input`
- `web/frontend/ecosystem.config.js` 与 `web/ecosystem.dev.config.js` 都是通过 `npm run preview` / `npm run dev` 启动 Vite，而不是指定其它入口文件

因此，当前前端入口真相应明确写成：

```text
index.html -> /src/main-standard.ts -> /src/router/index.ts
```

### 2.2 Route Truth

当前业务主路由真相仍以 `web/frontend/src/router/index.ts` 为准。

主业务域页面主要位于：

- `web/frontend/src/views/market/`
- `web/frontend/src/views/data/`
- `web/frontend/src/views/watchlist/`
- `web/frontend/src/views/strategy/`
- `web/frontend/src/views/trade/`
- `web/frontend/src/views/risk/`
- `web/frontend/src/views/system/`

### 2.3 Confirmed Active Exceptions

以下目录/文件虽然不属于 `views/<domain>/` 主干，但仍是现役链路的一部分：

- `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
  - `/dashboard` 当前仍直接路由到这里
- `web/frontend/src/views/TradingDashboard.vue`
  - `/trade/terminal` 当前仍直接路由到这里
- `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
  - `/detail/news/:symbol` 当前仍直接路由到这里
- `web/frontend/src/views/stocks/Screener.vue`
  - 虽然不是主路由入口，但 `web/frontend/src/views/watchlist/Screener.vue` 仍直接包装它
- `web/frontend/src/views/stocks/stockScreenerData.ts`
  - `web/frontend/src/composables/market/useDataAnalysis.ts` 仍直接引用它

---

## 3. Directory Status Judgment

| Directory / Area | Current Status | Evidence Summary | Current Judgment |
|---|---|---|---|
| `views/market` / `data` / `watchlist` / `strategy` / `trade` / `risk` / `system` | Active canonical routed pages | `router/index.ts` directly imports these paths | `有效` |
| `views/artdeco-pages` | Active compatibility / embedded source set | `router/index.ts` 仍直接导入多个 tab/page；多个 domain page 也继续复用其中数据或包装组件 | `有效，但非唯一真相源` |
| `views/announcement` | Active routed exception | `router/index.ts` 306 行直接导入 `AnnouncementMonitor.vue` | `有效` |
| `views/stocks` | Active compatibility dependency | `watchlist/Screener.vue` 与 `composables/market/useDataAnalysis.ts` 仍直接引用 | `失效主路由层，但兼容保留中` |
| `views/monitoring` | Not part of current `router/index.ts` truth, but still preserved by historical router files and test guards | `router/index.ts` 未导入；`router/index.js` 与 `router/index.js.backup-phase2.3` 仍直接导入 `WatchlistManagement.vue` / `RiskDashboard.vue`；`monitoring-*.spec.ts` 仍对其样式与页面文件做守护 | `历史路由目标 + 测试守护对象，待判定` |
| `views/composables` | Primarily serves root-level legacy views via relative imports | `Analysis.vue`、`BacktestWizard.vue`、`EnhancedDashboard.vue`、`Phase4Dashboard.vue`、`PortfolioManagement.vue`、`Settings.vue`、`TechnicalAnalysis.vue`、`TradingDashboard.vue`、`monitor.vue` 等 root-level 页面仍通过 `./composables/*` 相对路径引用；当前未发现 routed domain pages 直接依赖该目录 | `root-level legacy view support，待判定` |
| `views/converted.archive` | Present; no active router/views/composables import found | 仍有专门 config spec，说明删除前必须同步测试治理 | `待判定` |
| `views/demo` | Present; no active router/views/composables import found | 仍有多组 config spec 关注 demo 样式/入口 | `待判定` |
| `views/examples` | Present; no active router/views/composables import found | 仍有 example spec | `待判定` |
| `views/freqtrade-demo` | Present; no active router/views/composables import found | 仍有 `freqtrade-demo-mainline-gate.spec.ts` | `待判定` |
| `views/tdxpy-demo` | Present; no active router/views/composables import found | 仍有 `tdxpy-demo-mainline-gate.spec.ts` | `待判定` |
| `views/advanced-analysis` | Present; no active router/views/composables import found | 仍有 `advanced-analysis-mainline-gate.spec.ts` | `待判定` |
| `views/stock-analysis` | Present; no active router/views/composables import found | 仍有多组 `stock-analysis-*` spec | `待判定` |
| `views/technical` | Present; no active router/views/composables import found | `market/Technical.vue` 才是当前主路由入口 | `待判定` |
| `views/trading` | Present; no active router/views/composables import found | 仍有 `trading-mainline-gate.spec.ts` | `待判定` |
| `views/trading-decision` | Present; no active router/views/composables import found | 仍有 `trading-decision-mainline-gate.spec.ts` | `待判定` |
| `views/trade-management` | Present; no active router/views/composables import found | 仍有 `trade-management-*` spec | `待判定` |

说明：

- 这里的“未发现 active import”只代表本次审计范围内，对 `router/`、`views/`、`src/composables/` 的 TS/Vue 代码检索结果。
- 这不是“可以删除”的同义词。
- 按 `architecture/STANDARDS.md`，删除前仍需同时完成代码路径判定与功能树判定。

---

## 4. Residual Entry Variants

当前 `web/frontend/src/` 下仍存在多份入口变体：

- `main.js`
- `main-debug.js`
- `main-enhanced.ts`
- `main-minimal.ts`
- `main-original.js`
- `main-simplified.js`
- `main-standard.ts`
- `main-test.js`

但本次审计中，唯一被 `index.html` 实际加载的是：

- `main-standard.ts`

因此，这些 `main-*` 文件当前更像：

- 历史调试/迁移产物
- 本地实验入口
- 尚未完成收口的兼容残留

它们不应再被当作“当前入口待确认”的证据来源。

但这不等于它们都已与仓库完全脱钩。当前已确认：

- `web/frontend/index.html` 只加载 `main-standard.ts`
- `web/frontend/verify-mount.js` 仍直接读取 `web/frontend/src/main.js`

因此：

- `main-standard.ts` 是现役入口
- `main.js` 仍是脚本校验对象
- 其余 `main-*` 变体更接近历史/调试残留，但仍应在归档前补一轮 test/script caller 审计

---

## 5. Immediate Recommendations

### Priority A

把 `.planning/ROADMAP.md` 中 Phase 3 的 `Frontend entry: TBD` 改为基于证据的当前真相：

```text
Canonical frontend entry = web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts
```

### Priority B

不要把以下目录当作可直接清理对象：

- `views/announcement`
- `views/stocks`
- `views/artdeco-pages`

它们当前仍在现役路由或现役页面依赖链上。

### Priority C

下一批次应优先审计 `views/monitoring`，并同步检查：

- `web/frontend/src/router/index.js`
- `web/frontend/src/router/index.js.clean`
- `web/frontend/src/router/index.js.backup-phase2.3`
- `web/frontend/tests/unit/config/monitoring-*.spec.ts`

目标不是立即删除，而是先确认这些文件分别属于：

- 当前真相
- 历史备份
- 测试守护对象
- 可归档对象

当前已确认的最小事实：

- `web/frontend/src/router/index.ts` 不再把 `views/monitoring/` 作为主路由页面
- `web/frontend/src/router/index.js` 与 `web/frontend/src/router/index.js.backup-phase2.3` 仍把它作为 monitoring layout 的页面目标
- `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts`
- `web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts`
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`

仍把这些页面/样式文件当作受保护对象

### Priority D

对 `converted.archive/`、`demo/`、`examples/`、`freqtrade-demo/`、`tdxpy-demo/` 等目录，建议先补一轮“功能树状态表”，再决定归档或保留策略；不要仅凭目录名判断。

### Priority E

对 `views/composables/`，下一步不应直接移动目录，而应先分组：

- 仍由 root-level legacy views 使用的 composable
- 与新 domain 页面功能重复、可以迁移或合并的 composable
- 只剩测试或 demo 依赖的 composable

### Priority F

对 `main-*` 入口变体，下一步建议先把调用方分成三类：

- HTML 真入口
- 验证/诊断脚本入口
- 纯历史调试入口

至少在 `verify-mount.js` 完成收口前，不应把 `main.js` 直接视为可删文件。

---

## 6. `views/composables` File-Level Audit

当前 `web/frontend/src/views/composables/` 下文件可先按下面方式分类：

| File | Current Primary Consumer | Notes | Current Judgment |
|---|---|---|---|
| `useAdvancedAnalysis.ts` | `src/views/AdvancedAnalysis.vue` | root-level legacy page 相对引用 | `legacy page support` |
| `useAnalysis.ts` | `src/views/Analysis.vue` | 另有 config spec 直接读取源码 | `legacy page support + test-guarded` |
| `useBacktestWizard.ts` | `src/views/BacktestWizard.vue` | root-level legacy page 相对引用 | `legacy page support` |
| `useEnhancedDashboard.ts` | `src/views/EnhancedDashboard.vue` | root-level legacy page 相对引用 | `legacy page support` |
| `useIndustryConceptAnalysis.ts` | `src/views/IndustryConceptAnalysis.vue` | root-level legacy page 相对引用 | `legacy page support` |
| `usePortfolioManagement.ts` | `src/views/PortfolioManagement.vue` | root-level legacy page 相对引用 | `legacy page support` |
| `usePyprofilingDemo.ts` | `src/views/PyprofilingDemo.vue` | root-level demo shell 相对引用 | `legacy/demo support` |
| `useSettings.ts` | `src/views/Settings.vue` | root-level legacy page 相对引用 | `legacy page support` |
| `useTradingDashboard.ts` | `src/views/TradingDashboard.vue` | 同目录下测试仍直接覆盖 | `legacy page support + test-guarded` |
| `tradingDashboardActions.ts` | `useTradingDashboard.ts` | 另有 `__node_tests__` 直接覆盖 | `support module + test-guarded` |
| `usemonitor.ts` | `src/views/monitor.vue` | root-level legacy monitor 页面相对引用 | `legacy page support` |
| `useTechnicalAnalysis.ts` | `src/views/TechnicalAnalysis.vue` | 与 `src/views/technical/composables/useTechnicalAnalysis.ts` 并存 | `duplicate-candidate` |
| `useTechnicalAnalysis.shortcuts.ts` | `useTechnicalAnalysis.ts` | 只服务 root-level legacy technical composable | `support module` |
| `useTechnicalAnalysis.types.ts` | `useTechnicalAnalysis.ts` | 只服务 root-level legacy technical composable | `support module` |
| `usePhase4Dashboard.ts` | `src/views/Phase4Dashboard.vue` | 与 `src/views/demo/composables/usePhase4Dashboard.ts` 并存 | `duplicate-candidate` |

### Duplicate Candidate Notes

本次已经确认两组“重名且大体量”的分叉实现：

- `src/views/composables/usePhase4Dashboard.ts`：`380` 行
- `src/views/demo/composables/usePhase4Dashboard.ts`：`355` 行
- `diff -u` 显示两者不是薄包装，而是字段模型、service 依赖、图表与统计逻辑都存在明显分叉

- `src/views/composables/useTechnicalAnalysis.ts`：`441` 行
- `src/views/technical/composables/useTechnicalAnalysis.ts`：`485` 行
- `diff -u` 显示两者不是兼容导出，而是 API 依赖、状态模型、图表实现和交互逻辑均不同

这两组对象应优先视为：

- Phase 3/4 的重复实现候选
- 需要先做职责边界判定，再决定保留谁、谁降级为兼容层或被拆分

当前不适合直接做机械迁移或删除。

### Duplicate Priority Assessment

#### `usePhase4Dashboard` Pair

当前证据显示：

- `src/views/Phase4Dashboard.vue` 仍有历史独立路由资产 `src/router/phase4.routes.js`
- 但在本次审计范围内，未发现 `phase4.routes.js` 被当前 `router/index.ts` 或其他路由聚合链引用
- `src/router/phase4.routes.js` 还引用了缺失文件 `src/views/StrategyMgmtPhase4.vue`
- `src/views/Phase4Dashboard.vue` 也被 `root-demo-style-entrypoints.spec.ts` 纳入 root/demo entrypoint 守护
- `src/views/demo/Phase4Dashboard.vue` 主要被 demo 相关 style/source spec 守护

因此当前更合理的初步判断是：

- root 版本更接近 `历史页面资产 / 脱离主链的旧路由资产`
- demo 版本更接近 `示例/demo资产`

这意味着后续若要收敛，优先问题不是“删哪个”，而是先决定：

- 是否仍保留 `phase4.routes.js` 这一历史入口
- `Phase4Dashboard` 是否属于继续保留的历史页面，还是整体降级为 demo/example 资产

并且应优先补一个更具体的治理判断：

- `phase4.routes.js` 当前已经具备“过期残留路由文件”的特征，因为它既未接入现役路由链，又指向缺失页面

#### `useTechnicalAnalysis` Pair

当前证据显示：

- `src/views/TechnicalAnalysis.vue` 仍被历史 `router/index.js` 作为页面目标
- `src/views/composables/useTechnicalAnalysis.ts` 仍有单独的 legacy cleanup spec 守护
- `src/views/technical/TechnicalAnalysis.vue` 与 `src/views/technical/composables/useTechnicalAnalysis.ts` 则有独立的 `technical-web3-style-support.spec.ts`
- 当前主业务路由 `router/index.ts` 实际使用的是 `src/views/market/Technical.vue`，不是这两者中的任意一个
- `market-route-canonical-paths.spec.ts` 与 `domain-body-migration-ownership.spec.ts` 都把 `src/views/market/Technical.vue` 标为 canonical technical page body

因此当前更合理的初步判断是：

- root 版本更接近 `历史 root-level technical page`
- `views/technical/` 版本更接近 `独立子域实现 / 主题化分叉实现`

这组对象的核心问题不是简单重复，而是：

- 两套不同 UI/交互模型并存
- 两套不同 API / 图表 / 状态模型并存
- 但当前主路由已经绕开它们，改走 `market/Technical.vue`

因此它们应被视为：

- `离开主路由后的双分叉存量`
- 需要单独做功能树判定，而不是直接合并文件

### Functional Tree Status Suggestion

基于当前证据，先给出非删除性的功能树建议标签：

| Object | Suggested Functional Status |
|---|---|
| `src/views/Phase4Dashboard.vue` + `src/views/composables/usePhase4Dashboard.ts` | `失效但兼容/历史保留` |
| `src/views/demo/Phase4Dashboard.vue` + `src/views/demo/composables/usePhase4Dashboard.ts` | `实验/示例资产` |
| `src/views/TechnicalAnalysis.vue` + `src/views/composables/useTechnicalAnalysis.ts` | `失效但兼容/历史保留` |
| `src/views/technical/TechnicalAnalysis.vue` + `src/views/technical/composables/useTechnicalAnalysis.ts` | `独立分叉实现，待判定` |
| `src/views/market/Technical.vue` | `有效 canonical 入口` |

这些标签仅用于后续治理排序，不等同于删除批准。

### Suggested Exit Conditions

| Object | Suggested Exit Condition Before Any Deletion/Archive |
|---|---|
| `src/router/phase4.routes.js` | 确认无任何路由聚合链、测试或外部文档再把它当现役入口；补一条“历史失效”说明后再决定归档 |
| `src/views/Phase4Dashboard.vue` + `src/views/composables/usePhase4Dashboard.ts` | 先确认是否仍需作为历史页面保留；若不保留，应把相关 style/spec 守护迁移到 demo 版或归档说明 |
| `src/views/demo/Phase4Dashboard.vue` + `src/views/demo/composables/usePhase4Dashboard.ts` | 若继续作为示例资产，保留并在文档中明确为 demo truth；若不再需要，先清理对应 demo specs |
| `src/views/TechnicalAnalysis.vue` + `src/views/composables/useTechnicalAnalysis.ts` | 确认历史 `router/index.js*` 是否只作为备份；若是，应在 root legacy 路由资产审计后再决定归档 |
| `src/views/technical/TechnicalAnalysis.vue` + `src/views/technical/composables/useTechnicalAnalysis.ts` | 先确认是否还有独立子域/主题化展示价值；若无，再与对应 web3 style specs 一并治理 |
| `src/views/market/Technical.vue` | 作为 canonical 入口，除非主路由和 canonical ownership tests 同步变更，否则不得降级 |

---

## 7. Demo / Archive / Example Directories

### 7.1 `views/demo`

当前可直接看到的顶层文件包括：

- `OpenStockDemo.vue`
- `Phase4Dashboard.vue`
- `PyprofilingDemo.vue`
- `StockAnalysisDemo.vue`
- `Wencai.vue`
- `composables/usePhase4Dashboard.ts`

本次审计范围内未发现这些文件被当前 `router/index.ts` 直接导入，但大量 `web/frontend/tests/unit/config/*.spec.ts` 仍直接读取：

- `src/views/demo/*.vue`
- `src/views/demo/openstock/components/*`
- `src/views/demo/pyprofiling/components/*`
- `src/views/demo/stock-analysis/components/*`
- `src/views/demo/styles/*`

因此当前更准确的判断是：

- `views/demo/` 主要是 `测试守护对象 + 历史/demo资产`
- 不是当前主路由真相
- 也不是可以直接整目录删除的对象

### 7.2 `views/converted.archive`

当前目录中仍有多份 `.vue` 页面文件，例如：

- `dashboard.vue`
- `market-data.vue`
- `trading-management.vue`
- `data-analysis.vue`
- `risk-management.vue`

本次审计范围内未发现它们被现役 `router/index.ts` 或 TS/Vue 主链路直接导入，但相关 config spec 仍直接读取这些文件与样式源。

因此当前判断是：

- `views/converted.archive/` 更接近 `历史迁移快照 + 测试守护对象`
- 若后续要归档或删除，必须先同步处理对应 spec

### 7.3 `views/examples`

当前目录主要包含：

- `PageConfigExample.vue`
- `TradingDashboard.migrated.vue`
- `WebSocketConfigExample.vue`
- `composables/useTradingDashboard.migrated.ts`

本次审计范围内未发现它们进入当前主路由，但 config spec 仍直接引用这些示例文件。

因此当前判断是：

- `views/examples/` 属于 `示例资产 + 测试守护对象`
- 不应和“未使用死代码”混为一谈

---

## 8. Evidence Commands

本次审计主要使用以下命令：

```bash
sed -n '1,260p' web/frontend/src/router/index.ts
sed -n '260,380p' web/frontend/src/router/index.ts
find web/frontend/src/views -maxdepth 2 -type d | sort
find web/frontend/src/views -maxdepth 2 -type f \( -name '*.vue' -o -name '*.ts' -o -name '*.tsx' \) | sort
sed -n '1,120p' web/frontend/index.html
sed -n '1,220p' web/frontend/vite.config.mts
sed -n '1,220p' web/frontend/ecosystem.config.js
sed -n '1,220p' web/ecosystem.dev.config.js
sed -n '1,220p' web/frontend/src/main-standard.ts
rg -n --glob '*.ts' --glob '*.vue' "@/views/announcement/" web/frontend/src/router web/frontend/src/views web/frontend/src/composables
rg -n --glob '*.ts' --glob '*.vue' "@/views/stocks/" web/frontend/src/router web/frontend/src/views web/frontend/src/composables
rg -n --glob '*.ts' --glob '*.vue' "@/views/monitoring/" web/frontend/src/router web/frontend/src/views web/frontend/src/composables
for f in web/frontend/src/views/composables/*.ts; do ...; done
sed -n '1,220p' web/frontend/verify-mount.js
diff -u web/frontend/src/views/composables/usePhase4Dashboard.ts web/frontend/src/views/demo/composables/usePhase4Dashboard.ts
diff -u web/frontend/src/views/composables/useTechnicalAnalysis.ts web/frontend/src/views/technical/composables/useTechnicalAnalysis.ts
wc -l web/frontend/src/views/composables/usePhase4Dashboard.ts web/frontend/src/views/demo/composables/usePhase4Dashboard.ts web/frontend/src/views/composables/useTechnicalAnalysis.ts web/frontend/src/views/technical/composables/useTechnicalAnalysis.ts
find web/frontend/src/views/demo -maxdepth 2 -type f \( -name '*.vue' -o -name '*.ts' -o -name '*.js' \) | sort
find web/frontend/src/views/converted.archive -maxdepth 2 -type f \( -name '*.vue' -o -name '*.ts' -o -name '*.js' \) | sort
find web/frontend/src/views/examples -maxdepth 2 -type f \( -name '*.vue' -o -name '*.ts' -o -name '*.js' \) | sort
```

---

## 9. Reference Files

- `architecture/STANDARDS.md`
- `.planning/ROADMAP.md`
- `docs/guides/frontend-structure.md`
- `web/frontend/index.html`
- `web/frontend/vite.config.mts`
- `web/frontend/ecosystem.config.js`
- `web/ecosystem.dev.config.js`
- `web/frontend/src/main-standard.ts`
- `web/frontend/src/router/index.ts`
- `web/frontend/src/router/homeRoute.ts`
