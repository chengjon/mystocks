# API Compliance Testing Framework

## Overview

This comprehensive automated testing framework enforces API development guidelines and ensures continuous compliance with REST API standards. The framework validates code quality, documentation completeness, performance standards, and security requirements.

## Features

### 1. API Compliance Tests
- **Response Format Compliance**: Validates unified API response structure
- **Authentication Requirements**: Ensures protected endpoints require JWT authentication
- **Parameter Validation**: Checks Pydantic model validation completeness
- **HTTP Method Semantics**: Validates proper REST API design principles
- **Status Code Correctness**: Ensures appropriate HTTP status codes
- **REST API Design**: Validates resource naming and URL structure

### 2. Static Code Analysis
- **Docstring Documentation**: Ensures complete function documentation
- **Pydantic Model Validation**: Checks models include examples
- **Error Handling Patterns**: Validates proper error handling
- **Import Organization**: Ensures clean import statements
- **Type Annotations**: Verifies complete type hints
- **Security Vulnerability Detection**: Scans for common security issues

### 3. API Documentation Validation
- **OpenAPI Schema Completeness**: Validates Swagger/OpenAPI documentation
- **Endpoint Descriptions**: Ensures all endpoints have proper documentation
- **Request/Response Examples**: Validates example completeness
- **Authentication Documentation**: Checks security scheme documentation
- **Error Response Documentation**: Validates error response examples

### 4. Performance and Security Tests
- **Response Time Benchmarks**: Measures API endpoint performance
- **SQL Injection Detection**: Tests for SQL injection vulnerabilities
- **XSS Protection**: Validates cross-site scripting protection
- **Rate Limiting**: Verifies rate limiting functionality
- **Input Validation**: Tests input sanitization and validation

### 5. CI/CD Integration
- **GitHub Actions Workflow**: Automated testing in CI/CD pipeline
- **Pre-commit Hooks**: Local development validation
- **Automated Reporting**: Compliance status reporting
- **Badge Generation**: Visual compliance indicators

## Quick Start

### Prerequisites

- Python 3.9+
- FastAPI application
- PostgreSQL database (for testing)
- Required dependencies (see requirements.txt)

### Installation

1. **Install Dependencies**:
```bash
cd web/backend
pip install -r requirements.txt
pip install pytest pytest-cov pytest-html pytest-json-report
```

2. **Set Up Environment**:
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - POSTGRESQL_PASSWORD
# - JWT_SECRET_KEY
```

3. **Run All Tests**:
```bash
# Run comprehensive test suite
python -m pytest tests/test_api_compliance.py tests/test_static_code_analysis.py tests/test_api_documentation_validation.py tests/test_performance_and_security.py -v

# Or run individual test suites
python -m pytest tests/test_api_compliance.py -v
python -m pytest tests/test_static_code_analysis.py -v
python -m pytest tests/test_api_documentation_validation.py -v
python -m pytest tests/test_performance_and_security.py -v
```

## Test Suites

### 1. API Compliance Tests (`test_api_compliance.py`)

**Purpose**: Validates that all API endpoints follow unified response format and authentication requirements.

**Key Validations**:
- Response structure compliance (success/error format)
- JWT authentication for protected endpoints
- Parameter validation completeness
- HTTP method semantics
- Status code correctness

**Example Usage**:
```python
from tests.test_api_compliance import APIComplianceValidator

# Create validator
validator = APIComplianceValidator(test_client)

# Run comprehensive validation
results = validator.run_comprehensive_validation()

# Generate report
report = validator.generate_report()
print(report)
```

### 2. Static Code Analysis Tests (`test_static_code_analysis.py`)

**Purpose**: Analyzes source code for quality, security, and documentation compliance.

**Key Validations**:
- Security vulnerability detection (hardcoded secrets, SQL injection)
- Docstring completeness
- Type annotation coverage
- Import organization
- Code complexity analysis

**Example Usage**:
```python
from tests.test_static_code_analysis import StaticCodeAnalyzer

# Create analyzer
analyzer = StaticCodeAnalyzer()

# Analyze API directory
results = analyzer.analyze_api_directory()

# Generate report
report = analyzer.generate_report()
print(report)
```

### 3. API Documentation Validation Tests (`test_api_documentation_validation.py`)

**Purpose**: Validates OpenAPI/Swagger documentation completeness and accuracy.

**Key Validations**:
- OpenAPI schema completeness
- Endpoint documentation coverage
- Request/response examples
- Authentication scheme documentation
- Error response documentation

**Example Usage**:
```python
from tests.test_api_documentation_validation import APIDocumentationValidator

# Create validator
validator = APIDocumentationValidator(test_client)

# Run comprehensive validation
results = validator.run_comprehensive_validation()

# Generate report
report = validator.generate_report()
print(report)
```

### 4. Performance and Security Tests (`test_performance_and_security.py`)

**Purpose**: Validates API performance and security standards.

**Key Validations**:
- Response time benchmarks
- SQL injection vulnerability detection
- XSS protection validation
- Rate limiting verification
- Input sanitization checks

**Example Usage**:
```python
from tests.test_performance_and_security import PerformanceSecurityValidator

# Create validator
validator = PerformanceSecurityValidator(test_client)

# Run comprehensive validation
results = validator.run_comprehensive_validation()

# Generate report
report = validator.generate_report()
print(report)
```

## Configuration

### Environment Variables

```bash
# Database Configuration
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=your_username
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=mystocks

# Authentication
JWT_SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS_STR=http://localhost:3000,http://localhost:8080

# Testing
TEST_DATABASE_URL=postgresql://user:pass@localhost/testdb
```

### Test Configuration

**Customizing Thresholds**:
```python
# In test files, you can adjust quality thresholds

# API Compliance
MIN_COMPLIANCE_RATE = 0.8  # 80% minimum compliance

# Static Analysis
MAX_CRITICAL_ISSUES = 0
MAX_TYPE_ISSUES = 10

# Documentation
MIN_DOCUMENTATION_COVERAGE = 0.6  # 60% coverage

# Performance
MAX_RESPONSE_TIME = 2.0  # 2 seconds
MAX_CRITICAL_SLOW_ENDPOINTS = 0

# Security
MAX_SQL_VULNERABILITIES = 0
MAX_XSS_VULNERABILITIES = 2
```

## CI/CD Integration

### GitHub Actions Workflow

The framework includes a comprehensive GitHub Actions workflow (`.github/workflows/api-compliance-testing.yml`) that:

1. **Runs on Multiple Triggers**:
   - Push to main/develop branches
   - Pull requests
   - Daily scheduled runs
   - Manual workflow dispatch

2. **Tests Multiple Python Versions**:
   - Python 3.9, 3.10, 3.11

3. **Generates Comprehensive Reports**:
   - JSON test results
   - HTML coverage reports
   - Compliance badges

4. **Provides Feedback**:
   - PR comments with test results
   - Status checks
   - Artifacts for detailed analysis

### Pre-commit Hooks

Local development validation through pre-commit hooks (`.pre-commit-config.yaml`):

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run fast-api-compliance-check
```

**Available Hooks**:
- `fast-api-compliance-check`: API compliance validation
- `static-code-analysis-check`: Static code analysis
- `documentation-validation-check`: Documentation validation
- `security-check`: Security vulnerability checks
- `performance-check`: Performance benchmarks
- `openapi-schema-check`: OpenAPI schema validation

## Reporting

### Test Results Format

All test suites generate standardized JSON reports:

```json
{
  "timestamp": "2025-12-03T10:30:00Z",
  "summary": {
    "total_endpoints": 50,
    "compliant_endpoints": 45,
    "total_issues": 10,
    "critical_issues": 2
  },
  "endpoint_results": [
    {
      "path": "/api/stocks/search",
      "methods": ["GET", "POST"],
      "compliance": true,
      "issues": []
    }
  ],
  "global_issues": [
    "Missing OpenAPI security schemes documentation"
  ]
}
```

### Compliance Dashboard

The framework generates compliance metrics:

- **Overall Compliance Rate**: Percentage of compliant endpoints
- **Documentation Coverage**: Percentage of documented endpoints
- **Security Score**: Security vulnerability assessment
- **Performance Score**: Response time benchmarks
- **Code Quality Score**: Static analysis results

### Badge Generation

Automatic compliance badges for README files:

```
![API Compliance](https://img.shields.io/badge/API%20Compliance-85.0%25-brightgreen)
```

## Best Practices

### 1. Development Workflow

```bash
# 1. Make code changes
git checkout -b feature/new-endpoint

# 2. Run pre-commit hooks (automatically on commit)
git add .
git commit -m "Add new API endpoint"

# 3. Run full test suite locally
python -m pytest tests/ -v

# 4. Push and create PR
git push origin feature/new-endpoint

# 5. CI/CD runs automatically
# 6. Review test results in PR
```

### 2. Test Development

**Adding New Tests**:
```python
class TestNewFeature:
    def test_endpoint_compliance(self, compliance_validator):
        """Test new endpoint compliance"""
        results = compliance_validator.test_endpoint_compliance('/api/new/endpoint')
        assert results['compliance'], f"Compliance issues: {results['issues']}"

    def test_documentation_coverage(self, documentation_validator):
        """Test new endpoint documentation"""
        results = documentation_validator.validate_endpoint_documentation('/api/new/endpoint')
        assert results['has_description'], "Missing endpoint description"
```

**Custom Validation Rules**:
```python
def custom_validation_rule(endpoint_data):
    """Custom business logic validation"""
    # Add your validation logic here
    if not meets_criteria(endpoint_data):
        return {
            'compliance': False,
            'issues': ['Custom validation failed']
        }
    return {'compliance': True, 'issues': []}
```

### 3. Troubleshooting

**Common Issues**:

1. **Authentication Failures**:
```python
# Ensure test environment has valid credentials
# Set JWT_SECRET_KEY in .env
# Check user database has test users
```

2. **Database Connection Issues**:
```python
# Verify PostgreSQL is running
# Check connection string in .env
# Ensure test database exists
```

3. **Missing Dependencies**:
```bash
# Install all required packages
pip install -r requirements.txt
pip install pytest pytest-cov pytest-html pytest-json-report
```

4. **Slow Test Execution**:
```python
# Use pytest-xdist for parallel execution
pip install pytest-xdist
python -m pytest tests/ -n auto
```

## Maintenance

### Regular Updates

1. **Update Dependencies**:
```bash
pip list --outdated
pip install --upgrade package_name
```

2. **Review Test Thresholds**:
```python
# Adjust thresholds based on project growth
MIN_COMPLIANCE_RATE = 0.85  # Increase as project matures
MAX_RESPONSE_TIME = 1.5     # Tighten performance requirements
```

3. **Add New Validation Rules**:
```python
# Add new business-specific validation rules
# Update test suites to cover new API patterns
# Extend security scanning for new threat vectors
```

### Monitoring

1. **Test Execution Trends**:
   - Monitor success rates over time
   - Track performance degradation
   - Identify compliance patterns

2. **Alert Configuration**:
   - Set up alerts for failing tests
   - Monitor critical security vulnerabilities
   - Track documentation coverage

## Extending the Framework

### Adding New Test Types

1. **Create New Test Module**:
```python
# tests/test_new_validation.py
class NewValidationValidator:
    def __init__(self, client):
        self.client = client

    def validate_new_aspect(self):
        # Implement validation logic
        pass

class TestNewValidation:
    def test_new_aspect(self, new_validator):
        results = new_validator.validate_new_aspect()
        assert results['compliance']
```

2. **Update CI/CD Workflow**:
```yaml
- name: Run New Validation Tests
  run: |
    python -m pytest tests/test_new_validation.py -v
```

3. **Add Pre-commit Hook**:
```yaml
- id: new-validation-check
  name: New Validation Check
  entry: python -m pytest tests/test_new_validation.py -v
  language: system
```

### Custom Reporting

1. **Custom Report Formats**:
```python
def generate_custom_report(results):
    # Generate HTML, PDF, or other formats
    pass
```

2. **Integration with External Tools**:
```python
# Send results to monitoring systems
# Create dashboards
# Generate alerts
```

## Support and Contributing

### Getting Help

- **Documentation**: Check this guide and inline code comments
- **Examples**: Review existing test files for patterns
- **Issues**: Create GitHub issues for bugs or feature requests

### Contributing

1. **Fork the Repository**
2. **Create Feature Branch**
3. **Add Tests**
4. **Ensure All Tests Pass**
5. **Update Documentation**
6. **Submit Pull Request**

### License

This framework follows the same license as the main project.

---

## Quick Reference

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific suite
python -m pytest tests/test_api_compliance.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run performance tests only
python -m pytest tests/test_performance_and_security.py::TestPerformanceAndSecurity -v

# Install pre-commit hooks
pre-commit install

# Run pre-commit hooks manually
pre-commit run --all-files

# Generate compliance report
python -c "
from tests.test_api_compliance import APIComplianceValidator
from web.backend.tests.conftest import test_client
validator = APIComplianceValidator(test_client())
results = validator.run_comprehensive_validation()
print(validator.generate_report())
"
```

**Remember**: The goal is continuous improvement of API quality. Use the framework as a guide, but adapt thresholds and validations to match your project's specific requirements and maturity level.
