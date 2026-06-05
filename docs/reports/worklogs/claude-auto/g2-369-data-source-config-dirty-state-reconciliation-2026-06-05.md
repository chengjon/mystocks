# G2.369 Data Source Config Dirty-State Reconciliation

## Node

- Node: `G2.369`
- Title: `data source config dirty-state reconciliation`
- Date: `2026-06-05`
- Branch: `wip/root-dirty-20260403`
- HEAD observed: `d55418ad4`
- Mode: `no-source`
- `source_edit_authority`: `false`
- Parent evidence: `G2.368 data source config residual inventory`

## Authorization Boundary

This node reconciles the already-dirty `data_source_config` surface as evidence only.

Authorized:

- classify existing dirty hunks;
- compare the current dirty shape with active route/helper/test responsibilities;
- identify whether any dirty hunk can be accepted under no-source governance;
- recommend the next gate.

Not authorized:

- source edits;
- test edits;
- accepting or reverting dirty hunks;
- staging files;
- committing files;
- deleting or restoring legacy files;
- changing OpenAPI examples, response models, route semantics, or request schemas.

## Project Rules Applied

- `architecture/STANDARDS.md` remains the shared-rule source of truth.
- "Unused" or "old" is not enough to authorize deletion.
- Existing dirty state is not proof of prior approval.
- Contract-bearing route/helper/test changes require explicit source/test authority.
- Function-tree governance does not authorize source edits from evidence or decision-prepared states.
- GitNexus stale-index handling must use direct `gitnexus analyze`; the previous node refreshed the index with direct `gitnexus analyze --index-only --wal-checkpoint-threshold 67108864`, not `npx`.

## Scoped Dirty Baseline

Observed scoped dirty status:

```text
M tests/api/file_tests/test_data_source_config_api.py
 M web/backend/app/api/_data_source_config_responses.py
 D web/backend/app/api/data_source_config.old.py
 M web/backend/app/api/data_source_config.py
```

Observed scoped name-status:

```text
M	tests/api/file_tests/test_data_source_config_api.py
M	web/backend/app/api/_data_source_config_responses.py
D	web/backend/app/api/data_source_config.old.py
M	web/backend/app/api/data_source_config.py
```

No files above are accepted, reverted, staged, or committed by this node.

## Diff Summary

| File | Diff shape | High-signal classification |
| --- | ---: | --- |
| `tests/api/file_tests/test_data_source_config_api.py` | `+0 / -1`, 1 hunk | test import cleanup candidate |
| `web/backend/app/api/_data_source_config_responses.py` | `+9 / -2`, 2 hunks | helper now carries imports moved out of route module |
| `web/backend/app/api/data_source_config.old.py` | `+0 / -694`, 1 hunk | full legacy route file deletion candidate |
| `web/backend/app/api/data_source_config.py` | `+6 / -9`, 9 hunks | route module import tightening and relative helper import |

## File-by-File Reconciliation

### `tests/api/file_tests/test_data_source_config_api.py`

Observed dirty hunk:

- removes `from types import SimpleNamespace`.

Interpretation:

- This is likely a stale import cleanup candidate.
- It is low complexity by itself.
- It is still a test edit and cannot be accepted under this no-source node.

Disposition:

| Question | Decision |
| --- | --- |
| Can G2.369 accept it? | No |
| Is it a plausible source-authorized acceptance candidate later? | Yes |
| Required later gate | focused file-test run plus source/test authority |

### `web/backend/app/api/data_source_config.py`

Observed dirty hunks:

- narrows `from typing import Any, Dict, Optional` to `from typing import Optional`;
- removes route-module imports for:
  - `YAML_DATA_SOURCES_REGISTRY_PATH`;
  - `APIRouter`;
  - `Header`;
  - `settings`;
  - `BusinessException`;
  - `create_error_response`;
  - `verify_token`;
- switches response helper import from a non-relative form to:
  - `from ._data_source_config_responses import (...)`.

Current-use check:

| Name | Current route module count |
| --- | ---: |
| `YAML_DATA_SOURCES_REGISTRY_PATH` | 0 |
| `APIRouter` | 0 |
| `Header` | 0 |
| `settings` | 0 |
| `BusinessException` | 0 |
| `ErrorCodes` | 0 |
| `create_error_response` | 0 |
| `verify_token` | 0 |
| `Any` | 0 |
| `Dict` | 0 |
| `Optional` | 5 |

Interpretation:

- The route module dirty shape appears to tighten imports after moving or centralizing some responsibilities in `_data_source_config_responses.py`.
- The relative helper import is structurally more package-local than the previous unqualified import.
- Despite that, the route module is an active API surface with 9 route handlers and lifecycle hooks. Import changes can affect runtime import resolution and API startup.

Disposition:

| Question | Decision |
| --- | --- |
| Can G2.369 accept it? | No |
| Is it a plausible source-authorized acceptance candidate later? | Yes |
| Required later gate | import/runtime smoke plus focused file test |

### `web/backend/app/api/_data_source_config_responses.py`

Observed dirty hunks:

- expands typing import from `Any, Dict` to `Any, Dict, Optional`;
- adds imports for:
  - `YAML_DATA_SOURCES_REGISTRY_PATH`;
  - `APIRouter`;
  - `Header`;
  - `settings`;
  - `BusinessException`;
  - `ErrorCodes`;
  - `create_error_response`;
  - `verify_token`.

Current-use check:

| Name | Current helper count |
| --- | ---: |
| `YAML_DATA_SOURCES_REGISTRY_PATH` | 2 |
| `APIRouter` | 2 |
| `Header` | 2 |
| `settings` | 2 |
| `BusinessException` | 3 |
| `ErrorCodes` | 3 |
| `create_error_response` | 3 |
| `verify_token` | 2 |
| `Any` | 3 |
| `Dict` | 3 |
| `Optional` | 2 |

Interpretation:

- This helper is no longer only a static response-doc constant holder in the dirty baseline.
- It now carries imports tied to auth/config/error handling and backend runtime objects.
- That broadens the helper's responsibility and may be a legitimate extraction, but it is not safe to classify as "cosmetic" from inventory alone.

Disposition:

| Question | Decision |
| --- | --- |
| Can G2.369 accept it? | No |
| Is it a plausible source-authorized acceptance candidate later? | Maybe |
| Required later gate | inspect helper responsibilities, run import/runtime smoke, run contract-aware tests |

### `web/backend/app/api/data_source_config.old.py`

Observed dirty hunk:

- deletes the entire tracked file, approximately `694` lines.

Observed HEAD content before deletion:

- defines legacy request/response models including `DataSourceCreate`, `DataSourceUpdate`, `DataSourceResponse`, `VersionInfo`, `BatchOperationRequest`, `RollbackRequest`, `ReloadRequest`, and `ConfigChangeResponse`;
- defines route handlers for create, update, delete, get, list, batch, version history, rollback, reload, startup, and shutdown;
- imports `_data_source_config_old_reload`;
- exposes legacy route shapes such as:
  - `POST /`;
  - `PUT /{endpoint_name}`;
  - `DELETE /{endpoint_name}`;
  - `GET /{endpoint_name}`;
  - `GET /`;
  - `POST /batch`;
  - `GET /{endpoint_name}/versions`;
  - `POST /{endpoint_name}/rollback/{version}`;
  - `POST /reload`.

Interpretation:

- The filename indicates an old/legacy artifact, and the current canonical route appears to be `data_source_config.py`.
- However, the deletion is a full tracked-file removal.
- Under project standards, "old" naming and apparent replacement are not sufficient for deletion acceptance.
- The file also contains route and model behavior that must be checked against imports, router registration, docs, tests, and migration/exit criteria before retirement.

Disposition:

| Question | Decision |
| --- | --- |
| Can G2.369 accept deletion? | No |
| Is it a plausible source-authorized acceptance candidate later? | Unknown |
| Required later gate | explicit legacy-retirement evidence and deletion approval |

## GitNexus Evidence

Fresh GitNexus query for this surface returned:

| Evidence | Result |
| --- | --- |
| Index status | `stale=false`, `fresh_for_staged_diff=true` |
| Processes | no process returned for the exact dirty-state query |
| Definitions surfaced | `test_data_source_config_api.py`, `TestDataSourceConfigAPIFile`, `batch_operations`, `reload_config`, `ConfigManager`, `ConfigManager.create_endpoint`, route-doc contract tests |

Interpretation:

- The absence of a process result in this query is not deletion or acceptance evidence.
- The definitions confirm this is an active API/test/helper/core-manager area.
- Future source-authorized work should run symbol-level impact where specific functions/classes are edited.

## Decision Table

| Dirty item | Evidence strength | Risk if blindly accepted | G2.369 decision | Next gate |
| --- | --- | --- | --- | --- |
| Remove stale `SimpleNamespace` import in file test | local hunk only | Low | Hold, not accepted | include in source/test acceptance package |
| Tighten `data_source_config.py` imports | current name counts support unused-import removal | Medium: route startup/import behavior | Hold, not accepted | import smoke + focused file tests |
| Switch to relative response helper import | package-local import appears plausible | Medium: import resolution/regression risk | Hold, not accepted | import smoke + focused file tests |
| Move runtime/auth/error imports into `_data_source_config_responses.py` | helper name counts show active use | Medium/high: helper responsibility changed | Hold, not accepted | inspect helper design + contract-aware tests |
| Delete `data_source_config.old.py` | full tracked file deletion; old route/model surface exists in HEAD | High: legacy retirement without exit evidence | Block acceptance under no-source | separate deletion-retirement approval |

## Clean Boundary

This node draws a stricter boundary than G2.368:

- small import cleanup candidates exist;
- a larger helper-responsibility shift also exists;
- a full legacy-file deletion exists;
- these cannot be bundled together as a simple cleanup under no-source rules.

The safest next step is not implementation. It is an authorization-preflight that decides whether to split the follow-up into:

1. a narrow import/helper acceptance package; and
2. a separate legacy-file retirement review for `data_source_config.old.py`.

## Recommended Next Node

Recommended next node:

`G2.370 data source config acceptance authorization preflight / no-source`

Suggested purpose:

- decide whether source/test authority should be granted for the small import/helper/test cleanup package;
- explicitly exclude or separately gate `data_source_config.old.py` deletion unless legacy-retirement evidence is produced;
- define focused pytest/import gates before any source-authorized acceptance work.

Suggested source-authorized package, if later approved:

| Package | Include | Exclude |
| --- | --- | --- |
| Small acceptance package | import cleanup in `data_source_config.py`, relative helper import, stale test import removal, verified helper imports if design is accepted | deletion of `data_source_config.old.py` |
| Legacy-retirement package | only `data_source_config.old.py` deletion after exit evidence | route/helper import cleanup |

Suggested focused gates for any later source-authorized package:

- `python - <<'PY'` import smoke for `app.api.data_source_config`;
- `pytest tests/api/file_tests/test_data_source_config_api.py -q --no-cov`;
- if response docs are affected, relevant slices from `web/backend/tests/test_health_route_conflicts.py`;
- GitNexus impact/detect-changes before commit.

## Closeout

G2.369 is complete as a no-source dirty-state reconciliation node.

It authorizes no source edits, no test edits, no staging, no commit, and no deletion acceptance.

The current `data_source_config` dirty state should remain unresolved until an explicit source/test authorization gate is opened.
