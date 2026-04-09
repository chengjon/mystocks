# Web Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/web/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/web/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/web/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 之前仍把 ArtDeco 入口、统一规格、showcase、theme、Web3、HTML5 conversion、runtime planning 与多份历史报告全部平铺暴露
- 该 family 高入链、高耦合，但“高入链”不等于“全部继续根导航平铺”；需要保留少量主入口，其余收回 family transition index

## Changes

- 将 `docs/guides/web/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Web family 的根导航
- 根导航现在优先保留：
  - `guides/web/INDEX.md`
  - `guides/web/ARTDECO_START_HERE.md`
  - `guides/web/ARTDECO_MASTER_INDEX.md`
  - `guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
  - `guides/web/ARTDECO_COMPONENT_GUIDE.md`
  - `guides/web/ARTDECO_GRID_QUICK_REFERENCE.md`
  - `guides/web/ARTDECO_MENU_DATA_FETCHING_IMPLEMENTATION_GUIDE.md`
  - `guides/web/WEB_FRONTEND_STARTUP_GUIDE.md`
  - `guides/web/WEB_ACCESS_VERIFICATION_STANDARD.md`
  - `Supporting Guides` -> `guides/web/INDEX.md`
- 将 theme/showcase/report/Web3/HTML5 conversion/router migration/runtime planning 等材料收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - 无新增 canonical trunk；该 family 继续保持 `supporting`
- family transition index:
  - `docs/guides/web/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 ArtDeco history、theme、Web3、HTML5、planning、report leaf docs 的直接暴露
- retention duty:
  - `ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md`
  - `ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md`
  - `ARTDECO_GRID_QUICK_START.md`
  - `ARTDECO_MENU_API_MAPPING.md`
  - `ARTDECO_MENU_STRUCTURE_REFACTOR_PLAN.md`
  - `ARTDECO_MENU_USER_TESTING_GUIDE.md`
  - `ARTDECO_PAGE_TEMPLATE_GUIDE.md`
  - `ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
  - `ARTDECO_UI_UX_FUNCTIONALITY_GUIDE.md`
  - `ART_DECO_COMPONENTS_CATALOG.md`
  - `ART_DECO_COMPONENT_SHOWCASE.md`
  - `ART_DECO_COMPONENT_SHOWCASE_V2.md`
  - `ART_DECO_FINAL_REPORT.md`
  - `ART_DECO_IMPLEMENTATION_REPORT.md`
  - `ART_DECO_QUICK_REFERENCE.md`
  - `A_STOCK_DASHBOARD_USER_GUIDE.md`
  - `BLOOMBERG_TERMINAL_COMPONENT_GUIDE.md`
  - `CHART_SYSTEM_USER_GUIDE.md`
  - `LINEAR_THEME_COMPLETION_REPORT.md`
  - `LINEAR_THEME_GUIDE.md`
  - `TECHSTYLE_QUICK_REFERENCE.md`
  - `TECHSTYLE_THEME_GUIDE.md`
  - `TECHSTYLE_THEME_IMPROVEMENT_REPORT.md`
  - `TECHSTYLE_VISUAL_COMPARISON.md`
  - `VUE_TAB_DESIGN_GUIDELINES.md`
  - `WEB3_DESIGN_COMPLETE_REPORT.md`
  - `WEB3_DESIGN_SYSTEM.md`
  - `WEB3_IMPLEMENTATION_REPORT.md`
  - `WEB3_QUICK_START.md`
  - `2026-01-23-html5-migration-experience-optimization.md`
  - `HTML_TO_ARTDECO_VUE_CONVERSION_OPTIMIZED_PLAN.md`
  - `MYSTOCKS_HTML_TO_VUE_CONVERSION_STRATEGY.md`
  - `MYSTOCKS_WEB_STARTUP_EXPERIENCE.md`
  - `PHASE12_3_REALTIME_INTEGRATION.md`
  - `WEBSOCKET_PERFORMANCE_OPTIMIZATION_GUIDE.md`
  - `WEB_CLIENT_OPERATION_PLAN.md`
  - `WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md`
  - `WEB_FRAMEWORK_INTEGRATION_PLAN.md`
  - `WEB_HTML_SAMPLES_GUIDE.md`
  - `WEB_PAGES_DOCUMENTATION.md`
  - `WEB_PAGE_REDESIGN_COMPLETION_REPORT.md`
  - `WEB_ROUTER_MIGRATION_RECORD.md`
  - `WEB_TESTING_TOOLS_SETUP.md`
  - `web页面结构详细描述.md`
  - 以上文档继续保留为 specialized/reference docs

## Expected Effect

- 根导航优先暴露当前仍有高直接使用价值的 ArtDeco 上手入口、统一规格、关键实现说明与 runtime verification 入口
- theme/showcase/report/Web3/HTML5/planning 等材料不再与主入口平级暴露，但仍可通过 family index 进入
- `docs/guides/web/` 的下一轮若继续推进，只应围绕具体子 cluster 做 bounded cleanup，不适合回到 subtree-wide 收缩
