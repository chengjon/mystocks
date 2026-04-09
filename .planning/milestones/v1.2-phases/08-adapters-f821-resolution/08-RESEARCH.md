---
phase: 08-adapters-f821-resolution
type: research
created: "2026-04-10"
status: complete
---

# Phase 8 Research: Adapters F821 Resolution

**Goal:** Resolve all 468 F821 errors in src/adapters/ (15 files) by adding missing imports.

## Error Summary

| Symbol | Count | Files | Correct Import |
|--------|-------|-------|----------------|
| `logger` | 237 | 15 (all) | `import logging` + `logger = logging.getLogger(__name__)` |
| `pd` | 165 | 15 (all) | `import pandas as pd` |
| `ak` | 25 | 8 | `import akshare as ak` |
| `symbol_utils` | 8 | 7 | `from src.utils import symbol_utils` |
| `normalize_date` | 11 | 3 | `from src.utils.date_utils import normalize_date` |
| `date_utils` | 7 | 2 | `from src.utils import date_utils` |
| `Dict` | 4 | 4 | `from typing import Dict` |
| `Any` | 2 | 2 | `from typing import Any` |
| `ColumnMapper` | 2 | 2 | `from src.utils.column_mapper import ColumnMapper` |
| `format_stock_code_for_source` | 2 | 2 | `from src.utils.symbol_utils import format_stock_code_for_source` |
| `format_index_code_for_source` | 1 | 1 | `from src.utils.symbol_utils import format_index_code_for_source` |
| `datetime` | 2 | 2 | `from datetime import datetime` |
| `List` | 1 | 1 | `from typing import List` |
| `traceback` | 1 | 1 | `import traceback` |

## Per-File Breakdown

### Akshare Adapters (7 files, 236 errors)

| File | Errors | Missing Symbols |
|------|--------|----------------|
| `akshare/index_daily.py` | 32 | ak(3), pd(9), logger(13), normalize_date(6), format_index_code_for_source(1) |
| `akshare/industry_data.py` | 18 | ak(2), pd(8), logger(8) |
| `akshare/misc_data/get_futures_index_daily.py` | 54 | ak(4), pd(26), logger(24) |
| `akshare/misc_data/get_ths_industry_names.py` | 81 | ak(9), pd(36), logger(36) |
| `akshare/realtime_data.py` | 17 | ak(2), pd(6), logger(5), normalize_date(2), Any(1), Dict(1) |
| `akshare/stock_basic.py` | 14 | ak(2), pd(2), logger(5), ColumnMapper(1), format_stock_code_for_source(1), Any(1), Dict(1), List(1) |
| `akshare/stock_daily.py` | 20 | ak(2), pd(4), logger(8), normalize_date(3), ColumnMapper(1), format_stock_code_for_source(1), datetime(1) |

### Financial Adapters (8 files, 232 errors)

| File | Errors | Missing Symbols |
|------|--------|----------------|
| `financial/financial_data.py` | 30 | logger(20), pd(9), symbol_utils(1) |
| `financial/index_components.py` | 16 | logger(10), pd(5), symbol_utils(1) |
| `financial/index_daily.py` | 33 | logger(15), pd(12), ak(1), date_utils(2), symbol_utils(1), Dict(1), traceback(1) |
| `financial/market_calendar.py` | 17 | logger(11), pd(6) |
| `financial/news_data.py` | 16 | logger(9), pd(6), symbol_utils(1) |
| `financial/realtime_data.py` | 45 | logger(26), pd(17), symbol_utils(2) |
| `financial/stock_basic.py` | 25 | logger(20), pd(3), symbol_utils(1), Dict(1) |
| `financial/stock_daily.py` | 50 | logger(27), pd(16), date_utils(5), datetime(1), symbol_utils(1) |

## Import Source Verification

All import sources verified to exist in the codebase:

- `pandas` — third-party (in requirements)
- `logging` — stdlib
- `akshare` — third-party (in requirements)
- `src.utils.date_utils.normalize_date` — `src/utils/date_utils.py:10`
- `src.utils.symbol_utils.format_stock_code_for_source` — `src/utils/symbol_utils.py:114`
- `src.utils.symbol_utils.format_index_code_for_source` — `src/utils/symbol_utils.py:198`
- `src.utils.column_mapper.ColumnMapper` — `src/utils/column_mapper.py`
- `src.utils.date_utils` (module) — `src/utils/date_utils.py`
- `src.utils.symbol_utils` (module) — `src/utils/symbol_utils.py`
- `typing.Dict`, `typing.Any`, `typing.List` — stdlib
- `datetime.datetime` — stdlib
- `traceback` — stdlib

## Pattern from Existing Files

Reference files with correct imports already present:
- `src/adapters/akshare/base.py` — has `import pandas as pd`, lazy imports for symbol_utils/date_utils
- `src/adapters/akshare/modules/base.py` — has `import logging`, `logger = logging.getLogger(__name__)`, `import pandas as pd`
- `src/adapters/akshare_adapter.py` — has `from src.utils.date_utils import normalize_date`, `from src.utils.symbol_utils import ...`
- `src/adapters/financial_adapter.py` — has `from src.utils import date_utils, symbol_utils`

**Import order convention (from CLAUDE.md):** stdlib → third-party → local (`from src.*`)

## Risk Assessment

- **Circular imports:** None detected — all imports are from `src.utils.*` (utility layer) into `src.adapters.*` (adapter layer). No circular dependency.
- **Logic changes:** None required — only adding import statements at module top.
- **akshare in financial/:** `financial/index_daily.py` uses `ak` (akshare) — verified that akshare is a project dependency, this is intentional.
- **ColumnMapper in akshare/:** Two files need `ColumnMapper` — the canonical import is `from src.utils.column_mapper import ColumnMapper` (consistent with tdx_adapter and baostock_adapter).

## Recommended Plan Structure

**2 plans, 2 waves:**

1. **Wave 1 (Plan 08-01):** Akshare adapters — 7 files, 236 errors
   - Common pattern: all need `pd`, `logger`, most need `ak`
   - 3 files additionally need `normalize_date`, 2 need `ColumnMapper`/`format_stock_code_for_source`

2. **Wave 1 (Plan 08-02):** Financial adapters — 8 files, 232 errors
   - Common pattern: all need `pd`, `logger`, most need `symbol_utils`
   - 2 files additionally need `date_utils`, 1 needs `ak`, `traceback`

Both plans are independent and can run in parallel (Wave 1).

---

*Research completed: 2026-04-10*
