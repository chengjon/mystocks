# Duplicate Page Retirement Checklist

> **历史文档说明**:
> 本文档用于完成 `govern-phase3-phase4-frontend-closure` 的任务 `2.4`，
> 对齐 `Phase4Dashboard` 与 `TechnicalAnalysis` 的 root / demo / fork / canonical 角色，
> 并给出退场前置条件。
> 本文档不批准删除、合并或重命名。

**Generated:** 2026-04-07  
**Change:** `govern-phase3-phase4-frontend-closure`  
**Task:** `2.4 Produce and approve duplicate-page retirement checklists for Phase4Dashboard and TechnicalAnalysis`

## 1. Locked Judgments

当前需要固定的判断如下：

- `web/frontend/src/views/market/Technical.vue` = `有效 canonical 入口`
- `web/frontend/src/views/TechnicalAnalysis.vue` = `失效但兼容/历史保留`
- `web/frontend/src/views/technical/TechnicalAnalysis.vue` = `独立分叉实现，待判定`
- `web/frontend/src/views/Phase4Dashboard.vue` = `失效但兼容/历史保留`
- `web/frontend/src/views/demo/Phase4Dashboard.vue` = `实验/示例资产`

这意味着后续治理不是“二选一删重”，而是“按角色分别退场”。

## 2. Pair A: Phase4Dashboard

### 2.1 Role Matrix

| Object | Current Role | Why It Still Exists | Retirement Blocker |
|---|---|---|---|
| `src/views/Phase4Dashboard.vue` | historical page asset | 仍由 `phase4.routes.js` 证明其曾经有独立路由职责 | root 页面历史证据尚未收口 |
| `src/views/composables/usePhase4Dashboard.ts` | support module for historical page asset | 被 root 页面直接使用 | 跟随 root 页面一起治理 |
| `src/views/demo/Phase4Dashboard.vue` | demo/example asset | 仍被 demo mainline 与样式守护测试保护 | demo 资产策略尚未明确下线 |
| `src/views/demo/composables/usePhase4Dashboard.ts` | support module for demo asset | 被 demo 页面直接使用 | 跟随 demo 页面一起治理 |
| `src/router/phase4.routes.js` | stale route asset | 仍把 root 页面保留为历史独立入口证据 | E2 / E4 未闭环 |

### 2.2 Test Guard Mapping

| Test File | Guarded Object |
|---|---|
| `tests/unit/config/root-demo-style-entrypoints.spec.ts` | root `Phase4Dashboard.vue` + demo `Phase4Dashboard.vue` |
| `tests/unit/config/demo-mainline-gate.spec.ts` | demo 目录治理边界，间接锁定 `src/views/demo/Phase4Dashboard.vue` |
| `tests/unit/config/demo-phase4-dashboard-entry-style-source.spec.ts` | demo `Phase4Dashboard.vue` |
| `tests/unit/config/demo-phase4-dashboard-style-source.spec.ts` | demo `styles/Phase4Dashboard.scss` |

### 2.3 Retirement Checklist

- [ ] 2.3.1 `phase4.routes.js` 已正式归档或补足历史退役说明
- [ ] 2.3.2 root `Phase4Dashboard.vue` 是否还需要作为历史页面证据，已得到明确结论
- [ ] 2.3.3 `root-demo-style-entrypoints.spec.ts` 对 root 版的守护职责已迁移或归档说明完成
- [ ] 2.3.4 demo 资产是否继续保留，已由 demo 治理口径明确
- [ ] 2.3.5 `demo-mainline-gate.spec.ts` 与 `demo-phase4-dashboard-*.spec.ts` 已完成同步治理
- [ ] 2.3.6 root 与 demo composable 的保留/迁移路径已分别记录

### 2.4 Do-Not-Do

禁止：

1. 把 root 版和 demo 版当成“两个完全等价实现”
2. 在 `phase4.routes.js` 未收口前直接删除 root `Phase4Dashboard.vue`
3. 在 demo 侧测试未治理前删除 demo `Phase4Dashboard.vue`

## 3. Pair B: TechnicalAnalysis

### 3.1 Role Matrix

| Object | Current Role | Why It Still Exists | Retirement Blocker |
|---|---|---|---|
| `src/views/market/Technical.vue` | canonical technical page | 当前 `router/index.ts` 直接指向它，ownership tests 也锁定它 | 除非主路由与 canonical tests 同步变更，否则不能降级 |
| `src/views/TechnicalAnalysis.vue` | historical legacy page | 历史 `router/index.js` 仍把 `/technical` 指向它；root legacy composable 仍被测试守护 | 历史 route 证据与 legacy composable 仍未退场 |
| `src/views/composables/useTechnicalAnalysis.ts` | support module for historical legacy page | 被 root legacy technical page 使用，且有单独清理测试 | `use-technical-analysis-types-cleanup.spec.ts` 仍守护 |
| `src/views/technical/TechnicalAnalysis.vue` | independent fork pending judgment | 虽不在主路由，但仍被独立 web3/style 规则守护 | 需要先判断是否仍有独立展示价值 |
| `src/views/technical/composables/useTechnicalAnalysis.ts` | support module for independent fork | 被 `views/technical/TechnicalAnalysis.vue` 使用 | `console-log-cleanup-batch-23.spec.ts` 仍守护 |

### 3.2 Test Guard Mapping

| Test File | Guarded Object |
|---|---|
| `tests/unit/config/market-route-canonical-paths.spec.ts` | `router/index.ts -> @/views/market/Technical.vue` |
| `tests/unit/config/domain-body-migration-ownership.spec.ts` | `src/views/market/Technical.vue` canonical ownership |
| `tests/unit/config/use-technical-analysis-types-cleanup.spec.ts` | root `src/views/composables/useTechnicalAnalysis.ts` |
| `tests/unit/config/technical-web3-style-support.spec.ts` | `src/views/technical/TechnicalAnalysis.vue` + web3 style files |
| `tests/unit/config/console-log-cleanup-batch-23.spec.ts` | `src/views/technical/composables/useTechnicalAnalysis.ts` |

### 3.3 Retirement Checklist

- [ ] 3.3.1 `market/Technical.vue` 的 canonical 身份继续保持锁定，或有新的审批变更替代它
- [ ] 3.3.2 历史 `router/index.js*` 已明确只作为历史资产保留，不再承担 technical 迁移说明职责
- [ ] 3.3.3 root `TechnicalAnalysis.vue` 是否仍需作为历史 technical 页面证据，已得到明确结论
- [ ] 3.3.4 `use-technical-analysis-types-cleanup.spec.ts` 的守护职责已迁移或归档说明完成
- [ ] 3.3.5 `views/technical/TechnicalAnalysis.vue` 是否仍有独立展示价值，已得到明确结论
- [ ] 3.3.6 `technical-web3-style-support.spec.ts` 与 `console-log-cleanup-batch-23.spec.ts` 已完成同步治理
- [ ] 3.3.7 root 与 `views/technical/` 两条 composable 链的去向分别记录完成

### 3.4 Do-Not-Do

禁止：

1. 把 root `TechnicalAnalysis.vue` 和 `views/technical/TechnicalAnalysis.vue` 简化成同一类“旧页面”
2. 在 canonical tests 未调整前动 `market/Technical.vue`
3. 只删页面不处理对应 composable 与守护测试

## 4. Consolidated Retirement Order

推荐顺序如下：

1. 保持 `market/Technical.vue` 作为唯一 canonical technical page
2. 先完成 `phase4.routes.js` 与 `router/index.js*` 的历史资产收口
3. 再分别判断 `Phase4Dashboard` root/demo 与 `TechnicalAnalysis` root/fork 的保留价值
4. 最后才处理页面、composable、样式和测试的一起迁移或归档

## 5. Decision Output for Batch E4

本批次产出如下：

- `Phase4Dashboard`：
  - `root = historical page asset`
  - `demo = example/demo asset`
- `TechnicalAnalysis`：
  - `market = canonical`
  - `root = historical legacy page`
  - `technical/ = independent fork pending judgment`

后续任何删除、合并、改路由动作，都必须以这个角色划分为前提，而不是把它们当普通重复文件处理。
