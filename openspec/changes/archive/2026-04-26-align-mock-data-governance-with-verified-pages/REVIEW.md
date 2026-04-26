# Review: Align Mock Data Governance With Verified Pages

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Reviewer: Claude | Date: 2026-04-25
> Reviewed against: `docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md`, `openspec/specs/api-integration/spec.md`, current frontend source code

---

## Overall Verdict

**Direction correct, 4 issues to address before approval.**

The proposal's core thesis is well-aligned with `MOCK_DATA_USAGE_RULES.md` and the existing `api-integration` spec. Code-level verification confirms the drift the proposal identifies. The main gap is insufficient separation of the three distinct mock-routing layers currently in the codebase.

---

## 1. Proposal Claims vs. Code Reality

| Claim | Code Evidence | Verdict |
|-------|---------------|---------|
| Frontend adapters silently fall back to mock | `strategyAdapter.ts:30-32` (`adaptStrategyList`), `258-268` (`adaptStrategyDetail`); `marketAdapter.ts:54-56` (`adaptMarketOverview`), `107-109` (`adaptFundFlow`), `181-183` (`adaptKLineData`) — all return mock payload on API failure | **Confirmed** |
| `VITE_USE_MOCK_DATA` should be single execution truth | `apiClient.ts:165-167` routes to `mockApiClient`; `useBackendReadiness.ts:44` uses it for mock-mode detection | **Confirmed** |
| `VITE_APP_MODE` still active as switching truth | `strategyService.ts:36` (`const appMode = import.meta.env.VITE_APP_MODE \|\| 'real'`) drives endpoint selection between `/mock/strategy` and `/v1/strategy`; `ENVIRONMENT_SWITCHING_GUIDE.md` documents it | **Confirmed** |
| `useBackendReadiness` has mock fallback problem | Lines `76-84`, `96-106`: returns `usingMockFallback: true` with explicit mode labels and Chinese-language user-visible messages | **Overstated** — already well-governed with explicit flags |

---

## 2. Compliance with MOCK_DATA_USAGE_RULES

No conflicts. Direct alignment on all core rules:

| Rule (MOCK_DATA_USAGE_RULES) | Proposal Coverage |
|------------------------------|-------------------|
| "verified 页面不得在同一路径上真实接口失败后默默返回 mock 数据" | Tasks 2.1, 2.2 remove adapter silent fallback |
| "环境与开关" section: `VITE_USE_MOCK_DATA` is current truth, `VITE_APP_MODE` is historical | Tasks 2.3, 3.1 collapse onto `VITE_USE_MOCK_DATA` |
| "允许使用 Mock 的场景": explicit mock mode and automation isolation preserved | Design decision: "Preserve explicit mock mode, but prohibit silent same-path mock substitution" |
| "反模式: 页面内 if request failed -> return mockRows" | Exactly the pattern in current adapters, targeted for removal |

---

## 3. Issues to Address

### Issue 1: Three-layer mock mechanism not separated (Severity: High)

The proposal treats "mock fallback" as a single problem, but the codebase has three independent layers:

| Layer | File | Mechanism | Switch | Current Status |
|-------|------|-----------|--------|---------------|
| **Client layer** | `apiClient.ts:165-167` | Routes ALL requests to `mockApiClient` when enabled | `VITE_USE_MOCK_DATA` | Compliant — explicit mode switch |
| **Service layer** | `strategyService.ts:36-45` | Constructor selects `/mock/strategy` vs `/v1/strategy` endpoint based on env var | `VITE_APP_MODE` | **Dual-truth drift** — independent switch not governed by client layer |
| **Adapter layer** | `strategyAdapter.ts`, `marketAdapter.ts` | On API failure, returns mock payload regardless of any env var | None (always active) | **Silent fallback violation** — no switch at all |

**Dual-truth conflict scenario**:
- `VITE_USE_MOCK_DATA=true` + `VITE_APP_MODE=real` → `apiClient` routes everything to mock, but `strategyService` thinks it's calling real endpoints
- `VITE_USE_MOCK_DATA=false` + `VITE_APP_MODE=mock` → `strategyService` selects mock endpoint, but `apiClient` attempts real HTTP request to that endpoint

**Recommendation**: `design.md` should describe these three layers explicitly. `tasks.md` tasks should identify which layer each task targets.

### Issue 2: Open Questions should be pre-answered (Severity: Medium)

From `design.md`:

> "Which currently active pages still rely on adapter-level mock substitution despite being tracked as verified?"

This determines the actual scope of tasks 2.1 and 2.2. It should not remain open at approval time.

**Recommendation**: Either answer this question in the proposal itself (by auditing current page status), or restructure it as a mandatory pre-requisite output of task 1.1 with explicit deliverable criteria.

### Issue 3: New spec requirement is vague (Severity: Medium)

From `specs/api-integration/spec.md` (ADDED requirements):

> "The frontend SHALL use a single active execution truth for explicit mock-mode switching and SHALL keep historical switching models out of current verified-page runtime behavior."

"historical switching models" is undefined. It should specifically reference `VITE_APP_MODE` usage in `strategyService.ts` constructor.

**Recommendation**: Replace with concrete wording:

> The frontend SHALL NOT use `VITE_APP_MODE` or any service-level mock/real endpoint switching. All mock/real routing SHALL go through the shared `apiClient` via `VITE_USE_MOCK_DATA`.

### Issue 4: `useBackendReadiness` risk overstated (Severity: Low)

`useBackendReadiness.ts` already:
- Exposes `usingMockFallback` flag explicitly (lines 69-70, 81-84)
- Distinguishes `mockModeEnabled` (explicit mock) from `allowAutomationFallback` (automation session)
- Returns user-visible Chinese messages indicating current mode

This is significantly more governed than the adapter-layer silent fallback.

**Recommendation**: In both `proposal.md` (affected code list) and `tasks.md` (task 2.4), downgrade this file from "requires modification" to "confirm compliance only".

---

## 4. Per-Task Recommendations

| Task | Recommendation |
|------|---------------|
| **1.1** | Add deliverable: produce a table mapping each verified page to its adapter, showing whether silent mock fallback exists |
| **1.2** | Add `strategyService.ts` `VITE_APP_MODE` branching as a third class: "service-level dual-truth drift" |
| **2.1 / 2.2** | Clarify modification direction: adapters should return empty data + propagate error state (not mock payloads); consuming views/stores are responsible for rendering loading/error/empty states |
| **2.3** | Specify: remove `VITE_APP_MODE` branch from `strategyService.ts` constructor, hardcode `/v1/strategy` as endpoint, let mock/real switching be handled entirely by `apiClient`'s `VITE_USE_MOCK_DATA` gate |
| **2.4** | Downgrade to "confirm compliance" — `useBackendReadiness` already has explicit fallback labeling |
| **3.4** | Audit ledger should include three-layer classification: client layer / service layer / adapter layer mock routing status per page |

---

## 5. Summary

| Dimension | Assessment |
|-----------|-----------|
| Alignment with MOCK_DATA_USAGE_RULES | Full compliance, no conflicts |
| Accuracy of problem identification | Core problems confirmed; three-layer mechanism needs separation |
| Completeness of scope | Good, but `strategyService.ts` dual-truth deserves equal billing with adapters |
| Spec quality (spec.md) | MODIFIED requirements are clear; ADDED requirements need concretization |
| Migration plan feasibility | Phased approach is sound; governance baseline (task 1) correctly sequenced first |
| Risk assessment | Honest about error-state surfacing risk; `useBackendReadiness` risk should be lowered |
