# Implementation Tasks

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

> **仓库事实校对（2026-04-27）**:
> 当前仓库已经存在“部分 TypeScript 扩展系统”，但未按本 proposal 完整收口。
> 已核对到的核心证据包括：
> - 扩展目录与入口：`web/frontend/src/api/types/extensions/`、`web/frontend/src/api/types/extensions/index.ts`
> - 类型验证器：`web/frontend/src/api/types/tools/validators/TypeValidator.ts`
> - package scripts：`web/frontend/package.json`
> - 部分实现类型：`extensions/strategy.ts`、`extensions/common.ts`、`extensions/market/index.ts`
> 关键残缺点也很明确：
> - 仅 `market/` 子目录落地，`strategy/`、`common/`、`ui/`、`api/`、`utils/` 目录化结构未完整形成
> - `package.json` 引用了 `scripts/check-type-conflicts.js`、`scripts/generate-type-usage.js`，但当前文件未找到
> - `web/frontend/src/api/types/index.ts` 仍未导出 `extensions`
> - `web/frontend/tsconfig.json` 当前反而排除了 `src/api/types/extensions/**/*`
> 因此下方仅勾选有直接仓库证据支持的任务，避免把“有雏形”误写成“已完成收口”。


## Phase 1: Infrastructure Setup (1.5 hours)

### 1.1 Create Directory Structure
- [x] Create `src/api/types/extensions/` directory
- [ ] Create subdirectories: `strategy/`, `market/`, `common/`, `ui/`, `api/`, `utils/`
- [x] Create `extensions/index.ts` export file
- [x] Create `tools/validators/` directory

### 1.2 Setup Build Scripts
- [x] Update `package.json` with new type validation scripts
- [x] Add `type:validate` and `type:check:conflicts` commands
- [ ] Configure pre-commit hooks for type checking

### 1.3 Create Type Validator Tool
- [x] Implement `TypeValidator.ts` for conflict detection
- [x] Add type completeness validation
- [ ] Create usage statistics generator

## Phase 2: Core Type Definitions (2 hours)

> **局部事实说明**:
> 当前实现采用“`*VM` 为主 + 局部 alias”的命名方式，而不是完全按任务文案逐字命名。
> 只要目标类型已在扩展系统中落地，并承担对应职责，下方按“已实现但命名有偏差”处理。

### 2.1 Strategy Types (45 minutes)
- [x] Define `Strategy` interface with performance metrics
- [x] Create `BacktestResultVM` for frontend display
- [x] Add `CreateStrategyRequest` and `UpdateStrategyRequest`
- [x] Implement `StrategyPerformance` with Sharpe ratio, etc.

### 2.2 Market Types (30 minutes)
- [x] Create `MarketOverviewVM` with sentiment analysis
- [x] Define `KLineChartData` for chart visualization
- [x] Add `FundFlowChartPoint` for capital flow charts

### 2.3 Common Types (30 minutes)
- [ ] Define `PositionItem` type alias
- [x] Create `list<T>` and `date_type` utilities
- [x] Add basic validation types

### 2.4 Export Configuration (15 minutes)
- [ ] Update `src/api/types/index.ts` to merge exports
- [ ] Ensure backward compatibility with existing imports

## Phase 3: Extended Type Definitions (1.5 hours)

### 3.1 UI Component Types (45 minutes)
- [ ] Define `TableColumn<T>` for data tables
- [ ] Create `ChartDataPoint` for visualization
- [ ] Add `FormField` and validation types

### 3.2 API Utility Types (30 minutes)
- [x] Create `APIResponse<T>` wrapper type
- [x] Define pagination and sorting parameters
- [x] Add upload and WebSocket message types

### 3.3 Business Logic Types (30 minutes)
- [x] Add search, filter, and sort parameter types
- [ ] Create notification and modal component types

## Phase 4: Integration & Validation (1.5 hours)

> **局部事实说明**:
> 当前仓库已有全局 TypeScript / vue-tsc CI 工作流，
> 但本专题自身的集成并未完全闭环，因为 `extensions` 仍未被 `src/api/types/index.ts` 合并导出，且 `tsconfig.json` 当前把 `extensions/**/*` 排除在外。

### 4.1 Build Integration (30 minutes)
- [ ] Update `tsconfig.json` with type checking paths
- [ ] Configure Vite for type-only imports
- [x] Add type checking to CI/CD pipeline

### 4.2 Testing & Validation (45 minutes)
- [ ] Create type definition unit tests
- [ ] Validate all 42 types compile correctly
- [ ] Test import paths and type resolution

### 4.3 Documentation (30 minutes)
- [ ] Create type extension usage guide
- [ ] Document naming conventions and patterns
- [ ] Add examples for common use cases

## Phase 5: Deployment & Monitoring (1 hour)

### 5.1 Deployment Preparation (20 minutes)
- [ ] Run full type check on entire codebase
- [ ] Validate no breaking changes to existing code
- [ ] Prepare rollback plan if needed

### 5.2 Production Deployment (20 minutes)
- [ ] Commit type extension system
- [ ] Update package.json dependencies if needed
- [ ] Deploy to development environment

### 5.3 Monitoring Setup (20 minutes)
- [ ] Configure type checking in pre-commit hooks
- [ ] Set up automated type validation reports
- [ ] Create type health monitoring dashboard

## Validation Criteria

### Functional Validation
- [ ] All 36 TypeScript errors resolved
- [ ] All 42 types successfully compile
- [ ] Import statements work correctly
- [ ] No type conflicts detected

### Integration Validation
- [ ] Existing code continues to work
- [ ] Build process completes successfully
- [ ] Development server starts without errors
- [ ] Hot reload works with new types

### Quality Validation
- [ ] Type definitions follow naming conventions
- [ ] JSDoc comments complete and accurate
- [ ] No unused type definitions
- [ ] Type coverage meets 95% target

## Dependencies
- No external dependencies required
- Uses existing TypeScript and Vite setup
- Compatible with current build pipeline

## Risk Mitigation
- **Rollback Plan**: Delete extensions directory and revert index.ts
- **Incremental Rollout**: Can disable via feature flag if issues arise
- **Testing Coverage**: Comprehensive type validation before deployment</content>
<parameter name="filePath">openspec/changes/implement-typescript-type-extension-system/tasks.md
