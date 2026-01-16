# web-frontend-navigation Specification

## ADDED Requirements

### Requirement: Dynamic sidebar displays correct menu items for each module

The system SHALL provide a dynamic sidebar that updates its menu items based on the currently active module.

#### Scenario: Market module sidebar shows 8 specific submenu items
**GIVEN** user clicks on "市场行情" module tab
**WHEN** the sidebar updates
**THEN** exactly 8 submenu items should be displayed:
- ⚡ 实时行情监控
- 📊 技术指标分析
- 📡 通达信接口行情
- 💰 资金流向分析
- 🏷️ ETF行情
- 💡 概念行情分析
- ⏰ 竞价抢筹分析
- 🏆 龙虎榜分析

#### Scenario: Stocks module sidebar shows 6 specific submenu items
**GIVEN** user clicks on "股票管理" module tab
**WHEN** the sidebar updates
**THEN** exactly 6 submenu items should be displayed:
- ⭐ 自选股管理
- 📈 投资组合
- 📋 交易活动
- 🔍 股票筛选器
- 🏭 行业股票池
- 💡 概念股票池

### Requirement: URL routing supports nested module structure

The system SHALL support nested routing structure where each module has its own route group with child routes.

#### Scenario: Direct URL navigation works correctly
**GIVEN** user navigates using direct URLs like `/market/realtime` or `/stocks/watchlist`
**WHEN** the URL is entered
**THEN** the correct module tab should be activated
**AND** the correct submenu item should be highlighted
**AND** the corresponding page component should load

#### Scenario: Navigation state persists across page refreshes
**GIVEN** user has navigated to a specific module and submenu
**WHEN** the page is refreshed
**THEN** the same module tab should remain active
**AND** the same submenu item should remain highlighted
**AND** the same page content should be displayed

### Requirement: Vue Router configuration supports nested routes

The system SHALL use Vue Router 4.x with nested route configuration for proper module organization.

#### Scenario: Route guards handle module switching
**GIVEN** user navigates between different modules
**WHEN** route changes occur
**THEN** navigation state should update automatically
**AND** sidebar should reflect current module
**AND** no manual state synchronization should be required

### Requirement: Menu configuration is centralized and maintainable

The system SHALL maintain menu configuration in a centralized, easily maintainable format.

#### Scenario: Menu changes are made in single location
**GIVEN** menu items need to be modified
**WHEN** changes are required
**THEN** changes should be made in a single configuration file
**AND** all modules should use the same configuration pattern
**AND** menu items should include path, label, icon, and description