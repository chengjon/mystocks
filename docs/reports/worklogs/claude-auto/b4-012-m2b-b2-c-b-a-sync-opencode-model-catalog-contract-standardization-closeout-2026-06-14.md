# B4.012-M2b-B2-C-B-A sync OpenCode model catalog contract standardization closeout

Date: 2026-06-14
Node: `b4-012-sync-opencode-model-catalog-contract-standardization-authorization`
Mode: source-authorized implementation closeout

## Scope

This package closes the contract drift found after restoring `scripts/opencode/sync_opencode_model_catalog.py` to tracked HEAD.

Allowed implementation file:

- `scripts/opencode/sync_opencode_model_catalog.py`

No test file changes were required because the existing focused unit tests already captured the missing compatibility contract.

## Implementation

The script now preserves the legacy-compatible behavior expected by the focused unit contract:

- `enabled_providers` falls back to `["opencode", "gmn", "glm"]` when an older/minimal catalog omits the key.
- `server.port` is created with default `11000` when `server` is missing or malformed.
- Valid integer `server.port` values are preserved.
- Boolean and non-integer port values are treated as invalid and reset to `11000`.

This is intentionally narrow. It does not alter runtime config files, docs/guides, OMC sync tooling, frontend, API, OpenSpec, ST-HOLD, marketKlineData, or external dirty paths.

## Verification

Executed from `/opt/claude/mystocks_spec`:

- `env PYTHONDONTWRITEBYTECODE=1 python -m py_compile scripts/opencode/sync_opencode_model_catalog.py`
  - Result: passed.
- `env PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_sync_opencode_model_catalog.py -q --no-cov -p no:cacheprovider`
  - Result: 4 passed in 0.29s.

## GitNexus Impact

Pre-edit impact checks were run for the touched symbols:

- `build_provider_configs`: LOW risk; upstream callers limited to `apply_common -> main`; affected processes: 0.
- `apply_common`: LOW risk; upstream caller limited to `main`; affected processes: 0.

## Disposition

`B4.012-M2b-B2-C-B-A` can close once staged scope, GitNexus staged verification, OPENDOG advisory verification, and post-commit GitNexus index refresh complete.
