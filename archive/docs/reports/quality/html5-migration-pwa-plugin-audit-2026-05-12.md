# HTML5 Migration PWA Plugin Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.1.5 Configure Vite PWA plugin for build process`
Scope: Desktop-only, repo-local audit only

## Decision

`2.1.5` remains open.

This batch records the current Vite PWA plugin state. The repo includes a PWA plugin dependency and an archived `.bak` configuration snapshot, but the active Vite config keeps the plugin disabled.

## Evidence Checked

Commands:

```bash
rg -n "vite-plugin-pwa|VitePWA|pwa|registerSW|workbox|manifest|serviceWorker|sw\\.js" web/frontend/vite.config.* web/frontend/package.json web/frontend/src web/frontend/public web/frontend/tests
sed -n '1,220p' web/frontend/vite.config.mts
sed -n '1,120p' web/frontend/vite.config.ts.pwa.bak
```

Observed repo facts:

- `web/frontend/package.json` still lists `vite-plugin-pwa` as a dependency.
- `web/frontend/vite.config.mts` contains an explicit commented import line: `// import { VitePWA } from 'vite-plugin-pwa' // PWA 禁用`.
- The active Vite config has no `VitePWA(...)` plugin in the `plugins` array.
- `web/frontend/vite.config.ts.pwa.bak` preserves an archived PWA configuration snapshot, including a former `VitePWA(...)` setup.

## Gap Summary

The repo has a PWA plugin dependency and historical configuration evidence, but the active build does not enable it. That means `vite-plugin-pwa` is not part of the current build truth.

The archived `.bak` file is useful as a reference, but it does not prove the plugin is active in the current build process.

## Task Disposition

Keep `2.1.5` unchecked until a later approved batch either enables the plugin with a verified build path or formally de-scopes it from the Desktop-only change.

Minimum future evidence should include:

- An active `VitePWA(...)` build path, or an approved de-scope note.
- A verified build run showing the plugin is actually included.
- A decision on how the archived `.bak` snapshot should be treated in the current truth model.
