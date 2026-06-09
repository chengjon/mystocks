# Codebase Map Execution Plan Positioning And Rollout

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: governance positioning note for the `2026-05-19-codebase-map-openspec-execution-plan`.

## 1. Positioning

The `2026-05-19-codebase-map-openspec-execution-plan` is a **pre-implementation governance and decision-closure plan**, not a code implementation plan.

Its job is to:

- inventory the current state
- identify blockers
- define scope
- align evidence
- freeze decisions
- validate preconditions

Its output is documentation and evidence, not source edits.

## 2. Why This Is Not a Contradiction

The apparent mismatch is only superficial.

If the real goal is architectural change, then the compliant sequence is:

1. establish rules
2. lock the evidence
3. define what may move and what must not move
4. only then allow source changes

That is standard architecture governance, not wasted motion.

## 3. Current Hard Constraints

### Runtime gate

The current checkout still has a runtime import blocker:

- `web/backend/app/api/data_lineage.py` still uses a bare `_data_lineage_responses` import
- `app.main` import fails
- `test_health_route_conflicts.py --collect-only -q --no-cov` fails on the same chain

That means runtime route/OpenAPI evidence is not yet trustworthy enough for broad architecture claims.

### Batch gate

Core Batch 2 remains blocked by the OpenSpec reconciliation path:

- Task `3.2` is still open
- #83 evidence-package work has not been accepted as a Batch 2 gate opener
- issue15 remains unpublished

### Freshness gate

The local branch and the remote runtime-evidence commit are not the same thing.

Current local HEAD does not contain `bbb399071`, so any failure in the current checkout must be treated as stale-checkout evidence first, not as proof that the implementation worktree evidence was false.

## 4. What The Document Work Is For

This governance layer is useful because it does real work:

- records singletons, route ownership, schema dual directories, and compatibility shims
- documents what must remain compatible and what can later be retired
- captures control-plane taxonomy, OpenAPI exposure, and runtime-only routes
- identifies which changes need a separate proposal or approval gate
- turns hidden operational risk into visible evidence

That is not a substitute for coding. It is the prerequisite that keeps later coding from becoming guesswork.

## 5. What Remains Frozen For Now

The following architecture changes should stay frozen until the prerequisite gates are opened:

- backend core module physical split
- singleton lifecycle migration to DI
- API flat/package restructuring beyond evidence capture
- full health endpoint closure work
- unified logging refactor
- domain/infrastructure dependency rework

These items are not cancelled. They are deferred until the evidence and approval gates are satisfied.

## 6. Recommended Rollout Sequence

### Phase 1: Governance closure

Already mostly complete.

Keep the work limited to:

- report generation
- evidence alignment
- blocker mapping
- OpenSpec/task reconciliation
- clean governance commit hygiene

### Phase 2: Minimal runtime unblock

Next action should be a very small implementation lane whose only purpose is to restore trusted runtime evidence collection.

That lane should be limited to the `data_lineage.py` bare import blocker and nothing broader.

It should not:

- change architecture strategy
- advance Batch 2
- move issue15
- expand into Core refactoring

### Phase 3: Runtime evidence refresh

Once import smoke works again, refresh:

- route table evidence
- OpenAPI evidence
- duplicate `operationId` warnings
- runtime-only compatibility routes
- health/status probe consumer matrix

### Phase 4: Governance reconciliation for #83 / issue15 / Task 3.2

This is where Batch 2 becomes legitimately schedulable or stays blocked with explicit reasons.

### Phase 5: Real architecture implementation

Only after the above gates are open should the project move into:

- helper batch expansion
- adapter lifecycle DI
- service lifecycle DI
- API flat/package closure
- schema dual-directory closure
- CSRF composition-root cleanup

## 7. Concrete Next Step

The most useful next step is a separate, tiny runtime-unblock lane for the `data_lineage.py` import issue.

That lane should be treated as:

- environment unblocking
- not architecture redesign
- not Batch 2
- not #83 evidence-package work

Once that import chain is repaired, the project can re-run the runtime evidence and decide the next real architecture batch with clean facts.

