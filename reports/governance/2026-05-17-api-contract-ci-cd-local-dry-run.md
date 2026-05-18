# API Contract CI/CD Local Dry-Run Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-17
Change: `enhance-api-contract-management-integration`
Workflow inspected: `.github/workflows/api-contract-validation.yml`

## Scope

This is a local, workflow-equivalent dry-run for OpenSpec task `8.2 Test CI/CD integration with contract validation`.

It is not a GitHub Actions remote execution. It verifies the repository-local commands that can be executed from this workspace and records blockers that prevent closing `8.2`.

## Commands And Results

| Check | Local Equivalent | Result |
| --- | --- | --- |
| Contract model/service imports | Import `ContractVersion`, `ContractDiff`, `ContractValidation`, `ContractValidator`, `DiffEngine` | Passed |
| OpenAPI generation | `OpenAPIGenerator(...).scan_app(app); generate_spec()` | Passed, generated `504` paths |
| OpenAPI documentation regression gate | `python -m pytest -o addopts= web/backend/tests/test_health_route_conflicts.py web/backend/tests/test_api_documentation_validation.py -q -rs --no-cov` | Failed: `9 failed, 120 passed in 66.55s` |
| OpenAPI success example audit | `python scripts/dev/openapi_success_example_audit.py --show-non-json` | Passed for JSON success examples: `JSON_SUCCESS_MISSING_EXAMPLES 0`; still reports `NON_JSON_SUCCESS_RESPONSES 4` for non-JSON responses |
| Documentation collector equivalent | `APIDocumentationValidator(TestClient(app)).run_comprehensive_validation()` plus `find_success_json_response_example_gaps()` | Failed gate thresholds by one remaining route issue: `documented_endpoints=537`, `total_endpoints=538`, `json_success_missing_examples=0` |

## Current Collector Metrics

```json
{
  "authentication_issue_count": 0,
  "documented_endpoints": 537,
  "documented_percentage": 0.9981412639405205,
  "endpoints_with_errors": 537,
  "endpoints_with_examples": 536,
  "error_response_percentage": 0.9981412639405205,
  "example_percentage": 0.9962825278810409,
  "json_success_missing_examples": 0,
  "non_json_success_responses": 4,
  "schema_issue_count": 0,
  "total_endpoints": 538,
  "total_issues": 1
}
```

## Failure Details

The documentation regression gate still fails because current OpenAPI documentation coverage is below the frozen baseline:

```text
Documentation coverage 99.08% regressed below baseline 99.60%
Example coverage 99.63% regressed below baseline 99.80%
Error response documentation coverage 99.81% regressed below baseline 100.00%
9 failed, 120 passed in 66.55s
```

The failed tests were:

```text
test_health_routes_are_unique_and_domain_scoped
test_announcement_endpoints_have_examples_parameter_docs_and_error_responses
test_kline_data_endpoints_have_docs_examples_and_error_responses
test_sentiment_endpoint_has_docs_examples_and_parameter_descriptions
test_position_write_endpoints_have_request_and_response_examples
TestAPIDocumentationValidation.test_endpoint_documentation_completeness
TestAPIDocumentationValidation.test_request_response_examples
TestAPIDocumentationValidation.test_error_response_documentation
TestAPIDocumentationValidation.test_comprehensive_documentation_validation
```

The standalone success example audit now reports `0` JSON success responses without examples. Contract-management endpoints are no longer in the missing-example list.

The remaining collector issue is the strategy-management compatibility catch-all route not aligning cleanly with the generated OpenAPI schema:

```text
Total Endpoints: 538
Fully Documented: 537
With Examples: 536
With Error Responses: 537
Total Issues: 1
ENDPOINT: /api/strategy-mgmt/{path:path}
  - Endpoint not found in OpenAPI schema
```

The health route gate also reports duplicate operation IDs for the same strategy-management compatibility route family.

The audit also reports `4` non-JSON success responses:

```text
GET /api/v1/trade/reconciliation/export 200 [text/csv]
GET /api/metrics 200 [text/plain]
GET /api/gpu/metrics 200 [text/plain]
GET /metrics 200 [text/plain]
```

## Local Environment Notes

The local run also emitted non-gating environment noise:

- PostgreSQL-dependent paths attempted to connect to `localhost:5438` and were refused.
- Application teardown logged `cannot import name 'close_postgres_async' from 'src.monitoring.infrastructure.postgresql_async_v3'`.
- Local pytest report files were owned by `nobody`; `var/reports/test_timing.csv` and `.claude/tdd-guard/data/test.json` needed write permission before the original pytest command could finish.

These do not replace the blocking documentation assertions above.

## Conclusion

OpenSpec task `8.2` is tested locally but not closed.

The workflow is present and executable locally through the contract-validation steps, and the contract-management endpoints currently pass the success-example audit. The repository still fails the same documentation/example gates that the CI workflow invokes because of non-contract route documentation debt and duplicate strategy-management compatibility operation IDs.

Closing `8.2` requires either:

- adding the remaining OpenAPI success examples, error responses, schema descriptions, and duplicate operation ID fixes, then rerunning the local workflow-equivalent commands; or
- explicitly approving a baseline/gate adjustment with evidence, then rerunning the commands.

After the local workflow-equivalent commands pass, a GitHub Actions run should be used as final remote CI evidence.
