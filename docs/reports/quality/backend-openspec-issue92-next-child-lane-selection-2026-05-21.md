# Backend OpenSpec Issue #92 Next Child Lane Selection

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: review-ready recommendation
Date: 2026-05-21
Parent issue: #92

Boundary note: This document is a recommendation and evidence index only. It does
not authorize source code changes, GitHub issue publication, OpenSpec proposal
publication, OpenSpec implementation, old `.planning/codebase/` document
replacement, production rollout, or promotion of this recommendation into backend
execution authority.

## Context

The D2.1a `TechnicalPatternDetectionService` DI pilot is fully closed:

- PR `#112` implemented and merged the route-level DI seam.
- PR `#113` completed the OpenSpec task closeout.
- PR `#114` synchronized the steward tree so D2.1a is no longer left at a merge-review gate.

This report does not authorize a second implementation lane. It only ranks the next
candidate lanes and records which ones are blocked, decision-only, or ready for
further planning.

## Candidate Ranking

### 1. D2.3: Trading Route/OpenAPI Governance

Best next candidate.

Why it rises first:

- It is already framed as a governance/planning package, not a broad feature build.
- It directly follows the route/OpenAPI evidence refresh work that was already
  stabilized in the sequence unblocks and route-contract lanes.
- It can absorb the trading ownership, route matrix, probe consumer matrix, and
  route/OpenAPI exposure governance without authorizing unrelated backend changes.

Recommended next action:

- convert the planning package into the next explicitly approved governance child
  lane only after a human review confirms the scope still matches current-head
  route/OpenAPI evidence.

### 2. D2.5: Control-Plane OpenAPI Docs Stabilization

Strong secondary candidate.

Why it stays high:

- control-plane / probe documentation remains a distinct governance concern;
- it is useful for keeping health, readiness, status, and smoke-facing docs
  aligned with current route exposure;
- it should stay separate from any business API migration lane.

### 3. D2.4: Backup Route Ownership

Dedicated candidate, but narrower than D2.3.

Why it is not first:

- it is explicitly a separate ownership proposal track;
- it should not be folded into generic route governance or trading governance;
- it likely needs its own approval boundary once F is settled.

### 4. G: Service Seams and Singleton Pilots

Blocked until the interface/test-double strategy is explicitly designed.

Why it is not next:

- the singleton matrix already showed no low-risk pilot;
- the next gate requires interface extraction and test-double design before any
  pilot can be approved;
- D2.1a proves the route-level DI seam pattern, but not a second service pilot.

### 5. D2.6: PM2 Stateful Gate Approval

Decision-only, not an execution lane.

Why it remains last:

- it is governed by approval or named-equivalent approval;
- it does not become a general backend implementation channel;
- it should only open when a future stateful workflow genuinely needs a fresh PM2
  run.

## Recommendation

If the question is "what should be the next backend governance lane after D2.1a?",
the answer is:

1. Start with D2.3 route/OpenAPI governance.
2. Keep D2.5 as the next docs/probe stabilization candidate.
3. Leave D2.4, G, and D2.6 blocked or decision-only unless a separate review
   explicitly changes their gate.

## Boundary

This report does not authorize:

- code changes;
- OpenSpec proposal publication;
- new GitHub issue creation;
- moving `#92` to `ready-for-agent`;
- any second DI pilot;
- any route, OpenAPI, response contract, PM2, or function-tree taxonomy change.

It is a recommendation input only.
