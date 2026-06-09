# CODEBASE-MAP Task Completion Validity Review

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: current validity review and next-task breakdown
Date: 2026-05-21
Branch: `wip/root-dirty-20260403`
HEAD checked: `f97f2eb57`
Primary steward source: `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`

## Review Basis

| Source | Role | Current reading |
|---|---|---|
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Steward index | Coordinates the CODEBASE-MAP remediation program; does not authorize source changes by itself |
| `openspec/changes/sequence-backend-architecture-unblocks/tasks.md` | Active OpenSpec task checklist | Runtime unblock tasks are currently checked and the runtime smoke now reproduces against clean current HEAD |
| `docs/reports/quality/backend-sequence-runtime-unblock-implementation-2026-05-20.md` | Runtime unblock evidence | Records `routes=548`, `paths=500`, `operation_ids=536`, `duplicate_operation_ids=0`, and health conflict suite passing |
| `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md` | Existing Core split OpenSpec line | Core Batch 2 remains blocked; this runtime unblock does not promote the Core split branch |

## Current Source-State Fact

The current checkout no longer has dirty source files in the data-lineage runtime unblock surface:

```text
git status --short -- web/backend/app/api/data_lineage.py web/backend/app/api/_data_lineage_responses.py
<no output>
```

The data-lineage import repairs are present in current HEAD. Runtime unblock
completion can therefore be treated as clean-current-HEAD evidence for the
import, collect-only, and minimal OpenAPI checks reproduced below.

## Fresh Runtime Checks

| Check | Result | Interpretation |
|---|---|---|
| `PYTHONPATH=web/backend python -c "from app.main import app; print('routes', len(app.routes))"` | Passed: `routes 548` | Runtime import chain is healthy in current HEAD |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov` | Passed: `112 tests collected` | Health route conflict suite is collectible in current HEAD |
| `app.openapi()` snapshot | Passed: `routes=548`, `paths=500`, `operation_ids=536`, `duplicate_operation_ids=0` | Minimal route/OpenAPI smoke is meaningful again in current HEAD |

## Validity Judgment

| Claimed or implied completion | Validity | Reason |
|---|---|---|
| CODEBASE-MAP steward hierarchy exists and can coordinate the branch tree | Valid | The steward document has explicit state legend, branch mapping, update protocol, next gates, and deferred-item boundaries |
| Runtime unblock implementation | Valid for current HEAD | Current HEAD passes app import, collect-only, and minimal OpenAPI smoke |
| `sequence-backend-architecture-unblocks` Task 2.x evidence | Valid for current HEAD | The evidence report and current smoke agree |
| Route/OpenAPI refresh can proceed | Valid as next governance/evidence task | Minimal smoke is now possible from clean current HEAD; broader route/OpenAPI governance refresh can run |
| Core split Batch 2 scheduling | Invalid to claim ready | The steward tree and Core split tasks still block Batch 2 behind Task 3.2 disposition, accepted `#83` evidence, and explicit runtime evidence adoption |
| PM2/backend runtime gate closure | Not proven by this review | This review only reproduced import, collect-only, and OpenAPI smoke; PM2 workflow was not rerun here |
| OpenSpec archive readiness | Not decided by this review | `sequence-backend-architecture-unblocks` tasks are recorded complete, but archive still needs explicit human/OpenSpec closure decision |

## Effective Current State

The task line is effective as a current-HEAD runtime unblock and governance
sequencing step. It is not yet effective as Core split continuation, PM2 runtime
closure, or OpenSpec archive-ready state.

The steward control rule remains correct: broad architecture work must stay
frozen unless runtime evidence is current and explicitly accepted. The fresh
adjustment is that the runtime import chain is now healthy in current HEAD, so
the immediate next task is downstream evidence/governance refresh, not source
adoption.

## Next Task Breakdown

### Task C1: Completion Evidence Adoption

Status: immediate review item.

Actions:

- Record that runtime unblock evidence now reproduces against current HEAD `f97f2eb57`.
- Update any steward rows that still describe Task 2.x as dirty-worktree-only.
- Keep the runtime unblock accepted only for import, collect-only, and minimal OpenAPI smoke; do not expand it to PM2 or broad Core split gates.
- If a follow-up commit is needed for documentation-only updates, stage only the approved report and governance files.

Acceptance:

- Runtime unblock evidence is marked as current-HEAD evidence.
- No unrelated dirty files are swept into documentation or governance commits.

### Task C2: Sequence Branch Review And Archive Decision

Status: blocked on human review.

Actions:

- Review `openspec/changes/sequence-backend-architecture-unblocks/tasks.md`; current checklist records Tasks 1.x through 8.7 complete.
- Review the runtime, schema-shim, route/OpenAPI/probe, service-seam, commit-readiness, and commit-blocked reports referenced by the steward tree.
- Decide whether the line is ready for OpenSpec archive, or whether the prior commit-blocked report requires another explicit path-limited commit/review round first.
- Do not archive if the user wants additional PM2/backend runtime evidence before closure.

Acceptance:

- Human review accepts the completed task evidence.
- Archive decision is explicit and separate from Core Batch 2.

### Task C3: PM2 / Backend Runtime Gate Decision

Status: optional but required if the team wants runtime closure beyond import/OpenAPI smoke.

Actions:

- Decide whether `app.main` import, collect-only, and OpenAPI smoke are sufficient for this governance line.
- If full runtime closure is required, run the approved PM2/backend startup workflow or named equivalent.
- Record backend URL, frontend URL if involved, health/readiness endpoints, and any PM2 state.

Acceptance:

- PM2 evidence is either recorded or explicitly deferred.
- The report does not reuse old PM2 evidence as current truth without a freshness label.

### Task C4: Route/OpenAPI Governance Follow-Up

Status: unblocked, but not automatically authorized for endpoint retirement.

Actions:

- Use Task 5.x route table, OpenAPI, and probe matrix artifacts as current evidence.
- Classify the known `GET /metrics` duplicate path/method as a control-plane taxonomy item before changing route exposure.
- Do not delete or hide endpoints without a separate endpoint governance approval.

Acceptance:

- Route/OpenAPI evidence remains tied to HEAD and generation timestamp.
- Endpoint-retirement decisions stay outside this validity review.

### Task C5: Core Split Continuation Decision

Status: blocked.

Actions:

- Keep `split-backend-core-modules-with-compatibility-wrappers` Batch 2 frozen.
- Resolve Task 3.2 disposition explicitly.
- Decide whether current runtime evidence from `sequence-backend-architecture-unblocks` is accepted as evidence for this Core split branch.
- Do not schedule Core helper Batch 2 until runtime and evidence gates are accepted.

Acceptance:

- Batch 2 has an accepted gate disposition.
- OpenSpec tasks distinguish commit-scoped evidence from current-HEAD evidence.

### Task C6: Service Seam Proposal Path

Status: candidate only.

Actions:

- Use the Task 6.x service seam proposal-path report as planning input.
- Create a separate OpenSpec proposal only after human approval.
- Do not start service lifecycle implementation from this report.

Acceptance:

- Future service seam work has its own approved proposal and evidence boundary.

## Explicit Non-Goals

- Do not edit backend source from this validity review.
- Do not publish issue15 from this validity review.
- Do not archive `sequence-backend-architecture-unblocks`.
- Do not promote Core split Batch 2.
- Do not delete schema compatibility paths.
- Do not treat runtime import success as PM2 closure, Core Batch 2 authorization, or OpenSpec archive readiness.

## Verification Commands Used

```bash
git rev-parse --short=9 HEAD
git status --short -- web/backend/app/api/data_lineage.py web/backend/app/api/_data_lineage_responses.py
PYTHONPATH=web/backend python -c "from app.main import app; print('routes', len(app.routes))"
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov
PYTHONPATH=web/backend python - <<'PY'
from app.main import app
schema = app.openapi()
paths = schema.get("paths", {})
operation_ids = []
for path_item in paths.values():
    if isinstance(path_item, dict):
        for operation in path_item.values():
            if isinstance(operation, dict) and operation.get("operationId"):
                operation_ids.append(operation["operationId"])
duplicates = len(operation_ids) - len(set(operation_ids))
print(f"routes={len(app.routes)} paths={len(paths)} operation_ids={len(operation_ids)} duplicate_operation_ids={duplicates}")
PY
```
