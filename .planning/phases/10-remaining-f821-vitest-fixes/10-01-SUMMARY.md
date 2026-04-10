---
phase: 10
plan: 01
status: complete
completed: "2026-04-10"
---

# Plan 01: Python F821 Clearance — Complete

## Result

All 11 F821 undefined-name errors resolved. `ruff check src/ --select F821` exits 0 with no output.

## Changes

| File | Fix |
|------|-----|
| `src/alternative_data/_news_sentiment_service_helper.py` | Added `from src.alternative_data.news_sentiment_analyzer import NewsArticle` |
| `src/alternative_data/news_sentiment_analyzer.py` | Added conditional `import torch` with `TORCH_AVAILABLE` guard |
| `src/core/data_source/config_manager.py` | Added `import yaml` between stdlib and local imports |
| `src/database/service/adapter_queries.py` | Added `from src.database.service import DatabaseService` |
| `src/governance/risk_management/services/alert_rule_engine.py` | Removed f-string prefix from 2 template strings (not runtime vars) |
| `src/storage/database/database_manager/database_table_manager_methods/close_all_connections.py` | Added `from src.storage.database.database_manager import DatabaseType` |

## Verification

- `ruff check src/ --select F821` — zero output, exit 0
- No new lint errors introduced

## Self-Check: PASSED
