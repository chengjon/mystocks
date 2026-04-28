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
> - 根级提交前类型守卫：`.pre-commit-config.yaml` 已配置 `cd web/frontend && npx vue-tsc --noEmit`
> - 扩展目录外的共享类型沉淀：`src/components/shared/types.ts` 已提供 `TableColumn<T>`，`src/utils/chartDataUtils.types.ts` 已提供 `ChartDataPoint`
> - 实测验证：`cd web/frontend && npm run type-check` 通过；`cd web/frontend && npm run build:no-types` 通过
> 关键残缺点也很明确：
> - 仅 `market/` 子目录落地，`strategy/`、`common/`、`ui/`、`api/`、`utils/` 目录化结构未完整形成
> - `package.json` 引用了 `scripts/check-type-conflicts.js`、`scripts/generate-type-usage.js`，但当前文件未找到
> - `web/frontend/src/api/types/index.ts` 仍未导出 `extensions`
> - `web/frontend/tsconfig.json` 当前反而排除了 `src/api/types/extensions/**/*`
> - `cd web/frontend && npm run build` 当前未闭环：`generate_frontend_types.py` 在写 `src/api/types/admin.ts` 时因 `PermissionError` 失败，生成类型文件当前由 `nobody:nogroup` 持有
> 因此下方仅勾选有直接仓库证据支持的任务，避免把“有雏形”误写成“已完成收口”。


## Phase 1: Infrastructure Setup (1.5 hours)

### 1.1 Create Directory Structure
> **局部事实说明（2026-04-28）**:
> `web/frontend/src/api/types/extensions/` 当前仅能确认根目录与 `market/` 子目录存在；`strategy/`、`common/`、`ui/`、`api/`、`utils/` 子目录未在当前仓库落地。

- [x] Create `src/api/types/extensions/` directory
- [ ] Create subdirectories: `strategy/`, `market/`, `common/`, `ui/`, `api/`, `utils/`
- [x] Create `extensions/index.ts` export file
- [x] Create `tools/validators/` directory

### 1.2 Setup Build Scripts
- [x] Update `package.json` with new type validation scripts
- [x] Add `type:validate` and `type:check:conflicts` commands
- [x] Configure pre-commit hooks for type checking

### 1.3 Create Type Validator Tool
- [x] Implement `TypeValidator.ts` for conflict detection
- [x] Add type completeness validation
- [ ] Create usage statistics generator
  - [ ] Repo-truth：`web/frontend/package.json` 虽声明 `type:usage` -> `node scripts/generate-type-usage.js`，但当前未找到该脚本文件，因此不能视为 usage statistics generator 已落地。

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
> **局部事实说明**:
> `Position` 相关类型当前是“扩展层 `PositionVM` + 生成层 `PositionItem`”并存，不是单一统一别名设计，但“存在可用位置类型定义”这一任务目标已被当前仓库满足。

- [x] Define `PositionItem` type alias
- [x] Create `list<T>` and `date_type` utilities
- [x] Add basic validation types

### 2.4 Export Configuration (15 minutes)
- [ ] Update `src/api/types/index.ts` to merge exports
- [ ] Ensure backward compatibility with existing imports

## Phase 3: Extended Type Definitions (1.5 hours)

### 3.1 UI Component Types (45 minutes)
> **局部事实说明**:
> `TableColumn<T>` 与 `ChartDataPoint` 已存在于共享组件 / 工具类型模块中，但尚未并入 `src/api/types/extensions/` 统一收口。
> 当前未检出 `FormField` / validation types 的现行类型定义；仓库里仅能看到 `web/frontend/scripts/migrate-to-element-plus.sh` 中遗留的 `FormField -> el-input` 迁移脚本片段，不能作为类型实现证据。

- [x] Define `TableColumn<T>` for data tables
- [x] Create `ChartDataPoint` for visualization
- [ ] Add `FormField` and validation types

### 3.2 API Utility Types (30 minutes)
- [x] Create `APIResponse<T>` wrapper type
- [x] Define pagination and sorting parameters
- [x] Add upload and WebSocket message types

### 3.3 Business Logic Types (30 minutes)
- [x] Add search, filter, and sort parameter types
- [x] Create notification and modal component types
  - Repo-truth note: current implementations are distributed rather than unified under `src/api/types/extensions/`: notification-related shapes exist as `NotificationVM` / `NotificationPreferencesVM` in `src/utils/user-adapters/types-1.ts`, reusable toast notification contracts exist as `ToastConfig` / `ToastManager` in `src/composables/useToastManager.ts` with unit tests in `src/composables/__tests__/useToastManager.spec.ts`, and modal component contracts exist as `Props` / `Emits` in `src/components/shared/ui/DetailDialog.vue`.

## Phase 4: Integration & Validation (1.5 hours)

> **局部事实说明**:
> 当前仓库已有全局 TypeScript / vue-tsc CI 工作流，
> 但本专题自身的集成并未完全闭环，因为 `extensions` 仍未被 `src/api/types/index.ts` 合并导出，且 `tsconfig.json` 当前把 `extensions/**/*` 排除在外。

### 4.1 Build Integration (30 minutes)
> **局部事实说明（2026-04-28）**:
> `web/frontend/tsconfig.json` 当前虽然设置了 `allowImportingTsExtensions: true`，但同时把 `src/api/types/extensions/**/*` 排除在 typecheck 之外；`web/frontend/vite.config.mts` 也未见面向该扩展系统的专门 type-only import / extensions 集成配置。
> 因此 4.1.1 / 4.1.2 对应的集成收口仍未完成。

- [ ] Update `tsconfig.json` with type checking paths
- [ ] Configure Vite for type-only imports
- [x] Add type checking to CI/CD pipeline

### 4.2 Testing & Validation (45 minutes)
> **局部事实说明（2026-04-28）**:
> 当前仓库可以确认存在“类型相关回归/卫生测试”，例如：
> - `web/frontend/src/api/__tests__/strategy.test.ts` 直接导入 `@/api/types/extensions/strategy`
> - `web/frontend/tests/unit/config/*types-cleanup.spec.ts` 覆盖多个类型文件的 `ts-nocheck` 清理约束
> 但这仍不足以视为本专题要求的“扩展类型定义单元测试 + 42 types compile 闭环”；当前未找到专门面向 `extensions/` 目录全集的独立测试套件或编译核验报告。

- [ ] Create type definition unit tests
- [ ] Validate all 42 types compile correctly
- [x] Test import paths and type resolution

### 4.3 Documentation (30 minutes)
- [ ] Create type extension usage guide
- [ ] Document naming conventions and patterns
- [ ] Add examples for common use cases

## Phase 5: Deployment & Monitoring (1 hour)

### 5.1 Deployment Preparation (20 minutes)
- [x] Run full type check on entire codebase
- [ ] Validate no breaking changes to existing code
- [ ] Prepare rollback plan if needed

### 5.2 Production Deployment (20 minutes)
- [ ] Commit type extension system
- [ ] Update package.json dependencies if needed
- [ ] Deploy to development environment

### 5.3 Monitoring Setup (20 minutes)
- [x] Configure type checking in pre-commit hooks
- [ ] Set up automated type validation reports
- [ ] Create type health monitoring dashboard
  - [ ] Repo-truth：当前未找到自动生成类型校验报告或“type health dashboard”的现行实现；`type:check:conflicts` 与 `type:usage` 依赖的 `scripts/check-type-conflicts.js`、`scripts/generate-type-usage.js` 文件都不存在。

## Validation Criteria

### Functional Validation
- [ ] All 36 TypeScript errors resolved
- [ ] All 42 types successfully compile
- [x] Import statements work correctly
- [ ] No type conflicts detected

### Integration Validation
> **局部事实说明（2026-04-28）**:
> `cd web/frontend && npm run type-check` 与 `npm run build:no-types` 可通过，但这不能替代本节闭环：
> - `npm run build` 仍依赖 `generate_frontend_types.py`，当前会在写 `src/api/types/admin.ts` 时触发 `PermissionError`
> - `npm run dev` 默认同样先执行 `generate-types`
> 因此在生成链路权限问题消除前，`Build process completes successfully` 与 `Development server starts without errors` 继续保留未完成。

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
