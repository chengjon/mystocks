# AkShare `stock_strong_pool_em` Candidate Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote `stock_strong_pool_em -> stock_zt_pool_strong_em` from advisory help-candidate to an approved AkShare runtime mapping, with gate, repo-truth, adapter, route, registry, and focused tests updated together.

**Architecture:** Keep the public contract on the canonical target name `stock_strong_pool_em`, but resolve the upstream call internally to `akshare.stock_zt_pool_strong_em`. Follow the same micro-batch pattern already used for `stock_dt_pool_em`: first upgrade gate semantics from advisory to mapped, then add the runtime vertical slice, then sync repo-truth and OpenSpec state.

**Tech Stack:** Python 3.12, FastAPI, Pandas, pytest, OpenSpec, AkShare market adapter, YAML registry, markdown repo-truth docs.

---

### Task 1: Promote `stock_strong_pool_em` In The Gate Layer

**Files:**
- Modify: `tests/unit/scripts/test_collect_akshare_market_function_availability.py`
- Modify: `scripts/dev/quality_gate/collect_akshare_market_function_availability.py`

- [ ] **Step 1: Write the failing availability test**

```python
def test_collect_akshare_market_function_availability_marks_strong_pool_as_mapped(monkeypatch):
    class FakeModule:
        __version__ = "test-version"

        @staticmethod
        def stock_zt_pool_strong_em(date: str = "20241011"):
            return None

    def fake_import(name: str):
        assert name == "fake_akshare"
        return FakeModule

    monkeypatch.setattr("scripts.dev.quality_gate.collect_akshare_market_function_availability.importlib.import_module", fake_import)

    payload, exit_code = collect_availability(
        module_name="fake_akshare",
        function_names=["stock_strong_pool_em"],
    )

    row = payload["functions"][0]
    assert exit_code == 0
    assert row["available"] is True
    assert row["target_available"] is False
    assert row["resolution_status"] == "mapped"
    assert row["resolved_function"] == "stock_zt_pool_strong_em"
```

- [ ] **Step 2: Run the availability test to verify it fails**

Run:

```bash
pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py::test_collect_akshare_market_function_availability_marks_strong_pool_as_mapped -q --no-cov
```

Expected: `FAIL` because `collect_availability()` does not yet treat `stock_strong_pool_em` as an approved mapped capability.

- [ ] **Step 3: Implement the minimal gate-layer code**

In `collect_akshare_market_function_availability.py`, extend the approved mapping table:

```python
APPROVED_RUNTIME_MAPPINGS = {
    "stock_dt_pool_em": ("stock_zt_pool_dtgc_em",),
    "stock_strong_pool_em": ("stock_zt_pool_strong_em",),
}
```

No validator code change is expected for this batch, because `tests/unit/scripts/test_validate_akshare_market_repo_truth.py::test_validate_akshare_market_repo_truth_accepts_dt_pool_mapped_status` already covers generic mapped availability semantics.

- [ ] **Step 4: Run the gate tests to verify they pass**

Run:

```bash
pytest tests/unit/scripts/test_collect_akshare_market_function_availability.py -q --no-cov
pytest tests/unit/scripts/test_validate_akshare_market_repo_truth.py -q --no-cov
```

Expected: both files pass, with the new strong-pool mapped-state assertion green and the generic mapped repo-truth validator regression still passing.

### Task 2: Add The Runtime `strong_pool` Vertical Slice

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
async def test_get_stock_strong_pool_em_normalizes_columns():
    adapter = AkshareMarketDataAdapter()

    with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_zt_pool_strong_em", create=True) as mock_strong_pool:
        mock_strong_pool.return_value = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["002594"],
                "名称": ["比亚迪"],
                "涨跌幅": [9.98],
                "最新价": [268.12],
                "涨停价": [268.12],
                "成交额": [3560000000.0],
                "流通市值": [712000000000.0],
                "总市值": [780000000000.0],
                "换手率": [4.8],
                "涨速": [1.2],
                "是否新高": ["是"],
                "量比": [1.6],
                "涨停统计": ["3/5"],
                "入选理由": ["60日新高"],
                "所属行业": ["汽车整车"],
            }
        )

        result = await adapter.get_stock_strong_pool_em("20241011")

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
        "change_speed",
        "is_new_high",
        "volume_ratio",
        "limit_up_stats",
        "selection_reason",
        "industry",
        "query_date",
        "query_timestamp",
    } <= set(result.columns)
```

- [ ] **Step 2: Run the adapter test to verify it fails**

Run:

```bash
pytest tests/unit/adapters/test_akshare_stock_sentiment_incremental.py::test_get_stock_strong_pool_em_normalizes_columns -q --no-cov
```

Expected: `FAIL` because `AkshareMarketDataAdapter` does not yet expose `get_stock_strong_pool_em`.

- [ ] **Step 3: Write the failing backend route test**

```python
def test_stock_strong_pool_em_route_returns_success_payload():
    df = pd.DataFrame(
        {
            "sequence_no": [1],
            "symbol": ["002594"],
            "stock_name": ["比亚迪"],
            "change_percent": [9.98],
            "selection_reason": ["60日新高"],
            "query_date": ["20241011"],
        }
    )

    with patch(
        "app.api.akshare_market.sentiment_monitor.akshare_market_adapter.get_stock_strong_pool_em",
        new=AsyncMock(return_value=df),
    ):
        response = client.get("/api/akshare/market/stock/strong-pool/em?date=20241011")

    payload = response.json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["date"] == "20241011"
    assert payload["data"]["provider"] == "em"
    assert payload["data"]["data_type"] == "strong_pool"
```

- [ ] **Step 4: Run the backend route test to verify it fails**

Run:

```bash
pytest tests/backend/test_akshare_market_additional_routes.py::test_stock_strong_pool_em_route_returns_success_payload -q --no-cov
```

Expected: `FAIL` with missing route or missing adapter method.

- [ ] **Step 5: Implement the minimal runtime code**

In `stock_sentiment.py`, add:

```python
async def get_stock_strong_pool_em(self, date: str) -> pd.DataFrame:
    return ak.stock_zt_pool_strong_em(date=date)
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
    "换手率": "turnover_rate",
    "涨速": "change_speed",
    "是否新高": "is_new_high",
    "量比": "volume_ratio",
    "涨停统计": "limit_up_stats",
    "入选理由": "selection_reason",
    "所属行业": "industry",
}
```

Also add `query_date` and `query_timestamp`.

In `sentiment_monitor.py`, add `STOCK_STRONG_POOL_EM_RESPONSES` and route:

```python
@router.get("/stock/strong-pool/em", ...)
async def get_stock_strong_pool_em(date: str = Query(...), current_user: User = Depends(get_current_user)):
    df = await akshare_market_adapter.get_stock_strong_pool_em(date)
```

In `config/data_sources_registry.yaml`, add:

```yaml
akshare_stock_strong_pool_em:
  endpoint_name: akshare.stock_strong_pool_em
  description: AKShare强势股池
  test_parameters:
    date: '20241011'
```

Add the file-test placeholder:

```python
def test_stock_strong_pool_em_endpoint(self, api_test_fixtures):
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

Expected: the new `strong_pool` adapter and route tests pass with the focused suite.

### Task 3: Sync Repo-Truth And End-To-End Verification

**Files:**
- Modify: `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md`
- Modify: `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`
- Modify: `docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md`
- Modify: `openspec/changes/expand-akshare-data-sources/tasks.md`

- [ ] **Step 1: Update repo-truth docs for the promoted mapping**

Change row `6.6` in `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md` to:

```markdown
| 6.6 | `stock_strong_pool_em` | `/api/akshare/market/stock/strong-pool/em` | `get_stock_strong_pool_em()` | 已实现（官方改名映射：stock_zt_pool_strong_em） |
```

Update guide / troubleshooting text so `stock_strong_pool_em` moves from “advisory only” to “approved mapping already landed”, while `stock_new_em` remains advisory and `stock_news_main_em` / `stock_weak_pool_em` keep their current excluded / unresolved semantics.

- [ ] **Step 2: Update OpenSpec task state**

In `openspec/changes/expand-akshare-data-sources/tasks.md`:

```markdown
- [x] 6.6 实现强势股池 (akshare.stock_strong_pool_em)
```

Preserve:

- `6.3` excluded
- `6.7` unresolved gap
- `6.9` advisory candidate only
- `6.10-6.12` unchecked

- [ ] **Step 3: Run the full AkShare gate verification**

Run:

```bash
pytest tests/unit/scripts/test_run_akshare_market_gates.py -q --no-cov
python scripts/dev/quality_gate/run_akshare_market_gates.py --output-dir /tmp/akshare-market-gates-strong-pool
openspec validate expand-akshare-data-sources --strict
```

Expected:

- test file passes
- wrapper summary `pass=true`
- repo-truth gate `violation_count=0`
- OpenSpec validation passes

- [ ] **Step 4: Commit the micro-batch**

```bash
git add scripts/dev/quality_gate/collect_akshare_market_function_availability.py src/adapters/akshare/market_adapter/stock_sentiment.py web/backend/app/api/akshare_market/sentiment_monitor.py config/data_sources_registry.yaml tests/api/file_tests/test_akshare_market_api.py tests/unit/adapters/test_akshare_stock_sentiment_incremental.py tests/backend/test_akshare_market_additional_routes.py tests/unit/scripts/test_collect_akshare_market_function_availability.py tests/unit/scripts/test_validate_akshare_market_repo_truth.py docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md openspec/changes/expand-akshare-data-sources/tasks.md
git commit --only scripts/dev/quality_gate/collect_akshare_market_function_availability.py src/adapters/akshare/market_adapter/stock_sentiment.py web/backend/app/api/akshare_market/sentiment_monitor.py config/data_sources_registry.yaml tests/api/file_tests/test_akshare_market_api.py tests/unit/adapters/test_akshare_stock_sentiment_incremental.py tests/backend/test_akshare_market_additional_routes.py tests/unit/scripts/test_collect_akshare_market_function_availability.py tests/unit/scripts/test_validate_akshare_market_repo_truth.py docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md openspec/changes/expand-akshare-data-sources/tasks.md -m "feat(akshare): promote strong-pool official mapping"
```
