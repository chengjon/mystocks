# OpenSpec Residual Triage: integrate-fullstack-platform

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `integrate-fullstack-platform` 的裁定依据与处理结果，不是仓库共享规则正文。
> 当前共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 为何不应继续保留在 active list。

## Target

- Change: `integrate-fullstack-platform`

## Evidence

1. `openspec validate integrate-fullstack-platform --strict` fails because its spec files do not use valid OpenSpec delta format.
2. The proposal/design/specs still assume the old runtime contract `3000/8000`, while the current repo truth is `3020/8020` and PM2-first service management.
3. The change expects a root-level `run_platform.sh`, but the repository truth uses `scripts/runtime/run_platform.sh`.
4. The package still assumes broad Docker-orchestrated startup sequencing, while current repo governance and runtime conventions have already converged around PM2-first execution.
5. Repo audit finds partial integration evidence (router wiring, API client, startup script), but also major drift: route names/paths differ, env-file assumptions differ, and completion claims are not fully verifiable.

## Decision

Treat `integrate-fullstack-platform` as a stale residual integration proposal, not as a valid active execution line.

## Rationale

- Keeping an invalid-delta package in the active set preserves a false planning surface.
- The remaining useful integration truth already lives in code, PM2/runtime scripts, router/menu reality, and newer governance artifacts.
- If future fullstack-integration work is still needed, it should be reopened as a new bounded change aligned to current repo truth instead of reviving this outdated package.

## Action

- Remove `openspec/changes/integrate-fullstack-platform/` from the active change set.
- Preserve this triage note as the historical explanation for retirement.
