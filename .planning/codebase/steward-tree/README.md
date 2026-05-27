# Steward Tree Governance Contract

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active governance contract
- Prepared at: `2026-05-27T15:32:41+08:00`
- Scope: steward-tree operating model and tool responsibility boundaries

Boundary note: this contract defines how the steward tree is maintained. It does
not authorize source edits, OpenSpec proposal creation, issue label changes,
runtime rollout, PM2 commands, or PR merge decisions.

## Steward Tree Role

The steward tree is the program coordination layer for CODEBASE-MAP architecture
remediation. Its job is to keep five questions answerable:

1. What lane owns the next decision or implementation?
2. What evidence supports the current state?
3. What is explicitly forbidden in this lane?
4. Which artifact is stale, current, or commit-scoped?
5. What gate must happen before the next code change?

It is not a replacement for code, tests, OpenSpec, GitHub PRs, GitNexus,
Graphiti, or context-mode. It is the relationship index between them.

## Responsibility Boundaries

| System | Primary responsibility | Steward-tree relationship |
|---|---|---|
| context-mode | Keep command output, searches, counts, and analysis searchable without flooding context | Feed concise analysis into steward evidence; never become durable repo truth |
| GitNexus | Code graph, symbol context, impact analysis, and staged change blast-radius checks | Required before source edits; steward tree records the risk result and next gate |
| GitHub PR / issue | Delivery review, merge decision, issue labels, discussion, and branch state | Steward tree records PR state and next action; it cannot merge or approve by itself |
| Graphiti | Cross-session memory digest of accepted decisions and milestone summaries | Steward tree records what should be remembered; Graphiti remains digest-only |
| OpenSpec | Proposal, capability delta, task checklist, approval, and archive authority | Steward tree routes architecture changes through OpenSpec and records approval state |
| Reports | Human-readable evidence, verification, closeout, and review notes | Steward tree indexes reports and distinguishes accepted fact from review input |
| Source / tests / runtime probes | Actual implementation truth | Steward tree must defer to current verification when report snapshots are stale |

## Node Types

| Node type | Purpose | May edit source? | Required next gate |
|---|---|---:|---|
| evidence | Collect facts, counts, probes, and contradictions | No | Human or OpenSpec decision |
| decision | Choose lane, priority, or ownership | No | Authorization package |
| authorization | Define exact allowed paths, tests, rollback, and forbidden scope | No | Source implementation approval |
| implementation | Apply approved source/test changes | Yes, only approved paths | Verification and review |
| closeout | Record completion and residual blockers | No | Archive, next-lane decision, or stop |
| external | Track PRs, issues, or artifacts owned by another lane | No | Owning lane action |

## Minimum Node Fields

Each active node should have:

- `id`
- `title`
- `type`
- `state`
- `owner_lane`
- `parent`
- `evidence`
- `allowed_scope`
- `forbidden_scope`
- `current_head`
- `freshness`
- `next_gate`

The machine-readable form lives in
`.planning/codebase/steward-tree/steward-index.json`.

## State Vocabulary

Use these states unless a track has a documented reason to add another:

- `blocked`
- `for_review`
- `accepted`
- `open_pr`
- `merged`
- `closed`
- `deferred`
- `stale_aware`
- `contradiction_unresolved`

State changes should name the artifact or PR that proves the transition.

## Update Rules

1. Keep the root task-tree file as a navigation document, not a ledger dump.
2. Put long historical recovery material in `archive/`.
3. Put active gates in `current-next-gates.md`.
4. Put durable evidence pointers in `evidence-index.md`.
5. Put automation fields in `steward-index.json`.
6. Put track narrative in `tracks/*.md`.
7. Record accepted milestones in Graphiti only after the PR or decision package
   exists in repo/GitHub.

## Quality Rules

- Every implementation lane must have a prior authorization node.
- Every source lane must run GitNexus impact before edits and staged
  `detect_changes` before commit.
- Every generated artifact reference must include freshness policy.
- Every external review input must stay marked as review input until accepted.
- Every broad architecture topic must be split into lane-sized decisions before
  any source implementation begins.

## Guard Ideas

Future automation can validate:

- `steward-index.json` is valid JSON.
- Every active node has `next_gate`.
- Every non-implementation node has `source_edit_authority: false`.
- Every implementation node has allowed paths, forbidden paths, and rollback.
- Every referenced split file exists.
- Root task-tree file stays below a size threshold.
- PR numbers referenced by active external nodes are still queryable.
