## MODIFIED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Front-end Directory Layout
The system SHALL organize Vue page components inside domain-specific directories under `src/views/` according to business capabilities: market, data, strategy, trade, risk, watchlist, system, and errors.

Each domain directory SHALL contain:
- Main page files (e.g., `Overview.vue`, `Center.vue`)
- A `tabs/` subdirectory for tab-based sub-pages (optional)
- A `components/` subdirectory for domain-specific reusable components (optional)

#### Scenario: Post-migration navigation to market domain
- **WHEN** a user navigates to `/market/realtime`
- **THEN** the router resolves `src/views/market/Realtime.vue` and renders the market realtime analysis page

#### Scenario: Post-migration navigation to trade domain
- **WHEN** a user navigates to `/trade/center`
- **THEN** the router resolves `src/views/trade/Center.vue` and renders the trading center page

#### Scenario: Domain directory structure
- **WHEN** a developer inspects `src/views/`
- **THEN** they see exactly 8 domain folders (market, data, strategy, trade, risk, watchlist, system, errors) plus a `deprecated/` folder

### Requirement: Shared Asset Location
The system SHALL store all reusable UI components and composable logic under `src/shared/` (not under `src/views/`).

Shared assets are organized as:
- `src/shared/components/` – reusable Vue components (e.g., `KlineChart.vue`, `RiskMetricsPanel.vue`)
- `src/shared/composables/` – reusable Vue composables (e.g., `useMarketData.ts`, `useRiskMonitor.ts`)
- `src/shared/styles/` – shared SCSS files (e.g., `market.scss`, `trading.scss`)

All imports of shared assets SHALL use absolute paths with the `@/shared/` alias.

#### Scenario: Cross-domain component usage
- **WHEN** the Market page needs a K-line chart component
- **THEN** it imports `@/shared/components/KlineChart.vue` (not a relative path)

#### Scenario: Shared composable usage
- **WHEN** multiple domain pages need market data
- **THEN** they all import `@/shared/composables/useMarketData.ts`

#### Scenario: Shared style usage
- **WHEN** a page needs market-specific styling
- **THEN** it imports `@/shared/styles/market.scss` via `@import '@/shared/styles/market.scss'`

## ADDED Requirements

### Requirement: Deprecation Process
The system SHALL move all legacy demo, archive, and example pages to `src/views/deprecated/` and block their routes from the main router.

Deprecated pages are organized as:
- `src/views/deprecated/demo/` – demo pages (e.g., `OpenStockDemo.vue`, `PyprofilingDemo.vue`)
- `src/views/deprecated/archive/` – archived pages (e.g., `converted.archive/*`)
- `src/views/deprecated/examples/` – example pages (e.g., `PageConfigExample.vue`)

Deprecated pages SHALL NOT appear in the main navigation menu or router configuration.

#### Scenario: Accessing a deprecated page via direct URL
- **WHEN** a user navigates to `/demo/openstock` (old URL)
- **THEN** the router redirects to a "Page not found" view or displays a deprecation notice

#### Scenario: Deprecated folder structure
- **WHEN** a developer inspects `src/views/deprecated/`
- **THEN** they see 58 legacy pages organized by category (demo, archive, examples, freqtrade-demo, tdxpy-demo)

### Requirement: Template File Retention
The system SHALL retain `src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue` because it is required by `ArtDecoRiskManagement.vue` (now `src/views/risk/Center.vue`).

The template file SHALL NOT be moved or deleted during the migration.

#### Scenario: Template import in risk domain
- **WHEN** `src/views/risk/Center.vue` is rendered
- **THEN** it successfully imports `../../_templates/ArtDecoPageTemplate.vue` without errors

## REMOVED Requirements

### Requirement: Orphaned Pages in Root Views Directory
The system SHALL NOT contain orphaned Vue page files directly under `src/views/` (root level).

All page files SHALL be organized into domain-specific subdirectories or moved to `deprecated/`.

**Reason**: Orphaned pages at the root level violate the domain-driven architecture and make it unclear which pages are active vs. legacy.

**Migration**: All 44 root-level pages are either:
1. Moved to their corresponding domain folder (e.g., `BacktestAnalysis.vue` → `strategy/Backtest.vue`)
2. Moved to `deprecated/` (e.g., `FreqtradeDemo.vue` → `deprecated/demo/FreqtradeDemo.vue`)

#### Scenario: No orphaned pages after migration
- **WHEN** a developer runs `find src/views -maxdepth 1 -name "*.vue"`
- **THEN** the result is empty (no `.vue` files at the root level)

### Requirement: Shared Assets Under views/shared/
The system SHALL NOT store reusable components or composables under `src/views/shared/`.

All shared assets are moved to `src/shared/` (outside of `views/`).

**Reason**: Storing shared assets under `views/` perpetuates the "page vs. component" boundary blur and violates the separation-of-concerns principle.

**Migration**: All files from `src/views/shared/components/` and `src/views/shared/composables/` are moved to `src/shared/components/` and `src/shared/composables/` respectively.

#### Scenario: No shared assets under views/
- **WHEN** a developer inspects `src/views/shared/`
- **THEN** the directory is empty or does not exist
