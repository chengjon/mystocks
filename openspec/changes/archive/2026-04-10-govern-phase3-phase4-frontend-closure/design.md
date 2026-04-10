## Context

> **专题方案说明**:
> 本文件用于描述 `govern-phase3-phase4-frontend-closure` 的设计约束、分批策略与验证门禁。
> 它服务于当前 OpenSpec 变更的方案管理，不自动等同于当前仓库实现、共享治理规则或已完成结构收口的唯一事实来源。
> 执行时仍需同时核对 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、当前代码与实际验证结果。

The current repository contains several active frontend restructure proposals, but the 2026-04-07 repo-truth audits showed that multiple assumptions are unsafe:

- the runtime route truth is `web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts`
- `router/index.js*` files are historical assets, not live runtime truth
- `phase4.routes.js` is a stale route asset, not an active route aggregator
- `views/monitoring/` is not dead code; it is a combination of historical route targets and test-guarded assets
- `views/composables/` is still dominated by root-level legacy page support
- `Phase4Dashboard` and `TechnicalAnalysis` are not simple duplicates; they are mixed historical/demo/fork/canonical sets

This means the project needs a governance contract before any structural cleanup resumes.

## Goals

- Encode evidence-based route truth in OpenSpec so future batches do not rely on stale assumptions
- Encode lifecycle classification requirements for legacy frontend assets before relocation or removal
- Define a phased closure matrix that separates evidence gathering, retirement alignment, and structural mutation
- Constrain future implementation so route assets, test-guarded assets, and duplicate forks are not deleted prematurely

## Non-Goals

- This change does not itself delete, move, or rename runtime files
- This change does not resolve case-conflict directories yet
- This change does not finalize retirement of `views/monitoring`, `Phase4Dashboard`, or `TechnicalAnalysis`
- This change does not supersede every active frontend restructure proposal automatically; it only establishes the approved gating contract they must satisfy

## Key Decisions

### 1. Evidence-Based Route Truth Wins

The canonical route truth is defined by the actual runtime chain:

```text
index.html -> main-standard.ts -> router/index.ts
```

Historical router files may still matter for migration evidence, but they are not current runtime truth.

### 2. Historical Router Files Need Classification, Not Immediate Deletion

`router/index.js`, `router/index.js.clean`, `router/index.js.backup-phase2.3`, and `phase4.routes.js`
must be classified as historical backup, broken working copy, stale route asset, or similar lifecycle roles before any archive/removal action.

### 3. Legacy Frontend Assets Need Functional-Tree Labels

Before relocation or deletion, the system must classify page and composable assets into roles such as:

- canonical runtime truth
- historical route target
- historical backup
- stale route asset
- test-guarded artifact
- legacy page support
- duplicate-candidate
- demo/example asset

This avoids collapsing unlike assets into a single "deprecated" bucket.

### 4. Closure Must Be Executed In Ordered Batches

The approved execution order is:

1. E1 entry variant caller matrix
2. E2 legacy router archive strategy
3. E3 monitoring retirement alignment
4. E4 duplicate page retirement alignment
5. E5 case-conflict directory merge
6. E6 naming / shim / backup closure

Only E5-E6 are allowed to perform broad structural mutations, and only after E1-E4 finish.

### 5. Approval And Verification Gates Stay Explicit

Because this work changes route/layout/file structure semantics, OpenSpec approval and `architecture/STANDARDS.md`
gates remain binding. Structural cleanup requires explicit approval and relevant verification commands for the batch.

### 6. Documentation Governance Stays Upstream And Separate

The approved change `govern-documentation-truth-lifecycle` now acts as an upstream governance input
for this frontend closure work.

This means:

- frontend repo-truth reports and execution ledgers are evidence/report artifacts, not canonical trunk docs
- documentation cleanup for stale frontend restructure notes, legacy route explanations, or historical
  reports must follow the documentation-governance trunk-first workflow
- the repository should prefer `delete/archive > rewrite` for stale frontend documentation once
  canonical trunk mappings and decision registers exist
- this frontend change may reference the documentation-governance execution order, but it does not
  absorb or replace that change's implementation tasks

## Risks And Mitigations

### Risk: Existing active changes already assume direct relocation/removal

Mitigation:

- This change defines the gating contract those changes must satisfy before runtime mutations
- Follow-up work must reconcile or supersede unsafe assumptions rather than executing them blindly

### Risk: Historical docs still cite `router/index.js` as active truth

Mitigation:

- E2 explicitly includes doc-truth reconciliation before archive/removal

### Risk: Test-guarded assets look unused from the main router

Mitigation:

- The new spec requires route, test, and functional-tree alignment before deletion

## Rollout Strategy

1. Approve this governance change
2. Use the existing 2026-04-07 repo-truth reports as E1-E4 source artifacts
3. Treat `govern-documentation-truth-lifecycle` as the upstream path for any follow-up historical
   doc cleanup, taxonomy/audit work, or delete/archive decisions
4. Create or update follow-on execution changes only for concrete runtime mutations
5. Execute E5-E6 only after approval and after the retirement-condition matrix is complete
