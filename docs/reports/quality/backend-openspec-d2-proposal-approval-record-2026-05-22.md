# Backend OpenSpec D2 Proposal Approval Record - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

## Status

- Status: `approved-for-governance-execution`
- Approval timestamp: `2026-05-22T00:32:45+08:00`
- Approval source: current review thread human maintainer approval, expressed as
  `同意`
- Approval target: D2.3, D2.4, D2.5, and D2.6 OpenSpec proposal task-list
  approval gates
- Parent decision issue: GitHub issue `#92`

## Approved OpenSpec Changes

| Lane | Change ID | Proposal PR | Merge Commit | Approval Effect |
|---|---|---:|---|---|
| D2.3 | `refresh-backend-route-openapi-governance` | `#116` | `fd49d890e0a507b1bca0c792d623d6fcfda637bd` | Approved to execute governance/evidence route/OpenAPI task-list items only |
| D2.4 | `define-backend-backup-route-ownership` | `#118` | `dd56ba0a60532ed8e362b35beab2401b8a463d89` | Approved to execute governance/evidence backup route ownership task-list items only |
| D2.5 | `stabilize-backend-control-plane-openapi-docs` | `#117` | `a07f563456ba28ef99be4a2d36c9457a76e0e519` | Approved to execute governance/evidence control-plane documentation task-list items only |
| D2.6 | `approve-backend-pm2-stateful-gate` | `#119` | `1f32982098bfd7592dc291f0f8308ff6057d7ed3` | Approved to execute PM2 policy acceptance governance/evidence task-list items only |

## Authorization Boundary

This approval unlocks only the governance and evidence tasks already defined in
each change's `tasks.md`. It does not authorize:

- Backend source edits
- Frontend source edits
- Test edits
- Generated client edits
- `docs/api/` edits
- Route behavior changes
- OpenAPI schema or schema-exposure changes
- Probe URL changes
- PM2 command execution
- Service restart, stop, delete, or recreation
- New implementation issue creation
- Moving issue `#92` to `ready-for-agent`

Any implementation, runtime mutation, generated artifact update, docs/API update,
or PM2 execution remains locked behind a separate approved lane with explicit
write scope, evidence scope, rollback plan, and verification gate.

## Next Gates

| Lane | Next Gate |
|---|---|
| D2.3 | Execute `refresh-backend-route-openapi-governance` governance/evidence tasks using current-head route table, OpenAPI, probe, and ownership evidence before any route decision |
| D2.4 | Execute `define-backend-backup-route-ownership` governance/evidence tasks using current-head backup route, OpenAPI, security, permission, audit, and rollback evidence before any backup route decision |
| D2.5 | Execute `stabilize-backend-control-plane-openapi-docs` governance/evidence tasks using current-head control-plane taxonomy, schema exposure, runtime-only compatibility, and probe evidence before any docs/API or OpenAPI decision |
| D2.6 | Execute `approve-backend-pm2-stateful-gate` policy acceptance tasks only; no PM2 workflow may run until a future stateful approval record or approved named-equivalent runbook exists |

## Steward Tree Update

The steward tree records D2.3, D2.4, D2.5, and D2.6 as
`approved-for-governance-execution`. This state means the next worker may gather
and classify evidence under the existing OpenSpec task lists. It is not
implementation approval.

Updated file:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`

## Verification Scope For This Record

Required verification for this approval-record PR:

- `openspec validate refresh-backend-route-openapi-governance --strict`
- `openspec validate define-backend-backup-route-ownership --strict`
- `openspec validate stabilize-backend-control-plane-openapi-docs --strict`
- `openspec validate approve-backend-pm2-stateful-gate --strict`
- Markdown governance gate for this report and the steward tree
- Mainline scope gate for `governance/mainline/task-cards/pr-120.yaml`
- Cached diff whitespace check
