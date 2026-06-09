# Frontend Auth Routing Alignment Patch

Date: `2026-04-25`

This companion file describes the standalone staged patch exported to:

- `docs/reports/tasks/frontend-auth-routing-alignment-2026-04-25.patch`

Scope:

- `web/frontend/src/App.vue`
- `web/frontend/src/stores/auth.ts`
- `web/frontend/src/views/Login.vue`
- `web/frontend/src/views/NotFound.vue`
- `web/frontend/tests/e2e/auth-login.spec.ts`
- `web/frontend/tests/unit/config/dashboard-route-canonical-truth.spec.ts`
- `web/frontend/tests/unit/config/shell-route-runtime-guardrails.spec.ts`

Theme:

- Auth/login shell state alignment
- Blank-layout runtime shell handling
- QM compatibility redirect coverage
- 404 shell token alignment
- Guardrail coverage for canonical route behavior

Notes:

- This patch was exported from the current staged state only.
- It is intentionally separate from the MOCK governance batch.
- No staged files were added, removed, or unstaged during export.
- Validation status remains whatever was true in the source staged state; this export step did not rerun tests.
