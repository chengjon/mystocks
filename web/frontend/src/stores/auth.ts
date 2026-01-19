import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: number
  username: string
  email: string
  role: string
  roles?: string[]
  permissions: string[]
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)

  // Getters
  const isAdmin = computed(() => user.value?.role === 'admin')
  const hasPermission = computed(() => (permission: string) => {
    return user.value?.permissions?.includes(permission) ?? false
  })

  // Actions
  const setUser = (userData: User) => {
    user.value = userData
    isAuthenticated.value = true
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
  }

  const initializeAuth = () => {
    const savedToken = localStorage.getItem('auth_token')
    if (savedToken) {
      token.value = savedToken
      // TODO: Validate token with backend
    }
  }

  // Added to satisfy Login.vue usage
  const login = async (username: string, password: string): Promise<{ success: boolean; message?: string }> => {
    console.log('Login stub called with:', username)
    // Simulate login success
    setUser({
      id: 1,
      username: username || 'admin',
      email: 'admin@mystocks.com',
      role: 'admin',
      permissions: ['trade', 'view_market', 'manage_users']
    })
    return Promise.resolve({ success: true })
  }

  // Initialize on store creation
  initializeAuth()

  return {
    // State
    user,
    token,
    isAuthenticated,
    loading,

    // Getters
    isAdmin,
    hasPermission,

    // Actions
    setUser,
    setToken,
    logout,
    initializeAuth,
    login
  }
})
