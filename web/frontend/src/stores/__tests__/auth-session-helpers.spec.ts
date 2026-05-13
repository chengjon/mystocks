import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/index.js'

const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

vi.mock('@/api/index.js', () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn(),
    refreshToken: vi.fn()
  }
}))

const mockAuthApi = vi.mocked(authApi)

describe('Auth session helpers', () => {
  let authStore: ReturnType<typeof useAuthStore>

  beforeEach(() => {
    localStorageMock.getItem.mockReset()
    localStorageMock.setItem.mockReset()
    localStorageMock.removeItem.mockReset()
    localStorageMock.clear.mockReset()
    mockAuthApi.login.mockReset()
    mockAuthApi.logout.mockReset()
    mockAuthApi.refreshToken.mockReset()
    setActivePinia(createPinia())
    authStore = useAuthStore()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should not honor permissions when the local session token is blank', () => {
    authStore.isAuthenticated = true
    authStore.token = ''
    authStore.user = {
      id: 1,
      username: 'corrupted',
      email: 'corrupted@example.com',
      role: 'admin',
      permissions: ['*']
    }

    expect(authStore.hasPermission('risk:admin')).toBe(false)
  })

  it('should not treat users as administrators when the local session token is blank', () => {
    authStore.isAuthenticated = true
    authStore.token = ''
    authStore.user = {
      id: 1,
      username: 'corrupted-role',
      email: 'corrupted-role@example.com',
      role: 'admin',
      permissions: []
    }

    expect(authStore.isAdmin).toBe(false)
  })
})
