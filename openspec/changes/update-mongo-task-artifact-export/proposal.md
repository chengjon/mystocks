# Change: Make Mongo the sole task source of truth and export task artifacts

## Why

The current repository still uses `TASK.md` and `TASK-REPORT.md` as live task-carrier artifacts in several worker-facing flows, even though Mongo control-plane commands already exist for assignment, claim, plan, update, and submit.

This keeps the project in a hybrid state where Mongo is treated as the machine-state source of truth, but task definition and execution guidance still require hand-maintained markdown. That contradicts the intended cutover model and makes worker startup dependent on manual file synchronization.

## What Changes

- Make Mongo control-plane records the sole task-definition source for active multi-CLI work.
- Add export commands that render `TASK.md` and `TASK-REPORT.md` as generated snapshots from Mongo state.
- Update the collaboration contract so markdown task artifacts are treated as exported review/readability surfaces rather than hand-authored primary task records.
- Update docs to reflect the Mongo-first / exported-markdown model.

## Impact

- Affected specs:
  - `symphony-service`
- Affected code:
  - `scripts/runtime/maestro_collab.py`
  - `scripts/runtime/coordctl.py`
  - `scripts/runtime/export_collab_snapshots.py`
  - `tests/unit/runtime/test_maestro_coordination_cli.py`
  - `tests/unit/runtime/test_collab_migration_scripts.py`
  - related Mongo collaboration docs
