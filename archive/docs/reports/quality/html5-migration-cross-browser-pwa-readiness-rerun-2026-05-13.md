# HTML5 Migration Cross-Browser PWA Readiness Rerun

Date: 2026-05-13

Change: `implement-html5-migration-experience-optimization`

Scope: Current repo-local readiness check for task `3.2.2`; this is not a cross-browser PWA acceptance result.

## Checks

Commands / inspections:

```bash
cd web/frontend
npx playwright --version
npx playwright test --config playwright.config.ts tests/html5-runtime-acceptance.test.ts --list
```

Configuration inspected:

- `web/frontend/playwright.config.ts`
- `web/frontend/playwright.config.js`

## Result

- Playwright version: `1.57.0`
- `playwright.config.ts` project list for HTML5 runtime acceptance: `chromium`
- `playwright.config.js` project list: `chromium`, `firefox`, `webkit`
- `playwright.config.js` explicitly sets `serviceWorkers: "block"`
- `html5-runtime-acceptance.test.ts` lists 11 tests, all under `chromium`

## Disposition

`3.2.2` remains open.

The existing HTML5 runtime acceptance harness is Chromium-only. The general E2E config has Firefox/WebKit projects, but blocks service workers, so it cannot prove PWA behavior across browsers. Therefore current repo-local evidence is not sufficient for Chrome / Firefox / Safari / Edge PWA validation.

Future closure requires a service-worker-enabled cross-browser matrix with real browser/project results and clear notes for unsupported or unavailable browsers.

