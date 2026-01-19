# Design Document: integrate-fullstack-platform

## Architecture Overview

This integration connects three independently developed layers into a cohesive fullstack application:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue Frontend  │◄──►│   FastAPI       │◄──►│  Databases      │
│   (ArtDeco UI)  │    │   Backend       │    │  (TD+PGSQL)    │
│                 │    │   (469 APIs)    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Browser  │    │   HTTP/WS       │    │   Data Router   │
│   (Port 3000)   │    │   (Port 8000)   │    │   (Auto Route)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Design Decisions

### 1. Minimal Intervention Principle

**Decision**: Make only necessary changes to integrate components without modifying existing functionality.

**Rationale**:
- All components are independently tested and functional
- Avoid introducing new bugs during integration
- Maintain existing code quality and patterns
- Enable easy rollback if needed

**Implementation**:
- Router configuration only (no page modifications)
- Environment variables only (no hardcoded URLs)
- CORS configuration only (no backend logic changes)
- Startup scripts only (no deployment logic changes)

### 2. Environment-Based Configuration

**Decision**: Use environment variables for all external dependencies and configuration.

**Rationale**:
- Support multiple deployment environments (dev/staging/prod)
- Enable easy configuration changes without code modifications
- Follow twelve-factor app principles
- Maintain security (no hardcoded secrets)

**Implementation**:
- `.env.development`: Development environment settings
- `.env.production`: Production environment settings
- Runtime environment detection
- Fallback defaults for safety

### 3. Progressive Enhancement Approach

**Decision**: Implement integration in phases with clear validation at each step.

**Rationale**:
- Enable early detection of integration issues
- Allow incremental testing and validation
- Support partial rollbacks if needed
- Maintain system stability throughout integration

**Implementation**:
- Phase 1: Routing (UI-only, no backend dependency)
- Phase 2: API connection (requires backend availability)
- Phase 3: Deployment (requires full system integration)

## Technical Specifications

### Router Configuration

```typescript
// web/frontend/src/router/index.ts
{
  path: '/',
  name: 'Dashboard',
  component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),
  meta: { requiresAuth: true }
}
```

**Features**:
- Lazy loading for all routes
- Route-level code splitting
- Meta fields for authentication guards
- Nested route support for complex layouts

### API Client Architecture

```typescript
// web/frontend/src/api/client.ts
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for JWT
apiClient.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or redirect to login
    }
    return Promise.reject(error)
  }
)
```

### CORS Configuration

```python
# web/backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Deployment Script Architecture

```bash
#!/bin/bash
# run_platform.sh

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Trap SIGINT for graceful shutdown
trap 'echo -e "\n${YELLOW}Shutting down...${NC}"; cleanup; exit 0' INT

cleanup() {
    print_status "Stopping services..."
    # Kill background processes
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    print_status "Services stopped."
}

# Main execution
main() {
    print_status "Starting MyStocks Platform..."

    # Check prerequisites
    check_prerequisites

    # Start services
    start_database
    start_backend
    start_frontend

    # Wait for user interrupt
    print_status "Platform started successfully!"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend API: http://localhost:8000"
    print_status "Press Ctrl+C to stop"

    wait
}

main "$@"
```

## Security Considerations

### API Security
- JWT token validation on all protected endpoints
- CORS configuration limited to development ports
- Request/response sanitization
- Rate limiting implementation

### Environment Security
- No hardcoded secrets in codebase
- Environment variables for all configuration
- Separate configs for different environments
- Secure token storage in frontend

## Performance Optimizations

### Frontend Optimizations
- Route-based code splitting
- Component lazy loading
- Image optimization
- Bundle size monitoring

### API Optimizations
- Connection pooling
- Response caching
- Database query optimization
- Background job processing

### Deployment Optimizations
- Multi-stage Docker builds
- CDN integration
- Compression middleware
- Monitoring and alerting

## Error Handling Strategy

### Frontend Error Handling
```typescript
// Global error boundary
app.config.errorHandler = (error, instance, info) => {
  console.error('Global error:', error)
  // Show ArtDeco-styled error message
  showErrorToast('系统出现异常，请稍后重试')
}
```

### API Error Handling
```python
# Global exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "data": exc.errors()
        }
    )
```

### Network Error Handling
- Automatic retry logic for failed requests
- Exponential backoff for rate limiting
- Offline detection and graceful degradation
- User-friendly error messages

## Testing Strategy

### Integration Testing
- API endpoint connectivity tests
- Component integration tests
- End-to-end user workflow tests
- Performance regression tests

### Environment Testing
- Development environment validation
- Production build testing
- Cross-browser compatibility
- Mobile responsiveness testing

## Monitoring and Observability

### Application Metrics
- Page load times
- API response times
- Error rates
- User session tracking

### Infrastructure Metrics
- Server resource usage
- Database connection pools
- Cache hit rates
- Background job queues

### Logging Strategy
- Structured logging with correlation IDs
- Error tracking and alerting
- Performance monitoring
- Security event logging

## Rollback and Recovery

### Quick Rollback Procedures
1. **Router Rollback**: Restore previous router configuration
2. **Environment Rollback**: Revert environment variable changes
3. **API Rollback**: Remove new interceptors, restore old client
4. **Deployment Rollback**: Stop new processes, restart old ones

### Data Safety
- No destructive database operations
- Configuration changes are additive only
- Easy to revert environment changes
- Backup all modified files before changes

## Future Considerations

### Scalability
- Microservices architecture preparation
- API gateway implementation
- Load balancing configuration
- Database sharding considerations

### Maintainability
- Automated testing pipeline
- CI/CD integration
- Documentation automation
- Code quality monitoring

### Security Enhancements
- OAuth2 integration
- API rate limiting
- Security headers
- Audit logging

This design ensures a robust, maintainable integration that preserves all existing functionality while enabling seamless fullstack operation.