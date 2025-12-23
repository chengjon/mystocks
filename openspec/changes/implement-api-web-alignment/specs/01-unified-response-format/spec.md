# Unified Response Format Specification

## ADDED Requirements

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

**Requirement**: All API endpoints MUST use the APIResponse wrapper.

#### Scenario: Endpoint Implementation
**GIVEN** an API endpoint is being implemented
**WHEN** writing the endpoint handler
**THEN** it MUST use the APIResponse wrapper:
```python
from app.core.responses import APIResponse

@router.get("/market/overview")
async def get_market_overview():
    data = await market_service.get_overview()
    return APIResponse(data=data)
```

#### Scenario: Error Handling
**GIVEN** an API endpoint encounters a validation error
**WHEN** raising the error
**THEN** it MUST use the error response format:
```python
from fastapi import HTTPException
from app.core.responses import ErrorResponse

@router.post("/trade/order")
async def create_order(order: OrderRequest):
    if not order.symbol:
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                code=422,
                message="Symbol is required",
                details={"field": "symbol", "error": "missing"}
            ).dict()
        )
```

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