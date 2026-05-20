# Singleton Lifecycle Routing Matrix

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: inventory complete; no next `#79` stateless pilot was selected from this pass.

## Inventory

- Scanned `152` service `.py` files under `web/backend/app/services`
- `111` files matched singleton/getter/spec-loading patterns
- `spec_from_file_location` appears in five service files: `analysis_api.py`, `data_api_new.py`, `market_api.py`, `technical_pattern_detection_service.py`, and `trading_api.py`

## Routing matrix

| Bucket | Representative candidates | Decision |
|---|---|---|
| External-client wrapper | `miniqmt_live_bridge.py`, `multi_source_bridge_adapter.py`, `kronos_client.py`, `wencai_service.py`, `email_notification_service.py` | Keep in a separate wrapper/external-client lane; not a stateless pilot |
| DB/session-backed service | `data_api_service.py`, `data_api_new.py`, `market_data_service.py`, `unified_data_service.py`, `algorithm_service.py` | Heavy/stateful lane; do not pick directly for the next pilot |
| Cache/task-running service | `data_quality_monitor.py`, `streaming_service.py`, `room_broadcaster.py`, `indicator_filter.py` | Stateful cache or task loop; not a stateless pilot |
| Separate design gate | `realtime_mtm.py`, `adapter_loader.py`, `technical_pattern_detection_service.py`, `stock_search_service/stock_search_service.py` | Require a separate proposal/design gate before any movement |
| Low-risk stateless pilot | None selected | No candidate in this pass was clean enough to promote as the next `#79` pilot |

## Decision

- `IntegratedServices` is still export-only in `services/__init__.py`; it is not a useful pilot boundary by itself.
- `DataApiService` and `MarketDataService` remain heavily referenced and should stay out of the low-risk pilot lane.
- The next service lifecycle step should wait for a cleaner candidate rather than forcing one from the current inventory.

## Verification

- `git diff --check -- docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md`
