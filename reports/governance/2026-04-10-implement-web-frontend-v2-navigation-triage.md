# Triage: implement-web-frontend-v2-navigation

> **治理裁定说明**:
> 本文件记录 2026-04-10 对 `implement-web-frontend-v2-navigation` 的退场判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 是否还应保留。

## Decision

Retire `implement-web-frontend-v2-navigation` from the active OpenSpec frontier.

## Why It Cannot Stay Active

- The change is not structurally valid anymore: `openspec validate implement-web-frontend-v2-navigation --strict` fails with `No delta sections found`.
- The proposal, design, tasks, and supporting reports still anchor on stale runtime assumptions such as FastAPI port `8000` and PM2 process `mystocks-frontend-prod`, which conflict with the current repo baseline `8020/3020` and current PM2-first execution guidance.
- The change carries self-conflicting status evidence:
  - it is still listed as active by `openspec list`
  - historical status reports inside and outside the change already describe it as archived or fully completed
- Current frontend repo truth does not match the change's claimed route-integration target:
  - canonical navigation is now driven by `web/frontend/src/router/index.ts`
  - menu truth is now `web/frontend/src/layouts/MenuConfig.ts`
  - layout truth is now `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`
  - the expected large-scale ArtDeco child-route mapping is not the active routing model

## Relationship To Surviving Frontend Lines

- `implement-optimized-html-vue-artdeco-conversion` remains the canonical active visual / ArtDeco conversion line.
- The V2 navigation package should not compete with that mainline or redefine current router/menu truth.
- Any remaining navigation work should be handled either in the surviving ArtDeco mainline or in a new narrower proposal aligned with current repo truth.

## Retirement Mode

- Retire by removing the stale active change directory after this triage record is committed.
- Do not salvage or archive this change as-is, because preserving an invalid delta package as active history would keep contradictory execution truth in the frontier.
