# Change: Align Mock Data Governance With Verified Pages

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The repository's updated mock-data documentation now defines a stricter execution rule: mock data is allowed for explicit mock acceptance, development decoupling, and test isolation, but it must not remain a silent success-path fallback for `verified` pages. Current frontend adapters, environment-switching docs, and some service-layer switching logic still preserve the older "real fails -> use mock" behavior and an outdated `VITE_APP_MODE` switching model.

Without a governed change, the project risks continuing to claim "real path verified" while runtime behavior still hides backend failures behind mock payloads.

The runtime drift is not a single mechanism. It currently exists at three separate layers:

- client layer: `apiClient.ts` explicitly routes through `mockApiClient` when `VITE_USE_MOCK_DATA=true`
- service layer: `strategyService.ts` independently selects `/mock/strategy` vs `/v1/strategy` through `VITE_APP_MODE`
- adapter layer: strategy and market adapters return mock payloads on failure without any explicit mode switch

This proposal aligns those three layers so only the explicit client-layer switch remains as the current frontend execution truth for mock mode.

## What Changes

- Enforce that `verified` pages do not silently fall back to mock payloads on the same user path.
- Remove service-level dual-truth switching in `strategyService.ts` so frontend mock routing is governed only by the shared client layer.
- Align frontend mock switching on `VITE_USE_MOCK_DATA` as the active execution truth, while downgrading `VITE_APP_MODE` to historical/legacy status.
- Retain controlled fallback only for explicit mock acceptance mode and approved automation/readiness isolation flows.
- Update implementation and documentation to distinguish:
  - client-layer explicit mock mode
  - service-layer dual-truth drift
  - adapter-layer silent fallback violation
  - explicit mock mode
  - real mainline verification
  - historical fallback/hybrid behavior that must not remain in verified primary flows
- Add a governance inventory/checklist so page-level mock usage can be audited against `verified/pending` status and mock-routing layer classification.

## Impact

- Affected specs:
  - `api-integration`
- Affected code:
  - `web/frontend/src/api/adapters/strategyAdapter.ts`
  - `web/frontend/src/api/adapters/marketAdapter.ts`
  - `web/frontend/src/api/services/strategyService.ts`
  - `web/frontend/src/api/apiClient.ts`
  - `web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`
  - `docs/guides/mock-data/*`
- Affected test/documentation surfaces:
  - strategy/market frontend adapter tests
  - E2E or smoke documentation that still describes mock-path success as real verification
  - verified-page audit output mapping each page to adapter/service/client mock-routing status
