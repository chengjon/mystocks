# Next Development Phases - API Contract Platform

**Status**: CLI_3 Complete ✅
**Date**: 2025-12-30
**Current TypeScript Errors**: 262
**Project State**: Frontend Market Data Integration Complete, Trade Module Repaired

---

## 📊 Current Achievements Summary

### ✅ Completed (Phase 1-3)

**Phase 1: Frontend Integration (P1)**
- ✅ MarketApiService refactored with auto-generated types
- ✅ MarketAdapter updated for split API structure
- ✅ useMarket composable enhanced with parallel fetching
- ✅ Dashboard migrated to new data flow

**Phase 2: Backend Repair (P2)**
- ✅ APIResponse/UnifiedResponse converted to Generic[T]
- ✅ Trade module re-enabled and functional
- ✅ api-contract-sync CLI enhanced with robust helpers

**Phase 3: Contract Expansion (P2)**
- ✅ OpenAPI specs generated for trading, technical-analysis, strategy-management
- ✅ 3 new contracts registered and activated
- ✅ Platform now supports 4 API contracts (market-data, trading, technical-analysis, strategy-management)

**Code Quality (Previous Session)**
- ✅ 682 code issues fixed (100% major problems)
- ✅ All P0 syntax errors resolved
- ✅ All P1 major issues resolved
- ✅ Project quality elevated to "Excellent" standard

---

## 🎯 Next Development Roadmap

### Phase 4: Frontend Type Hygiene (P1) - 2-3 Weeks

**Objective**: Reduce 262 TypeScript errors to <50, enable strict type checking

#### 4.1 Generated Types Cleanup (Week 1)

**Problem**: Missing exports and type mismatches in generated-types.ts

**Tasks**:
1. **Fix Missing Exports** (1-2 days)
   - Add `UserProfileResponse`, `WatchlistResponse`, `NotificationResponse`
   - Export `IndicatorResult`, `IndicatorParameter` consistently
   - Ensure all OpenAPI schema types are properly exported

2. **Standardize Type Names** (1 day)
   ```typescript
   // Current inconsistencies
   NotificationTestResponse vs NotificationResponse
   IndicatorParams vs IndicatorParameter
   EChartOption vs EChartsOption

   // Target: Single canonical name per type
   export type NotificationResponse = ...  // Use this everywhere
   export type IndicatorParameter = ...    // Use this everywhere
   export type EChartsOption = ...         // Use echarts types
   ```

3. **Update Import References** (1 day)
   - Fix all `@/api/types/generated-types` imports
   - Update 15+ files with wrong type references

**Success Criteria**:
- ✅ All type export errors resolved (fixes ~10 errors)
- ✅ Import errors reduced by 90%

#### 4.2 ECharts Type Standardization (Week 1, Days 3-5)

**Problem**: `EChartOption` vs `EChartsOption` inconsistency

**Tasks**:
1. **Unified ECharts Types** (1 day)
   ```typescript
   // src/types/charts.ts
   import type { EChartsOption } from 'echarts'

   // Export canonical type
   export type ChartOption = EChartsOption

   // Use in all components
   // ❌ const option: EChartOption = ...
   // ✅ const option: ChartOption = ...
   ```

2. **Update Chart Components** (2 days)
   - Fix `RiskMonitor.vue` (5 chart instances)
   - Fix `StockDetail.vue` K-line charts
   - Fix `TechnicalAnalysis.vue` indicator charts
   - Fix `Dashboard.vue` overview charts

**Success Criteria**:
- ✅ All ECharts type errors resolved (fixes ~20 errors)
- ✅ Consistent chart type usage across codebase

#### 4.3 Element Plus Type Compatibility (Week 2, Days 1-2)

**Problem**: `TagType` incompatible with Element Plus `EpPropMergeType`

**Tasks**:
1. **Type Guard Functions** (1 day)
   ```typescript
   // src/utils/type-guards.ts
   import type { TagType } from '@/types/common'
   import type { EpPropMergeType } from 'element-plus'

   export function toElementTagType(tag: TagType): 'primary' | 'success' | 'warning' | 'info' | 'danger' {
     const mapping = {
       'bull': 'success',
       'bear': 'danger',
       'neutral': 'info',
       'warning': 'warning',
       'primary': 'primary'
     }
     return mapping[tag] || 'info'
   }
   ```

2. **Update All Tag Usage** (1 day)
   - Fix `IndicatorLibrary.vue` (2 instances)
   - Fix `RiskMonitor.vue` (3 instances)

**Success Criteria**:
- ✅ All TagType errors resolved (fixes ~5 errors)

#### 4.4 Contract Type Alignment (Week 2, Days 3-5)

**Problem**: Generated contract types don't match frontend type expectations

**Tasks**:
1. **Audit Type Mismatches** (1 day)
   ```typescript
   // Example mismatches found:
   - StrategyDefinition missing: strategy_code, strategy_name_cn
   - BacktestResult missing: initial_capital, final_capital, total_trades, profit_factor
   - IndicatorMetadata missing: categories, outputs, reference_lines, min_data_points_formula
   - PanelType enum mismatch: string vs "overlay" | "separate"
   ```

2. **Update OpenAPI Specifications** (2 days)
   - Add missing fields to contract YAMLs
   - Regenerate types with complete schemas
   - Ensure field names match frontend expectations

3. **Create Type Adapter Layer** (2 days)
   ```typescript
   // src/api/adapters/contract-adapter.ts
   export function adaptStrategyDefinition(
     contract: StrategyDefinitionContract
   ): StrategyDefinition {
     return {
       ...contract,
       // Add missing fields with defaults
       strategy_code: contract.code || '',
       strategy_name_cn: contract.nameZh || contract.name,
       // ... map other fields
     }
   }
   ```

**Success Criteria**:
- ✅ All contract type errors resolved (fixes ~50 errors)
- ✅ Frontend types aligned with backend contracts

#### 4.5 Type Inference & Strict Mode (Week 3)

**Problem**: `unknown` types, string/number comparisons, missing type guards

**Tasks**:
1. **Fix Unknown Types** (1 day)
   - Add proper type annotations to trade-adapters.ts
   - Fix `map`/`length` errors on unknown arrays

2. **Type Guards for Comparisons** (1 day)
   ```typescript
   // src/utils/type-guards.ts
   export function isNumeric(value: string | number): value is number {
     return typeof value === 'number'
   }

   // Usage
   if (isNumeric(price) && price >= 100) { ... }
   ```

3. **Enable Strict Type Checking** (1 day)
   - Update tsconfig.json with strict mode flags
   - Fix remaining ~100 type errors
   - Document acceptable type any usage

**Success Criteria**:
- ✅ TypeScript errors reduced from 262 to <50
- ✅ Strict type checking enabled
- ✅ Type coverage >90%

---

### Phase 5: Contract Testing & Consistency (P1) - 1-2 Weeks

**Objective**: Automated verification that backend implementation matches OpenAPI contracts

#### 5.1 Contract Testing Framework (Week 1)

**Tasks**:
1. **Choose Testing Tool** (1 day)
   - Option A: Schemathesis (property-based testing)
   - Option B: Custom pytest middleware (lightweight)
   - **Recommendation**: Start with custom pytest

2. **Implement Contract Validator** (2-3 days)
   ```python
   # tests/contract_test_utils.py
   from pydantic import ValidationError
   from openapi_spec_validator import validate_spec

   def validate_response_against_contract(
       contract_path: str,
       endpoint: str,
       response_data: dict,
       status_code: int
   ):
       """Validate response matches OpenAPI schema"""
       spec = load_openapi_spec(contract_path)
       schema = spec['paths'][endpoint]['get']['responses'][status_code]

       try:
           validate_schema(schema, response_data)
           return True, "OK"
       except ValidationError as e:
           return False, str(e)
   ```

3. **Integration Tests for 4 Contracts** (2 days)
   - market-data: 6 endpoints
   - trading: 8 endpoints
   - technical-analysis: 10 endpoints
   - strategy-management: 5 endpoints

**Success Criteria**:
- ✅ Contract test suite covering all 4 APIs
- ✅ CI/CD integration for automated testing

#### 5.2 Real Sync Logic Implementation (Week 2)

**Problem**: VersionManager.sync() is currently a mock

**Tasks**:
1. **Database-to-Spec Generation** (2 days)
   ```python
   # api-contract-sync/db_to_spec.py
   def generate_openapi_from_db_models(router_module) -> OpenAPISpec:
       """
       Inspect FastAPI router models, generate OpenAPI schema
       """
       routes = inspect_router(router_module)
       operations = []

       for route in routes:
         operation = {
           'summary': route.summary,
           'parameters': extract_pydanitc_models(route.params),
           'responses': extract_response_models(route.responses)
         }
         operations.append(operation)

       return OpenAPISpec(operations=operations)
   ```

2. **Spec-to-Database Migration** (2 days)
   ```python
   # api-contract-sync/spec_to_db.py
   def sync_spec_to_database(spec_path: str):
       """
       Update database schema based on OpenAPI spec changes
       """
       spec = load_openapi_spec(spec_path)

       for path, methods in spec['paths'].items():
         for method, operation in methods.items():
           ensure_schema_exists(operation['requestBody'])
           ensure_schema_exists(operation['responses'])
   ```

3. **Bidirectional Sync CLI** (1 day)
   ```bash
   api-contract-sync sync --direction db-to-spec  # Generate spec from DB
   api-contract-sync sync --direction spec-to-db  # Update DB from spec
   api-contract-sync sync --direction bidirectional # Merge both
   ```

**Success Criteria**:
- ✅ Real sync logic implemented
- ✅ Database and spec stay in sync automatically

---

### Phase 6: Developer Experience Automation (P2) - 1 Week

**Objective**: Integrate contract sync into daily development workflow

#### 6.1 Pre-commit Hooks (Days 1-2)

**Tasks**:
1. **Create Contract Sync Hook** (1 day)
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: local
       hooks:
         - id: sync-api-contracts
           name: Sync API Contracts
           entry: bash scripts/dev/sync_contracts.sh
           language: system
           pass_filenames: false
           always_run: true
   ```

2. **Create Sync Script** (1 day)
   ```bash
   #!/bin/bash
   # scripts/dev/sync_contracts.sh

   echo "🔄 Syncing API contracts..."

   # 1. Check for contract changes
   if git diff --name-only HEAD~1 | grep -q "api/contracts/"; then
     echo "📝 Contracts changed, regenerating types..."
     python scripts/dev/generate_frontend_types.py
   fi

   # 2. Validate contracts
   api-contract-sync validate --all

   # 3. Run type checks
   cd web/frontend && npm run type-check
   ```

**Success Criteria**:
- ✅ Contracts auto-sync on commit
- ✅ Type generation fully automated

#### 6.2 Boilerplate Code Generation (Days 3-5)

**Tasks**:
1. **Scaffold Command Design** (1 day)
   ```bash
   api-contract-sync scaffold \
     --contract market-data \
     --endpoint GET /overview \
     --template vue-service \
     --output src/services/api/marketService.ts
   ```

2. **Jinja2 Templates** (2 days)
   ```
   templates/
   ├── vue-service.j2        # Axios-based service class
   ├── vue-composable.j2     # Reactivity composable
   └── vue-adapter.j2        # Data transformation adapter
   ```

3. **Generator Implementation** (2 days)
   ```python
   # api-contract-sync/generate.py
   def generate_service_layer(contract_id: str, template_type: str):
       contract = load_contract(contract_id)
       endpoints = contract.get_endpoints()

       for endpoint in endpoints:
         service_code = render_template('vue-service.j2', {
           'endpoint': endpoint,
           'types': endpoint.types,
           'method': endpoint.method
         })

         write_file(output_path, service_code)
   ```

**Success Criteria**:
- ✅ One command generates service + adapter + composable
- ✅ Reduces boilerplate by 80%

---

### Phase 7: Full API Registry (P2) - 4-6 Weeks

**Objective**: Register all 200+ backend APIs in contract platform

#### 7.1 API Inventory & Prioritization (Week 1)

**Tasks**:
1. **Backend Router Audit** (2 days)
   ```bash
   # List all routers
   find web/backend/app/api -name '*.py' | grep -E "(router|routes)"

   # Categorize by domain
   - announcement (公告)
   - indicators (技术指标)
   - market (市场数据)
   - data (数据管理)
   - backtest (回测)
   - trading (交易)
   - risk_management (风控)
   - ml (机器学习)
   - monitoring (监控)
   ```

2. **Prioritization Matrix** (2 days)
   - **P0** (Critical): trading, market, data - 30 APIs
   - **P1** (High): backtest, risk_management - 25 APIs
   - **P2** (Medium): indicators, announcement - 40 APIs
   - **P3** (Low): monitoring, ml - 20 APIs

3. **Create Registration Roadmap** (1 day)
   - Week 2-3: P0 APIs (30)
   - Week 4-5: P1 APIs (25)
   - Week 6-8: P2 APIs (40)
   - Week 9-10: P3 APIs (20)

**Success Criteria**:
- ✅ Complete API inventory documented
- ✅ Prioritized registration roadmap

#### 7.2 Batch Registration Pipeline (Week 2-8)

**Tasks**:
1. **Automated Spec Generation** (ongoing)
   ```python
   # scripts/dev/generate_openapi_from_router.py
   def generate_spec_from_router(router_module: str):
       """
       Automatically extract OpenAPI spec from FastAPI router
       """
       router = import_router(router_module)
       spec = router.openapi()

       # Clean up spec
       spec = normalize_spec(spec)

       # Save to contracts directory
       save_spec(f"api/contracts/{router_module}.yaml", spec)
   ```

2. **Validation & Registration** (ongoing)
   ```bash
   # Batch register P0 APIs
   for router in trading market data; do
     api-contract-sync register --from-router $router
     api-contract-sync activate $router
   done
   ```

3. **Type Regeneration** (ongoing)
   ```bash
   # Regenerate all frontend types after batch registration
   npm run generate-types
   ```

**Success Criteria**:
- ✅ 115 APIs (P0+P1+P2) registered by Week 8
- ✅ All types auto-generated

#### 7.3 Documentation & Maintenance (Week 9-10)

**Tasks**:
1. **API Registry Dashboard** (3 days)
   - List all registered contracts
   - Show coverage per domain
   - Track deprecations and versions

2. **Maintenance Workflows** (2 days)
   - Contract update guidelines
   - Deprecation process
   - Versioning strategy

**Success Criteria**:
- ✅ Complete API documentation
- ✅ Sustainable maintenance process

---

## 📅 Timeline Summary

| Phase | Duration | Priority | Dependencies |
|-------|----------|----------|--------------|
| **Phase 4**: Frontend Type Hygiene | 2-3 weeks | **P1** | CLI_3 complete |
| **Phase 5**: Contract Testing | 1-2 weeks | **P1** | Phase 4 complete |
| **Phase 6**: Dev Automation | 1 week | P2 | Phase 5 complete |
| **Phase 7**: Full API Registry | 4-6 weeks | P2 | Phase 6 complete |

**Total Timeline**: 8-12 weeks to complete all 4 phases

---

## 🎯 Quick Wins vs Long-term Investments

### Quick Wins (1-2 weeks each)
1. ✅ **Fix generated types exports** - Immediate ~10 error reduction
2. ✅ **Standardize ECharts types** - ~20 error reduction
3. ✅ **Element Plus type guards** - ~5 error reduction

### Strategic Investments (4-6 weeks each)
1. **Contract type alignment** - Prevents future drift
2. **Automated testing** - Quality assurance
3. **Full API registry** - Developer productivity

---

## 🚀 Recommended Starting Point

**Week 1-2**: Phase 4.1-4.2 (Generated Types + ECharts)

**Why**:
- ✅ Immediate visible impact (reduce 262 errors to ~150)
- ✅ Unblock developers working with charts and indicators
- ✅ Build confidence in type system
- ✅ Foundation for later phases

**First 3 Tasks** (in order):
1. Fix missing exports in generated-types.ts (1-2 days)
2. Standardize ECharts types (1 day)
3. Update all chart components with new types (2-3 days)

---

## 📊 Progress Tracking

**Current Metrics**:
- TypeScript Errors: 262
- Registered Contracts: 4 APIs
- Contract Coverage: ~5% (4 of ~200 endpoints)

**Target Metrics** (after Phase 4):
- TypeScript Errors: <50
- Registered Contracts: 4 APIs (unchanged)
- Type Safety: >90%

**Target Metrics** (after Phase 7):
- TypeScript Errors: <20
- Registered Contracts: 115 APIs (P0+P1+P2)
- Contract Coverage: ~60%
- Type Safety: >95%

---

## 💡 Decision Points

**Decision 1**: Schemathesis vs Custom Contract Testing?
- **Recommendation**: Start with custom pytest, migrate to Schemathesis if needed
- **Rationale**: Lower learning curve, sufficient for current needs

**Decision 2**: Strict Type Checking Timeline?
- **Option A**: Enable immediately (breaks many things)
- **Option B**: Gradual rollout (recommended)
- **Recommendation**: Fix critical type errors first, then enable strict mode in Week 3

**Decision 3**: API Registry Priority?
- **Option A**: All APIs at once (4-6 months)
- **Option B**: Domain-by-domain (recommended)
- **Recommendation**: Register P0/P1 APIs first (2-3 months), P2/P3 later

---

## 🔄 Continuous Improvement

**Weekly Retrospective** Questions:
1. How many TypeScript errors were fixed?
2. How many contracts were registered?
3. What blocked progress?
4. What can be automated?

**Monthly Reviews**:
1. Update roadmap based on learnings
2. Adjust priorities as needed
3. Celebrate milestones achieved

---

**Next Step**: Review and approve this roadmap, then begin Phase 4.1 (Generated Types Cleanup)

**Owner**: Main CLI (Claude Code)
**Review Date**: 2025-01-06 (1 week)
**Stakeholders**: Frontend Team, Backend Team, DevOps Team
