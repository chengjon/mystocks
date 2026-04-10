# OpenSpec Residual Triage: implement-optimized-testing-strategy

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对残留 OpenSpec active change 的裁定依据与处理结果，不是仓库共享规则正文。
> 当前共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该残留提案为何不再继续保留在 active list。

## Target

- Change: `implement-optimized-testing-strategy`

## Evidence

1. The change is absent from the 2026-03-27 mainline triage surfaces that were used to classify old unfinished task packs.
2. No current closeout, replacement-task, or governance execution artifact references this change by id.
3. The proposal/design still assume frontend/backend ports `3001/8000`, which drift from the current repo truth `3020/8020`.
4. The proposal creates broad parallel capabilities (`esm-compatibility-testing`, `environment-stabilization`, `layered-testing-framework`, `toolchain-integration`, `ai-assisted-testing`) instead of aligning to the current formal governance and code-quality trunks.
5. The task list remains `0/17`, with no repo-truth execution ledger or completion evidence.

## Decision

Treat `implement-optimized-testing-strategy` as a stale residual proposal, not as an active execution line.

Rationale:

- Current testing and environment governance already route through existing trunks such as `architecture/STANDARDS.md`, `openspec/specs/code-quality/spec.md`, PM2-first runtime conventions, and committed smoke / E2E workflows.
- Keeping this outdated proposal active would preserve a second, drifting planning surface for testing governance.
- If future testing strategy work is needed, it should be reopened as a new bounded change aligned to current repo truth instead of reviving this January-era package.

## Action

- Remove `openspec/changes/implement-optimized-testing-strategy/` from the active change set.
- Preserve this triage record as the historical justification for retirement.
