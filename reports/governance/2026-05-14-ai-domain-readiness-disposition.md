# 2026-05-14 AI Domain Readiness Disposition

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Scope

This disposition consolidates the follow-up work after `reports/governance/2026-05-14-ai-domain-runtime-readiness-review.md`.

It covers the `07-高级分析与AI` readiness evidence for:

- `7.1 机器学习策略`
- `7.2 批量分析`
- `7.3 情感分析`

This document does not modify `FUNCTION_TREE`, does not change the domain-level status, and does not convert external dependencies into repo-local completion claims.

## Current Decision

`07-高级分析与AI` should continue to remain:

| Domain | Current status | Disposition |
|--------|----------------|-------------|
| `07-高级分析与AI` | `🧪 实验性 / 50%` | Keep `🧪 / 50%` |

The reason is now narrower than in the initial review:

- The `7.3` runtime path defect has been fixed and verified.
- The `/ai/ml` smoke instability concern has been revalidated with repeat browser evidence.
- Remaining blockers are governance and production-readiness boundaries, not first-batch feature implementation gaps.

## Source Evidence

| Evidence | Role |
|----------|------|
| `reports/governance/2026-05-14-ai-domain-runtime-readiness-review.md` | Source review. Establishes why domain status should not be upgraded directly. |
| `527a18cc5 fix(frontend): use canonical sentiment api client` | Fixes `/ai/sentiment` double `/api` runtime path composition. |
| `reports/governance/2026-05-14-ai-sentiment-runtime-path-fix-result.md` | Records sentiment path fix verification and `2 passed` targeted browser smoke. |
| `reports/governance/2026-05-14-ai-ml-runtime-smoke-stability-result.md` | Records `/ai/ml` single-run and repeated Chromium smoke evidence. |
| `8e5a07e84 docs(governance): record ml workbench release evidence` | Records `7.1` release evidence and canonical API/page surface. |

## Finding Disposition

| Review finding | Disposition | Evidence |
|----------------|-------------|----------|
| `/ai/sentiment` requests `/api/api/v1/sentiment/market` and shows sync error | Closed | `527a18cc5`; targeted unit/component tests; `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e -- --project=chromium tests/e2e/ai-sentiment-workbench.spec.ts` -> `2 passed (9.6s)` |
| `/ai/ml` direct smoke can show skeleton/empty content or navigation timeout | Closed for current tested path and environment | `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e -- --project=chromium tests/e2e/ai-ml-workbench.spec.ts` -> `12 passed (23.6s)`; repeat run `--repeat-each=3` -> `36 passed (1.2m)` |
| `7.1` has runtime dependencies but no governed model artifact | Open | `models.total=0` in source review; requires governed artifact or explicit external-dependency decision |
| `7.2` is runtime registry evidence, not production scheduler closure | Open | Requires scheduler mutation, persistence, progress tracking, audit, and failure-recovery boundary decisions |
| `07` domain governance paths and catalog are not fully aligned with canonical `/ai/*` and `/api/v1/*` surfaces | Open | Requires dedicated `align-ai-domain-governance-status` package; do not bundle into runtime bugfixes |

## Closed Repo-Local Items

1. `fix-ai-sentiment-runtime-path`

   Status: closed.

   Outcome: `aiSentiment.ts` uses canonical `apiClient` and `/v1/sentiment/*` literals, producing runtime `/api/v1/sentiment/*` requests.

2. `stabilize-ai-ml-smoke`

   Status: closed for current tested browser path.

   Outcome: `/ai/ml` Chromium smoke passed once and under `--repeat-each=3`.

3. `restore-playwright-browser-readiness`

   Status: closed in the local environment.

   Outcome: Playwright Chromium, ffmpeg, and headless shell are installed in `/root/.cache/ms-playwright/`.

## Remaining Work

### 1. ML Artifact / External Dependency Decision

Decide whether the next milestone requires:

- a governed sample model artifact under a controlled model directory; or
- an explicit external dependency record stating that model artifacts, reproducible training datasets, and training windows are outside the current repo-local milestone.

This should not be described as “continue developing 7.1” unless new first-batch functionality is actually required.

### 2. Batch Analysis Production Boundary

Define whether `7.2` should remain runtime-registry evidence or move toward production scheduler behavior.

Minimum boundary decisions:

- task persistence;
- progress and lifecycle state;
- mutation semantics;
- audit trail;
- failure recovery;
- operational ownership.

### 3. AI Domain Governance Alignment

Prepare a separate `align-ai-domain-governance-status` package only after the two boundary decisions above are made.

Expected scope:

- `docs/FUNCTION_TREE.md` domain API prefix wording;
- `governance/function-tree/catalog.yaml` canonical entrypoints;
- cross-reference to `/ai/ml`, `/ai/batch`, `/ai/sentiment`;
- status proposal, if any, from `🧪 / 50%` to `🚧 / 60%-65%`.

## Non-Goals

- Do not upgrade `07-高级分析与AI` status in this disposition.
- Do not modify `FUNCTION_TREE` as part of this evidence consolidation.
- Do not reopen `7.1`, `7.2`, or `7.3` as broad implementation lines.
- Do not count missing model artifacts, production scheduler behavior, or real-world data sources as completed repo-local work without explicit evidence.

## Recommended Next Step

Create the smallest next work item as:

`decide-ai-domain-external-runtime-boundaries`

Purpose:

- classify ML artifacts/training datasets/training windows as repo-local or external;
- classify batch scheduler/persistence/audit as repo-local or future production scope;
- produce a yes/no gate for whether `align-ai-domain-governance-status` may proceed.
