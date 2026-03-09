# Root Coverage and Backups Convergence Report

- Date: `2026-03-09`
- Worktree: `dev-repo-hygiene-b1`
- Change: `integrate-repository-hygiene`

## Summary

- Goal: eliminate root-level lifecycle debt for `coverage.json` and `backups/`.
- Before remediation:
  - `errors: 0`
  - `warnings: 15`
- After remediation:
  - `errors: 0`
  - `warnings: 12`

## Changes

- Moved tracked root coverage artifact:
  - `coverage.json` → `reports/coverage/coverage.json`
- Moved tracked historical registry backups:
  - `backups/data_source_registry/*.json` → `archive/backups/data_source_registry/*.json`
- Updated future write targets to avoid regenerating root debt:
  - `pytest.ini` now writes JSON coverage to `reports/coverage/coverage.json`
  - `tests/pytest_runtime_artifacts.py` now cleans stray root `coverage.json`
  - `scripts/dev/cleanup_temp_files.py` now rehomes unexpected root `backups/` into `var/backups/<stamp>/legacy-root-backups`
  - `src/infrastructure/backup_recovery/backup_manager.py` default backup root → `var/backups`
  - `src/infrastructure/backup_recovery/backup_scheduler.py` default backup root → `var/backups`
  - `scripts/sync_sources.py` registry backup target → `var/backups/data_source_registry`
  - `scripts/migrations/migrate_watchlist_to_monitoring.py` default backup dir → `var/backups`
  - `scripts/dev/quality/check_coverage.py` and `scripts/tests/run_e2e_tests.sh` now read/write canonical coverage JSON path

## Evidence

- `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py tests/unit/scripts/test_repository_hygiene_paths.py -q -o addopts=''`
- `openspec validate integrate-repository-hygiene --strict`
- `python scripts/maintenance/check_structure.py --format text`
