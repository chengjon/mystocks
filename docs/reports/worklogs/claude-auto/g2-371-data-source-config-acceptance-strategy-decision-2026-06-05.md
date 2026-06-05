# G2.371 Data Source Config Acceptance Strategy Decision

## Node

- Node: `G2.371`
- Title: `data source config acceptance strategy decision`
- Date: `2026-06-05`
- Branch: `wip/root-dirty-20260403`
- HEAD observed: `3b892167c`
- Mode: `no-source`
- `source_edit_authority`: `false`
- Parent evidence:
  - `G2.368 data source config residual inventory`
  - `G2.369 data source config dirty-state reconciliation`
  - `G2.370 data source config acceptance authorization preflight`

## Authorization Boundary

This node selects the strategy for a possible later source-authorized acceptance package.

Authorized:

- choose between the two strategies identified by G2.370;
- define package boundaries;
- define non-goals and future gates.

Not authorized:

- source edits;
- test edits;
- accepting dirty hunks;
- restoring dirty hunks;
- deleting or restoring `data_source_config.old.py`;
- staging files;
- committing files.

## Parent Evidence Freshness

G2.370 recorded parent evidence at `d55418ad4`.

Current HEAD is `3b892167c`.

Because the parent evidence head differs from current HEAD, this node re-ran the minimal current-state checks before making a strategy decision.

## Current-State Recheck

### Import Smoke

Command:

```bash
PYTHONPATH=/opt/claude/mystocks_spec/web/backend:/opt/claude/mystocks_spec python - <<'PY'
import importlib
module = importlib.import_module("app.api.data_source_config")
print("import app.api.data_source_config: ok")
print("router routes:", len(getattr(module, "router").routes))
print("has settings:", hasattr(module, "settings"))
print("router response keys:", sorted(getattr(module, "router").responses.keys()))
PY
```

Observed result:

```text
import app.api.data_source_config: ok
router routes: 9
has settings: False
router response keys: [400, 404, 409, 500]
```

### Focused File Test

Command:

```bash
pytest tests/api/file_tests/test_data_source_config_api.py -q --no-cov
```

Observed result:

```text
3 failed, 7 passed, 13 warnings
```

Failing tests remain:

| Test | Failure |
| --- | --- |
| `test_get_current_user_returns_system_in_testing_mode` | `AttributeError: module 'app.api.data_source_config' has no attribute 'settings'` |
| `test_get_current_user_rejects_missing_authorization_outside_testing` | `AttributeError: module 'app.api.data_source_config' has no attribute 'settings'` |
| `test_router_response_descriptions_include_success_and_conflict` | `KeyError: 200` |

Current-state interpretation:

- The dirty module is importable.
- The active router still has 9 routes.
- The public module contract expected by the focused file test is not satisfied.
- `router.responses` currently exposes only the default error response keys, not the success keys asserted by the test.
- The same acceptance blocker observed in G2.370 remains true at `3b892167c`.

## Strategy Options

| Strategy | Meaning | Benefit | Cost/Risk |
| --- | --- | --- | --- |
| Strategy A: preserve public module contract | Keep `app.api.data_source_config` exposing the contract expected by existing file tests while retaining safe import cleanup where possible | minimal behavioral movement; treats focused tests as contract guard | may require route module to re-export or own some helper symbols |
| Strategy B: accept helper-owned boundary | Treat `_data_source_config_responses.py` as the owner of router/auth/config helpers and update tests around that boundary | cleaner ownership if intentionally designed | broader contract move; test rewrite required; higher chance of hiding API startup/docs regression |

## Decision

Chosen strategy:

`Strategy A: preserve public module contract`

Reason:

- The focused file test failures are useful contract evidence, not noise.
- The active API module is expected to remain the import boundary for route tests and API startup checks.
- The current dirty state moved `settings` and router ownership into `_data_source_config_responses.py`, but did not update tests or prove that this is the intended new boundary.
- Strategy A keeps the later source-authorized package narrow.
- Strategy A avoids turning a small acceptance package into a design rewrite.

Rejected strategy:

`Strategy B: accept helper-owned boundary`

Reason:

- It requires test edits to bless a new ownership boundary.
- It broadens `_data_source_config_responses.py` from response-doc helper into router/auth/config helper owner.
- That move may be valid only after a separate design authorization.
- It is too large for the current dirty-state acceptance path.

## Package Boundary

### Later Small Acceptance Package

If source/test authority is granted later, the small package may include only:

| File | Allowed purpose |
| --- | --- |
| `web/backend/app/api/data_source_config.py` | preserve public module contract, keep import smoke passing, retain safe import cleanup if tests pass |
| `web/backend/app/api/_data_source_config_responses.py` | keep response constants/helper behavior aligned with route module contract |
| `tests/api/file_tests/test_data_source_config_api.py` | only update if needed to reflect preserved public contract or remove stale import |

### Explicitly Excluded

| File | Decision |
| --- | --- |
| `web/backend/app/api/data_source_config.old.py` | excluded from small package |

The legacy file deletion remains blocked unless a separate retirement gate proves exit criteria.

## Non-Goals

The next source-authorized package, if approved, must not:

- delete `data_source_config.old.py`;
- rewrite the route API surface;
- rewrite OpenAPI semantics beyond what the current contract requires;
- migrate validators or lifecycle hooks as incidental cleanup;
- broaden the response helper into a general route/auth/config owner without separate design approval;
- touch unrelated data-source registry/factory modules.

## Required Future Gates

Before any source edit:

| Gate | Requirement |
| --- | --- |
| GitNexus refresh | If stale, run direct `gitnexus analyze`, not `npx gitnexus analyze` |
| GitNexus impact | Run impact on any edited symbol, at minimum `get_current_user`, `router`, and edited route/helper symbols |
| Risk handling | Warn before proceeding if impact is HIGH or CRITICAL |

After source/test edits:

| Gate | Command / Evidence |
| --- | --- |
| Import smoke | import `app.api.data_source_config`, confirm 9 routes and expected contract |
| Focused file test | `pytest tests/api/file_tests/test_data_source_config_api.py -q --no-cov` |
| Route-doc slice | run targeted `web/backend/tests/test_health_route_conflicts.py` cases only if response docs or examples are changed |
| Diff hygiene | `git diff --check` |
| Pre-commit graph check | `gitnexus detect_changes` before commit |

## Recommended Next Node

Recommended next node:

`G2.372 data source config Strategy A source authorization / source-authorized`

Required authorization shape:

- `source_edit_authority=true`;
- `test_edit_authority=true`;
- scope limited to the small package files listed above;
- `data_source_config.old.py` deletion explicitly excluded;
- use Strategy A as the implementation direction;
- run the focused gates listed in this report.

Alternative if source authorization is not granted:

`G2.372 data source config legacy-retirement evidence inventory / no-source`

That alternative should only inspect whether `data_source_config.old.py` has sufficient exit evidence for a later deletion gate.

## Closeout

G2.371 is complete as a no-source strategy decision node.

Decision:

- choose Strategy A;
- preserve `app.api.data_source_config` as the public route module contract;
- do not accept the current dirty state as-is;
- do not accept `data_source_config.old.py` deletion;
- require explicit source/test authorization before implementation.
