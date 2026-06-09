# Remaining Code Worktree Audit (2026-03-22)

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


This document captures the final audit state for the last two retained code worktrees after repository hygiene cleanup.

## Scope

- `.claude/worktrees/agent-a4211c9c`
- `.claude/worktrees/agent-ae2e0e74`

## Summary Verdict

### Keep For Integration Review

#### `agent-a4211c9c`

- Branch: `worktree-agent-a4211c9c`
- HEAD: `2399d3d86`
- Dirty files: 8
- Functional-tree status: `待判定（含候选有效改动，也含回退风险）`
- Recommendation: keep
- Preserved patch: `docs/reports/tasks/WORKTREE-agent-a4211c9c-PRESERVED-2026-03-22.patch`

Why:

- Contains real backend and frontend code changes, not runtime artifacts.
- Includes a `/health/ready` readiness endpoint, which aligns with `architecture/STANDARDS.md`.
- Adds API parameter validation and safer SQL handling in health/log endpoints.
- The change set is operationally meaningful and plausibly worth upstreaming.

Files:

- `web/backend/app/api/health.py`
- `web/backend/app/api/market/market_data_request.py`
- `web/backend/app/api/system/system_health.py`
- `web/backend/app/core/security.py`
- `web/backend/app/tasks/wencai_tasks.py`
- `web/frontend/src/composables/useKLineData.ts`
- `web/frontend/src/utils/cache/part-1.ts`
- `web/frontend/src/utils/chartPerformanceUtils.ts`

Diff profile:

- `172` insertions
- `138` deletions

Risk notes:

- `web/backend/app/core/security.py` changes authentication behavior toward stricter fail-closed semantics.
- Compared with current `main`, this worktree also regresses some newer implementation details:
  - removes current MongoDB readiness participation in `health.py`
  - replaces logger/error-handling paths with older `print`-style behavior in several places
  - inlines older request-model logic in `market_data_request.py`
- Any integration should run backend API tests and readiness probe checks.
- Recommended handling: selective cherry-pick/manual port, not direct wholesale merge.

### Keep Pending Product / Routing Decision

#### `agent-ae2e0e74`

- Branch: `worktree-agent-ae2e0e74`
- HEAD: `0a38f4857`
- Dirty files: 4
- Functional-tree status: `待判定（偏实验/分叉实现）`
- Recommendation: keep, but do not auto-merge
- Preserved patch: `docs/reports/tasks/WORKTREE-agent-ae2e0e74-PRESERVED-2026-03-22.patch`

Why:

- Contains real frontend code changes, not runtime artifacts.
- The route diff is large and behavior-changing.
- It rewires `/qm` routing from a dedicated nested layout to redirect-based passthrough behavior.

Files:

- `web/frontend/package.json`
- `web/frontend/src/main-standard.ts`
- `web/frontend/src/router/index.ts`
- `web/frontend/start.sh`

Diff profile:

- `17` insertions
- `240` deletions

Risk notes:

- The route edit removes a large `/qm` child-route tree and replaces it with redirect logic.
- This may be intentional cleanup, but it is product- and navigation-affecting.
- Compared with current `main`, parts of this worktree are stale or regressive:
  - `test:artdeco-style` points back to `tests/bloomberg-style.test.ts`
  - route defaults and API metadata are older than current mainline router state
- Integration would require route-by-route verification and full frontend smoke/E2E coverage.
- Recommended handling: explicit product decision first; if no one wants this route direction, discard rather than merge.

## Main-Repo State After Cleanup

Low-risk generated artifacts were removed from the main repo and corresponding ignore rules were added:

- `web/frontend/tsconfig.tsbuildinfo`
- `web/frontend/test-results.json`
- `tests/playwright-report/index.html`
- `tests/test-results/.last-run.json`
- `config/coverage.json`
- `scripts/tests/coverage.xml`
- `scripts/tests/test-directory-org/coverage.json`
- `src/gpu/api_system/coverage.xml`
- `tests/coverage.json`
- `tests/test-directory-org/coverage.json`
- `tests/e2e/test-results-realtime.json`
- `web/backend/coverage.json`
- `web/backend/coverage.xml`

Canonical retained reports:

- `reports/coverage/coverage.json`
- `reports/coverage/coverage.xml`
- `reports/coverage.json`
- `reports/coverage.xml`
- `reports/unit/test-results.xml`
- `reports/integration/test-results.xml`

## Recommended Next Action

1. Review `agent-a4211c9c` first for selective integration.
2. Treat `agent-ae2e0e74` as a routing decision branch and require explicit approval before integration or retirement.
3. Do not delete either worktree until their code changes are either migrated or explicitly discarded.

## Workspace Cleanup Decision

The worktree directories themselves may be retired after preserving:

- the branch refs
- the patch files listed above

This retires workspace artifacts without losing the uncommitted code deltas.
