# Frontend View Governance A4 SkeletonUsage Archive Prep

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for `A4-skeleton-usage-archive-prep`.

This package does not move files, edit runtime code, or retire guards.

## Candidate

| File | Classification | Route/menu status | Guard status | Proposed lifecycle |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/SkeletonUsage.vue` | `candidate-review/demo-sandbox` | No active router/menu owner found in focused search | Direct package target-file guard, workflow path-scope guard, tokenization unit spec, and workflow gate unit spec | Not execution-approved until guard successor is defined |

## Evidence

Focused active-reference search found no route/menu owner for `SkeletonUsage.vue`.

Direct guard owners found:

- `web/frontend/package.json` contains `--target-file src/views/SkeletonUsage.vue` in `lint:artdeco:changed`.
- `.github/workflows/frontend-testing.yml` treats `web/frontend/src/views/SkeletonUsage.vue` as an ArtDeco scope input.
- `web/frontend/tests/unit/config/skeleton-usage-tokenization.spec.ts` reads `src/views/SkeletonUsage.vue` directly.
- `web/frontend/tests/unit/workflows/ci-workflow-gates.spec.ts` asserts both the package guard and workflow path guard contain `SkeletonUsage.vue`.

Functional asset assessment:

- The page is a root-level visual demo for `ArtDecoSkeleton`, not a canonical business page.
- The reusable capability is `web/frontend/src/components/artdeco/core/ArtDecoSkeleton.vue`, not this demo shell.
- The page currently provides a convenient tokenization regression fixture for skeleton sizing expressions.

## Successor Requirement Before Execution

Do not archive `SkeletonUsage.vue` until one of these successor paths is selected:

1. Move the tokenization fixture to a component-owned guard that reads `ArtDecoSkeleton.vue` and a small dedicated fixture under tests.
2. Keep a minimal non-routed fixture under `web/frontend/tests/fixtures/` and update package/workflow guards to that fixture.
3. Defer archive and leave `SkeletonUsage.vue` active as a guard anchor until ArtDeco skeleton component coverage is migrated.

## Proposed Mutation Scope If Approved Later

If a successor guard is approved:

- Move `web/frontend/src/views/SkeletonUsage.vue` to `archive/web/frontend/src/views/root-sandbox/skeleton-usage/SkeletonUsage.vue`.
- Add an archive README with restore rules and successor guard references.
- Retire only the direct package target-file guard and workflow path-scope guard for `SkeletonUsage.vue`.
- Replace or retire `skeleton-usage-tokenization.spec.ts` only after equivalent tokenization coverage exists elsewhere.
- Update `ci-workflow-gates.spec.ts` only for the intentionally changed package/workflow guard expectations.

## Required Execution Gates

- GitNexus impact for `SkeletonUsage.vue`, `skeleton-usage-tokenization.spec.ts`, and relevant workflow guard tests before mutation.
- Exact active-reference search after the move.
- Successor guard proof for ArtDeco skeleton tokenization.
- OpenSpec strict validation.
- Markdown governance gate for archive README, execution report, prep report, and `tasks.md`.
- `git diff --cached --name-status`.
- `git diff --cached --check`.
- `gitnexus_detect_changes(scope="staged")`.

## Decision

This candidate is ready for a guard-successor decision, not direct archive execution. The safe next step is to decide whether to migrate skeleton token/workflow coverage to component-owned tests or defer this page.
