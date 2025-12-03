#!/bin/bash

# API Compliance Testing Framework Setup Script
# This script sets up the complete testing framework

set -e  # Exit on any error

echo "🚀 Setting up API Compliance Testing Framework..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "web/backend/requirements.txt" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Step 1: Setting up Python environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

print_success "Python version check passed: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

print_status "Step 2: Installing dependencies..."

# Install backend dependencies
print_status "Installing backend dependencies..."
cd web/backend
pip install -r requirements.txt

# Install additional testing dependencies
print_status "Installing testing dependencies..."
pip install pytest pytest-cov pytest-html pytest-json-report pytest-xdist
pip install pytest-asyncio pytest-mock
pip install pre-commit

print_success "Dependencies installed"

cd ../..

print_status "Step 3: Setting up environment variables..."

# Check if .env file exists
if [ ! -f "web/backend/.env" ]; then
    if [ -f "web/backend/.env.example" ]; then
        cp web/backend/.env.example web/backend/.env
        print_success "Created .env file from template"
    else
        print_warning "Creating basic .env file..."
        cat > web/backend/.env << EOF
# Database Configuration
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password_here
POSTGRESQL_DATABASE=mystocks

# Authentication
JWT_SECRET_KEY=your_secret_key_here_please_change
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS_STR=http://localhost:3000,http://localhost:8080

# Testing
TEST_DATABASE_URL=postgresql://postgres:your_password_here@localhost/test_mystocks
EOF
        print_warning "Please update web/backend/.env with your configuration"
    fi
else
    print_status "Environment file already exists"
fi

print_status "Step 4: Setting up pre-commit hooks..."

# Install pre-commit hooks
if command -v pre-commit &> /dev/null; then
    pre-commit install
    print_success "Pre-commit hooks installed"
else
    print_warning "Pre-commit not available. Install with: pip install pre-commit"
fi

print_status "Step 5: Running initial tests..."

# Test if we can import the modules
cd web/backend

print_status "Testing module imports..."
python -c "
import sys
try:
    from app.main import app
    print('✅ FastAPI app import successful')
except ImportError as e:
    print(f'❌ FastAPI app import failed: {e}')
    sys.exit(1)

try:
    from tests.test_api_compliance import APIComplianceValidator
    print('✅ API Compliance validator import successful')
except ImportError as e:
    print(f'❌ API Compliance validator import failed: {e}')
    sys.exit(1)

try:
    from tests.test_static_code_analysis import StaticCodeAnalyzer
    print('✅ Static Code Analyzer import successful')
except ImportError as e:
    print(f'❌ Static Code Analyzer import failed: {e}')
    sys.exit(1)

try:
    from tests.test_api_documentation_validation import APIDocumentationValidator
    print('✅ Documentation Validator import successful')
except ImportError as e:
    print(f'❌ Documentation Validator import failed: {e}')
    sys.exit(1)

try:
    from tests.test_performance_and_security import PerformanceSecurityValidator
    print('✅ Performance & Security Validator import successful')
except ImportError as e:
    print(f'❌ Performance & Security Validator import failed: {e}')
    sys.exit(1)

print('✅ All test modules imported successfully')
"

cd ../..

print_status "Step 6: Creating test configuration..."

# Create pytest configuration if it doesn't exist
if [ ! -f "web/backend/pytest.ini" ]; then
    cat > web/backend/pytest.ini << EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    security: marks tests as security-related
    performance: marks tests as performance-related
    documentation: marks tests as documentation-related
    compliance: marks tests as compliance-related
EOF
    print_success "Created pytest configuration"
fi

print_status "Step 7: Running basic validation..."

# Run a quick smoke test
cd web/backend

print_status "Running smoke test..."
python -c "
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    # Test OpenAPI schema generation
    from app.main import app
    from fastapi.openapi.utils import get_openapi

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    required_fields = ['openapi', 'info', 'paths']
    missing = [field for field in required_fields if field not in schema]

    if missing:
        print(f'❌ OpenAPI schema missing fields: {missing}')
        sys.exit(1)
    else:
        print('✅ OpenAPI schema validation passed')

    # Test unified response model
    from app.core.responses import APIResponse, ErrorResponse, create_success_response

    response = create_success_response(data={'test': 'data'})
    if response.success and response.data:
        print('✅ Unified response model validation passed')
    else:
        print('❌ Unified response model validation failed')
        sys.exit(1)

    print('✅ All smoke tests passed')

except Exception as e:
    print(f'❌ Smoke test failed: {e}')
    sys.exit(1)
"

cd ../..

print_status "Step 8: Creating convenience scripts..."

# Create test runner script
cat > run_compliance_tests.sh << 'EOF'
#!/bin/bash

# API Compliance Test Runner
# Usage: ./run_compliance_tests.sh [test_type]

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    print_error "Virtual environment not found. Run setup_compliance_testing.sh first"
    exit 1
fi

cd web/backend

TEST_TYPE=${1:-"all"}

case $TEST_TYPE in
    "compliance"|"api")
        print_status "Running API Compliance Tests..."
        python -m pytest tests/test_api_compliance.py -v -m "not slow"
        ;;
    "static"|"code")
        print_status "Running Static Code Analysis Tests..."
        python -m pytest tests/test_static_code_analysis.py -v -m "not slow"
        ;;
    "documentation"|"docs")
        print_status "Running Documentation Validation Tests..."
        python -m pytest tests/test_api_documentation_validation.py -v -m "not slow"
        ;;
    "performance"|"perf")
        print_status "Running Performance Tests..."
        python -m pytest tests/test_performance_and_security.py::TestPerformanceAndSecurity::test_response_time_benchmarks -v
        ;;
    "security"|"sec")
        print_status "Running Security Tests..."
        python -m pytest tests/test_performance_and_security.py -TestPerformanceAndSecurity::test_sql_injection_detection tests/test_performance_and_security.py::TestPerformanceAndSecurity::test_xss_protection_validation tests/test_performance_and_security.py::TestPerformanceAndSecurity::test_authentication_security -v
        ;;
    "all")
        print_status "Running All Compliance Tests..."
        python -m pytest tests/test_api_compliance.py tests/test_static_code_analysis.py tests/test_api_documentation_validation.py tests/test_performance_and_security.py -v -m "not slow"
        ;;
    "comprehensive")
        print_status "Running Comprehensive Tests (including slow tests)..."
        python -m pytest tests/test_api_compliance.py tests/test_static_code_analysis.py tests/test_api_documentation_validation.py tests/test_performance_and_security.py -v
        ;;
    *)
        print_error "Unknown test type: $TEST_TYPE"
        echo "Usage: $0 [compliance|static|documentation|performance|security|all|comprehensive]"
        exit 1
        ;;
esac

print_success "Tests completed successfully!"
EOF

chmod +x run_compliance_tests.sh

# Create report generator script
cat > generate_compliance_report.sh << 'EOF'
#!/bin/bash

# API Compliance Report Generator
# Generates comprehensive compliance report

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    print_error "Virtual environment not found. Run setup_compliance_testing.sh first"
    exit 1
fi

cd web/backend

print_status "Generating comprehensive compliance report..."

python << 'PYTHON_EOF'
import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from tests.test_api_compliance import APIComplianceValidator
    from tests.test_static_code_analysis import StaticCodeAnalyzer
    from tests.test_api_documentation_validation import APIDocumentationValidator
    from tests.test_performance_and_security import PerformanceSecurityValidator
    from fastapi.testclient import TestClient
    from app.main import app

    # Create test client
    client = TestClient(app)

    # Run all validations
    print("Running API Compliance validation...")
    api_validator = APIComplianceValidator(client)
    api_results = api_validator.run_comprehensive_validation()

    print("Running Static Code Analysis...")
    static_analyzer = StaticCodeAnalyzer()
    static_results = static_analyzer.analyze_api_directory()

    print("Running Documentation validation...")
    doc_validator = APIDocumentationValidator(client)
    doc_results = doc_validator.run_comprehensive_validation()

    print("Running Performance & Security validation...")
    perf_validator = PerformanceSecurityValidator(client)
    perf_results = perf_validator.run_comprehensive_validation()

    # Compile comprehensive report
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "api_compliance": {
            "summary": api_results["summary"],
            "compliance_rate": api_results["summary"]["compliant_endpoints"] / max(api_results["summary"]["total_endpoints"], 1)
        },
        "static_analysis": {
            "summary": static_results["summary"],
            "quality_score": 1.0 - (static_results["summary"]["total_issues"] / max(static_results["summary"]["files_analyzed"] * 20, 1))
        },
        "documentation": {
            "summary": doc_results["summary"],
            "documentation_coverage": doc_results["summary"]["documented_endpoints"] / max(doc_results["summary"]["total_endpoints"], 1)
        },
        "performance_security": {
            "summary": perf_results["summary"],
            "security_score": 1.0 - (perf_results["summary"]["critical_issues"] / max(perf_results["summary"]["total_tests_run"], 1))
        }
    }

    # Calculate overall score
    scores = [
        report["api_compliance"]["compliance_rate"],
        report["static_analysis"]["quality_score"],
        report["documentation"]["documentation_coverage"],
        report["performance_security"]["security_score"]
    ]
    report["overall_score"] = sum(scores) / len(scores)
    report["overall_status"] = "PASS" if report["overall_score"] >= 0.8 else "NEEDS_IMPROVEMENT"

    # Save report
    with open("compliance_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "="*80)
    print("API COMPLIANCE FRAMEWORK REPORT")
    print("="*80)
    print(f"Generated: {report['timestamp']}")
    print(f"Overall Score: {report['overall_score']:.1%}")
    print(f"Status: {report['overall_status']}")
    print()

    print("Component Scores:")
    print(f"  API Compliance: {report['api_compliance']['compliance_rate']:.1%}")
    print(f"  Code Quality: {report['static_analysis']['quality_score']:.1%}")
    print(f"  Documentation: {report['documentation']['documentation_coverage']:.1%}")
    print(f"  Security: {report['performance_security']['security_score']:.1%}")

    print("\nDetailed reports:")
    print("  - Full JSON report: compliance_report.json")
    print("  - Coverage report: htmlcov/index.html")

    print("="*80)

except Exception as e:
    print(f"Error generating report: {e}")
    sys.exit(1)

PYTHON_EOF

print_success "Compliance report generated successfully!"
print_status "Open web/backend/htmlcov/index.html for detailed coverage report"
print_status "Open web/backend/compliance_report.json for detailed JSON report"

cd ..
EOF

chmod +x generate_compliance_report.sh

print_success "Convenience scripts created:"
echo "  - run_compliance_tests.sh [test_type]  # Run specific test suites"
echo "  - generate_compliance_report.sh        # Generate comprehensive report"

print_status "Setup completed successfully!"

echo ""
print_success "🎉 API Compliance Testing Framework is ready!"
echo ""
echo "Next steps:"
echo "1. Update web/backend/.env with your database configuration"
echo "2. Run './run_compliance_tests.sh' to validate the framework"
echo "3. Check docs/api/API_COMPLIANCE_TESTING_FRAMEWORK.md for detailed documentation"
echo ""
echo "Quick commands:"
echo "  ./run_compliance_tests.sh compliance    # Run API compliance tests"
echo "  ./run_compliance_tests.sh all           # Run all tests"
echo "  ./generate_compliance_report.sh        # Generate comprehensive report"
echo ""
print_warning "Remember to activate the virtual environment before running tests:"
echo "  source venv/bin/activate"