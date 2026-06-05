# G2.370 Data Source Config Acceptance Authorization Preflight

## Node

- Node: `G2.370`
- Title: `data source config acceptance authorization preflight`
- Date: `2026-06-05`
- Branch: `wip/root-dirty-20260403`
- HEAD observed: `d55418ad4`
- Mode: `no-source`
- `source_edit_authority`: `false`
- Parent evidence:
  - `G2.368 data source config residual inventory`
  - `G2.369 data source config dirty-state reconciliation`

## Authorization Boundary

This node decides whether the current `data_source_config` dirty state is ready for source-authorized acceptance.

Authorized:

- run read-only/import/test verification commands;
- classify whether a source-authorized package is safe to open;
- define package boundaries and required gates.

Not authorized:

- source edits;
- test edits;
- deleting or restoring `data_source_config.old.py`;
- accepting dirty hunks;
- staging files;
- committing files.

## Preflight Question

Can the current `data_source_config` dirty state be authorized as a single source/test acceptance package?

Answer: no.

Reason:

- import smoke passes;
- the focused file test does not pass;
- the dirty state includes both small import/helper changes and a full legacy file deletion;
- the current route/helper/test contract is internally inconsistent.

## Scoped Dirty Baseline

Observed scoped dirty files remain:

```text
M tests/api/file_tests/test_data_source_config_api.py
 M web/backend/app/api/_data_source_config_responses.py
 D web/backend/app/api/data_source_config.old.py
 M web/backend/app/api/data_source_config.py
```

This node did not accept, revert, stage, or commit these files.

## Verification Evidence

### Import Smoke

Command:

```bash
PYTHONPATH=/opt/claude/mystocks_spec/web/backend:/opt/claude/mystocks_spec python - <<'PY'
import importlib
module = importlib.import_module("app.api.data_source_config")
print("import app.api.data_source_config: ok")
print("router routes:", len(getattr(module, "router").routes))
PY
```

Observed result:

```text
import app.api.data_source_config: ok
router routes: 9
```

Interpretation:

- The dirty baseline can import the active route module.
- Import success is necessary but insufficient for acceptance because file-level contract tests fail.

### Focused File Test

Command:

```bash
pytest tests/api/file_tests/test_data_source_config_api.py -q --no-cov
```

Observed result:

```text
3 failed, 7 passed, 13 warnings
```

Failing tests:

| Test | Failure |
| --- | --- |
| `test_get_current_user_returns_system_in_testing_mode` | `AttributeError: module 'app.api.data_source_config' has no attribute 'settings'` |
| `test_get_current_user_rejects_missing_authorization_outside_testing` | `AttributeError: module 'app.api.data_source_config' has no attribute 'settings'` |
| `test_router_response_descriptions_include_success_and_conflict` | `KeyError: 200` |

Interpretation:

- The current dirty shape moved or stopped exposing `settings` at `app.api.data_source_config`.
- The file test still expects `data_source_config_module.settings`.
- The route-level `router.responses` no longer includes the expected `200` and `201` entries at the location asserted by the test.
- Therefore, the dirty state is not an acceptance-ready package.

## Contract Drift Evidence

Current dirty `data_source_config.py` imports selected helper objects from the response helper:

```text
from ._data_source_config_responses import (
    DATA_SOURCE_CONFIG_BATCH_RESPONSES,
    DATA_SOURCE_CONFIG_CREATE_RESPONSES,
    DATA_SOURCE_CONFIG_DELETE_RESPONSES,
    DATA_SOURCE_CONFIG_DETAIL_RESPONSES,
    DATA_SOURCE_CONFIG_LIST_RESPONSES,
    DATA_SOURCE_CONFIG_RELOAD_RESPONSES,
    DATA_SOURCE_CONFIG_ROLLBACK_RESPONSES,
    DATA_SOURCE_CONFIG_UPDATE_RESPONSES,
    DATA_SOURCE_CONFIG_VERSIONS_RESPONSES,
    get_current_user,
    router,
)
```

Current dirty `_data_source_config_responses.py` now owns broader route/helper dependencies:

```text
from fastapi import APIRouter, Header
from app.core.config import settings
from app.core.security import verify_token
router = APIRouter(...)
```

HEAD baseline previously had route-module-level imports:

```text
from fastapi import APIRouter, Body, Depends, Header, Path, Query, Request
from app.core.config import settings
from app.core.security import verify_token
from _data_source_config_responses import (...)
```

Preflight interpretation:

- The dirty change appears to move router/auth/config ownership from the route module into `_data_source_config_responses.py`.
- That may be a valid design, but the current tests were not aligned with that boundary.
- A source-authorized package must either preserve the old module-level contract or intentionally update tests to the new contract.
- This cannot be authorized as a passive acceptance package.

## Legacy Deletion Evidence

`web/backend/app/api/data_source_config.old.py` remains a tracked file deleted in the current dirty state.

Reference scan for `data_source_config.old` and old helper tokens found documentation/report references including:

| File | Reference type |
| --- | --- |
| `docs/reports/TEST_ORDER_RECOMMENDATION.md` | report reference |
| `docs/reports/plans/code-simplification-notes.md` | cleanup/planning reference |
| `docs/reports/plans/compatibility-inventory.md` | compatibility inventory reference |
| `docs/reports/plans/phase-b-execution-checklist.md` | execution checklist reference |
| `docs/reports/pylint-errors-by-module.txt` | lint/debt report reference |
| `docs/reports/quality/backend-audit-2026-05-14.md` | quality audit reference |
| `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md` | residual inventory reference |
| `reports/structure-baseline/directory-structure-report.txt` | structure baseline reference |
| `web/backend/CONTEXT.md` | backend context reference |

Preflight interpretation:

- No active Python import was proven by this scan.
- That still does not authorize deletion.
- The file is a tracked legacy route artifact with prior audit/planning references.
- It requires separate retirement evidence and explicit deletion approval.

## Authorization Decision Table

| Candidate package | Current evidence | Blocking issue | Authorization decision |
| --- | --- | --- | --- |
| Accept all current dirty files as one package | Import smoke passes | focused file test fails; legacy deletion mixed with route/helper/test contract changes | Reject as-is |
| Small import/helper/test acceptance package | Route import smoke passes; some stale-import evidence exists | tests fail because module-level `settings` and `router.responses` contract changed | Not ready |
| Update tests to new helper-owned contract | dirty design may intentionally move ownership into helper | requires explicit test-edit authority and design decision | Needs source/test authorization after preflight |
| Preserve old route-module contract | would likely satisfy current tests | requires source edits and impact review | Needs source/test authorization after preflight |
| Delete `data_source_config.old.py` | old file appears legacy and no active Python import was proven | full tracked-file deletion lacks retirement/exit evidence | Block; separate legacy-retirement gate |

## Required Next Decision

Before implementation, choose one of two explicit strategies:

| Strategy | Meaning | Include `data_source_config.old.py` deletion? |
| --- | --- | --- |
| A. Preserve public module contract | Keep/restore `data_source_config_module.settings` and expected route response docs while retaining safe import cleanup where possible | No |
| B. Accept new helper-owned boundary | Treat `_data_source_config_responses.py` as owner of router/auth/config helpers and update tests to assert that new boundary | No |

In both strategies, `data_source_config.old.py` deletion remains excluded.

## Recommended Next Node

Recommended next node:

`G2.371 data source config acceptance strategy decision / no-source`

Purpose:

- choose Strategy A or Strategy B;
- keep `data_source_config.old.py` deletion out of the small package;
- define exact source/test files authorized for a later implementation node;
- define exact focused gates.

Recommended default:

Strategy A: preserve public module contract.

Reason:

- It minimizes behavioral and test-contract movement.
- It treats the current failing tests as a useful contract signal.
- It keeps the package narrow enough for a later source-authorized acceptance node.

## Future Gates If Strategy A Is Authorized

Required pre-edit GitNexus:

- impact on `get_current_user`, `router`, and any edited route/helper symbol;
- warn if risk is high or critical.

Required verification:

- import smoke for `app.api.data_source_config`;
- `pytest tests/api/file_tests/test_data_source_config_api.py -q --no-cov`;
- targeted route-doc tests from `web/backend/tests/test_health_route_conflicts.py` if response docs change;
- `git diff --check`;
- `gitnexus detect_changes` before commit.

## Closeout

G2.370 is complete as a no-source authorization preflight.

Decision:

- do not authorize current dirty state as-is;
- do not accept `data_source_config.old.py` deletion;
- split strategy choice into a no-source decision node before any source/test implementation.
