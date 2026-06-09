# G2.368 Data Source Config Residual Inventory

## Node

- Node: `G2.368`
- Title: `data source config residual inventory`
- Date: `2026-06-05`
- Branch: `wip/root-dirty-20260403`
- HEAD observed: `d55418ad4`
- Mode: `no-source`
- `source_edit_authority`: `false`

## Authorization Boundary

This node is a no-source inventory only.

Authorized:

- inspect the `data_source_config` residual surface;
- refresh/read code-intelligence evidence;
- record a single report and decision table.

Not authorized:

- source edits;
- test edits;
- acceptance of existing dirty hunks;
- revert of existing dirty hunks;
- deletion of legacy files;
- API contract changes;
- implementation or provider-seam work.

## Governance Rules Applied

- `architecture/STANDARDS.md` remains the shared-rule source of truth.
- "Unused" or "unreferenced" is not sufficient evidence for deletion.
- Compatibility or legacy-looking files cannot be retired without explicit exit evidence.
- This report records observations only; it does not authorize cleanup.
- GitNexus stale-index caveat was handled with the project-native command:
  - `gitnexus analyze --index-only --wal-checkpoint-threshold 67108864`
  - Result: repository indexed successfully, `235,702 nodes`, `323,091 edges`, `300 flows`.
  - Important: this node used direct `gitnexus analyze`, not `npx gitnexus analyze`.

## Scope

Primary files:

| File | Role | Observed status |
| --- | --- | --- |
| `web/backend/app/api/data_source_config.py` | API route module | dirty: modified |
| `web/backend/app/api/_data_source_config_responses.py` | OpenAPI response/example helper | dirty: modified |
| `web/backend/app/api/data_source_config_schemas.py` | request schema module | clean in scoped diff |
| `web/backend/app/api/data_source_config.old.py` | legacy/old route artifact | dirty: deleted |
| `tests/api/file_tests/test_data_source_config_api.py` | file-level route/helper contract tests | dirty: modified |

Context-only evidence files:

| File | Evidence role |
| --- | --- |
| `web/backend/tests/test_health_route_conflicts.py` | broader route-doc and response-doc contract tests reference this API area |
| `scripts/migrations/004_data_source_config_tables.sql` | schema/data-store support context |
| `src/core/data_source/config_manager.py` | core config manager used by the API route surface |

Scoped dirty status observed:

```text
M tests/api/file_tests/test_data_source_config_api.py
 M web/backend/app/api/_data_source_config_responses.py
 D web/backend/app/api/data_source_config.old.py
 M web/backend/app/api/data_source_config.py
```

Scoped name-status observed:

```text
M	tests/api/file_tests/test_data_source_config_api.py
M	web/backend/app/api/_data_source_config_responses.py
D	web/backend/app/api/data_source_config.old.py
M	web/backend/app/api/data_source_config.py
```

## Current API Surface

`web/backend/app/api/data_source_config.py` is an active route module, not a dormant residual file.

Observed route surface:

| Line | Route | Handler | Response helper |
| --- | --- | --- | --- |
| 101 | `POST /` | `create_data_source` | `DATA_SOURCE_CONFIG_CREATE_RESPONSES` |
| 169 | `PUT /{endpoint_name}` | `update_data_source` | `DATA_SOURCE_CONFIG_UPDATE_RESPONSES` |
| 247 | `DELETE /{endpoint_name}` | `delete_data_source` | `DATA_SOURCE_CONFIG_DELETE_RESPONSES` |
| 294 | `GET /{endpoint_name}` | `get_data_source` | `DATA_SOURCE_CONFIG_DETAIL_RESPONSES` |
| 337 | `GET /` | `list_data_sources` | `DATA_SOURCE_CONFIG_LIST_RESPONSES` |
| 382 | `POST /batch` | `batch_operations` | `DATA_SOURCE_CONFIG_BATCH_RESPONSES` |
| 493 | `GET /{endpoint_name}/versions` | `get_version_history` | `DATA_SOURCE_CONFIG_VERSIONS_RESPONSES` |
| 556 | `POST /{endpoint_name}/rollback` | `rollback_to_version` | `DATA_SOURCE_CONFIG_ROLLBACK_RESPONSES` |
| 616 | `POST /reload` | `reload_config` | `DATA_SOURCE_CONFIG_RELOAD_RESPONSES` |
| 661 | startup event | `startup_event` | n/a |
| 667 | shutdown event | `shutdown_event` | n/a |

Observed local helpers and lifecycle functions:

| Symbol | Evidence |
| --- | --- |
| `handle_config_error` | local error-to-`UnifiedResponse` mapper |
| `create_data_source` | participates in GitNexus process `proc_83_create_data_source` |
| `reload_config` | surfaced by GitNexus and tied to `ConfigManager.reload_config` context |
| `startup_event` / `shutdown_event` | route-local lifecycle hooks |

## Response Helper Surface

`web/backend/app/api/_data_source_config_responses.py` is active because the route module imports/uses response constants for each route class.

Observed response constants:

| Constant | Role |
| --- | --- |
| `DATA_SOURCE_CONFIG_DETAIL_RESPONSES` | detail/read response docs |
| `DATA_SOURCE_CONFIG_LIST_RESPONSES` | list response docs |
| `DATA_SOURCE_CONFIG_DELETE_RESPONSES` | delete response docs |
| `DATA_SOURCE_CONFIG_VERSIONS_RESPONSES` | version history response docs |
| `DATA_SOURCE_CONFIG_CREATE_RESPONSES` | create response docs |
| `DATA_SOURCE_CONFIG_UPDATE_RESPONSES` | update response docs |
| `DATA_SOURCE_CONFIG_BATCH_RESPONSES` | batch operation response docs |
| `DATA_SOURCE_CONFIG_ROLLBACK_RESPONSES` | rollback response docs |
| `DATA_SOURCE_CONFIG_RELOAD_RESPONSES` | reload response docs |

Decision implication: this helper is not a cleanup candidate under no-source rules. Any changes here would be API-documentation behavior and require explicit source/test authority plus contract-aware gates.

## Schema Surface

`web/backend/app/api/data_source_config_schemas.py` is a compact schema module and was clean in the scoped diff.

Observed schema/model symbols:

| Symbol | Role |
| --- | --- |
| `DataSourceCreate` | create request model |
| `DataSourceUpdate` | update request model |
| `BatchOperationItem` | batch item model |
| `BatchOperationRequest` | batch request model |
| `RollbackRequest` | rollback request model |
| `ReloadRequest` | reload request model |
| `validate_data_category` | create model validator |
| `validate_operations` | batch request validator |

Decision implication: no evidence supports schema cleanup or migration in this node.

## Test Surface

`tests/api/file_tests/test_data_source_config_api.py` is an active file-level contract guard and is currently dirty.

Observed tests:

| Test | Guarded behavior |
| --- | --- |
| `test_router_registers_expected_config_routes` | route registration and prefix/tags |
| `test_router_contains_expected_number_of_route_method_pairs` | route-method count |
| `test_all_routes_use_unified_response_model` | response model uniformity |
| `test_create_route_keeps_created_status_code` | create status code |
| `test_route_names_remain_stable_for_core_operations` | route name stability |
| `test_get_current_user_returns_system_in_testing_mode` | testing-mode user fallback |
| `test_get_current_user_rejects_missing_authorization_outside_testing` | auth rejection behavior |
| `test_handle_config_error_maps_duplicate_and_not_found` | error mapping |
| `test_module_docstring_mentions_crud_versioning_and_hot_reload` | documented module responsibilities |
| `test_router_response_descriptions_include_success_and_conflict` | response-doc descriptions |

Decision implication: the current dirty test file is part of the surface that must be reconciled before any acceptance or source-authorized follow-up.

## Reference Evidence

Fresh GitNexus query after direct index refresh found:

| Evidence | Result |
| --- | --- |
| Process | `proc_83_create_data_source` |
| Process summary | `Create_data_source -> Get_redis_client` |
| Process type | `cross_community` |
| Indexed API symbol | `web/backend/app/api/data_source_config.py:create_data_source` |
| Additional definitions | file-level test class, health route contract tests, `ConfigManager`, `ConfigManager.reload_config` |
| Index status | `stale: false` |

Static reference inventory found `91` files containing scoped tokens. Category distribution:

| Category | Count |
| --- | ---: |
| API | 3 |
| Tests | 11 |
| `src` | 5 |
| Scripts | 2 |
| Docs | 25 |
| Other tracked files | 45 |

Non-doc key references include:

| File | Relevance |
| --- | --- |
| `config/data_sources_loader.py` | config/data-source loading context |
| `scripts/analyze_config_debt.py` | config-debt analysis context |
| `scripts/tests/test_phase3_integration.py` | integration script context |
| `src/core/data_source/config_manager.py` | core manager implementation context |
| `src/core/datasource/registry.py` | data-source registry context |
| `tests/unit/test_datasource/test_health.py` | datasource unit test context |
| `tests/unit/test_datasource/test_registry.py` | datasource registry test context |
| `web/backend/tests/test_health_route_conflicts.py` | broader route-doc contract context |

The high reference count includes docs, generated/vendor-like plugin files, reports, and governance artifacts; it is not a hard dependency metric. It is only an inventory signal.

## Decision Table

| Surface | Evidence | Current disposition | Next authorization required |
| --- | --- | --- | --- |
| `data_source_config.py` route module | active route surface, 9 route handlers plus lifecycle hooks, GitNexus process membership | Active API surface; not a cleanup candidate | Dirty-state reconciliation before any source edit |
| `_data_source_config_responses.py` helper | imported response constants cover all observed route classes | Active API documentation helper; not a cleanup candidate | Source/test authority plus contract-doc gates |
| `data_source_config_schemas.py` | compact schema module, clean scoped diff, validators in use | Hold as canonical schema support | No action from this node |
| `data_source_config.old.py` | scoped diff shows deletion already present | Existing dirty deletion; not accepted by this no-source node | Separate approval to accept or restore deletion after evidence review |
| `test_data_source_config_api.py` | active file-level route/helper tests; currently dirty | Existing dirty test baseline; no acceptance by this node | Separate dirty-state reconciliation and focused pytest gate |
| `web/backend/tests/test_health_route_conflicts.py` | broader API-doc contract definitions reference data-source config area | External contract context, not part of immediate edit scope | Include in any future source-authorized gate if OpenAPI docs change |
| `ConfigManager` context | API route delegates to core config manager behavior | Downstream dependency context, not residual cleanup | Impact analysis required before touching manager behavior |

## Boundary Decision

This candidate should not proceed directly into implementation.

Reason:

- The scoped surface already contains dirty source/test changes.
- The route module is active and contract-bearing.
- The response helper affects OpenAPI examples/responses.
- The deleted `data_source_config.old.py` is an unresolved dirty-state fact, not evidence of authorized retirement.
- Under `architecture/STANDARDS.md`, no-source inventory cannot convert "old", "unused", or "already deleted in worktree" into deletion approval.

Clean next gate:

`G2.369 data source config dirty-state reconciliation / no-source`

Suggested scope for that gate:

- reconcile the modified `data_source_config.py`;
- reconcile the modified `_data_source_config_responses.py`;
- reconcile the deleted `data_source_config.old.py`;
- reconcile the modified `test_data_source_config_api.py`;
- decide whether a later source-authorized acceptance package is justified.

Non-goals for that gate:

- no implementation;
- no revert;
- no deletion acceptance;
- no OpenAPI behavior change;
- no broad data-source subsystem refactor.

## Closeout

G2.368 is complete as a no-source inventory node.

The clean boundary is:

- `data_source_config` is an active API/contract surface, not a residual cleanup target;
- current source/test dirtiness must be reconciled before any implementation or commit package;
- this report authorizes no source, test, deletion, or API-contract change.
