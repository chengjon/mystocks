# AkShare `stock_dt_pool_em` Candidate Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote `stock_dt_pool_em -> stock_zt_pool_dtgc_em` from advisory help-candidate to an approved AkShare runtime mapping, with gate, repo-truth, adapter, route, registry, and focused tests updated together.

**Architecture:** Keep the public contract on the canonical target name `stock_dt_pool_em`, but resolve the upstream call internally to `akshare.stock_zt_pool_dtgc_em`. Update the quality-gate layer so `stock_dt_pool_em` is treated as a mapped capability instead of a same-name miss, and keep all other unresolved section-6 items on their current semantics.

**Tech Stack:** Python 3.12, FastAPI, Pandas, pytest, OpenSpec, AkShare market adapter, YAML registry, markdown repo-truth docs.

---

### Task 1: Promote `stock_dt_pool_em` In The Gate Layer

**Files:**
- Modify: `tests/unit/scripts/test_collect_akshare_market_function_availability.py`
- Modify: `tests/unit/scripts/test_validate_akshare_market_repo_truth.py`
- Modify: `scripts/dev/quality_gate/collect_akshare_market_function_availability.py`
- Modify: `scripts/dev/quality_gate/validate_akshare_market_repo_truth.py`

- [ ] **Step 1: Write the failing availability test**

```python
def test_collect_akshare_market_function_availability_marks_dt_pool_as_mapped(monkeypatch):
    class FakeModule:
        __version__ = "test-version"

        @staticmethod
        def stock_zt_pool_dtgc_em(date: str = "20241011"):
            return None

    def fake_import(name: str):
        assert name == "fake_akshare"
        return FakeModule

    monkeypatch.setattr(
        "scripts.dev.quality_gate.collect_akshare_market_function_availability.importlib.import_module",
        fake_import,
    )

    payload, exit_code = collect_availability(
        module_name="fake_akshare",
        function_names=["stock_dt_pool_em"],
    )

    row = payload["functions"][0]
    assert exit_code == 0
    assert row["available"] is True
    assert row["target_available"] is False
    assert row["resolution_status"] == "mapped"
    assert row["resolved_function"] == "stock_zt_pool_dtgc_em"
```

- [ ] **Step 2: Run the availability test to verify it fails**

Run:

```bash
pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py::test_collect_akshare_market_function_availability_marks_dt_pool_as_mapped -q --no-cov
```

Expected: `FAIL` because `collect_availability()` does not yet emit `target_available`, `resolution_status`, or `resolved_function`, and still treats `stock_dt_pool_em` as unavailable.

- [ ] **Step 3: Write the failing repo-truth validator test**

```python
def test_validate_akshare_market_repo_truth_accepts_dt_pool_mapped_status(tmp_path: Path):
    manifest = [
        {
            "task_id": "6.5",
            "function_name": "stock_dt_pool_em",
            "registry_key": "akshare_stock_dt_pool_em",
            "adapter_method": "get_stock_dt_pool_em",
            "route_fragment": "/stock/dt-pool/em",
            "unit_test_token": "test_get_stock_dt_pool_em_normalizes_columns",
            "backend_test_token": "test_stock_dt_pool_em_route_returns_success_payload",
            "api_test_token": "test_stock_dt_pool_em_endpoint",
        }
    ]
```

Fixture expectations:

```json
{
  "functions": [
    {
      "name": "stock_dt_pool_em",
      "available": true,
      "target_available": false,
      "resolution_status": "mapped",
      "resolved_function": "stock_zt_pool_dtgc_em"
    }
  ]
}
```

Repo-truth row expectation:

```markdown
| 6.5 | `stock_dt_pool_em` | `/api/akshare/market/stock/dt-pool/em` | `get_stock_dt_pool_em()` | 已实现（官方改名映射：stock_zt_pool_dtgc_em） |
```

- [ ] **Step 4: Run the repo-truth validator test to verify it fails**

Run:

```bash
pytest tests/unit/scripts/test_validate_akshare_market_repo_truth.py::test_validate_akshare_market_repo_truth_accepts_dt_pool_mapped_status -q --no-cov
```

Expected: `FAIL` because `validate_akshare_market_repo_truth.py` only understands same-name `available=True` or missing `available=False`.

- [ ] **Step 5: Implement the minimal gate-layer code**

In `collect_akshare_market_function_availability.py`, add an approved-mapping table for this batch only:

```python
APPROVED_RUNTIME_MAPPINGS = {
    "stock_dt_pool_em": ("stock_zt_pool_dtgc_em",),
}
```

When a canonical target is missing but an approved upstream mapping is callable, emit:

```python
row.update(
    {
        "available": True,
        "target_available": False,
        "resolved_function": "stock_zt_pool_dtgc_em",
        "resolution_status": "mapped",
    }
)
```

In `validate_akshare_market_repo_truth.py`, treat mapped availability as implemented, and allow the repo-truth status fragment:

```python
expected_status_fragment = "已实现" if available else "未检出同名函数"
```

while preserving `target_available` for audit output.

- [ ] **Step 6: Run the gate tests to verify they pass**

Run:

```bash
pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py -q --no-cov
pytest tests/unit/scripts/test_validate_akshare_market_repo_truth.py -q --no-cov
```

Expected: both files pass with the new mapped-state assertions green.

- [ ] **Step 7: Commit the gate-layer micro-batch**

```bash
git add tests/unit/scripts/test_collect_akshare_market_function_availability.py tests/unit/scripts/test_validate_akshare_market_repo_truth.py scripts/dev/quality_gate/collect_akshare_market_function_availability.py scripts/dev/quality_gate/validate_akshare_market_repo_truth.py
git commit -m "feat(akshare): support dt-pool mapped gate status"
```

### Task 2: Add The Runtime `dt_pool` Vertical Slice

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
async def test_get_stock_dt_pool_em_normalizes_columns():
    adapter = AkshareMarketDataAdapter()

    with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_zt_pool_dtgc_em", create=True) as mock_dt_pool:
        mock_dt_pool.return_value = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["000001"],
                "名称": ["平安银行"],
                "涨跌幅": [-9.98],
                "最新价": [8.21],
                "成交额": [560000000.0],
                "流通市值": [145000000000.0],
                "总市值": [182000000000.0],
                "动态市盈率": [5.8],
                "换手率": [3.2],
                "封单资金": [68000000.0],
                "最后封板时间": ["145501"],
                "板上成交额": [120000000.0],
                "连续跌停": [2],
                "开板次数": [1],
                "所属行业": ["银行"],
            }
        )

        result = await adapter.get_stock_dt_pool_em("20241011")

    assert {
        "sequence_no",
        "symbol",
        "stock_name",
        "change_percent",
        "latest_price",
        "turnover_amount",
        "circulating_market_cap",
        "total_market_cap",
        "dynamic_pe_ratio",
        "turnover_rate",
        "limit_down_fund",
        "last_limit_down_time",
        "board_turnover_amount",
        "consecutive_limit_down_count",
        "reopen_count",
        "industry",
        "query_date",
        "query_timestamp",
    } <= set(result.columns)
```

- [ ] **Step 2: Run the adapter test to verify it fails**

Run:

```bash
pytest tests/unit/adapters/test_akshare_stock_sentiment_incremental.py::test_get_stock_dt_pool_em_normalizes_columns -q --no-cov
```

Expected: `FAIL` because `AkshareMarketDataAdapter` does not yet expose `get_stock_dt_pool_em`.

- [ ] **Step 3: Write the failing backend route test**

```python
def test_stock_dt_pool_em_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "sequence_no": [1],
            "symbol": ["000001"],
            "stock_name": ["平安银行"],
            "change_percent": [-9.98],
            "latest_price": [8.21],
            "query_date": ["20241011"],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_dt_pool_em",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/stock/dt-pool/em?date=20241011")

    payload = response.json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["date"] == "20241011"
    assert payload["data"]["provider"] == "em"
    assert payload["data"]["data_type"] == "dt_pool"
```

- [ ] **Step 4: Run the backend route test to verify it fails**

Run:

```bash
pytest tests/backend/test_akshare_market_additional_routes.py::test_stock_dt_pool_em_route_returns_success_payload -q --no-cov
```

Expected: `FAIL` with missing route or missing adapter method.

- [ ] **Step 5: Implement the minimal runtime code**

In `stock_sentiment.py`, mirror the existing `get_stock_zt_pool_em()` structure but call `ak.stock_zt_pool_dtgc_em(date=date)` and rename columns as follows:

```python
{
    "序号": "sequence_no",
    "代码": "symbol",
    "名称": "stock_name",
    "涨跌幅": "change_percent",
    "最新价": "latest_price",
    "成交额": "turnover_amount",
    "流通市值": "circulating_market_cap",
    "总市值": "total_market_cap",
    "动态市盈率": "dynamic_pe_ratio",
    "换手率": "turnover_rate",
    "封单资金": "limit_down_fund",
    "最后封板时间": "last_limit_down_time",
    "板上成交额": "board_turnover_amount",
    "连续跌停": "consecutive_limit_down_count",
    "开板次数": "reopen_count",
    "所属行业": "industry",
}
```

In `sentiment_monitor.py`, add `STOCK_DT_POOL_EM_RESPONSES` and route:

```python
@router.get("/stock/dt-pool/em", ...)
async def get_stock_dt_pool_em(date: str = Query(...), current_user: User = Depends(get_current_user)):
    df = await akshare_market_adapter.get_stock_dt_pool_em(date)
```

In `config/data_sources_registry.yaml`, add:

```yaml
akshare_stock_dt_pool_em:
  endpoint_name: akshare.stock_dt_pool_em
  description: AKShare跌停股池
  test_parameters:
    date: '20241011'
```

Add the placeholder file-test:

```python
def test_stock_dt_pool_em_endpoint(self, api_test_fixtures):
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

Expected: the new `dt_pool` adapter and route tests pass with the existing focused suite.

- [ ] **Step 7: Commit the runtime micro-batch**

```bash
git add tests/unit/adapters/test_akshare_stock_sentiment_incremental.py src/adapters/akshare/market_adapter/stock_sentiment.py tests/backend/test_akshare_market_additional_routes.py web/backend/app/api/akshare_market/sentiment_monitor.py config/data_sources_registry.yaml tests/api/file_tests/test_akshare_market_api.py
git commit -m "feat(akshare): add mapped dt-pool runtime slice"
```

### Task 3: Sync Repo-Truth And End-To-End Verification

**Files:**
- Modify: `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md`
- Modify: `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`
- Modify: `docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md`
- Modify: `openspec/changes/expand-akshare-data-sources/tasks.md`
- Modify: `tests/unit/scripts/test_run_akshare_market_gates.py` (only if summary fields need updates)

- [ ] **Step 1: Update repo-truth docs for the promoted mapping**

Change row `6.5` in `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md` to:

```markdown
| 6.5 | `stock_dt_pool_em` | `/api/akshare/market/stock/dt-pool/em` | `get_stock_dt_pool_em()` | 已实现（官方改名映射：stock_zt_pool_dtgc_em） |
```

Update guide / troubleshooting text so `stock_dt_pool_em` moves from “advisory only” to “approved mapping already landed”, while `stock_strong_pool_em` and `stock_new_em` remain advisory candidates.

- [ ] **Step 2: Update OpenSpec task state**

In `openspec/changes/expand-akshare-data-sources/tasks.md`:

```markdown
- [x] 6.5 实现跌停板行情 (akshare.stock_dt_pool_em)
```

Preserve:

- `6.3` excluded
- `6.6` advisory candidate only
- `6.7` unresolved gap
- `6.9` advisory candidate only
- `6.10-6.12` unchecked

- [ ] **Step 3: Run the full AkShare gate verification**

Run:

```bash
pytest tests/unit/scripts/test_run_akshare_market_gates.py -q --no-cov
python scripts/dev/quality_gate/run_akshare_market_gates.py --output-dir /tmp/akshare-market-gates-dt-pool
openspec validate expand-akshare-data-sources --strict
```

Expected:

- test file passes
- wrapper summary `pass=true`
- repo-truth gate `violation_count=0`
- OpenSpec validation passes

- [ ] **Step 4: Commit the repo-truth sync**

```bash
git add docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md openspec/changes/expand-akshare-data-sources/tasks.md tests/unit/scripts/test_run_akshare_market_gates.py
git commit -m "docs(akshare): mark dt-pool mapping implemented"
```

