# api-documentation Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose
Define OpenAPI schema generation and interactive API documentation requirements for the MyStocks backend
service.
## Requirements
### Requirement: OpenAPI Schema Generation

The system SHALL automatically generate OpenAPI/Swagger documentation from FastAPI endpoint definitions.

#### Scenario: Auto-generate OpenAPI Schema
**GIVEN** FastAPI application is running
**WHEN** the `/openapi.json` endpoint is accessed
**THEN** it SHALL return a valid OpenAPI 3.0 schema
**AND** the schema SHALL include all API endpoints with their paths, methods, parameters, and response schemas.

#### Scenario: Schema Contains Complete Endpoint Information
**GIVEN** an API endpoint is defined in the FastAPI application
**WHEN** the OpenAPI schema is generated
**THEN** each endpoint SHALL include:
- HTTP method (GET, POST, PUT, DELETE)
- Path definition
- Operation ID
- Description/docstring
- Request parameters (path, query, body)
- Response schemas for all status codes
- Tag categorization

### Requirement: Swagger UI Accessibility

The system SHALL provide an accessible Swagger UI for interactive API documentation.

#### Scenario: Swagger UI Endpoint
**GIVEN** the backend service is running
**WHEN** accessing `/docs` endpoint
**THEN** it SHALL return a fully functional Swagger UI
**AND** the UI SHALL display all API endpoints
**AND** users SHALL be able to test endpoints directly from the UI.

#### Scenario: ReDoc Alternative Documentation
**GIVEN** the backend service is running
**WHEN** accessing `/redoc` endpoint
**THEN** it SHALL return an alternative API documentation using ReDoc
**AND** the ReDoc interface SHALL display the same OpenAPI schema information.

### Requirement: API Documentation Completeness

All API endpoints SHALL have complete and accurate documentation.

#### Scenario: Authentication Endpoints Documentation
**GIVEN** the authentication endpoints exist in the system
**WHEN** viewing the API documentation
**THEN** the following endpoints SHALL be documented:
- POST `/api/v1/auth/login` - User login with credentials
- POST `/api/v1/auth/logout` - User logout
- GET `/api/v1/auth/me` - Get current user information

#### Scenario: Market Data Endpoints Documentation
**GIVEN** the market data endpoints exist in the system
**WHEN** viewing the API documentation
**THEN** the following endpoints SHALL be documented:
- GET `/api/v1/market/symbols` - Get stock list
- GET `/api/v1/market/kline` - Get K-line data
- GET `/api/v1/market/realtime` - Get realtime market data

#### Scenario: Strategy Management Endpoints Documentation
**GIVEN** the strategy management endpoints exist in the system
**WHEN** viewing the API documentation
**THEN** the following endpoints SHALL be documented:
- GET `/api/v1/strategies` - List all strategies
- POST `/api/v1/strategies` - Create new strategy
- GET `/api/v1/strategies/{id}` - Get strategy details
- PUT `/api/v1/strategies/{id}` - Update strategy
- DELETE `/api/v1/strategies/{id}` - Delete strategy

#### Scenario: Backtest Endpoints Documentation
**GIVEN** the backtest endpoints exist in the system
**WHEN** viewing the API documentation
**THEN** the following endpoints SHALL be documented:
- POST `/api/v1/backtests` - Create new backtest
- GET `/api/v1/backtests/{id}` - Get backtest results
- GET `/api/v1/backtests/{id}/trades` - Get backtest trade records

#### Scenario: System Monitoring Endpoints Documentation
**GIVEN** the system monitoring endpoints exist in the system
**WHEN** viewing the API documentation
**THEN** the following endpoints SHALL be documented:
- GET `/health` - Health check endpoint
- GET `/metrics` - Prometheus metrics endpoint
- GET `/api/v1/system/status` - System status information

### Requirement: API Documentation Index

The system SHALL provide a comprehensive API documentation index.

#### Scenario: API Index File
**GIVEN** API documentation is complete
**WHEN** accessing `docs/api/API_INDEX.md`
**THEN** it SHALL contain:
- Links to all API endpoint documentation
- Description of each API group (Authentication, Market Data, Strategies, etc.)
- Request/response examples for each endpoint
- Error code reference links

### Requirement: Data Model Documentation

The system SHALL provide complete documentation for all data models.

#### Scenario: Data Models Documentation
**GIVEN** Pydantic models are defined in the system
**WHEN** viewing the data model documentation
**THEN** `docs/api/DATA_MODELS.md` SHALL include:
- All request/response DTO models
- Field definitions with types and descriptions
- Validation rules and constraints
- Example values for each field

### Requirement: Error Code Reference

The system SHALL provide a comprehensive error code reference.

#### Scenario: Error Code Documentation
**GIVEN** error codes are defined in the system
**WHEN** viewing the error code reference
**THEN** `docs/api/ERROR_CODES.md` SHALL include:
- All error codes with their meanings
- HTTP status code mapping
- Suggested user actions for each error
- Troubleshooting steps for common errors

### Requirement: Control-Plane OpenAPI Documentation Must Be Stabilized Through Evidence

Control-plane OpenAPI documentation SHALL use current route, schema, and probe
consumer evidence before documentation, probe, schema exposure, or runtime route
changes are authorized.

#### Scenario: Control-plane docs proposal records current evidence

- **WHEN** a control-plane OpenAPI documentation lane is proposed
- **THEN** the proposal SHALL record runtime route count, OpenAPI path count,
  broad control/status candidate count, schema-exposed and hidden route counts,
  duplicate operationId count, probe consumer matrix scope, captured git head,
  and stale-if-head-mismatch policy.

#### Scenario: Health and readiness taxonomy is explicit

- **WHEN** health or readiness endpoints are documented
- **THEN** the documentation packet SHALL distinguish platform liveness,
  canonical readiness, compatibility readiness, service health, detailed
  diagnostics, intentionally absent readiness aliases, and business-domain
  health/status endpoints.

#### Scenario: Metrics and docs schema surfaces are classified separately

- **WHEN** metrics, docs UI, OpenAPI schema, or runtime-only compatibility
  endpoints are documented
- **THEN** the documentation packet SHALL distinguish metrics scrape surfaces,
  docs UI routes, schema retrieval routes, business API operations, and
  runtime-only hidden compatibility routes.

#### Scenario: Runtime route existence is not schema exposure

- **WHEN** a route exists at runtime but is hidden from OpenAPI operation schema
- **THEN** the documentation packet SHALL record runtime existence and
  `include_in_schema` state as separate facts before any exposure change is
  proposed.

#### Scenario: Proposal-only control-plane docs work remains locked

- **WHEN** a control-plane OpenAPI documentation change is in proposal or
  evidence-only state
- **THEN** it SHALL NOT authorize backend source edits, frontend source edits,
  tests, generated client changes, docs/API edits, route path changes, router
  registration changes, operationId changes, response contract changes, probe
  URL changes, PM2 workflow execution, or `include_in_schema` changes.
