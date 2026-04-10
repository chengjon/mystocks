# Adjudication: implement-optimized-html-vue-artdeco-conversion

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `implement-optimized-html-vue-artdeco-conversion` 的主线定位，不是仓库共享规则正文。
> 当前共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 在当前前端治理中的角色。

## Decision

Keep `implement-optimized-html-vue-artdeco-conversion` as the canonical active execution line for the frontend ArtDeco visual / design-system conversion track.

## Evidence

- The change is structurally valid in OpenSpec.
- Historical governance already identified it as the primary successor for the HTML→Vue + ArtDeco visual-quality line.
- Competing roadmap-style package `frontend-optimization-six-phase` has now been retired from the active set.
- Current repo audit still finds both implementation evidence and open gaps, which means this line remains active rather than complete.

## Constraint

This change should be treated as the only active frontend visual-conversion mainline for this area.

Related frontend changes may still exist, but they should not redefine the ArtDeco visual-execution truth unless they explicitly supersede this line through a new approved proposal.
