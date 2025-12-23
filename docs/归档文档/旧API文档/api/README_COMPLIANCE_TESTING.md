# API Compliance Testing Framework

## Quick Start

The API Compliance Testing Framework provides comprehensive automated testing to ensure API quality, security, and documentation standards.

### 🚀 One-Command Setup

```bash
# Run the setup script (handles everything automatically)
./setup_compliance_testing.sh
```

### 🧪 Quick Test Run

```bash
# Run all compliance tests
./run_compliance_tests.sh

# Or run specific test suites
./run_compliance_tests.sh compliance      # API compliance tests
./run_compliance_tests.sh security        # Security tests only
./run_compliance_tests.sh documentation  # Documentation tests only
```

### 📊 Generate Reports

```bash
# Generate comprehensive compliance report
./generate_compliance_report.sh
```

## What It Tests

### ✅ API Compliance
- Unified response structure validation
- Authentication requirements verification
- Parameter validation completeness
- HTTP method semantics compliance
- Proper status code usage

### 🔍 Static Code Analysis
- Security vulnerability detection
- Code quality metrics
- Documentation completeness
- Type annotation coverage
- Import organization

### 📚 Documentation Validation
- OpenAPI/Swagger schema completeness
- Endpoint documentation coverage
- Request/response examples
- Authentication scheme documentation

### ⚡ Performance & Security
- Response time benchmarks
- SQL injection vulnerability detection
- XSS protection validation
- Rate limiting verification
- Input sanitization checks

## Features

### CI/CD Integration
- **GitHub Actions**: Automated testing on push/PR
- **Pre-commit Hooks**: Local development validation
- **Automated Reporting**: PR comments and status checks
- **Badge Generation**: Visual compliance indicators

### Comprehensive Reporting
- **JSON Reports**: Machine-readable test results
- **HTML Coverage**: Detailed coverage reports
- **Compliance Scores**: Overall quality metrics
- **Trend Analysis**: Track improvements over time

### Flexible Configuration
- **Adjustable Thresholds**: Customize quality standards
- **Selective Testing**: Run specific test suites
- **Environment Support**: Multiple Python versions
- **Parallel Execution**: Faster test runs

## Test Results Example

```
=== API COMPLIANCE TEST SUITE SUMMARY ===
Total Endpoints: 45
Compliant: 42 (93.3%)
Non-Compliant: 3
Total Errors: 7

Performance Analysis:
Average Response Time: 0.342s
Fast Endpoints: 38
Slow Endpoints: 2

Security Analysis:
SQL Injection Vulnerabilities: 0
XSS Vulnerabilities: 1
Input Validation Issues: 3
Authentication Issues: 0

Critical Issues: 2
Status: PASS
```

## File Structure

```
web/backend/tests/
├── test_api_compliance.py              # API compliance validation
├── test_static_code_analysis.py       # Static code analysis
├── test_api_documentation_validation.py # Documentation validation
├── test_performance_and_security.py   # Performance & security tests
└── conftest.py                         # Test configuration

.github/workflows/
└── api-compliance-testing.yml         # CI/CD workflow

docs/api/
├── API_COMPLIANCE_TESTING_FRAMEWORK.md # Complete documentation
└── README_COMPLIANCE_TESTING.md      # This quick start guide
```

## Environment Setup

### Required Environment Variables

```bash
# Database
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=your_username
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=mystocks

# Authentication
JWT_SECRET_KEY=your_secret_key_here

# Testing
TEST_DATABASE_URL=postgresql://user:pass@localhost/testdb
```

### Database Setup

The framework requires a PostgreSQL database for testing:

```sql
-- Create test database
CREATE DATABASE test_mystocks;

-- Create test user (optional)
CREATE USER testuser WITH PASSWORD 'testpass';
GRANT ALL PRIVILEGES ON DATABASE test_mystocks TO testuser;
```

## Usage Examples

### Running Specific Tests

```bash
# API compliance only
python -m pytest web/backend/tests/test_api_compliance.py::TestAPICompliance::test_comprehensive_api_compliance -v

# Security checks only
python -m pytest web/backend/tests/test_performance_and_security.py -k "security" -v

# Documentation validation only
python -m pytest web/backend/tests/test_api_documentation_validation.py -v
```

### Custom Validation Rules

```python
# Add custom business logic validation
def custom_business_rule_validation(endpoint_data):
    """Custom validation for your specific requirements"""
    # Your validation logic here
    return {
        'compliance': True,
        'issues': []
    }
```

### Performance Benchmarking

```python
# Custom performance tests
from tests.test_performance_and_security import PerformanceSecurityValidator

validator = PerformanceSecurityValidator(test_client)
results = validator.test_response_times([
    {'url': '/api/critical/endpoint1', 'method': 'GET'},
    {'url': '/api/critical/endpoint2', 'method': 'POST'},
])
```

## Troubleshooting

### Common Issues

**Authentication Failures**:
```bash
# Check JWT secret key
echo $JWT_SECRET_KEY

# Update .env file
vim web/backend/.env
```

**Database Connection Issues**:
```bash
# Test PostgreSQL connection
psql -h localhost -U your_user -d mystocks

# Check environment variables
cat web/backend/.env | grep POSTGRESQL
```

**Missing Dependencies**:
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r web/backend/requirements.txt
pip install pytest pytest-cov pytest-html
```

**Slow Test Execution**:
```bash
# Run tests in parallel
pip install pytest-xdist
python -m pytest web/backend/tests/ -n auto
```

## Configuration

### Adjust Quality Thresholds

Edit test files to customize thresholds:

```python
# In test_api_compliance.py
MIN_COMPLIANCE_RATE = 0.8  # 80% compliance required

# In test_performance_and_security.py
MAX_RESPONSE_TIME = 2.0  # 2 second maximum response time

# In test_static_code_analysis.py
MAX_CRITICAL_ISSUES = 0  # No critical issues allowed
```

### Test Customization

Add new test types by extending the base validator classes:

```python
class CustomValidator(BaseValidator):
    def validate_custom_aspect(self):
        # Your custom validation logic
        pass
```

## Monitoring and Alerts

### GitHub Actions Integration

The CI/CD workflow provides:
- **Automatic test runs** on every push and PR
- **PR comments** with test results summary
- **Status checks** for compliance validation
- **Artifact storage** for detailed reports
- **Badge generation** for compliance status

### Local Development

Pre-commit hooks ensure quality before commits:
```bash
# Install hooks (automatically done by setup script)
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Best Practices

### Development Workflow

1. **Make changes** to your API code
2. **Run pre-commit hooks** (automatically on commit)
3. **Run test suite** locally before pushing
4. **Create PR** for automated testing
5. **Review results** and fix any issues
6. **Merge** when all tests pass

### Continuous Improvement

- **Monitor trends** in compliance scores
- **Adjust thresholds** as project matures
- **Add new validations** for emerging requirements
- **Update documentation** with new patterns
- **Review security** requirements regularly

## Support

### Documentation

- **Complete Guide**: `docs/api/API_COMPLIANCE_TESTING_FRAMEWORK.md`
- **API Documentation**: `http://localhost:8000/docs`
- **Test Examples**: See individual test files

### Getting Help

1. **Check this guide** for common issues
2. **Review test output** for specific error messages
3. **Consult complete documentation** for detailed explanations
4. **Create GitHub issue** for bugs or feature requests

### Contributing

1. **Fork repository**
2. **Create feature branch**
3. **Add tests** for new functionality
4. **Ensure all tests pass**
5. **Update documentation**
6. **Submit pull request**

---

## Quick Commands Reference

```bash
# Setup
./setup_compliance_testing.sh                    # Full setup

# Testing
./run_compliance_tests.sh [type]                 # Run tests
python -m pytest web/backend/tests/ -v          # Direct pytest
pre-commit run --all-files                       # Pre-commit hooks

# Reports
./generate_compliance_report.sh                  # Comprehensive report
open web/backend/htmlcov/index.html             # Coverage report
cat web/backend/compliance_report.json          # JSON results

# Environment
source venv/bin/activate                        # Activate environment
cat web/backend/.env                           # Check configuration
```

**Remember**: The framework is designed to be extensible. Adapt thresholds, add new validations, and customize reports to match your project's specific requirements and quality standards.
