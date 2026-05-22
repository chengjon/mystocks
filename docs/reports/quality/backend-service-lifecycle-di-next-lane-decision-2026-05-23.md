# Backend Service Lifecycle DI Next-Lane Decision - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: decision-packet-prepared-for-review
- Workline: G2.16 service lifecycle DI next-lane decision
- Current branch: `g2-16-service-di-next-decision`
- Current HEAD: `03c48f74d73f1de505470698966776f6624a0ec7`
- Parent issue: https://github.com/chengjon/mystocks/issues/92
- Service lifecycle issue: https://github.com/chengjon/mystocks/issues/79
- Decision PR: https://github.com/chengjon/mystocks/pull/156
- Decision PR checks at creation: Mainline Governance Gate passed;
  check-compliance passed
- Recorded at: `2026-05-23T03:19:24+08:00`

Boundary note: This packet selects the next governance lane only. It does not
authorize backend source edits, frontend edits, tests, generated clients,
route/OpenAPI changes, PM2/runtime work, OpenSpec changes, issue label movement,
or `ready-for-agent` movement.

## Input State

| Item | Current state | Evidence |
|---|---|---|
| PR `#154` | `MERGED` | `1dcb394a49a9d95e939b2119acc431b825954036` |
| PR `#155` | `MERGED` | `03c48f74d73f1de505470698966776f6624a0ec7` |
| Issue `#79` | `OPEN`, `needs-triage` | Live GitHub status checked from this worktree |
| Issue `#92` | `OPEN`, `enhancement`, `ready-for-human`, `ready-for-downstream` | Live GitHub status checked from this worktree |
| G2.1 candidate classification | Accepted historical input | `email_service.py` selected; `announcement_service.py` and `watchlist_service.py` deferred |
| G2.4/G2.8 candidate selections | Consumed | `announcement_service.py` and `watchlist_service.py` were selected and completed in later packets |
| G2.12-G2.15 helper cleanup | Complete | Adapter-aware watchlist helper seam selected, authorized, implemented, and closed out |

## Decision

Select a G2.17 current-head service lifecycle DI candidate refresh as the next
lane.

Do not select a fourth route-surface service implementation candidate in this
packet. Do not start another adapter-aware cleanup in this packet. Do not move
issue `#79` or issue `#92` labels in this packet.

## Rationale

The accepted low/medium-risk candidate queue has been consumed:

- `email_service.py` was the first future service lifecycle DI pilot.
- `announcement_service.py` was selected as the second candidate and completed.
- `watchlist_service.py` was selected as the third candidate and completed.
- The explicit watchlist adapter/data helper seam left by G2.11 was closed by
  G2.14 and recorded by G2.15.

The prior G2.1 classification was useful, but it is now stale as a selection
source for further source edits. It was measured before multiple service DI
commits and before the watchlist helper cleanup. It also did not identify a clean
fourth route-surface service with lower governance risk than closing the
watchlist adapter-aware seam.

The next safe step is therefore evidence refresh, not implementation
authorization.

## G2.17 Refresh Scope

If this decision is accepted, G2.17 should create a current-head evidence packet
that:

- regenerates the service singleton/getter inventory under
  `web/backend/app/services`;
- records current HEAD, generation timestamp, and stale-if-head-mismatch status;
- distinguishes completed route-surface DI pilots, completed helper cleanups,
  candidates still requiring source edits, and false positives;
- rechecks GitNexus context/impact for any candidate recommended for a future
  authorization packet;
- classifies candidates by route-surface service, helper/adapter seam,
  process-level singleton, external client/session-backed service, cache/task
  runner, and false positive;
- recommends either a G2.18 implementation authorization candidate or a pause of
  the service lifecycle DI sequence.

G2.17 remains evidence/design only. Source edits remain locked until a later
authorization packet names exact files, tests, rollback plan, and GitNexus gates.

## Explicit Non-Goals

This decision packet does not authorize:

- editing `web/backend/app/services/**`;
- editing route handlers or OpenAPI contracts;
- creating or modifying OpenSpec changes/specs;
- changing GitHub issue labels;
- moving issue `#79` or issue `#92` to `ready-for-agent`;
- creating a new implementation issue;
- starting a fourth service lifecycle DI source implementation;
- running PM2/stateful gates.

## Next Gate

Human review of this G2.16 decision packet.

If accepted, create a separate G2.17 current-head candidate refresh packet before
any further service lifecycle DI source edits.
