# B4.012-M2b-B2-C-B sync OpenCode model catalog contract drift no-source audit

Date: 2026-06-14
Branch: `wip/root-dirty-20260403`
Mode: `no-source`
Node: `b4-012-sync-opencode-model-catalog-contract-drift-audit`
Parent: `b4-012-sync-opencode-model-catalog-restore-authorization`

## Scope

This audit investigates the focused test failure left after `B4.012-M2b-B2-C-A` restored:

- `scripts/opencode/sync_opencode_model_catalog.py`

to `HEAD`.

Read-only evidence paths:

- `scripts/opencode/sync_opencode_model_catalog.py`
- `tests/unit/test_sync_opencode_model_catalog.py`
- `opencode.json`
- `.config/opencode/model/model-catalog.json`
- `.config/oh-my-opencode.noco.json`
- `.config/opencode/model/model-stack.env`
- `.config/opencode/model/main.model`
- `.config/opencode/model/small.model`
- `.config/opencode/model/asxs.base_url`

## Boundary

This package is no-source only. It does not modify source, tests, config, OpenSpec, frontend, API, ST-HOLD, marketKlineData, or external dirty paths.

## Current State

- Current HEAD at audit time: `726be97e2 B4.012-M2b-B2-C-A: block OpenCode model restore on contract drift`
- `scripts/opencode/sync_opencode_model_catalog.py`: clean, byte-equivalent to `HEAD`
- `tests/unit/test_sync_opencode_model_catalog.py`: clean
- Related OMC sibling files and tests: clean
- Staged files at audit start: none

## Reproduction

Command:

```bash
env PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_sync_opencode_model_catalog.py -q --no-cov -p no:cacheprovider
```

Observed result from the restore package:

- `4 failed in 0.42s`
- `apply_common` raises `KeyError: 'enabled_providers'`
- `test_main_updates_model_files_from_catalog` raises `KeyError: 'server'`

## Root Cause Evidence

Current `apply_common` requires a top-level catalog key:

- `config["enabled_providers"] = catalog["enabled_providers"]`

It does not currently write or preserve/default `config["server"]["port"]`.

Current `_minimal_catalog()` in the paired test contains only:

- `external_models.gmn`
- `external_models.glm`

It does not contain:

- `enabled_providers`
- `defaults`
- `server`
- `omo_agents`
- `opencode_free_models`

History shows a real contract drift:

- In commit `4462a820aa`, `apply_common` used `catalog.get("enabled_providers", ...)` and set `server.port` to `11000` when missing or invalid.
- In commit `76f195f69f`, `apply_common` changed to require `catalog["enabled_providers"]`, build provider config directly, accept `plugin_list`, and no longer set `server.port`.
- The paired tests still assert the older `server.port` behavior and use the older minimal fixture shape.

## Runtime Configuration Evidence

Local OpenCode model catalog:

- Path: `.config/opencode/model/model-catalog.json`
- Top-level keys: `defaults`, `enabled_providers`, `external_models`, `omo_agents`, `opencode_free_models`, `source`, `version`
- `enabled_providers`: `opencode`, `glm`, `asxs`
- `external_models`: `glm`, `asxs`
- No `gmn`

Project `opencode.json`:

- Exists
- `enabled_providers`: `opencode`, `glm`, `asxs`
- Provider keys: `opencode`, `glm`, `asxs`
- `server.port`: `11000`
- `model` and `small_model` point to `.config/opencode/model/*.model`

Local OMO config:

- Path: `.config/oh-my-opencode.noco.json`
- `enabled_providers`: `opencode`, `glm`, `asxs`
- Provider keys: `opencode`, `glm`, `asxs`
- No `server`

Model refs:

- `.config/opencode/model/main.model`: `glm/glm-5.1`
- `.config/opencode/model/small.model`: `opencode/glm-5-free`
- `.config/opencode/model/asxs.base_url`: exists
- `.config/opencode/model/gmn.base_url`: absent

## Interpretation

This is not just a stale test fixture and not just a failed restore package.

The current tracked source/test pair still reflects an older `gmn/glm` contract, while local runtime configuration has already moved to an `opencode/glm/asxs` contract. The prior dirty script was an attempted ASXS provider migration, but it also failed the current tests and removed behavior that tests still expect.

Therefore the next package should not silently choose one side. It needs explicit source/test contract standardization.

## Recommended Direction

Prepare a source/test authorization package for a minimal contract standardization:

Allowed source/test paths:

- `scripts/opencode/sync_opencode_model_catalog.py`
- `tests/unit/test_sync_opencode_model_catalog.py`

Recommended implementation questions for that package:

1. Should tracked source follow the current local `asxs` model catalog?
2. Should `apply_common` continue to preserve/default `server.port=11000`, at least for project `opencode.json`?
3. Should tests update fixtures from `gmn/glm` to `opencode/glm/asxs`, or preserve a legacy `gmn` test path separately?
4. Should generated/local config files remain evidence only, or should any tracked config/docs be updated in a separate config/docs package?

Recommended minimal acceptance gates:

- `python -m py_compile scripts/opencode/sync_opencode_model_catalog.py`
- `env PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_sync_opencode_model_catalog.py -q --no-cov -p no:cacheprovider`
- GitNexus impact on `apply_common` and `apply_omo_specific`
- GitNexus `verify-staged` and `detect-changes --scope staged`
- OPENDOG verification blocker count remains 0

## Non-Goals

- Do not modify OMC sibling script or OMC test.
- Do not alter docs/guides, OpenSpec, frontend, API, ST-HOLD, marketKlineData, or unrelated dirty paths in this no-source package.
- Do not accept the prior dirty ASXS diff without tests.
- Do not hide generated/local config changes inside the source/test package unless explicitly authorized later.

## Decision

Prepare a separate source/test authorization node for `B4.012-M2b-B2-C-B-A sync OpenCode model catalog contract standardization`.

This no-source node does not unblock `B4.012-M2b-B2-C-A` by itself. The blocked restore node should remain blocked until a source/test contract package either updates the contract and tests or provides a narrower accepted fix.
