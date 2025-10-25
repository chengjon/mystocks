import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    try {
      const response = await authApi.login(username, password)

      // 注意：响应拦截器已经返回了 response.data，所以这里直接使用 response
      token.value = response.access_token
      user.value = response.user

      localStorage.setItem('token', token.value)
      localStorage.setItem('user', JSON.stringify(user.value))

      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '登录失败'
      }
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = ''
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }

  async function checkAuth() {
    if (!token.value) return false

    try {
      const response = await authApi.getCurrentUser()
      user.value = response  // 响应拦截器已经返回了 data
      return true
    } catch (error) {
      logout()
      return false
    }
  }

  async function refreshToken() {
    try {
      const response = await authApi.refreshToken()
      token.value = response.access_token  // 响应拦截器已经返回了 data
      localStorage.setItem('token', token.value)
      return true
    } catch (error) {
      logout()
      return false
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    checkAuth,
    refreshToken
  }
})
