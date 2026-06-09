# Backend Codebase Map / OpenSpec Line Handoff

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: handoff for the codebase-map / backend OpenSpec governance line.

Generated at: 2026-05-21 Asia/Shanghai

Current local snapshot checked for this handoff:

| Field | Value |
|---|---|
| Branch | `wip/root-dirty-20260403` |
| Local HEAD | `80b8389ed Record miniQMT forward receive result` |
| Remote branch | `origin/wip/root-dirty-20260403` at `ca215767b4bbc04b237a408a409ac63cb799bf80` |
| Branch relation | ahead 9, behind 57 |
| Worktree | dirty; many unrelated files outside this line |
| Staged area | empty at handoff check |
| This-line target files | clean at handoff check |

## Purpose

This line converted the earlier backend audit / codebase-map concerns into a
bounded OpenSpec-governed execution path. It deliberately separated:

- GitHub issue publication and triage;
- current-head evidence capture;
- implementation-lane runtime unblock work;
- downstream human decisions;
- future proposal or implementation work that still requires explicit approval.

The current handoff target is not to continue broad refactoring. It is to keep
the evidence chain accurate, route the next decisions through the published
GitHub / OpenSpec gates, and avoid mixing unrelated dirty-worktree changes into
this line.

## Current Issue State

Verified with `gh issue view` on 2026-05-21:

| Issue | State | Labels | Meaning |
|---|---|---|---|
| `#80` `[Backend OpenSpec] Approve orchestration and C/E/F/G proposal scope` | `OPEN` | `enhancement`, `ready-for-human` | Original approval / orchestration issue remains open as governance context. |
| `#83` `[Backend OpenSpec] Build shared C/E/F evidence package` | `CLOSED` | `enhancement`, `evidence-accepted`, `ready-for-agent`, `ready-for-downstream` | Shared C/E/F evidence package accepted; no longer a blocker for downstream governance. |
| `#92` `[Backend OpenSpec] Decide post-approval implementation plan` | `OPEN` | `enhancement`, `ready-for-downstream`, `ready-for-human` | Current downstream human decision issue. Treat this as the live successor to the old local issue15 draft. |

The old local draft still exists at:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/15-decide-post-approval-plan.md
```

It still contains:

```text
BLOCKED_BY_TODO: shared evidence package.
```

Do not treat that old draft as the current live issue state without first
reconciling it against GitHub issue `#92`.

## Completed Work

### Publication And Governance Package

Completed and recorded:

- compressed the earlier backend OpenSpec publication shape into the approval /
  shared-evidence / downstream-decision flow;
- published and triaged issue `#83`;
- accepted `#83` shared C/E/F evidence for downstream governance;
- kept backend implementation locked unless a separate approved implementation
  lane exists;
- preserved the distinction between issue publication, evidence capture, and
  implementation.

Primary records:

```text
docs/reports/quality/backend-openspec-line-summary-and-next-plan-2026-05-19.md
docs/reports/quality/backend-openspec-issue83-ready-for-agent-status-2026-05-19.md
docs/reports/quality/backend-openspec-issue83-runtime-triage-2026-05-19.md
docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md
.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md
```

### Runtime Blocker Reconciliation

The earlier `ContractDriftIncidentListResponse` blocker was superseded. The
next blocker was the bare `_data_lineage_responses` import. That blocker was
routed out of `#83` evidence-only work and later fixed in the implementation
lane.

Current task-tree evidence says:

- `backend-sequence-runtime-unblock-implementation-2026-05-20.md` records
  `app.main` importing with `routes=548`;
- `test_health_route_conflicts.py` reports `112 passed`;
- OpenAPI paths are `500`;
- duplicate operationIds are `0`.

Relevant commits include:

```text
f97f2eb57 fix(api): repair data lineage companion imports
86849805e docs(codebase): attach route openapi runtime diff
93b40f80a docs(plan): record openspec execution progress
```

### Static Evidence And Decision Records

The following evidence / decision records were created or refreshed and are
tracked as stale-aware artifacts:

```text
docs/reports/quality/backend-schema-dual-directory-closure-2026-05-19.md
docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md
docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md
docs/reports/quality/backend-csrf-composition-root-decision-2026-05-19.md
docs/reports/quality/backend-error-contract-completion-verification-2026-05-19.md
docs/reports/quality/backend-external-evidence-alignment-2026-05-19.md
docs/reports/quality/codebase-map-freshness-2026-05-19.md
```

Notable current-head facts captured in these records:

- schema dual directory: `web/backend/app/schemas/` is the canonical direction;
- static `from app.schema` references were tracked and later schema-shim closure
  evidence reports zero legacy consumers;
- API flat/package records remain static-only until route/OpenAPI evidence is
  accepted as current;
- service lifecycle matrix found no implementation-ready clean `#79` stateless
  pilot from that pass;
- CSRF canonical ownership stays with `web/backend/app/main.py`, while
  `app_factory.py` remains compatibility/test oriented;
- P3-C5 error-contract fixed-field scan over `web/backend/app/api` was all zero;
- miniQMT evidence was recorded as external, non-backend-authorizing evidence.

### Codebase Map / Execution Plan Artifacts

The main codebase-map review was updated to include OpenSpec publication
alignment, evidence-index rows, and freshness constraints:

```text
.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md
docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md
.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md
```

The task tree is the best compact map for the next session. It currently
separates shallow runtime/schema/route closure from deeper service-seam proposal
work.

### Commits To Know

Recent commits relevant to this line:

```text
93b40f80a docs(plan): record openspec execution progress
9dafa1646 docs(codebase): refresh openspec execution plan status
e74bf92f1 docs(governance): record codebase map validity review
86849805e docs(codebase): attach route openapi runtime diff
f97f2eb57 fix(api): repair data lineage companion imports
09636d8ef chore: clean up dot-directory tracking and gitignore governance
93c6f6a05 chore(docs): record sequence backend unblocks
7b097fffd Record miniQMT authoritative-ready evidence alignment
6530c88f3 docs(codebase): record openspec execution evidence
31660d10d docs(plan): tighten codebase map openspec execution plan
19ca5521a docs(codebase): incorporate review corrections
```

## Current Gates And Boundaries

### Must Not Do

- Do not start broad backend refactors from the codebase map.
- Do not treat historical issue15 draft text as the live downstream issue.
- Do not start Core helper Batch 2 just because `#83` is accepted.
- Do not retire wrappers, endpoints, or schema shims without a current-head
  decision record and tests.
- Do not pull, merge, or rebase the dirty root worktree casually; there are many
  unrelated changes.
- Do not use `#83` to authorize implementation; `#83` is closed and accepted as
  evidence.

### Live Constraints

- The root branch is dirty and diverged from remote. Use a clean worktree for
  implementation if possible.
- GitHub issue state is current truth for `#80`, `#83`, and `#92`; recheck before
  acting.
- OpenSpec state must be validated with `openspec validate <change-id> --strict`
  before sharing or closing related branches.
- GitNexus staged scope checks are required before committing code or structured
  refactors.
- Markdown governance and `git diff --check` are required for report batches.

## Next Work Plan

### 1. Start From Issue `#92`

Treat `#92` as the live downstream decision issue.

Recommended next action:

- review `#92` body and comments;
- decide whether its downstream split is ready to proceed;
- update or retire the old local issue15 draft only as a historical artifact,
  not as the live decision source;
- keep `#92` in `ready-for-human` until the human decision is explicit.

### 2. Reconcile Core Split OpenSpec Task State

Current `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md`
still has important unchecked items:

```text
3.2 Introduce same-name packages with __init__.py re-exports.
4.3 Run PM2 backend startup smoke.
4.4 Run health/readiness smoke.
4.5 Confirm no unintended route or OpenAPI drift.
```

The task file also notes that commit-scoped evidence exists and later runtime
unblock evidence shows current-head runtime smoke passing. The next owner should
not blindly tick these boxes. Instead:

1. Re-read `backend-core-split-governance-reconciliation-2026-05-19.md`.
2. Re-read `backend-sequence-runtime-unblock-implementation-2026-05-20.md`.
3. Re-read `backend-route-openapi-probe-refresh-2026-05-20.md`.
4. Decide whether that evidence is accepted as the active task state for the
   Core split OpenSpec branch.
5. Only then update `tasks.md`, with the decision rationale.

### 3. Continue Route / OpenAPI Governance

The route/OpenAPI/probe refresh has current evidence:

```text
routes=548
OpenAPI paths=500
duplicate operationIds=0
probe hit files=188
```

Known next gate:

- classify the duplicate runtime path/method for `GET /metrics` under
  control-plane endpoint governance;
- do not retire, expose, or hide endpoints until that classification is recorded.

Primary artifact:

```text
docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md
```

### 4. Continue Schema Shim Closure Carefully

Task-tree evidence says schema shim closure reached zero legacy `app.schema`
consumers and canonical `app.schemas` exports are available.

Next owner should:

- verify current HEAD still has zero legacy `app.schema` active consumers;
- keep compatibility tests visible;
- decide shim retirement separately from consumer migration;
- avoid deleting compatibility shims in the same batch as route/OpenAPI work.

Primary artifact:

```text
docs/reports/quality/backend-schema-shim-closure-implementation-2026-05-20.md
```

### 5. Keep Service Seam Work Proposal-Only

The singleton/service lifecycle line is not implementation-ready.

Current evidence says:

- no clean stateless `#79` pilot was selected from the inventory pass;
- service seam work needs interface and test-double strategy, not another blind
  singleton cleanup;
- `realtime_mtm` and `adapter_loader` need separate gates.

Next owner should prepare a proposal or decision pack only after human approval.

Primary artifacts:

```text
docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md
docs/reports/quality/backend-service-seam-proposal-path-2026-05-20.md
```

### 6. Maintain Freshness Metadata

For every new evidence artifact, record:

- `generated_at`;
- `git_head`;
- `current_head_checked_at_review`;
- `stale_if_head_mismatch`;
- whether evidence is current-head, dirty-worktree, clean-worktree, or
  commit-scoped.

Update:

```text
docs/reports/quality/codebase-map-freshness-2026-05-19.md
.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md
.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md
```

## Suggested Verification Commands

Use scoped checks; avoid global gates unless the next task explicitly requires
them.

```bash
git diff --check -- <edited-files>
python scripts/compliance/markdown_governance_gate.py --root-dir . --format json <edited-md-files>
openspec validate sequence-backend-architecture-unblocks --strict
openspec validate split-backend-core-modules-with-compatibility-wrappers --strict
```

For current GitHub state:

```bash
gh issue view 80 --json number,state,labels,title,url,comments
gh issue view 83 --json number,state,labels,title,url,comments
gh issue view 92 --json number,state,labels,title,url,comments
```

Before any code commit:

```text
Stage only the intended files, then run GitNexus detect_changes(scope="staged").
```

## Recommended Skills For Next Session

- `superpowers:executing-plans` for continuing from the existing execution plan.
- `superpowers:verification-before-completion` before claiming any gate closed.
- `triage` if editing or transitioning GitHub issues.
- `improve-codebase-architecture` only for proposal/decision shaping, not
  implementation by default.

## Handoff Summary

The immediate next session should start with GitHub issue `#92` and the task tree
instead of the older issue15 draft. The line is ready for downstream human
decision work and evidence reconciliation, not broad implementation. The most
important technical follow-up is to decide whether the runtime unblock and
route/OpenAPI evidence should close the corresponding Core split OpenSpec tasks.
After that, route governance, schema shim retirement, and service seam proposal
work can proceed as separate, explicitly approved branches.
