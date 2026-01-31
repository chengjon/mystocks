'''
# File-Level API Testing Framework

This directory contains the comprehensive file-level API testing framework for MyStocks. The framework tests API endpoints by file boundaries rather than individual endpoints, providing efficient and maintainable testing for the entire API suite.

## Overview

**Traditional Testing**: 566 individual endpoint tests
**File-Level Testing**: 62 file-based test units (89% reduction)

### Key Features

- **Parallel Execution**: Up to 8 files tested simultaneously
- **Comprehensive Coverage**: All endpoints within a file tested together
- **Contract Validation**: OpenAPI specification compliance
- **Performance Monitoring**: Response time and throughput validation
- **Error Handling**: Consistent error response validation
- **Integration Testing**: Cross-endpoint functionality verification

## Directory Structure

```
tests/file_level/
├── core.py              # Main testing framework and runner
├── fixtures.py          # Test utilities and fixtures
├── conftest.py          # Pytest configuration and shared fixtures
├── run_file_tests.py    # Command-line test runner
├── test_*.py           # Individual file-level test files
├── config/
│   └── test_config.yaml # Test configuration
├── fixtures/            # Test data fixtures
│   └── *.json          # Sample data files
└── reports/            # Generated test reports
```

## Usage

### Running File-Level Tests

```bash
# Run all file-level tests
pytest tests/file_level/ -v

# Run specific file test
pytest tests/file_level/test_market_file_level.py -v

# Run with coverage
pytest tests/file_level/ --cov=web/backend/app --cov-report=html

# Run in parallel
pytest tests/file_level/ -n auto
```

### Command-Line Runner

```bash
# Run file-level tests with custom options
python tests/file_level/run_file_tests.py \
    --api-dir web/backend/app/api \
    --max-workers 4 \
    --format json \
    --verbose

# Generate HTML report
python tests/file_level/run_file_tests.py --format html
```

### Configuration

Edit `tests/file_level/config/test_config.yaml` to configure:

- API base URLs and timeouts
- Database connections
- Parallel execution settings
- File-specific test configurations
- Reporting options

## Test Categories

### 1. Basic Connectivity Tests
Verify that API endpoints are accessible and return proper HTTP status codes.

### 2. Endpoint Functionality Tests
Test core business logic and data processing for each endpoint.

### 3. Integration Tests
Test multiple endpoints working together within a file.

### 4. Error Handling Tests
Verify consistent error responses and proper error handling.

### 5. Performance Tests
Monitor response times and validate performance requirements.

### 6. Contract Compliance Tests
Validate OpenAPI specification compliance and schema validation.

## File Test Structure

Each file-level test follows this pattern:

```python
class Test<ApiFile>FileLevel:
    """File-level tests for <api_file>.py"""

    API_BASE = "/api/<endpoint>"
    FILE_NAME = "<api_file>.py"
    EXPECTED_ENDPOINTS = <count>

    def test_endpoint_functionality(self):
        """Test core endpoint functionality"""

    def test_error_handling(self):
        """Test error scenarios"""

    def test_file_integration(self):
        """Test multiple endpoints together"""

    def test_performance(self):
        """Test response times"""

    def test_contract_compliance(self):
        """Test OpenAPI compliance"""
```

## Test Fixtures

### Shared Fixtures (conftest.py)

- `client`: FastAPI TestClient instance
- `async_client`: Async HTTP client
- `auth_headers`: Authentication headers
- `test_data_factory`: Test data generator
- `performance_tester`: Response time monitor

### File-Specific Fixtures

- `sample_market_data`: Sample market data
- `sample_user_data`: Sample user data
- `bulk_market_data`: Large datasets for testing

## Test Data Management

### Factory Pattern

```python
from tests.file_level.fixtures import TestDataFactory

factory = TestDataFactory()
market_data = factory.create_market_data(symbol="600000")
bulk_data = factory.create_bulk_market_data(["600000", "600519"], count_per_symbol=10)
```

### Fixture Files

Test data stored in JSON files under `fixtures/` directory:

```json
[
  {
    "symbol": "600000",
    "price": 10.50,
    "volume": 1000000,
    "timestamp": "2025-01-10T10:00:00Z"
  }
]
```

## Parallel Execution

The framework supports parallel test execution:

```python
@pytest.fixture
def parallel_runner():
    return ParallelTestRunner(max_workers=4)

async def test_parallel_endpoints(parallel_runner):
    test_functions = [test_endpoint_1, test_endpoint_2, test_endpoint_3]
    results = await parallel_runner.run_tests_parallel(test_functions)
```

## Reporting

### Test Results

Results saved in multiple formats:

- **JSON**: Structured data for CI/CD integration
- **HTML**: Human-readable reports with charts
- **YAML**: Configuration-compatible format

### Coverage Integration

```bash
pytest tests/file_level/ --cov=web/backend/app --cov-report=html:htmlcov
```

## Current Implementation Status

### Phase 1: Foundation Setup ✅
'''

- [x] Test infrastructure setup
- [x] Pytest-based file testing framework
- [x] Test utilities and fixtures
- [x] Test data management
- [x] Configuration system
- [x] Basic test runner

### Phase 2: Core File Testing (In Progress)

#### Priority 0: Contract Files (16 files)
- [x] market.py (13 endpoints) - **COMPLETED**
- [ ] technical_analysis.py (9 endpoints)
- [ ] strategy_management.py (9 endpoints)
- [ ] risk_management.py (36 endpoints)
- [ ] announcement.py (13 endpoints)
- [ ] contract/routes.py (12 endpoints)
- [ ] auth.py (9 endpoints)
- [ ] Remaining 9 contract files

#### Priority 1: Core Business Files (14 files)
- [ ] data.py (29 endpoints)
- [ ] akshare_market.py (34 endpoints)
- [ ] efinance.py (20 endpoints)
- [ ] market_v2.py (13 endpoints)
- [ ] watchlist.py (15 endpoints)
- [ ] cache.py (12 endpoints)
- [ ] Remaining 8 files

## Success Metrics

- **Coverage**: 100% endpoint coverage through file-level tests
- **Efficiency**: 89% reduction in test management complexity
- **Performance**: <30 minutes for full suite execution
- **Quality**: 95%+ test pass rate
- **Maintenance**: 70% reduction in test maintenance effort

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run File-Level API Tests
  run: |
    python tests/file_level/run_file_tests.py \
      --max-workers 4 \
      --format json \
      --verbose

- name: Upload Test Reports
  uses: actions/upload-artifact@v3
  with:
    name: file-level-test-reports
    path: tests/file_level/reports/
```

## Contributing

### Adding New File Tests

1. Create `test_<file>_file_level.py`
2. Follow the test class pattern
3. Add file configuration to `test_config.yaml`
4. Create necessary fixtures
5. Run tests and verify coverage

### Best Practices

- Test endpoints as cohesive units
- Include integration scenarios
- Validate error handling
- Monitor performance
- Ensure contract compliance

## Troubleshooting

### Common Issues

**FastAPI App Not Available**
```
pytest.skip("FastAPI application not available for testing")
```
Solution: Ensure backend app is properly imported

**Database Connection Issues**
```
# Use test database configuration
pytest --tb=short -x
```
Solution: Check database connectivity and configuration

**Parallel Execution Problems**
```
# Reduce workers or disable parallel execution
pytest -n 1 tests/file_level/
```
Solution: Adjust max_workers in configuration

## Future Enhancements

- [ ] AI-assisted test generation
- [ ] Automated contract validation
- [ ] Performance regression detection
- [ ] Load testing integration
- [ ] Test result analytics dashboard</content>
<parameter name="filePath">tests/file_level/README.md
