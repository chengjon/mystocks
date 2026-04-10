# Adjudication: add-comprehensive-risk-management-system

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `add-comprehensive-risk-management-system` 的当前治理判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 是否应继续保留，以及应如何理解其边界。

## Decision

Keep `add-comprehensive-risk-management-system` active, but treat it as a partially landed risk-domain execution line rather than a fully unified end-to-end risk management platform.

## Why It Should Stay

- The change is structurally valid: `openspec validate add-comprehensive-risk-management-system --strict` passes.
- Current repo evidence shows real implementation already exists across risk-domain modules, backend APIs, frontend views, and tests:
  - risk domain services: `src/governance/risk_management/services/`
  - GPU risk calculators: `src/governance/risk_management/calculators/gpu_calculator/`
  - backend APIs: `web/backend/app/api/risk/{metrics,alerts,stop_loss,v31}.py`
  - compatibility/core surfaces: `web/backend/app/api/risk_management_core.py`, `web/backend/app/api/risk_management.py`
  - frontend risk views: `web/frontend/src/views/risk/` and `web/frontend/src/views/artdeco-pages/risk-tabs/`
  - tests: `tests/api/file_tests/test_risk_management_api.py`, `tests/backend/test_risk_management_core.py`, `tests/e2e/risk-monitor*.spec.*`
- Its capability boundary is still meaningful: it is the active planning line for the repo's broader risk-management surface, not a stale historical proposal.

## Why It Must Not Be Read As Complete

Current repo truth shows a partially converged surface rather than one clean completed system:

- The backend risk area is split across multiple layers and compatibility surfaces (`risk/`, `risk_management_core.py`, `risk_management.py`, `risk_v31/`, plus `.bak` residue), which means the original proposal's unified-platform framing is ahead of current structural reality.
- `web/backend/app/api/risk/metrics.py` still uses mock/fallback data source paths for some calculations, so source presence alone does not prove production-grade real-data closure.
- The repo contains backward-compatibility and fallback behavior in multiple risk services, indicating the system is still carrying transition layers rather than a fully settled canonical architecture.
- Proposal claims around WebSocket integration, Grafana integration, and end-to-end risk alerting cannot be read as fully verified governance facts solely from file presence.
- The change bundles stock risk, portfolio VaR/CVaR, stop-loss execution, alerting, frontend dashboards, and operational observability into one oversized package; the repo shows substantial slices, but not a single fully proven closure point.

## Current Repo-Truth Reading

- Treat this as an active, partially executed risk-domain mainline with substantial real code already in place.
- Treat VaR/CVaR, stop-loss, alerting, and risk dashboard surfaces as implemented to varying degrees, but not yet structurally converged into one finished platform.
- Treat compatibility files, fallback paths, and mock-backed calculations as evidence that additional bounded closeout work is still needed.

## Relationship To Current Trunks

- This change should be read as an execution line under the repo's existing governance/risk/monitoring surfaces, not as a separate truth system.
- Current repo truth lives in `src/governance/risk_management/`, the `web/backend/app/api/risk/` family, and the active frontend risk pages.
- Future closure must continue to follow `architecture/STANDARDS.md`, especially the rules on migration closure, compatibility-layer retirement, and avoiding parallel long-lived truths.

## Execution Rule For Future Sessions

- Do not retire this change as stale.
- Do not mark it complete from broad module presence alone.
- Do not continue the original checklist mechanically.
- If execution resumes, first restate the unresolved current-truth slice:
  - identify the canonical backend entry surface among `risk/`, `risk_management_core.py`, `risk_management.py`, and `risk_v31/`
  - replace or eliminate mock/fallback data paths in risk metrics where production-truth is expected
  - verify which alerting and WebSocket flows are actually wired end to end versus only scaffolded
  - scope compatibility cleanup and route convergence as bounded follow-on work before claiming full risk-platform closure
