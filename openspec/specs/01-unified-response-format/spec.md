# 01-unified-response-format Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose
Define the standard response envelope, wrapper usage, and frontend handling expectations for all
MyStocks API responses.
## Requirements
### Requirement: All API endpoints MUST return responses in a standardized format.

#### Scenario: Successful API Response
**GIVEN** any API endpoint is called successfully
**WHEN** the endpoint processes the request
**THEN** it SHALL return a response with the following structure:
```json
{
  "success": true,
  "code": 0,
  "message": "操作成功",
  "data": { /* actual response data */ },
  "request_id": "uuid-string",
  "timestamp": "2025-12-06T10:30:00Z"
}
```

#### Scenario: Error API Response
**GIVEN** any API endpoint encounters an error
**WHEN** the error is processed
**THEN** it SHALL return an error response with the following structure:
```json
{
  "success": false,
  "code": 422,
  "message": "Validation error: field is required",
  "details": {
    "field": "symbol",
    "error": "missing"
  },
  "request_id": "uuid-string",
  "timestamp": "2025-12-06T10:30:00Z"
}
```

### Requirement: Response Wrapper Implementation

The backend API SHALL ensure all FastAPI route handlers that are added or
modified in backend API modules declare an OpenAPI response model using
`UnifiedResponse[...]` or
`UnifiedPaginatedResponse[...]` unless the route is explicitly classified as a
legacy raw/control-plane exception with documented justification.

The declared response model MUST match the successful response envelope exposed
to callers. If the migration requires changing a response payload shape, the
same change MUST include endpoint-level regression coverage and an OpenAPI diff
record.

#### Scenario: Modified route file enters the commit gate

- **GIVEN** a backend API route file is staged for commit
- **WHEN** the route contains HTTP decorators such as `@router.get`,
  `@router.post`, `@router.put`, or `@router.delete`
- **THEN** each changed route declaration MUST use
  `response_model=UnifiedResponse[...]` or
  `response_model=UnifiedPaginatedResponse[...]`
- **AND** `UnifiedResponse Contract Guard` MUST report `errors=0` for the staged
  route file set.

#### Scenario: Runtime unblock touches a route file with historical contract debt

- **GIVEN** a runtime import fix requires editing a route file
- **AND** that file contains historical route response-model debt
- **WHEN** the runtime fix is prepared for commit
- **THEN** the route response-model debt MUST be resolved in a separate
  route-contract lane or the runtime fix MUST remain uncommitted
- **AND** the runtime lane MUST NOT bypass the guard with `--no-verify`.

### Requirement: Frontend Response Interceptor

**Requirement**: Frontend MUST have a response interceptor that handles the unified format.

#### Scenario: Successful Response Handling
**GIVEN** the API returns a successful response
**WHEN** the frontend receives it
**THEN** the interceptor SHALL extract and return only the `data` field:
```typescript
// Returns: { /* actual response data */ }
const result = await api.get('/market/overview')
```

#### Scenario: Error Response Handling
**GIVEN** the API returns an error response
**WHEN** the frontend receives it
**THEN** the interceptor SHALL extract and display the `message` field:
```typescript
// Shows: "Validation error: field is required"
ElMessage.error(error.message)
```

### Requirement: Response Status Code Mapping

**Requirement**: HTTP status codes MUST be properly mapped to response codes.

#### Scenario: Standard HTTP Responses
**GIVEN** different API response scenarios
**WHEN** returning responses
**THEN** HTTP status codes SHALL map as follows:
- 2xx (Success) → `success: true, code: 0`
- 400 (Bad Request) → `success: false, code: 400`
- 401 (Unauthorized) → `success: false, code: 401`
- 403 (Forbidden) → `success: false, code: 403`
- 422 (Validation) → `success: false, code: 422`
- 500 (Server Error) → `success: false, code: 500`

### Requirement: Request ID Tracking

**Requirement**: Every API request MUST have a unique identifier.

#### Scenario: Request Tracking
**GIVEN** an API request is made
**WHEN** the request is processed
**THEN** a unique `request_id` MUST be generated and included in the response
**AND** the same ID MUST be logged for debugging purposes.

### Requirement: Timestamp Standardization

**Requirement**: All response timestamps MUST be in ISO 8601 format.

#### Scenario: Response Timestamp
**GIVEN** any API response
**WHEN** the response is created
**THEN** the `timestamp` field MUST be an ISO 8601 UTC timestamp
**AND** it MUST reflect the exact time the response was generated.
