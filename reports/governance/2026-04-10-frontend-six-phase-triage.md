# OpenSpec Residual Triage: frontend-optimization-six-phase

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `frontend-optimization-six-phase` 的裁定依据与处理结果，不是仓库共享规则正文。
> 当前共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 为何不应继续保留在 active list。

## Target

- Change: `frontend-optimization-six-phase`

## Evidence

1. The package has no `specs/` directory, so it does not provide valid OpenSpec deltas as an executable change.
2. Historical governance already classified it as an auxiliary frontend-upgrade roadmap rather than the canonical design-system execution line.
3. Historical governance explicitly converged the design-system / ArtDeco execution mainline to `implement-optimized-html-vue-artdeco-conversion`.
4. Repo audit can still find implementation evidence (layouts, TypeScript environment, chart work), which means the useful content survives in code and supporting reports rather than depending on this package staying active.

## Decision

Treat `frontend-optimization-six-phase` as a retired roadmap artifact, not as a valid active OpenSpec execution line.

## Rationale

- Keeping a no-delta roadmap in the active change set preserves a false parallel execution surface.
- The canonical active line for frontend visual / ArtDeco conversion should remain `implement-optimized-html-vue-artdeco-conversion`.
- The remaining useful information in this package is historical planning/reference material, not current active change truth.

## Action

- Remove `openspec/changes/frontend-optimization-six-phase/` from the active change set.
- Preserve this triage note as the historical explanation for retirement.
