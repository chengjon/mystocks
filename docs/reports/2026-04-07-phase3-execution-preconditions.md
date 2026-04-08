# Phase 3 Execution Preconditions

> **使用说明**:
> 本文件把 2026-04-07 前端结构审计结果转成执行前置清单，供后续 Phase 3 / Phase 4 批次直接引用。
> 当前共享规则与删除/迁移门禁仍以 `architecture/STANDARDS.md` 为准；本文件不是删除批准，也不替代用户审批。

**Generated:** 2026-04-07  
**Branch observed:** `wip/root-dirty-20260403`

---

## 1. Purpose

本清单只服务一件事：

- 把“已经查明的 repo truth”转换成“下一个执行批次必须先满足的前置条件”

避免下一批次再次出现以下问题：

- 把历史路由资产误当成现役页面
- 把测试守护资产误当成死代码
- 把双分叉实现当成普通 rename/merge 问题

---

## 2. Locked Truths

当前已可直接作为后续执行前提的事实：

1. 当前前端真实入口是：

```text
web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts
```

2. 当前 technical page canonical 入口是：

```text
src/views/market/Technical.vue
```

3. 以下对象不是当前主路由真相，但也不能直接按“无引用即删”处理：

- `src/views/monitoring/*`
- `src/views/demo/*`
- `src/views/converted.archive/*`
- `src/views/examples/*`
- `src/views/composables/*`
- `src/router/phase4.routes.js`

---

## 3. Batch Order

建议把 Phase 3 后续执行拆成下面 4 个微批次：

### Batch A

前端入口与历史路由文件收口

对象：

- `src/main.js`
- `src/main-standard.ts`
- `src/router/index.js*`
- `src/router/phase4.routes.js`

### Batch B

`views/composables/` root legacy support 审计收口

对象：

- `src/views/composables/*`
- 其 root-level 页面消费者

### Batch C

双分叉实现治理

对象：

- `Phase4Dashboard` root/demo 双分叉
- `TechnicalAnalysis` root/technical 双分叉

### Batch D

测试守护资产与历史示例资产分类归档

对象：

- `views/demo/`
- `views/converted.archive/`
- `views/examples/`

---

## 4. Preconditions By Batch

### 4.1 Batch A: Entry And Legacy Router Cleanup

#### Must Confirm

- `index.html` 仍只加载 `main-standard.ts`
- `verify-mount.js` 是否仍需要读取 `src/main.js`
- `router/index.js`、`index.js.clean`、`index.js.backup-phase2.3` 是否全部仅作为历史备份
- `phase4.routes.js` 是否存在任何主链外部消费方

#### Known Facts

- `main-standard.ts` 是当前 HTML 真入口
- `main.js` 仍被 `web/frontend/verify-mount.js` 直接读取
- `phase4.routes.js` 当前未发现被现役路由聚合链引用
- `phase4.routes.js` 还引用缺失文件 `StrategyMgmtPhase4.vue`
- `index.js` 已可标记为 `historical legacy router asset`
- `index.js.clean` 已可标记为 `historical broken backup / stale working copy`
- `index.js.backup-phase2.3` 已可标记为 `historical backup`

#### Exit Condition

- 可以明确给 `phase4.routes.js` 标注为：
  - `历史失效路由文件`
  - 或 `仍需保留的历史资产`
- 在 `verify-mount.js` 收口前，不应把 `main.js` 直接归为可删入口
- 当前路由资产分类报告已形成；下一步重点转为这些文件对应页面目标的功能树判定

---

### 4.2 Batch B: `views/composables/` Governance

#### Must Confirm

- 每个 composable 的主消费者是谁
- 是否属于 root-level legacy page support
- 是否只被 test/demo 持有
- 是否存在同名分叉实现

#### Known Facts

- `useAnalysis.ts`、`useBacktestWizard.ts`、`useEnhancedDashboard.ts`、`useSettings.ts`、`useTradingDashboard.ts` 等仍服务 root-level 页面
- `usePhase4Dashboard.ts` 与 demo 版并存
- `useTechnicalAnalysis.ts` 与 `views/technical/` 版并存
- 文件级状态表已形成：`docs/reports/2026-04-07-views-composables-status.md`

#### Exit Condition

- 为每个 `src/views/composables/*.ts` 补一个状态标签：
  - `legacy page support`
  - `test-guarded`
  - `demo support`
  - `duplicate-candidate`
  - `support module`

---

### 4.3 Batch C: Duplicate Candidate Resolution

#### Pair 1: `Phase4Dashboard`

对象：

- `src/views/Phase4Dashboard.vue`
- `src/views/composables/usePhase4Dashboard.ts`
- `src/views/demo/Phase4Dashboard.vue`
- `src/views/demo/composables/usePhase4Dashboard.ts`

#### Must Confirm

- root 版是否仍需作为历史页面保留
- demo 版是否是唯一需要保留的展示资产
- `phase4.routes.js` 是否需要保留为历史说明，还是应归档

#### Current Suggested Labels

- root 版：`失效但兼容/历史保留`
- demo 版：`实验/示例资产`
- 当前判定报告已形成：`docs/reports/2026-04-07-duplicate-page-functional-status.md`

#### Exit Condition

- 给 root 版写出“保留理由”或“退场条件”
- 给 demo 版写出“继续保留为示例资产”或“随 demo 资产一起归档”的明确口径

#### Pair 2: `TechnicalAnalysis`

对象：

- `src/views/TechnicalAnalysis.vue`
- `src/views/composables/useTechnicalAnalysis.ts`
- `src/views/technical/TechnicalAnalysis.vue`
- `src/views/technical/composables/useTechnicalAnalysis.ts`
- `src/views/market/Technical.vue`

#### Must Confirm

- root 版是否只是历史 root-level technical page
- `views/technical/` 版是否仍有独立展示价值
- 是否接受 `market/Technical.vue` 作为唯一 canonical page body

#### Current Suggested Labels

- root 版：`失效但兼容/历史保留`
- `views/technical/` 版：`独立分叉实现，待判定`
- `market/Technical.vue`：`有效 canonical 入口`
- 当前判定报告已形成：`docs/reports/2026-04-07-duplicate-page-functional-status.md`

#### Exit Condition

- 必须先明确是否继续保留 `views/technical/` 版
- 若不保留，需要连同 `technical-web3-style-support.spec.ts` 一起治理
- 若保留，需在文档中写清“它为何不是主路由真相却仍需存在”

---

### 4.4 Batch D: Demo / Archive / Example Assets

#### Must Confirm

- 哪些目录只是测试守护资产
- 哪些目录仍承载真实示例价值
- 哪些 spec 必须先迁移或删除，目录才可动

#### Known Facts

- `views/demo/` 当前主要被大量 config spec 直接读取
- `views/converted.archive/` 当前更接近历史迁移快照 + 测试守护对象
- `views/examples/` 当前更接近示例资产 + 测试守护对象
- `views/monitoring` 功能树状态已形成：`docs/reports/2026-04-07-monitoring-functional-status.md`

#### Exit Condition

- 在目录级改动前，必须先列出对应 spec 清单
- 不允许跳过 spec 治理直接做目录删除

---

## 5. Recommended Deliverables For Next Session

下一轮最适合直接产出的文档/结果：

1. `views/monitoring` 页面目标退场条件细化
   - 功能树判定已完成
   - 下一步需把 Playwright / Vitest 守护范围与归档策略对齐

2. `Phase4Dashboard` 与 `TechnicalAnalysis` 的退场条件细化
   - 当前功能树判定已完成
   - 下一步应把“保留理由”进一步对齐到具体 spec 与归档策略

3. 历史路由文件与页面目标的退场条件对齐
   - 已有 `docs/reports/2026-04-07-legacy-router-asset-status.md`
   - 已有 `docs/reports/2026-04-07-monitoring-functional-status.md`
   - 已有 `docs/reports/2026-04-07-views-composables-status.md`
   - 已有 `docs/reports/2026-04-07-duplicate-page-functional-status.md`
   - 下一步应把 route asset judgement 对齐到具体测试与归档步骤

4. 执行批次矩阵
   - 已有 `docs/reports/2026-04-07-phase3-4-execution-matrix.md`
   - 后续实施可直接按 E1-E6 批次推进

---

## 6. References

- `architecture/STANDARDS.md`
- `.planning/ROADMAP.md`
- `docs/reports/2026-04-07-legacy-router-asset-status.md`
- `docs/reports/2026-04-07-monitoring-functional-status.md`
- `docs/reports/2026-04-07-views-composables-status.md`
- `docs/reports/2026-04-07-duplicate-page-functional-status.md`
- `docs/reports/2026-04-07-phase3-4-execution-matrix.md`
- `docs/reports/2026-04-07-project-status-and-tech-debt-priorities.md`
- `docs/reports/2026-04-07-frontend-structure-repo-truth-audit.md`
- `web/frontend/index.html`
- `web/frontend/src/router/index.ts`
- `web/frontend/src/router/index.js`
- `web/frontend/src/router/phase4.routes.js`
- `web/frontend/src/views/Phase4Dashboard.vue`
- `web/frontend/src/views/demo/Phase4Dashboard.vue`
- `web/frontend/src/views/TechnicalAnalysis.vue`
- `web/frontend/src/views/technical/TechnicalAnalysis.vue`
- `web/frontend/src/views/market/Technical.vue`
