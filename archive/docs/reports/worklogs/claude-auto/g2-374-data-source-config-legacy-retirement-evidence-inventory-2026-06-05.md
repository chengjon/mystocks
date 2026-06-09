# G2.374 Data Source Config Legacy-Retirement Evidence Inventory

## Node

- Node: `G2.374`
- Title: `data source config legacy-retirement evidence inventory`
- Date: `2026-06-05`
- Branch: `wip/root-dirty-20260403`
- HEAD observed: `d920e6bfa`
- Mode: `no-source`
- `source_edit_authority`: `false`
- Parent closeout: `G2.373 data source config post-commit closeout`

## Authorization Boundary

This node is an evidence inventory only.

Authorized:

- inspect current dirty state for `web/backend/app/api/data_source_config.old.py`;
- inspect tracked HEAD content for the deleted file;
- inspect active references and historical/documentation references;
- decide whether a later deletion-retirement authorization is justified.

Not authorized:

- delete files;
- restore files;
- edit source;
- edit tests;
- stage files;
- commit files;
- accept the current deletion.

## Current State

Current scoped status:

```text
D web/backend/app/api/data_source_config.old.py
```

Tracking evidence:

| Fact | Result |
| --- | --- |
| `data_source_config.old.py` tracked by Git | yes |
| File exists in current worktree | no |
| Current deletion staged | no |
| Current deletion accepted by this node | no |

## HEAD Content Summary

`web/backend/app/api/data_source_config.old.py` at HEAD is a `695` line legacy route module.

Imports:

```text
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, validator
from app.api._data_source_config_old_reload import (...)
from app.core.responses import (...)
from src.core.data_source.config_manager import ConfigManager
from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async
```

Important observation:

- The legacy file imports `app.api._data_source_config_old_reload`.
- `web/backend/app/api/_data_source_config_old_reload.py` is not tracked at current HEAD.
- This makes the old module structurally suspect as an active runtime module, but it is still not deletion approval by itself.

## Legacy Route Surface

The old file defines request/response models, local helpers, and route handlers.

Representative symbols:

| Symbol | Role |
| --- | --- |
| `DataSourceCreate` | legacy create request model |
| `DataSourceUpdate` | legacy update request model |
| `DataSourceResponse` | legacy response model |
| `VersionInfo` | legacy version response model |
| `BatchOperationRequest` | legacy batch request model |
| `BatchOperationResponse` | legacy batch response model |
| `RollbackRequest` | legacy rollback request model |
| `ReloadRequest` | legacy reload request model |
| `ConfigChangeResponse` | legacy mutation response model |
| `get_config_manager` | legacy manager factory |
| `get_current_user` | legacy auth helper |
| `handle_config_error` | legacy error mapper |

Observed route decorators:

| Route | Handler |
| --- | --- |
| `POST /` | `create_data_source` |
| `PUT /{endpoint_name}` | `update_data_source` |
| `DELETE /{endpoint_name}` | `delete_data_source` |
| `GET /{endpoint_name}` | `get_data_source` |
| `GET /` | `list_data_sources` |
| `POST /batch` | `batch_operations` |
| `GET /{endpoint_name}/versions` | `get_version_history` |
| `POST /{endpoint_name}/rollback/{version}` | `rollback_to_version` |
| `POST /reload` | `reload_config` |
| startup event | `startup_event` |
| shutdown event | `shutdown_event` |

Interpretation:

- The old file contains a full legacy route implementation, not a trivial shim.
- It duplicates the same broad route domain now served by the active `data_source_config.py` line.
- Its deletion must be treated as legacy-retirement, not import cleanup.

## Reference Evidence

Token scan:

- tokens: `data_source_config.old`, `data_source_config_old`, `_data_source_config_old_reload`;
- active Python non-self references found: `0`;
- documentation/report references found: `9`.

Documentation/report references:

```text
docs/reports/TEST_ORDER_RECOMMENDATION.md
docs/reports/plans/code-simplification-notes.md
docs/reports/plans/compatibility-inventory.md
docs/reports/plans/phase-b-execution-checklist.md
docs/reports/pylint-errors-by-module.txt
docs/reports/quality/backend-audit-2026-05-14.md
docs/reports/quality/backend-residual-files-inventory-2026-05-14.md
reports/structure-baseline/directory-structure-report.txt
web/backend/CONTEXT.md
```

Interpretation:

- No active Python caller/importer was found by the scoped token scan.
- The remaining references are governance, audit, context, or historical documentation references.
- This supports a deletion-retirement candidate classification.
- It does not, by itself, authorize deletion.

## History Evidence

Recent tracked history for the old file:

```text
76f195f69 2026-03-17 security: sanitize tracked secrets and prep history rewrite
dc7d2a5a0 2026-01-31 20260131,保存一个版本
c6973b3a6 2026-01-20 docs: optimize web client operation plan
0fe8b9022 2026-01-10 feat: comprehensive project updates for January 2026
```

Interpretation:

- The file predates the current G2.372 Strategy A acceptance.
- The current active API contract has now been repaired and committed separately.
- The old file remains a distinct legacy-retirement question.

## Decision Table

| Evidence | Finding | Decision impact |
| --- | --- | --- |
| Tracked file currently deleted in worktree | yes | deletion is present but not accepted |
| Active Python non-self references | `0` | supports deletion-retirement candidacy |
| Historical/docs references | `9` | docs do not block deletion, but should be acknowledged |
| Old file imports missing tracked helper | yes, `_data_source_config_old_reload.py` is not tracked | strengthens legacy/suspect classification |
| Old file has full route surface | yes, 9 route handlers plus lifecycle events | deletion must be explicit retirement, not cleanup |
| Active `data_source_config.py` Strategy A line landed | yes, `df5aba5c2` | active contract is preserved separately |

## Boundary Decision

This node does not accept the deletion.

Evidence is sufficient to classify `data_source_config.old.py` as a deletion-retirement candidate.

Evidence is not sufficient for this no-source node to stage, commit, or approve the deletion.

## Recommended Next Node

Recommended next node:

`G2.375 data_source_config.old deletion-retirement authorization / source-authorized`

Required authorization shape:

- `source_edit_authority=true`;
- scope limited to `web/backend/app/api/data_source_config.old.py`;
- allowed action: accept the already-present deletion only;
- do not edit active `data_source_config.py`;
- do not edit `_data_source_config_responses.py`;
- do not edit tests unless explicitly separately authorized;
- do not touch unrelated data-source modules.

Required gates:

- GitNexus impact or file-level detect for `data_source_config.old.py`;
- `git diff --cached --check`;
- focused import smoke for `app.api.data_source_config`;
- focused pytest: `pytest tests/api/file_tests/test_data_source_config_api.py -q --no-cov`;
- GitNexus staged detect before commit.

Alternative no-source next node:

`G2.375 data_source_config.old documentation-reference triage / no-source`

Use this only if the team wants to classify whether `web/backend/CONTEXT.md` and historical reports should be updated before deletion acceptance.

## Closeout

G2.374 is complete as a no-source legacy-retirement evidence inventory.

It authorizes no deletion.

It confirms that `data_source_config.old.py` is a strong candidate for a tightly scoped deletion-retirement authorization node.
