# Frontend Auth Routing Alignment PR Summary

Suggested commit title:

- `frontend: align auth shell and qm compatibility routing`

Suggested PR title:

- `frontend: align auth shell states with canonical qm compatibility routing`

Summary:

- Align blank-layout runtime handling in `App.vue` so auth-style routes can bypass the default shell wrapper and readiness banner.
- Bridge login pending state through the shared auth store to keep page-level loading feedback consistent with the real auth request lifecycle.
- Refresh `Login.vue` and `NotFound.vue` runtime shells so they stay within the current ArtDeco token system and expose clearer route/auth status feedback.
- Extend E2E and unit guardrails for `/qm` compatibility redirects, canonical return URLs, blank-layout runtime handling, and shell token usage.

Included files:

- `web/frontend/src/App.vue`
- `web/frontend/src/stores/auth.ts`
- `web/frontend/src/views/Login.vue`
- `web/frontend/src/views/NotFound.vue`
- `web/frontend/tests/e2e/auth-login.spec.ts`
- `web/frontend/tests/unit/config/dashboard-route-canonical-truth.spec.ts`
- `web/frontend/tests/unit/config/shell-route-runtime-guardrails.spec.ts`

Review focus:

- Blank layout routes must not inherit the default shell/banner container.
- Login redirect handling must preserve canonical return URLs for `/qm` compatibility paths.
- Login loading state must reflect the actual auth request window.
- 404 and login shells must stay on current ArtDeco runtime tokens instead of legacy token names.

Validation note:

- This summary file was generated after patch export only.
- No additional tests were run as part of creating this PR summary artifact.
