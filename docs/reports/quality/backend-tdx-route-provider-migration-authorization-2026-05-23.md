# Backend TDX Route Provider Migration Authorization - 2026-05-23

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Status: review-ready.

Scope: G2.39 decision/authorization packet for a future TDX route-provider
migration.

Current HEAD: `30c78a22dce5879396dfd5c7760cc61161377528`.

Parent issue: `#79` service lifecycle DI, currently `OPEN` with
`needs-triage`.

Parent PR: `#178` merged G2.38 TDX route dependency consumer matrix at
`30c78a22dce5879396dfd5c7760cc61161377528`.

Boundary note: this packet authorizes only a future implementation lane if
human review accepts it. This packet itself does not change backend source,
tests, route paths, OpenAPI schema, PM2/runtime state, OpenSpec changes, issue
labels, or compatibility getter behavior.

## Current Input State

G2.38 established the current TDX consumer taxonomy:

| Evidence | Current state | Interpretation |
|---|---|---|
| `/api/v1/tdx` route surface | five `Depends(get_tdx_service)` public route consumers | active route-provider migration candidate |
| `/api/ml/tdx` route surface | local `TdxDataService()` variable usage | unrelated to `app.services.tdx_service` lifecycle DI |
| `dashboard_data_source.py` | direct body calls to `get_tdx_service()` are `0`; default provider fallback remains | out of this route-provider lane |
| `tdx_service.py` | defines `TdxService`, `_tdx_service_instance`, `get_tdx_service()`, and `install_tdx_service(app, service=None)` | route-provider seam can be added while preserving compatibility getter |

Targeted OpenAPI smoke at current HEAD:

| Field | Value |
|---|---:|
| `paths_total` | 500 |
| `operation_ids` | 536 |
| `duplicate_operation_ids` | 0 |
| TDX OpenAPI paths | 7 |

TDX service symbol snapshot:

| File | Key counts |
|---|---|
| `web/backend/app/services/tdx_service.py` | `get_tdx_service`: 2; `install_tdx_service`: 1; `get_tdx_service_dependency`: 0; `TDX_SERVICE_STATE_KEY`: 0; `app.state.tdx_service`: 1 |
| `web/backend/app/api/tdx.py` | `get_tdx_service`: 6; `Depends(get_tdx_service)`: 5; `get_tdx_service_dependency`: 0 |
| `web/backend/app/main.py` | `install_tdx_service`: 2; no route dependency changes needed |
| `web/backend/app/api/dashboard_data_source.py` | `get_tdx_service`: 5 as import/default-provider/private-helper text; no direct route/helper body calls |

## Decision

Decision: approve, subject to human review, a future G2.40 implementation lane
that migrates only the `/api/v1/tdx` route dependency surface from
`Depends(get_tdx_service)` to a dedicated app-state provider dependency.

This decision does not authorize deleting `get_tdx_service()`.

The compatibility getter must remain available because:

1. `install_tdx_service(app, service=None)` still uses it as fallback when no
   explicit app-state service exists.
2. `dashboard_data_source.py` still keeps it as the default provider fallback.
3. Tests and historical consumers still rely on the compatibility surface.

## Future Allowed Write Scope

If this authorization packet is approved, a future implementation branch may
modify only:

| Path | Future allowed change |
|---|---|
| `web/backend/app/services/tdx_service.py` | Add `TDX_SERVICE_STATE_KEY`, add `get_tdx_service_dependency(request: Request)`, update installer internals to use the named state key, and preserve `get_tdx_service()` compatibility fallback. |
| `web/backend/app/api/tdx.py` | Convert only the five `/api/v1/tdx` `Depends(get_tdx_service)` parameters to `Depends(get_tdx_service_dependency)` while keeping route functions, paths, response models, auth dependencies, and operation IDs stable. |
| `web/backend/tests/test_tdx_service_lifecycle_di.py` | Add focused provider install, app-state override, fallback, and route dependency override coverage. |
| `docs/reports/quality/backend-tdx-route-provider-migration-implementation-2026-05-23.md` | Record future implementation evidence and verification results. |
| future PR task card | Bind the implementation PR to the authorized source/test/report paths. |

## Future Implementation Shape

The future implementation should follow the established app-state provider plus
compatibility fallback shape used by prior service lifecycle DI migrations:

- keep `get_tdx_service()` as the compatibility getter;
- add `TDX_SERVICE_STATE_KEY = "tdx_service"`;
- keep `install_tdx_service(app, service=None)` as the app-state installer;
- make the installer store/read via the named state key;
- add `get_tdx_service_dependency(request: Request) -> TdxService`;
- make the dependency provider read `request.app.state` and fall back to
  `install_tdx_service(request.app)` when absent;
- inject `TdxService` into the five `/api/v1/tdx` route handlers with
  `Depends(get_tdx_service_dependency)`;
- preserve all route paths, HTTP methods, response models, response envelopes,
  validation behavior, auth dependencies, exception behavior, and OpenAPI
  exposure.

## Explicit Non-Goals

The future implementation lane must not:

- remove `get_tdx_service()`;
- change `TdxService` construction behavior;
- change real TDX adapter connection behavior;
- modify `web/backend/app/api/dashboard_data_source.py`;
- modify `web/backend/app/api/ml.py`;
- modify `web/backend/app/main.py`;
- modify `src/adapters/**`;
- modify `web/backend/app/services/__init__.py`;
- change `/api/ml/tdx` behavior;
- change route paths, HTTP methods, response models, response envelopes, auth,
  exception behavior, or OpenAPI schema exposure;
- change docs/API, generated clients, frontend code, PM2 scripts, runtime config,
  OpenSpec changes/specs, or GitHub issue labels;
- expand into dashboard helper provider design or TDX adapter refactoring.

## Required Future Gates

Before any future source implementation commit:

1. Run GitNexus context/impact for `get_tdx_service`, `install_tdx_service`,
   `get_stock_quote` in `web/backend/app/api/tdx.py`, and `health_check` in
   `web/backend/app/api/tdx.py`. If GitNexus resolves an ambiguous symbol, use
   file-path-qualified context and record the ambiguity.
2. Add failing focused tests for provider install/app-state override/fallback and
   at least one route dependency override path.
3. Implement the smallest provider seam that satisfies those tests.
4. Run focused pytest for `web/backend/tests/test_tdx_service_lifecycle_di.py`.
5. Run a representative guard that confirms `tdx.py` route body direct
   `get_tdx_service()` calls remain `0` and `Depends(get_tdx_service)` becomes
   `0`.
6. Run `ruff check` and `black --check` on touched backend source/test files.
7. Run an `app.main` import and targeted OpenAPI smoke confirming paths stay
   `500`, duplicate operation IDs stay `0`, and the seven TDX OpenAPI paths stay
   present.
8. Stage only the authorized paths and run GitNexus `detect_changes` on the
   staged scope before committing.

## Future Verification Commands

The future implementation packet should use commands equivalent to:

```bash
pytest -o addopts= web/backend/tests/test_tdx_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
ruff check web/backend/app/services/tdx_service.py web/backend/app/api/tdx.py web/backend/tests/test_tdx_service_lifecycle_di.py
black --check web/backend/app/services/tdx_service.py web/backend/app/api/tdx.py web/backend/tests/test_tdx_service_lifecycle_di.py
```

The OpenAPI smoke must set only dummy required environment variables needed to
import `app.main`; it must not start PM2 or call real external TDX services.

## Rollback Plan For Future Implementation

If the future implementation causes regressions:

- revert the future implementation PR;
- restore the five `/api/v1/tdx` route parameters to
  `Depends(get_tdx_service)`;
- remove the new dedicated provider and state-key constant only if no later
  accepted lane has started to depend on them;
- keep `get_tdx_service()` compatibility getter available;
- keep this authorization packet as historical governance evidence unless the
  decision itself is explicitly superseded.

## Review Checklist

This packet should be accepted only if reviewers agree that:

- `/api/v1/tdx` route-provider migration is an appropriate next service
  lifecycle DI implementation candidate;
- the first implementation scope is limited to `tdx_service.py`, `tdx.py`,
  focused lifecycle tests, implementation evidence, and a future task card;
- `dashboard_data_source.py`, `api/ml.py`, `main.py`, adapters, OpenAPI contract
  changes, frontend, PM2, and OpenSpec work remain out of scope;
- `get_tdx_service()` remains an active compatibility getter after the future
  implementation.

## Next Gate

Human review of this G2.39 authorization packet.

If accepted, create a separate G2.40 implementation branch. No source edits are
authorized by G2.39 until that separate implementation lane is explicitly
started.
