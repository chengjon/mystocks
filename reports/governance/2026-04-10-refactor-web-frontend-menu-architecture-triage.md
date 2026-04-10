# Triage: refactor-web-frontend-menu-architecture

> **治理裁定说明**:
> 本文件记录 2026-04-10 对 `refactor-web-frontend-menu-architecture` 的退场判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 是否还应保留。

## Decision

Retire `refactor-web-frontend-menu-architecture` from the active OpenSpec frontier.

## Why It No Longer Fits The Current Frontend Truth

- The change proposes a competing frontend mainline rather than a bounded delta:
  - menu regrouping
  - layout rewrite
  - design-token system
  - command palette
  - WebSocket manager
  - performance program
  - testing infrastructure
- Its architecture direction is incompatible with the already-adjudicated ArtDeco mainline:
  - it explicitly plans to remove ArtDeco
  - it redefines the visual system as Bloomberg dark-theme first
  - it treats ArtDeco as a dependency to uninstall rather than the current active conversion truth
- Current repo truth already reflects a different settled structure:
  - `web/frontend/src/router/index.ts` uses a 7-domain navigation model, not the proposal's 6-domain architecture
  - `web/frontend/src/layouts/MenuConfig.ts` is the current menu SSOT
  - `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` and existing command-palette implementations show that some ideas were absorbed piecemeal without this change remaining the canonical plan
- Keeping this change active would create direct competition with `implement-optimized-html-vue-artdeco-conversion`, which has already been adjudicated as the only active frontend visual-conversion mainline.

## Relationship To Current Repo Evidence

- Some concepts from this package were partially realized in code, but not under this package's full target architecture.
- The change's remaining scope is too broad, too stale, and too contradictory to be treated as an executable current proposal.
- If future frontend navigation or layout convergence is needed, it should be proposed again from current router/menu/layout truth instead of reviving this pre-convergence package.

## Retirement Mode

- Retire by removing the stale active change directory after this triage record is committed.
- Do not keep it as an active umbrella, because its retained scope would continue to compete with the current approved frontend ArtDeco execution line.
