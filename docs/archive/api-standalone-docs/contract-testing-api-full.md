# Contract Testing Framework - API Reference

## Module: src.contract_testing

Complete API reference for the MyStocks Contract Testing Framework.

## Classes and Functions

### SpecificationValidator

OpenAPI specification validation and parsing.

```python
from src.contract_testing import SpecificationValidator, APIEndpoint, HTTPMethod, Parameter
```

#### Class: SpecificationValidator

Loads, validates, and parses OpenAPI specifications.

**Attributes**:
- `spec: Dict[str, Any]` - Loaded OpenAPI specification
- `endpoints: List[APIEndpoint]` - Parsed endpoints
- `title: str` - API title from spec
- `version: str` - API version from spec

**Methods**:

##### `__init__(spec_path: str = "")`
Initialize validator, optionally loading a spec file.

```python
# Without initial spec
validator = SpecificationValidator()

# With initial spec
validator = SpecificationValidator('openapi.json')
```

##### `load_specification(spec_path: str) -> Dict[str, Any]`
Load OpenAPI specification from file.

```python
spec = validator.load_specification('openapi.json')
```

**Parameters**:
- `spec_path` (str): Path to OpenAPI spec file (JSON or YAML)

**Returns**:
- `Dict[str, Any]` - Loaded specification dictionary

**Raises**:
- `FileNotFoundError` - If spec file doesn't exist
- `json.JSONDecodeError` - If JSON is invalid
- `yaml.YAMLError` - If YAML is invalid

##### `_validate_spec_structure() -> bool`
Validate OpenAPI specification structure.

```python
validator._validate_spec_structure()
```

**Raises**:
- `ValueError` - If spec structure is invalid

##### `_extract_metadata() -> None`
Extract metadata from specification.

```python
validator._extract_metadata()
print(f"API: {validator.title} v{validator.version}")
```

##### `_parse_endpoints() -> None`
Parse all endpoints from specification.

```python
validator._parse_endpoints()
```

##### `get_all_endpoints() -> List[APIEndpoint]`
Get all parsed endpoints.

```python
endpoints = validator.get_all_endpoints()
for endpoint in endpoints:
    print(f"{endpoint.method.value.upper()} {endpoint.path}")
```

**Returns**:
- `List[APIEndpoint]` - List of all endpoints

##### `get_endpoint(method: str, path: str) -> Optional[APIEndpoint]`
Get specific endpoint by method and path.

```python
endpoint = validator.get_endpoint('GET', '/api/users')
if endpoint:
    print(f"Found: {endpoint.summary}")
```

**Parameters**:
- `method` (str): HTTP method (GET, POST, etc.)
- `path` (str): URL path

**Returns**:
- `Optional[APIEndpoint]` - Endpoint if found, None otherwise

##### `get_summary() -> Dict`
Get specification summary with statistics.

```python
summary = validator.get_summary()
print(f"Title: {summary['title']}")
print(f"Total Endpoints: {summary['total_endpoints']}")
```

**Returns**:
- `Dict` - Summary with title, version, total_endpoints

##### `export_endpoints_json(output_path: str) -> None`
Export endpoints to JSON file.

```python
validator.export_endpoints_json('endpoints.json')
```

**Parameters**:
- `output_path` (str): Path to output JSON file

### TestHooksManager

Test lifecycle hook management.

```python
from src.contract_testing import TestHooksManager, HookContext, HookType, Hook
```

#### Class: TestHooksManager

Manages registration and execution of test hooks.

**Attributes**:
- `hooks: Dict[HookType, List[Hook]]` - Registered hooks by type
- `hook_execution_log: List[Dict]` - Log of hook executions

**Methods**:

##### `register_hook(hook_type: HookType, handler: Callable, name: str = "", description: str = "", priority: int = 0) -> None`
Register a hook handler.

```python
def my_setup(context: HookContext):
    context.test_state['initialized'] = True

manager.register_hook(HookType.BEFORE_ALL, my_setup, name="setup", priority=1)
```

**Parameters**:
- `hook_type` (HookType): Type of hook
- `handler` (Callable): Hook handler function
- `name` (str): Hook name (default: "")
- `description` (str): Hook description (default: "")
- `priority` (int): Hook priority, higher runs first (default: 0)

##### `before_all(handler: Callable, name: str = "", description: str = "") -> None`
Register beforeAll hook.

```python
@manager.before_all
def setup(context: HookContext):
    pass
```

##### `after_all(handler: Callable, name: str = "", description: str = "") -> None`
Register afterAll hook.

##### `before_each(handler: Callable, name: str = "", description: str = "") -> None`
Register beforeEach hook.

##### `after_each(handler: Callable, name: str = "", description: str = "") -> None`
Register afterEach hook.

##### `execute_hooks(hook_type: HookType, context: HookContext) -> None`
Execute all hooks of given type.

```python
context = HookContext(
    test_id="test_1",
    endpoint_method="GET",
    endpoint_path="/api/users"
)
manager.execute_hooks(HookType.BEFORE_EACH, context)
```

**Parameters**:
- `hook_type` (HookType): Type of hooks to execute
- `context` (HookContext): Context for hook execution

**Raises**:
- `Exception` - If any hook fails

##### `get_hooks_by_type(hook_type: HookType) -> List[Hook]`
Get all hooks of specific type.

```python
before_all_hooks = manager.get_hooks_by_type(HookType.BEFORE_ALL)
```

**Parameters**:
- `hook_type` (HookType): Hook type to filter by

**Returns**:
- `List[Hook]` - Filtered hooks

##### `get_execution_log() -> List[Dict]`
Get hook execution log.

```python
log = manager.get_execution_log()
for entry in log:
    print(f"{entry['hook_type']}: {entry['success']}")
```

**Returns**:
- `List[Dict]` - Execution log entries

##### `clear_hooks() -> None`
Clear all registered hooks.

```python
manager.clear_hooks()
```

#### Class: HookContext

Context passed to hook handlers.

**Attributes**:
- `test_id: str` - Test identifier
- `endpoint_method: str` - HTTP method
- `endpoint_path: str` - URL path
- `timestamp: datetime` - Hook execution time
- `request_data: Dict` - Request data (mutable)
- `response_data: Dict` - Response data (mutable)
- `test_state: Dict` - Test state (mutable)
- `metadata: Dict` - Additional metadata (mutable)

**Usage**:
```python
def setup_hook(context: HookContext):
    context.test_state['user_id'] = 'test_123'
    context.request_data['auth_header'] = 'Bearer token'
```

#### Enum: HookType

Hook execution phases.

- `BEFORE_ALL` - Before all tests
- `AFTER_ALL` - After all tests
- `BEFORE_EACH` - Before each endpoint test
- `AFTER_EACH` - After each endpoint test
- `BEFORE_TRANSACTION` - Before each request
- `AFTER_TRANSACTION` - After each request

### APIConsistencyChecker

API vs specification consistency verification.

```python
from src.contract_testing import APIConsistencyChecker, DiscrepancyReport, DiscrepancyType
```

#### Class: APIConsistencyChecker

Checks consistency between OpenAPI spec and actual API.

**Attributes**:
- `spec_validator: SpecificationValidator` - Spec validator instance
- `api_endpoints: Dict[str, Dict]` - Registered API endpoints
- `discrepancies: List[DiscrepancyReport]` - Found discrepancies

**Methods**:

##### `__init__(spec_validator: SpecificationValidator)`
Initialize consistency checker.

```python
validator = SpecificationValidator('openapi.json')
checker = APIConsistencyChecker(validator)
```

**Parameters**:
- `spec_validator` (SpecificationValidator): Loaded spec validator

##### `register_api_endpoint(method: str, path: str, parameters: Optional[List[str]] = None, response_codes: Optional[List[int]] = None, description: str = "") -> None`
Register actual API endpoint.

```python
checker.register_api_endpoint(
    method="GET",
    path="/api/users",
    parameters=["limit", "offset"],
    response_codes=[200, 400, 401, 500]
)
```

**Parameters**:
- `method` (str): HTTP method
- `path` (str): URL path
- `parameters` (Optional[List[str]]): List of parameter names
- `response_codes` (Optional[List[int]]): List of response codes
- `description` (str): Endpoint description

##### `scan_api_documentation(endpoint_docs: Dict[str, Dict]) -> None`
Scan API documentation and register endpoints.

```python
docs = {
    "GET /api/users": {
        "parameters": ["limit"],
        "response_codes": [200, 400]
    }
}
checker.scan_api_documentation(docs)
```

**Parameters**:
- `endpoint_docs` (Dict[str, Dict]): Endpoint documentation

##### `check_consistency() -> List[DiscrepancyReport]`
Check consistency between spec and API.

```python
discrepancies = checker.check_consistency()
for d in discrepancies:
    print(f"{d.severity}: {d.description}")
```

**Returns**:
- `List[DiscrepancyReport]` - Found discrepancies

##### `get_critical_issues() -> List[DiscrepancyReport]`
Get critical-level discrepancies.

```python
critical = checker.get_critical_issues()
```

**Returns**:
- `List[DiscrepancyReport]` - Critical discrepancies

##### `get_warnings() -> List[DiscrepancyReport]`
Get warning-level discrepancies.

**Returns**:
- `List[DiscrepancyReport]` - Warning discrepancies

##### `get_info() -> List[DiscrepancyReport]`
Get info-level discrepancies.

**Returns**:
- `List[DiscrepancyReport]` - Info discrepancies

##### `get_summary() -> Dict`
Get consistency check summary.

```python
summary = checker.get_summary()
print(f"Score: {summary['consistency_score']}/100")
print(f"Critical: {summary['critical_issues']}")
```

**Returns**:
- `Dict` - Summary with statistics

##### `export_report(output_path: str) -> None`
Export consistency report to JSON.

```python
checker.export_report('consistency_report.json')
```

**Parameters**:
- `output_path` (str): Output file path

#### Class: DiscrepancyReport

Single discrepancy report.

**Attributes**:
- `type: DiscrepancyType` - Type of discrepancy
- `endpoint_method: str` - HTTP method
- `endpoint_path: str` - URL path
- `severity: str` - Severity level (critical, warning, info)
- `description: str` - Description of issue
- `expected: Optional[str]` - Expected value
- `actual: Optional[str]` - Actual value
- `suggestion: str` - Suggestion for fix

#### Enum: DiscrepancyType

Types of discrepancies.

- `MISSING_ENDPOINT` - Endpoint in spec but not in API
- `EXTRA_ENDPOINT` - Endpoint in API but not in spec
- `PARAMETER_MISMATCH` - Parameter configuration mismatch
- `MISSING_PARAMETER` - Required parameter missing in API
- `EXTRA_PARAMETER` - Undocumented parameter in API
- `RESPONSE_CODE_MISMATCH` - Response code configuration mismatch
- `MISSING_RESPONSE_CODE` - Expected response code not returned
- `EXTRA_RESPONSE_CODE` - Unexpected response code returned
- `SECURITY_MISMATCH` - Security configuration mismatch
- `STATUS_CODE_DOCUMENTATION` - Status code documentation issue

### ContractTestEngine

Main contract testing orchestrator.

```python
from src.contract_testing import ContractTestEngine
```

#### Class: ContractTestEngine

Orchestrates contract testing execution.

**Attributes**:
- `spec_validator: SpecificationValidator` - Spec validator
- `hooks_manager: TestHooksManager` - Hooks manager
- `consistency_checker: APIConsistencyChecker` - Consistency checker
- `test_handlers: Dict[str, Callable]` - Test handlers
- `test_results: List[TestResult]` - Test results
- `start_time: Optional[datetime]` - Test start time
- `end_time: Optional[datetime]` - Test end time

**Methods**:

##### `__init__(spec_path: str)`
Initialize contract test engine.

```python
engine = ContractTestEngine('openapi.json')
```

**Parameters**:
- `spec_path` (str): Path to OpenAPI spec file

##### `register_test_handler(endpoint_key: str, handler: Callable) -> None`
Register test handler for endpoint.

```python
def test_users(endpoint, context):
    assert endpoint.method.value.upper() == "GET"
    return 1

engine.register_test_handler("GET /api/users", test_users)
```

**Parameters**:
- `endpoint_key` (str): Endpoint key (e.g., "GET /api/users")
- `handler` (Callable): Test handler function

##### `register_api_endpoint(method: str, path: str, parameters: Optional[List[str]] = None, response_codes: Optional[List[int]] = None, description: str = "") -> None`
Register actual API endpoint for consistency checking.

```python
engine.register_api_endpoint("GET", "/api/users", response_codes=[200, 400])
```

**Parameters**: Same as APIConsistencyChecker.register_api_endpoint()

##### `run_tests() -> Dict[str, Any]`
Run all contract tests.

```python
results = engine.run_tests()
print(f"Passed: {results['passed']}/{results['total']}")
```

**Returns**:
- `Dict[str, Any]` - Test summary with total, passed, failed, pass_rate, duration_ms

##### `check_consistency() -> Dict[str, Any]`
Check API consistency with specification.

```python
consistency = engine.check_consistency()
print(f"Score: {consistency['consistency_score']}/100")
```

**Returns**:
- `Dict[str, Any]` - Consistency summary

##### `export_test_results(output_path: str) -> None`
Export test results to JSON.

```python
engine.export_test_results('results.json')
```

**Parameters**:
- `output_path` (str): Output file path

##### `get_test_results() -> List[TestResult]`
Get all test results.

```python
results = engine.get_test_results()
```

**Returns**:
- `List[TestResult]` - Test results

#### Class: TestResult

Single test result.

**Attributes**:
- `test_id: str` - Test identifier
- `endpoint_method: str` - HTTP method
- `endpoint_path: str` - URL path
- `status: str` - Status (passed, failed, skipped)
- `duration_ms: float` - Execution duration
- `error_message: Optional[str]` - Error message if failed
- `assertions: int` - Number of assertions
- `assertions_passed: int` - Number of passing assertions

**Methods**:

##### `to_dict() -> Dict`
Convert to dictionary.

```python
result_dict = test_result.to_dict()
```

### ContractTestReportGenerator

Multi-format report generation.

```python
from src.contract_testing import ContractTestReportGenerator
```

#### Class: ContractTestReportGenerator

Generates reports in JSON, Markdown, and HTML formats.

**Attributes**:
- `test_results: List[Dict]` - Test results
- `consistency_summary: Dict` - Consistency check summary
- `discrepancies: List[Dict]` - Discrepancies
- `start_time: Optional[datetime]` - Test start time
- `end_time: Optional[datetime]` - Test end time

**Methods**:

##### `__init__()`
Initialize report generator.

```python
generator = ContractTestReportGenerator()
```

##### `add_test_results(results: List[Dict]) -> None`
Add test results.

```python
results = [
    {"status": "passed", "endpoint_method": "GET", "endpoint_path": "/api/users"},
    {"status": "failed", "endpoint_method": "POST", "endpoint_path": "/api/users"}
]
generator.add_test_results(results)
```

**Parameters**:
- `results` (List[Dict]): Test result dictionaries

##### `add_consistency_check(summary: Dict, discrepancies: List[Dict]) -> None`
Add consistency check results.

```python
generator.add_consistency_check(
    summary={"consistency_score": 85.5, "critical_issues": 2},
    discrepancies=[...]
)
```

**Parameters**:
- `summary` (Dict): Consistency summary
- `discrepancies` (List[Dict]): Discrepancy reports

##### `set_time_range(start: datetime, end: datetime) -> None`
Set test execution time range.

```python
from datetime import datetime
generator.set_time_range(
    start=datetime.now(),
    end=datetime.now()
)
```

**Parameters**:
- `start` (datetime): Start time
- `end` (datetime): End time

##### `generate_json_report(output_path: str) -> None`
Generate JSON report.

```python
generator.generate_json_report('report.json')
```

**Parameters**:
- `output_path` (str): Output file path

##### `generate_markdown_report(output_path: str) -> None`
Generate Markdown report.

```python
generator.generate_markdown_report('report.md')
```

**Parameters**:
- `output_path` (str): Output file path

##### `generate_html_report(output_path: str) -> None`
Generate HTML report.

```python
generator.generate_html_report('report.html')
```

**Parameters**:
- `output_path` (str): Output file path

##### `generate_all_reports(output_dir: str = "reports") -> None`
Generate all report formats.

```python
generator.generate_all_reports('reports/')
```

**Parameters**:
- `output_dir` (str): Output directory

## Enums

### HTTPMethod

HTTP methods supported by OpenAPI.

```python
from src.contract_testing import HTTPMethod

method = HTTPMethod.GET
print(method.value)  # "get"
```

**Values**:
- `GET` = "get"
- `POST` = "post"
- `PUT` = "put"
- `DELETE` = "delete"
- `PATCH` = "patch"
- `HEAD` = "head"
- `OPTIONS` = "options"

## Data Classes

### Parameter

OpenAPI parameter definition.

```python
from src.contract_testing import Parameter

param = Parameter(
    name="limit",
    in_="query",
    required=False,
    type="integer",
    description="Number of results"
)
```

**Attributes**:
- `name: str` - Parameter name
- `in_: str` - Parameter location (path, query, header, body)
- `required: bool` - Is required (default: False)
- `schema: Dict[str, Any]` - JSON Schema (default: {})
- `description: str` - Parameter description (default: "")
- `type: str` - Parameter type (default: "string")

### APIEndpoint

OpenAPI endpoint definition.

```python
from src.contract_testing import APIEndpoint, HTTPMethod

endpoint = APIEndpoint(
    path="/api/users",
    method=HTTPMethod.GET,
    summary="List users",
    parameters=[],
    responses={200: {"description": "Success"}}
)
```

**Attributes**:
- `path: str` - URL path
- `method: HTTPMethod` - HTTP method
- `summary: str` - Endpoint summary (default: "")
- `description: str` - Endpoint description (default: "")
- `parameters: List[Parameter]` - Parameters (default: [])
- `request_body: Optional[Dict]` - Request body schema
- `responses: Dict[int, Dict]` - Response definitions (default: {})
- `tags: List[str]` - Tags (default: [])
- `security: List[Dict]` - Security requirements (default: [])

---

**API Reference v1.0** - Complete Contract Testing Framework API documentation
