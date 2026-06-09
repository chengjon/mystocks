# Backend Core Split Other-Line Next Work And Boundary

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Recorded at: `2026-05-19`

## Purpose

This document gives the other implementation line a concrete follow-up direction
after the first low-risk Core helper split, while keeping this publication /
triage line clean.

It exists to prevent three failure modes:

- mixing GitHub issue publication work with backend implementation commits;
- fast-forwarding or merging remote work into a dirty checkout with untracked
  governance artifacts;
- treating unresolved PM2 / health / OpenAPI blockers as part of the validation
  messages split when they appear to belong to the contract/OpenAPI startup
  lane.

## Current Cross-Line Facts

Reported completed implementation commit:

```text
commit: caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe
title: refactor(core): split validation messages wrapper
```

Local checkout state when this guidance was written:

```text
current branch: wip/root-dirty-20260403
current HEAD: 02ac506cec8ef926e09090208cb584be65621749
remote wip/root-dirty-20260403: e7c0cbdd1724f949f555e409dfe67efecf008be6
local branch containing caa5a6bd6: contract-startup-unblock
```

Important interpretation:

- `caa5a6bd6` is visible locally as a Git object.
- `caa5a6bd6` is in the newer remote branch history.
- the current checkout `HEAD` is not yet fast-forwarded to that remote state.
- this publication line has untracked governance artifacts that must not be
  overwritten or mixed into backend implementation commits.

## Ownership Boundary

This publication / governance line owns:

- issue `#80` approval record;
- issue `#83` publication and triage status;
- evidence-routing decisions for issue `#83`;
- issue15 draft readiness and publication boundary;
- local governance reports under `docs/reports/quality/`.

The other implementation line owns:

- the Core helper split implementation commit;
- `web/backend/app/core/validation/messages.py`;
- `web/backend/app/core/validation_messages.py`;
- `web/backend/app/core/validation/__init__.py`;
- `tests/unit/core/test_validation_messages_compat.py`;
- F-line implementation evidence for the validation messages split;
- follow-up verification needed to close OpenSpec tasks 4.3 / 4.4 / 4.5.

Shared information, not shared ownership:

- commit `caa5a6bd6`;
- `docs/reports/quality/backend-core-split-helper-batch1-2026-05-19.md`;
- OpenSpec change `split-backend-core-modules-with-compatibility-wrappers`;
- GitHub issue `#83` evidence discussion.

## Git Hygiene Rules

Do not run `git pull`, `git merge`, `git rebase`, or `git reset` in the current
checkout until this publication line's untracked governance artifacts are
preserved.

Before the other line continues, choose one of these safe paths:

| Path | When to use | Required action |
|---|---|---|
| Separate worktree | preferred for implementation continuation | create or reuse a clean worktree from `origin/wip/root-dirty-20260403` or the implementation branch |
| Commit governance docs first | if this checkout must be updated | stage only the publication-line docs and commit them separately before fast-forwarding |
| Stash only with manifest | if a commit is not desired yet | record an exact file manifest, stash only the intended docs, then verify restoration |

Do not mix these into one commit:

- issue publication records;
- GitHub triage comments;
- backend Core implementation;
- PM2 / contract startup fixes;
- generated evidence artifacts.

Minimum status checks before any branch movement:

```bash
git status --short
git log -1 --oneline --decorate
git ls-remote origin refs/heads/wip/root-dirty-20260403
```

If the status output contains untracked publication-line docs, stop and preserve
them before updating the checkout.

## Recommended Other-Line Work Plan

### 1. Preserve The Implementation Baseline

Record the exact implementation baseline before further work:

```text
caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe
```

The other line should keep the validation messages split as one small completed
batch. Do not expand the same commit or follow-up commit into unrelated contract,
OpenAPI, PM2, or route changes.

Expected stable facts:

- canonical path: `app.core.validation.messages`;
- compatibility wrapper: `app.core.validation_messages`;
- package re-export: `app.core.validation`;
- wrapper retirement is deferred;
- no route registration, OpenAPI contract, database, cache, security, socketio,
  or logger runtime ownership was intentionally changed by this helper split.

### 2. Reconcile F-Line Evidence Into Issue 83

Issue `#83` should absorb the completed batch as evidence, not as a new
implementation request.

Evidence to attach or cite after approval:

```text
commit: caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe
report: docs/reports/quality/backend-core-split-helper-batch1-2026-05-19.md
tests: tests/unit/core/test_validation_messages_compat.py
```

Issue `#83` must remain `needs-triage` until its triage gate is rerun against
the updated state. Do not move it to `ready-for-agent` only because one F-line
implementation batch landed elsewhere.

### 3. Keep OpenSpec Tasks Honest

For `split-backend-core-modules-with-compatibility-wrappers`, keep task status
aligned with actual verification evidence.

Current expected interpretation:

| Task | Status direction | Notes |
|---|---|---|
| 3.1 | can remain done | first low-risk helper split completed |
| 3.2 | review before marking done | package re-export exists for this batch, but task wording may imply broader same-name package strategy |
| 3.3 | can remain done for this batch | old-path wrapper exists |
| 4.1 | done if import smoke evidence is retained | include old and new paths |
| 4.2 | done if targeted tests are retained | `test_validation_messages_compat.py` passed |
| 4.3 | keep open | PM2 backend startup blocked |
| 4.4 | keep open | health smoke blocked by startup failure |
| 4.5 | keep open | route/OpenAPI drift cannot be closed until runtime/generation path is unblocked |

Do not mark 4.3 / 4.4 / 4.5 done using import smoke or unit tests alone.

### 4. Isolate The Contract Startup Blocker

Reported blocker:

```text
ImportError: cannot import name 'ContractDriftIncidentListResponse' from 'app.api.contract.schemas'
```

Treat this as a separate contract/OpenAPI startup blocker unless direct evidence
shows the validation messages split caused it.

The other line should:

1. Reproduce the import error from a clean checkout that includes the newer
   remote branch state.
2. Identify whether `ContractDriftIncidentListResponse` was renamed, deleted,
   moved, or never exported.
3. Decide whether the fix belongs in:
   - `app.api.contract.schemas`;
   - the importing contract route/module;
   - generated schema export code;
   - a contract/OpenAPI stabilization proposal.
4. Fix it only under the correct ownership lane.
5. After the fix, rerun PM2 startup, health smoke, and route/OpenAPI drift
   checks.

Do not bundle the contract import fix into "Core helper split batch 1" unless
direct causality is proven.

### 5. Close Runtime Gates Only After Runtime Evidence

After the contract startup blocker is resolved, the other line should run the
runtime gates that were left open:

```bash
./scripts/run_pm2_integration_workflow.sh
```

or a named equivalent approved for the implementation issue.

Then verify health endpoints:

```text
/api/health/services
/health/ready
/api/health/ready
```

Then confirm route/OpenAPI drift using the repo's current route/OpenAPI evidence
workflow and record:

- command used;
- branch and HEAD;
- generated artifact paths;
- route count deltas;
- OpenAPI path deltas;
- known unrelated historical failures, if any.

### 6. Do Not Start The Next Core Split Yet

Do not start a second Core split batch until:

- issue `#83` has absorbed the first-batch evidence;
- task 4.3 / 4.4 / 4.5 status is either closed with evidence or explicitly
  documented as blocked by a separate lane;
- issue15 draft is revised to account for the completed validation messages
  split;
- wrapper retirement criteria remain explicit and unmet.

The next batch should be selected only after current evidence is reconciled.

## Issue 15 Boundary

Issue15 remains unpublished.

Current draft still contains:

```text
BLOCKED_BY_TODO: shared evidence package.
```

Keep that placeholder until issue `#83` has a completed or explicitly accepted
evidence status.

Before issue15 publication, revise its F-line language:

- remove or reframe "select the first low-risk Core split batch";
- cite `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe`;
- cite `docs/reports/quality/backend-core-split-helper-batch1-2026-05-19.md`
  if present in the target checkout;
- ask the human reviewer to decide the next Core split batch or wrapper
  retirement criteria instead of reopening the already-completed batch1
  decision.

## Stop Conditions

Stop and ask for review if any of the following happens:

- current checkout has untracked governance artifacts and a branch update is
  needed;
- `caa5a6bd6` is not reachable from the branch being used for continuation;
- the PM2 blocker appears to require contract/OpenAPI code changes;
- a proposed fix touches both Core helper split files and contract route/schema
  files in the same commit;
- issue `#83` is about to be moved to `ready-for-agent`;
- issue15 is about to be published before its draft is updated for the completed
  validation messages split.

## Current Recommendation

Continue the other implementation line in a clean worktree or clean branch state.

Use this line only to:

- reference the completed F evidence;
- keep issue `#83` in `needs-triage`;
- revise issue15 before publication;
- avoid mixing publication artifacts with backend implementation commits.
