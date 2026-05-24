# Codebase Map Steward Tree Practice Guide - 2026-05-24

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for-review
- Prepared at: `2026-05-24`
- Workline: codebase map steward-tree practice summary
- Primary steward index: `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- Prior retrospective: `.planning/codebase/CODEBASE-MAP-STEWARD-TREE-RETROSPECTIVE-2026-05-22.md`
- Current reference point: through G2.46 AdvancedAnalysis route-provider closeout PR preparation
- Scope: governance method summary only

Boundary note: this guide summarizes the steward-tree operating model and
improvement proposals. It does not authorize backend source edits, frontend
source edits, tests, generated client updates, docs/API edits, OpenSpec proposal
creation, issue label changes, PM2 commands, runtime rollout, or movement of any
GitHub issue to `ready-for-agent`.

## Executive Summary

The steward tree became the control surface for a long-running architecture
remediation program. Its most important function was not replacing OpenSpec,
GitHub issues, reports, PRs, or source code. Its role was to connect those
artifacts into a recoverable state machine:

```text
architecture concern
-> evidence package
-> decision package
-> implementation authorization
-> source implementation
-> verification
-> closeout
-> next candidate selection
```

In this project, the tree helped prevent architecture work from becoming an
unbounded refactor. It let the team repeatedly answer:

- What has already been accepted?
- What was only evidence, not implementation authority?
- Which exact files or domains may be changed next?
- Which compatibility surfaces must stay?
- Which PR, issue, report, commit, and JSON artifact prove the current state?
- What is the next gate before another agent can safely continue?

The pattern is transferable to other projects whenever work spans multiple
agents, branches, review rounds, and partial implementation lanes.

## Functions Proven In This Project

### 1. Cross-Line Coordination

The codebase remediation effort had several simultaneous lanes:

| Lane | Example scope | Steward-tree function |
|---|---|---|
| Route/OpenAPI governance | route table, OpenAPI path count, probe consumers, trading/backup/control-plane ownership | Kept route facts, schema exposure, runtime-only compatibility, and consumer matrices under one vocabulary |
| Core split governance | validation helper split, wrapper retention, docs/API import standardization | Prevented wrapper deletion from being inferred from source import migration alone |
| Service lifecycle DI | email, announcement, watchlist, stock-search, market-data, TDX, AdvancedAnalysis provider seams | Forced candidate classification, authorization, implementation, closeout, and refresh into separate steps |
| Error-contract closure | P3-C5 / HTTPException migration | Stopped stale counts from reopening already-closed work |
| PM2/stateful gate | stateful integration workflow approval | Kept runtime mutation behind explicit approval rather than letting it leak through evidence packages |

Without the tree, these lanes would have competed inside the master execution
plan and GitHub issue labels. The tree gave each lane a current state and a
single next gate.

### 2. Authorization Boundary Control

The tree repeatedly separated five different artifact types:

| Artifact type | What it can do | What it cannot do |
|---|---|---|
| Evidence package | Record current facts, counts, consumers, blockers | Authorize code changes |
| Decision package | Choose a direction or classify ownership | Implement that direction |
| Authorization package | Define a future write scope and required gates | Modify source in the same packet |
| Implementation PR | Change exactly the authorized files | Broaden scope or delete compatibility surfaces without prior approval |
| Closeout packet | Record merged result and next gate | Start the next implementation lane |

This distinction became critical in issue `#92` and issue `#79`. It allowed the
project to accept broad architecture decisions while still forcing each source
change into a narrow reviewed batch.

### 3. Context Recovery Across Long Threads

The work crossed many PRs, worktrees, reports, and human review comments. The
tree made later continuation possible because each row carried enough context to
resume without asking the user to reconstruct history.

A useful row contained:

- lane or parent node
- state
- source evidence path
- current fact summary
- PR/issue/commit anchor
- next gate
- forbidden scope
- supersession or freshness note

This directly helped after context compaction and between independent worklines.
An agent could read the tree and know whether it should classify, authorize,
implement, close out, archive, or stop.

### 4. Scope-Creep Resistance

The steward tree made hidden broadening visible. Recurring examples included:

- evidence-only reports trying to contain optional backend fixes
- route governance drifting into route mutation
- compatibility wrappers being treated as automatically deletable
- broad singleton scans being mistaken for implementation backlogs
- stale generated artifacts being treated as current truth
- issue labels being interpreted as complete architecture state

The strongest protection was to write the forbidden action beside the next gate.
For example: "candidate refresh only; no source edits; no compatibility getter
retirement; no next target selected."

### 5. Freshness And Evidence Management

The tree forced artifact freshness to be explicit. This mattered because route
tables, OpenAPI snapshots, GitNexus impact results, runtime smoke reports, and
issue states were not always produced at the same commit.

The working rule that emerged:

- If evidence differs because it was generated at different HEADs, mark older
  evidence stale-aware.
- If evidence differs at the same HEAD, create a reconciliation task.
- Do not unblock implementation from stale or ambiguous evidence.
- Put machine-readable freshness fields in generated JSON whenever possible.

### 6. Human Review Compression

The tree turned long review discussions into short state transitions. Instead
of asking a reviewer to reread the entire thread, the reviewer could evaluate:

- the new report
- the generated JSON artifact
- the task card
- the tree row update
- the next gate and non-goals

This made repeated review/approval cycles faster while preserving traceability.

### 7. Reusable Implementation Conveyor

The service lifecycle DI workline proved that the tree can operate as a
conveyor, not just an index:

```text
candidate refresh
-> usefulness / ownership triage
-> implementation authorization
-> implementation PR
-> closeout
-> current-head refresh
-> next candidate selection
```

By G2.46, the line had accumulated multiple service-provider seams and had a
repeatable rule: no new source implementation starts until the previous
implementation has a closeout and the current-head candidate inventory has been
refreshed.

## Observed Benefits

| Benefit | Concrete effect in this project |
|---|---|
| Reduced accidental implementation | Evidence and decision artifacts no longer implied source-edit authority |
| Smaller PRs | Implementation branches were constrained to exact files and tests |
| Safer compatibility migration | Compatibility getters and wrappers were retained until consumer matrices existed |
| Better stale-evidence handling | Old F821, HTTPException, route table, and OpenAPI counts stopped being treated as current truth |
| Easier review | Reviewers could check one row, one report, one JSON artifact, and one task card |
| Better multi-agent handoff | Later agents could continue from the next gate instead of reopening prior decisions |
| More reliable architecture sequencing | Broad seams were decomposed before implementation candidates were selected |

## Costs And Friction

The model also introduced overhead:

| Cost | Why it appeared | How to manage it |
|---|---|---|
| More documents | Each phase needed a durable artifact | Keep artifacts short and typed by purpose |
| Repetitive state updates | Tree, report, JSON, task card, PR body can duplicate facts | Generate stable fields from one machine-readable index where possible |
| Review fatigue | Many governance PRs can look similar | Add active-gate register and closeout summary |
| Stale tree risk | If a PR merges without tree update, later agents see old state | Make tree update a required closeout check |
| Ambiguous labels | GitHub issue labels are too coarse for architecture state | Treat labels as workflow signals, not truth source |

## Lessons Learned

### Lesson 1: Closeout Is Not Optional

Implementation completion and governance completion are different. A source PR
can pass tests and still leave the next agent unsure whether the lane is closed,
whether compatibility cleanup is authorized, or whether another candidate can
start. A closeout row and closeout report should be mandatory after each
implementation merge.

### Lesson 2: Candidate Counts Are Not Backlogs

Regex or static scans are useful for finding candidates, but they do not define
the implementation queue. Every candidate needs classification:

- active route dependency
- compatibility fallback
- factory/helper
- external-client wrapper
- DB/session-backed service
- cache/task-running service
- process-level singleton
- broad data seam
- false positive

Only after that classification should a single target be authorized.

### Lesson 3: Compatibility Surfaces Need Their Own Decisions

After route migration, old getters or wrappers may have zero route calls but
still serve tests, exports, external imports, or future fallback behavior. The
tree should treat cleanup as a separate retention/retirement decision, not as an
automatic part of the implementation PR.

### Lesson 4: Exact Forbidden Scope Beats Generic Warnings

"Do not broaden scope" is weaker than listing exact forbidden surfaces:

- no backend source
- no tests
- no route behavior
- no OpenAPI exposure
- no docs/API
- no generated clients
- no PM2
- no issue labels
- no OpenSpec archive
- no compatibility getter retirement

The exact list makes review and automation simpler.

### Lesson 5: Machine-Readable State Is Needed

Markdown is good for human review, but automated guards need JSON/YAML. The
project became more reliable when each important row had:

- a human report
- a generated JSON artifact
- a mainline task card
- a PR/issue/commit anchor

Other projects should not rely on narrative Markdown alone.

## Recommended Steward-Tree Structure For Other Projects

Use three layers:

```text
1. Human tree
   .planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-YYYY-MM-DD.md

2. Machine index
   .planning/codebase/generated/steward-tree-nodes-YYYY-MM-DD.json

3. Per-PR task card
   governance/mainline/task-cards/pr-<number>.yaml
```

### Human Tree Minimum Fields

| Field | Purpose |
|---|---|
| Node ID | Stable reference such as `G2.46` |
| Parent lane | Lets readers see the larger workline |
| State | Candidate, evidence, authorization, implementation, closeout, archived, etc. |
| Source evidence | Report paths, JSON paths, PRs, issues |
| Current facts | Short factual summary with counts and commit hashes |
| Next gate | Exactly one next allowed action |
| Forbidden scope | What must not be done from this node |

### Machine Node Minimum Fields

```json
{
  "node_id": "G2.46",
  "parent_lane": "G",
  "state": "closeout-prepared",
  "source_evidence": [
    "docs/reports/quality/example.md"
  ],
  "generated_artifacts": [
    ".planning/codebase/generated/example.json"
  ],
  "current_head": "",
  "current_head_checked_at_review": "",
  "stale_if_head_mismatch": true,
  "authorized_paths": [],
  "forbidden_paths": [],
  "next_gate": "",
  "source_edits_authorized": false,
  "implementation_target_selected": false
}
```

### Task Card Minimum Fields

```yaml
task:
  id: "pr-000"
  title: "..."

scope:
  allowed_paths: []
  forbidden_paths: []

non_goals: []

acceptance:
  checks: []

governance:
  approval:
    required: false
    approved_by: "main"
    approved_at: "YYYY-MM-DDTHH:MM:SS+08:00"
```

## Suggested State Machine

Recommended standard lifecycle:

1. `observed`
2. `evidence-prepared`
3. `decision-prepared`
4. `authorization-prepared`
5. `approved-for-implementation`
6. `implementation-prepared`
7. `implementation-merged`
8. `closeout-prepared`
9. `closeout-merged`
10. `candidate-refresh-prepared`
11. `archived` or `deferred`

Rules:

- A node must not jump from `evidence-prepared` to source implementation.
- A node must not select a new implementation target during closeout unless the
  closeout explicitly includes a reviewed candidate-selection packet.
- A node must not archive an OpenSpec change until implementation and closeout
  evidence are accepted.
- A node must not delete compatibility surfaces without a separate consumer
  matrix and retention/retirement decision.

## Optimization Recommendations

### 1. Add An Active Gate Register

The long tree is useful historically, but daily work needs a compact table:

| Gate | Lane | Current blocker | Next allowed action | Forbidden action |
|---|---|---|---|---|
| G2.47 | Service lifecycle DI | PR `#186` review/merge | Candidate selection and usefulness triage | Source edits |

This register should only list open gates. It reduces continuation time and
prevents old closed rows from distracting the next agent.

### 2. Generate A Steward Node JSON Index

Create a generated file such as:

`.planning/codebase/generated/steward-tree-nodes-YYYY-MM-DD.json`

This index should be the automation-friendly state source for guards and
dashboards. The Markdown tree remains the human review surface.

### 3. Add A Steward-Tree Guard

A lightweight guard should fail before review if:

- a source evidence path does not exist
- a named OpenSpec change does not exist
- a row claims implementation without an authorization packet
- a merged implementation has no closeout row
- an evidence-only row changes backend source
- a closeout row selects a new implementation target without a candidate packet
- a generated artifact lacks `git_head` or `stale_if_head_mismatch`

### 4. Standardize Closeout Reports

Every closeout report should answer:

- Which PR merged?
- Which commit merged?
- Which exact behavior changed?
- Which compatibility surfaces remain?
- Which tests/smokes passed?
- Which issue labels changed or did not change?
- What is the next gate?
- What is still explicitly unauthorized?

### 5. Split Human Narrative From Automation Fields

Do not make automation parse long prose. Keep stable fields in JSON/YAML and let
Markdown explain the meaning.

Recommended field names:

- `source_edits_authorized`
- `implementation_target_selected`
- `compatibility_retirement_authorized`
- `openspec_changes_authorized`
- `issue_label_changes_authorized`
- `pm2_execution_authorized`
- `stale_if_head_mismatch`

### 6. Keep Graph Memory As Digest Only

Graph memory is useful for cross-session summaries, but it should not become the
truth source. Store concise digests:

- accepted decision
- forbidden scope
- next gate
- PR/issue/commit/report anchors

Current truth should remain in repository artifacts and current code.

### 7. Add A Review Checklist Per Node Type

Different node types need different review questions:

| Node type | Review checklist |
|---|---|
| Evidence | Are facts current? Are stale artifacts labeled? |
| Decision | Does it choose direction without authorizing implementation? |
| Authorization | Are allowed paths, forbidden paths, tests, rollback, and GitNexus gates explicit? |
| Implementation | Does the diff match the authorization exactly? |
| Closeout | Does it record merged result and avoid selecting the next target? |
| Candidate refresh | Does it classify candidates before choosing one? |

### 8. Use PR Numbers As Delivery Anchors, Not Node IDs

PR numbers are useful anchors but unstable for planning before creation. Keep
node IDs independent, then add PR numbers after creation:

```text
G2.46 -> PR #186
```

This avoids renaming documents when a PR number is not known yet.

## Anti-Patterns To Avoid

| Anti-pattern | Result |
|---|---|
| One master plan keeps absorbing every new finding | The plan becomes impossible to execute and review |
| Evidence package contains optional source fix | Later agents treat evidence as implementation authority |
| Candidate scan becomes backlog | Broad or dangerous services get picked by regex |
| Closeout omitted after merge | Next agent cannot tell whether another lane is authorized |
| Compatibility wrapper deleted because active route refs are zero | Tests, exports, or external consumers can break |
| Issue label treated as full state | Architecture gates disappear behind coarse workflow labels |
| Generated artifact lacks commit metadata | Route/OpenAPI/count differences become impossible to interpret |

## Adoption Checklist For Another Project

1. Pick one architecture remediation program, not the whole repository.
2. Create one human steward tree under a planning directory.
3. Define a state legend before creating the first row.
4. Require every row to have one next gate and one forbidden-scope note.
5. Add generated JSON artifacts for counts, inventories, and current-head scans.
6. Add a task card for every PR that changes governance or implementation state.
7. Require closeout after every implementation merge.
8. Keep graph or agent memory as digest only.
9. Review stale evidence before authorizing source changes.
10. Treat compatibility cleanup as a separate decision lane.

## Minimal Starter Template

````markdown
# <Program Name> Steward Tree

> Boundary note: this document coordinates architecture work. It does not
> authorize source edits unless a specific implementation authorization packet
> says so.

## State Legend

| State | Meaning |
|---|---|
| evidence-prepared | Facts collected; no implementation authority |
| decision-prepared | Direction selected; no source edits |
| authorization-prepared | Future write scope prepared for review |
| implementation-merged | Source PR merged |
| closeout-prepared | Merged result and next gate recorded |

## Active Gate Register

| Gate | Lane | Current blocker | Next allowed action | Forbidden action |
|---|---|---|---|---|

## Tree

```text
Program
├── A. Baseline
├── B. Evidence lane
├── C. Decision lane
└── D. Implementation lane
```

## Evidence Ledger

| Artifact | Lane | Current fact | Next gate |
|---|---|---|---|
````

## Current Recommendation For MyStocks

For this project, the immediate next steward-tree improvement should be:

1. Keep PR `#186` as G2.46 closeout/current-head refresh only.
2. After PR `#186` is reviewed and merged, create G2.47 as a dedicated
   candidate-selection and usefulness/ownership triage packet.
3. Add an Active Gate Register to the tree before the next source
   implementation authorization.
4. Start producing a machine-readable steward node index so future guards do
   not need to parse narrative Markdown.
