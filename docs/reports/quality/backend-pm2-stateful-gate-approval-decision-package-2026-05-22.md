# Backend PM2 Stateful Gate Approval Decision Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

Date: 2026-05-22
Status: decision-package-prepared-for-review
Branch: `d2-6-pm2-stateful-gate-approval-evidence`
HEAD checked: `b35d016f8b89baf0889fb57a090f4a09b698e375`
OpenSpec change: `approve-backend-pm2-stateful-gate`
Issue: `#92`

## Purpose

This package executes the approved D2.6 governance/evidence task list for PM2
stateful gate approval policy. It converts the proposal into a reviewable
approval contract and keeps the execution boundary explicit:

- no PM2 command execution
- no service stop, delete, restart, or recreation
- no backend source, frontend source, test, docs/API, route, OpenAPI, probe URL,
  generated client, or runtime behavior changes
- no implementation issue creation
- no movement of issue `#92` to `ready-for-agent`

## Decision Summary

| Decision | Result |
|---|---|
| PM2 workflow modes | `gate`, `regression`, and `all` remain stateful workflows. |
| Issue `#92` | Remains a decision issue only; it does not authorize PM2 execution by implication. |
| Health/status task `4.7` | Remains closed by `backend-health-status-pm2-gate-2026-05-18.md` unless new current-HEAD evidence contradicts that report. |
| Future PM2 execution | Requires explicit approval or an approved named equivalent before any PM2 command is run. |
| Stop rule | Future agents must stop if `scripts/run_pm2_integration_workflow.sh` appears without an explicit approval record. |

## Current Evidence

| Evidence | Value |
|---|---|
| Current HEAD | `b35d016f8b89baf0889fb57a090f4a09b698e375` |
| Issue `#92` state | `OPEN` |
| Issue `#92` labels | `enhancement`, `ready-for-human`, `ready-for-downstream` |
| Issue `#92` `ready-for-agent` | absent |
| Static script path | `scripts/run_pm2_integration_workflow.sh` |
| Static script SHA-256 | `b638d6a32657922fc161f9c5d473c92d82d2acfa0f74b49d61cd53782679b92c` |
| Historical PM2 gate report | `docs/reports/quality/backend-health-status-pm2-gate-2026-05-18.md` |
| Generated evidence artifact | `.planning/codebase/generated/pm2-stateful-gate-approval-evidence-2026-05-22.json` |

The static script scan confirms these stateful markers:

- `pm2 stop all`
- `pm2 delete all`
- `pm2 start ecosystem.test.config.js`
- `bash scripts/run_e2e_pm2.sh`
- dispatch modes for `gate`, `regression`, and `all`

No PM2 command was executed while preparing this package.

## Approval Record Template

Any future stateful PM2 workflow approval must record:

- approval source
- approval timestamp
- approving human or owner
- target branch and commit
- exact command mode or named equivalent
- expected state mutation
- service impact and ports
- rollback and restore commands
- evidence destination
- timeout and stop rule
- acceptance owner
- for named equivalents, the exact command set, substitution reason, and what
  full PM2 workflow evidence remains unproven

Read-only PM2 sampling must record the exact command list and explicitly state
that no service mutation is expected.

## Boundaries

This package accepts the policy. It does not approve a fresh PM2 run.

The health/status `4.7` PM2 evidence remains a historical closure artifact for
that line. It can be cited for governance and archive decisions only with its
freshness limits recorded. It is not a reusable approval to run
`scripts/run_pm2_integration_workflow.sh`.

## Review Checklist

- [x] `gate`, `regression`, and `all` are classified as stateful PM2 workflows.
- [x] Issue `#92` remains a decision issue and has no `ready-for-agent` label.
- [x] Health/status task `4.7` remains closed unless contradicted by new
  current-HEAD evidence.
- [x] Future agents must stop before running `scripts/run_pm2_integration_workflow.sh`
  without explicit approval or an approved named equivalent.
- [x] Approval record required fields are captured.
- [x] No PM2 command was executed by this package.
- [x] No implementation issue was created by this package.
