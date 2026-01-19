# Specification: API Connectivity

## Overview
The API connectivity system enables secure, reliable communication between the Vue frontend and FastAPI backend, supporting all 469 API endpoints with proper authentication, error handling, and environment management.

## Requirements

### MODIFIED Requirements

#### Environment Configuration
**Scenario**: Application runs in different environments
- **GIVEN** application starts in development mode
- **WHEN** API client initializes
- **THEN** connects to `http://localhost:8000`
- **AND** in production connects to configured production URL
- **AND** environment variables override defaults

#### JWT Authentication
**Scenario**: User performs authenticated API call
- **GIVEN** user is logged in with valid JWT token
- **WHEN** API request is made
- **THEN** Authorization header includes `Bearer {token}`
- **AND** token automatically refreshed if expired
- **AND** unauthorized requests redirect to login

#### CORS Configuration
**Scenario**: Frontend makes cross-origin request to backend
- **GIVEN** frontend runs on port 3000
- **WHEN** API request is made
- **THEN** backend accepts request from allowed origins
- **AND** proper CORS headers returned
- **AND** credentials supported for authentication

#### Error Handling
**Scenario**: Backend API returns error response
- **GIVEN** API call fails with 500 error
- **WHEN** response received by frontend
- **THEN** user sees ArtDeco-styled error message
- **AND** error logged for debugging
- **AND** appropriate fallback behavior occurs

### ADDED Requirements

#### API Client Architecture
**Scenario**: Frontend needs to call backend APIs
- **GIVEN** 469 API endpoints exist
- **WHEN** frontend initializes
- **THEN** single API client configured
- **AND** base URL from environment variables
- **AND** timeout and retry logic configured
- **AND** request/response interceptors active

#### Request Interception
**Scenario**: API request is about to be sent
- **GIVEN** user makes API call
- **WHEN** request interceptor runs
- **THEN** JWT token added to headers
- **AND** request logging occurs
- **AND** loading indicators shown

#### Response Interception
**Scenario**: API response is received
- **GIVEN** backend returns response
- **WHEN** response interceptor runs
- **THEN** success responses processed normally
- **AND** error responses trigger appropriate handling
- **AND** response logging occurs

#### Network Resilience
**Scenario**: Network connection is unstable
- **GIVEN** intermittent network issues
- **WHEN** API calls fail
- **THEN** automatic retry with exponential backoff
- **AND** user notified of connectivity issues
- **AND** offline mode supported where possible

## Implementation Details

### Environment Configuration
```typescript
// .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
VITE_API_RETRY_ATTEMPTS=3

// .env.production
VITE_API_BASE_URL=https://api.mystocks.com
VITE_API_TIMEOUT=15000
VITE_API_RETRY_ATTEMPTS=2
```

### API Client Setup
```typescript
// src/api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getStoredToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Add request ID for tracking
        config.headers['X-Request-ID'] = this.generateRequestId()

        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log successful responses in development
        if (import.meta.env.DEV) {
          console.log(`API ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`)
        }
        return response
      },
      async (error) => {
        const originalRequest = error.config

        // Handle token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          const newToken = await this.refreshToken()
          if (newToken) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return this.client(originalRequest)
          }
        }

        // Handle other errors
        this.handleApiError(error)
        return Promise.reject(error)
      }
    )
  }

  private getStoredToken(): string | null {
    return localStorage.getItem('auth_token')
  }

  private async refreshToken(): Promise<string | null> {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) return null

      const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken
      })

      const newToken = response.data.access_token
      localStorage.setItem('auth_token', newToken)
      return newToken
    } catch {
      // Refresh failed, redirect to login
      this.redirectToLogin()
      return null
    }
  }

  private handleApiError(error: any) {
    const status = error.response?.status
    const message = error.response?.data?.message || error.message

    // Show user-friendly error messages
    switch (status) {
      case 400:
        showToast('请求参数错误', 'error')
        break
      case 401:
        showToast('登录已过期，请重新登录', 'warning')
        this.redirectToLogin()
        break
      case 403:
        showToast('权限不足', 'error')
        break
      case 404:
        showToast('请求的资源不存在', 'error')
        break
      case 500:
        showToast('服务器内部错误，请稍后重试', 'error')
        break
      default:
        if (!navigator.onLine) {
          showToast('网络连接已断开', 'warning')
        } else {
          showToast('网络请求失败，请检查连接', 'error')
        }
    }

    // Log error for debugging
    console.error('API Error:', {
      status,
      message,
      url: error.config?.url,
      method: error.config?.method
    })
  }

  private redirectToLogin() {
    // Clear stored tokens
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')

    // Redirect to login page
    window.location.href = '/login'
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  // Public methods for API calls
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config)
    return response.data
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config)
    return response.data
  }

  // ... other HTTP methods
}

export const apiClient = new ApiClient()
```

### Backend CORS Configuration
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MyStocks API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "https://mystocks-frontend.vercel.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Request-ID"],
    max_age=86400,  # 24 hours
)

# Additional security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubdomains"

    # Request tracking
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")

    return response
```

### Error Handling Components
```typescript
// src/components/common/ApiErrorBoundary.vue
<template>
  <div class="api-error-boundary">
    <div v-if="hasError" class="error-display">
      <ArtDecoCard variant="outlined" class="error-card">
        <template #header>
          <div class="error-header">
            <ArtDecoIcon name="alert-triangle" class="error-icon" />
            <h3>连接异常</h3>
          </div>
        </template>

        <div class="error-content">
          <p>{{ errorMessage }}</p>
          <div class="error-actions">
            <ArtDecoButton @click="retry" :loading="retrying">
              重新连接
            </ArtDecoButton>
            <ArtDecoButton variant="outline" @click="refreshPage">
              刷新页面
            </ArtDecoButton>
          </div>
        </div>
      </ArtDecoCard>
    </div>
    <slot v-else />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'

// Props
interface Props {
  error?: Error | null
  offline?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  error: null,
  offline: false
})

// Reactive state
const hasError = ref(false)
const errorMessage = ref('')
const retrying = ref(false)

// Watch for errors
watch(() => props.error, (newError) => {
  if (newError) {
    hasError.value = true
    errorMessage.value = getErrorMessage(newError)
  } else {
    hasError.value = false
  }
})

watch(() => props.offline, (offline) => {
  if (offline) {
    hasError.value = true
    errorMessage.value = '网络连接已断开，请检查网络连接'
  }
})

// Methods
const getErrorMessage = (error: Error): string => {
  if (!navigator.onLine) {
    return '网络连接已断开，请检查网络连接'
  }

  // Check for specific error types
  if (error.message.includes('timeout')) {
    return '请求超时，请稍后重试'
  }

  if (error.message.includes('401')) {
    return '登录已过期，请重新登录'
  }

  if (error.message.includes('500')) {
    return '服务器内部错误，请稍后重试'
  }

  return '网络请求失败，请稍后重试'
}

const retry = async () => {
  retrying.value = true
  try {
    // Emit retry event to parent
    emit('retry')
    // Simulate network check
    await new Promise(resolve => setTimeout(resolve, 2000))
    hasError.value = false
  } catch {
    errorMessage.value = '重试失败，请检查网络连接'
  } finally {
    retrying.value = false
  }
}

const refreshPage = () => {
  window.location.reload()
}

// Emits
const emit = defineEmits<{
  retry: []
}>()
</script>

<style scoped lang="scss">
.api-error-boundary {
  .error-display {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    padding: 2rem;
  }

  .error-card {
    max-width: 500px;
    text-align: center;
  }

  .error-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    color: var(--artdeco-danger);
  }

  .error-icon {
    font-size: 1.5rem;
  }

  .error-content {
    .error-actions {
      display: flex;
      gap: 1rem;
      justify-content: center;
      margin-top: 1.5rem;
    }
  }
}
</style>
```

## Performance Considerations

### Connection Pooling
- Axios keep-alive connections
- Connection reuse for multiple requests
- Automatic connection cleanup

### Caching Strategy
- Browser cache for static assets
- API response caching with ETags
- Service worker for offline support

### Monitoring
- Request/response logging
- Performance metrics collection
- Error rate monitoring
- Network latency tracking

## Cross-references
- **routing-system**: API connectivity enables navigation to data-dependent pages
- **deployment-scripts**: API configuration tested in full deployment scenario
- **environment-config**: API URLs managed through environment variables