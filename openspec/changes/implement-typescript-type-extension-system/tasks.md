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
- [x] Create usage statistics generator
  - Repo-truth（2026-05-03）：`web/frontend/scripts/generate-type-usage.js` 已落地；当前会输出 `extensions.files`、`extensions.exported_types`、`main_index.exports_extensions`、`combined_public_surface.exported_types` 等 JSON summary。

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
- [x] Update `src/api/types/index.ts` to merge exports
- [x] Ensure backward compatibility with existing imports
  - Repo-truth（2026-05-03）：当前仓库采用 `export * as extensions from './extensions';` 的命名空间导出，而不是顶层 `export *` 平铺；这样既暴露统一入口，又避免与 `src/api/types/common/all.ts` 已公开的 `APIResponse` / `PaginatedResponse` / `PaginationParams` 等现有顶层类型发生冲突。

## Phase 3: Extended Type Definitions (1.5 hours)

### 3.1 UI Component Types (45 minutes)
> **局部事实说明**:
> `TableColumn<T>` 与 `ChartDataPoint` 已存在于共享组件 / 工具类型模块中，但尚未并入 `src/api/types/extensions/` 统一收口。
> `FormField` / validation types 当前已在 `web/frontend/src/api/types/extensions/ui.ts` 落地，并由 `extensions/index.ts` 统一导出；该层仍属于 frontend-only UI metadata，而不是后端契约生成结果。

- [x] Define `TableColumn<T>` for data tables
- [x] Create `ChartDataPoint` for visualization
- [x] Add `FormField` and validation types
  - Repo-truth（2026-05-03）：当前已新增 `FormField`、`FormValidationRule`、`FormValidationSchema`、`FormValidationState`、`FormFieldOption`、`FormFieldComponent` 等表单/UI 元数据类型，路径为 `web/frontend/src/api/types/extensions/ui.ts`。

### 3.2 API Utility Types (30 minutes)
- [x] Create `APIResponse<T>` wrapper type
- [x] Define pagination and sorting parameters
- [x] Add upload and WebSocket message types

### 3.3 Business Logic Types (30 minutes)
- [x] Add search, filter, and sort parameter types
- [x] Create notification and modal component types
  - Repo-truth note: current implementations are distributed rather than unified under `src/api/types/extensions/`: notification-related shapes exist as `NotificationVM` / `NotificationPreferencesVM` in `src/utils/user-adapters/types-1.ts`, reusable toast notification contracts exist as `ToastConfig` / `ToastManager` in `src/composables/useToastManager.ts` with unit tests in `src/composables/__tests__/useToastManager.spec.ts`, and modal component contracts exist as `Props` / `Emits` in `src/components/shared/ui/DetailDialog.vue`.

## Phase 4: Integration & Validation (1.5 hours)

> **局部事实说明（2026-05-03）**:
> 当前仓库已有全局 TypeScript / vue-tsc CI 工作流；本专题在 repo 内的关键缺口已缩小为：
> - `extensions` 已经通过 `src/api/types/index.ts` 以命名空间方式公开
> - `tsconfig.json` 已不再排除 `extensions/**/*`
> - `npm run type-check` 当前可在包含扩展类型的前提下通过
> 仍未闭环的主要是 Vite 专项配置、专题使用文档，以及“42 types”这类历史计数口径与当前仓库事实不一致的问题。

### 4.1 Build Integration (30 minutes)
> **局部事实说明（2026-05-03）**:
> `web/frontend/tsconfig.json` 目前仍保留 `allowImportingTsExtensions: true`，且已将 `src/api/types/extensions/**/*` 重新纳入 typecheck；`cd web/frontend && npm run type-check` 当前通过。
> 但 `web/frontend/vite.config.mts` 仍未见面向该扩展系统的专门 type-only import / extensions 集成配置，因此本节只闭合 `tsconfig` 侧，不拔高到 Vite 全量闭环。

- [x] Update `tsconfig.json` with type checking paths
- [ ] Configure Vite for type-only imports
- [x] Add type checking to CI/CD pipeline

### 4.2 Testing & Validation (45 minutes)
> **局部事实说明（2026-05-03）**:
> 当前仓库已新增面向本专题脚本闭环的独立测试：
> - `tests/unit/scripts/test_frontend_type_extension_tooling.py`
> 该测试会直接验证：
> - 主索引公开 `extensions`
> - `tsconfig.json` 不再排除 `extensions/**/*`
> - `scripts/validate-types.js`、`scripts/check-type-conflicts.js`、`scripts/generate-type-usage.js` 全部可运行
> 但 “Validate all 42 types compile correctly” 这一历史计数口径仍与当前仓库事实不一致：`type:usage` 当前统计到 `extensions.exported_types = 85`，因此仅能确认“包含扩展类型的 `npm run type-check` 通过”，不能把旧的 `42` 计数照抄为完成。

- [x] Create type definition unit tests
- [x] Validate all 42 types compile correctly
  - Repo-truth（2026-05-03）：`cd web/frontend && npm run type:report -- --report-dir /tmp/type-extension-dashboard-smoke` 当前返回 `typecheck.ok = true`、`type_error_count = 0`；历史任务文案中的 “42 types” 计数已经与当前仓库实际 surface 漂移，但“当前扩展类型面可通过编译检查”这一目标已被仓库内验证满足。
- [x] Test import paths and type resolution

### 4.3 Documentation (30 minutes)
- [x] Create type extension usage guide
- [x] Document naming conventions and patterns
- [x] Add examples for common use cases
  - Repo-truth（2026-05-03）：当前使用指南已落在 `docs/guides/typescript/TYPESCRIPT_EXTENSION_SYSTEM_REPO_TRUTH_GUIDE.md`，内容聚焦当前真实结构、命名规则、导入建议、验证脚本与常见边界，不再复述旧实施计划。

## Phase 5: Deployment & Monitoring (1 hour)

### 5.1 Deployment Preparation (20 minutes)
- [x] Run full type check on entire codebase
- [x] Validate no breaking changes to existing code
  - Repo-truth（2026-05-03）：当前已新增 compile-time smoke fixture `web/frontend/src/api/types/compatibility-smoke.ts`，并通过 `cd web/frontend && npm run type-check` 验证 legacy root exports（`APIResponse` / `PaginationParams` / `UnifiedResponse`）与扩展层导出（`StrategyVM` / `FormField`）可在同一编译链中共存。
- [x] Prepare rollback plan if needed
  - Repo-truth（2026-05-03）：当前回滚顺序已写入 `docs/guides/typescript/TYPESCRIPT_EXTENSION_SYSTEM_REPO_TRUTH_GUIDE.md` 第 7 节，覆盖 `extensions` 命名空间导出、专题类型文件、compatibility smoke fixture 以及 `type:validate` / `type:check:conflicts` / `type:audit:quality` / `type:usage` / `type:report` / `type:dashboard` 脚本入口的最小回退路径。

### 5.2 Production Deployment (20 minutes)
- [ ] Commit type extension system
- [ ] Update package.json dependencies if needed
- [ ] Deploy to development environment

### 5.3 Monitoring Setup (20 minutes)
- [x] Configure type checking in pre-commit hooks
- [x] Set up automated type validation reports
  - Repo-truth（2026-05-03）：`web/frontend/scripts/generate-type-validation-report.js` 已落地，并由 `npm run type:report` 暴露；当前会归并 `validate-types`、`check-type-conflicts`、`audit-type-extension-quality`、`generate-type-usage` 与 `npm run type-check`，默认写入 `reports/analysis/typescript-extension-validation/`，同时生成时间戳 JSON 与 `latest.json`。
- [x] Create type health monitoring dashboard
  - Repo-truth（2026-05-03）：当前已新增 `web/frontend/scripts/generate-type-health-dashboard.js`，并由 `npm run type:dashboard` 暴露；该脚本会读取 `type:report` 生成的 `latest.json`，默认输出到 `reports/analysis/typescript-extension-validation/dashboard/`，同时生成时间戳 HTML 与 `latest.html` 静态 dashboard artifact。
  - Repo-truth（2026-05-03）：当前已经具备 `type:report` 的 JSON artifact 生成能力，但仍未接入可视化 dashboard、定时调度或持续监控面板。

## Validation Criteria

### Functional Validation
- [x] All 36 TypeScript errors resolved
  - Repo-truth（2026-05-03）：`type:report` 当前记录 `typecheck.type_error_count = 0`，说明本专题当前 typecheck 链路下已无可观测 TypeScript 编译错误；原始 “36” 为历史问题计数，不再作为当前仓库基线。
- [x] All 42 types successfully compile
  - Repo-truth（2026-05-03）：当前 `type:report` 已记录 `typecheck.ok = true`；历史 “42” 计数与当前扩展类型面规模已发生漂移，但“当前扩展类型面编译通过”这一验收语义已满足。
- [x] Import statements work correctly
- [x] No type conflicts detected
  - Repo-truth（2026-05-03）：`cd web/frontend && node scripts/check-type-conflicts.js` 当前返回 `No type conflicts detected`；主索引对 `extensions` 的公开方式是命名空间导出，不再把扩展层直接平铺到顶层 public surface。

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
- [x] Type definitions follow naming conventions
  - Repo-truth（2026-05-03）：`cd web/frontend && npm run type:audit:quality` 当前返回 `naming.ok = true`，并把 `list`、`date_type` 视为当前仓库明确允许保留的 legacy utility aliases，而不是命名违规。
- [x] JSDoc comments complete and accurate
  - Repo-truth（2026-05-03）：`cd web/frontend && npm run type:audit:quality` 当前返回 `jsdoc.ok = true`、`jsdoc.missing = []`；此前缺失的 `strategy.ts` / `ui.ts` 顶层导出注释已补齐。
- [ ] No unused type definitions
  - Repo-truth（2026-05-03）：`type:audit:quality` 当前仍报告 `unused.count = 47`，因此这项继续保持未完成，避免把“可观测到未使用”误写成“已治理完成”。
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
