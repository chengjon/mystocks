import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { PiniaStoreFactory } from '@/stores/storeFactory'
import { createLoadingConfig } from '@/api/unifiedApiClient'
import { authApi } from '@/api/index.js'

export interface User {
  id: number
  username: string
  email: string
  role: string
  roles?: string[]
  permissions: string[]
}

// Create a login API store using the factory
// Transform response to match expected format: backend returns {data: {token}}, we need {access_token}
interface LoginResponse {
  success?: boolean
  data?: {
    token?: string
    token_type?: string
    user?: User
  }
  access_token?: string
  token?: string
  token_type?: string
  user?: User
  message?: string
}

interface RefreshTokenResponse {
  success?: boolean
  data?: {
    access_token?: string
    token?: string
  } | null
  access_token?: string
  token?: string
}

const AUTH_TOKEN_KEY = 'auth_token'
const AUTH_USER_KEY = 'auth_user'
const LEGACY_AUTH_TOKEN_KEY = 'token'
const LEGACY_AUTH_USER_KEY = 'user'
const REFRESH_TOKEN_KEY = 'refresh_token'

function readStoredValue(primaryKey: string, legacyKey: string): string | null {
  const primaryValue = localStorage.getItem(primaryKey)
  if (primaryValue !== null && primaryValue !== undefined) {
    return primaryValue
  }

  return localStorage.getItem(legacyKey) ?? null
}

function clearStoredAuth() {
  localStorage.removeItem(AUTH_TOKEN_KEY)
  localStorage.removeItem(AUTH_USER_KEY)
  localStorage.removeItem(LEGACY_AUTH_TOKEN_KEY)
  localStorage.removeItem(LEGACY_AUTH_USER_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

function isStoredUser(value: unknown, options: { requireNumberId?: boolean } = {}): value is User {
  if (!value || typeof value !== 'object') {
    return false
  }

  const candidate = value as Partial<User>
  const hasValidId = options.requireNumberId ? typeof candidate.id === 'number' : true
  const hasValidEmail = candidate.email === undefined || typeof candidate.email === 'string'
  const hasValidRole = candidate.role === undefined || typeof candidate.role === 'string'
  const hasValidPermissions = candidate.permissions === undefined || isStringArray(candidate.permissions)
  const hasValidRoles = candidate.roles === undefined || isStringArray(candidate.roles)
  return (
    typeof candidate.username === 'string' &&
    candidate.username.trim().length > 0 &&
    hasValidId &&
    hasValidEmail &&
    hasValidRole &&
    hasValidPermissions &&
    hasValidRoles
  )
}

const useLoginStore = PiniaStoreFactory.createApiStore<{
  access_token: string
  token_type: string
  user?: User
}>({
  id: 'auth-login',
  endpoint: '/auth/login',
  method: 'POST',
  loading: createLoadingConfig(true),
  request: (params?: unknown) => {
    const credentials = (params || {}) as { username?: string; password?: string }
    return authApi.login(credentials.username || '', credentials.password || '')
  },
  transform: (data: LoginResponse) => {
    // Backend returns {success, data: {token, ...}, message, ...}
    // We need to return {access_token, token_type, user}
    if (data?.data?.token) {
      return {
        access_token: data.data.token,
        token_type: data.data.token_type || 'bearer',
        user: data.data.user
      }
    }
    // Fallback for other response formats
    return {
      access_token: data?.access_token || data?.token || '',
      token_type: data?.token_type || 'bearer',
      user: data?.user
    }
  },
  validate: (data: LoginResponse): boolean => !!(data && (data?.data?.token || data.access_token || data.token))
})

const LHCI_AUTH_USER: User = {
  id: 1,
  username: 'lhci-admin',
  email: 'lhci-admin@mystocks.local',
  role: 'admin',
  permissions: ['*']
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = ref(false)
  const loginPending = ref(false)

  // Get login store instance for internal use
  const loginStore = useLoginStore()

  // Getters
  const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.roles?.includes('admin') === true)
  const hasPermission = computed(() => (permission: string) => {
    const permissions = user.value?.permissions ?? []
    return permissions.includes('*') || permissions.includes(permission)
  })

  const isLoading = computed(() => loginPending.value || loginStore.isLoading)

  // Actions
  const setUser = (userData: User) => {
    if (
      typeof token.value !== 'string' ||
      token.value.trim().length === 0 ||
      !isStoredUser(userData, { requireNumberId: true })
    ) {
      clearLocalSession()
      return
    }

    user.value = userData
    isAuthenticated.value = true
    // Save user data to localStorage for persistence
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(userData))
  }

  const setToken = (tokenValue: string) => {
    if (typeof tokenValue !== 'string' || tokenValue.trim().length === 0) {
      clearLocalSession()
      return
    }

    token.value = tokenValue
    localStorage.setItem(AUTH_TOKEN_KEY, tokenValue)
  }

  const clearLocalSession = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    loginStore.clear()
    clearStoredAuth()
  }

  const logout = async () => {
    clearLocalSession()

    try {
      await authApi.logout()
    } catch (error) {
      console.warn('Remote logout failed:', error)
    }
  }

  const refreshSession = async (): Promise<boolean> => {
    if (!token.value || !user.value || !isStoredUser(user.value, { requireNumberId: true })) {
      clearLocalSession()
      return false
    }

    try {
      const response = (await authApi.refreshToken()) as RefreshTokenResponse
      const refreshedToken = response?.data?.access_token || response?.data?.token || response?.access_token || response?.token

      if (typeof refreshedToken !== 'string' || refreshedToken.trim().length === 0) {
        clearLocalSession()
        return false
      }

      setToken(refreshedToken)
      return true
    } catch (error) {
      console.warn('Session refresh failed:', error)
      clearLocalSession()
      return false
    }
  }

  const initializeAuth = () => {
    const savedToken = readStoredValue(AUTH_TOKEN_KEY, LEGACY_AUTH_TOKEN_KEY)
    const savedUser = readStoredValue(AUTH_USER_KEY, LEGACY_AUTH_USER_KEY)
    const shouldBootstrapLhciAuth = import.meta.env.VITE_LHCI_AUTH_BYPASS === 'true'

    if (savedToken !== null) {
      if (savedToken.trim().length === 0) {
        clearLocalSession()
        return
      }

      token.value = savedToken

      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser)
          if (!isStoredUser(userData, { requireNumberId: true })) {
            throw new Error('Invalid stored user payload')
          }
          user.value = userData
          isAuthenticated.value = true
        } catch (error) {
          console.error('Failed to parse saved user data:', error)
          // Clear corrupted data
          clearStoredAuth()
          token.value = null
          user.value = null
          isAuthenticated.value = false
        }
      } else {
        clearStoredAuth()
        token.value = null
        user.value = null
        isAuthenticated.value = false
      }
      return
    }

    if (shouldBootstrapLhciAuth) {
      setToken('lhci-auth-token')
      setUser(LHCI_AUTH_USER)
    }
  }

  // Login with standardized API pattern
  const login = async (username: string, password: string): Promise<{ success: boolean; message?: string; error?: unknown }> => {
    loginPending.value = true
    try {
      const loginData = await loginStore.fetch({ username, password })
      const tokenValue = loginData?.access_token
      const userData = loginData?.user

      if (
        typeof tokenValue !== 'string' ||
        tokenValue.trim().length === 0 ||
        !userData ||
        !isStoredUser(userData, { requireNumberId: true })
      ) {
        clearLocalSession()
        return {
          success: false,
          message: 'Invalid response from server',
          error: { message: 'Missing auth token or user payload' }
        }
      }

      // Set token and user data
      setToken(tokenValue)
      setUser({
        id: userData?.id || 1,
        username: userData?.username || username,
        email: userData?.email || `${username}@example.com`,
        role: userData?.role || 'user',
        roles: userData?.roles,
        permissions: userData?.permissions || []
      })

      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      clearLocalSession()

      // Handle different error types
      if (error instanceof Error) {
        // Check for common HTTP status codes in error message
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
          return {
            success: false,
            message: '用户名或密码错误',
            error
          }
        }
        if (error.message.includes('429')) {
          return {
            success: false,
            message: '请求过于频繁，请稍后再试',
            error
          }
        }
        return {
          success: false,
          message: error.message,
          error
        }
      }

      return {
        success: false,
        message: '网络错误，请检查网络连接',
        error
      }
    } finally {
      loginPending.value = false
    }
  }

  // Initialize on store creation
  initializeAuth()

  return {
    // State
    user,
    token,
    isAuthenticated,

    // Getters
    isAdmin,
    hasPermission,
    isLoading,

    // Actions
    setUser,
    setToken,
    logout,
    refreshSession,
    initializeAuth,
    login
  }
})
