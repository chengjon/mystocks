# HTML5 Migration Accessibility Axe Smoke Rerun

Date: 2026-05-13

Change: `implement-html5-migration-experience-optimization`

Scope: Current repo-local accessibility smoke rerun for task `2.8.5`; this is not a full accessibility closure.

## Command

```bash
cd web/frontend
PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:axe
```

Script resolved to:

```bash
playwright test --config playwright.config.js --project=chromium tests/e2e/accessibility-smoke.spec.ts
```

## Environment Readiness

- `mystocks-backend`: PM2 online
- `mystocks-frontend`: PM2 online
- Frontend probe: `http://127.0.0.1:3020/` returned `HTTP/1.1 200 OK`
- Backend readiness probe used: `http://127.0.0.1:8020/health/ready`; HEAD probe returned `405 Method Not Allowed`, so this rerun should not be read as a backend readiness validation.

## Result

- Exit status: `0`
- Browser project: `chromium`
- Test file: `tests/e2e/accessibility-smoke.spec.ts`
- Reported result: `3 passed`, `1 flaky`

The flaky case was:

```text
[chromium] › tests/e2e/accessibility-smoke.spec.ts › Accessibility smoke › strategy repository page has no serious accessibility violations
```

The failing retry point waited for:

```text
getByRole("heading", { level: 1, name: "策略仓库工作台" })
```

and did not find the heading within the 5 second expectation window.

## Disposition

This rerun refreshes local axe-smoke evidence only.

`2.8.5` remains open because:

- the current gate covers only the existing smoke file, not a full route/component accessibility matrix;
- the result includes one flaky case;
- WAVE / pa11y or equivalent tooling is still not wired as full evidence;
- WCAG 2.1 AA closure is still not established.

