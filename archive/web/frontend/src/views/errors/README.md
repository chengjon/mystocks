# Frontend Error Demo Shell Archive

> **导航说明**:
> 本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

Date: 2026-05-11

Governing change: `openspec/changes/update-frontend-view-governance`

## Archived Files

| Archived file | Original path | Lifecycle status | Successor | Reason |
| --- | --- | --- | --- | --- |
| `Forbidden.vue` | `web/frontend/src/views/errors/Forbidden.vue` | `archive-candidate/demo-error-shell` | `web/frontend/src/views/NotFound.vue` for active blank-layout error route truth; no dedicated 403 successor | No active route/menu/pageConfig owner; stale links and local permission workflow were not promoted into formal route contract. |
| `NetworkError.vue` | `web/frontend/src/views/errors/NetworkError.vue` | `archive-candidate/demo-error-shell` | `no-successor-needed` | No active route/menu/pageConfig owner; local network retry shell was not promoted into formal error contract. |
| `ServiceUnavailable.vue` | `web/frontend/src/views/errors/ServiceUnavailable.vue` | `archive-candidate/demo-error-shell` | `no-successor-needed` | No active route/menu/pageConfig owner; local health-probe shell was not promoted into formal endpoint truth. |
| `styles/ServiceUnavailable.scss` | `web/frontend/src/views/errors/styles/ServiceUnavailable.scss` | `archive-candidate/support-asset` | `no-successor-needed` | Style asset only supported the archived `ServiceUnavailable.vue` demo shell. |

## Retired Active Guards

The following direct guards were moved out of active `web/frontend/tests/unit/config/` with this batch:

- `errors-mainline-gate.spec.ts`
- `errors-forbidden-style-source.spec.ts`
- `errors-network-style-source.spec.ts`
- `errors-service-unavailable-style-source.spec.ts`

`web/frontend/package.json` also removed the `lint:artdeco:changed` target for `src/views/errors`.

## Restore Rule

If a future change promotes 403, network-unavailable, or service-unavailable pages into formal routes, restore these files from archive only after defining route ownership, blank-layout behavior, backend endpoint truth, and active test coverage.
