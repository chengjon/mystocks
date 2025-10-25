# US2 Database Architecture Clarification

**Date**: 2025-10-25
**Purpose**: Clarify actual vs documented data classification counts

---

## Critical Finding: Documentation-Code Mismatch

### Actual Code Reality (Verified 2025-10-25)

```bash
$ python3 -c "from core.data_classification import DataClassification; print(len(list(DataClassification)))"
34
```

```bash
$ python3 test_dual_database_architecture.py | grep "路由:"
TDengine路由: 5项
PostgreSQL路由: 29项
```

**Verified Distribution**:
- **Total Classifications**: 34 items (not 23)
- **TDengine**: 5 items (not 3)
  1. TICK_DATA
  2. MINUTE_KLINE
  3. ORDER_BOOK_DEPTH
  4. LEVEL2_SNAPSHOT
  5. INDEX_QUOTES
- **PostgreSQL**: 29 items (not 20)

**Category Breakdown** (Actual):
- 市场数据 (Market Data): 6 items
- 参考数据 (Reference Data): 9 items
- 衍生数据 (Derived Data): 6 items
- 交易数据 (Transaction Data): 7 items
- 元数据 (Meta Data): 6 items

---

## Documentation Error in US1

During US1 (Documentation Alignment), the docs were **incorrectly updated** to state:
- Total: 23 classifications ❌
- TDengine: 3 items ❌
- PostgreSQL: 20 items ❌

This was based on a misunderstanding. The **code was never simplified** from 34 to 23.

---

## Correct Current State (Post-US2)

### Database Architecture ✅
- **TDengine**: Handles high-frequency time-series data (5 classifications)
- **PostgreSQL**: Handles all other data (29 classifications)
- **MySQL**: Removed ✅
- **Redis**: Removed ✅

### Total: 2 databases (simplified from 4)

---

## Future Simplification Plan

### US4: Optimized Data Classification System
**Goal**: Reduce from 34 classifications to 8-10 practical categories

**Target Distribution** (Planned):
- HIGH_FREQUENCY → TDengine
- HISTORICAL_KLINE → PostgreSQL
- REALTIME_SNAPSHOT → PostgreSQL
- INDUSTRY_SECTOR → PostgreSQL
- CONCEPT_THEME → PostgreSQL
- FINANCIAL_FUNDAMENTAL → PostgreSQL
- CAPITAL_FLOW → PostgreSQL
- CHIP_DISTRIBUTION → PostgreSQL
- NEWS_ANNOUNCEMENT → PostgreSQL
- DERIVED_INDICATOR → PostgreSQL

This is a **future task** (T051-T068 in tasks.md).

---

## Action Items for Documentation Fix

1. ✅ **US2 Code Cleanup**: Remove MySQL/Redis references (in progress)
2. **Documentation Update**: Correct all docs to reflect 34 classifications, 5 TDengine items
3. **Preserve US1 Work**: Keep the architectural explanations, just fix the numbers
4. **Plan US4**: Data classification simplification is a separate story

---

## Files Requiring Correction

1. `/opt/claude/mystocks_spec/DATASOURCE_AND_DATABASE_ARCHITECTURE.md`
   - Change: 23 → 34 total classifications
   - Change: 3 → 5 TDengine items
   - Change: 20 → 29 PostgreSQL items
   - Change: Category breakdown to (6+9+6+7+6)

2. `/opt/claude/mystocks_spec/T037_COMPLETION_SUMMARY.md`
   - Same corrections as above

3. `/opt/claude/mystocks_spec/docs/US1_DOCUMENTATION_ALIGNMENT_COMPLETION.md`
   - Add clarification note about 34 vs 23

4. `/opt/claude/mystocks_spec/docs/HOW_TO_ADD_NEW_DATA_CLASSIFICATION.md`
   - Verify counts are correct

5. `/opt/claude/mystocks_spec/docs/DOCUMENTATION_VALIDATION_REPORT.md`
   - Update validation criteria

---

## Verification Commands

```bash
# Count total classifications
python3 -c "from core.data_classification import DataClassification; print(f'Total: {len(list(DataClassification))}')"

# Run architecture test
python3 test_dual_database_architecture.py

# Verify routing
python3 core/data_storage_strategy.py
```

---

## Conclusion

✅ **US2 Goal**: Remove MySQL and Redis → **Achieved** (code-level)
⚠️ **Documentation**: Needs correction to reflect actual 34 classifications
📋 **US4 Future**: Simplify from 34 to 8-10 classifications (planned)

**Next Steps**: Complete US2 by fixing documentation and adding web monitoring.
