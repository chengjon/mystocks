## 1. Inventory

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **2026-05-18 跨线对齐**:
> P3-A4 已生成 singleton lifecycle inventory。E change 的剩余工作不是重复
> 收集同一份 evidence，而是复用或 supersede P3-A4，并补齐 DI-specific
> lifecycle classification、F import compatibility block 标记与 pilot 决策。
>
> **2026-05-18 pilot implementation evidence**:
> `docs/reports/quality/backend-lifecycle-di-inventory-2026-05-18.md`
> and `docs/reports/quality/generated/backend-lifecycle-di-eastmoney-enhanced-pilot-evidence-2026-05-18.md`
> record the approved single-pilot implementation. Remaining adapter and
> service singleton candidates are out of scope for this batch.
>
> **2026-05-19 follow-on batch evidence**:
> `web/backend/tests/test_cninfo_lifecycle_di.py` and the accompanying
> `web/backend/app/adapters/cninfo_adapter.py` / `web/backend/app/app_factory.py`
> wiring document the next adapter-only lifecycle DI expansion after the
> verified EastMoney pilot.
>
> **2026-05-19 second follow-on batch evidence**:
> `web/backend/tests/test_eastmoney_lifecycle_di.py` and the accompanying
> `web/backend/app/adapters/eastmoney_adapter.py` / `web/backend/app/app_factory.py`
> wiring extend the same lifecycle pattern to the direct EastMoney adapter.

- [x] 1.1 Confirm orchestration artifact: `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`.
- [x] 1.2 Generate current singleton inventory with `python scripts/dev/backend_audit_baseline.py docs/reports/quality/generated` and use `docs/reports/quality/generated/backend-audit-baseline.json`. Existing P3-A4 inventory is recorded in `docs/reports/quality/backend-audit-phase3-decision-records.md`.
- [x] 1.3 Generate current module-level `get_xxx` inventory with `rg -n "^def get_\\w+\\(" web/backend/app > docs/reports/quality/generated/backend-getter-inventory.txt`.
- [x] 1.4 Identify existing `Depends`, `app.state`, lifespan, shutdown, and factory patterns.
- [x] 1.5 Classify candidates by lifecycle class.
- [x] 1.6 Identify candidates implemented in Core database/cache/security/socketio/logger modules and mark them blocked by F import compatibility matrix.

## 2. Design Decisions

- [x] 2.1 Select one low-risk representative pilot candidate only.
- [x] 2.2 Define test override strategy for the pilot.
- [x] 2.3 Define teardown strategy for the pilot if it is heavy or connection-backed.
- [x] 2.4 Define compatibility getter retention and retirement conditions.
- [x] 2.5 If the pilot touches shared Core modules, confirm F's lifecycle-owned module list and import compatibility matrix first.

## 3. Implementation

- [x] 3.1 Implement only the approved single pilot.
- [x] 3.2 Use lifespan/app.state, factory ownership, or compatibility getter according to the pilot's lifecycle classification.
- [x] 3.3 Keep compatibility wrappers until consumer migration is verified.
- [x] 3.4 Do not expand to another singleton/getter candidate in the same batch.

## 4. Verification

- [x] 4.1 Run import smoke for old and new dependency paths.
- [x] 4.2 Run dependency override tests.
- [x] 4.3 Run lifecycle startup/shutdown smoke.
- [x] 4.4 Run affected API tests. No production route was modified; the affected API surface is the focused FastAPI probe route in `web/backend/tests/test_eastmoney_enhanced_lifecycle_di.py`.
- [x] 4.5 Confirm no request-level recreation of heavy services.
- [x] 4.6 Attach teardown evidence artifact: test fixture output, shutdown hook smoke, log excerpt, or resource close assertion.

## 5. Closure

- [x] 5.1 Update documentation with lifecycle classification.
- [x] 5.2 Record remaining singleton debt and owner.
- [x] 5.3 Mark compatibility getter retirement candidates only after evidence is complete.

## 6. Follow-on Batch: CninfoAdapter

- [x] 6.1 Reuse the verified EastMoney lifecycle pattern for one additional adapter-only follow-on batch.
- [x] 6.2 Preserve `get_cninfo_adapter()` as a compatibility getter while introducing `install_cninfo_adapter()` and `get_cninfo_adapter_dependency()`.
- [x] 6.3 Add `app.state` install/close wiring for `CninfoAdapter` in the FastAPI lifespan.
- [x] 6.4 Add focused dependency override, compatibility getter fallback, and teardown tests for the new provider.
- [x] 6.5 Verify the new batch with targeted pytest, lint, and syntax checks.

## 7. Follow-on Batch: EastMoneyAdapter

- [x] 7.1 Reuse the verified lifecycle pattern for the direct EastMoney adapter.
- [x] 7.2 Preserve `get_eastmoney_adapter()` as a compatibility getter while introducing `install_eastmoney_adapter()` and `get_eastmoney_adapter_dependency()`.
- [x] 7.3 Add `app.state` install/close wiring for `EastMoneyAdapter` in the FastAPI lifespan.
- [x] 7.4 Add focused dependency override, compatibility getter fallback, and teardown tests for the provider.
- [x] 7.5 Verify the batch with targeted pytest, lint, syntax, and OpenSpec checks.
