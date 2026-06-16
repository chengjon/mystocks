# B4.013-GOV-M1 Mainline Alignment Governance Adoption

Date: 2026-06-15

## Scope

Authorized work:

- Adopt the validated `adopt-mainline-alignment-governance` OpenSpec change into core governance entrypoints.
- Add repository-level mainline alignment and visible-result rules.
- Update Agent entry references without duplicating the full standard.
- Add active runtime mainline FUNCTION_TREE/governance metadata.
- Pause residual B4.012 detail/cleanup gates so they do not compete with the active runtime mainline.

Explicitly excluded:

- No source code changes.
- No test changes.
- No API, route, store, UI, PM2, runtime, OpenSpec implementation beyond this governance change, ST-HOLD, or `marketKlineData` changes.
- No external dirty-file cleanup.

## Files Updated

- `architecture/STANDARDS.md`
- `AGENTS.md`
- `CLAUDE.md`
- `docs/FUNCTION_TREE.md`
- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/tree.md`
- `.governance/programs/artdeco-web-design-governance/cards/b4-013-runtime-mainline-bring-up.yaml`
- `openspec/changes/adopt-mainline-alignment-governance/tasks.md`

## Governance Changes

- Added `主线对齐与结果可见准则` to `architecture/STANDARDS.md`.
- Made P0/P2/P3 classification a task admission rule.
- Made visible, reproducible runtime output mandatory for mainline closeout.
- Made usability gates precede detail gates.
- Prohibited premature repair of inactive future feature code.
- Added the five-day rolling mainline cycle and blocker rollover rule.
- Added `B4.013 Runtime Mainline Bring-Up` as the active mainline FUNCTION_TREE governance entry.
- Paused residual B4.012 cleanup/detail gates by transitioning them to `blocked` with an unblock target preserving their prior state.

## B4.012 Gates Paused

- `b4-012-m3-residual-dirty-atlas-rebaseline`
- `b4-012-m3a-tests-residual-domain-audit`
- `b4-012-m3a-b-api-backend-contract-tests-split`
- `b4-012-m3a-d-e2e-frontend-tests-split`
- `b4-012-m3a-e-performance-runtime-security-tests-split`
- `b4-012-m3a-u-untracked-tests-provenance-review`
- `b4-012-m3a-c-adapter-data-source-tests-split`
- `b4-012-m3a-d1-e2e-browser-smoke-authorization`

## Validation

Passed:

- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs scope-check --files ... --root /opt/claude/mystocks_spec`
  - Result: `scope-check: 15 changed file(s) within active authorization`
- `openspec validate adopt-mainline-alignment-governance --strict`
  - Result: `Change 'adopt-mainline-alignment-governance' is valid`
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --root /opt/claude/mystocks_spec`
  - Result: `governance validation passed`
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --steward --root /opt/claude/mystocks_spec`
  - Result: `governance validation passed`
- `git diff --check -- <target governance/docs files>`
  - Result: no output, exit code 0

## Next Step

Start `B4.013-M0 Runtime Mainline No-Source Audit`: verify whether the program starts, pages are reachable, API/store/data flow is continuous, browser console is clean enough for the current path, and smoke evidence exists. Do not start P2/P3 cleanup until the P0 mainline path is runnable.
