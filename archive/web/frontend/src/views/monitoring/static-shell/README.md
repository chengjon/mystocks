# Frontend Monitoring Static Shell Archive

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

Date: 2026-05-11

Governing change: `openspec/changes/update-frontend-view-governance`

## Archived Files

| Archived file | Original path | Lifecycle status | Successor | Reason |
| --- | --- | --- | --- | --- |
| `MonitoringDashboard.vue` | `web/frontend/src/views/monitoring/MonitoringDashboard.vue` | `archive-candidate/legacy-static-shell` | `no-successor-needed`; shell text points to `/market/realtime`, `/risk/overview`, and `/market/lhb` | No active route/menu owner; previously degraded to an honest static shell because no reusable canonical monitoring truth exists for the old pseudo-live dashboard surface. |
| `MonitoringDashboard.spec.ts` | `web/frontend/src/views/monitoring/__tests__/MonitoringDashboard.spec.ts` | `archive-candidate/static-shell-proof` | `no-successor-needed` | Local repair-proof spec moved with the archived static shell. |
| `MonitoringDashboard.scss` | `web/frontend/src/views/monitoring/styles/MonitoringDashboard.scss` | `archive-candidate/orphan-style-support` | `no-successor-needed` | Style asset only supported the archived monitoring static shell and was no longer active route support. |

## Retired Active Guards

The following active config guards removed only the static-shell entries in this batch:

- `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts`
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`
- `web/frontend/tests/unit/config/console-log-cleanup-batch-1.spec.ts`

No router, menu, package, or other monitoring functional pages were changed.

## Restore Rule

If a future change restores this dashboard as a formal monitoring route, first define route ownership, menu placement, canonical data truth, request provenance, and active test coverage. Do not restore it as a pseudo-live shell.
