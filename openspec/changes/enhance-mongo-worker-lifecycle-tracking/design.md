## Context

MyStocks has already introduced a Mongo-backed multi-CLI control plane for work dispatch, updates,
requests, and summary status. That gives main CLI a durable registry, but the current model still
falls short in real usage:

- `dispatched` means "main created the task", not "worker received the task"
- progress is only visible through free-form updates, so main cannot reliably tell whether a worker
  is `1/5`, `3/7`, or effectively blocked
- a worker can finish code changes locally yet still miss the required commit/push/review handoff

The user now wants Mongo to become the single operational source of truth for active worker state.
That requires the control plane to represent the full worker lifecycle, not just assignment and
ad hoc notes.

## Goals

- Let main CLI distinguish "dispatched" from "accepted and started"
- Let workers publish structured task decomposition and completion progress into Mongo
- Let main CLI see concise progress ratios and current focus without reading Markdown by default
- Give workers an explicit end-of-task handoff flow that includes verification, commit, and push
- Keep the model light enough to adopt immediately without disrupting the current worker 1-5 lines

## Non-Goals

- Do not introduce a heavy workflow engine or approval DAG
- Do not replace `TASK.md` / `TASK-REPORT.md` with generated documents in this change
- Do not make database-level per-worker credentials a prerequisite for adoption
- Do not merge this coordination enhancement into the current business-domain worker assignments

## Decisions

### 1. Use `work claim` as the receipt-and-start signal

We will not add a separate persisted `claimed` workflow state. Instead:

- `dispatched` continues to mean "main created and sent the assignment"
- `work claim` records the worker receipt in Mongo and writes the first lifecycle update
- the active work state becomes `in_progress`
- the summary view stores `claimed_by` and `claimed_at`

This keeps the externally visible state machine compact while still preserving the operational fact
that the worker explicitly accepted the task.

### 2. Add a dedicated `work_plan_items` collection

Free-form `work_updates` are useful for narration, but they are not sufficient for deterministic
progress reporting. We will add `work_plan_items` with one record per worker-defined execution step.

Each plan item includes:

- `work_item_id`
- `plan_item_id`
- `title`
- `order`
- `status` (`todo`, `doing`, `done`, `blocked`)
- `evidence_summary`
- `updated_at`

This allows main CLI to compute `done / total`, identify the current focus item, and detect blocked
execution without parsing prose.

### 3. Keep delivery submission lightweight and append-only

We will not create a separate `work_submissions` collection in this change. Instead:

- `work submit` writes a structured lifecycle update with delivery metadata
- the update includes commit SHA, branch, optional remote, verification summary, and handoff summary
- the summary view is refreshed with `submitted_at`, `delivery_commit`, and `delivery_branch`
- successful submit moves the derived state to `ready_for_review`

This keeps the persistence model smaller while still giving main enough information to review the
delivered work.

### 4. Main reads an aggregated board view, not raw collections by default

Main CLI should not need to manually join raw collections during day-to-day coordination. The
summary/read model should expose the operational board directly.

The aggregated board row will include:

- work identity: `work_item_id`, `branch`, `owner_cli`
- lifecycle: `status`, `claimed_by`, `claimed_at`, `updated_at`
- progress: `plan_total`, `plan_done`, `progress_percent`, `current_focus`
- blocking: `has_pending_request`, `blocker`
- delivery: `submitted_at`, `delivery_commit`, `delivery_branch`
- narrative: `latest_update`

### 5. `TASK.md` remains the worker entrypoint, but Mongo becomes the runtime fact source

We will keep the user-facing startup instruction unchanged:

`请按你当前 worktree 的 TASK.md 开工。`

But the task contract will explicitly guide the worker through the Mongo lifecycle:

1. read the assigned work item from Mongo
2. `work claim`
3. publish initial plan items
4. update progress as plan items advance
5. record verification evidence and update `TASK-REPORT.md`
6. commit, push, and `work submit`

This preserves the simple operator experience while removing ambiguity for workers.

## Data Model Changes

### New collection

`work_plan_items`

Suggested indexes:

- unique: `(work_item_id, plan_item_id)`
- sort/read: `(work_item_id, order)`
- summary refresh aid: `(work_item_id, status, updated_at desc)`

### Extended summary view

`worker_status_views` adds:

- `claimed_by: str | null`
- `claimed_at: datetime | null`
- `plan_total: int`
- `plan_done: int`
- `progress_percent: int`
- `current_focus: str | null`
- `submitted_at: datetime | null`
- `delivery_commit: str | null`
- `delivery_branch: str | null`

### Structured update kinds

`work_updates.details` becomes meaningful rather than always empty. The first supported `kind`
values are:

- `claim`
- `progress`
- `submit`

## CLI Surface

### Worker commands

- `coordctl work claim <work_item_id> --actor-cli <worker_cli> --summary "..."`
- `coordctl plan add <work_item_id> --actor-cli <worker_cli> --title "..." --order <n>`
- `coordctl plan mark <work_item_id> <plan_item_id> --actor-cli <worker_cli> --status done --evidence "..."`
- `coordctl work submit <work_item_id> --actor-cli <worker_cli> --commit <sha> --branch <branch> --summary "..." [--remote origin] [--verify "..."]`

### Main commands

- `coordctl work board --active-only --output json|text`
- `coordctl work show <work_item_id> --include-plan --output json`

## Summary Refresh Rules

The summary view must refresh after:

- `work_item` create or transition
- `work claim`
- `plan add`
- `plan mark`
- `update add`
- `request create`
- `request review`
- `work submit`

Derived fields should follow these rules:

- `status`: latest lifecycle status from structured updates, else `work_item.status`
- `plan_total`: count of plan items for the work item
- `plan_done`: count of plan items whose status is `done`
- `progress_percent`: `floor(plan_done * 100 / plan_total)` when `plan_total > 0`, else `0`
- `current_focus`: first `doing` item by order, else first non-`done` item by order, else `null`

## Rollout

This change should be implemented as a separate coordination workstream. It should not be pushed
into worker 1-5 business scopes.

Recommended rollout:

1. implement storage and CLI support
2. update worker `TASK.md` templates and Mongo operation guide
3. start using the lifecycle on new coordination tasks
4. optionally backfill current active tasks by issuing `work claim` and initial plan items

## Risks

### Risk: Worker friction increases

Workers now need to perform a few more control-plane actions.

Mitigation:

- keep the CLI sequence short and explicit
- embed exact commands in `TASK.md`
- use a single `work submit` command to bundle final handoff metadata

### Risk: Plan items become stale if workers ignore them

Mitigation:

- make plan publication part of the required startup flow
- surface `plan_total = 0` on the main board so missing decomposition is obvious

### Risk: The board and Markdown drift

Mitigation:

- treat Mongo as runtime fact source
- keep `TASK-REPORT.md` as evidence narrative, not status authority
