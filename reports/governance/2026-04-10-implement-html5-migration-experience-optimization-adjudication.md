# Adjudication: implement-html5-migration-experience-optimization

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `implement-html5-migration-experience-optimization` 的当前治理判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 是否应继续保留，以及应如何理解其边界。

## Decision

Keep `implement-html5-migration-experience-optimization` active, but treat it as a mixed package that must be read as two different scopes rather than one unified completed program.

## Why It Should Stay

- The change is structurally valid: `openspec validate implement-html5-migration-experience-optimization --strict` passes.
- Current repo evidence shows meaningful partial implementation already exists for the HTML5 / platform-feature side:
  - `web/frontend/public/manifest.json`
  - `web/frontend/public/sw.js`
  - `web/frontend/src/utils/indexedDB.ts`
  - `web/frontend/src/utils/workersManager.ts`
  - worker assets under `web/frontend/public/workers/`
- This means the proposal is not a fully obsolete roadmap artifact.

## Why It Must Not Be Read As A Single Current-Truth Plan

The package mixes two different concerns that no longer move together cleanly:

1. frontend architecture/menu/layout optimization
2. advanced HTML5 / PWA / platform features

Current repo truth shows these two halves have diverged:

- Menu/layout truth is governed by current router/layout/menu mainlines, not by this package alone.
- PWA and HTML5 feature artifacts exist, but the original proposal still overclaims missing foundations such as "No PWA support" and "Only localStorage".
- Historical audit also shows several promised capabilities remain unverified or incomplete, including push subscription backend support, manifest screenshot assets, and various modern browser API integrations.

## Practical Interpretation

- Keep the change active for the still-relevant HTML5/PWA/platform-feature slice.
- Do not treat it as the canonical plan for frontend menu/layout convergence.
- Do not treat the presence of manifest/service-worker/IndexedDB files as proof that the full package is complete.

## Execution Rule For Future Sessions

- Do not retire this change as stale.
- Do not continue the original checklist mechanically from top to bottom.
- If execution resumes, first split remaining current-truth work into bounded slices such as:
  - PWA/runtime capability verification and completion
  - IndexedDB / worker integration hardening
  - push notification and offline support gaps
  - browser-API and accessibility items that still have real product value
- Frontend menu/layout work should continue under the current router/menu/layout governance lines instead of being reintroduced here as parallel truth.
