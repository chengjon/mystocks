# Backend Next Child Lane Selection

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

Date: 2026-05-22
Status: child-lane-selection-prepared-for-review
Branch: `next-child-lane-selection`
HEAD checked: `c45eaa9c6ba12fbe411015877eef68a48f99a7e8`
Decision timestamp: 2026-05-22T10:54:13+08:00
Parent issue: `#92`

## Purpose

This report selects the next candidate child lane after issue `#92` completed
D2 downstream closeout, OpenSpec archive, and parent disposition.

It is a governance selection packet only. It does not create a new
implementation issue, does not create or modify an OpenSpec proposal, and does
not move any issue to `ready-for-agent`.

## Current Issue State

| Issue | State | Labels | Role |
|---|---|---|---|
| `#92` | `OPEN` | `enhancement`, `ready-for-downstream`, `ready-for-human` | Parent downstream decision index |
| `#78` | `OPEN` | `needs-triage` | Adapter lifecycle DI prerequisite lane |
| `#79` | `OPEN` | `needs-triage` | Service lifecycle DI lane, blocked by `#78` |

## Selected Next Candidate

Select `#78` adapter lifecycle DI triage and evidence reconciliation as the next
child-lane candidate.

Recommended candidate name:
`G1-adapter-lifecycle-di-triage-and-reconciliation`.

Recommended future OpenSpec change ID, if approved later:
`reconcile-backend-adapter-lifecycle-di`.

## Rationale

`#79` service singleton migration is explicitly blocked by `#78`. The service
lane also has broader risk because previous evidence records many service
singleton candidates and no clean implementation batch without further
classification.

`#78` already has a pilot comment recording an EastMoney enhanced adapter
lifecycle DI pilot and targeted verification, but the issue remains
`needs-triage`. That makes `#78` the better next gate: reconcile what is already
done, identify the remaining adapter targets, and decide whether implementation
can proceed as a narrow child lane.

## Required G1 Evidence Before Implementation

The next G1 packet must collect current-head evidence for:

- which of the original six adapter singleton targets remain unresolved
- whether the EastMoney enhanced pilot is present in the current branch
- whether canonical `app.main` lifecycle wiring is still deferred or now possible
- which route handlers still call adapter getter singletons directly
- whether test override coverage exists for each migrated adapter
- whether any adapter is not stateless and must be excluded or split out
- exact write scope for any future implementation batch
- rollback and compatibility getter strategy

## Non-Selected Candidates

| Candidate | Disposition |
|---|---|
| `#79` service lifecycle DI | Not selected yet; remains blocked by `#78` and requires per-candidate classification before further migration. |
| D2.2d wrapper deletion | Not selected; wrapper deletion remains locked behind a separate explicit implementation batch. |
| Route/OpenAPI mutation | Not selected; D2.3-D2.5 remain governance evidence, and mutation needs a separate child packet. |
| PM2 execution | Not selected; D2.6 requires a narrow explicit approval issue, issue comment, or approved runbook. |

## Non-Authorization

This selection packet does not authorize:

- backend source, frontend source, test, generated client, docs/API, route,
  OpenAPI, probe URL, script, config, runtime, or PM2 changes
- issue label changes
- creating implementation issues
- moving `#78`, `#79`, or `#92` to `ready-for-agent`
- creating or modifying OpenSpec proposals
- migrating adapter or service singletons

## Next Gate

Prepare a separate G1 evidence/triage packet for `#78`. That packet may request
approval for a later implementation child lane only after it records current
HEAD evidence, exact write scope, verification gates, and rollback.
