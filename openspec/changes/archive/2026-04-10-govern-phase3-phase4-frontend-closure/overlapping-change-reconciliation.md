# Overlapping Change Reconciliation

> **历史文档说明**:
> 本文档用于完成 `govern-phase3-phase4-frontend-closure` 的任务 `3.4`，
> 记录当前 change 与其他活跃 frontend restructure changes 的口径对齐关系。
> 目标是阻止旧假设在后续运行时变更中被继续直接执行。

**Generated:** 2026-04-07  
**Change:** `govern-phase3-phase4-frontend-closure`

## 1. Reconciliation Decision

在涉及以下对象时，本 change 的 repo-truth 结论优先于旧 change 中的泛化结构假设：

- `main-*.js/ts` 入口变体
- `verify-mount.js`
- `router/index.js*`
- `phase4.routes.js`
- `views/monitoring/*`
- `Phase4Dashboard`
- `TechnicalAnalysis`

原因是：2026-04-07 的 repo-truth 审计已经证明，这些对象不能再被当作“普通重复文件”或“可立即迁移/删除对象”处理。

## 2. Conflicting Assumptions Now Superseded

### 2.1 `restructure-frontend-directory`

需要被本 change 覆盖的旧假设：

1. **“Zero-duplicate routing” 可直接执行**
   - 当前不成立。
   - `Phase4Dashboard`、`TechnicalAnalysis`、`views/monitoring/*` 仍处于历史资产 / demo / fork / test-guard 的混合状态。

2. **“Deprecated pages can move to deprecated/ immediately”**
   - 当前不成立。
   - `architecture/STANDARDS.md` 已要求先做代码路径判定 + 功能树判定；
     2026-04-07 审计进一步证明多个页面仍承担历史证据或测试守护职责。

3. **`src/router/index.js` 可作为直接重构对象**
   - 当前不成立。
   - 当前 runtime truth 已锁定为 `index.html -> main-standard.ts -> router/index.ts`；
     `router/index.js*` 只能先按历史资产治理。

### 2.2 `refactor-web-frontend-menu-architecture`

需要被本 change 覆盖的旧假设：

1. **把 `web/frontend/src/router/index.js` 当作现役“路由配置（完全重构）”**
   - 当前不成立。
   - 相关 proposal/design 仍以 `router/index.js` 作为主路由承载体，但 repo truth 已转移到 `router/index.ts`。

### 2.3 `frontend-optimization-six-phase`

需要被本 change 覆盖的旧假设：

1. **将 `TechnicalAnalysis.vue` 的迁移/类型化结果继续等同于当前 canonical technical page**
   - 当前不成立。
   - `src/views/market/Technical.vue` 才是当前 canonical technical route body；
     root `TechnicalAnalysis.vue` 现在只属于历史 legacy 页面链路。

## 3. Operational Rule Going Forward

在后续 runtime mutation 开始前，执行人必须遵守以下口径：

1. 若旧 change 仍引用 `router/index.js` 作为当前路由真相，必须先改写为历史资产口径
2. 若旧 change 试图直接移动或删除 `views/monitoring/*`、`Phase4Dashboard`、`TechnicalAnalysis`，必须先补对应 retirement checklist
3. 若旧 change 试图把 `main.js` 视为可删入口，必须先完成 `verify-mount.js` 与相关脚本的 caller 收口

## 4. Practical Outcome

因此，`govern-phase3-phase4-frontend-closure` 当前承担的不是“重复一个更大的重构计划”，而是：

- 为已有重构 change 补充 repo-truth 约束
- 阻止旧计划在未完成资产分类前继续推进结构删除
- 规定 `E1-E4` 必须先于任何 `E5-E6` 结构性变更完成

## 5. Decision Output

后续如需继续执行 frontend directory 结构调整，默认流程应为：

1. 先引用本 change 的 `entry-variant-caller-matrix.md`
2. 再引用 `legacy-router-archive-strategy.md`
3. 再引用 `monitoring-retirement-checklist.md`
4. 再引用 `duplicate-page-retirement-checklist.md`
5. 只有这些前置约束已满足，才允许进入实际目录合并、命名收尾或 shim 清理
