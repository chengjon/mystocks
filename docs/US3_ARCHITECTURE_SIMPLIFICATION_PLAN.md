# US3: Architecture Layers Simplification - Implementation Plan

**Date**: 2025-10-25
**Branch**: 002-arch-optimization
**Priority**: P1
**Status**: Planning Phase

---

## Executive Summary

**Goal**: Simplify from 7-layer architecture to 3-layer architecture
**Expected Benefits**:
- Code reduction: 11,000 lines → ≤4,000 lines (64% reduction)
- Performance: 120ms → ≤80ms per 1000 records (33% improvement)
- Routing decision: <5ms
- Improved maintainability and developer understanding

---

## Current Architecture Analysis (7 Layers)

### Layer 1: External Data Sources
- Akshare, Baostock, Financial adapters
- **Purpose**: Fetch data from external APIs
- **Status**: Keep (required)

### Layer 2: Adapter Interface Layer
- `IDataSource` interface
- **Purpose**: Abstract external data sources
- **Status**: Keep (required)

### Layer 3: Factory Pattern Layer
- `factory/data_source_factory.py`
- **Purpose**: Create adapter instances
- **Issue**: Unnecessary abstraction for 2-3 adapters
- **Action**: ❌ DELETE

### Layer 4: Unified Manager Layer
- `unified_manager.py` (MyStocksUnifiedManager)
- **Purpose**: Orchestrate data operations
- **Issue**: Too complex, mixing concerns
- **Action**: ⚠️ SIMPLIFY → Thin wrapper

### Layer 5: Storage Strategy Layer
- `core/data_storage_strategy.py` (DataStorageStrategy)
- **Purpose**: Route data to databases
- **Issue**: Separate layer for simple routing
- **Action**: ⚠️ MERGE into DataManager

### Layer 6: Data Access Layer
- `data_access/tdengine_access.py`
- `data_access/postgresql_access.py`
- **Purpose**: Database-specific operations
- **Status**: ✅ Keep (required)

### Layer 7: Monitoring Infrastructure
- `monitoring/alert_manager.py` (complex)
- `monitoring/data_quality_monitor.py` (complex)
- `monitoring/performance_monitor.py` (complex)
- **Purpose**: System monitoring
- **Issue**: Over-engineered for current needs
- **Action**: ⚠️ SIMPLIFY → Keep only core monitoring

---

## Target Architecture (3 Layers)

### Layer 1: Adapter Layer
**Components**:
- External data source adapters (Akshare, etc.)
- `IDataSource` interface

**Responsibilities**:
- Fetch data from external sources
- Transform to standard format

**Files to Keep**:
- `adapters/akshare_adapter.py`
- `adapters/baostock_adapter.py`
- `adapters/financial_adapter.py`
- `interfaces/data_source.py`

### Layer 2: Data Management Layer (NEW)
**Components**:
- `DataManager` class (new, in `core.py`)
- Data classification and routing logic
- Adapter registration

**Responsibilities**:
- Register/manage adapters
- Route data to correct database (<5ms)
- Data validation
- Orchestrate operations

**Key Methods**:
```python
class DataManager:
    def __init__(self):
        self._adapters = {}
        self._tdengine = TDengineDataAccess()
        self._postgresql = PostgreSQLDataAccess()
        self._routing = {...}  # Classification → Database mapping

    def register_adapter(self, name, adapter)
    def get_target_database(self, classification) → DatabaseTarget
    def save_data(self, classification, data, table_name)
    def load_data(self, classification, table_name, **filters)
```

### Layer 3: Database Layer
**Components**:
- `TDengineDataAccess`
- `PostgreSQLDataAccess`
- Core monitoring database

**Responsibilities**:
- Execute database operations
- Connection management
- Query execution

**Files to Keep**:
- `data_access/tdengine_access.py`
- `data_access/postgresql_access.py`
- `monitoring/monitoring_database.py` (simplified)

---

## Implementation Tasks (T037-T050)

### Phase 1: Core Refactoring (T037-T042)

**T037**: Create DataManager class
- New class in `core.py`
- Combines routing, validation, orchestration
- Estimated: 300-400 lines

**T038**: Implement adapter registration
- `register_adapter()`, `unregister_adapter()`, `list_adapters()`
- Estimated: 50 lines

**T039**: Implement data routing
- `get_target_database(classification)`
- Merge routing logic from DataStorageStrategy
- Target: <5ms decision time
- Estimated: 100 lines

**T040**: Delete Factory Pattern
- Remove `factory/data_source_factory.py`
- Update imports in all files

**T041**: Delete DataStorageStrategy
- Remove from `core/data_storage_strategy.py`
- Merge routing into DataManager

**T042**: Simplify MyStocksUnifiedManager
- Convert to thin initialization wrapper
- Delegate all operations to DataManager
- Reduce from ~600 lines to ~100 lines

### Phase 2: Monitoring Simplification (T043)

**T043**: Simplify monitoring infrastructure
- Delete `monitoring/alert_manager.py` (complex abstractions)
- Delete `monitoring/data_quality_monitor.py` (complex abstractions)
- Keep `monitoring/monitoring_database.py` (core functionality)
- Keep `monitoring/performance_monitor.py` (if simple)

**Files to Delete**:
- `monitoring/alert_manager.py`
- `monitoring/data_quality_monitor.py`

**Files to Keep**:
- `monitoring/monitoring_database.py`

### Phase 3: Migration & Testing (T044-T046)

**T044**: Update all imports
- Global search/replace for old class references
- Update test files
- Update adapters

**T045**: Code metrics validation
- Run `cloc` on core files
- Verify ≤4,000 lines (vs 11,000 baseline)

**T046**: Performance benchmarking
- Create `tests/performance/test_new_architecture_latency.py`
- Test 1000 records save/load
- Verify ≤80ms (vs 120ms baseline)
- Verify routing <5ms

### Phase 4: Web Integration (T047-T050)

**T047**: Performance Monitor page
- Create `web/frontend/src/views/system/PerformanceMonitor.vue`
- Display routing latency, save/load performance

**T048**: Performance metrics API
- `GET /api/system/performance/metrics`
- Return query latency, throughput metrics

**T049**: Architecture layers API
- `GET /api/system/architecture/layers`
- Return 3-layer structure visualization data

**T050**: Add menu
- Add "性能监控" to system management menu

---

## Code Reduction Estimate

### Files to Delete
- `factory/data_source_factory.py` (~200 lines)
- `monitoring/alert_manager.py` (~400 lines)
- `monitoring/data_quality_monitor.py` (~500 lines)
- `core/data_storage_strategy.py` (partial, ~200 lines routing logic)

**Total deletion**: ~1,300 lines

### Files to Simplify
- `unified_manager.py`: 600 → 100 lines (-500 lines)
- Various imports and references: ~200 lines

**Total simplification**: ~700 lines

### Files to Add
- DataManager in `core.py`: +400 lines
- Performance tests: +200 lines

**Total addition**: +600 lines

**Net reduction**: 1,300 + 700 - 600 = **1,400 lines**

**Note**: This may not reach the 64% reduction target without further optimization

---

## Performance Improvement Strategy

### Routing Optimization
- Pre-compute classification→database mapping
- Use dict lookup instead of function calls
- Target: <5ms per routing decision

### Save/Load Optimization
- Batch operations
- Remove unnecessary validation layers
- Direct database access
- Target: ≤80ms per 1000 records

---

## Risks & Mitigation

### Risk 1: Breaking Changes
**Mitigation**:
- Keep MyStocksUnifiedManager as compatibility wrapper
- Gradual migration
- Comprehensive testing

### Risk 2: Performance Regression
**Mitigation**:
- Benchmark before/after
- Load testing
- Rollback plan

### Risk 3: Loss of Monitoring Features
**Mitigation**:
- Preserve core monitoring
- Document removed features
- Plan for future enhancement if needed

---

## Rollback Plan

If issues arise:
1. Revert git commits
2. Restore from archive/
3. Keep both implementations temporarily

---

## Success Criteria

✅ **Code Reduction**: Core files ≤4,000 lines
✅ **Performance**: 1000 records ≤80ms
✅ **Routing**: Decision <5ms
✅ **Tests Pass**: All existing tests pass
✅ **Web Interface**: Performance monitoring dashboard works
✅ **Compatibility**: Existing code continues to work

---

## Timeline Estimate

- Phase 1 (T037-T042): 2-3 hours
- Phase 2 (T043): 30 minutes
- Phase 3 (T044-T046): 1-2 hours
- Phase 4 (T047-T050): 1-2 hours

**Total**: 5-8 hours of development work

---

## Decision Point

⚠️ **This is a significant refactoring task**

**Recommendation**:
- US3 is a major architectural change
- Requires careful implementation and testing
- Should be done in a dedicated session with full attention

**Options**:
1. **Proceed now**: Continue with T037-T050 implementation
2. **Defer**: Complete smaller tasks first, tackle US3 in next session
3. **Partial**: Implement Phase 1-2 now, defer Web integration

**User decision required**: How would you like to proceed?

---

**Status**: Awaiting user decision on implementation approach
