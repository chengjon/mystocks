## MODIFIED Requirements

### Requirement: OpenAPI Schema Generation

The system SHALL automatically generate OpenAPI/Swagger documentation from FastAPI endpoint definitions with integrated contract validation capabilities.

#### Scenario: Auto-generate OpenAPI Schema with Contract Validation
**GIVEN** FastAPI application is running
**WHEN** the `/openapi.json` endpoint is accessed
**THEN** it SHALL return a valid OpenAPI 3.0 schema
**AND** the schema SHALL include all API endpoints with their paths, methods, parameters, and response schemas
**AND** the schema SHALL be validated against contract requirements before generation

#### Scenario: Contract-Validated Schema Generation
**GIVEN** an API endpoint is defined in the FastAPI application
**WHEN** the OpenAPI schema is generated
**THEN** each endpoint SHALL include:
- HTTP method (GET, POST, PUT, DELETE)
- Path definition with contract validation
- Operation ID linked to contract requirements
- Description/docstring from contract specifications
- Request parameters (path, query, body) with contract validation
- Response schemas for all status codes validated against contracts
- Tag categorization aligned with contract groupings

### Requirement: API Documentation Completeness

All API endpoints SHALL have complete and accurate documentation with contract validation integration.

#### Scenario: Contract-Validated Authentication Endpoints
**GIVEN** the authentication endpoints exist in the system
**WHEN** viewing the API documentation
**THEN** the following endpoints SHALL be documented and contract-validated:
- POST `/api/v1/auth/login` - User login with credentials (validated against auth contract)
- POST `/api/v1/auth/logout` - User logout (validated against auth contract)
- GET `/api/v1/auth/me` - Get current user information (validated against auth contract)

#### Scenario: Contract-Validated Market Data Endpoints
**GIVEN** the market data endpoints exist in the system
**WHEN** viewing the API documentation
**THEN** the following endpoints SHALL be documented and contract-validated:
- GET `/api/v1/market/symbols` - Get stock list (validated against market data contract)
- GET `/api/v1/market/kline` - Get K-line data (validated against market data contract)
- GET `/api/v1/market/realtime` - Get realtime market data (validated against market data contract)

## ADDED Requirements

### Requirement: Contract Validation Integration

The API documentation system SHALL integrate with contract validation to ensure documentation accuracy and compliance.

#### Scenario: Documentation Validation Against Contracts
**GIVEN** API documentation is generated
**WHEN** the documentation build process runs
**THEN** all documented endpoints SHALL be validated against their corresponding contracts
**AND** any discrepancies SHALL be reported as build failures

#### Scenario: Contract Drift Detection in Documentation
**GIVEN** contracts are updated
**WHEN** the documentation is next generated
**THEN** the system SHALL detect contract drift
**AND** flag outdated documentation for review

### Requirement: Runtime Contract Validation Documentation

The system SHALL provide comprehensive documentation for runtime contract validation features.

#### Scenario: Runtime Validation Developer Guide
**GIVEN** runtime contract validation is implemented
**WHEN** developers need to understand validation features
**THEN** `docs/api/RUNTIME_CONTRACT_VALIDATION.md` SHALL exist
**AND** it SHALL include:
- How to enable/disable validation per environment
- Configuration options for validation strictness
- Error handling and reporting mechanisms
- Performance impact considerations