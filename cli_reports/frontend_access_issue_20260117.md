# Frontend Access Issue Investigation Report
**Date:** 2026-01-17
**Status:** Resolved
**Investigator:** Gemini CLI

## 1. Initial Symptoms
- User reported inability to access the frontend at `http://localhost:3001`.
- Backend services appeared to be running, but PM2 status for frontend showed instability.

## 2. Root Cause Analysis

### Issue 1: PM2 Restart Loop
- **Observation:** `pm2 list` showed `mystocks-frontend-dev` with >3700 restarts.
- **Cause:** `web/ecosystem.dev.config.js` had `watch: ['src']` enabled. The startup command `npm run dev` triggers a type generation script that writes to `src/api/types`. This file write triggered the PM2 watcher, causing an immediate restart, creating an infinite loop.
- **Fix:** Disabled PM2 watcher (`watch: false`) in `web/ecosystem.dev.config.js` to rely on Vite's internal Hot Module Replacement (HMR).

### Issue 2: Import Path Error
- **Observation:** Vite build error: `Failed to resolve import "./services/versionNegotiator.js"`.
- **Cause:** The file was a TypeScript file (`versionNegotiator.ts`), but the import in `main.js` explicitly used the `.js` extension, which Vite could not resolve.
- **Fix:** Updated `main.js` to import from `./services/versionNegotiator` (without extension), allowing Vite to resolve the `.ts` file correctly.

### Issue 3: CommonJS/ESM Interop (Day.js)
- **Observation:** Browser console error: `Uncaught SyntaxError: The requested module ... does not provide an export named 'default'`.
- **Cause:** `dayjs` is a CommonJS module. When imported in an ES Module context without proper optimization, Vite failed to synthesize the default export.
- **Fix:** Added `dayjs` to `optimizeDeps.include` in `vite.config.ts` to force pre-bundling and ESM conversion.

### Issue 4: Dynamic Import Failure (Day.js Plugin)
- **Observation:** Browser console error: `Uncaught SyntaxError: ... dayjs/plugin/localeData.js ... does not provide an export named 'default'`.
- **Cause:** Similar to Issue 3, the specific plugin module also required pre-bundling.
- **Fix:** Added `dayjs/plugin/localeData` to `optimizeDeps.include` in `vite.config.ts`.

### Issue 5: Missing Vue Components
- **Observation:** Build error: `The plugin "vite:dep-scan" was triggered by this import...` pointing to missing files.
- **Cause:** `ArtDecoTradingCenter.vue` referenced several components (`ArtDecoStatusIndicator`, `ArtDecoBreadcrumb`, `ArtDecoFooter`, `ArtDecoLoadingOverlay`) that did not exist in the codebase.
- **Fix:** Created the missing Vue components in `web/frontend/src/components/artdeco/core/`.

## 3. Current Status
- **Service Status:** `mystocks-frontend-dev` is ONLINE (pid: 2).
- **Network:** Port 3001 is listening (`netstat` confirmed).
- **Logs:** No critical errors in PM2 logs.
- **Access:** `curl http://localhost:3001` returns the valid HTML index page.
- **Note:** `unplugin-vue-components` warnings about naming conflicts persist but are non-blocking.

## 4. Verification Steps
1. Run `pm2 list` to confirm status.
2. Check `http://localhost:3001` in the browser.
3. Verify that the loading spinner appears (from the newly created overlay component) and then the application loads.
