# Technical Design for Quantitative Trading Algorithms API

## Context

MyStocks has implemented 11 quantitative trading algorithms with GPU acceleration, but these algorithms are only accessible programmatically within the codebase. This change exposes these algorithms through REST APIs to enable external integration, frontend access, and broader ecosystem adoption.

## Goals / Non-Goals

### Goals
- **Expose all 11 algorithms** via standardized REST APIs
- **Maintain existing performance** (68x GPU acceleration)
- **Enable real-time usage** through WebSocket integration
- **Support batch processing** for high-throughput scenarios
- **Provide comprehensive documentation** and examples

### Non-Goals
- Modify existing algorithm implementations
- Replace existing internal algorithm usage
- Add new algorithms (only expose existing ones)
- Implement frontend UI beyond basic API integration

## Decisions

### 1. API Architecture Decision
**Chosen**: RESTful API with FastAPI
**Alternatives Considered**:
- GraphQL: Too complex for algorithm execution patterns
- gRPC: Not suitable for web ecosystem integration
- Custom protocol: Would require more client development

**Rationale**: FastAPI provides excellent async support, automatic OpenAPI generation, and seamless integration with existing Pydantic models. RESTful design is familiar to most developers and suitable for algorithm execution workflows.

### 2. Authentication Strategy
**Chosen**: JWT Bearer tokens with existing authentication system
**Rationale**: Leverages existing auth infrastructure, provides stateless authentication suitable for API usage, and maintains security standards.

### 3. Response Format
**Chosen**: Unified response format following project standards
```json
{
  "code": "SUCCESS",
  "message": "Operation completed",
  "data": {...},
  "request_id": "req_123456"
}
```

### 4. Algorithm Instantiation Pattern
**Chosen**: Factory pattern with dependency injection
```python
algorithm = algorithm_factory.create(AlgorithmType.SVM, config)
result = await algorithm.train(data, config)
```

**Rationale**: Provides clean separation between API layer and algorithm implementation, enables easy testing and mocking, and supports future algorithm additions.

### 5. GPU Resource Management
**Chosen**: Reuse existing GPU acceleration framework
**Rationale**: Maintains proven performance optimizations and avoids duplicating GPU management code.

### 6. Database Storage Strategy
**Chosen**: Extend existing dual database architecture
- **Algorithm models**: PostgreSQL (relational data)
- **Execution results**: TDengine (time-series performance data)
- **Real-time signals**: Redis (temporary caching)

### 7. Error Handling Strategy
**Chosen**: Hierarchical error handling with specific error codes
- `ALGORITHM_NOT_FOUND`: 算法不存在
- `INVALID_PARAMETERS`: 参数验证失败
- `GPU_UNAVAILABLE`: GPU资源不可用
- `EXECUTION_TIMEOUT`: 执行超时

## Risks / Trade-offs

### Performance vs. Flexibility
**Risk**: API overhead might impact real-time performance
**Mitigation**: Use async endpoints, implement caching, optimize serialization

### Security vs. Usability
**Risk**: Complex authentication might hinder adoption
**Mitigation**: Provide clear documentation and SDK examples

### Scalability vs. Complexity
**Risk**: Supporting all algorithms increases maintenance burden
**Mitigation**: Modular design allows independent updates

## Migration Plan

### Phase 1: Infrastructure (Non-disruptive)
- Add new API routes without affecting existing endpoints
- Create database tables alongside existing schema
- Deploy alongside existing services

### Phase 2-5: Incremental Rollout
- Deploy algorithm categories one by one
- Monitor performance and usage patterns
- Roll back individual algorithms if issues arise

### Phase 6: Full Integration
- Update frontend to use new APIs
- Deprecate old internal algorithm usage
- Full production deployment

## Open Questions

### 1. Rate Limiting Strategy
**Question**: What are appropriate rate limits for algorithm execution?
**Options**:
- Per-user limits based on subscription tier
- Per-algorithm limits based on computational cost
- Global limits with queuing for high-demand algorithms

### 2. Result Caching Strategy
**Question**: How long should we cache algorithm results?
**Considerations**:
- Real-time trading signals need immediate updates
- Historical analysis can benefit from caching
- Model predictions may have different freshness requirements

### 3. Batch Processing Limits
**Question**: What are reasonable limits for batch operations?
**Factors**:
- Memory constraints for large datasets
- GPU memory limitations
- Response time expectations
- Database transaction limits

### 4. WebSocket Connection Management
**Question**: How to handle WebSocket connection lifecycle?
**Considerations**:
- Connection pooling and reuse
- Automatic reconnection on failures
- Resource cleanup on disconnection
- Authentication token refresh

### 5. Algorithm Versioning
**Question**: How to handle algorithm updates without breaking existing integrations?
**Options**:
- Semantic versioning for API endpoints
- Backward-compatible updates when possible
- Deprecation warnings for breaking changes
- Multiple algorithm versions in parallel