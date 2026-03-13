# Compatibility Retention Archival Plan

## Purpose

This plan defines how the remaining compatibility-retained assets should be isolated or archived without
breaking active code paths.

The current retained set is:

- `src/adapters/legacy_adapter.py`
- `src/adapters/akshare/legacy_market_data.py`
- `config/sina_finance_only.yaml`
- `config/data_sources/sina_finance.yaml`
- `config/datasource.yaml.example`

## Strategy

Use three different treatments, depending on runtime criticality:

1. `archive-ready`
   For assets that are not in active runtime paths and can move out of `src/` or `config/`.

2. `in-source isolation`
   For assets that still participate in imports and need a compatibility boundary before they can move.

3. `config compatibility hold`
   For configuration files still consumed by scripts or standalone APIs and therefore not safe to move yet.

## Canonical Targets

If and when execution begins, use these targets:

- Non-runtime example code:
  - `archive/code-compatibility/examples/`

- Compatibility code that still needs import stability:
  - `src/**/compat/`

- Compatibility-only config that is still script-driven:
  - `config/compatibility/`

- Example templates for standalone or experimental APIs:
  - `config/templates/`

## Asset Plan

### 1. `src/adapters/legacy_adapter.py`

- Current state:
  - No GitNexus upstream runtime impact.
  - Referenced by `scripts/dev/examples/real_project_application/...part1.py`.
  - Semantically a demo/refactoring sample, not a production adapter.

- Recommended treatment:
  - `archive-ready`

- Proposed destination:
  - `archive/code-compatibility/examples/legacy_adapter.py`

- Preconditions:
  - Update the example script path reference.
  - Confirm no tests import this file directly.

- Execution notes:
  - Move the file to archive.
  - Replace the old path reference in the example script with the archived path or with a short explanatory note.

- Rollback:
  - Restore the file to `src/adapters/legacy_adapter.py`.

### 2. `src/adapters/akshare/legacy_market_data.py`

- Current state:
  - Re-exported by `src/adapters/akshare/__init__.py`.
  - Exists specifically to preserve sync compatibility for old AkShare market overview calls.
  - Runtime impact is low, but import stability still matters.

- Recommended treatment:
  - `in-source isolation`

- Proposed destination:
  - `src/adapters/akshare/compat/legacy_market_data.py`

- Preconditions:
  - Add `src/adapters/akshare/compat/__init__.py`.
  - Keep `src/adapters/akshare/__init__.py` exporting the same public names.
  - Optionally keep a thin compatibility shim at the old module path for one cycle if direct imports exist outside package exports.

- Execution notes:
  - Do not archive directly.
  - First isolate under `compat/`, then observe whether direct file-path imports still exist.
  - Only after one more audit cycle consider moving it to archive.

- Rollback:
  - Move the compat file back to `src/adapters/akshare/legacy_market_data.py`.

### 3. `config/sina_finance_only.yaml`

- Current state:
  - Directly used by `scripts/quick_health_check.sh`.
  - Used by `scripts/tests/legacy/test_sina_integration_final.py` as the main config file.
  - Acts as a narrow compatibility main config.

- Recommended treatment:
  - `config compatibility hold`

- Proposed destination in a later phase:
  - `config/compatibility/sina_finance/main.yaml`

- Preconditions:
  - Update script consumers to the new path.
  - Verify loader behavior remains identical.

- Execution notes:
  - Do not move yet.
  - First mark it as compatibility-only in comments or documentation.
  - Move only when the two known script consumers are updated.

- Rollback:
  - Restore the old file path and script references.

### 4. `config/data_sources/sina_finance.yaml`

- Current state:
  - Loaded indirectly via `config/sina_finance_only.yaml`.
  - Not in the main registry path, but active in the isolated Sina Finance compatibility flow.

- Recommended treatment:
  - `config compatibility hold`

- Proposed destination in a later phase:
  - `config/compatibility/sina_finance/source.yaml`

- Preconditions:
  - Move together with `config/sina_finance_only.yaml`.
  - Update `load_sources` or loader entrypoint accordingly.

- Execution notes:
  - Treat it as part of one compatibility package with `sina_finance_only.yaml`.
  - Do not move independently.

- Rollback:
  - Restore both config files together.

### 5. `config/datasource.yaml.example`

- Current state:
  - Corresponds to `DataSourceRegistry` / `src/api/datasource/routes.py`.
  - That API chain exists and has tests.
  - Not the main Web app runtime path, but still a live standalone management surface.

- Recommended treatment:
  - `config compatibility hold`

- Proposed destination in a later phase:
  - `config/templates/datasource-registry.yaml.example`

- Preconditions:
  - Decide whether `src/api/datasource/routes.py` remains part of supported architecture.
  - Update any docs/tests that refer to the current example path.

- Execution notes:
  - Keep in place until the standalone datasource API is either integrated or formally deprecated.

- Rollback:
  - Restore the template path and any doc references.

## Recommended Execution Order

1. Move `legacy_adapter.py` to archive.
2. Isolate `legacy_market_data.py` into `compat/`.
3. Decide whether the standalone datasource API remains supported.
4. If yes, keep `datasource.yaml.example` but relocate it to `config/templates/`.
5. If the Sina Finance compatibility flow is still needed, move both YAML files together into `config/compatibility/`.

## Guardrails

- Do not move compatibility assets and rename imports in the same batch unless verification is available.
- Prefer one compatibility family per batch:
  - AkShare legacy compatibility
  - Sina Finance compatibility
  - Standalone datasource API compatibility
- After each batch:
  - re-run targeted tests
  - re-scan for old path references
  - update `TASK-REPORT.md`

## Minimum Verification For Execution

- Path reference scan using `rg`
- Syntax validation for touched Python/JS/YAML
- Targeted tests for the affected compatibility family
- Updated inventory entry in `TASK-REPORT.md`
