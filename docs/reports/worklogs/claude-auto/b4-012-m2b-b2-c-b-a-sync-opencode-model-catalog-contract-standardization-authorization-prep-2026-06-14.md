# B4.012-M2b-B2-C-B-A sync OpenCode model catalog contract standardization authorization prep

Date: 2026-06-14
Branch: `wip/root-dirty-20260403`
Mode: `authorization-prepared`
Node: `b4-012-sync-opencode-model-catalog-contract-standardization-authorization`
Parent decision: `b4-012-sync-opencode-model-catalog-contract-drift-audit`

## Source Decision

This authorization prep is based on:

- `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-c-b-sync-opencode-model-catalog-contract-drift-no-source-2026-06-14.md`

The C-B no-source audit found that the restore-only package cleared the dirty script diff, but the focused paired test still fails 4/4 because tracked source, tracked test, and local runtime configuration disagree about the OpenCode model catalog contract.

## Current Evidence

- Current HEAD when prepared: `726be97e2 B4.012-M2b-B2-C-A: block OpenCode model restore on contract drift`
- `scripts/opencode/sync_opencode_model_catalog.py`: clean and byte-equivalent to `HEAD`
- `tests/unit/test_sync_opencode_model_catalog.py`: clean
- Focused test: `4 failed in 0.42s`
- Root causes:
  - `apply_common` requires `catalog["enabled_providers"]`
  - `_minimal_catalog()` does not include `enabled_providers`
  - `apply_common` no longer writes/defaults `server.port`
  - paired tests still assert `server.port` behavior
  - local runtime config is `opencode/glm/asxs`, while tracked tests still assert `gmn/glm`

## Allowed Paths

Future implementation is limited to:

- `scripts/opencode/sync_opencode_model_catalog.py`
- `tests/unit/test_sync_opencode_model_catalog.py`
- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/tree.md`
- `.governance/programs/artdeco-web-design-governance/cards/b4-012-sync-opencode-model-catalog-contract-standardization-authorization.yaml`
- `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-c-b-a-sync-opencode-model-catalog-contract-standardization-authorization-prep-2026-06-14.md`

## Explicit Non-Goals

- Do not modify `scripts/opencode/sync_omc_model_catalog.py`.
- Do not modify `tests/unit/test_sync_omc_model_catalog.py`.
- Do not modify `opencode.json`.
- Do not modify `.config/opencode/*`.
- Do not modify docs/guides, OpenSpec, frontend, API, ST-HOLD, marketKlineData, or unrelated dirty paths.
- Do not introduce a broad ASXS migration outside the minimal source/test contract needed for `sync_opencode_model_catalog.py` focused tests.

## Commit Gate For This Authorization Prep

- Exact staged allowlist only.
- No source or test file staged during authorization prep.
- `git diff --cached --check` passes.
- GitNexus staged review reports low or no process impact.
- OPENDOG verification reports no cleanup/refactor blockers.

## Future Implementation Gate

If the user approves source/test implementation, the package must:

- Run GitNexus impact before editing mapped symbols such as `apply_common` and `apply_omo_specific`.
- Run `python -m py_compile scripts/opencode/sync_opencode_model_catalog.py`.
- Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_sync_opencode_model_catalog.py -q --no-cov -p no:cacheprovider
```

- Keep staged files within the allowed paths.
- Run `git diff --cached --check`.
- Run GitNexus `verify-staged` and `detect-changes --scope staged`.
- Record whether the accepted contract is `opencode/glm/asxs` or a narrower compatibility fix.

## Boundary Confirmation

This package prepares source/test authorization only. It does not authorize implementation until the user explicitly approves and the node reaches `approved-for-implementation`.
