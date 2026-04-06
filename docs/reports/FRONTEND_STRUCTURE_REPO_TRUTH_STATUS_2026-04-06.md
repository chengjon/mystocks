# Frontend Structure Repo-Truth Status

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
