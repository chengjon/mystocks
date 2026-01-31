# Frontend Routing Optimization - Implementation Guide

## Overview

This document provides guidance for developers implementing the new frontend routing optimization system, which includes JWT-based authentication, standardized API data management, and real-time WebSocket integration.

## Architecture Overview

### Core Components

1. **Authentication System** (`src/stores/auth.ts`, `src/router/guards.ts`)
   - JWT token-based authentication with localStorage persistence
   - Route guards for protecting authenticated routes
   - Automatic token validation and refresh

2. **API Store Factory** (`src/stores/storeFactory.ts`)
   - Standardized Pinia store creation for API data
   - Built-in caching, loading states, and error handling
   - Support for pagination and real-time updates

3. **WebSocket Manager** (`src/utils/webSocketManager.ts`)
   - Connection lifecycle management with auto-reconnection
   - Event-driven message handling
   - Heartbeat monitoring and connection state tracking

4. **Data Adapters** (`src/stores/dataAdapters.ts`)
   - Standardized data transformation between API and store formats
   - Validation and error handling for data integrity

## Authentication Implementation

### Basic Usage

```typescript
import { useAuthStore } from '@/stores/auth'
import { authGuard } from '@/router/guards'

const authStore = useAuthStore()

// Login
await authStore.login('username', 'password')

// Check authentication status
if (authStore.isAuthenticated) {
  // User is logged in
}

// Logout
authStore.logout()
```

### Route Protection

Routes are protected by default. Mark public routes explicitly:

```typescript
// In router configuration
{
  path: '/login',
  name: 'login',
  component: () => import('@/views/Login.vue'),
  meta: {
    requiresAuth: false  // Explicitly public
  }
}

// Protected routes don't need requiresAuth: true (it's default)
// But you can be explicit:
{
  path: '/dashboard',
  name: 'dashboard',
  component: () => import('@/views/Dashboard.vue'),
  meta: {
    requiresAuth: true  // Explicitly protected
  }
}
```

### Custom Authentication Logic

```typescript
import { hasPermission, isAdmin } from '@/router/guards'

// Check permissions
if (hasPermission('trade')) {
  // Allow trading operations
}

// Check admin role
if (isAdmin()) {
  // Show admin features
}
```

## API Store Factory Usage

### Basic API Store

```typescript
import { PiniaStoreFactory } from '@/stores/storeFactory'

// Create a simple API store
const useUserProfileStore = PiniaStoreFactory.createApiStore({
  id: 'user-profile',
  endpoint: '/api/user/profile',
  method: 'GET',
  cache: { enabled: true, key: 'user-profile', ttl: 300000 }, // 5 minutes
  loading: { enabled: true, key: 'profile-loading' }
})

// Usage in component
const profileStore = useUserProfileStore()

// Fetch data
await profileStore.fetch()

// Access data
console.log(profileStore.data) // User profile object
console.log(profileStore.loading) // Loading state
console.log(profileStore.error) // Error message if any
```

### Real-time Store with WebSocket

```typescript
import { createMarketDataStore } from '@/stores/apiStores'

// Create real-time market data store
const useMarketDataStore = createMarketDataStore(
  'market-data',
  '/api/market/quotes'
)

// Usage in component
const marketStore = useMarketDataStore()

// Connect to real-time updates
marketStore.connectWebSocket()

// Data will be automatically updated via WebSocket
// Falls back to polling if WebSocket fails
```

### Paginated Store

```typescript
import { PiniaStoreFactory } from '@/stores/storeFactory'

const useTransactionHistoryStore = PiniaStoreFactory.createPaginatedStore({
  id: 'transaction-history',
  endpoint: '/api/transactions',
  pageSize: 20,
  cache: { enabled: true, key: 'transactions', ttl: 600000 } // 10 minutes
})

// Usage
const historyStore = useTransactionHistoryStore()

// Load first page
await historyStore.fetchPage(1)

// Navigate pages
await historyStore.nextPage()
await historyStore.prevPage()
await historyStore.goToPage(5)

// Check pagination state
console.log(historyStore.hasNextPage)
console.log(historyStore.currentPage)
```

## WebSocket Integration

### Basic WebSocket Usage

```typescript
import { marketDataWebSocket } from '@/utils/webSocketManager'

// Subscribe to market data updates
marketDataWebSocket.on('market-update', (message) => {
  console.log('Market update:', message.data)
})

// Send subscription request
marketDataWebSocket.send({
  type: 'subscribe',
  channel: 'market-quotes',
  symbols: ['AAPL', 'GOOGL']
})

// Check connection status
if (marketDataWebSocket.isConnected()) {
  // WebSocket is connected
}
```

### Custom WebSocket Manager

```typescript
import { WebSocketManager } from '@/utils/webSocketManager'

const customWS = new WebSocketManager({
  url: 'ws://custom-server:8080',
  reconnectAttempts: 5,
  reconnectInterval: 2000,
  heartbeatInterval: 30000
})

// Handle connection state changes
customWS.onStateChange((state) => {
  console.log('Connection state:', state)
})

// Connect
await customWS.connect()
```

## Data Adapters

### Creating Custom Adapters

```typescript
import { createAdapter } from '@/utils/adapterUtils'

const customAdapter = createAdapter({
  // Transform API response to internal format
  transform: (apiData) => {
    return apiData.map(item => ({
      id: item.id,
      name: item.title,
      createdAt: new Date(item.created_at),
      status: item.status === 'active' ? 'enabled' : 'disabled'
    }))
  },

  // Validate transformed data
  validate: (data) => {
    return data.every(item =>
      item.id &&
      item.name &&
      item.createdAt instanceof Date
    )
  }
})

// Usage with store
const useCustomStore = PiniaStoreFactory.createApiStore({
  id: 'custom-data',
  endpoint: '/api/custom',
  transform: customAdapter.transform,
  validate: customAdapter.validate
})
```

## Error Handling

### API Errors

```typescript
try {
  await store.fetch()
} catch (error) {
  if (error instanceof ApiError) {
    // Handle API-specific errors
    console.error('API Error:', error.message)
    if (error.statusCode === 401) {
      // Redirect to login
      router.push('/login')
    }
  } else {
    // Handle other errors
    console.error('Unexpected error:', error)
  }
}
```

### WebSocket Errors

```typescript
wsManager.onStateChange((state) => {
  switch (state) {
    case 'error':
      console.error('WebSocket connection error')
      // Show user notification
      break
    case 'disconnected':
      console.warn('WebSocket disconnected')
      // Attempt to reconnect or show offline message
      break
    case 'connected':
      console.log('WebSocket reconnected')
      // Resubscribe to channels if needed
      break
  }
})
```

## Performance Optimization

### Caching Strategies

```typescript
// Different cache strategies for different data types

// Real-time data (short cache)
cache: { enabled: true, ttl: 30000, strategy: 'memory' }

// Frequent data (medium cache)
cache: { enabled: true, ttl: 300000, strategy: 'memory' }

// Reference data (long cache)
cache: { enabled: true, ttl: 3600000, strategy: 'localStorage' }

// Historical data (very long cache)
cache: { enabled: true, ttl: 86400000, strategy: 'localStorage' }
```

### WebSocket Optimization

```typescript
// Use specific channels to reduce data volume
wsManager.send({
  type: 'subscribe',
  channel: 'market-quotes',
  symbols: ['AAPL', 'MSFT'], // Only subscribe to needed symbols
  fields: ['price', 'volume'] // Only request needed fields
})
```

## Migration Guide

### From Old Stores to New Factory

```typescript
// Old way
const useOldStore = defineStore('old', () => {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetch = async () => {
    loading.value = true
    try {
      const response = await api.get('/endpoint')
      data.value = response
    } catch (err) {
      error.value = err
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, fetch }
})

// New way
const useNewStore = PiniaStoreFactory.createApiStore({
  id: 'new-store',
  endpoint: '/endpoint',
  cache: { enabled: true, key: 'new-store', ttl: 300000 },
  loading: { enabled: true, key: 'new-store-loading' }
})
```

### From Direct API Calls to Stores

```typescript
// Old way
const fetchData = async () => {
  const response = await api.get('/api/data')
  return response
}

// New way
const store = useDataStore()
await store.fetch()
return store.data
```

## Testing

### Unit Tests for Stores

```typescript
import { describe, it, expect, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should handle login', async () => {
    const store = useAuthStore()

    // Mock successful login
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: 'token' })
    })

    await store.login('user', 'pass')
    expect(store.isAuthenticated).toBe(true)
  })
})
```

### Integration Tests

```typescript
describe('Store Factory Integration', () => {
  it('should create and use real-time store', async () => {
    const store = PiniaStoreFactory.createRealtimeStore({
      id: 'test-realtime',
      endpoint: '/api/test'
    })

    const storeInstance = store()

    // Test WebSocket connection
    await storeInstance.connectWebSocket()
    expect(storeInstance.isConnected).toBe(true)
  })
})
```

## Best Practices

1. **Use Factory for New Stores**: Always use `PiniaStoreFactory` for new API stores instead of manual store creation.

2. **Consistent Naming**: Use kebab-case for store IDs (e.g., `'user-profile'`, `'market-data'`).

3. **Cache Wisely**: Choose appropriate cache TTL and strategy based on data update frequency.

4. **Handle Errors Gracefully**: Always check for loading and error states in components.

5. **WebSocket Channels**: Use specific channels and subscribe only to needed data to reduce overhead.

6. **Data Validation**: Always validate data in adapters to ensure type safety.

7. **Testing**: Write tests for all stores, especially authentication and real-time features.

## Troubleshooting

### Authentication Issues

- Check if token is stored in localStorage
- Verify API endpoints return correct JWT format
- Ensure route guards are properly configured

### WebSocket Problems

- Check network connectivity
- Verify WebSocket server is running
- Check browser console for connection errors
- Ensure proper channel subscription

### Store Caching Issues

- Clear localStorage/sessionStorage for cache issues
- Check cache TTL settings
- Verify cache keys are unique

### Performance Problems

- Monitor WebSocket message frequency
- Check cache hit rates
- Profile component re-renders
- Use React DevTools for store updates