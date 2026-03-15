## 1. Control Plane Model
- [x] 1.1 Add `work_plan_items` storage models, indexes, and store methods
- [x] 1.2 Extend `worker_status_views` and related Pydantic models with claim, progress, and delivery fields
- [x] 1.3 Define structured update detail payloads for `claim`, `progress`, and `submit`

## 2. Coordination Service
- [x] 2.1 Add service operations for `claim`, plan item create/update, and `submit`
- [x] 2.2 Refresh summary aggregation from work items, plan items, requests, and lifecycle updates
- [x] 2.3 Enforce worker ownership boundaries for plan and submit operations

## 3. CLI Surface
- [x] 3.1 Add worker-facing commands: `work claim`, `plan add`, `plan mark`, `work submit`
- [x] 3.2 Add main-facing board/read commands: `work board`, `work show --include-plan`
- [x] 3.3 Return stable JSON/text outputs for the new commands

## 4. Guidance And Templates
- [x] 4.1 Update Mongo multi-CLI operation guide and checklist with the new lifecycle
- [x] 4.2 Update root `TASK.md` template content so workers follow claim -> plan -> submit flow
- [x] 4.3 Clarify that Mongo is the runtime fact source and `TASK-REPORT.md` is evidence/handoff context

## 5. Verification
- [x] 5.1 Add unit tests for claim, plan progress aggregation, submit handling, and authorization
- [x] 5.2 Add CLI tests for board/read and worker lifecycle commands
- [x] 5.3 Run `openspec validate enhance-mongo-worker-lifecycle-tracking --strict`
- [x] 5.4 Run `git diff --check`
