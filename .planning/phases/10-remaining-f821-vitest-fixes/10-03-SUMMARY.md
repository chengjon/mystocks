---
phase: 10
plan: 03
status: complete
completed: "2026-04-10"
---

# Plan 03: System Settings & DataManagement Test Realignment — Complete

## Result

All 4 vitest tests passing across both spec files. Zero unhandled rejections in full suite.

## Changes

| File | Fix |
|------|-----|
| `ArtDecoSystemSettings.spec.ts` | Added `getSystemGeneralSettingsMock` + `updateSystemGeneralSettingsMock` mocks; updated assertions to match Settings.vue (`系统配置中心`, `保存系统设置`, 3 tabs); removed stale localStorage assertion |
| `ArtDecoDataManagement.spec.ts` | Removed stale `ArtDecoDataManagementVm` interface; added mocks for `useArtDecoApi`, `dataManagementData`, `dataManagementCapabilities`; rewrote to test actual DataSource.vue rendered output |

## Verification

- `vitest run src/views/artdeco-pages/system-tabs/__tests__/` — 4/4 passed, 0 failed
- `vitest run` full suite — 0 unhandled rejections

## Self-Check: PASSED
