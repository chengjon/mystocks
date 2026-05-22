# Backend OpenSpec Issue 92 Archive Execution

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

Date: 2026-05-22
Status: archive-executed-prepared-for-pr-review
Branch: `issue92-openspec-archive`
Base HEAD: `fdedf35c22eecc79199847511fcb4434d0a398d4`
Parent issue: `#92`

## Purpose

This report records the separate OpenSpec archive PR for the completed issue
`#92` downstream OpenSpec changes. The final closeout waiver and
archive-readiness review were merged before this archive work began.

## Archive Preconditions

| Gate | Evidence |
|---|---|
| Final closeout waiver | PR `#132`, `backend-openspec-issue92-downstream-final-closeout-2026-05-22-review-waiver.md` |
| Archive readiness review | PR `#131`, `backend-openspec-issue92-archive-readiness-2026-05-22-review.md` |
| Archive readiness packet | PR `#130`, `backend-openspec-issue92-archive-readiness-2026-05-22.md` |
| Parent issue boundary | Issue `#92` remains `OPEN` with no `ready-for-agent` label |

## Archived Changes

| Change | Archive directory | Spec updated |
|---|---|---|
| `inject-technical-pattern-detection-service-di` | `openspec/changes/archive/2026-05-22-inject-technical-pattern-detection-service-di/` | `openspec/specs/architecture-governance/spec.md` |
| `refresh-backend-route-openapi-governance` | `openspec/changes/archive/2026-05-22-refresh-backend-route-openapi-governance/` | `openspec/specs/architecture-governance/spec.md` |
| `define-backend-backup-route-ownership` | `openspec/changes/archive/2026-05-22-define-backend-backup-route-ownership/` | `openspec/specs/architecture-governance/spec.md` |
| `stabilize-backend-control-plane-openapi-docs` | `openspec/changes/archive/2026-05-22-stabilize-backend-control-plane-openapi-docs/` | `openspec/specs/api-documentation/spec.md` |
| `approve-backend-pm2-stateful-gate` | `openspec/changes/archive/2026-05-22-approve-backend-pm2-stateful-gate/` | `openspec/specs/architecture-governance/spec.md` |

## Validation

Pre-archive strict validation passed for all five change IDs:

- `inject-technical-pattern-detection-service-di`
- `refresh-backend-route-openapi-governance`
- `define-backend-backup-route-ownership`
- `stabilize-backend-control-plane-openapi-docs`
- `approve-backend-pm2-stateful-gate`

Post-archive validation:

- `openspec validate --specs --strict`: `32 passed, 0 failed`
- `openspec validate --changes --strict`: `28 passed, 0 failed`

After archive, none of the five change IDs remain in the active OpenSpec change
list.

## Spec Requirements Added

The archive applied five requirements into canonical specs:

- `api-documentation`: Control-Plane OpenAPI Documentation Must Be Stabilized
  Through Evidence
- `architecture-governance`: Backend Service DI Pilot Governance
- `architecture-governance`: Route OpenAPI Governance Must Precede Route
  Mutation
- `architecture-governance`: Backup Route Ownership Must Be Explicit Before
  Mutation
- `architecture-governance`: Stateful PM2 Workflow Execution Requires Explicit
  Approval

## Non-Authorization

This archive PR does not authorize:

- source, test, docs/API, route, OpenAPI runtime behavior, probe URL, generated
  client, script, config, runtime, PM2, or frontend changes
- implementation issue creation
- moving issue `#92` to `ready-for-agent`
- wrapper deletion, route mutation, backup route implementation, docs/API edits,
  a second DI pilot, service singleton migration, or PM2 command execution

## Next Gate

After this archive PR merges, issue `#92` can remain open as the downstream
decision index unless a human explicitly closes or relabels it. Any new
implementation work must start from a new approved child lane with exact write
scope, verification gates, rollback plan, and issue routing.
