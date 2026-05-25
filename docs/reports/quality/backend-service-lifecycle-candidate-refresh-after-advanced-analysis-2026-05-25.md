# Backend Service Lifecycle Candidate Refresh After AdvancedAnalysis - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.93 service lifecycle candidate refresh after AdvancedAnalysis
Status: ready for review

## Purpose

Refresh the service lifecycle getter-retirement candidate list after the
AdvancedAnalysis public compatibility getter lane closed in PR `#245`.

This packet is governance-only. It records current evidence, updates the
steward tree, and selects a future authorization candidate. It does not
authorize backend source edits, tests edits, route/API changes, OpenAPI exposure
changes, PM2 execution, OpenSpec changes, GitHub issue label movement, or getter
deletion.

## Input State

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-93-service-lifecycle-candidate-refresh-after-advanced-analysis` |
| Branch | `g2-93-service-lifecycle-candidate-refresh-after-advanced-analysis` |
| Current HEAD | `0d98e77257372ba9a92dfda40b2c42343b89e92f` |
| HEAD subject | `docs(governance): close out advanced analysis getter retirement (#245)` |
| Parent PR | `#245`, `MERGED`, merge commit `0d98e77257372ba9a92dfda40b2c42343b89e92f` |
| Parent PR URL | `https://github.com/chengjon/mystocks/pull/245` |
| GitNexus refresh | `gitnexus analyze --with-gitignore` completed before this packet |

## Current-Head Scan Summary

| Metric | Value | Notes |
|---|---:|---|
| Service files scanned | `152` | `web/backend/app/services/**/*.py` |
| App files scanned | `575` | `web/backend/app/**/*.py` |
| API files scanned | `219` | `web/backend/app/api/**/*.py` |
| Getter definitions found | `23` | This packet includes service package exporter definitions in the scan. Earlier narrower summaries counted fewer definitions. |
| Candidate-like definitions | `6` | Route/API hits=`0`, package export hits=`0`, and low app-reference count. |
| Hold definitions | `17` | Exported package seams, active route consumers, or broad service seams. |

## Candidate Rows

| Candidate | File | App refs | Route/API refs | Test refs | Package export refs | Disposition |
|---|---|---:|---:|---:|---:|---|
| `get_wencai_service` | `web/backend/app/services/wencai_service.py:419` | `1` | `0` | `0` | `0` | Select as future G2.94 authorization candidate only |
| `get_enhanced_data_service` | `web/backend/app/services/data_service_enhanced.py:580` | `2` | `0` | `0` | `0` | Hold; enhanced data seam needs its own ownership review before selection |
| `get_announcement_service` | `web/backend/app/services/announcement_service.py:526` | `2` | `0` | `1` | `0` | Hold; announcement route DI lane is already closed, so avoid reopening from a generic refresh |
| `get_tradingview_service` | `web/backend/app/services/tradingview_widget_service.py:322` | `2` | `0` | `2` | `0` | Hold; keep behind a dedicated TradingView follow-up if needed |
| `get_email_service` | `web/backend/app/services/email_notification_service.py:324` | `3` | `0` | `3` | `0` | Hold; duplicate logical getter name and prior email DI lane require a separate decision |
| `get_email_service` | `web/backend/app/services/email_service.py:325` | `3` | `0` | `3` | `0` | Hold; duplicate logical getter name and prior email DI lane require a separate decision |

## Selected Next Lane

Select `get_wencai_service` as the next future authorization candidate.

Rationale:

- Its app-code references are definition-only in the service module.
- It has `0` route/API references.
- It has `0` focused test references.
- It has `0` `web/backend/app/services/__init__.py` package export references.
- GitNexus upstream impact for `get_wencai_service` is LOW with impacted count
  `0`, direct callers `0`, affected processes `0`, and affected modules `0`.

Boundary:

- This selection does not authorize deleting `WencaiService`.
- `WencaiService` remains active through direct class usage in
  `web/backend/app/api/wencai.py`, `web/backend/app/tasks/wencai_tasks.py`, and
  `src/database/services/database_service.py`.
- A future G2.94 packet must be authorization-only first. Any later source-capable
  branch must rerun GitNexus impact, prove TDD red/green, and define exact source
  and test scope before modifying `web/backend/app/services/wencai_service.py`.

## Verification Evidence

| Check | Result |
|---|---|
| Parent PR state | `#245` is `MERGED`, merge commit `0d98e77257372ba9a92dfda40b2c42343b89e92f` |
| GitNexus index | Refreshed with `gitnexus analyze --with-gitignore`; graph contains `62,748` nodes, `145,892` edges, `3,295` clusters, and `300` flows |
| Getter candidate scan | `152` service files, `575` app files, `219` API files, `23` getter definitions, `6` candidate-like definitions, `17` holds |
| Selected candidate impact | `get_wencai_service`: LOW, impacted count `0`, direct callers `0`, affected processes `0`, affected modules `0` |

## Non-Goals

- Do not edit backend source or tests.
- Do not delete `get_wencai_service` in this packet.
- Do not delete or migrate `WencaiService`.
- Do not change routes, response models, response shapes, or OpenAPI exposure.
- Do not create or modify OpenSpec changes/specs.
- Do not change GitHub issue labels or readiness state.
- Do not reopen completed email, announcement, DataSourceFactory, StockSearch, or
  AdvancedAnalysis getter lanes from this packet.

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

Human review / PR merge decision for this G2.93 governance packet.

If accepted, create G2.94 as a Wencai getter-retirement authorization packet
before any source edit. G2.94 should remain authorization-only unless it is
explicitly superseded by a separately approved implementation branch.
