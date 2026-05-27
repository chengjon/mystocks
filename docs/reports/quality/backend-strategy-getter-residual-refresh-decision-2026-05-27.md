# Backend Strategy Getter Residual Refresh Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.181
- State: ready for review
- Date: 2026-05-27
- Base HEAD: `ba929aee2e7fc0de0278f80f30caa185fafa6b5c`
- Parent closeout: G2.180, PR `#333`, merge commit `ba929aee2e7fc0de0278f80f30caa185fafa6b5c`
- Scope: governance decision package only

Boundary note: this report does not authorize backend source edits, frontend
source edits, tests, generated client updates, docs/API edits, OpenSpec proposal
creation, issue label changes, PM2 commands, runtime rollout, compatibility
deletion, adapter-local cleanup implementation, backtest task helper
implementation, route behavior changes, or OpenAPI exposure changes.

## Purpose

G2.180 closed the approved Strategy adapter provider implementation after PR
`#331` and recorded that `get_strategy_service` residuals still exist. This
package re-checks those residuals at the post-closeout base HEAD and decides
which residual class should become the next governance target.

This is a decision package, not an implementation package. It keeps the
Strategy getter residual surfaces separated so future work cannot treat one
residual count as broad permission to edit all Strategy-related files.

## Residual Scan

At HEAD `ba929aee2e7fc0de0278f80f30caa185fafa6b5c`, production `.py`
`get_strategy_service` hits under `web/backend/app` remain `19`:

| File | Hits | Lines | Decision |
|---|---:|---|---|
| `web/backend/app/services/adapters/strategy_adapter.py` | 10 | `40`, `47`, `49`, `106`, `120`, `136`, `153`, `183`, `332`, `344` | Canonical adapter-local residual. Keep under future adapter-local lifecycle cleanup consideration; do not start source edits from this package. |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 | `20`, `33`, `34`, `388`, `454`, `499` | Route provider fallback residual. Select as the recommended next governance target. |
| `web/backend/app/tasks/backtest_tasks.py` | 2 | `19`, `21` | Backtest task helper residual. Do not reopen from this package unless later current-HEAD evidence contradicts the closed resolver-seam handling. |
| `web/backend/app/services/strategy_service.py` | 1 | `455` | Public getter definition. Retain as public compatibility entrypoint; not a deletion, rename, or privatization candidate here. |

## Decision

Select `web/backend/app/api/strategy_management/_strategy_execution_router.py`
as the next governance target, but only as a separate route/provider fallback
decision package. The recommended next work item is:

- G2.182: Strategy route provider fallback residual decision package

G2.182 should decide the route/provider fallback boundary before any source
authorization. It should not be treated as automatic permission to edit the
route file.

## Deferred Residuals

The remaining residual classes stay explicitly deferred:

- `strategy_adapter.py`: future adapter-local lifecycle cleanup candidate only.
- `backtest_tasks.py`: no-op unless a fresh contradiction appears.
- `strategy_service.py`: retained public getter definition.

## Steward Updates

This package updates the split steward tree only:

- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`
- `.planning/codebase/generated/strategy-getter-residual-refresh-decision-2026-05-27.json`

## Next Gate

Review G2.181. If accepted, prepare G2.182 as a route/provider fallback
decision package before any further Strategy getter source edits.
