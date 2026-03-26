import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { PiniaStoreFactory } from '@/stores/storeFactory'
import { _unifiedApiClient, createLoadingConfig } from '@/api/unifiedApiClient'
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
  data?: {
    token?: string
    token_type?: string
    user?: User
  }
  access_token?: string
  token?: string
  token_type?: string
  user?: User
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
  validate: (data: LoginResponse): boolean => !!(data && (data.access_token || data.token))
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

  // Get login store instance for internal use
  const loginStore = useLoginStore()

  // Getters
  const isAdmin = computed(() => user.value?.role === 'admin')
  const hasPermission = computed(() => (permission: string) => {
    return user.value?.permissions?.includes(permission) ?? false
  })

  const isLoading = computed(() => loginStore.isLoading)

  // Actions
  const setUser = (userData: User) => {
    user.value = userData
    isAuthenticated.value = true
    // Save user data to localStorage for persistence
    localStorage.setItem('auth_user', JSON.stringify(userData))
  }

  const setToken = (tokenValue: string) => {
    token.value = tokenValue
    localStorage.setItem('auth_token', tokenValue)
  }

  const logout = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  const initializeAuth = () => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')
    const shouldBootstrapLhciAuth = import.meta.env.VITE_LHCI_AUTH_BYPASS === 'true'

    if (savedToken) {
      token.value = savedToken

      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser)
          user.value = userData
          isAuthenticated.value = true
        } catch (error) {
          console.error('Failed to parse saved user data:', error)
          // Clear corrupted data
          localStorage.removeItem('auth_token')
          localStorage.removeItem('auth_user')
          token.value = null
          user.value = null
          isAuthenticated.value = false
        }
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
    try {
      // Use authApi.login which correctly sets Content-Type to application/x-www-form-urlencoded
      const response = await authApi.login(username, password) as LoginResponse

      // Backend returns {success, data: {token, token_type, user}, message}
      // Extract token from nested data structure
      const tokenValue = response?.data?.token || response?.access_token || response?.token
      const userData = response?.data?.user || response?.user

      if (!tokenValue) {
        return {
          success: false,
          message: 'Invalid response from server',
          error: { message: 'No access token received' }
        }
      }

      // Set token and user data
      setToken(tokenValue)
      setUser({
        id: userData?.id || 1,
        username: username,
        email: userData?.email || `${username}@example.com`,
        role: userData?.role || 'user',
        permissions: userData?.permissions || []
      })

      return { success: true }
    } catch (error) {
      console.error('Login error:', error)

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
    initializeAuth,
    login
  }
})
