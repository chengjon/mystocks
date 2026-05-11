import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { authGuard } from '@/router/guards'
import { authApi } from '@/api/index.js'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    error: vi.fn(),
    warning: vi.fn(),
    success: vi.fn()
  }
}))

vi.mock('@/api/index.js', () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn()
  }
}))

const mockAuthApi = vi.mocked(authApi)

describe('Authentication Guards', () => {
  let authStore: ReturnType<typeof useAuthStore>

  beforeEach(() => {
    localStorageMock.getItem.mockReset()
    localStorageMock.setItem.mockReset()
    localStorageMock.removeItem.mockReset()
    localStorageMock.clear.mockReset()
    mockAuthApi.login.mockReset()
    mockAuthApi.logout.mockReset()
    mockAuthApi.logout.mockResolvedValue({ success: true, code: 200, data: undefined })
    setActivePinia(createPinia())
    authStore = useAuthStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('useAuthStore', () => {
    it('should initialize with empty state', () => {
      expect(authStore.user).toBeNull()
      expect(authStore.token).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })

    it('should set token and update authentication state', () => {
      const testToken = 'test-jwt-token'
      authStore.setToken(testToken)

      expect(authStore.token).toBe(testToken)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', testToken)
    })

    it('should set user and update authentication state', () => {
      const testUser = { id: '1', username: 'testuser', email: 'test@example.com' }
      authStore.setUser(testUser)

      expect(authStore.user).toEqual(testUser)
      expect(authStore.isAuthenticated).toBe(true)
    })

    it('should honor wildcard permissions for authenticated administrators', () => {
      authStore.setUser({
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        role: 'admin',
        permissions: ['*']
      })

      expect(authStore.hasPermission('risk:admin')).toBe(true)
    })

    it('should treat users with admin in roles as administrators', () => {
      authStore.setUser({
        id: 1,
        username: 'role-admin',
        email: 'role-admin@example.com',
        role: 'user',
        roles: ['admin'],
        permissions: []
      })

      expect(authStore.isAdmin).toBe(true)
    })

    it('should handle login success', async () => {
      mockAuthApi.login.mockResolvedValue({
        success: true,
        code: 200,
        message: 'OK',
        data: {
          token: 'test-token',
          token_type: 'bearer',
          user: {
            id: 1,
            username: 'testuser',
            email: 'test@example.com',
            role: 'user',
            permissions: []
          }
        }
      })

      const result = await authStore.login('testuser', 'password')

      expect(result.success).toBe(true)
      expect(authStore.token).toBe('test-token')
      expect(authStore.user?.username).toBe('testuser')
    })

    it('should handle login failure', async () => {
      mockAuthApi.login.mockRejectedValue(new Error('Invalid credentials'))

      const result = await authStore.login('testuser', 'wrongpassword')

      expect(result.success).toBe(false)
      expect(result.message).toBe('Invalid credentials')
    })

    it('should clear stale local session when login fails', async () => {
      authStore.setToken('stale-token')
      authStore.setUser({
        id: 1,
        username: 'stale-user',
        email: 'stale@example.com',
        role: 'user',
        permissions: []
      })
      mockAuthApi.login.mockRejectedValue(new Error('Invalid credentials'))

      const result = await authStore.login('testuser', 'wrongpassword')

      expect(result.success).toBe(false)
      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user')
    })

    it('should logout and clear data', async () => {
      // Set initial state
      authStore.setToken('test-token')
      authStore.setUser({ id: '1', username: 'testuser' })
      mockAuthApi.logout.mockResolvedValue({ success: true, code: 200, data: undefined })

      // Logout
      await authStore.logout()

      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
      expect(mockAuthApi.logout).toHaveBeenCalledTimes(1)
    })

    it('should keep local logout complete when remote logout fails', async () => {
      authStore.setToken('test-token')
      authStore.setUser({ id: '1', username: 'testuser' })
      mockAuthApi.logout.mockRejectedValue(new Error('logout unavailable'))

      await authStore.logout()

      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
    })

    it('should check auth on initialization', () => {
      // Create a fresh store instance for this test
      const freshStore = useAuthStore()

      // Mock localStorage for this test
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'auth_token') return 'stored-token'
        if (key === 'auth_user') return JSON.stringify({ id: '1', username: 'storeduser' })
        return null
      })

      // Manually trigger initialization
      freshStore.initializeAuth()

      expect(freshStore.token).toBe('stored-token')
      expect(freshStore.user?.username).toBe('storeduser')
      expect(freshStore.isAuthenticated).toBe(true)
    })

    it('should restore auth state from legacy storage keys', () => {
      const freshStore = useAuthStore()

      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'auth_token') return null
        if (key === 'auth_user') return null
        if (key === 'token') return 'legacy-token'
        if (key === 'user') return JSON.stringify({ id: '9', username: 'legacyuser' })
        return null
      })

      freshStore.initializeAuth()

      expect(freshStore.token).toBe('legacy-token')
      expect(freshStore.user?.username).toBe('legacyuser')
      expect(freshStore.isAuthenticated).toBe(true)
    })

    it('should clear orphaned stored tokens when the user payload is missing', () => {
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'auth_token') return 'orphaned-token'
        if (key === 'auth_user') return null
        return null
      })

      authStore.initializeAuth()

      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user')
    })

    it('should clear stored sessions when the user payload is not a valid user object', () => {
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'auth_token') return 'stored-token'
        if (key === 'auth_user') return JSON.stringify({ permissions: ['*'] })
        return null
      })

      authStore.initializeAuth()

      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user')
    })

    it('should bootstrap lighthouse auth for protected mock pages when enabled', () => {
      const freshStore = useAuthStore()
      const originalFlag = import.meta.env.VITE_LHCI_AUTH_BYPASS

      localStorageMock.getItem.mockReturnValue(null)
      window.history.replaceState({}, '', 'http://localhost:3000/dashboard')
      import.meta.env.VITE_LHCI_AUTH_BYPASS = 'true'

      freshStore.initializeAuth()

      expect(freshStore.token).toBe('lhci-auth-token')
      expect(freshStore.user?.username).toBe('lhci-admin')
      expect(freshStore.isAuthenticated).toBe(true)

      import.meta.env.VITE_LHCI_AUTH_BYPASS = originalFlag
    })
  })

  describe('authGuard', () => {
    it('should allow access to public routes', () => {
      // Ensure user is not authenticated for this test
      authStore.logout()

      const to = { name: 'login', meta: { requiresAuth: false } }
      const result = authGuard(to)

      expect(result).toBe(true)
    })

    it('should redirect to login for protected routes when not authenticated', () => {
      // Ensure user is not authenticated
      authStore.logout()

      const to = { name: 'dashboard', meta: { requiresAuth: true }, fullPath: '/dashboard' }
      const result = authGuard(to)

      expect(result).toEqual({
        name: 'login',
        query: { redirect: '/dashboard' }
      })
    })

    it('should allow access to protected routes when authenticated', () => {
      // Authenticate user
      authStore.setUser({ id: '1', username: 'testuser' })

      const to = { name: 'dashboard', meta: { requiresAuth: true } }
      const result = authGuard(to)

      expect(result).toBe(true)
    })

    it('should redirect authenticated users without required route permission', () => {
      authStore.setUser({
        id: 1,
        username: 'operator',
        email: 'operator@example.com',
        role: 'user',
        permissions: ['risk:view']
      })

      const to = {
        name: 'risk-admin',
        meta: { requiresAuth: true, permission: 'risk:admin' },
        fullPath: '/risk/admin'
      }
      const result = authGuard(to)

      expect(result).toEqual({ path: '/403' })
    })

    it('should redirect authenticated users without an allowed route role', () => {
      authStore.setUser({
        id: 1,
        username: 'operator',
        email: 'operator@example.com',
        role: 'user',
        roles: ['operator'],
        permissions: ['*']
      })

      const to = {
        name: 'admin-settings',
        meta: { requiresAuth: true, roles: ['admin'] },
        fullPath: '/system/admin'
      }
      const result = authGuard(to)

      expect(result).toEqual({ path: '/403' })
    })

    it('should redirect authenticated users away from login page', () => {
      // Authenticate user
      authStore.setUser({ id: '1', username: 'testuser' })

      const to = { name: 'login', meta: { requiresAuth: false } }
      const result = authGuard(to)

      expect(result).toEqual({ name: 'dashboard' })
    })

    it('should default to requiring authentication', () => {
      // Ensure user is not authenticated
      authStore.logout()

      const to = { name: 'someroute', meta: {}, fullPath: '/someroute' }
      const result = authGuard(to)

      expect(result).toEqual({
        name: 'login',
        query: { redirect: '/someroute' }
      })
    })

    it('should keep the login route reachable when lighthouse auth bypass is enabled', () => {
      const originalFlag = import.meta.env.VITE_LHCI_AUTH_BYPASS
      import.meta.env.VITE_LHCI_AUTH_BYPASS = 'true'

      const to = { name: 'login', meta: { requiresAuth: false } }
      const result = authGuard(to)

      expect(result).toBe(true)

      import.meta.env.VITE_LHCI_AUTH_BYPASS = originalFlag
    })
  })
})
