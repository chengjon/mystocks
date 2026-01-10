## MODIFIED Requirements
### Requirement: All API endpoints MUST return responses in a standardized format with optional performance metadata.
All API endpoints MUST return responses in a standardized format. When performance monitoring is enabled, responses MAY include performance metadata.

#### Scenario: Enhanced Successful Response
- **GIVEN** any API endpoint is called successfully
- **WHEN** the endpoint processes the request
- **THEN** it SHALL return a response with performance field:
```json
{
  "success": true,
  "code": 0,
  "message": "操作成功",
  "data": { /* actual response data */ },
  "request_id": "uuid-string",
  "timestamp": "2025-12-06T10:30:00Z",
  "performance": {
    "latency_ms": 45.5,
    "trace_id": "abc123",
    "cache_hit": true
  }
}
```

#### Scenario: Performance Field Documentation
- **GIVEN** an API response is generated
- **WHEN** performance monitoring is enabled
- **THEN** the performance field MAY contain:
  - `latency_ms`: Response time in milliseconds
  - `trace_id`: Distributed tracing identifier
  - `cache_hit`: Whether the response was served from cache

### Requirement: Response Wrapper Implementation
All API endpoints MUST use the APIResponse wrapper with optional performance tracking.

#### Scenario: Performance Tracking Integration
- **GIVEN** an API endpoint is being implemented
- **WHEN** writing the endpoint handler
- **THEN** it MAY include performance tracking via the wrapper:
```python
from app.core.responses import APIResponse, track_performance

@router.get("/market/overview")
async def get_market_overview():
    with track_performance() as perf:
        data = await market_service.get_overview()
        perf.cache_hit = data.is_cached
    return APIResponse(data=data, performance=perf.to_dict())
```
