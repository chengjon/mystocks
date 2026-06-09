# Trade Reconciliation Statement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an MVP trade reconciliation statement capability with multi-account switching, normalized-template and `miniQMT` CSV import, deterministic read-only matching, CSV export, and a dedicated `/trade/reconciliation` page.

**Architecture:** Reuse the existing trade-domain route family and UI domain, but keep reconciliation separate from `History.vue` and from broker-lifecycle reconciliation. The first batch should project internal statements from persisted `backtest_trades` into synthetic reconciliation account descriptors (`backtest:<backtest_id>`), normalize external CSVs into one `BrokerStatementRow` shape, store imported batches in memory by `import_batch_id`, and run deterministic one-to-one matching before exposing paginated results and CSV export.

**Tech Stack:** OpenSpec, FastAPI, Pydantic, SQLAlchemy, Python stdlib `csv`, Vue 3, Vitest, Playwright, existing trade-domain API/service patterns, `UnifiedResponse`.

---

## File Structure

### OpenSpec

- Create: `openspec/changes/add-trade-reconciliation-statement/proposal.md`
  Purpose: describe why the reconciliation statement capability is needed and how it affects the trade domain.
- Create: `openspec/changes/add-trade-reconciliation-statement/design.md`
  Purpose: capture the approved design decisions that are now fixed by the reviewed spec.
- Create: `openspec/changes/add-trade-reconciliation-statement/tasks.md`
  Purpose: implementation checklist mirroring this execution plan at OpenSpec level.
- Create: `openspec/changes/add-trade-reconciliation-statement/specs/trade-reconciliation-statement/spec.md`
  Purpose: define the first canonical OpenSpec requirement set for statement reconciliation.
- Create: `openspec/changes/add-trade-reconciliation-statement/specs/frontend-routing/spec.md`
  Purpose: record the additive `/trade/reconciliation` route and the label correction from `历史对账` to `交易历史`.

### Backend

- Modify: `web/backend/app/api/trade/__init__.py`
  Purpose: expose one package-level `router` that mounts both the existing trade routes and the new reconciliation routes without bloating `routes.py`.
- Create: `web/backend/app/api/trade/reconciliation_models.py`
  Purpose: request/response Pydantic models for reconciliation accounts, statements, imports, results, and export metadata.
- Create: `web/backend/app/api/trade/reconciliation_routes.py`
  Purpose: route handlers for `/reconciliation/accounts`, `/statements`, `/import`, `/results`, and `/export`.
- Create: `web/backend/app/services/statement_reconciliation/internal_statement_source.py`
  Purpose: project persisted `BacktestTradeModel` rows into `InternalStatementRow` and synthetic `backtest:<backtest_id>` account descriptors.
- Create: `web/backend/app/services/statement_reconciliation/import_batch_store.py`
  Purpose: in-memory import batch ledger keyed by `import_batch_id`.
- Create: `web/backend/app/services/statement_reconciliation/parsers/normalized_template.py`
  Purpose: validate and normalize the project-defined template CSV.
- Create: `web/backend/app/services/statement_reconciliation/parsers/miniqmt.py`
  Purpose: validate and normalize the supported `miniQMT` raw CSV header set.
- Create: `web/backend/app/services/statement_reconciliation/matcher.py`
  Purpose: deterministic one-to-one statement matching with locked timestamp normalization.
- Create: `web/backend/app/services/statement_reconciliation/export.py`
  Purpose: serialize filtered reconciliation results into CSV with the required response headers.
- Create: `web/backend/tests/test_trade_reconciliation_internal_statement_source.py`
  Purpose: verify synthetic account projection and internal statement mapping.
- Create: `web/backend/tests/test_trade_reconciliation_parsers.py`
  Purpose: verify normalized-template and `miniQMT` parsing plus validation errors.
- Create: `web/backend/tests/test_trade_reconciliation_matcher.py`
  Purpose: verify deterministic match status classification and row consumption.
- Create: `web/backend/tests/test_trade_reconciliation_routes.py`
  Purpose: verify route contract shape, upload handling, pagination, and export headers.

### Frontend

- Modify: `web/frontend/src/api/trade.ts`
  Purpose: add reconciliation-specific trade API methods while preserving the existing trade history methods.
- Create: `web/frontend/src/views/trade/composables/reconciliationDataTransform.ts`
  Purpose: convert backend reconciliation payloads into view-local rows, summaries, and account options.
- Create: `web/frontend/src/views/trade/composables/useTradeReconciliation.ts`
  Purpose: own page-local state, load orchestration, upload flow, and export flow.
- Create: `web/frontend/src/views/trade/Reconciliation.vue`
  Purpose: dedicated reconciliation statement page with account switcher, date range, CSV import, CSV export, summaries, and results table.
- Modify: `web/frontend/src/router/index.ts`
  Purpose: add `/trade/reconciliation` and rename `/trade/history` display text to `交易历史`.
- Modify: `web/frontend/src/layouts/MenuConfig.ts`
  Purpose: add a dedicated trade reconciliation menu entry and stop using `history` as the reconciliation label.
- Modify: `web/frontend/src/config/pageConfig.ts`
  Purpose: register the new reconciliation page and rename the existing history page metadata.
- Create: `web/frontend/src/views/trade/__tests__/Reconciliation.spec.ts`
  Purpose: verify account switching, upload state flow, summary rendering, and read-only discrepancy statuses.

### End-To-End And Governance Closeout

- Create: `tests/e2e/trade-reconciliation-page.spec.ts`
  Purpose: smoke the reconciliation flow with mocked backend responses and CSV import.
- Modify: `docs/FUNCTION_TREE.md`
  Purpose: move `5.2 对账单` from `🚧` to `✅` only after the MVP is implemented and verified.

---

### Task 1: OpenSpec Change For Trade Reconciliation Statement

**Files:**
- Create: `openspec/changes/add-trade-reconciliation-statement/proposal.md`
- Create: `openspec/changes/add-trade-reconciliation-statement/design.md`
- Create: `openspec/changes/add-trade-reconciliation-statement/tasks.md`
- Create: `openspec/changes/add-trade-reconciliation-statement/specs/trade-reconciliation-statement/spec.md`
- Create: `openspec/changes/add-trade-reconciliation-statement/specs/frontend-routing/spec.md`

- [ ] **Step 1: Write the OpenSpec proposal from the approved design**

```md
# Change: add trade reconciliation statement

## Why
`FUNCTION_TREE` still marks `5.2 对账单` as unfinished. The current trade domain only exposes history and execution-oriented flows, not a dedicated reconciliation statement capability.

## What Changes
- Add a dedicated trade reconciliation statement capability under the trade domain.
- Add account descriptors, internal statement projection, CSV import, deterministic matching, and CSV export.
- Add a dedicated `/trade/reconciliation` frontend route.

## Impact
- Affected specs: `trade-reconciliation-statement`, `frontend-routing`
- Affected code: `web/backend/app/api/trade/*`, `web/frontend/src/views/trade/*`, `web/frontend/src/router/index.ts`
```

- [ ] **Step 2: Write the initial capability spec delta**

```md
## ADDED Requirements
### Requirement: Trade Reconciliation Statement Surface
The system SHALL provide a dedicated trade reconciliation statement capability under the trade domain.

#### Scenario: User opens the reconciliation page
- **WHEN** the user navigates to `/trade/reconciliation`
- **THEN** the system SHALL expose account switching, date-range filtering, CSV import, CSV export, and a read-only discrepancy result surface

### Requirement: Deterministic Statement Matching
The reconciliation capability SHALL normalize internal and broker statement rows into explicit models and perform deterministic one-to-one matching.

#### Scenario: Imported statement rows are matched
- **WHEN** an import batch is compared with internal statement rows
- **THEN** the system SHALL classify each internal row as `matched`, `mismatched`, or `missing_broker_record`
- **AND** it SHALL NOT permit operator override in this batch
```

- [ ] **Step 3: Add the additive frontend-routing delta for the new page**

```md
## ADDED Requirements
### Requirement: Trade Reconciliation Route
The frontend routing system SHALL expose a dedicated reconciliation statement page under the trade domain.

#### Scenario: User navigates to the reconciliation page
- **WHEN** the user opens `/trade/reconciliation`
- **THEN** the router SHALL load the reconciliation page
- **AND** the navigation label for `/trade/history` SHALL remain `交易历史`
- **AND** the navigation label for `/trade/reconciliation` SHALL be `对账单`
```

- [ ] **Step 4: Write the OpenSpec task checklist**

```md
## 1. Backend
- [ ] 1.1 Add reconciliation route contract and models
- [ ] 1.2 Add internal statement projection from persisted trade history
- [ ] 1.3 Add normalized-template and `miniQMT` CSV parsers
- [ ] 1.4 Add deterministic matcher and CSV export

## 2. Frontend
- [ ] 2.1 Add `/trade/reconciliation` route and menu/page registry entries
- [ ] 2.2 Add reconciliation API client methods and page-local transforms
- [ ] 2.3 Add the dedicated reconciliation page and unit coverage

## 3. Validation
- [ ] 3.1 Run targeted backend tests
- [ ] 3.2 Run targeted frontend unit tests
- [ ] 3.3 Run reconciliation page smoke coverage
- [ ] 3.4 Update `FUNCTION_TREE` after verification
```

- [ ] **Step 5: Validate the OpenSpec change**

Run:

```bash
openspec validate add-trade-reconciliation-statement --strict
```

Expected:

```text
Change 'add-trade-reconciliation-statement' is valid
```

- [ ] **Step 6: Commit the OpenSpec slice**

```bash
git add \
  openspec/changes/add-trade-reconciliation-statement/proposal.md \
  openspec/changes/add-trade-reconciliation-statement/design.md \
  openspec/changes/add-trade-reconciliation-statement/tasks.md \
  openspec/changes/add-trade-reconciliation-statement/specs/trade-reconciliation-statement/spec.md \
  openspec/changes/add-trade-reconciliation-statement/specs/frontend-routing/spec.md
git commit -m "docs(openspec): add trade reconciliation statement change"
```

---

### Task 2: Backend Account Descriptors And Internal Statement Projection

**Files:**
- Modify: `web/backend/app/api/trade/__init__.py`
- Create: `web/backend/app/api/trade/reconciliation_models.py`
- Create: `web/backend/app/api/trade/reconciliation_routes.py`
- Create: `web/backend/app/services/statement_reconciliation/internal_statement_source.py`
- Create: `web/backend/tests/test_trade_reconciliation_internal_statement_source.py`
- Create: `web/backend/tests/test_trade_reconciliation_routes.py`

- [ ] **Step 1: Write the failing internal-statement-source tests**

```python
from decimal import Decimal
from types import SimpleNamespace

from web.backend.app.services.statement_reconciliation.internal_statement_source import (
    build_statement_account_id,
    list_reconciliation_accounts,
    query_internal_statements,
)


def test_build_statement_account_id_projects_backtest_identity():
    assert build_statement_account_id(7) == "backtest:7"


def test_query_internal_statements_maps_backtest_trade_rows():
    row = SimpleNamespace(
        id=101,
        backtest_id=7,
        trade_date="2026-05-06",
        symbol="600519.SH",
        direction="buy",
        amount=100,
        price=Decimal("1750.00"),
        commission=Decimal("52.50"),
        total_cost=Decimal("175000.00"),
    )

    payload = query_internal_statements._map_rows_for_test([row], account_id="backtest:7")

    assert payload[0]["account_id"] == "backtest:7"
    assert payload[0]["trade_id"] == "101"
    assert payload[0]["order_id"] == "backtest-7-101"
    assert payload[0]["amount"] == "175000.00"
```

- [ ] **Step 2: Run the new backend tests and confirm the source module does not exist yet**

Run:

```bash
pytest web/backend/tests/test_trade_reconciliation_internal_statement_source.py -q --no-cov
```

Expected:

```text
FAIL ... ModuleNotFoundError: No module named '...internal_statement_source'
```

- [ ] **Step 3: Add the internal statement source and synthetic account projection**

```python
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal

from app.core.database import SessionLocal
from app.repositories.backtest_repository import BacktestTradeModel


def build_statement_account_id(backtest_id: int) -> str:
    return f"backtest:{backtest_id}"


def parse_statement_account_id(account_id: str) -> int:
    prefix, raw_backtest_id = account_id.split(":", 1)
    if prefix != "backtest":
        raise ValueError(f"unsupported reconciliation account_id: {account_id}")
    return int(raw_backtest_id)


def list_reconciliation_accounts() -> list[dict[str, str]]:
    session = SessionLocal()
    try:
        backtest_ids = [
            int(value)
            for (value,) in session.query(BacktestTradeModel.backtest_id).distinct().order_by(BacktestTradeModel.backtest_id.desc()).all()
        ]
        return [
            {
                "account_id": build_statement_account_id(backtest_id),
                "label": f"Backtest #{backtest_id}",
                "account_type": "backtest",
            }
            for backtest_id in backtest_ids
        ]
    finally:
        session.close()
```

- [ ] **Step 4: Add the reconciliation route contract for `/accounts` and `/statements`**

```python
router = APIRouter(prefix="/reconciliation", tags=["trade-reconciliation"])


@router.get("/accounts", response_model=UnifiedResponse[dict[str, Any]])
async def get_reconciliation_accounts() -> UnifiedResponse[dict[str, Any]]:
    return create_success_response(
        data={"items": list_reconciliation_accounts()},
        message="Reconciliation accounts loaded",
    )


@router.get("/statements", response_model=UnifiedResponse[dict[str, Any]])
async def get_reconciliation_statements(
    account_id: str = Query(...),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> UnifiedResponse[dict[str, Any]]:
    payload = query_internal_statements(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return create_success_response(data=payload, message="Reconciliation statements loaded")
```

- [ ] **Step 5: Mount the new reconciliation router without growing `routes.py`**

```python
from fastapi import APIRouter

from .routes import router as trade_routes_router
from .reconciliation_routes import router as reconciliation_router

router = APIRouter()
router.include_router(trade_routes_router)
router.include_router(reconciliation_router)

__all__ = ["router"]
```

- [ ] **Step 6: Run the route and source tests**

Run:

```bash
pytest \
  web/backend/tests/test_trade_reconciliation_internal_statement_source.py \
  web/backend/tests/test_trade_reconciliation_routes.py \
  -q --no-cov
```

Expected:

```text
all selected reconciliation source and route tests pass
```

- [ ] **Step 7: Commit the account-and-statement slice**

```bash
git add \
  web/backend/app/api/trade/__init__.py \
  web/backend/app/api/trade/reconciliation_models.py \
  web/backend/app/api/trade/reconciliation_routes.py \
  web/backend/app/services/statement_reconciliation/internal_statement_source.py \
  web/backend/tests/test_trade_reconciliation_internal_statement_source.py \
  web/backend/tests/test_trade_reconciliation_routes.py
git commit -m "feat(trade): add reconciliation statement source"
```

---

### Task 3: Backend CSV Parsers And Import Batch Store

**Files:**
- Create: `web/backend/app/services/statement_reconciliation/import_batch_store.py`
- Create: `web/backend/app/services/statement_reconciliation/parsers/normalized_template.py`
- Create: `web/backend/app/services/statement_reconciliation/parsers/miniqmt.py`
- Modify: `web/backend/app/api/trade/reconciliation_routes.py`
- Create: `web/backend/tests/test_trade_reconciliation_parsers.py`

- [ ] **Step 1: Write failing parser tests for both supported CSV shapes**

```python
from web.backend.app.services.statement_reconciliation.parsers.normalized_template import parse_normalized_template_csv
from web.backend.app.services.statement_reconciliation.parsers.miniqmt import parse_miniqmt_csv


def test_parse_normalized_template_csv_returns_canonical_rows():
    csv_bytes = (
        "account_id,trade_date,trade_time,symbol,direction,price,quantity,amount,commission,order_id,trade_id\n"
        "backtest:7,2026-05-06,09:31:00,600519.SH,buy,1750.00,100,175000.00,52.50,backtest-7-101,101\n"
    ).encode("utf-8")

    rows = parse_normalized_template_csv(csv_bytes)

    assert rows[0]["account_id"] == "backtest:7"
    assert rows[0]["symbol"] == "600519.SH"
    assert rows[0]["order_id"] == "backtest-7-101"


def test_parse_miniqmt_csv_maps_supported_headers():
    csv_bytes = (
        "证券代码,买卖方向,成交价格,成交数量,成交金额,手续费,委托编号,成交编号,成交时间\n"
        "600519.SH,买入,1750.00,100,175000.00,52.50,backtest-7-101,101,2026-05-06 09:31:00\n"
    ).encode("utf-8-sig")

    rows = parse_miniqmt_csv(csv_bytes, account_id="backtest:7")

    assert rows[0]["account_id"] == "backtest:7"
    assert rows[0]["direction"] == "buy"
    assert rows[0]["trade_id"] == "101"
```

- [ ] **Step 2: Run the parser tests and confirm both parser modules are missing**

Run:

```bash
pytest web/backend/tests/test_trade_reconciliation_parsers.py -q --no-cov
```

Expected:

```text
FAIL ... ModuleNotFoundError for the parser modules
```

- [ ] **Step 3: Implement the normalized-template parser**

```python
REQUIRED_TEMPLATE_COLUMNS = {
    "account_id",
    "trade_date",
    "trade_time",
    "symbol",
    "direction",
    "price",
    "quantity",
    "amount",
    "commission",
    "order_id",
    "trade_id",
}


def parse_normalized_template_csv(csv_bytes: bytes) -> list[dict[str, str]]:
    text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    header = set(reader.fieldnames or [])
    missing = sorted(REQUIRED_TEMPLATE_COLUMNS - header)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")

    rows = []
    for row_number, row in enumerate(reader, start=2):
        rows.append(
            {
                "account_id": row["account_id"].strip(),
                "trade_time": f'{row["trade_date"].strip()} {row["trade_time"].strip()}',
                "symbol": row["symbol"].strip().upper(),
                "direction": row["direction"].strip().lower(),
                "price": row["price"].strip(),
                "quantity": row["quantity"].strip(),
                "amount": row["amount"].strip(),
                "commission": row["commission"].strip(),
                "order_id": row["order_id"].strip(),
                "trade_id": row["trade_id"].strip(),
                "source_type": "normalized_template",
                "raw_row_number": row_number,
            }
        )
    if not rows:
        raise ValueError("csv contains no data rows")
    return rows
```

- [ ] **Step 4: Implement the `miniQMT` parser and import batch store**

```python
MINIQMT_COLUMN_MAP = {
    "证券代码": "symbol",
    "买卖方向": "direction",
    "成交价格": "price",
    "成交数量": "quantity",
    "成交金额": "amount",
    "手续费": "commission",
    "委托编号": "order_id",
    "成交编号": "trade_id",
    "成交时间": "trade_time",
}


def parse_miniqmt_csv(csv_bytes: bytes, *, account_id: str) -> list[dict[str, str]]:
    text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    header = set(reader.fieldnames or [])
    missing = sorted(MINIQMT_COLUMN_MAP.keys() - header)
    if missing:
        raise ValueError(f"missing supported miniQMT columns: {', '.join(missing)}")

    direction_map = {"买入": "buy", "卖出": "sell"}
    rows = []
    for row_number, row in enumerate(reader, start=2):
        rows.append(
            {
                "account_id": account_id,
                "trade_time": row["成交时间"].strip(),
                "symbol": row["证券代码"].strip().upper(),
                "direction": direction_map[row["买卖方向"].strip()],
                "price": row["成交价格"].strip(),
                "quantity": row["成交数量"].strip(),
                "amount": row["成交金额"].strip(),
                "commission": row["手续费"].strip(),
                "order_id": row["委托编号"].strip(),
                "trade_id": row["成交编号"].strip(),
                "source_type": "miniqmt",
                "raw_row_number": row_number,
            }
        )
    if not rows:
        raise ValueError("csv contains no data rows")
    return rows
```

- [ ] **Step 5: Add the `/import` route backed by an in-memory batch store**

```python
@router.post("/import", response_model=UnifiedResponse[dict[str, Any]])
async def import_reconciliation_csv(
    file: UploadFile,
    source_type: str = Form(...),
    account_id: str | None = Form(None),
) -> UnifiedResponse[dict[str, Any]]:
    csv_bytes = await file.read()
    if source_type == "normalized_template":
        rows = parse_normalized_template_csv(csv_bytes)
    elif source_type == "miniqmt":
        if not account_id:
            raise HTTPException(status_code=422, detail={"message": "account_id is required for miniqmt imports"})
        rows = parse_miniqmt_csv(csv_bytes, account_id=account_id)
    else:
        raise HTTPException(status_code=422, detail={"message": "unsupported source_type"})

    import_batch = import_batch_store.create_batch(
        account_id=account_id,
        source_type=source_type,
        rows=rows,
    )
    return create_success_response(data=import_batch, message="Reconciliation import batch created")
```

- [ ] **Step 6: Re-run the parser and import tests**

Run:

```bash
pytest \
  web/backend/tests/test_trade_reconciliation_parsers.py \
  web/backend/tests/test_trade_reconciliation_routes.py \
  -q --no-cov
```

Expected:

```text
all selected parser and import-route tests pass
```

- [ ] **Step 7: Commit the parser/import slice**

```bash
git add \
  web/backend/app/services/statement_reconciliation/import_batch_store.py \
  web/backend/app/services/statement_reconciliation/parsers/normalized_template.py \
  web/backend/app/services/statement_reconciliation/parsers/miniqmt.py \
  web/backend/app/api/trade/reconciliation_routes.py \
  web/backend/tests/test_trade_reconciliation_parsers.py
git commit -m "feat(trade): add reconciliation csv import"
```

---

### Task 4: Backend Matcher, Results Route, And CSV Export

**Files:**
- Create: `web/backend/app/services/statement_reconciliation/matcher.py`
- Create: `web/backend/app/services/statement_reconciliation/export.py`
- Modify: `web/backend/app/api/trade/reconciliation_routes.py`
- Create: `web/backend/tests/test_trade_reconciliation_matcher.py`

- [ ] **Step 1: Write failing matcher tests for the three allowed statuses**

```python
from web.backend.app.services.statement_reconciliation.matcher import match_statement_rows


def test_match_statement_rows_marks_exact_match():
    results = match_statement_rows(
        internal_rows=[{"trade_id": "101", "order_id": "backtest-7-101", "symbol": "600519.SH", "direction": "buy", "trade_time": "2026-05-06 09:31:00", "quantity": "100", "price": "1750.00", "amount": "175000.00", "commission": "52.50"}],
        broker_rows=[{"trade_id": "101", "order_id": "backtest-7-101", "symbol": "600519.SH", "direction": "buy", "trade_time": "2026-05-06 09:31:00", "quantity": "100", "price": "1750.00", "amount": "175000.00", "commission": "52.50"}],
    )

    assert results[0]["match_status"] == "matched"


def test_match_statement_rows_marks_missing_broker_record():
    results = match_statement_rows(
        internal_rows=[{"trade_id": "101", "order_id": "backtest-7-101", "symbol": "600519.SH", "direction": "buy", "trade_time": "2026-05-06 09:31:00", "quantity": "100", "price": "1750.00", "amount": "175000.00", "commission": "52.50"}],
        broker_rows=[],
    )

    assert results[0]["match_status"] == "missing_broker_record"
```

- [ ] **Step 2: Run the matcher tests and confirm the matcher module does not exist yet**

Run:

```bash
pytest web/backend/tests/test_trade_reconciliation_matcher.py -q --no-cov
```

Expected:

```text
FAIL ... ModuleNotFoundError for matcher.py
```

- [ ] **Step 3: Implement deterministic timestamp normalization and one-to-one matching**

```python
def normalize_match_timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if "T" in value or value.endswith("Z") else datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    return parsed.replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")


def build_fallback_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    return (
        row["symbol"],
        row["direction"],
        normalize_match_timestamp(row["trade_time"]),
        str(row["quantity"]),
        str(row["price"]),
    )


def match_statement_rows(internal_rows: list[dict[str, str]], broker_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    broker_by_order_id = {row["order_id"]: row for row in broker_rows if row.get("order_id")}
    remaining_fallback = {build_fallback_key(row): row for row in broker_rows if row.get("order_id") not in broker_by_order_id}
    consumed_ids: set[str] = set()
    results = []

    for internal_row in internal_rows:
        broker_row = broker_by_order_id.get(internal_row["order_id"])
        if broker_row and broker_row["trade_id"] not in consumed_ids:
            consumed_ids.add(broker_row["trade_id"])
            status = "matched" if build_fallback_key(internal_row) == build_fallback_key(broker_row) and internal_row["amount"] == broker_row["amount"] and internal_row["commission"] == broker_row["commission"] else "mismatched"
            results.append({"match_status": status, "match_reason": status, "internal_row": internal_row, "broker_row": broker_row})
            continue

        broker_row = remaining_fallback.pop(build_fallback_key(internal_row), None)
        if broker_row is not None and broker_row["trade_id"] not in consumed_ids:
            consumed_ids.add(broker_row["trade_id"])
            results.append({"match_status": "matched", "match_reason": "matched_by_fallback_key", "internal_row": internal_row, "broker_row": broker_row})
            continue

        results.append({"match_status": "missing_broker_record", "match_reason": "no_broker_candidate", "internal_row": internal_row, "broker_row": None})
    return results
```

- [ ] **Step 4: Add `/results` and `/export` routes**

```python
@router.get("/results", response_model=UnifiedResponse[dict[str, Any]])
async def get_reconciliation_results(
    account_id: str = Query(...),
    import_batch_id: str = Query(...),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    match_status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> UnifiedResponse[dict[str, Any]]:
    internal_page = query_internal_statements(account_id=account_id, start_date=start_date, end_date=end_date, page=1, page_size=10000)
    import_batch = import_batch_store.get_batch(import_batch_id)
    rows = match_statement_rows(internal_page["items"], import_batch["rows"])
    if match_status:
        rows = [row for row in rows if row["match_status"] == match_status]
    start = (page - 1) * page_size
    end = start + page_size
    return create_success_response(data={"items": rows[start:end], "total_count": len(rows)}, message="Reconciliation results loaded")


@router.get("/export")
async def export_reconciliation_results(...):
    csv_content = build_reconciliation_csv(rows)
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=reconciliation-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.csv"},
    )
```

- [ ] **Step 5: Re-run matcher, route, and export-header tests**

Run:

```bash
pytest \
  web/backend/tests/test_trade_reconciliation_matcher.py \
  web/backend/tests/test_trade_reconciliation_routes.py \
  -q --no-cov
```

Expected:

```text
all selected matcher and route-export tests pass
```

- [ ] **Step 6: Commit the matcher/results/export slice**

```bash
git add \
  web/backend/app/services/statement_reconciliation/matcher.py \
  web/backend/app/services/statement_reconciliation/export.py \
  web/backend/app/api/trade/reconciliation_routes.py \
  web/backend/tests/test_trade_reconciliation_matcher.py \
  web/backend/tests/test_trade_reconciliation_routes.py
git commit -m "feat(trade): add reconciliation matching results"
```

---

### Task 5: Frontend Trade Reconciliation Page And Trade API Methods

**Files:**
- Modify: `web/frontend/src/api/trade.ts`
- Create: `web/frontend/src/views/trade/composables/reconciliationDataTransform.ts`
- Create: `web/frontend/src/views/trade/composables/useTradeReconciliation.ts`
- Create: `web/frontend/src/views/trade/Reconciliation.vue`
- Modify: `web/frontend/src/router/index.ts`
- Modify: `web/frontend/src/layouts/MenuConfig.ts`
- Modify: `web/frontend/src/config/pageConfig.ts`
- Create: `web/frontend/src/views/trade/__tests__/Reconciliation.spec.ts`

- [ ] **Step 1: Write a failing page test for account loading and discrepancy statuses**

```ts
import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/api/trade.ts', () => ({
  tradeApi: {
    getReconciliationAccounts: vi.fn().mockResolvedValue([{ accountId: 'backtest:7', label: 'Backtest #7', accountType: 'backtest' }]),
    getReconciliationStatements: vi.fn().mockResolvedValue({ items: [], totalCount: 0 }),
    getReconciliationResults: vi.fn().mockResolvedValue({
      items: [
        { matchStatus: 'matched', matchReason: 'matched_by_order_id', internalRow: { symbol: '600519.SH' }, brokerRow: { symbol: '600519.SH' } },
        { matchStatus: 'missing_broker_record', matchReason: 'no_broker_candidate', internalRow: { symbol: '300750.SZ' }, brokerRow: null },
      ],
      totalCount: 2,
    }),
  },
}))

import TradeReconciliationPage from '../Reconciliation.vue'

describe('Trade reconciliation page', () => {
  it('loads account options and renders read-only discrepancy statuses', async () => {
    const wrapper = mount(TradeReconciliationPage as never)

    await flushPromises()

    expect(wrapper.text()).toContain('Backtest #7')
    expect(wrapper.text()).toContain('matched')
    expect(wrapper.text()).toContain('missing_broker_record')
  })
})
```

- [ ] **Step 2: Run the page test and confirm the new page does not exist yet**

Run:

```bash
cd web/frontend && npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts
```

Expected:

```text
FAIL ... Cannot find module '../Reconciliation.vue'
```

- [ ] **Step 3: Extend the trade API service with reconciliation methods**

```ts
async getReconciliationAccounts(): Promise<Array<{ accountId: string; label: string; accountType: string }>> {
  const rawData = await request.get(`${this.baseUrl}/reconciliation/accounts`)
  const payload = unwrapResponseData<TradeRouteEnvelope<{ items?: unknown[] }>>(rawData)
  return asArray(payload?.items).map((item) => {
    const record = asRecord(item)
    return {
      accountId: asString(record.account_id),
      label: asString(record.label),
      accountType: asString(record.account_type),
    }
  })
}

async importReconciliationCsv(formData: FormData): Promise<{ importBatchId: string }> {
  const rawData = await request.post(`${this.baseUrl}/reconciliation/import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  const payload = unwrapResponseData<TradeRouteEnvelope<{ import_batch_id?: string }>>(rawData)
  return { importBatchId: asString(payload.import_batch_id) }
}
```

- [ ] **Step 4: Add the page-local transform and orchestration composable**

```ts
export interface ReconciliationResultRowVM {
  symbol: string
  matchStatus: 'matched' | 'mismatched' | 'missing_broker_record'
  matchReason: string
}

export function toReconciliationResultRows(raw: unknown): ReconciliationResultRowVM[] {
  const payload = asRecord(raw)
  const items = Array.isArray(payload.items) ? payload.items : []
  return items.map((item) => {
    const record = asRecord(item)
    const internalRow = asRecord(record.internalRow || record.internal_row)
    return {
      symbol: asString(internalRow.symbol),
      matchStatus: asString(record.matchStatus || record.match_status) as ReconciliationResultRowVM['matchStatus'],
      matchReason: asString(record.matchReason || record.match_reason),
    }
  })
}
```

- [ ] **Step 5: Create the dedicated reconciliation page and route/menu entries**

```ts
{
  path: 'reconciliation',
  name: 'trade-reconciliation',
  component: () => import('@/views/trade/Reconciliation.vue'),
  meta: { title: '对账单', requiresAuth: true, api: '/api/v1/trade/reconciliation/statements' }
}
```

```ts
{ path: '/trade/reconciliation', label: '对账单', icon: 'TradeHistory', businessKey: 'trade.reconciliation' }
```

```ts
'trade-reconciliation': {
  type: 'page',
  routePath: 'reconciliation',
  title: '对账单',
  description: '内部账单与外部券商成交对账',
  apiEndpoint: '/api/v1/trade/reconciliation/statements',
  wsChannel: 'trade:reconciliation',
  component: 'Reconciliation.vue',
  requiresAuth: true,
},
```

- [ ] **Step 6: Re-run the page test and targeted lint**

Run:

```bash
cd web/frontend && npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts
```

Expected:

```text
1 file passed
```

Run:

```bash
cd web/frontend && npx eslint --no-warn-ignored \
  src/api/trade.ts \
  src/views/trade/composables/reconciliationDataTransform.ts \
  src/views/trade/composables/useTradeReconciliation.ts \
  src/views/trade/Reconciliation.vue \
  src/views/trade/__tests__/Reconciliation.spec.ts \
  src/router/index.ts \
  src/layouts/MenuConfig.ts \
  src/config/pageConfig.ts
```

Expected:

```text
no output
```

- [ ] **Step 7: Commit the frontend slice**

```bash
git add \
  web/frontend/src/api/trade.ts \
  web/frontend/src/views/trade/composables/reconciliationDataTransform.ts \
  web/frontend/src/views/trade/composables/useTradeReconciliation.ts \
  web/frontend/src/views/trade/Reconciliation.vue \
  web/frontend/src/router/index.ts \
  web/frontend/src/layouts/MenuConfig.ts \
  web/frontend/src/config/pageConfig.ts \
  web/frontend/src/views/trade/__tests__/Reconciliation.spec.ts
git commit -m "feat(trade): add reconciliation statement page"
```

---

### Task 6: End-To-End Smoke And FUNCTION_TREE Closeout

**Files:**
- Create: `tests/e2e/trade-reconciliation-page.spec.ts`
- Modify: `docs/FUNCTION_TREE.md`

- [ ] **Step 1: Write the mocked reconciliation smoke test**

```ts
import { test, expect } from '@playwright/test'

test('trade reconciliation page imports and exports statement results', async ({ page }) => {
  await page.route('**/api/v1/trade/reconciliation/accounts', async (route) => {
    await route.fulfill({ json: { success: true, data: { items: [{ account_id: 'backtest:7', label: 'Backtest #7', account_type: 'backtest' }] } } })
  })
  await page.route('**/api/v1/trade/reconciliation/statements**', async (route) => {
    await route.fulfill({ json: { success: true, data: { items: [], total_count: 0 } } })
  })
  await page.route('**/api/v1/trade/reconciliation/import', async (route) => {
    await route.fulfill({ json: { success: true, data: { import_batch_id: 'batch-001' } } })
  })
  await page.route('**/api/v1/trade/reconciliation/results**', async (route) => {
    await route.fulfill({ json: { success: true, data: { items: [{ match_status: 'matched', match_reason: 'matched_by_order_id', internal_row: { symbol: '600519.SH' }, broker_row: { symbol: '600519.SH' } }], total_count: 1 } } })
  })
  await page.route('**/api/v1/trade/reconciliation/export**', async (route) => {
    await route.fulfill({ status: 200, headers: { 'content-type': 'text/csv; charset=utf-8' }, body: 'match_status,symbol\nmatched,600519.SH\n' })
  })

  await page.goto('/trade/reconciliation')
  await expect(page.getByText('Backtest #7')).toBeVisible()
  await expect(page.getByText('matched')).toBeVisible()
})
```

- [ ] **Step 2: Run the smoke test and confirm it fails before the page and routes exist**

Run:

```bash
npx playwright test tests/e2e/trade-reconciliation-page.spec.ts --project=chromium
```

Expected:

```text
FAIL ... navigation or selector errors before the page is implemented
```

- [ ] **Step 3: Update `FUNCTION_TREE` only after the smoke and targeted tests pass**

```md
| 对账单 | ✅ | `web/frontend/src/views/trade/Reconciliation.vue`<br>`web/backend/app/api/trade/reconciliation_routes.py`<br>`web/backend/app/services/statement_reconciliation/` | 多账户切换、内部账单投影、`normalized_template` 与 `miniQMT` CSV 导入、自动对账状态与 CSV 导出 |
```

- [ ] **Step 4: Run the final verification bundle**

Run:

```bash
pytest \
  web/backend/tests/test_trade_reconciliation_internal_statement_source.py \
  web/backend/tests/test_trade_reconciliation_parsers.py \
  web/backend/tests/test_trade_reconciliation_matcher.py \
  web/backend/tests/test_trade_reconciliation_routes.py \
  -q --no-cov
```

Expected:

```text
all selected backend reconciliation tests pass
```

Run:

```bash
cd web/frontend && npx vitest run src/views/trade/__tests__/Reconciliation.spec.ts
```

Expected:

```text
1 file passed
```

Run:

```bash
npx playwright test tests/e2e/trade-reconciliation-page.spec.ts --project=chromium
```

Expected:

```text
1 passed
```

Run:

```bash
pytest tests/unit/governance/test_function_tree_doc_sync.py tests/unit/governance/test_function_tree_catalog.py -q --no-cov
```

Expected:

```text
all selected FUNCTION_TREE governance tests pass
```

- [ ] **Step 5: Commit the smoke and governance closeout**

```bash
git add \
  tests/e2e/trade-reconciliation-page.spec.ts \
  docs/FUNCTION_TREE.md
git commit -m "docs(function-tree): close trade reconciliation mvp"
```

---

## Self-Review Checklist

- Spec coverage:
  - account-descriptor contract: Task 2
  - internal statement projection: Task 2
  - normalized-template and `miniQMT` import: Task 3
  - deterministic `matched` / `mismatched` / `missing_broker_record`: Task 4
  - CSV export: Task 4
  - dedicated page and route: Task 5
  - smoke and `FUNCTION_TREE` closeout: Task 6
- Placeholder scan:
  - no `TODO`, `TBD`, or deferred “implement later” steps remain in the task body
- Type consistency:
  - `account_id`, `import_batch_id`, `match_status`, and `source_type` names are used consistently across backend, frontend, and tests
