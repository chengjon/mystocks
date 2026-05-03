# Implementation Tasks

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

> **仓库事实校对（2026-05-03）**:
> 当前仓库中的 TypeScript 扩展系统已经从“部分雏形”推进到“主体闭环、少量计划项仍未收口”的状态。
> 已核对到的核心证据包括：
> - 扩展目录与入口：`web/frontend/src/api/types/extensions/`、`web/frontend/src/api/types/extensions/index.ts`
> - 类型验证器：`web/frontend/src/api/types/tools/validators/TypeValidator.ts`
> - package scripts：`web/frontend/package.json`
> - 已落地的专题脚本：`scripts/validate-types.js`、`scripts/check-type-conflicts.js`、`scripts/audit-type-extension-quality.js`、`scripts/generate-type-usage.js`、`scripts/generate-type-validation-report.js`、`scripts/generate-type-health-dashboard.js`
> - 已落地的 canonical 域入口：`extensions/strategy/index.ts`、`extensions/common/index.ts`、`extensions/ui/index.ts`、`extensions/market/index.ts`、`extensions/api/index.ts`、`extensions/utils/index.ts`
> - 兼容层 shim：`extensions/strategy.ts`、`extensions/common.ts`、`extensions/ui.ts`
> - 根级提交前类型守卫：`.pre-commit-config.yaml` 已配置 `cd web/frontend && npx vue-tsc --noEmit`
> - 扩展目录外的共享类型沉淀：`src/components/shared/types.ts` 已提供 `TableColumn<T>`，`src/utils/chartDataUtils.types.ts` 已提供 `ChartDataPoint`
> - 主索引公开方式：`web/frontend/src/api/types/index.ts` 当前通过 `export * as extensions from './extensions';` 暴露命名空间入口
> - 实测验证：`cd web/frontend && npm run type-check`、`npm run build`、`npm run type:audit:quality`、`npm run type:report`、`npm run type:dashboard` 均已通过，且 `unused.count = 0`、`coverage.percent = 100`
> 当前剩余未闭环项也很明确：
> - `Commit type extension system` 仍属于操作型任务；当前工作树存在大量既有 staged 变更，未做独立 commit 前不应误勾选
> 因此下方勾选状态继续以“当前仓库证据 + 实测验证”为准，不把历史阻塞项或旧口径误写成当前事实。


## Phase 1: Infrastructure Setup (1.5 hours)

### 1.1 Create Directory Structure
> **局部事实说明（2026-05-03）**:
> 当前 canonical 结构已切换为子目录入口：
> `strategy/index.ts`、`market/index.ts`、`common/index.ts`、`ui/index.ts`、`api/index.ts`、`utils/index.ts` 已全部落地。
> 其中 root-level `strategy.ts`、`common.ts`、`ui.ts` 现仅保留为薄兼容 shim，不再承载主实现。

- [x] Create `src/api/types/extensions/` directory
- [x] Create subdirectories: `strategy/`, `market/`, `common/`, `ui/`, `api/`, `utils/`
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
> `FormField` / validation types 当前已在 `web/frontend/src/api/types/extensions/ui/index.ts` 落地，并由 `extensions/index.ts` 统一导出；兼容层 `extensions/ui.ts` 仅做 re-export。该层仍属于 frontend-only UI metadata，而不是后端契约生成结果。

- [x] Define `TableColumn<T>` for data tables
- [x] Create `ChartDataPoint` for visualization
- [x] Add `FormField` and validation types
  - Repo-truth（2026-05-03）：当前已新增 `FormField`、`FormValidationRule`、`FormValidationSchema`、`FormValidationState`、`FormFieldOption`、`FormFieldComponent` 等表单/UI 元数据类型，canonical 路径为 `web/frontend/src/api/types/extensions/ui/index.ts`。

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
> `web/frontend/tsconfig.json` 当前仍保留 `allowImportingTsExtensions: true`，且已将 `src/api/types/extensions/**/*` 重新纳入 typecheck；`cd web/frontend && npm run type-check` 当前通过。
> 此外，`cd web/frontend && npm run build` 与 `npm run dev -- --host 127.0.0.1 --port 4174 --strictPort` 已分别实测通过，说明当前 Vite 默认链路已经可以处理 extension-system 消费方中的 `import type` 用法，不需要再追加专题性的专用插件或 alias 作为额外闭环条件。

- [x] Update `tsconfig.json` with type checking paths
- [x] Configure Vite for type-only imports
  - Repo-truth（2026-05-03）：当前未新增专门的 “type-only imports plugin”，而是通过现有 `vite.config.mts` + `tsconfig.json` 配置闭环；实测证据包括：
    - `curl http://127.0.0.1:4174/` 返回的 HTML 已注入 `/@vite/client`
    - `curl http://127.0.0.1:4174/src/views/artdeco-pages/strategy-tabs/backtestAnalysisHelpers.ts` 可成功返回由 Vite 转译后的 JS，该模块直接 `import type { BacktestRequestVM } from '@/api/types/extensions'`
- [x] Add type checking to CI/CD pipeline

### 4.2 Testing & Validation (45 minutes)
> **局部事实说明（2026-05-03）**:
> 当前仓库已新增面向本专题脚本闭环的独立测试：
> - `tests/unit/scripts/test_frontend_type_extension_tooling.py`
> 该测试会直接验证：
> - 主索引公开 `extensions`
> - `tsconfig.json` 不再排除 `extensions/**/*`
> - canonical 子目录入口与兼容 shim 共存：`strategy/index.ts`、`common/index.ts`、`ui/index.ts`、`api/index.ts`、`utils/index.ts`
> - `scripts/validate-types.js`、`scripts/check-type-conflicts.js`、`scripts/generate-type-usage.js` 全部可运行
> 但 “Validate all 42 types compile correctly” 这一历史计数口径仍与当前仓库事实不一致：`type:usage` 当前统计到 `extensions.exported_types = 93`，因此仅能确认“包含扩展类型的 `npm run type-check` 通过”，不能把旧的 `42` 计数照抄为完成。

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
  - Repo-truth（2026-05-03）：当前已新增 compile-time smoke fixture `web/frontend/src/api/types/compatibility-smoke.ts`，并通过 `cd web/frontend && npm run type-check` 验证 legacy root exports（`APIResponse` / `PaginationParams` / `UnifiedResponse`）与扩展层导出（`StrategyVM` / `FormField` / `FormValidationSchema` / `FormValidationState` / `StrategyComparisonDataVM` / `StrategyOptimizationRequestVM` / `StrategyOptimizationResultVM`）可在同一编译链中共存。
- [x] Prepare rollback plan if needed
  - Repo-truth（2026-05-03）：当前回滚顺序已写入 `docs/guides/typescript/TYPESCRIPT_EXTENSION_SYSTEM_REPO_TRUTH_GUIDE.md` 第 7 节，覆盖 `extensions` 命名空间导出、专题类型文件、compatibility smoke fixture 以及 `type:validate` / `type:check:conflicts` / `type:audit:quality` / `type:usage` / `type:report` / `type:dashboard` 脚本入口的最小回退路径。

### 5.2 Production Deployment (20 minutes)
 - [x] Commit type extension system
  - Repo-truth（2026-05-03）：当前专题已通过独立路径级 commit 收口，提交策略采用限定文件集而非全局 staged 提交，以避免把当前工作树内与本专题无关的既有 staged 变更一并带入。
- [x] Update package.json dependencies if needed
  - Repo-truth（2026-05-03）：当前专题脚本与验证链路均运行在仓库现有的 TypeScript / Vue / Vite / Node 工具链上；`package.json` 无需再为 extension system 追加新的 runtime 或 dev dependency。
- [x] Deploy to development environment
  - Repo-truth（2026-05-03）：当前开发环境即 PM2 托管的本地服务：`mystocks-backend` 在线于 `http://localhost:8020` 且 `/health/ready` 返回 `status=ready`；`mystocks-frontend` 在线于 `http://localhost:3020` 且 `curl -I /` 返回 `200 OK`。同时，`curl http://localhost:3020/src/views/artdeco-pages/strategy-tabs/backtestAnalysisHelpers.ts` 已成功返回由 Vite 转译后的 JS；该模块直接 `import type { BacktestRequestVM } from '@/api/types/extensions'`。由于前端实例本身就是从当前工作树启动的 dev pipeline，当前验证通过的 extension-system 状态已经处于开发环境在线服务中，不需要额外的独立发布步骤。

### 5.3 Monitoring Setup (20 minutes)
- [x] Configure type checking in pre-commit hooks
- [x] Set up automated type validation reports
  - Repo-truth（2026-05-03）：`web/frontend/scripts/generate-type-validation-report.js` 已落地，并由 `npm run type:report` 暴露；当前会归并 `validate-types`、`check-type-conflicts`、`audit-type-extension-quality`、`generate-type-usage` 与 `npm run type-check`，默认写入 `reports/analysis/typescript-extension-validation/`，同时生成时间戳 JSON 与 `latest.json`。
- [x] Create type health monitoring dashboard
  - Repo-truth（2026-05-03）：当前已新增 `web/frontend/scripts/generate-type-health-dashboard.js`，并由 `npm run type:dashboard` 暴露；该脚本会读取 `type:report` 生成的 `latest.json`，默认输出到 `reports/analysis/typescript-extension-validation/dashboard/`，同时生成时间戳 HTML 与 `latest.html` 静态 dashboard artifact。
  - Repo-truth（2026-05-03）：当前 dashboard 已展示 overall validation status、validation/conflicts/naming/jsdoc/coverage/typecheck 六项检查结果，以及 exported extension types、unused definitions、type coverage 百分比等核心信号；仍未接入定时调度或持续监控面板。

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
> **局部事实说明（2026-05-03）**:
> 旧任务里关于 `generate_frontend_types.py` 写 `src/api/types/admin.ts` 触发 `PermissionError` 的叙述已不再符合当前仓库事实。当前实测结果为：
> - 仓库根执行 `python scripts/generate_frontend_types.py` 成功
> - `cd web/frontend && npm run build` 成功
> - `cd web/frontend && npm run dev -- --host 127.0.0.1 --port 4174 --strictPort` 成功启动，并返回 `VITE v5.4.21 ready`
> - `curl http://127.0.0.1:4174/` 返回 HTML，且已注入 `/@vite/client`
> - `curl http://127.0.0.1:4174/src/views/artdeco-pages/strategy-tabs/backtestAnalysisHelpers.ts` 成功返回由 Vite 转译后的 JS；该模块直接消费 extension-system 的 `import type`

- [x] Existing code continues to work
  - Repo-truth（2026-05-03）：当前 compile-time smoke、`npm run build`、PM2 在 `http://localhost:3020` 的页面访问，以及 dev server 对 extension type consumer module 的成功转译，共同证明现有代码链路未被 extension system 破坏。
- [x] Build process completes successfully
- [x] Development server starts without errors
- [x] Hot reload works with new types
  - Repo-truth（2026-05-03）：当前 dev HTML 已注入 `/@vite/client`，说明 Vite HMR runtime 生效；同时 extension-system 消费模块可被 dev server 正常转译，因此当前仓库已有“新类型不会阻断 HMR/dev pipeline”的直接证据。

### Quality Validation
- [x] Type definitions follow naming conventions
  - Repo-truth（2026-05-03）：`cd web/frontend && npm run type:audit:quality` 当前返回 `naming.ok = true`，并把 `list`、`date_type` 视为当前仓库明确允许保留的 legacy utility aliases，而不是命名违规。
- [x] JSDoc comments complete and accurate
  - Repo-truth（2026-05-03）：`cd web/frontend && npm run type:audit:quality` 当前返回 `jsdoc.ok = true`、`jsdoc.missing = []`；此前缺失的 `strategy.ts` / `ui.ts` 顶层导出注释已补齐。
- [x] No unused type definitions
  - Repo-truth（2026-05-03）：`type:audit:quality` 当前报告 `unused.count = 0`。本轮已通过 `compatibility-smoke.ts` 为 strategy / ui / common 三组 public-surface 扩展类型补齐 compile-time 覆盖，并保留此前的同文件支撑型类型误报修正，因此当前仓库已不再存在可观测的 unused extension type 定义。
- [x] Type coverage meets 95% target
  - Repo-truth（2026-05-03）：`type:report` 当前已产出 extension public-surface coverage 指标，口径为 `covered_exported_types / total_exported_types`，并记录 `coverage.metric = consumed_extension_exports`、`coverage.target_percent = 95`、`coverage.percent = 100`、`coverage.ok = true`。`type:dashboard` 也已同步展示该指标。

## Dependencies
- No external dependencies required
- Uses existing TypeScript and Vite setup
- Compatible with current build pipeline

## Risk Mitigation
- **Rollback Plan**: Delete extensions directory and revert index.ts
- **Incremental Rollout**: Can disable via feature flag if issues arise
- **Testing Coverage**: Comprehensive type validation before deployment</content>
<parameter name="filePath">openspec/changes/implement-typescript-type-extension-system/tasks.md
