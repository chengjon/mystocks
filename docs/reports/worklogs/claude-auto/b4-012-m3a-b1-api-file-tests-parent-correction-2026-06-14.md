# B4.012-M3a-B1 API file tests parent gate correction

Date: 2026-06-14
Branch: wip/root-dirty-20260403
Scope: governance metadata only

## Summary

Merged the external handoff at `/tmp/handoff-8kS0u1.md` into the current B4.012-M3a tests residual governance line.

The handoff identified a metadata caution: `b4-012-m3a-b1-api-file-tests-authorization` was prepared as the first implementation authorization packet under `b4-012-m3a-b-api-backend-contract-tests-split`, but its `parent` field was empty.

This correction updates only the Function Tree node metadata:

- `b4-012-m3a-b1-api-file-tests-authorization`
  - `parent`: `b4-012-m3a-b-api-backend-contract-tests-split`
  - status remains `authorization-prepared`
  - `source_edits_authorized` remains `false`
  - allowed paths remain unchanged

## Boundary

No source, test, runtime, OpenSpec, frontend, backend, ST-HOLD, marketKlineData, or external dirty files were edited.

The existing dirty test files under `tests/api/file_tests/` remain untouched and unstaged. The external untracked inventory worklog remains untouched and unstaged.

## Reason

The B1 authorization packet is a child of the M3a-B no-source split. Correcting the parent relationship keeps the Function Tree hierarchy aligned before any later explicit source/test authorization review.

## Verification Plan

- `ft-governance validate`
- `git diff --cached --check`
- GitNexus staged verification
- GitNexus staged change detection
- OPENDOG verification blocker check
