## ADDED Requirements

### Requirement: API Router Aggregation

The system SHALL provide a unified API router that aggregates all domain-specific routers.

#### Scenario: Router aggregation
- **WHEN** the application starts
- **THEN** all domain routers SHALL be aggregated into a main router
- **AND** the main router SHALL be mounted at the API base path

#### Scenario: Domain router registration
- **WHEN** registering domain routers
- **THEN** each domain router SHALL have a unique prefix
- **AND** domain routers SHALL be self-contained

### Requirement: Service Layer Separation

The system SHALL separate business logic from API handling.

#### Scenario: Service creation
- **WHEN** implementing business logic
- **THEN** a new service class or module SHALL be created
- **AND** the service SHALL be placed in the `services/` directory

#### Scenario: Service invocation from API
- **WHEN** an API endpoint needs business logic
- **THEN** it SHALL invoke a service method
- **AND** the API endpoint SHALL NOT contain business logic

#### Scenario: Service independence
- **WHEN** testing business logic
- **THEN** services SHALL be testable without API layer
- **AND** services SHALL NOT import API modules

### Requirement: Model Layer Purity

The system SHALL maintain pure data models without business logic.

#### Scenario: Model definition
- **WHEN** defining Pydantic models
- **THEN** models SHALL only contain data structure definitions
- **AND** models SHALL NOT contain methods that implement business logic

#### Scenario: Model usage
- **WHEN** services need data structures
- **THEN** they SHALL use Pydantic models
- **AND** models MAY be imported by services

## MODIFIED Requirements

### Requirement: API Endpoint Organization

API endpoints SHALL be organized by business domain.

#### Scenario: System domain endpoints
- **WHEN** creating system-related endpoints
- **THEN** they SHALL be organized under `/api/v1/system/`
- **AND** include health and routing endpoints

#### Scenario: Strategy domain endpoints
- **WHEN** creating strategy-related endpoints
- **THEN** they SHALL be organized under `/api/v1/strategy/`
- **AND** include ML strategy and technical indicator endpoints

#### Scenario: Trading domain endpoints
- **WHEN** creating trading-related endpoints
- **THEN** they SHALL be organized under `/api/v1/trading/`
- **AND** include session and positions endpoints

#### Scenario: Admin domain endpoints
- **WHEN** creating admin-related endpoints
- **THEN** they SHALL be organized under `/api/v1/admin/`
- **AND** include auth, audit, and optimization endpoints

#### Scenario: Analysis domain endpoints
- **WHEN** creating analysis-related endpoints
- **THEN** they SHALL be organized under `/api/v1/analysis/`
- **AND** include sentiment, backtest, and stress test endpoints

## REMOVED Requirements

### Requirement: Monolithic API File

The previous monolithic API file (`mystocks_complete.py`) is REMOVED.

**Reason**: A single file containing all API endpoints is not maintainable and violates single responsibility principle.

**Migration**: The monolithic file SHALL be split into domain-specific API modules. All endpoints SHALL be preserved with their existing paths and behaviors.
