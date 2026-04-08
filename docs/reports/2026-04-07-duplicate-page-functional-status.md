# Duplicate Page Functional Status

> **使用说明**:
> 本文件用于补完 2026-04-07 Phase 3/4 审计中的 Batch C，专门记录 `Phase4Dashboard` 与 `TechnicalAnalysis` 双分叉实现的功能树状态。
> 当前共享规则、删除门禁与迁移收口口径仍以 `architecture/STANDARDS.md` 为准；本文件只给出状态判定与退场条件，不构成删除批准。

**Generated:** 2026-04-07  
**Branch observed:** `wip/root-dirty-20260403`

---

## 1. Scope

本次只处理两组高优先级双分叉对象：

1. `Phase4Dashboard`
2. `TechnicalAnalysis`

目标不是决定“现在删哪个”，而是先明确：

- 哪个对象是当前 canonical truth
- 哪些对象只是历史保留或示例资产
- 哪些对象仍需单独写保留理由

---

## 2. Locked Truths

当前已锁定的前提：

1. 当前前端主路由真相源是：

```text
web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts
```

2. 当前 technical canonical route body 是：

```text
src/views/market/Technical.vue
```

3. `phase4.routes.js` 已可判定为 `stale route asset`，不是当前主链入口。

---

## 3. Pair A: `Phase4Dashboard`

### 3.1 In-Scope Objects

- `src/views/Phase4Dashboard.vue`
- `src/views/composables/usePhase4Dashboard.ts`
- `src/views/demo/Phase4Dashboard.vue`
- `src/views/demo/composables/usePhase4Dashboard.ts`
- `src/router/phase4.routes.js`

### 3.2 Current Evidence

- `web/frontend/src/views/Phase4Dashboard.vue:213-240` 使用 root 版 `./composables/usePhase4Dashboard`
- `web/frontend/src/views/demo/Phase4Dashboard.vue:227-247` 使用 demo 版 `./composables/usePhase4Dashboard`
- `web/frontend/src/router/phase4.routes.js:7-30` 只为 root `Phase4Dashboard.vue` 提供旧 Phase 4 路由入口
- `web/frontend/tests/unit/config/root-demo-style-entrypoints.spec.ts:20-32` 同时守护：
  - `src/views/Phase4Dashboard.vue`
  - `src/views/demo/Phase4Dashboard.vue`
- `web/frontend/tests/unit/config/demo-mainline-gate.spec.ts:15` 明确把 `src/views/demo/Phase4Dashboard.vue` 视为 demo 资产治理范围
- `web/frontend/tests/unit/config/demo-phase4-dashboard-entry-style-source.spec.ts:6-7` 直接读取 demo 版页面

### 3.3 Functional Tree Judgment

| Object | Functional Status | Reason |
|---|---|---|
| `src/views/Phase4Dashboard.vue` + root composable | `失效但兼容/历史保留` | 已脱离当前主路由，仅剩旧 `phase4.routes.js` 证明其曾是独立页面资产 |
| `src/views/demo/Phase4Dashboard.vue` + demo composable | `实验/示例资产` | 仍被 demo mainline gate 与样式守护 spec 直接保护 |
| `src/router/phase4.routes.js` | `过期残留路由资产` | 不在主链且引用缺失页面 |

### 3.4 Keep Rationale

当前更合理的保留理由是：

- root 版不是当前主链，但仍是“曾经有独立页面/路由”的历史证据
- demo 版不是当前主路由真相，但仍承担示例/demo 资产职责

因此，现阶段不应把这组对象误写成：

- “两个等价实现，挑一个删”

更准确的口径应是：

- `root = historical page asset`
- `demo = example/demo asset`

### 3.5 Exit Conditions

对 root 版退场，至少应满足：

1. `phase4.routes.js` 已正式归档或退役说明完成
2. 不再需要 root `Phase4Dashboard.vue` 作为历史页面证据
3. 与 root 版关联的 style/source 守护已迁移或一并归档说明

对 demo 版退场，至少应满足：

1. demo 资产策略明确决定下线
2. `demo-mainline-gate.spec.ts` 与 `demo-phase4-dashboard-*.spec.ts` 完成治理
3. 确认不再需要 `Phase4Dashboard` 作为 demo 展示入口

---

## 4. Pair B: `TechnicalAnalysis`

### 4.1 In-Scope Objects

- `src/views/TechnicalAnalysis.vue`
- `src/views/composables/useTechnicalAnalysis.ts`
- `src/views/technical/TechnicalAnalysis.vue`
- `src/views/technical/composables/useTechnicalAnalysis.ts`
- `src/views/market/Technical.vue`

### 4.2 Current Evidence

- `web/frontend/src/views/TechnicalAnalysis.vue:137-166` 使用 root legacy composable
- `web/frontend/src/views/technical/TechnicalAnalysis.vue:259-290` 使用 `views/technical/` 版 composable
- `web/frontend/src/router/index.ts:49-52` 当前主路由 technical 页面已切到 `@/views/market/Technical.vue`
- `web/frontend/tests/unit/config/market-route-canonical-paths.spec.ts:12-14` 直接守护 `@/views/market/Technical.vue`
- `web/frontend/tests/unit/config/domain-body-migration-ownership.spec.ts:20-28` 明确把 `src/views/market/Technical.vue` 定义为 canonical page body
- `web/frontend/tests/unit/config/use-technical-analysis-types-cleanup.spec.ts:5-14` 直接守护 root legacy composable
- `web/frontend/tests/unit/config/technical-web3-style-support.spec.ts:9-27` 直接守护 `views/technical/TechnicalAnalysis.vue`
- `web/frontend/tests/unit/config/console-log-cleanup-batch-23.spec.ts:5-10` 直接守护 `views/technical/composables/useTechnicalAnalysis.ts`

### 4.3 Functional Tree Judgment

| Object | Functional Status | Reason |
|---|---|---|
| `src/views/market/Technical.vue` | `有效 canonical 入口` | 当前主路由与 ownership tests 都已把它锁定为 canonical technical page |
| `src/views/TechnicalAnalysis.vue` + root composable | `失效但兼容/历史保留` | 已脱离当前主路由，但仍保留 root legacy 页面与 legacy composable 守护 |
| `src/views/technical/TechnicalAnalysis.vue` + technical composable | `独立分叉实现，待判定` | 不在主路由真相链，但仍有独立页面样式与 composable 守护 |

### 4.4 Keep Rationale

当前更合理的保留理由是：

- `market/Technical.vue` 是当前唯一 canonical technical route body
- root `TechnicalAnalysis.vue` 更像旧 technical page
- `views/technical/TechnicalAnalysis.vue` 更像一个历史上独立存在过的主题化 / 子域化 technical 实现

因此，当前不应把这组三者误写成：

- “两个旧页 + 一个新页，旧页都可删”

更准确的口径应是：

- `market = canonical`
- `root = historical legacy page`
- `technical/ = independent fork pending judgment`

### 4.5 Exit Conditions

对 root 版退场，至少应满足：

1. 历史 `router/index.js*` 已明确只作为历史资产保留，不再承担任何迁移说明职责
2. `use-technical-analysis-types-cleanup.spec.ts` 的守护职责得到迁移或归档解释
3. 不再需要 root `TechnicalAnalysis.vue` 作为历史 technical 页面证据

对 `views/technical/` 版退场，至少应满足：

1. 确认它不再具有独立展示价值
2. `technical-web3-style-support.spec.ts` 与 `console-log-cleanup-batch-23.spec.ts` 完成治理
3. 确认所有仍需保留的 technical 页面职责都已由 `market/Technical.vue` 或其他 canonical 页面承接

---

## 5. Consolidated Recommendation

当前最稳妥的 Phase 3/4 口径是：

1. `market/Technical.vue` 继续锁定为唯一 canonical technical page
2. `Phase4Dashboard` root/demo 先按“历史页面资产 + demo资产”并存处理
3. root `TechnicalAnalysis` 与 `views/technical/TechnicalAnalysis` 继续按“双分叉存量”处理
4. 下一步优先写“退场条件对齐”，不要直接做文件删除或机械合并

---

## 6. Evidence

本次报告主要基于以下证据：

```bash
nl -ba web/frontend/src/views/Phase4Dashboard.vue | sed -n '200,260p'
nl -ba web/frontend/src/views/demo/Phase4Dashboard.vue | sed -n '220,280p'
nl -ba web/frontend/src/views/TechnicalAnalysis.vue | sed -n '130,190p'
nl -ba web/frontend/src/views/technical/TechnicalAnalysis.vue | sed -n '250,310p'
nl -ba web/frontend/src/views/market/Technical.vue | sed -n '1,120p'
rg -n --no-messages "Phase4Dashboard\.vue|TechnicalAnalysis\.vue|market/Technical\.vue" web/frontend/tests/unit/config -g '*.spec.ts'
```

---

## 7. References

- `architecture/STANDARDS.md`
- `docs/reports/2026-04-07-legacy-router-asset-status.md`
- `docs/reports/2026-04-07-views-composables-status.md`
- `docs/reports/2026-04-07-frontend-structure-repo-truth-audit.md`
- `docs/reports/2026-04-07-phase3-execution-preconditions.md`
- `web/frontend/src/views/Phase4Dashboard.vue`
- `web/frontend/src/views/demo/Phase4Dashboard.vue`
- `web/frontend/src/views/TechnicalAnalysis.vue`
- `web/frontend/src/views/technical/TechnicalAnalysis.vue`
- `web/frontend/src/views/market/Technical.vue`
