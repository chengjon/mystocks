# Tasks: integrate-repository-hygiene

## 0. Specification and Planning

- [x] Add OpenSpec proposal, design, and spec deltas for repository hygiene governance
- [x] Add design and implementation plan docs for repository hygiene governance

## 1. Batch 1 — Governance Alignment and Safe Entry Points

> This is the recommended first execution batch. It is intentionally bounded to
> policy alignment, dry-run-first entrypoints, and baseline refresh. It does not
> yet move large groups of repository files.

### 1.1 Baseline and Canonical Targets

- [x] Refresh `docs/FILE_CLEANUP_TASK.md` to match the current repository baseline
- [x] Rewrite target locations in `docs/FILE_CLEANUP_TASK.md` to use canonical lifecycle directories:
  - [x] `docs/`
  - [x] `reports/`
  - [x] `archive/`
  - [x] `var/`
- [x] Update directory governance policy to allow the canonical lifecycle directories required by the rollout
- [x] Add or update a focused policy test proving canonical targets such as `archive/`, `reports/`, and `var/` do not trigger root errors once approved

### 1.2 Safe Hygiene Entry Points

- [x] Upgrade `scripts/maintenance/rotate_logs.sh` to support:
  - [x] `--dry-run`
  - [x] canonical archive/runtime targets
  - [x] human-readable summary output
- [x] Add a canonical `scripts/maintenance/monitor_file_size.sh` entrypoint that reuses existing Python scanning logic
- [x] Add or upgrade `scripts/cleanup/auto_cleanup.sh` so destructive actions are opt-in and dry-run is the default safe path
- [x] Converge or wrap duplicate cleanup and file-size scripts under the canonical entrypoints instead of maintaining parallel flows

### 1.3 Batch 1 Verification

- [x] Add focused tests for:
  - [x] cleanup dry-run behavior
  - [x] log rotation dry-run and archive target resolution
  - [x] file-size monitoring output and machine-readable format
- [x] Create initial canonical runtime/report/archive directories without introducing new governance violations
- [x] Validate Batch 1 with:
  - [x] `openspec validate integrate-repository-hygiene --strict`
  - [x] targeted `pytest` for policy / cleanup / rotation / size-monitor scripts
  - [x] `python scripts/maintenance/check_structure.py --format text`

## 2. Batch 2 — Root Error Remediation

- [x] Baseline current root `error` findings from `check_structure`
- [x] Produce a first small remediation batch for root `error` findings
- [x] Move only bounded runtime artifacts to canonical lifecycle targets
- [x] Re-run directory governance verification and record the delta in `reports/governance/`

## 3. Batch 3 — Documentation Lifecycle Convergence

- [x] Produce a migration inventory for stale docs, evidence docs, and historical docs
- [x] Move one bounded category at a time into `reports/` or `archive/`
- [x] Update affected documentation workflow/index files after each migration batch
- [x] Re-run governance checks and keep warning/error deltas auditable
