# Tasks: TDX数据源适配器集成

**Input**: Design documents from `/specs/004-tdx-pytdx-mystocks/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/IDataSource_contract.md

**Tests**: Tests are included per IDataSource contract requirements and spec.md acceptance criteria

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `adapters/`, `tests/`, `interfaces/`, `utils/` at repository root
- Paths follow MyStocks monorepo structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration

- [ ] **T001** Add TDX configuration to `.env` file (TDX_SERVER_HOST, TDX_SERVER_PORT, TDX_POOL_SIZE, TDX_MAX_RETRIES, TDX_RETRY_DELAY, TDX_API_TIMEOUT)
- [ ] **T002** [P] Verify pytdx library availability in `temp/pytdx/hq.py` - confirm TdxHq_API and TdxExHq_API classes exist
- [ ] ] **T003** [P] Verify existing utilities - ColumnMapper, normalize_date, format_stock_code_for_source in `utils/` directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core adapter infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] **T004** Create skeleton `adapters/tdx_adapter.py` with TdxDataSource class inheriting from IDataSource
- [ ] **T005** Implement `__init__()` method with configuration loading (api_timeout, max_retries from .env)
- [ ] **T006** Implement connection management helper `_get_tdx_connection()` returning TdxHq_API context manager
- [ ] **T007** Implement market code identification helper `_get_market_code(symbol: str) -> int` (0=深圳, 1=上海)
- [ ] **T008** Implement retry decorator `_retry_api_call()` with exponential backoff (max_retries, retry_delay)
- [ ] **T009** Implement data validation helper `_validate_kline_data(df: pd.DataFrame) -> pd.DataFrame` (check nulls, positive prices, OHLC logic)
- [ ] **T010** Implement logging initialization in `__init__()` - `self.logger = logging.getLogger(__name__)`
- [ ] **T011** Create stub implementations for all 8 IDataSource methods (return empty DataFrame/Dict/List with warning logs)

**Checkpoint**: Foundation ready - TdxDataSource class structure complete, user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 获取实时行情数据 (Priority: P1) 🎯 MVP

**Goal**: Users can fetch real-time stock quotes (latest price, volume, bid/ask) for single or multiple stocks from TDX servers without API rate limits

**Independent Test**: Call `tdx.get_real_time_data('600519')` and verify response contains `{'code', 'name', 'price', 'volume', 'timestamp'}` keys with valid data

### Tests for User Story 1

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] **T012** [P] [US1] Contract test for `get_real_time_data()` in `tests/test_tdx_contract.py` - verify method exists, returns Union[Dict, str], handles errors gracefully
- [ ] **T013** [P] [US1] Unit test for real-time quote success case in `tests/test_tdx_adapter.py` - mock `get_security_quotes()`, verify column mapping, validate all required fields present
- [ ] **T014** [P] [US1] Unit test for real-time quote error cases in `tests/test_tdx_adapter.py` - test invalid symbol, connection failure, timeout
- [ ] **T015** [P] [US1] Integration test for real-time quote in `tests/test_tdx_integration.py` - test actual TDX connection (optional, requires network)

### Implementation for User Story 1

- [ ] **T016** [US1] Implement `get_real_time_data(symbol: str) -> Union[Dict, str]` in `adapters/tdx_adapter.py`:
  - Use `_get_market_code()` to identify market (0/1)
  - Call `api.get_security_quotes([(market, code)])`
  - Apply `ColumnMapper.to_english()`
  - Extract single row to Dict
  - Add `timestamp` field (current time)
  - Return error string on exception
- [ ] **T017** [US1] Add logging for real-time quote operations - INFO on success (symbol, price), ERROR on failure with exception details
- [ ] **T018** [US1] Add input validation - check symbol is 6-digit string, log warning if invalid format

**Checkpoint**: At this point, User Story 1 (real-time quotes) should be fully functional and testable independently. Test: `tdx.get_real_time_data('600519')` returns valid quote dict.

---

## Phase 4: User Story 2 - 获取历史K线数据 (Priority: P1) 🎯 MVP

**Goal**: Users can fetch historical daily K-line data (OHLCV) for a stock within a date range to perform technical analysis and backtesting

**Independent Test**: Call `tdx.get_stock_daily('600519', '2024-01-01', '2024-12-31')` and verify DataFrame contains columns `['date', 'open', 'high', 'low', 'close', 'volume', 'amount']` with records within date range

### Tests for User Story 2

- [ ] **T019** [P] [US2] Contract test for `get_stock_daily()` in `tests/test_tdx_contract.py` - verify method signature, return type pd.DataFrame, required columns present
- [ ] **T020** [P] [US2] Contract test for `get_index_daily()` in `tests/test_tdx_contract.py` - verify same contract as `get_stock_daily()` but for indices
- [ ] **T021** [P] [US2] Unit test for `get_stock_daily()` success case in `tests/test_tdx_adapter.py` - mock `get_security_bars()`, verify pagination logic (800 records/batch), column mapping
- [ ] **T022** [P] [US2] Unit test for `get_stock_daily()` edge cases in `tests/test_tdx_adapter.py` - test empty date range, invalid symbol, weekend dates
- [ ] **T023** [P] [US2] Unit test for `get_index_daily()` in `tests/test_tdx_adapter.py` - mock `get_index_bars()`, verify index-specific logic
- [ ] **T024** [P] [US2] Integration test for historical K-line in `tests/test_tdx_integration.py` - fetch actual data for known stock, validate data quality

### Implementation for User Story 2

- [ ] **T025** [P] [US2] Implement `get_stock_daily(symbol: str, start_date: str, end_date: str) -> pd.DataFrame` in `adapters/tdx_adapter.py`:
  - Use `_get_market_code()` to identify market
  - Apply `normalize_date()` to start/end dates
  - Calculate total trading days in range
  - Loop pagination: call `api.get_security_bars(category=9, market, code, start_pos, 800)` in 800-record chunks
  - Concatenate all DataFrames
  - Apply `ColumnMapper.to_english()`
  - Apply `_validate_kline_data()`
  - Filter by date range
  - Return DataFrame or empty on error
- [ ] **T026** [P] [US2] Implement `get_index_daily(symbol: str, start_date: str, end_date: str) -> pd.DataFrame` in `adapters/tdx_adapter.py`:
  - Same logic as `get_stock_daily()` but use `api.get_index_bars(category=9, market, code, start_pos, 800)`
- [ ] **T027** [US2] Add logging for historical K-line operations - INFO with symbol, date range, record count; ERROR on failure
- [ ] **T028** [US2] Add progress logging for pagination - DEBUG log every batch fetched (e.g., "Fetched batch 1/5: 800 records")

**Checkpoint**: At this point, User Stories 1 AND 2 (real-time quotes + historical K-lines) should both work independently. Test: Fetch daily data for multiple stocks, verify data completeness and correctness. **MVP COMPLETE** - These two stories form the minimum viable product.

---

## Phase 5: User Story 3 - 获取分时数据和成交明细 (Priority: P2)

**Goal**: Users can view intraday minute-by-minute price movements and tick-level transaction details for short-term trading analysis

**Independent Test**: Call custom method `tdx.get_minute_data('600519', '2024-10-15')` (or similar) and verify DataFrame contains minute-level timestamps and prices. Call `tdx.get_tick_data('600519', count=1000)` and verify tick records with time, price, volume, bs_flag.

**Note**: These methods are NOT part of IDataSource interface - they are TDX-specific extensions

### Tests for User Story 3

- [ ] **T029** [P] [US3] Unit test for `get_minute_data()` method in `tests/test_tdx_adapter.py` - mock `get_minute_time_data()`, verify column mapping, time format
- [ ] **T030** [P] [US3] Unit test for `get_history_minute_data()` method in `tests/test_tdx_adapter.py` - mock `get_history_minute_time_data()`, verify date parameter
- [ ] **T031** [P] [US3] Unit test for `get_tick_data()` method in `tests/test_tdx_adapter.py` - mock `get_transaction_data()`, verify bs_flag mapping (0→SELL, 1→BUY, 2→NEUTRAL)
- [ ] **T032** [P] [US3] Integration test for minute data in `tests/test_tdx_integration.py` - fetch actual intraday data during market hours

### Implementation for User Story 3

- [ ] **T033** [P] [US3] Implement extension method `get_minute_data(symbol: str) -> pd.DataFrame` in `adapters/tdx_adapter.py`:
  - Get current day minute data using `api.get_minute_time_data(market, code)`
  - Apply `ColumnMapper.to_english()`
  - Return DataFrame with columns: ['time', 'price', 'volume', 'avg_price']
- [ ] **T034** [P] [US3] Implement extension method `get_history_minute_data(symbol: str, date: str) -> pd.DataFrame` in `adapters/tdx_adapter.py`:
  - Get historical day minute data using `api.get_history_minute_time_data(market, code, date)`
  - Apply `normalize_date()` to date parameter
  - Apply `ColumnMapper.to_english()`
- [ ] **T035** [P] [US3] Implement extension method `get_tick_data(symbol: str, start: int = 0, count: int = 1000) -> pd.DataFrame` in `adapters/tdx_adapter.py`:
  - Call `api.get_transaction_data(market, code, start, count)`
  - Map bs_flag: 0→'SELL', 1→'BUY', 2→'NEUTRAL'
  - Apply `ColumnMapper.to_english()`
  - Return DataFrame with columns: ['datetime', 'price', 'volume', 'bs_flag']
- [ ] **T036** [US3] Add logging for minute/tick data operations - INFO with symbol, data type, record count
- [ ] **T037** [US3] Update `adapters/__init__.py` to export extension methods (if needed for public API)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Test: Fetch minute and tick data for active stocks during market hours, verify granular time-series data.

---

## Phase 6: User Story 4 - 获取财务和除权除息信息 (Priority: P3)

**Goal**: Users can query financial indicators (PE, ROE, revenue) and dividend/split records for fundamental analysis and value investing

**Independent Test**: Call `tdx.get_financial_data('600519')` and verify DataFrame/Dict contains keys like `['pe_ratio', 'net_profit', 'revenue', 'roe']`. Call custom method `tdx.get_dividend_info('600519')` and verify dividend records with dates and amounts.

### Tests for User Story 4

- [ ] **T038** [P] [US4] Contract test for `get_financial_data()` in `tests/test_tdx_contract.py` - verify method signature, return type pd.DataFrame, required columns
- [ ] **T039** [P] [US4] Contract test for `get_stock_basic()` in `tests/test_tdx_contract.py` - verify method returns Dict with company info (partial support)
- [ ] **T040** [P] [US4] Unit test for `get_financial_data()` in `tests/test_tdx_adapter.py` - mock `get_finance_info()`, verify Dict→DataFrame conversion, column mapping
- [ ] **T041** [P] [US4] Unit test for `get_stock_basic()` in `tests/test_tdx_adapter.py` - mock `get_company_info_content()`, verify partial data extraction (code, name only)
- [ ] **T042** [P] [US4] Unit test for `get_dividend_info()` extension method in `tests/test_tdx_adapter.py` - mock `get_xdxr_info()`, verify category mapping (1→DIVIDEND, 2→BONUS, 3→PLACEMENT)

### Implementation for User Story 4

- [ ] **T043** [P] [US4] Implement `get_financial_data(symbol: str, period: str = 'quarter') -> pd.DataFrame` in `adapters/tdx_adapter.py`:
  - Call `api.get_finance_info(market, code)` (returns Dict)
  - Convert Dict to single-row DataFrame
  - Map Chinese keys to English: 'pe'→'pe_ratio', 'pb'→'pb_ratio', 'lirun'→'net_profit', 'shouyi'→'revenue', 'roe'→'roe', 'mgsy'→'eps', 'zgb'→'total_share', 'ltg'→'float_share'
  - Add 'date' column (current date or report date if available)
  - Note: `period` parameter ignored (pytdx limitation - only latest data available)
  - Return DataFrame or empty on error
- [ ] **T044** [P] [US4] Implement `get_stock_basic(symbol: str) -> Dict` in `adapters/tdx_adapter.py`:
  - Call `api.get_company_info_content(market, code, filename, start, length)` (returns text)
  - Parse text to extract 'code' and 'name' (simple regex or string split)
  - For other fields ('industry', 'list_date', 'total_share', 'float_share'): set to None or fetch from `get_finance_info()`
  - Return Dict with keys: {'code', 'name', 'industry', 'list_date', 'total_share', 'float_share'}
  - Log warning about partial support (⚠️ Limited data from pytdx)
  - Return empty dict on error
- [ ] **T045** [P] [US4] Implement extension method `get_dividend_info(symbol: str) -> pd.DataFrame` in `adapters/tdx_adapter.py`:
  - Call `api.get_xdxr_info(market, code)`
  - Map 'category' field: 1→'DIVIDEND', 2→'BONUS', 3→'PLACEMENT'
  - Apply `ColumnMapper.to_english()` for other columns ('date', 'fh'→'dividend', 'fhbl'→'bonus_ratio', 'pg'→'placement_ratio', 'pgjg'→'placement_price')
  - Return DataFrame with dividend records
- [ ] **T046** [US4] Add logging for financial data operations - INFO with symbol, data type; WARNING for partial support limitations
- [ ] **T047** [US4] Add documentation comment in `get_stock_basic()` explaining pytdx limitations and recommending alternative data sources (akshare) for complete info

**Checkpoint**: At this point, User Stories 1-4 should all work independently. Test: Query financial data and dividend history for large-cap stocks, verify fundamental indicators available for analysis.

---

## Phase 7: User Story 5 - 获取板块信息 (Priority: P3)

**Goal**: Users can query sector/industry classifications and constituent stocks for sector rotation analysis and thematic investing

**Independent Test**: Call `tdx.get_index_components('银行')` (or sector code) and verify list of stock codes returned. Call extension method `tdx.get_sector_list()` and verify list of sectors with names and codes.

**Note**: `get_index_components()` is part of IDataSource but may have limited pytdx support for true indices (vs sectors)

### Tests for User Story 5

- [ ] **T048** [P] [US5] Contract test for `get_index_components()` in `tests/test_tdx_contract.py` - verify method signature, return type List[str]
- [ ] **T049** [P] [US5] Unit test for `get_index_components()` in `tests/test_tdx_adapter.py` - mock `get_block_info()`, verify sector constituent extraction
- [ ] **T050** [P] [US5] Unit test for `get_sector_list()` extension method in `tests/test_tdx_adapter.py` - mock block data file reading, verify sector name/code parsing
- [ ] **T051** [P] [US5] Integration test for sector info in `tests/test_tdx_integration.py` - query actual sector constituents, validate stock code format

### Implementation for User Story 5

- [ ] **T052** [P] [US5] Implement `get_index_components(symbol: str) -> List[str]` in `adapters/tdx_adapter.py`:
  - Call `api.get_block_info()` to get sector data (may require specific file/parameter for pytdx)
  - Filter by `symbol` parameter (sector name or code)
  - Extract stock codes from constituent list
  - Return List[str] of 6-digit stock codes
  - Log warning if sector not found or pytdx doesn't support true index constituents (e.g., 沪深300)
  - Return empty list on error
- [ ] **T053** [P] [US5] Implement extension method `get_sector_list() -> pd.DataFrame` in `adapters/tdx_adapter.py`:
  - Call pytdx methods to list available sectors/blocks
  - Return DataFrame with columns: ['sector_code', 'sector_name', 'sector_type']
  - sector_type: 'INDUSTRY' or 'CONCEPT'
- [ ] **T054** [US5] Add logging for sector info operations - INFO with sector name, constituent count; WARNING if data unavailable
- [ ] **T055** [US5] Add documentation for `get_index_components()` explaining difference between sector constituents (supported) vs index constituents like HS300 (may not be supported)

**Checkpoint**: All user stories (1-5) should now be independently functional. Test: Query all board sectors, extract constituents, verify comprehensive sector coverage for market analysis.

---

## Phase 8: Stub Implementations (Required for IDataSource Compliance)

**Purpose**: Implement stub methods for IDataSource interface methods not supported by pytdx

- [ ] **T056** [P] [STUB] Implement `get_market_calendar(start_date: str, end_date: str) -> pd.DataFrame` stub in `adapters/tdx_adapter.py`:
  - Log warning: "get_market_calendar not supported by TDX adapter - use akshare or other data source"
  - Return empty DataFrame: `pd.DataFrame()`
- [ ] **T057** [P] [STUB] Implement `get_news_data(symbol: str, limit: int = 20) -> List[Dict]` stub in `adapters/tdx_adapter.py`:
  - Log warning: "get_news_data not supported by TDX adapter - use akshare or other data source"
  - Return empty list: `[]`
- [ ] **T058** [STUB] Add unit tests for stub methods in `tests/test_tdx_adapter.py` - verify they return empty results without raising exceptions

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] **T059** [P] Add comprehensive docstrings to all methods in `adapters/tdx_adapter.py` following Google/NumPy style
- [ ] **T060** [P] Add type hints to all method parameters and return types in `adapters/tdx_adapter.py`
- [ ] **T061** [P] Run mypy type checking: `mypy adapters/tdx_adapter.py` - fix all type errors
- [ ] **T062** [P] Run pylint: `pylint adapters/tdx_adapter.py` - address code quality issues (aim for 9.0+ score)
- [ ] **T063** [P] Add `adapters/tdx_adapter.py` to `adapters/__init__.py` exports: `from .tdx_adapter import TdxDataSource`
- [ ] **T064** Create example usage script `examples/tdx_example.py` demonstrating all user stories (real-time quote, daily K-line, minute data, financial data, sector info)
- [ ] **T065** [P] Update `README.md` (if exists) with TDX adapter section explaining features, installation, basic usage
- [ ] **T066** [P] Create performance benchmark script `benchmarks/tdx_benchmark.py` comparing TDX vs akshare speed for real-time quotes and daily K-lines
- [ ] **T067** Run full test suite: `pytest tests/test_tdx_*.py -v` - ensure 100% pass rate
- [ ] **T068** [P] Add error message constants file `adapters/tdx_errors.py` for standardized error messages (e.g., "TDX_CONNECTION_FAILED", "INVALID_SYMBOL_FORMAT")
- [ ] **T069** Implement optional connection pool support using `TdxHqPool_API` from `temp/pytdx/hq.py` (enhancement beyond MVP)
- [ ] **T070** [P] Add batch real-time quote extension method `get_real_time_data_batch(symbols: List[str]) -> pd.DataFrame` for optimal multi-stock queries
- [ ] **T071** Run quickstart.md validation - manually execute all code examples in `specs/004-tdx-pytdx-mystocks/quickstart.md`, verify they work
- [ ] **T072** [P] Add monitoring integration - log all adapter operations to MonitoringDatabase via MyStocksUnifiedManager hooks (if not automatic)
- [ ] **T073** Create data validation script `scripts/validate_tdx_data.py` to check data quality (no nulls, positive prices, OHLC logic) after bulk fetches
- [ ] **T074** Security review - verify no hardcoded credentials, all config from .env, sensitive data properly handled
- [ ] **T075** Performance optimization - profile adapter methods, optimize slow operations (e.g., pagination loops, data transformations)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (real-time quotes): Independent, can start after Phase 2
  - User Story 2 (historical K-lines): Independent, can start after Phase 2
  - User Story 3 (minute/tick data): Independent, can start after Phase 2
  - User Story 4 (financial/dividend): Independent, can start after Phase 2
  - User Story 5 (sector info): Independent, can start after Phase 2
- **Stub Implementations (Phase 8)**: Can run in parallel with user stories or after
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

**Critical Finding**: All 5 user stories are **completely independent** after Foundational phase completes. No user story depends on another.

- **User Story 1 (P1)**: Real-time quotes - Can start after Foundational (Phase 2) - No dependencies
- **User Story 2 (P1)**: Historical K-lines - Can start after Foundational (Phase 2) - No dependencies
- **User Story 3 (P2)**: Minute/tick data - Can start after Foundational (Phase 2) - No dependencies
- **User Story 4 (P3)**: Financial/dividend - Can start after Foundational (Phase 2) - No dependencies
- **User Story 5 (P3)**: Sector info - Can start after Foundational (Phase 2) - No dependencies

**Implication**: With 5 developers, all user stories can be implemented in parallel after Phase 2 completion.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD order)
- All tests within a story marked [P] can run in parallel
- Implementation tasks may have internal dependencies (models → services → endpoints)
- Story is complete when all its tasks are done and tests pass

### Parallel Opportunities

- **Phase 1 (Setup)**: All 3 tasks can run in parallel
- **Phase 2 (Foundational)**: T004-T011 are mostly sequential (building on each other)
- **Phase 3-7 (User Stories)**: **All 5 phases can run 100% in parallel** once Phase 2 completes
- **Within Each User Story**: All test tasks marked [P] can run in parallel, some implementation tasks marked [P] can run in parallel
- **Phase 8 (Stubs)**: Both stub tasks can run in parallel
- **Phase 9 (Polish)**: All tasks marked [P] can run in parallel

---

## Parallel Example: All User Stories

```bash
# After Phase 2 (Foundational) completes, launch all user stories in parallel:

# Developer A: User Story 1 (Real-time quotes)
Task: "T012 - T018"

# Developer B: User Story 2 (Historical K-lines)
Task: "T019 - T028"

# Developer C: User Story 3 (Minute/tick data)
Task: "T029 - T037"

# Developer D: User Story 4 (Financial/dividend)
Task: "T038 - T047"

# Developer E: User Story 5 (Sector info)
Task: "T048 - T055"

# All stories complete independently and integrate seamlessly
```

---

## Parallel Example: User Story 1 (Real-time Quotes)

```bash
# Launch all tests for User Story 1 together:
Task: "T012 Contract test for get_real_time_data() in tests/test_tdx_contract.py"
Task: "T013 Unit test for real-time quote success case in tests/test_tdx_adapter.py"
Task: "T014 Unit test for real-time quote error cases in tests/test_tdx_adapter.py"
Task: "T015 Integration test for real-time quote in tests/test_tdx_integration.py"

# Then implement (sequential):
Task: "T016 Implement get_real_time_data() method"
Task: "T017 Add logging"
Task: "T018 Add input validation"
```

---

## Parallel Example: User Story 2 (Historical K-lines)

```bash
# Launch all tests for User Story 2 together:
Task: "T019 Contract test for get_stock_daily() in tests/test_tdx_contract.py"
Task: "T020 Contract test for get_index_daily() in tests/test_tdx_contract.py"
Task: "T021 Unit test for get_stock_daily() success case in tests/test_tdx_adapter.py"
Task: "T022 Unit test for get_stock_daily() edge cases in tests/test_tdx_adapter.py"
Task: "T023 Unit test for get_index_daily() in tests/test_tdx_adapter.py"
Task: "T024 Integration test for historical K-line in tests/test_tdx_integration.py"

# Then implement (some parallel possible):
Task: "T025 Implement get_stock_daily() method" [P]
Task: "T026 Implement get_index_daily() method" [P]
Task: "T027 Add logging"
Task: "T028 Add progress logging"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

**Minimal Viable Product**: Real-time quotes + Historical K-lines

1. Complete Phase 1: Setup (T001-T003) - ~30 minutes
2. Complete Phase 2: Foundational (T004-T011) - **CRITICAL** - ~4-6 hours
3. Complete Phase 3: User Story 1 (T012-T018) - ~4 hours
4. Complete Phase 4: User Story 2 (T019-T028) - ~6 hours
5. **STOP and VALIDATE**: Test both stories independently
6. Add stub implementations (T056-T058) - ~30 minutes
7. Deploy/demo MVP

**Total MVP Effort**: ~15-17 hours (2 days)

**MVP Deliverable**: TdxDataSource adapter with 2 core methods (`get_real_time_data`, `get_stock_daily`, `get_index_daily`) fully functional, tested, and production-ready.

### Incremental Delivery

1. **Foundation** (Phase 1 + 2): Setup + Foundational infrastructure → Foundation ready (~6-7 hours)
2. **MVP** (Phase 3 + 4): User Stories 1 & 2 → Test independently → Deploy/Demo (~10 hours)
3. **Enhancement 1** (Phase 5): User Story 3 (minute/tick) → Test independently → Deploy/Demo (~6 hours)
4. **Enhancement 2** (Phase 6): User Story 4 (financial/dividend) → Test independently → Deploy/Demo (~6 hours)
5. **Enhancement 3** (Phase 7): User Story 5 (sector info) → Test independently → Deploy/Demo (~4 hours)
6. **Completeness** (Phase 8): Stub implementations → Full IDataSource compliance (~30 minutes)
7. **Polish** (Phase 9): Documentation, optimization, monitoring → Production-ready (~6-8 hours)

**Total Effort**: ~38-42 hours (5-6 days)

Each increment adds value without breaking previous stories. Can stop at any checkpoint and deploy what's complete.

### Parallel Team Strategy

**With 5 developers**, optimal parallel execution after Foundational phase:

1. **Week 1, Day 1-2**: Team completes Setup + Foundational together (Phases 1-2)
2. **Week 1, Day 3-5**: Once Foundational is done, split into 5 parallel tracks:
   - **Developer A**: User Story 1 (Real-time quotes) - T012-T018
   - **Developer B**: User Story 2 (Historical K-lines) - T019-T028
   - **Developer C**: User Story 3 (Minute/tick data) - T029-T037
   - **Developer D**: User Story 4 (Financial/dividend) - T038-T047
   - **Developer E**: User Story 5 (Sector info) - T048-T055
3. **Week 2, Day 1**: Integration testing - verify all stories work together
4. **Week 2, Day 2**: Stub implementations + Polish (all developers)
5. **Week 2, Day 3**: Final validation, documentation, deployment

**Total Calendar Time**: ~2 weeks (with team parallelization vs 6 weeks sequential)

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 8 tasks (T004-T011)
- **Phase 3 (US1 Real-time)**: 7 tasks (4 tests + 3 implementation)
- **Phase 4 (US2 Historical)**: 10 tasks (6 tests + 4 implementation)
- **Phase 5 (US3 Minute/Tick)**: 9 tasks (4 tests + 5 implementation)
- **Phase 6 (US4 Financial)**: 10 tasks (5 tests + 5 implementation)
- **Phase 7 (US5 Sector)**: 8 tasks (4 tests + 4 implementation)
- **Phase 8 (Stubs)**: 3 tasks
- **Phase 9 (Polish)**: 17 tasks

**Total**: 75 tasks

**Test Tasks**: 27 (36% of total - comprehensive test coverage)
**Implementation Tasks**: 31 (41% of total)
**Infrastructure/Polish Tasks**: 17 (23% of total)

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label (US1-US5) maps task to specific user story for traceability
- Each user story is **independently completable and testable**
- All 5 user stories are **100% independent** - no inter-story dependencies
- Tests written FIRST (TDD) - verify they fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP = User Stories 1 + 2 (real-time quotes + historical K-lines)
- Stub implementations (T056-T058) required for full IDataSource interface compliance
- Extensions (minute data, tick data, batch queries, dividend info, sector list) are TDX-specific enhancements beyond IDataSource contract

---

**Generated**: 2025-10-15
**Based On**: spec.md (5 user stories), plan.md, data-model.md, contracts/IDataSource_contract.md
**Ready for**: Implementation via parallel execution or incremental delivery
