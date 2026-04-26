## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The repository already has a normative rule in `openspec/specs/api-integration/spec.md` that `verified` pages must not silently fall back to mock data. Updated documentation under `docs/guides/mock-data/` reinforces that rule and clarifies that mock data is for development decoupling, testing stability, and explicit mock acceptance, not for masking real-path failure.

The implementation still contains three classes of drift:

1. Frontend adapters that convert failed real responses into mock payloads.
2. Frontend service/documentation paths that still treat `VITE_APP_MODE` as an active switching truth.
3. Backend and historical docs that retain hybrid/fallback language without enough classification, increasing the risk that engineers misread approved explicit mock fallback as allowed verified-path behavior.

More concretely, the current frontend stack has three independent mock-routing layers that need to be separated in governance:

| Layer | Current file(s) | Mechanism | Current governance status |
|------|------|------|------|
| Client layer | `web/frontend/src/api/apiClient.ts` | Routes requests to `mockApiClient` when `VITE_USE_MOCK_DATA=true` | Compliant explicit mock-mode gate |
| Service layer | `web/frontend/src/api/services/strategyService.ts` | Chooses `/mock/strategy` vs `/v1/strategy` using `VITE_APP_MODE` | Dual-truth drift that must be removed |
| Adapter layer | `strategyAdapter.ts`, `marketAdapter.ts` | Returns mock payloads after failed real responses without explicit mode switch | Silent fallback violation that must be removed from verified mainline |

## Goals / Non-Goals

- Goals:
  - Make verified-page runtime behavior match the current documented governance.
  - Establish one active frontend mock switch truth: `VITE_USE_MOCK_DATA`.
  - Preserve approved controlled fallback only where the user path is explicitly mock or automation-isolated.
  - Create an implementation checklist that can be executed in phases without losing auditability.
- Non-Goals:
  - Remove every mock asset from the repository.
  - Redesign all backend data-source fallback behavior in one batch.
  - Reclassify every historical document in the repository immediately.

## Decisions

- Decision: Treat this as a cross-cutting governance alignment change under `api-integration`.
  - Why: The core mismatch is not a new feature; it is a runtime contract mismatch between documented verified-page behavior and current frontend integration behavior.

- Decision: Preserve explicit mock mode, but prohibit silent same-path mock substitution for verified pages.
  - Why: The project still needs development decoupling and stable automation modes. The issue is hidden substitution, not all mock usage.

- Decision: Use `apiClient` + `VITE_USE_MOCK_DATA` as the frontend switching truth.
  - Why: The shared client already implements this switch, and leaving service-local `VITE_APP_MODE` branching creates dual truths.

- Decision: Treat `useBackendReadiness.ts` as a compliance-confirmation surface, not a primary remediation surface.
  - Why: Its fallback is already explicitly labeled by mode and user-visible state, unlike the silent adapter fallback pattern.

- Decision: Keep a page-level audit ledger/checklist as part of rollout.
  - Why: This prevents future drift where a page is documented as verified while its runtime still behaves like pending/mock-backed.

## Risks / Trade-offs

- Risk: Removing adapter-level mock fallback may surface more visible frontend error states immediately.
  - Mitigation: Scope rollout to verified paths first and ensure views/stores already expose loading/error/empty states with request identifiers.

- Risk: Some tests or workflows currently depend on implicit mock payloads.
  - Mitigation: Reclassify those flows as explicit mock-mode tests or update them to assert visible failure states.

- Risk: Backend hybrid/fallback concepts may still confuse future work.
  - Mitigation: Document classification boundaries during rollout and defer larger backend fallback redesign to a follow-up change if needed.

## Migration Plan

1. Freeze the governance baseline: page status, current mock entrypoints, and current switching truth.
2. Audit verified pages against the three-layer client/service/adapter model and record where silent fallback still exists.
3. Remove silent mock fallback from verified-path frontend adapters.
4. Collapse frontend switching onto `VITE_USE_MOCK_DATA` through shared client usage and retire `VITE_APP_MODE` service-level branching.
5. Update docs and tests so explicit mock mode is described as explicit mock mode, not real verification.
6. Record remaining non-mainline fallback patterns as approved exceptions or follow-up debt.

## Open Questions

- Whether any backend hybrid/fallback paths should be reclassified under a separate follow-up OpenSpec change instead of this batch.
