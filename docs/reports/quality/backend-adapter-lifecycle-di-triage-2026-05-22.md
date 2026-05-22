# Backend Adapter Lifecycle DI Triage

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

Date: 2026-05-22
Status: triage-evidence-prepared-for-review
Branch: `g1-adapter-lifecycle-triage`
HEAD checked: `2dbca698612a420a3ee56b121bac8646d8433f6e`
Generated at: 2026-05-22T11:08:52+08:00
Primary issue: `#78`
Parent issue: `#92`
Blocked downstream issue: `#79`

## Purpose

This report prepares the G1 evidence and triage packet for issue `#78`
adapter lifecycle DI reconciliation after issue `#92` was retained as the
post-D2 parent decision index.

This is a governance and evidence packet only. It does not create an
implementation issue, does not create or modify an OpenSpec proposal, does not
change issue labels, and does not authorize backend source, tests, route,
OpenAPI, docs/API, runtime, PM2, script, config, or generated-client changes.

## Current Issue State

| Issue | State | Labels | Role |
|---|---|---|---|
| `#92` | `OPEN` | `enhancement`, `ready-for-downstream`, `ready-for-human` | Parent downstream decision index |
| `#78` | `OPEN` | `needs-triage` | Adapter lifecycle DI prerequisite lane |
| `#79` | `OPEN` | `needs-triage` | Service lifecycle DI lane, still blocked by `#78` |

## Current-HEAD Adapter Evidence

Exact-symbol scanning at HEAD
`2dbca698612a420a3ee56b121bac8646d8433f6e` found that the five current adapter
modules below already expose dependency-provider and app-state helper shapes.
None of the five scanned modules still contains `_instance = None`.

| Target | Module | `_instance = None` | Provider symbols | App-state helpers | Test evidence file | Direct current consumers |
|---|---|---:|---|---|---|---:|
| `eastmoney_adapter` | `web/backend/app/adapters/eastmoney_adapter.py` | No | `get_eastmoney_adapter`, `get_eastmoney_adapter_dependency` | install + close helpers present | `web/backend/tests/test_eastmoney_lifecycle_di.py` | 3 |
| `eastmoney_enhanced` | `web/backend/app/adapters/eastmoney_enhanced.py` | No | `get_eastmoney_enhanced_adapter`, `get_eastmoney_enhanced_adapter_dependency` | install + close helpers present | `web/backend/tests/test_eastmoney_enhanced_lifecycle_di.py` | 1 |
| `akshare_extension` | `web/backend/app/adapters/akshare_extension.py` | No | `get_akshare_extension`, `get_akshare_extension_dependency` | install + close helpers present | `web/backend/tests/test_akshare_extension_lifecycle_di.py` | 3 |
| `tqlex_adapter` | `web/backend/app/adapters/tqlex_adapter.py` | No | `get_tqlex_adapter`, `get_tqlex_adapter_dependency` | install + close helpers present | `web/backend/tests/test_tqlex_lifecycle_di.py` | 2 |
| `cninfo_adapter` | `web/backend/app/adapters/cninfo_adapter.py` | No | `get_cninfo_adapter`, `get_cninfo_adapter_dependency` | install + close helpers present | `web/backend/tests/test_cninfo_lifecycle_di.py` | 1 |

The test files above are evidence of existing dependency override or lifecycle
test coverage presence. This packet did not rerun those tests and does not
claim fresh runtime validation.

## Wiring And Consumer Findings

`web/backend/app/app_factory.py` mentions the EastMoney enhanced installer and
contains app-state wiring. `web/backend/app/main.py` does not mention the
EastMoney enhanced installer at this HEAD. That means canonical production
entry wiring remains a decision point before any future implementation lane,
not an automatic code edit in this packet.

The exact-symbol consumer scan found no direct API route handler consumer for
the five provider/getter symbol groups. Remaining direct consumers are
service/core files:

- `web/backend/app/core/adapter_factory.py`
- `web/backend/app/core/unified_market_data_service.py`
- `web/backend/app/services/market_data_service/market_data_service_methods/part1.py`
- `web/backend/app/services/market_data_service_v2.py`
- `web/backend/app/services/multi_source_manager.py`

These consumers must be classified before implementation as one of:

- acceptable compatibility getter use
- candidate for provider injection in a future approved lane
- factory/core integration point that should remain centralized
- false positive or out-of-scope for issue `#78`

## Realtime MTM Disposition

The original issue `#78` scope mentioned `realtime_mtm`. Current-head scanning
did not find a `realtime_mtm` adapter file under `web/backend/app/adapters/`.
Mentions exist in:

- `web/backend/app/main.py`
- `web/backend/app/api/realtime_mtm_init.py`
- `web/backend/app/api/realtime_market.py`
- `web/backend/app/api/realtime_mtm_adapter.py`
- `web/backend/tests/test_runtime_logging_wave5.py`
- `web/backend/tests/test_logging_noise_regressions.py`
- `web/backend/tests/test_health_route_conflicts.py`

Triage disposition: do not treat `realtime_mtm` as a current adapter singleton
implementation target until its canonical adapter identity and owner are
proved. It should either be removed from the issue `#78` adapter-target list or
handled by a separately approved realtime route/service lane.

## Recommended G1 Decision

Recommended review outcome for this packet:

1. Accept the current provider/app-state/test evidence for
   `eastmoney_adapter`, `eastmoney_enhanced`, `akshare_extension`,
   `tqlex_adapter`, and `cninfo_adapter`.
2. Treat issue `#78` as a reconciliation lane, not a broad implementation lane.
3. Do not start issue `#79` service lifecycle DI until issue `#78` has a
   reviewed disposition.
4. Require a separate implementation authorization before touching any source
   or test file.
5. If a future G1 implementation lane is approved, start with exact write scope
   and GitNexus impact on the selected symbols before edits.

## Future Implementation Preconditions

Any later implementation packet must include:

- selected adapter target list and excluded targets
- app `main.py` versus `app_factory.py` composition-root decision
- exact files allowed for edits
- classification of the five direct service/core consumers
- current-head test plan for dependency overrides and import stability
- rollback plan for app-state lifecycle registration
- GitNexus impact before source edits
- `gitnexus_detect_changes(scope="staged")` before commit

## Non-Authorization

This packet does not authorize:

- backend source, frontend source, test, generated client, docs/API, route,
  OpenAPI, probe URL, script, config, runtime, or PM2 changes
- issue label changes
- creating implementation issues
- moving `#78`, `#79`, or `#92` to `ready-for-agent`
- creating or modifying OpenSpec proposals
- migrating adapter or service singletons
- treating `realtime_mtm` as an implementation target before canonical identity
  and ownership are proved

## Evidence Artifact

Structured evidence is recorded in:

`.planning/codebase/generated/adapter-lifecycle-di-triage-2026-05-22.json`
