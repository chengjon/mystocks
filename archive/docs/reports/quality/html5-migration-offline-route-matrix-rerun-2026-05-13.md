# HTML5 Migration Offline Route Matrix Rerun

Date: 2026-05-13

Change: `implement-html5-migration-experience-optimization`

Scope: Current repo-local rerun for task `3.2.1`; this is not an offline route-matrix closure.

## Full Harness Attempt

An attempt was made to run the full opt-in HTML5 runtime acceptance harness against a local Vite preview on port `4174`.

The run exceeded the tool wait window before producing a usable acceptance summary. A possible leftover preview process was cleaned up afterwards:

```text
node .../vite preview --host 127.0.0.1 --port 4174
```

The port probe after cleanup no longer returned a live preview response.

## Focused Offline Matrix Check

To avoid conflating unrelated runtime probes with `3.2.1`, the focused offline route-matrix test was rerun directly:

```bash
cd web/frontend
FRONTEND_PORT=4174 HTML5_RUNTIME_ACCEPTANCE=1 \
  npx playwright test \
  --config playwright.config.ts \
  --project=chromium \
  tests/html5-runtime-acceptance.test.ts \
  -g "records offline fallback behavior for eleven desktop routes"
```

Result:

```text
status=0
1 skipped
```

## Disposition

`3.2.1` remains open.

The focused test is still explicitly skipped/fixme in the current harness, matching the existing blocker: Desktop Chromium offline navigation attempts under `context.setOffline(true)` do not yet provide a stable 11-route service-worker-controlled matrix.

Future closure requires a real route-by-route offline matrix record covering the agreed Desktop routes, not another skipped/fixme test result.

