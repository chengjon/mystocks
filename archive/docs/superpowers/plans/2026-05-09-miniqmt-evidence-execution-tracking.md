# miniQMT Evidence Execution Tracking Implementation Plan

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect `/api/v1/trade/execution-tracking` to existing miniQMT bridge evidence stores while preserving the rule that bridge evidence is not broker truth.

**Architecture:** Add a read-only evidence service under the backend trade service layer. The API route keeps its response models stable and delegates record loading/timeline construction to the service. Existing in-memory trigger records remain a fallback for UI-created trigger requests.

**Tech Stack:** FastAPI, Pydantic v2, pytest, existing `src.application.trading` miniQMT evidence ledgers, existing `UnifiedResponse` route contract.

---

### Task 1: Evidence Service Contract

**Files:**
- Create: `web/backend/app/services/trade/execution_tracking_evidence.py`
- Create: `web/backend/app/services/trade/__init__.py`
- Test: `web/backend/tests/test_trade_execution_tracking_evidence.py`

- [ ] **Step 1: Write failing tests for miniQMT attempt mapping**

Create `web/backend/tests/test_trade_execution_tracking_evidence.py` with tests that build a submission-attempt record containing `order_id`, `account_scope`, `bridge_task_id`, `submission_status`, `transport_status`, `external_order_id`, and `source_name`. Assert the mapped execution row exposes bridge evidence and preserves `review_required` when `external_order_id` is absent.

Run: `pytest web/backend/tests/test_trade_execution_tracking_evidence.py -q --no-cov`

Expected: FAIL because `web.backend.app.services.trade.execution_tracking_evidence` does not exist.

- [ ] **Step 2: Implement minimal evidence service**

Create `ExecutionTrackingEvidenceService` with:
- constructor dependencies for `submission_attempt_store`, optional `divergence_store`, optional `broker_correlation_store`, and optional `session_trigger_records`
- `load_records(account_id, order_id=None, bridge_task_id=None, page=1, page_size=20) -> list[dict[str, Any]]`
- `load_record_by_tracking_id(tracking_id: str) -> dict[str, Any] | None`
- `build_timeline(record: Mapping[str, Any]) -> list[dict[str, Any]]`

Use `submission_attempt_store.fetch_recent(limit=page_size)` and filter by `account_scope`, `order_id`, and `bridge_task_id`.

- [ ] **Step 3: Verify evidence service tests pass**

Run: `pytest web/backend/tests/test_trade_execution_tracking_evidence.py -q --no-cov`

Expected: PASS.

### Task 2: Route Delegation

**Files:**
- Modify: `web/backend/app/api/trade/execution_tracking_routes.py`
- Test: `web/backend/tests/test_trade_execution_tracking_routes.py`

- [ ] **Step 1: Add route tests for injected evidence service**

Extend route tests with a fake evidence service whose `load_records` returns a miniQMT attempt and whose `build_timeline` returns bridge submission evidence. Assert the list endpoint includes the record and the detail endpoint includes the evidence timeline.

Run: `pytest web/backend/tests/test_trade_execution_tracking_routes.py -q --no-cov`

Expected: FAIL because the route still reads only `_EXECUTION_TRIGGERS` and internal statements directly.

- [ ] **Step 2: Wire the route to the service**

Keep existing Pydantic response models in `execution_tracking_routes.py`. Replace direct record loading with a small provider function such as `get_execution_tracking_evidence_service()` and call the service from list/detail handlers.

Keep `record_execution_trigger()` for `/trigger`, but pass `_EXECUTION_TRIGGERS` into the service so UI-triggered session evidence remains visible.

- [ ] **Step 3: Verify route tests pass**

Run: `pytest web/backend/tests/test_trade_execution_tracking_routes.py -q --no-cov`

Expected: PASS.

### Task 3: Safety Semantics

**Files:**
- Modify: `web/backend/app/services/trade/execution_tracking_evidence.py`
- Test: `web/backend/tests/test_trade_execution_tracking_evidence.py`
- Test: `web/backend/tests/test_trade_execution_tracking_routes.py`

- [ ] **Step 1: Add tests for bridge-only terminal evidence**

Add a record with `bridge_result_status="success"` or a live bridge incident category, no `external_order_id`, and no `broker_event_type`. Assert `broker_state == "review_required"` and `identity_status == "missing_broker_identity"`.

- [ ] **Step 2: Add tests for broker lifecycle identity**

Add a record with `external_order_id="broker-001"` and `broker_event_type="order_acknowledged"`. Assert the mapped row may become `broker_acknowledged` and the timeline includes a broker identity event.

- [ ] **Step 3: Implement the safety mapping**

Implement a single helper such as `resolve_broker_state(record)` that returns `broker_acknowledged` only when both an external broker identity and broker lifecycle event type are present. Never derive broker acknowledgement from `transport_status`, `receipt_status`, or `bridge_result_status`.

- [ ] **Step 4: Verify safety tests pass**

Run: `pytest web/backend/tests/test_trade_execution_tracking_evidence.py web/backend/tests/test_trade_execution_tracking_routes.py -q --no-cov`

Expected: PASS.

### Task 4: Verification And Closeout

**Files:**
- Modify: `openspec/changes/connect-execution-tracking-to-miniqmt-evidence/tasks.md`
- Optional Test: `web/frontend/src/views/trade/__tests__/Execution.spec.ts`
- Optional E2E: `web/frontend/tests/e2e/trade-execution-tracking.spec.ts`

- [ ] **Step 1: Validate OpenSpec**

Run: `openspec validate connect-execution-tracking-to-miniqmt-evidence --strict`

Expected: `Change 'connect-execution-tracking-to-miniqmt-evidence' is valid`.

- [ ] **Step 2: Run backend verification**

Run: `pytest web/backend/tests/test_trade_execution_tracking_evidence.py web/backend/tests/test_trade_execution_tracking_routes.py -q --no-cov`

Expected: all tests pass.

- [ ] **Step 3: Run frontend verification only if response text or UI evidence rendering changes**

Run: `npm run test -- --run src/views/trade/__tests__/Execution.spec.ts`

Run: `E2E_FRONTEND_PORT=3035 npx playwright test --config playwright.config.js --project=chromium tests/e2e/trade-execution-tracking.spec.ts`

Expected: execution workbench unit and Chromium E2E smoke pass.

- [ ] **Step 4: Commit implementation**

Stage only this slice's files and commit:

```bash
git add web/backend/app/services/trade/execution_tracking_evidence.py web/backend/app/services/trade/__init__.py web/backend/app/api/trade/execution_tracking_routes.py web/backend/tests/test_trade_execution_tracking_evidence.py web/backend/tests/test_trade_execution_tracking_routes.py openspec/changes/connect-execution-tracking-to-miniqmt-evidence/tasks.md
git commit -m "feat(trade): connect execution tracking to miniqmt evidence"
```
