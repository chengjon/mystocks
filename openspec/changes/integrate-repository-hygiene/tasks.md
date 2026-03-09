# Tasks: integrate-repository-hygiene

- [ ] Add OpenSpec proposal, design, and spec deltas for repository hygiene governance
- [ ] Refresh `docs/FILE_CLEANUP_TASK.md` to match the current repository baseline and canonical targets
- [ ] Update directory governance policy to allow the canonical lifecycle directories required by the rollout
- [ ] Add or upgrade the unified hygiene entrypoints:
  - [ ] `scripts/cleanup/auto_cleanup.sh`
  - [ ] `scripts/maintenance/rotate_logs.sh`
  - [ ] `scripts/maintenance/monitor_file_size.sh`
- [ ] Converge or wrap duplicate cleanup and file-size scripts under the canonical entrypoints
- [ ] Add focused tests for cleanup dry-run behavior, log rotation, and file-size monitoring
- [ ] Create initial canonical runtime/report/archive directories without introducing new governance violations
- [ ] Produce a first remediation batch for current root `error` findings
- [ ] Validate with targeted pytest and `openspec validate integrate-repository-hygiene --strict`
