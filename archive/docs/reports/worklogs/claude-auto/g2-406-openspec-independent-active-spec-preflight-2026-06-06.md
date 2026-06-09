# G2.406 OpenSpec Independent Active Spec Preflight

Date: 2026-06-06
Scope: no-source preflight for remaining independent untracked active spec additions after the broker/QMT safety cluster.

## Scope

This preflight covers the five residual untracked active spec directories called out by G2.398 as independent tooling / runtime / analysis specs:

- `openspec/specs/codex-task-looping/spec.md`
- `openspec/specs/containerized-runtime-deployment/spec.md`
- `openspec/specs/frontend-audit-orchestration/spec.md`
- `openspec/specs/kronos-integration-contract/spec.md`
- `openspec/specs/portfolio-attribution-analysis/spec.md`

The broker/QMT safety files are out of scope for this node and have already been accepted through dedicated packages.

## Evidence

- HEAD at preflight: `5d92fc67a`
- `openspec validate --specs --strict`: `47 passed, 0 failed`
- `openspec validate --changes --strict`: `16 passed, 0 failed`
- All five capabilities are visible in `openspec list --specs`.
- All five files are untracked active spec additions under `openspec/specs/**`.

| Capability | Status | Requirements | Scenarios | Archive delta origin | Notes |
|---|---:|---:|---:|---|---|
| `codex-task-looping` | `??` | 4 | 5 | `2026-05-12-add-codex-ralph-loop-plugin` | Repo-local Codex task loop plugin contract. |
| `containerized-runtime-deployment` | `??` | 4 | 8 | `2026-05-12-add-containerized-runtime-deployment-capability` | Containerized runtime deployment and smoke evidence contract. |
| `frontend-audit-orchestration` | `??` | 7 | 11 | `2026-05-12-add-page-audit-orchestration-governance` | Page-audit orchestration governance contract. |
| `kronos-integration-contract` | `??` | 8 | 14 | `2026-05-12-add-kronos-integration-contract` | Kronos integration boundary and adapter contract. |
| `portfolio-attribution-analysis` | `??` | 6 | 11 | `2026-05-12-add-portfolio-attribution-analysis` | Portfolio attribution analysis capability contract. |

## Decision

These files share the same permission state (`no-source` evidence now, source acceptance still pending) and the same mechanical shape (single active spec additions), but they do not share a single product or safety domain.

Do not accept all five in one source-authorized commit. Accept them as independent one-file spec packages so each package has a precise allowlist and an isolated GitNexus staged detection result.

## Proposed Source-Authorized Packages

1. `G2.407 openspec codex task looping spec acceptance`
   - `openspec/specs/codex-task-looping/spec.md`
2. `G2.408 openspec containerized runtime deployment spec acceptance`
   - `openspec/specs/containerized-runtime-deployment/spec.md`
3. `G2.409 openspec frontend audit orchestration spec acceptance`
   - `openspec/specs/frontend-audit-orchestration/spec.md`
4. `G2.410 openspec kronos integration contract spec acceptance`
   - `openspec/specs/kronos-integration-contract/spec.md`
5. `G2.411 openspec portfolio attribution analysis spec acceptance`
   - `openspec/specs/portfolio-attribution-analysis/spec.md`

## Gates For Each Acceptance Package

- Stage only the single file listed for that package.
- Run `git diff --cached --check`.
- Run `openspec validate --specs --strict`.
- Run `openspec validate --changes --strict`.
- Run GitNexus staged detection with a fresh index.
- Commit only if risk is acceptable and the staged allowlist still matches exactly.
