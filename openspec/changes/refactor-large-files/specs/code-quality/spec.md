## MODIFIED Requirements

### Requirement: File Size Limits

The codebase SHALL enforce maximum file size limits to maintain code quality and maintainability.

#### Scenario: Python file size limit
- **WHEN** a Python file exceeds 500 lines
- **THEN** the file SHALL be considered for refactoring
- **AND** the development team SHOULD create a plan to split the file

#### Scenario: Vue file size limit
- **WHEN** a Vue file exceeds 500 lines
- **THEN** the file SHALL be considered for component splitting
- **AND** the template, script, and style sections SHOULD be analyzed for independent components

#### Scenario: TypeScript file size limit
- **WHEN** a TypeScript file exceeds 500 lines of type definitions
- **THEN** the file SHALL be split into multiple files by domain
- **AND** an index.ts file SHALL provide unified exports

### Requirement: Single Responsibility Principle

Each module, class, and function SHALL have a single, well-defined responsibility.

#### Scenario: API layer separation
- **WHEN** creating API endpoints
- **THEN** the API layer SHALL only handle request/response parsing
- **AND** business logic SHALL be delegated to service layers

#### Scenario: Service layer separation
- **WHEN** implementing business logic
- **THEN** services SHALL not depend on API layer
- **AND** services MAY depend on models and utilities

#### Scenario: Model layer purity
- **WHEN** defining data models
- **THEN** models SHALL only contain data structures
- **AND** models SHALL NOT contain business logic

## ADDED Requirements

### Requirement: Domain-Based API Organization

The backend API SHALL be organized by business domain rather than development phase.

#### Scenario: Domain-based directory structure
- **WHEN** organizing API files
- **THEN** directories SHALL use domain names (system, strategy, trading, admin, analysis)
- **AND** directories SHALL NOT use phase numbers (phase1, phase2, etc.)

#### Scenario: System domain
- **WHEN** creating system-related APIs
- **THEN** they SHALL be placed in the `api/v1/system/` directory
- **AND** include health checks and routing management

#### Scenario: Strategy domain
- **WHEN** creating strategy-related APIs
- **THEN** they SHALL be placed in the `api/v1/strategy/` directory
- **AND** include ML strategy and technical indicators

#### Scenario: Trading domain
- **WHEN** creating trading-related APIs
- **THEN** they SHALL be placed in the `api/v1/trading/` directory
- **AND** include session management and positions

#### Scenario: Admin domain
- **WHEN** creating admin-related APIs
- **THEN** they SHALL be placed in the `api/v1/admin/` directory
- **AND** include authentication, audit, and optimization

#### Scenario: Analysis domain
- **WHEN** creating analysis-related APIs
- **THEN** they SHALL be placed in the `api/v1/analysis/` directory
- **AND** include sentiment, backtest, and stress test

### Requirement: Vue Component Splitting

Vue components exceeding 500 lines SHALL be split into smaller, focused components.

#### Scenario: Component template splitting
- **WHEN** a Vue template exceeds 200 lines
- **THEN** the template SHOULD be analyzed for extractable components
- **AND** each component SHALL have a single responsibility

#### Scenario: Component script splitting
- **WHEN** Vue script setup exceeds 200 lines
- **THEN** logic SHOULD be extracted to composables
- **AND** API calls SHOULD be moved to dedicated API files

#### Scenario: Component style splitting
- **WHEN** component styles exceed 100 lines
- **THEN** shared styles SHOULD be moved to global SCSS files
- **AND** component-specific styles SHALL use scoped CSS

### Requirement: Dependency Direction

Code dependencies SHALL follow a strict direction from high-level to low-level modules.

#### Scenario: API depends on Services
- **WHEN** implementing API endpoints
- **THEN** the API module MAY import service modules
- **AND** the API module SHALL NOT be imported by service modules

#### Scenario: Services depend on Models
- **WHEN** implementing services
- **THEN** service modules MAY import model modules
- **AND** service modules SHALL NOT be imported by model modules

#### Scenario: Circular dependency prevention
- **WHEN** two modules require each other's functionality
- **THEN** a third common module SHALL be created
- **OR** local imports (within functions) SHALL be used as a last resort

## REMOVED Requirements

### Requirement: Phase-Based API Organization

The previous requirement for organizing APIs by development phase is REMOVED.

**Reason**: Phase-based organization does not reflect business domains and causes confusion for new developers.

**Migration**: All phase-based directories (phase1, phase2, phase3, phase4, phase5) SHALL be migrated to domain-based directories (system, strategy, trading, admin, analysis).
