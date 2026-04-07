# Frontend Structure Repo-Truth Status

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


## Scope

This report records the current local execution truth for `restructure-frontend-directory` as of `2026-04-06`. It is a repo-truth status snapshot backed by Mongo work items and committed micro-batches.

## Current Execution Frontier

- Phases 0 through 5 are materially closed in local repo truth
- Phase 4 was closed through route/layout ledger reconciliation, not a second router rewrite
- Phase 5 was closed through the verified safe smoke chain and Playwright matrix / real-read evidence
- Phase 6 through Phase 9 remain open because they depend on formal review, merge, deploy, archive, and final communication gates outside the current local control plane

## Effort Accounting

- Historical planning estimate: `26 person-days (≈ 3.5 weeks)`
- Source of estimate: the original Phase 1 approval package and restructure planning artifacts
- Current measured actual: not reconstructable from the local repo and Mongo execution records alone

## Interpretation Rule

The `26 person-days` number remains useful as historical planning context, but it must not be reported as a current measured actual for the completed local execution batches. The current repo truth only supports the following defensible statement:

- the restructure was planned with an estimated effort of `26 person-days`
- the local execution has materially closed phases 0 through 5 through verified micro-batches
- the remaining phases are external workflow or follow-up gates and therefore still open

## Primary Evidence

- OpenSpec ledger:
  - `openspec/changes/restructure-frontend-directory/tasks.md`
  - `openspec/changes/restructure-frontend-directory/MIGRATION_PROGRESS.md`
- Router / verification truth:
  - `web/frontend/src/router/index.ts`
  - `web/frontend/tests/unit/config/router-full-path-uniqueness.spec.ts`
  - `web/frontend/tests/e2e/phase1-mainline-matrix.spec.ts`
  - `web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`
  - `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts`
- Repo-truth structure guide:
  - `docs/guides/frontend-structure.md`

## Remaining Gates

- Formal code review and sign-off
- Merge to `main`
- CI / staging deployment
- Post-deployment validation
- OpenSpec archive
- Final lint/spot-check and external communication tasks
