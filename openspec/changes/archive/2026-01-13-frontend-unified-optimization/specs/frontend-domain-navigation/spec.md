## ADDED Requirements

### Requirement: Domain-Driven Navigation System
The system SHALL provide a domain-driven navigation architecture that organizes the application into logical functional domains with dynamic sidebar content.

#### Scenario: Domain switching updates navigation
- **WHEN** user switches between Market, Selection, Strategy, Trading, Risk, and Settings domains
- **THEN** the sidebar menu content SHALL update to show domain-specific pages
- **AND** the breadcrumb navigation SHALL reflect the current domain context
- **AND** the URL SHALL follow semantic patterns (/market/list, /selection/watchlist)

#### Scenario: Navigation maintains state across domains
- **WHEN** user navigates between domains
- **THEN** the active domain state SHALL be preserved
- **AND** the sidebar collapse/expand state SHALL be maintained
- **AND** recent navigation history SHALL be available

### Requirement: Dynamic Sidebar Component
The system SHALL implement a dynamic sidebar that adapts its content based on the active functional domain.

#### Scenario: Market domain sidebar displays 8 pages
- **WHEN** Market domain is active
- **THEN** sidebar SHALL display: Real-time Quotes, Technical Analysis, TDX Integration, Capital Flow, ETF Market, Concept Analysis, Auction Analysis, LHB Analysis
- **AND** each menu item SHALL have appropriate icons and labels
- **AND** menu items SHALL be clickable and navigate to correct pages

#### Scenario: Selection domain sidebar displays 6 pages
- **WHEN** Selection domain is active
- **THEN** sidebar SHALL display: Watchlist Management, Portfolio Management, Trading Activity, Stock Screener, Industry Stocks, Concept Stocks
- **AND** menu SHALL support search and filtering
- **AND** menu SHALL show item counts/badges where applicable

### Requirement: Command Palette Navigation
The system SHALL provide a keyboard-driven command palette for rapid navigation and actions.

#### Scenario: Command palette activation
- **WHEN** user presses Ctrl+K (or Cmd+K on Mac)
- **THEN** command palette SHALL open with input focus
- **AND** SHALL display recent commands and available actions
- **AND** SHALL support fuzzy search across all commands

#### Scenario: Command execution
- **WHEN** user selects a command from palette
- **THEN** the corresponding action SHALL execute
- **AND** navigation commands SHALL change the active page/domain
- **AND** palette SHALL close after successful execution

### Requirement: Responsive Navigation Design
The system SHALL provide responsive navigation that works across all device sizes from 320px to 4K.

#### Scenario: Mobile navigation (320px-767px)
- **WHEN** viewport width is ≤767px
- **THEN** sidebar SHALL collapse to hamburger menu
- **AND** domain switching SHALL use bottom tab navigation
- **AND** touch targets SHALL be minimum 44px

#### Scenario: Desktop navigation (768px-4K)
- **WHEN** viewport width is ≥768px
- **THEN** sidebar SHALL be fully visible and collapsible
- **AND** domain switching SHALL use top navigation bar
- **AND** SHALL support multi-column layouts</content>
<parameter name="filePath">openspec/changes/frontend-unified-optimization/specs/frontend-domain-navigation/spec.md