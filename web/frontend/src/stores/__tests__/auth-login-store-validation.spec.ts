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

describe('Auth login store validation', () => {
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
    vi.restoreAllMocks()
  })

  it('should reject non-string login tokens at store validation time', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    mockAuthApi.login.mockResolvedValue({
      success: true,
      code: 200,
      message: 'OK',
      data: {
        token: 1 as unknown as string,
        token_type: 'bearer',
        user: {
          id: 1,
          username: 'badtoken',
          email: 'badtoken@example.com',
          role: 'user',
          permissions: []
        }
      }
    })

    const result = await authStore.login('badtoken', 'password')

    expect(result).toEqual({
      success: false,
      message: 'Invalid response from server',
      error: { message: 'Missing auth token or user payload' }
    })
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Login error:',
      expect.objectContaining({ message: 'Data validation failed' })
    )
  })

  it('should reject blank login tokens at store validation time', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    mockAuthApi.login.mockResolvedValue({
      success: true,
      code: 200,
      message: 'OK',
      data: {
        token: '   ',
        token_type: 'bearer',
        user: {
          id: 1,
          username: 'blanktoken',
          email: 'blanktoken@example.com',
          role: 'user',
          permissions: []
        }
      }
    })

    const result = await authStore.login('blanktoken', 'password')

    expect(result).toEqual({
      success: false,
      message: 'Invalid response from server',
      error: { message: 'Missing auth token or user payload' }
    })
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Login error:',
      expect.objectContaining({ message: 'Data validation failed' })
    )
  })
})
