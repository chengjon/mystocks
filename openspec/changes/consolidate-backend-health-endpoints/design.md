> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Context

The May 2026 audit review found:

- 46 health-like route decorators in backend code.
- `GET /health` local decorator duplicates across 22 modules.
- `GET /status` local decorator duplicates across 13 modules.
- The generated full-path route table shows 26 final URL duplicate groups, including `/health`, `/status`, `trading`, and `backup-recovery` paths.
- `/health/readiness` has zero current code hits.
- `/health/ready` and `/api/health/ready` are current readiness probes.
- `/api/health/services` is the current system services probe exposed by `api/health.py` through the `/api` router prefix.

The main risk is not missing readiness. The risk is unclassified health-like and status-like routes across platform probes, domain smoke checks, metrics, SSE, adapter/database health, examples, and legacy modules.

## Goals

- Preserve platform liveness/readiness behavior.
- Define canonical health/status categories.
- Avoid breaking monitoring, PM2, CI, tests, frontend, and external probes.
- Retire only endpoints proven to be redundant and unconsumed.
- Make health/status endpoint changes visible in OpenAPI diff.

## Non-Goals

- This change does not remove every domain `/health` endpoint by default.
- This change does not consolidate unrelated domain route ownership such as `trading` or `backup`; domain route duplicates are handled by domain router governance.
- This change does not change service lifecycle or dependency ownership.
- This change does not delete `monitoring_old/`; that remains governed by residual-file cleanup rules.

## Decisions

### Decision: Health/status endpoints are classified, not blanket-deleted

Health-like and status-like endpoints must be classified as:

- Platform liveness/readiness.
- System service health.
- Domain smoke.
- Metrics or observability.
- Adapter/database diagnostic.
- Status/summary endpoint.
- Example or embedded app.

`backup_recovery_secure/cleanup_old_backups.py` and similar domain endpoints must be classified before action. If the endpoint is part of backup domain route ownership rather than platform probe behavior, implementation belongs to the deferred backup domain router follow-up, not to this health/status consolidation.

### Decision: Final full-path route table gates runtime conflict claims

Local decorator duplicates are valid migration smell and taxonomy evidence. They do not by themselves prove a final runtime URL conflict. Implementation must use prefix-expanded full-path route evidence and OpenAPI diff before deleting, re-prefixing, or redirecting endpoints.

### Decision: Readiness paths remain available during migration

`/health/ready` and `/api/health/ready` must remain available until all PM2, monitoring, CI, and frontend consumers have migrated.

### Decision: `/api/health/services` is the current services probe

Root `/health/services` must not be used as the current service probe unless a later approved implementation intentionally adds or redirects it.

## Migration Plan

1. Confirm orchestration from `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`.
2. Generate or confirm local decorator route baseline, prefix-expanded full-path route table, and OpenAPI schema.
3. Classify all health-like and status-like endpoints.
4. Build PM2, monitoring, CI, frontend, tests, scripts, and external consumer matrix.
5. Select canonical probes and compatibility paths.
6. Decide which domain health/status endpoints stay with their domain router owner.
7. Retire or redirect low-risk endpoints one batch at a time.
8. Run readiness/service probe smoke and OpenAPI diff after each batch.

## Rollback

- Restore removed route decorator or router registration.
- Restore previous probe path or compatibility alias.
- Restore PM2/monitoring/CI probe config if changed.
- Re-run readiness and service probe smoke.

## Risks / Trade-offs

- Some domain health/status endpoints may be useful smoke checks rather than redundant platform checks.
- Route prefix composition can make decorator text misleading; prefix-expanded full-path route table evidence is required for runtime conflict claims.
- Probe changes can cause false production outage signals even when application logic works.

## Open Questions

- Which domain health endpoints are used by frontend or operational pages?
- Should some domain smoke endpoints remain intentionally separate from platform readiness?
- Should root `/health/services` be added as compatibility alias, or should all consumers use `/api/health/services`?
- Which status endpoints are platform status versus domain status, and which should remain intentionally separate?
