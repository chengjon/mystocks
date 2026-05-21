# Backend OpenSpec Issue92 Downstream Split Acceptance

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: accepted decision split
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Accepted draft: `docs/reports/quality/backend-openspec-issue92-downstream-decision-split-2026-05-21.md`
- Draft PR: <https://github.com/chengjon/mystocks/pull/95>
- Draft merge commit: `6e9ebea25008bbe167e6db287c4c1a45f724a895`
- Acceptance source: current review thread, human maintainer approval
- Acceptance timestamp: `2026-05-21T01:02:26Z`

## Decision

The downstream decision split for issue `#92` is accepted in full.

The accepted split remains a decision-governance boundary. It does not authorize
backend implementation, route mutation, Core file movement, PM2 workflow
execution, or movement of any downstream implementation issue to
`ready-for-agent`.

## Accepted Points

| Decision point | Accepted disposition |
|---|---|
| First DI design pilot | `TechnicalPatternDetectionService` is accepted as the first DI design pilot candidate. The purpose is to establish the dependency injection pattern, lifecycle ownership vocabulary, teardown rule, and rollback pattern before broader service migration. |
| Trading route ownership | Trading route ownership is folded into the unified route/OpenAPI governance lane. It should not be split into a standalone iteration line unless later evidence contradicts the governance fit. |
| Backup route ownership | Backup route ownership is split into its own dedicated proposal candidate. `backup_recovery_secure/cleanup_old_backups.py` and backup-related route/logic ownership belong to this dedicated lane, with separate authorization, security, and operational rules. |

## Accepted Downstream Tracks

| Track | Accepted state | Next gate |
|---|---|---|
| D2.1 `select-backend-technical-pattern-di-pilot` | Accepted as first DI design pilot track | Draft a concrete design packet; no source edits until the implementation plan is approved |
| D2.2 `decide-backend-core-validation-wrapper-retirement` | Accepted as wrapper-retirement readiness track | Prepare readiness evidence for `app.core.validation_messages` retirement or explicit deferral |
| D2.3 `refresh-backend-route-openapi-governance` | Accepted as the unified route/OpenAPI governance parent for trading route ownership | Draft route governance proposal candidate using route table/OpenAPI/probe evidence |
| D2.4 `settle-backend-backup-route-ownership` | Accepted as dedicated backup route ownership proposal candidate | Draft backup ownership proposal candidate, including `cleanup_old_backups.py` |
| D2.5 `stabilize-backend-control-plane-openapi-docs` | Accepted as residual-tail documentation stabilization track | Draft residual-tail decision issue after D2.3 scope is clear |
| D2.6 `approve-backend-pm2-stateful-gate` | Accepted as residual-tail stateful approval track | Draft approval issue or named equivalent for PM2 stateful gate; do not execute from issue `#92` |

## Implementation Boundary

Allowed after this acceptance:

- Update governance documents and issue comments to reflect the accepted split.
- Draft downstream decision/design packets or proposal candidates.
- Create child decision issues only when their scope remains decision/design-only
  or proposal-only.

Still not allowed from this acceptance alone:

- Backend implementation.
- Route mutation.
- Core file movement.
- Compatibility wrapper retirement.
- PM2 stateful workflow execution.
- Moving any downstream issue to `ready-for-agent`.
- Treating issue `#92` as a blanket approval for architecture refactoring.

## Steward Update Requirement

The steward tree should show issue `#92` as `downstream-split-accepted`.

The next operational step is D2.1 design-packet drafting for
`TechnicalPatternDetectionService`. That packet must remain design-only until a
separate implementation approval exists.

