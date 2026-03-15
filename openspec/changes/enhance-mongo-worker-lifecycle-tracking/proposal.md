# Change: Enhance Mongo worker lifecycle tracking

## Why
The current Mongo coordination control plane can persist dispatched work items, updates, requests,
and summary views, but it still lacks three operational capabilities that main CLI now needs in
practice:

- a worker receipt/claim signal so main can distinguish "dispatched" from "accepted and started"
- structured plan-item progress so main can see `done / total` instead of only free-form notes
- an explicit submit flow so workers do not stop at local completion without commit/push/review handoff

Without these capabilities, Mongo cannot yet serve as the sole operational source of truth for
active worker execution state.

## What Changes
- Add a worker claim flow that records receipt and moves active work into a real started state
- Add structured plan items under each work item and aggregate plan progress into the summary view
- Add a worker submit flow that records delivery metadata before moving work to `ready_for_review`
- Extend the main CLI board/read model to expose claim, progress, blocker, and delivery summary
- Update worker operating guidance so `TASK.md` maps to an explicit Mongo-backed lifecycle

## Impact
- Affected specs: `symphony-service`
- Affected code: `src/services/maestro/collab/**`, `scripts/runtime/maestro_collab.py`, `scripts/runtime/coordctl.py`, `docs/guides/MONGO_MULTICLI_*`, `TASK.md` templates, related tests
