# HTML5 Migration Accessibility Tooling Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.8.5 Test with accessibility tools`
Scope: Desktop-only, repo-local audit only

## Decision

`2.8.5` remains open.

This batch records the current accessibility tooling surface. The repo has an axe-based smoke test wired into frontend scripts and CI, plus Lighthouse accessibility measurements in the broader performance smoke path. It does not yet have WAVE integration, a full seven-domain accessibility audit matrix, complete WCAG 2.1 AA coverage, or quantified accessibility-improvement evidence.

## Evidence Checked

Commands:

```bash
rg -n "test:e2e:axe|axe|WAVE|wave|@axe-core|accessibility-smoke|accessibility|pa11y|lighthouse|categories:accessibility|serious|critical" web/frontend/package.json web/frontend/tests .github/workflows/frontend-testing.yml openspec/changes/implement-html5-migration-experience-optimization docs/reports/quality
sed -n '1,460p' web/frontend/tests/e2e/accessibility-smoke.spec.ts
node -e "const p=require('./web/frontend/package.json'); console.log(JSON.stringify(Object.fromEntries(Object.entries(p.scripts||{}).filter(([k])=>k.includes('axe')||k.includes('access')||k.includes('lighthouse')||k.includes('wave'))), null, 2)); console.log('deps', Object.keys({...p.dependencies,...p.devDependencies}).filter(k=>/axe|pa11y|wave|lighthouse/i.test(k)).sort())"
```

Observed repo facts:

- `web/frontend/package.json` exposes `test:e2e:axe`, which runs `playwright test --config playwright.config.js --project=chromium tests/e2e/accessibility-smoke.spec.ts`.
- `web/frontend/package.json` includes `@axe-core/playwright` and `lighthouse`; it does not expose a WAVE or pa11y script.
- `.github/workflows/frontend-testing.yml` includes a `Run axe accessibility smoke` step that runs `npm run test:e2e:axe`.
- `web/frontend/tests/e2e/accessibility-smoke.spec.ts` covers four smoke pages: `/login`, `/strategy/repo`, `/risk/overview`, and `/trade/terminal`.
- The current axe helper fails only `serious` and `critical` violations and explicitly disables `color-contrast`.
- The smoke uses `.include("main")` for the authenticated representative pages, which is useful for main-content scanning but not equivalent to full-page or full-route inventory coverage.

## Gap Summary

The existing axe smoke gate is useful and already CI-visible, but it is intentionally narrow. It does not cover all seven canonical domains, all routed page states, dialogs, tables, chart surfaces, filters, trading forms, or error/loading/empty states.

WAVE is not integrated in the current repo-local tooling surface. No WAVE command, dependency, generated report, or workflow step was found in this audit.

The current axe threshold ignores minor/moderate findings and disables color-contrast. That is a reasonable smoke-test boundary, but it cannot be used to claim WCAG 2.1 AA closure or quantified accessibility improvement.

Lighthouse is present and provides accessibility category signals in the broader smoke path, but Lighthouse accessibility scores are not a replacement for WAVE/axe route inventory, keyboard-only tests, screen-reader acceptance, or manual review.

## Task Disposition

Keep `2.8.5` unchecked until a later approved batch defines and executes a complete accessibility tooling matrix.

Minimum future evidence should include:

- A declared route/component coverage matrix for accessibility tooling.
- WAVE integration or a documented approved alternative.
- Axe coverage beyond four smoke pages, including representative dialogs, tables, forms, charts, loading/error/empty states, and the active layout.
- A decision on whether `color-contrast`, minor, and moderate violations are in or out of scope.
- Quantified before/after or baseline accessibility results, if the task continues to claim quantitative improvement.
