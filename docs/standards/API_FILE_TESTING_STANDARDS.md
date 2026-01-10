# API File-Level Testing Standards

## Overview

This document defines the testing standards and criteria for file-level API testing in MyStocks.
File-level testing groups 566 API endpoints into 62 logical test units, reducing complexity by 89%
while maintaining 100% endpoint coverage.

## Test Categories and Priorities

### P0: Contract-Managed Files (16 files, 100% coverage required)
**Files**: market.py, trade/routes.py, technical_analysis.py, strategy_management.py,
         risk_management.py, announcement.py, contract/routes.py, auth.py,
         data.py, akshare_market.py, efinance.py, market_v2.py, strategy_mgmt.py,
         strategy.py, technical/routes.py

**Testing Requirements**:
- ✅ 100% functional endpoint coverage
- ✅ OpenAPI contract validation
- ✅ Response schema compliance
- ✅ Version compatibility testing
- ✅ Integration testing with dependent modules

**Pass Criteria**:
- All endpoints return expected response formats
- Contract validation passes without errors
- Response schemas match OpenAPI specifications
- No breaking changes introduced

### P1: Core Business Files (14 files, 90% coverage required)
**Files**: monitoring.py, signal_monitoring.py, gpu_monitoring.py, prometheus_exporter.py,
         notification.py, watchlist.py, backup_recovery.py, data_quality.py,
         data_lineage.py, cache.py, websocket.py, sse_endpoints.py,
         backtest_ws.py, realtime_market.py

**Testing Requirements**:
- ✅ 90% functional endpoint coverage
- ✅ Integration testing with core systems
- ✅ Error handling validation
- ✅ Performance baseline testing

**Pass Criteria**:
- Core business logic functions correctly
- Integration with other modules works
- Error scenarios handled appropriately
- Performance within acceptable limits

### P2: Utility Files (32 files, 70% coverage required)
**Files**: All remaining API files including system management, external integrations, etc.

**Testing Requirements**:
- ✅ 70% functional endpoint coverage
- ✅ Smoke testing for basic functionality
- ✅ Configuration validation
- ✅ Basic error handling

**Pass Criteria**:
- Basic functionality works
- No critical errors in normal operation
- Configuration is valid
- System remains stable

## Test Execution Standards

### Test Environment Requirements

#### Infrastructure Setup
- **Database**: Isolated PostgreSQL test instance per file
- **Cache**: Dedicated Redis instance for each test file
- **External Services**: Mocked or isolated external API calls
- **File Isolation**: Test data and fixtures isolated per file

#### Test Data Management
- **Isolation**: Each file test uses dedicated data set
- **Cleanup**: Automatic cleanup after test completion
- **Versioning**: Test data tied to API contract versions
- **Mock Integration**: Seamless fallback to mock data

### Test Case Standards

#### Functional Testing
```python
# Required test structure for each endpoint
def test_endpoint_functionality():
    """Test basic functionality of endpoint"""
    # Arrange
    setup_test_data()

    # Act
    response = call_endpoint()

    # Assert
    assert response.status_code == 200
    assert response.data matches expected_schema
```

#### Contract Validation
```python
# Required for P0 files
def test_contract_compliance():
    """Validate OpenAPI contract compliance"""
    # Load contract specification
    spec = load_openapi_spec()

    # Validate implementation
    validator = ContractValidator(spec)
    assert validator.validate_endpoint(endpoint)
    assert validator.validate_response_schema(response)
```

#### Error Handling
```python
# Required for all files
def test_error_handling():
    """Test error scenarios and handling"""
    # Test invalid inputs
    assert invalid_input_returns_proper_error()

    # Test system errors
    assert system_error_returns_500_status()

    # Test timeout scenarios
    assert timeout_returns_proper_response()
```

#### Performance Testing
```python
# Required for P0 and P1 files
def test_performance_requirements():
    """Validate performance meets requirements"""
    # Response time within limits
    assert response_time < MAX_RESPONSE_TIME

    # Concurrent request handling
    assert concurrent_requests_handled_properly()

    # Memory usage acceptable
    assert memory_usage < MAX_MEMORY_USAGE
```

### Test Reporting Standards

#### Success Metrics
- **P0 Files**: 100% pass rate, 0 contract violations
- **P1 Files**: ≥95% pass rate, all critical functionality working
- **P2 Files**: ≥90% pass rate, no critical failures

#### Coverage Requirements
- **P0 Files**: 100% endpoint coverage, 100% contract validation
- **P1 Files**: 90% endpoint coverage, integration tests passing
- **P2 Files**: 70% endpoint coverage, smoke tests passing

#### Quality Gates
- **Unit Test Coverage**: ≥80% for P0 files, ≥70% for P1 files, ≥50% for P2 files
- **Contract Compliance**: 100% for P0 files
- **Error Rate**: <5% acceptable error rate
- **Performance**: Within defined SLAs

## Implementation Guidelines

### Test File Organization
```
tests/api/file_tests/
├── __init__.py              # Core testing framework
├── conftest.py              # Pytest fixtures and configuration
├── run_file_tests.py        # CLI test runner
├── test_{file}.py           # Individual file test modules
├── fixtures/                # Test data fixtures
├── reports/                 # Test result storage
└── config/                  # Test configuration files
```

### Test Naming Conventions
```python
# File-level test modules
test_{api_file}.py

# Test method naming
test_{endpoint}_{scenario}()
test_contract_compliance()
test_error_handling()
test_performance_requirements()
```

### Test Data Management
```python
# Fixture usage
@pytest.fixture
def api_test_fixtures():
    """Common API test configuration"""
    return {
        "base_url": "http://localhost:8000",
        "timeout": 30,
        "retries": 3
    }

@pytest.fixture
def mock_responses():
    """Mock API response data"""
    return {
        "success": {"status": "ok", "data": {...}},
        "error": {"status": "error", "message": "..."}
    }
```

## CI/CD Integration

### Automated Testing Pipeline
- **Trigger**: API file changes or scheduled runs
- **Parallel Execution**: Up to 8 files tested simultaneously
- **Result Aggregation**: Comprehensive test reporting
- **Quality Gates**: Block deployment on critical failures

### Test Result Integration
- **PR Comments**: Automatic test result comments on pull requests
- **Dashboard**: Real-time test status dashboard
- **Alerts**: Failure notifications to development team
- **Reports**: Detailed HTML/JSON test reports

## Maintenance and Evolution

### Test Suite Updates
- **API Changes**: Tests updated when API contracts change
- **New Endpoints**: Test cases added for new functionality
- **Bug Fixes**: Regression tests added for fixed issues
- **Performance**: Benchmarks updated as system evolves

### Quality Monitoring
- **Trend Analysis**: Track test pass rates over time
- **Coverage Monitoring**: Ensure coverage requirements maintained
- **Performance Tracking**: Monitor test execution times
- **Flakiness Detection**: Identify and fix flaky tests

## Compliance and Standards

### OpenAPI Contract Compliance
- **P0 Files**: Must pass 100% contract validation
- **Schema Validation**: Response schemas must match specifications
- **Version Compatibility**: API versioning must be maintained
- **Documentation Sync**: OpenAPI docs must reflect implementation

### Code Quality Standards
- **Test Code Coverage**: Tests themselves must be well-tested
- **Documentation**: All tests must have clear documentation
- **Maintainability**: Test code must be easy to understand and modify
- **Performance**: Tests must execute within reasonable time limits

## Troubleshooting Guide

### Common Issues and Solutions

#### Test Isolation Problems
**Symptoms**: Tests interfere with each other
**Solutions**:
- Use dedicated database schemas per test file
- Implement proper fixture cleanup
- Avoid shared state between tests

#### Contract Validation Failures
**Symptoms**: Contract validation errors
**Solutions**:
- Update OpenAPI specifications to match implementation
- Fix response schema mismatches
- Update contract versions for breaking changes

#### Performance Test Failures
**Symptoms**: Tests exceed time limits
**Solutions**:
- Optimize test data loading
- Implement parallel test execution
- Review and optimize endpoint performance

#### Flaky Test Issues
**Symptoms**: Tests pass/fail inconsistently
**Solutions**:
- Implement proper test data isolation
- Use deterministic test data
- Avoid timing-dependent assertions