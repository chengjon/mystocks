> Superseded body: do not publish this issue body directly.
> Its scope is merged into `14-build-shared-evidence-package.md`.

## What to build

Refresh and reconcile shared route table and OpenAPI evidence after the P3
implementation line. This is evidence-only work. Do not mutate route
registration or API code.

Existing evidence already available:

- `docs/reports/quality/generated/backend-fullpath-route-table.md`
- `docs/reports/quality/generated/backend-fullpath-route-table.json`
- `docs/reports/quality/generated/openapi-before.json`

The current known route table was refreshed after the P3-D scanner fix. It
records `538` routes, `0` full-path duplicate groups, and `2` remaining orphan
route files. The current OpenAPI baseline is OpenAPI `3.1.0` with `501` unique
paths.

## OpenSpec requirement

- C tasks 1.2-1.5
- G tasks 1.2-1.5

## Acceptance criteria

- `docs/reports/quality/generated/backend-fullpath-route-table.md` exists and
  records current branch, HEAD, and summary.
- `docs/reports/quality/generated/backend-fullpath-route-table.json` exists.
- `docs/reports/quality/generated/openapi-before.json` exists, or the issue
  records why OpenAPI generation is blocked.
- Post-P3 route/OpenAPI evidence is regenerated or explicitly confirmed current.
- The issue summary reconciles route-table method+path counts with OpenAPI
  unique path counts.
- The issue summary diffs any post-P3 OpenAPI baseline against
  `docs/reports/quality/generated/openapi-before.json`.
- Summary separates local decorator duplicates from final full-path conflicts.
- No route mutation is performed.

## Verification

```bash
cd web/backend && python ../../scripts/dev/backend_audit_fullpath_routes.py ../../docs/reports/quality/generated
python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json
```

## Pre-publish verification

`python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json`
was run successfully on 2026-05-18. It produced valid OpenAPI JSON at:

```text
docs/reports/quality/generated/openapi-before.json
```

Observed result:

- OpenAPI version: `3.1.0`
- Path count: `501`
- Non-blocking warning: duplicate operation ID for `_strategy_mgmt_compat.py`

## Blocked by

BLOCKED_BY_TODO: issue 1 approval.
