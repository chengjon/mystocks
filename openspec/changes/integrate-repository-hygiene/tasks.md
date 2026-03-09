# Tasks: integrate-repository-hygiene

## 0. Specification and Planning

- [x] Add OpenSpec proposal, design, and spec deltas for repository hygiene governance
- [x] Add design and implementation plan docs for repository hygiene governance

## 1. Batch 1 — Governance Alignment and Safe Entry Points

> This is the recommended first execution batch. It is intentionally bounded to
> policy alignment, dry-run-first entrypoints, and baseline refresh. It does not
> yet move large groups of repository files.

### 1.1 Baseline and Canonical Targets

- [ ] Refresh `docs/FILE_CLEANUP_TASK.md` to match the current repository baseline
- [ ] Rewrite target locations in `docs/FILE_CLEANUP_TASK.md` to use canonical lifecycle directories:
  - [ ] `docs/`
  - [ ] `reports/`
  - [ ] `archive/`
  - [ ] `var/`
- [ ] Update directory governance policy to allow the canonical lifecycle directories required by the rollout
- [ ] Add or update a focused policy test proving canonical targets such as `archive/`, `reports/`, and `var/` do not trigger root errors once approved

### 1.2 Safe Hygiene Entry Points

- [ ] Upgrade `scripts/maintenance/rotate_logs.sh` to support:
  - [ ] `--dry-run`
  - [ ] canonical archive/runtime targets
  - [ ] human-readable summary output
- [ ] Add a canonical `scripts/maintenance/monitor_file_size.sh` entrypoint that reuses existing Python scanning logic
- [ ] Add or upgrade `scripts/cleanup/auto_cleanup.sh` so destructive actions are opt-in and dry-run is the default safe path
- [ ] Converge or wrap duplicate cleanup and file-size scripts under the canonical entrypoints instead of maintaining parallel flows

### 1.3 Batch 1 Verification

- [ ] Add focused tests for:
  - [ ] cleanup dry-run behavior
  - [ ] log rotation dry-run and archive target resolution
  - [ ] file-size monitoring output and machine-readable format
- [ ] Create initial canonical runtime/report/archive directories without introducing new governance violations
- [ ] Validate Batch 1 with:
  - [ ] `openspec validate integrate-repository-hygiene --strict`
  - [ ] targeted `pytest` for policy / cleanup / rotation / size-monitor scripts
  - [ ] `python scripts/maintenance/check_structure.py --format text`

## 2. Batch 2 — Root Error Remediation

- [ ] Baseline current root `error` findings from `check_structure`
- [ ] Produce a first small remediation batch for root `error` findings
- [ ] Move only bounded runtime artifacts to canonical lifecycle targets
- [ ] Re-run directory governance verification and record the delta in `reports/governance/`

## 3. Batch 3 — Documentation Lifecycle Convergence

- [ ] Produce a migration inventory for stale docs, evidence docs, and historical docs
- [ ] Move one bounded category at a time into `reports/` or `archive/`
- [ ] Update affected documentation workflow/index files after each migration batch
- [ ] Re-run governance checks and keep warning/error deltas auditable
