# Backend Service Lifecycle Candidate Refresh After Wencai - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.97 service lifecycle candidate refresh after Wencai
Status: ready for review

## Purpose

Refresh the service lifecycle getter-retirement candidate list after the Wencai
public compatibility getter lane closed in PR `#249`.

This packet is governance-only. It records current evidence, updates the
steward tree, and selects a future authorization candidate. It does not
authorize backend source edits, tests edits, route/API changes, OpenAPI exposure
changes, PM2 execution, OpenSpec changes, GitHub issue label movement, or getter
deletion.

## Input State

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-97-service-lifecycle-candidate-refresh-after-wencai` |
| Branch | `g2-97-service-lifecycle-candidate-refresh-after-wencai` |
| Current HEAD | `c0aa9731503f3f8d8c9017ed787745ddaf6a5aab` |
| HEAD subject | `docs(governance): close out wencai getter retirement (#249)` |
| Parent PR | `#249`, `MERGED`, merge commit `c0aa9731503f3f8d8c9017ed787745ddaf6a5aab` |
| GitNexus refresh | `gitnexus analyze --with-gitignore` completed before this packet |

## Current-Head Scan Summary

| Metric | Value |
|---|---:|
| Service files scanned | `152` |
| App files scanned | `575` |
| API files scanned | `219` |
| Test files scanned | `1007` |
| Getter definitions found | `22` |
| Candidate-like definitions | `5` |
| Hold definitions | `17` |

`get_wencai_service` is no longer present as a service getter definition.

## Candidate Rows

| Candidate | File | App refs | Route/API refs | Test refs | Package export refs | Disposition |
|---|---|---:|---:|---:|---:|---|
| `get_enhanced_data_service` | `web/backend/app/services/data_service_enhanced.py:580` | `2` | `0` | `0` | `0` | Select as future G2.98 authorization candidate only |
| `get_announcement_service` | `web/backend/app/services/announcement_service.py:526` | `2` | `0` | `1` | `0` | Hold; announcement route DI lane is already closed |
| `get_tradingview_service` | `web/backend/app/services/tradingview_widget_service.py:322` | `2` | `0` | `2` | `0` | Hold for dedicated TradingView follow-up if needed |
| `get_email_service` | `web/backend/app/services/email_notification_service.py:324` | `3` | `0` | `3` | `0` | Hold; duplicate logical getter name and prior email DI lane require a separate decision |
| `get_email_service` | `web/backend/app/services/email_service.py:325` | `3` | `0` | `3` | `0` | Hold; duplicate logical getter name and prior email DI lane require a separate decision |

## Selected Next Lane

Select `get_enhanced_data_service` as the next future authorization candidate.

Rationale:

- The getter has no route/API references.
- It has no focused test references.
- It has no package export references.
- GitNexus impact is LOW with impacted count `3` and affected processes `0`.

Boundary:

- This selection does not authorize deleting `EnhancedDataService`.
- `EnhancedDataService` remains active through direct class usage in
  `web/backend/app/api/v1/system/health.py`.
- A future G2.98 packet must be authorization-only first and must distinguish
  getter retirement from the active enhanced-data service class.

## Verification Evidence

| Check | Result |
|---|---|
| GitNexus index | Refreshed with `gitnexus analyze --with-gitignore`; graph contains `62,762` nodes, `145,902` edges, `3,299` clusters, and `300` flows |
| Getter candidate scan | `152` service files, `575` app files, `219` API files, `1007` test files, `22` getter definitions, `5` candidate-like definitions, `17` holds |
| Selected candidate impact | `get_enhanced_data_service`: LOW, impacted count `3`, affected processes `0` |
| Selected candidate context | getter body initializes `_enhanced_data_service` lazily; incoming graph refs are internal to `data_service_enhanced.py` only |

## Boundary

Out of scope here:

- source or test edits;
- route/API edits;
- OpenAPI exposure changes;
- frontend or generated client edits;
- PM2/runtime execution;
- OpenSpec changes/spec updates;
- GitHub issue label changes.

## Next Gate

Human review / PR merge decision for this G2.97 governance packet.

If accepted, create G2.98 as an EnhancedDataService getter-retirement
authorization packet before any source edit.
