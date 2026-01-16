## ADDED Requirements

### Requirement: Test File Splitting

Test files exceeding 1000 lines SHALL be split into focused test modules.

#### Scenario: Test file organization by feature
- **WHEN** a test file exceeds 1000 lines
- **THEN** it SHALL be split by feature or functionality
- **AND** each test file SHALL focus on a single aspect

#### Scenario: Test file naming
- **WHEN** splitting test files
- **THEN** new test files SHALL have descriptive names
- **AND** naming SHALL follow the pattern `test_<feature>_<aspect>.py`

#### Scenario: Test fixtures organization
- **WHEN** multiple tests share fixtures
- **THEN** fixtures SHALL be moved to dedicated fixture files
- **AND** fixture files SHALL be placed in a `fixtures/` subdirectory

### Requirement: Testability of Split Modules

Split modules SHALL maintain or improve testability.

#### Scenario: Service layer testing
- **WHEN** business logic is moved to services
- **THEN** services SHALL be testable without API layer
- **AND** services SHALL have unit tests with mocking

#### Scenario: Component testing
- **WHEN** Vue components are split
- **THEN** each child component SHALL be independently testable
- **AND** composables SHALL have unit tests

#### Scenario: API endpoint testing
- **WHEN** API endpoints are organized by domain
- **THEN** domain-specific API tests SHALL be created
- **AND** API tests SHALL verify contract compliance

### Requirement: Test Coverage for Split Files

Split files SHALL maintain appropriate test coverage.

#### Scenario: Minimum coverage for new modules
- **WHEN** new modules are created from split files
- **THEN** they SHALL achieve at least 80% test coverage
- **AND** critical paths SHALL have 100% coverage

#### Scenario: Coverage tracking
- **WHEN** running test coverage
- **THEN** coverage SHALL be tracked per module
- **AND** coverage drops SHALL be investigated

## MODIFIED Requirements

### Requirement: Test File Size Limits

Test files SHALL have maximum size limits for maintainability.

#### Scenario: Maximum test file size
- **WHEN** a test file exceeds 1000 lines
- **THEN** it SHALL be considered for splitting
- **AND** the splitting plan SHALL be documented

#### Scenario: Optimal test file size
- **WHEN** creating new test files
- **THEN** target size SHALL be 300-500 lines
- **AND** each test file SHALL test a single concern

### Requirement: Test Organization

Tests SHALL be organized by the code they test.

#### Scenario: Backend test organization
- **WHEN** organizing backend tests
- **THEN** they SHALL mirror the source code structure
- **AND** tests for `services/foo.py` SHALL be in `tests/services/test_foo.py`

#### Scenario: Frontend test organization
- **WHEN** organizing frontend tests
- **THEN** they SHALL be placed alongside the component
- **OR** in a dedicated `tests/` directory with mirror structure

## REMOVED Requirements

### Requirement: Monolithic Test Files

Large monolithic test files (exceeding 1500 lines) are REMOVED.

**Reason**: Monolithic test files are difficult to navigate and maintain, leading to reduced test quality.

**Migration**: Each monolithic test file SHALL be split into:
- Feature-specific test modules
- Shared fixture files
- Helper utility modules
