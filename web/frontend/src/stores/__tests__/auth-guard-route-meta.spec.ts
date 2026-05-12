import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { authGuard } from '@/router/guards'
import { authApi } from '@/api/index.js'
import { useAuthStore } from '@/stores/auth'

const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

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
    logout: vi.fn(),
    refreshToken: vi.fn()
  }
}))

describe('authGuard route metadata validation', () => {
  let authStore: ReturnType<typeof useAuthStore>
  const mockAuthApi = vi.mocked(authApi)

  beforeEach(() => {
    localStorageMock.getItem.mockReset()
    localStorageMock.setItem.mockReset()
    localStorageMock.removeItem.mockReset()
    localStorageMock.clear.mockReset()
    mockAuthApi.logout.mockReset()
    mockAuthApi.refreshToken.mockReset()
    mockAuthApi.logout.mockResolvedValue({ success: true, code: 200, data: undefined })
    mockAuthApi.refreshToken.mockResolvedValue({ success: true, code: 200, data: { access_token: 'refreshed-token' } })

    setActivePinia(createPinia())
    authStore = useAuthStore()
    authStore.setToken('admin-token')
    authStore.setUser({
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      role: 'admin',
      permissions: ['*']
    })
  })

  it('should reject malformed route permission metadata', () => {
    const result = authGuard({
      name: 'risk-admin',
      meta: { requiresAuth: true, permissions: 'risk:admin' as unknown as string[] },
      fullPath: '/risk/admin'
    })

    expect(result).toEqual({ path: '/403' })
  })

  it('should reject malformed route role metadata without throwing', () => {
    const to = {
      name: 'admin-settings',
      meta: { requiresAuth: true, roles: 'admin' as unknown as string[] },
      fullPath: '/system/admin'
    }

    expect(() => authGuard(to)).not.toThrow()
    expect(authGuard(to)).toEqual({ path: '/403' })
  })
})
