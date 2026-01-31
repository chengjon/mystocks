import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { authGuard } from '@/router/guards'

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

describe('Authentication Guards', () => {
  let authStore: ReturnType<typeof useAuthStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    authStore = useAuthStore()
    vi.clearAllMocks()
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

    it('should handle login success', async () => {
      // Mock successful API response
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          access_token: 'test-token',
          user: { id: '1', username: 'testuser' }
        })
      })

      const result = await authStore.login('testuser', 'password')

      expect(result.success).toBe(true)
      expect(authStore.token).toBe('test-token')
      expect(authStore.user?.username).toBe('testuser')
    })

    it('should handle login failure', async () => {
      // Mock failed API response
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ message: 'Invalid credentials' })
      })

      const result = await authStore.login('testuser', 'wrongpassword')

      expect(result.success).toBe(false)
      expect(result.message).toContain('Invalid credentials')
    })

    it('should logout and clear data', () => {
      // Set initial state
      authStore.setToken('test-token')
      authStore.setUser({ id: '1', username: 'testuser' })

      // Logout
      authStore.logout()

      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user')
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
  })
})