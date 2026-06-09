# Risk Orphan Static Shells Truth Audit

## Scope
- Files:
  - `web/frontend/src/views/risk/Portfolio.vue`
  - `web/frontend/src/views/risk/Positions.vue`
- Synthetic route key: `/secondary/risk-orphan-static-shells`
- Family: `local-action-and-execution-truth`

## Problem
- These pages were not active route truth or imported by active owners.
- They still rendered standalone `Coming Soon` / `Phase 7` placeholders for portfolio-risk and position-risk analysis.
- Keeping these placeholders as independent child pages would preserve non-canonical risk entry points without verified route ownership.

## Repair
- Converted both pages to honest static shells.
- Preserved files for compatibility and linked users to canonical `/risk/management` and `/risk/position`.
- Did not add a new risk API, store, snapshot, request badge, freshness strip, or shell-owned execution state.

## Verification
- RED:
  - `cd web/frontend && npx vitest run tests/unit/config/risk-orphan-static-shells.spec.ts` failed because the old pages lacked `legacy-static-shell`.
- GREEN:
  - `cd web/frontend && npx vitest run tests/unit/config/risk-orphan-static-shells.spec.ts` passed (`1/1`).
- Source scan:
  - `rg "Coming Soon|Phase 7|el-alert|Portfolio Risk Analysis|Position Risk Analysis" web/frontend/src/views/risk/Portfolio.vue web/frontend/src/views/risk/Positions.vue` produced no matches.

## Outcome
- The retired risk child pages no longer claim standalone Phase roadmap placeholder truth.
