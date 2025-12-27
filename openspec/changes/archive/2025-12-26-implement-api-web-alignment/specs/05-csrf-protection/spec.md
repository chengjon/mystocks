# CSRF Protection Specification

## ADDED Requirements

### Requirement: CSRF Token Endpoint

**Requirement**: Backend MUST provide an endpoint to fetch CSRF tokens.

#### Scenario: Token Retrieval
**GIVEN** a client needs a CSRF token
**WHEN** making a GET request to `/api/auth/csrf`
**THEN** it SHALL receive a response with a unique token:

```json
{
  "success": true,
  "code": 0,
  "message": "CSRF token generated",
  "data": {
    "token": "abc123def456...",
    "expires_in": 3600
  },
  "request_id": "uuid",
  "timestamp": "2025-12-06T10:30:00Z"
}
```

### Requirement: Token Validation Middleware

**Requirement**: All state-changing requests MUST be validated for CSRF token.

#### Scenario: Request Validation
**GIVEN** a POST/PUT/DELETE/PATCH request
**WHEN** it reaches the backend
**THEN** the middleware MUST:
1. Extract CSRF token from `X-CSRF-Token` header
2. Verify token against stored value
3. Reject request with 403 if invalid or missing
4. Allow request to proceed if valid

#### Scenario: Token Expiration
**GIVEN** a CSRF token has expired
**WHEN** a request uses the expired token
**THEN** the server SHALL return a 403 error with message "CSRF token expired"

### Requirement: Frontend Token Management

**Requirement**: Frontend MUST automatically include CSRF token in requests.

#### Scenario: Automatic Token Injection
**GIVEN** an Axios request is made
**WHEN** it's a POST/PUT/DELETE/PATCH request
**THEN** the interceptor SHALL automatically add the CSRF token:

```typescript
// Request interceptor
instance.interceptors.request.use(async (config) => {
  const method = config.method?.toUpperCase()

  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method || '')) {
    // Skip CSRF for public endpoints
    const isPublicEndpoint = config.url?.startsWith('/api/public/')

    if (!isPublicEndpoint) {
      const token = await getCSRFToken()
      config.headers['X-CSRF-Token'] = token
    }
  }

  return config
})
```

#### Scenario: Token Storage
**GIVEN** a CSRF token is received
**WHEN** storing it
**THEN** it MUST be stored in:
- Memory for the current session
- Session storage for tab-specific sessions
- NEVER in local storage (XSS risk)

```typescript
// Token storage with expiration
class CSRFTokenManager {
  private token: string | null = null
  private expiresAt: number = 0

  async getToken(): Promise<string> {
    // Check if token is valid
    if (!this.token || Date.now() > this.expiresAt) {
      await this.refreshToken()
    }
    return this.token!
  }

  private async refreshToken() {
    const response = await axios.get('/api/auth/csrf')
    this.token = response.data.data.token
    this.expiresAt = Date.now() + (response.data.data.expires_in * 1000)
  }
}
```

### Requirement: Error Handling

**Requirement**: CSRF errors MUST be handled gracefully with user feedback.

#### Scenario: Invalid Token Error
**GIVEN** a request fails with CSRF error
**WHEN** the response interceptor handles it
**THEN** it SHALL:
1. Clear the stored invalid token
2. Fetch a new token
3. Show user-friendly message
4. Optionally retry the request

```typescript
// Response interceptor
instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response } = error

    if (response?.status === 403) {
      const message = response.data?.message

      if (message?.includes('CSRF')) {
        // Clear invalid token
        csrfManager.clearToken()

        // Try to refresh and retry once
        if (!error._retryCount) {
          error._retryCount = 1
          const newToken = await csrfManager.getToken()
          error.config.headers['X-CSRF-Token'] = newToken
          return instance.request(error.config)
        }

        // Show error to user
        ElMessage.error('安全验证失败，请刷新页面重试')
      }
    }

    return Promise.reject(error)
  }
)
```

### Requirement: Exemption Rules

**Requirement**: Certain endpoints MUST be exempt from CSRF protection.

#### Scenario: Public Endpoints
**GIVEN** a public API endpoint
**WHEN** defining it
**THEN** it SHOULD be marked as CSRF exempt:

```python
from fastapi import FastAPI
from app.middleware.csrf import csrf_exempt

app = FastAPI()

@app.get("/api/public/market-data")
@csrf_exempt
async def get_public_market_data():
    """Public endpoint, no CSRF required"""
    pass

# Or using middleware configuration
exempt_patterns = [
    "/api/public/*",
    "/api/auth/login",
    "/api/auth/csrf",
    "/api/health"
]
```

### Requirement: SameSite Cookie Configuration

**Requirement**：Backend MUST configure cookies with SameSite attribute.

#### Scenario：Cookie Security
**GIVEN** session cookies are set
**WHEN** configuring them
**THEN** they MUST include:

```python
from fastapi import Response

response.set_cookie(
    key="session",
    value=session_token,
    httponly=True,
    secure=True,  # HTTPS only
    samesite="strict"  # or "lax" for cross-origin needs
)
```

### Requirement: Development Environment Considerations

**Requirement**：CSRF protection MUST work in development environment.

#### Scenario：Local Development
**GIVEN** development on localhost
**WHEN** configuring CSRF
**THEN** it SHALL:
1. Allow same-origin requests
2. Handle different ports properly
3. Provide clear error messages for debugging

```python
# Development CSRF configuration
if app.debug:
    # Allow localhost origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-CSRF-Token"]
    )
```

### Requirement: Testing CSRF Protection

**Requirement**：CSRF implementation MUST be thoroughly tested.

#### Scenario：Unit Tests
**GIVEN** CSRF middleware is implemented
**WHEN** writing tests
**THEN** test:
- Valid token acceptance
- Invalid token rejection
- Missing token rejection
- Token expiration handling
- Exempt endpoint access

```python
# Test example
def test_csrf_protection(client):
    # Test without token
    response = client.post("/api/trade/order")
    assert response.status_code == 403
    assert "CSRF" in response.json()["message"]

    # Test with valid token
    token = client.get("/api/auth/csrf").json()["data"]["token"]
    headers = {"X-CSRF-Token": token}
    response = client.post("/api/trade/order", headers=headers)
    assert response.status_code != 403
```
