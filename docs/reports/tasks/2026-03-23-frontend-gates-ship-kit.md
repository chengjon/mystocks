# Frontend Gates Ship Kit

## Current State

- current_branch: `main`
- note: the worktree contains many unrelated pre-existing changes outside this frontend gate scope
- recommendation: create a dedicated branch before staging only the files listed below

## Suggested Branch

```bash
git switch -c chore/frontend-gates-mainline
```

## Scoped Staging Command

```bash
git add -- \
  .github/pull_request_template.md \
  .github/workflows/e2e-testing.yml \
  .github/workflows/frontend-testing.yml \
  .github/workflows/visual-testing.yml \
  docs/guides/frontend/INDEX.md \
  docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md \
  docs/reports/tasks/2026-03-23-frontend-gates-pr-draft.md \
  docs/reports/tasks/2026-03-23-frontend-gates-ship-kit.md \
  docs/superpowers/plans/2026-03-23-frontend-test-gates.md \
  docs/testing/e2e/README.md \
  web/frontend/lighthouserc.cjs \
  web/frontend/package-lock.json \
  web/frontend/package.json \
  web/frontend/scripts/lighthouse-auth.cjs \
  web/frontend/scripts/stable-unit-suite.js \
  web/frontend/src/api/services/__tests__/dashboardService.spec.ts \
  web/frontend/src/api/services/dashboardService.ts \
  web/frontend/src/router/guards.ts \
  web/frontend/src/stores/__tests__/auth-guard.spec.ts \
  web/frontend/src/stores/auth.ts \
  web/frontend/tests/README-E2E.md \
  web/frontend/tests/e2e/auth-login.spec.ts \
  web/frontend/tests/e2e/critical/menu-navigation-fixed.spec.ts \
  web/frontend/tests/unit/config/lighthouse-mainline-gates.spec.ts \
  web/frontend/tests/unit/config/testing-mainline-gates.spec.ts \
  web/frontend/tests/unit/config/visual-chart-gates.spec.ts \
  web/frontend/tests/unit/scripts/stable-unit-suite.spec.ts \
  web/frontend/tests/unit/scripts/validate-e2e-setup.spec.ts \
  web/frontend/tests/unit/workflows/ci-workflow-gates.spec.ts \
  web/frontend/tests/visual/components/charts/backtest.spec.ts \
  web/frontend/tests/visual/components/charts/technical-analysis.spec.ts \
  web/frontend/tests/visual/config/visual.config.ts \
  web/frontend/tests/visual/pages/dashboard.spec.ts \
  web/frontend/tests/visual/utils/helpers.ts \
  web/frontend/validate-e2e-setup.js
```

## Suggested Commit Message

```bash
git commit -m "test(frontend): consolidate ci, e2e, lighthouse, and visual gates"
```

## Suggested PR Title

`test(frontend): consolidate CI, E2E, Lighthouse, and visual gates`

## Suggested PR Body Source

- long draft: [2026-03-23-frontend-gates-pr-draft.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-23-frontend-gates-pr-draft.md)
- reviewer quick reference: [PR_GATE_QUICK_REFERENCE.md](/opt/claude/mystocks_spec/docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md)

## Final Verification Commands

Run these before pushing if you want one last confirmation on the scoped branch:

```bash
cd web/frontend
npm run test:unit:stable
npm run test:e2e:business-smoke
npm run test:e2e:axe
npm run test:e2e:lighthouse
npm run test:visual:dashboard
npm run test:visual:charts
npm run build
npm run test:type-ceiling
```

## Reviewer-Facing Evidence Snapshot

- unit: `33 files / 343 tests passed`
- business smoke: `chromium 39/39 passed`
- a11y: `chromium 2/2 passed`
- cross-browser smoke: `firefox 12/12 passed`, `webkit 12/12 passed`
- visual dashboard: `chromium 6/6 passed`
- visual charts: `chromium 4/4 passed`
- lighthouse: protected routes remained on `dashboard`, `market/realtime`, `strategy/repo`
- type ceiling: `0 / baseline 0`
