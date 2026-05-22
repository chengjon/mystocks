# CODEBASE-MAP Steward Tree Retrospective - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for-review
- Workline: steward tree retrospective and next operating model
- Steward index: `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- Current HEAD checked: `68da82084266ca7f9b7be9f5b55da7ac5e64fbd7`
- Prepared at: `2026-05-22`
- Scope: governance analysis only

Boundary note: This document records operating lessons for the steward tree. It
does not authorize backend source edits, frontend source edits, tests, generated
client updates, docs/API edits, OpenSpec proposal creation, issue label changes,
PM2 commands, runtime rollout, or movement of issue `#79` or issue `#92` to
`ready-for-agent`.

## What The Steward Tree Has Done

The steward tree has become the coordination layer between the codebase map,
OpenSpec branches, GitHub issues, PRs, implementation reports, and human review
decisions. Its main value is not that it replaces those artifacts; its value is
that it records how they relate and what gate must happen next.

### 1. Sequenced Parallel Worklines

The tree converted a broad architecture remediation program into ordered lanes:

| Lane | Steward role |
|---|---|
| Route/OpenAPI governance | Keep route evidence, OpenAPI exposure, compatibility shims, and control-plane endpoints in one route-governance vocabulary |
| Core split governance | Keep Core Batch 2 blocked until explicit reconciliation gates are satisfied |
| Service lifecycle DI | Separate adapter closeout, service candidate classification, implementation authorization, implementation, and closeout |
| CSRF/schema/error-contract/control-plane | Preserve decision-only or evidence-only state until a later approved branch exists |

This prevented unrelated worklines from using a shared architecture concern as
implicit approval for code changes.

### 2. Preserved The Authorization Boundary

The tree repeatedly made the same distinction explicit:

- evidence package
- decision package
- implementation authorization package
- source implementation
- closeout record

That separation was important in issue `#92` and issue `#79`. It allowed the
project to accept planning and evidence while keeping source changes locked
until a smaller, reviewed implementation packet existed.

### 3. Made State Recoverable After Context Loss

Several threads spanned many reviews, worktrees, PRs, and commits. The steward
tree gave later sessions enough context to resume without re-litigating old
decisions. A usable row always included:

- parent lane
- source evidence
- state
- current fact
- next gate
- forbidden scope

This was especially useful after the `email_service.py` lifecycle DI lane:
candidate classification in PR `#140`, implementation authorization in PR
`#141`, implementation in PR `#142`, and closeout in PR `#143` remained
traceable as one state machine instead of four disconnected PRs.

### 4. Reduced Scope Creep

The tree caught and constrained recurring failure modes:

- treating evidence-only work as permission to edit backend code
- turning route governance into a broad route migration
- starting a second service DI candidate before the first pilot was closed
- reopening completed P3-C5 error-contract work from stale counts
- treating compatibility wrappers as automatically deletable

The strongest pattern was to write the non-goals next to the current gate, not
in a separate document only.

### 5. Preserved Freshness And Evidence Context

The tree encouraged recording commit hashes, PR numbers, issue state, and
artifact paths. This mattered when generated route tables, OpenAPI counts,
GitNexus impact results, and runtime reports were produced at different HEADs.

The practical rule that emerged:

- If two artifacts disagree and were produced at different HEADs, mark older
  evidence as stale-aware.
- If two artifacts disagree at the same HEAD, create a reconciliation task.
- Do not unblock dependent implementation work from stale evidence.

## Operating Lessons

### Lesson 1: Closeout Is A Real Phase

Implementation completion is not the same as governance completion. The project
needed PR `#143` after PR `#142` so that the tree could record the merged
functional result and the next gate. Without closeout, later agents would see a
merged implementation but not know whether a second candidate was authorized.

### Lesson 2: Candidate Classification Must Precede Authorization

The service lifecycle DI lane showed that broad singleton counts are not an
implementation backlog. A useful candidate packet must classify:

- already converted patterns
- completed pilot evidence
- first future candidates
- name-collision risks
- critical or broad route-impact exclusions
- large or cross-cutting exclusions
- domain-heavy medium candidates
- real-time or process-level singleton designs

This helped avoid choosing a high-impact service just because it matched a
singleton regex.

### Lesson 3: The Tree Needs Both Human And Machine-Readable State

Natural-language rows are readable, but automated guards need stable fields.
The tree worked best when paired with generated JSON artifacts and PR task
cards. Future rows should carry stable state values instead of only narrative
phrases.

### Lesson 4: Exact Forbidden Scope Prevents Misexecution

Short forbidden-scope lists such as "no source edits" were useful, but the most
effective rows named the exact forbidden surfaces:

- backend source
- frontend source
- tests
- generated clients
- docs/API
- OpenSpec proposals/specs
- issue labels
- `ready-for-agent` movement
- PM2 commands
- runtime rollout

This made review comments easier to absorb without accidentally broadening the
work.

### Lesson 5: Issue Labels And Tree State Can Diverge

GitHub labels are workflow signals, not full architecture state. The tree must
continue to record the real gate even when issue labels are coarse. Current
example: issue `#79` remains `OPEN` with `needs-triage` after the first
`email_service.py` pilot closed; that does not mean a second service migration
is already authorized.

## Improvement Opportunities

### 1. Add A Machine-Readable Steward Node Index

Create `.planning/codebase/generated/steward-tree-nodes-YYYY-MM-DD.json` with
one object per branch:

```json
{
  "node_id": "G2.4",
  "parent": "G",
  "state": "second-candidate-selection-prepared-for-review",
  "source_evidence": [],
  "current_head_checked": "",
  "next_gate": "",
  "authorized_scope": [],
  "forbidden_scope": []
}
```

The Markdown tree can remain the human-facing map, while the JSON index becomes
the guard-friendly state source.

### 2. Standardize State Transitions

Recommended lifecycle:

1. `candidate-observed`
2. `evidence-classified`
3. `authorization-prepared`
4. `approved-for-implementation`
5. `implemented`
6. `reviewed`
7. `merged`
8. `recorded`
9. `archived` or `deferred`

Rows should not jump from `evidence-classified` to `implemented`. The missing
state should become a review blocker.

### 3. Split Narrative Tree From Active Gate Register

Keep the current tree as the long-form map, but add a compact "Active Gate
Register" with only open gates:

| Gate | Owner lane | Current blocker | Next allowed action | Forbidden action |
|---|---|---|---|---|

This would make daily continuation faster and reduce accidental work on closed
branches.

### 4. Add Freshness Fields To Every Generated Artifact

Every generated evidence artifact should include:

- `generated_at`
- `git_head`
- `current_head_checked_at_review`
- `stale_if_head_mismatch`
- `source_artifact_paths`
- `review_disposition`

This should apply to route tables, OpenAPI counts, GitNexus impact summaries,
singleton inventories, and issue-state snapshots.

### 5. Add A Steward-Tree Guard

A lightweight guard could check:

- every source evidence path exists
- every active OpenSpec change exists if named
- every issue/PR link has a captured state
- no row contains implementation authorization without an authorization packet
- no closed implementation row lacks a closeout artifact
- no future source edit appears in an evidence-only row

This would turn several recurring review findings into pre-review failures.

### 6. Keep Graph Memory As A Digest, Not A Truth Source

Graphiti is useful for recording durable decisions and cross-thread summaries.
It should store concise digests:

- what was accepted
- what remains forbidden
- what the next gate is
- which commit/PR/report anchors the decision

It should not replace the actual Markdown reports, OpenSpec tasks, GitHub
issues, or current code.

## Recommended Operating Model

For each future architecture branch:

1. Create or update evidence package.
2. Record candidate classification and exclusions.
3. Create an implementation authorization packet only after review.
4. Implement exactly the authorized write scope.
5. Run scoped verification and GitNexus staged-change detection when code is
   changed.
6. Merge only after review.
7. Create a closeout/update PR for the steward tree.
8. Do not start the next candidate until the closeout row says the next
   selection gate is open.

## Immediate Next Use

The next steward-tree use should be G2.4: review the first
`email_service.py` pilot evidence and select a second service lifecycle DI
candidate package without source edits.

Current-head candidate comparison supports `announcement_service.py` as the
next authorization-candidate input, not as an implementation approval:

| Candidate | GitNexus risk | Direct callers | Extra affected symbols | Disposition |
|---|---:|---:|---:|---|
| `announcement_service.py` / `get_announcement_service` | MEDIUM | 11 | 0 transitive symbols reported | Better next candidate; one route module owns the direct callers |
| `watchlist_service.py` / `get_watchlist_service` | MEDIUM | 9 | 6 transitive symbols through data adapter layers | Defer; adapter/data-layer coupling makes it a larger design surface |

Next gate: human review of the G2.4 selection package. If accepted, create a
separate G2.5 implementation authorization packet for `announcement_service.py`
with exact write scope, tests, rollback plan, GitNexus pre-edit gate, and
forbidden scope. No service source edit is authorized by this retrospective.
