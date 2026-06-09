# AkShare `stock_new_em` Candidate Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote `stock_new_em -> stock_zt_pool_sub_new_em` from advisory help-candidate to an approved AkShare runtime mapping, with gate, repo-truth, adapter, route, registry, and focused tests updated together.

**Architecture:** Keep the public contract on the canonical target name `stock_new_em`, but resolve the upstream call internally to `akshare.stock_zt_pool_sub_new_em`. Follow the same micro-batch pattern already used for `stock_dt_pool_em` and `stock_strong_pool_em`: first upgrade gate semantics from advisory to mapped, then add the runtime vertical slice, then sync repo-truth and OpenSpec state.

**Tech Stack:** Python 3.12, FastAPI, Pandas, pytest, OpenSpec, AkShare market adapter, YAML registry, markdown repo-truth docs.

---

### Task 1: Promote `stock_new_em` In The Gate Layer

**Files:**
- Modify: `tests/unit/scripts/test_collect_akshare_market_function_availability.py`
- Modify: `scripts/dev/quality_gate/collect_akshare_market_function_availability.py`

- [ ] **Step 1: Write the failing availability tests**

Add a dedicated mapped-state test:

```python
def test_collect_akshare_market_function_availability_marks_new_pool_as_mapped(monkeypatch):
    class FakeModule:
        __version__ = "test-version"

        @staticmethod
        def stock_zt_pool_sub_new_em(date: str = "20241011"):
            return None

    def fake_import(name: str):
        assert name == "fake_akshare"
        return FakeModule

    monkeypatch.setattr("scripts.dev.quality_gate.collect_akshare_market_function_availability.importlib.import_module", fake_import)

    payload, exit_code = collect_availability(
        module_name="fake_akshare",
        function_names=["stock_new_em"],
    )

    row = payload["functions"][0]
    assert exit_code == 0
    assert row["available"] is True
    assert row["target_available"] is False
    assert row["resolution_status"] == "mapped"
    assert row["resolved_function"] == "stock_zt_pool_sub_new_em"
```

Also update the existing `test_collect_akshare_market_function_availability_surfaces_help_candidates()` expectation so `stock_new_em` no longer stays in `help_candidate_functions`.

- [ ] **Step 2: Run the availability tests to verify they fail**

Run:

```bash
pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py::test_collect_akshare_market_function_availability_marks_new_pool_as_mapped -q --no-cov
pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py::test_collect_akshare_market_function_availability_surfaces_help_candidates -q --no-cov
```

Expected:

- the new mapped test fails because `collect_availability()` does not yet treat `stock_new_em` as approved
- the existing help-candidate test still expects `stock_new_em` to remain advisory

- [ ] **Step 3: Implement the minimal gate-layer code**

In `collect_akshare_market_function_availability.py`, extend the approved mapping table:

```python
APPROVED_RUNTIME_MAPPINGS = {
    "stock_dt_pool_em": ("stock_zt_pool_dtgc_em",),
    "stock_strong_pool_em": ("stock_zt_pool_strong_em",),
    "stock_new_em": ("stock_zt_pool_sub_new_em",),
}
```

No validator code change is expected for this batch, because `tests/unit/scripts/test_validate_akshare_market_repo_truth.py::test_validate_akshare_market_repo_truth_accepts_dt_pool_mapped_status` already covers generic mapped availability semantics.

- [ ] **Step 4: Run the gate tests to verify they pass**

Run:

```bash
pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py -q --no-cov
pytest tests/unit/scripts/test_validate_akshare_market_repo_truth.py -q --no-cov
```

Expected: both files pass, with the new `stock_new_em` mapped-state assertion green and the generic mapped repo-truth validator regression still passing.

### Task 2: Add The Runtime `new_pool` Vertical Slice

**Files:**
- Modify: `tests/unit/adapters/test_akshare_stock_sentiment_incremental.py`
- Modify: `src/adapters/akshare/market_adapter/stock_sentiment.py`
- Modify: `tests/backend/test_akshare_market_additional_routes.py`
- Modify: `web/backend/app/api/akshare_market/sentiment_monitor.py`
- Modify: `config/data_sources_registry.yaml`
- Modify: `tests/api/file_tests/test_akshare_market_api.py`

- [ ] **Step 1: Write the failing adapter test**

```python
@pytest.mark.asyncio
async def test_get_stock_new_em_normalizes_columns():
    adapter = AkshareMarketDataAdapter()

    with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_zt_pool_sub_new_em", create=True) as mock_new_pool:
        mock_new_pool.return_value = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["301000"],
                "名称": ["肇民科技"],
                "涨跌幅": [10.01],
                "最新价": [35.61],
                "涨停价": [35.61],
                "成交额": [980000000.0],
                "流通市值": [5400000000.0],
                "总市值": [8200000000.0],
                "转手率": [12.6],
                "开板几日": [5],
                "开板日期": ["2024-10-08"],
                "上市日期": ["2024-09-27"],
                "是否新高": ["是"],
                "涨停统计": ["2/6"],
                "所属行业": ["汽车零部件"],
            }
        )

        result = await adapter.get_stock_new_em("20241011")

    assert {
        "sequence_no",
        "symbol",
        "stock_name",
        "change_percent",
        "latest_price",
        "limit_up_price",
        "turnover_amount",
        "circulating_market_cap",
        "total_market_cap",
        "turnover_rate",
        "open_board_days",
        "open_board_date",
        "listed_date",
        "is_new_high",
        "limit_up_stats",
        "industry",
        "query_date",
        "query_timestamp",
    } <= set(result.columns)
```

- [ ] **Step 2: Run the adapter test to verify it fails**

Run:

```bash
pytest tests/unit/adapters/test_akshare_stock_sentiment_incremental.py::test_get_stock_new_em_normalizes_columns -q --no-cov
```

Expected: `FAIL` because `AkshareMarketDataAdapter` does not yet expose `get_stock_new_em`.

- [ ] **Step 3: Write the failing backend route test**

```python
def test_stock_new_em_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "sequence_no": [1],
            "symbol": ["301000"],
            "stock_name": ["肇民科技"],
            "change_percent": [10.01],
            "listed_date": ["2024-09-27"],
            "query_date": ["20241011"],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_new_em",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/stock/new/em?date=20241011")

    payload = response.json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["date"] == "20241011"
    assert payload["data"]["provider"] == "em"
    assert payload["data"]["data_type"] == "new_pool"
```

- [ ] **Step 4: Run the backend route test to verify it fails**

Run:

```bash
pytest tests/backend/test_akshare_market_additional_routes.py::test_stock_new_em_route_returns_success_payload -q --no-cov
```

Expected: `FAIL` with missing route or missing adapter method.

- [ ] **Step 5: Implement the minimal runtime code**

In `stock_sentiment.py`, add:

```python
async def get_stock_new_em(self, date: str) -> pd.DataFrame:
    return ak.stock_zt_pool_sub_new_em(date=date)
```

and normalize columns as follows:

```python
{
    "序号": "sequence_no",
    "代码": "symbol",
    "名称": "stock_name",
    "涨跌幅": "change_percent",
    "最新价": "latest_price",
    "涨停价": "limit_up_price",
    "成交额": "turnover_amount",
    "流通市值": "circulating_market_cap",
    "总市值": "total_market_cap",
    "转手率": "turnover_rate",
    "开板几日": "open_board_days",
    "开板日期": "open_board_date",
    "上市日期": "listed_date",
    "是否新高": "is_new_high",
    "涨停统计": "limit_up_stats",
    "所属行业": "industry",
}
```

Also add `query_date` and `query_timestamp`.

In `sentiment_monitor.py`, add `STOCK_NEW_EM_RESPONSES` and route:

```python
@router.get("/stock/new/em", ...)
async def get_stock_new_em(date: str = Query(...), current_user: User = Depends(get_current_user)):
    df = await akshare_market_adapter.get_stock_new_em(date)
```

In `config/data_sources_registry.yaml`, add:

```yaml
akshare_stock_new_em:
  endpoint_name: akshare.stock_new_em
  description: AKShare次新股池
  test_parameters:
    date: '20241011'
```

Add the file-test placeholder:

```python
def test_stock_new_em_endpoint(self, api_test_fixtures):
    assert api_test_fixtures["retry_attempts"] >= 1
    assert api_test_fixtures["mock_enabled"] is True
    assert api_test_fixtures["contract_validation"] is True
```

- [ ] **Step 6: Run the runtime tests to verify they pass**

Run:

```bash
pytest tests/unit/adapters/test_akshare_stock_sentiment_incremental.py -q --no-cov
pytest tests/backend/test_akshare_market_additional_routes.py -q --no-cov
pytest tests/api/file_tests/test_akshare_market_api.py -q --no-cov
```

Expected: the new `new_pool` adapter and route tests pass with the focused suite.

### Task 3: Sync Repo-Truth And End-To-End Verification

**Files:**
- Modify: `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md`
- Modify: `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`
- Modify: `docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md`
- Modify: `openspec/changes/expand-akshare-data-sources/tasks.md`

- [ ] **Step 1: Update repo-truth docs for the promoted mapping**

Change row `6.9` in `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md` to:

```markdown
| 6.9 | `stock_new_em` | `/api/akshare/market/stock/new/em` | `get_stock_new_em()` | 已实现（官方改名映射：stock_zt_pool_sub_new_em） |
```

Update guide / troubleshooting text so `stock_new_em` moves from “advisory only” to “approved mapping already landed”, while `stock_news_main_em` stays excluded and `stock_weak_pool_em` stays unresolved.

- [ ] **Step 2: Update OpenSpec task state**

In `openspec/changes/expand-akshare-data-sources/tasks.md`:

```markdown
- [x] 6.9 实现次新股池 (akshare.stock_new_em)
```

Preserve:

- `6.3` excluded
- `6.7` unresolved gap
- `6.10-6.12` unchecked

- [ ] **Step 3: Run the full AkShare gate verification**

Run:

```bash
pytest tests/unit/scripts/test_run_akshare_market_gates.py -q --no-cov
python scripts/dev/quality_gate/run_akshare_market_gates.py --output-dir /tmp/akshare-market-gates-new-pool
openspec validate expand-akshare-data-sources --strict
python -m py_compile src/adapters/akshare/market_adapter/stock_sentiment.py web/backend/app/api/akshare_market/sentiment_monitor.py
```

Expected:

- test file passes
- wrapper summary `pass=true`
- wrapper summary shows `available_count=7`, `missing_count=2`, `repo_truth_violation_count=0`
- OpenSpec validation passes
- py_compile passes

- [ ] **Step 4: Commit the micro-batch**

```bash
git add scripts/dev/quality_gate/collect_akshare_market_function_availability.py src/adapters/akshare/market_adapter/stock_sentiment.py web/backend/app/api/akshare_market/sentiment_monitor.py config/data_sources_registry.yaml tests/api/file_tests/test_akshare_market_api.py tests/backend/test_akshare_market_additional_routes.py tests/unit/adapters/test_akshare_stock_sentiment_incremental.py tests/unit/scripts/test_collect_akshare_market_function_availability.py docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md openspec/changes/expand-akshare-data-sources/tasks.md
git commit --only scripts/dev/quality_gate/collect_akshare_market_function_availability.py src/adapters/akshare/market_adapter/stock_sentiment.py web/backend/app/api/akshare_market/sentiment_monitor.py config/data_sources_registry.yaml tests/api/file_tests/test_akshare_market_api.py tests/backend/test_akshare_market_additional_routes.py tests/unit/adapters/test_akshare_stock_sentiment_incremental.py tests/unit/scripts/test_collect_akshare_market_function_availability.py docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md openspec/changes/expand-akshare-data-sources/tasks.md -m "feat(akshare): promote new-pool official mapping"
```
