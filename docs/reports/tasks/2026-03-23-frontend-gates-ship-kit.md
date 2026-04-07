# Frontend Gates Ship Kit

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## Current State

- current_branch: `main`
- note: the worktree contains many unrelated pre-existing changes outside this frontend gate scope
- recommendation: create a dedicated branch before staging only the files listed below
- additional_note: current git index also contains unrelated staged changes; avoid plain `git commit` from this checkout

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

## Patch Export

A scoped patch for this change set has been exported to:

```text
/tmp/frontend-gates.patch
```

This is the safest route if you want to apply the frontend gate changes in a clean worktree or another clone:

```bash
git apply /tmp/frontend-gates.patch
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
