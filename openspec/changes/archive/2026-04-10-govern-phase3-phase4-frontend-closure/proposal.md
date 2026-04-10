# Change: Govern Phase 3/4 Frontend Closure Execution

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why
Current frontend-structure work is blocked by repo-truth drift. The 2026-04-07 audits established that several assets previously assumed to be removable are actually historical route targets, test-guarded artifacts, or duplicate-candidate forks. Without an approved phased closure contract, any direct implementation would risk deleting or relocating assets before their route truth, test guards, and retirement conditions are aligned.

## What Changes
- Define an evidence-based frontend route-truth contract anchored on `index.html -> main-standard.ts -> router/index.ts`.
- Require historical router files to be classified before they can be archived or removed.
- Require lifecycle classification for legacy frontend assets such as `views/monitoring/`, `views/composables/`, duplicate page forks, demo assets, and archive/example trees.
- Establish an execution matrix for Phase 3 / Phase 4 closure work that sequences evidence gathering, retirement-condition alignment, and structural mutations in separate batches.
- Block direct structural cleanup until approval gates, caller inventories, and test-guard alignment are satisfied.

## Impact
- Affected specs: `frontend-routing`, `file-organization`, `directory-governance`
- Affected docs/artifacts: `docs/reports/2026-04-07-*.md`, `.planning/ROADMAP.md`, future Phase 3 / 4 execution ledgers
- Affected code (future batches, not this proposal): `web/frontend/src/router/*`, `web/frontend/src/views/*`, related Vitest / Playwright suites
- Risk: Medium. The proposal is governance-first, but it directly constrains how several active frontend refactor changes may proceed.
