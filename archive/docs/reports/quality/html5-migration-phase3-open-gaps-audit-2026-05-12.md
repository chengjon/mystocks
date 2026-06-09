# HTML5 Migration Phase 3 Open Gaps Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: Phase 3 integration / validation / deployment / training gaps
Scope: Desktop-only, repo-local audit only

## Decision

Several Phase 3 items remain open by design.

This batch records the residual Phase 3 boundary after the repo-local HTML5 runtime and accessibility sweeps. The repo has supporting guides, local acceptance harnesses, and several closed surfacing points, but the remaining Phase 3 items are mostly external validation, rollout, deployment, or execution records that cannot be fabricated from code or docs alone.

## Evidence Checked

Commands:

```bash
sed -n '541,735p' openspec/changes/implement-html5-migration-experience-optimization/tasks.md
find docs/guides/frontend -maxdepth 1 -type f | rg 'HTML5_RUNTIME|HTML5_MIGRATION'
find docs/reports/tasks -maxdepth 1 -type f | rg 'html5-runtime'
```

Observed repo facts:

- `3.1.1` and `3.1.2` remain open because they require real service-worker-controlled online/offline route matrices and worker/IndexedDB data-flow observations, not just templates or partial probes.
- `3.2.1` and `3.2.2` remain open because they require actual offline matrix / cross-browser execution records.
- `3.2.4` remains open because the worker manager is still a placeholder path and the worker protocol asset path is incomplete for a real worker benchmark.
- `3.3.2` and `3.3.3` remain open because they require real rollout records, rollback/monitoring execution, and sign-off evidence.
- `3.4.4` remains open because it requires actual training or knowledge-sharing execution records.
- `docs/guides/frontend/HTML5_RUNTIME_*` files now cover the materials layer, but the materials layer is not the same as execution evidence.
- `docs/reports/tasks/2026-05-10-html5-runtime-local-acceptance.md` and `web/frontend/tests/html5-runtime-acceptance.test.ts` provide useful repo-local acceptance attempts, but they do not close every Phase 3 open gap.

## Gap Summary

The Phase 3 remainder is mostly not a coding backlog. It is a validation, rollout, and execution backlog.

The repo has enough evidence to describe the boundary truth, but not enough to claim the remaining items are complete. In particular, external acceptance, gray release, production deployment, rollback drills, and training sessions need real execution records.

## Task Disposition

Keep the remaining Phase 3 open items unchecked until their corresponding real execution records exist.

Minimum future evidence should include:

- Service-worker-controlled online/offline route matrix results for `3.1.1` / `3.2.1`.
- Cross-browser PWA execution records for `3.2.2`.
- Real worker orchestration and benchmark evidence for `3.2.4`.
- Rollout / rollback / monitoring execution evidence for `3.3.2` / `3.3.3`.
- A real training or technical-sharing record for `3.4.4`.
