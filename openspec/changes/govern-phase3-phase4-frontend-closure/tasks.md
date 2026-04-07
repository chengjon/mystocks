## 1. Spec Formalization

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

- [x] 1.1 Add evidence-based frontend route truth and historical route-asset classification requirements to `frontend-routing`
  - Evidence: `specs/frontend-routing/spec.md` delta defines the canonical runtime route chain and blocks treating `router/index.js*` or `phase4.routes.js` as live truth without an approved change.
- [x] 1.2 Add legacy frontend asset lifecycle classification requirements to `file-organization`
  - Evidence: `specs/file-organization/spec.md` delta requires `views/monitoring`, `views/composables`, duplicate page forks, and demo/archive/example trees to be classified before relocation or removal.
- [x] 1.3 Add phased structural closure and approval-gate requirements to `directory-governance`
  - Evidence: `specs/directory-governance/spec.md` delta defines E1-E6 batch sequencing and change-scoped retirement gates.

## 2. Execution Preparation

- [x] 2.1 Produce and approve the entry variant caller matrix for `main-*.js/ts` and `verify-mount.js`
  - Evidence: `entry-variant-caller-matrix.md` classifies `main-standard.ts` as the canonical runtime entry, `main.js` as a retained non-canonical entry still read by `verify-mount.js`, and separates active script/tooling callers from historical documentation references.
- [x] 2.2 Produce and approve the legacy router archive strategy for `router/index.js*` and `phase4.routes.js`
  - Evidence: `legacy-router-archive-strategy.md` assigns archive order and retirement gates to `index.js`, `index.js.clean`, `index.js.backup-phase2.3`, and `phase4.routes.js`, and explicitly blocks premature archive/delete actions before E3/E4 close.
- [x] 2.3 Produce and approve the monitoring retirement checklist aligning historical routes, Vitest guards, and Playwright coverage
  - Evidence: `monitoring-retirement-checklist.md` maps `views/monitoring/*` to historical-route and test-guard roles, enumerates the blocking Vitest/Playwright suites, and defines the retirement checklist that must clear before any directory-level cleanup.
- [x] 2.4 Produce and approve duplicate-page retirement checklists for `Phase4Dashboard` and `TechnicalAnalysis`
  - Evidence: `duplicate-page-retirement-checklist.md` distinguishes canonical, historical, independent-fork, and demo roles across `Phase4Dashboard` and `TechnicalAnalysis`, and records the page/composable/test gates that must close before any retirement action.
- [x] 2.5 Record the upstream dependency on approved documentation governance so frontend report/doc cleanup follows trunk-first rules instead of file-by-file historical rewrites
  - Evidence: `documentation-governance-alignment.md` records the approved `govern-documentation-truth-lifecycle` inputs, canonical truth trunks, `delete/archive > rewrite` bias, and the required execution order for future frontend documentation cleanup.

## 3. Post-Approval Implementation Waves

- [x] 3.1 Execute governance-alignment batches E1-E4 without deleting assets prematurely
  - Evidence: `entry-variant-caller-matrix.md`, `legacy-router-archive-strategy.md`, `monitoring-retirement-checklist.md`, and `duplicate-page-retirement-checklist.md` complete the approved E1-E4 governance/alignment batches while explicitly blocking premature structural cleanup.
- [x] 3.2 Execute case-conflict directory merge batch E5 with build / stylelint / route-smoke verification
  - Verification status: `e5-case-conflict-verification.md` now confirms that true case-conflict directories are already absent, E5-scoped stylelint passes, `vue-tsc --noEmit` passes, `npm run build` passes, and stable route smoke passes (`10/10` in Chromium).
- [x] 3.3 Execute naming / shim / backup closure batch E6 only after upstream structural convergence is complete
  - Verification status: `naming-shim-backup-closure-ledger.md` classifies E6 objects into `keep-canonical`, `keep-tooling`, `keep-compat`, `archive-candidate`, and `blocked-remove`, records migration gates for `main.js` / `verify-mount.js` / router backups / root shims, and verifies active compatibility surfaces with `node web/frontend/verify-mount.js` and `npx vitest run tests/unit/use-websocket-with-config.spec.ts`.
- [x] 3.4 Reconcile or supersede overlapping assumptions in existing active frontend restructure changes before runtime mutations begin
  - Evidence: `overlapping-change-reconciliation.md` records which assumptions in active frontend restructure changes are superseded by the 2026-04-07 repo-truth governance contract before any runtime mutations proceed.

## 4. Validation

- [x] 4.1 Run `openspec validate govern-phase3-phase4-frontend-closure --strict`
  - Evidence: `openspec validate govern-phase3-phase4-frontend-closure --strict` returned `Change 'govern-phase3-phase4-frontend-closure' is valid`.
