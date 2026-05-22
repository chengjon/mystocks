# Backend Adapter Lifecycle DI Disposition

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

Date: 2026-05-22
Status: disposition-prepared-for-review
Branch: `g1-issue78-disposition`
HEAD checked: `299f0aa7672993859b2cdd1f6515981a99d90f1e`
Generated at: 2026-05-22T11:27:03+08:00
Primary issue: `#78`
Parent issue: `#92`
Blocked downstream issue: `#79`
Input PR: `#136`

## Purpose

This report converts the merged G1 adapter lifecycle DI triage packet into a
disposition recommendation for issue `#78`.

This is a governance disposition packet only. It does not close issue `#78`,
does not change issue labels, does not create an implementation issue, does not
create or modify an OpenSpec proposal, and does not authorize backend source,
tests, route, OpenAPI, docs/API, runtime, PM2, script, config, or generated
client changes.

## Inputs

| Input | State | Evidence |
|---|---|---|
| PR `#136` | Merged | `299f0aa7672993859b2cdd1f6515981a99d90f1e` |
| G1 triage report | Merged | `docs/reports/quality/backend-adapter-lifecycle-di-triage-2026-05-22.md` |
| G1 triage JSON | Merged | `.planning/codebase/generated/adapter-lifecycle-di-triage-2026-05-22.json` |
| Issue `#78` | `OPEN`, `needs-triage` | Adapter lifecycle DI prerequisite lane |
| Issue `#79` | `OPEN`, `needs-triage` | Service lifecycle DI lane blocked by `#78` |
| Issue `#92` | `OPEN`, `ready-for-downstream` | Parent downstream decision index |

## Disposition Summary

Recommended disposition: after human review accepts this packet, close issue
`#78` as reconciled governance evidence, not as an implementation backlog.

Rationale:

- The five current adapter targets have provider/app-state/test evidence.
- The five current adapter targets no longer show `_instance = None`.
- The remaining exact-symbol consumers are service/core integration points, not
  direct route-handler adapter getter calls.
- `realtime_mtm` is not proved as a current adapter target under
  `web/backend/app/adapters/`.
- Any remaining consumer migration, realtime identity decision, or production
  composition-root wiring should be a separate child packet with exact write
  scope, not continued inside issue `#78`.

## Adapter Target Disposition

| Target | Evidence state | Recommended disposition |
|---|---|---|
| `eastmoney_adapter` | Provider symbols, app-state helpers, lifecycle test evidence, no `_instance = None` | Accept as reconciled for issue `#78`; direct service/core consumers need classification only if a future cleanup lane is approved |
| `eastmoney_enhanced` | Provider symbols, app-state helpers, lifecycle test evidence, no `_instance = None`; `app_factory.py` wiring present | Accept as reconciled for issue `#78`; `main.py` composition-root decision is separate future scope |
| `akshare_extension` | Provider symbols, app-state helpers, lifecycle test evidence, no `_instance = None` | Accept as reconciled for issue `#78`; direct service/core consumers need classification only if a future cleanup lane is approved |
| `tqlex_adapter` | Provider symbols, app-state helpers, lifecycle test evidence, no `_instance = None` | Accept as reconciled for issue `#78`; direct service/core consumers need classification only if a future cleanup lane is approved |
| `cninfo_adapter` | Provider symbols, app-state helpers, lifecycle test evidence, no `_instance = None` | Accept as reconciled for issue `#78`; direct service/core consumers need classification only if a future cleanup lane is approved |
| `realtime_mtm` | No adapter file proved under `web/backend/app/adapters/`; mentions exist in runtime/API/test files | Remove from current adapter singleton implementation scope until canonical identity and ownership are proved |

## Remaining Work Routing

Do not continue implementation inside issue `#78`. Route remaining concerns as
separate gates:

| Concern | Route |
|---|---|
| Direct service/core adapter getter consumers | Optional future cleanup or design packet with exact files and GitNexus impact |
| `realtime_mtm` identity and ownership | Separate realtime route/service governance packet if needed |
| `main.py` versus `app_factory.py` adapter composition-root wiring | Separate app composition-root decision or implementation authorization if needed |
| Service singleton lifecycle DI | Issue `#79`, only after issue `#78` disposition is human-accepted |

## Effect On Issue `#79`

This packet recommends that issue `#79` remain blocked until a human accepts the
issue `#78` disposition.

After acceptance, issue `#79` may move to a new design/triage packet for service
lifecycle DI, but not directly to implementation. The service lane still needs
candidate classification, interface/test-double strategy, exact write scope,
verification gates, and rollback before source edits.

## Recommended Issue Comment

If accepted, post a closing or closeout comment to issue `#78` with this
substance:

> Issue `#78` is reconciled as governance evidence. The five current adapter
> targets have provider/app-state/test evidence and no `_instance = None`;
> `realtime_mtm` is not a proved current adapter target under
> `web/backend/app/adapters/`. Remaining consumer cleanup, realtime ownership,
> and composition-root work must use separate approved child lanes. Closing
> `#78` does not authorize implementation or move `#79` to implementation.

## Non-Authorization

This packet does not authorize:

- closing issue `#78` without human approval
- changing issue labels
- backend source, frontend source, test, generated client, docs/API, route,
  OpenAPI, probe URL, script, config, runtime, or PM2 changes
- creating implementation issues
- moving `#78`, `#79`, or `#92` to `ready-for-agent`
- creating or modifying OpenSpec proposals
- migrating adapter or service singletons

## Evidence Artifact

Structured disposition evidence is recorded in:

`.planning/codebase/generated/adapter-lifecycle-di-disposition-2026-05-22.json`
