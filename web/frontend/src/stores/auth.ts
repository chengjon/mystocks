import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const permissions = ref<string[]>(JSON.parse(localStorage.getItem('permissions') || '[]'))

  const isAuthenticated = computed(() => !!token.value)

  // Task 2.1.1: 使用watch API自动保存到localStorage
  watch(token, (newToken) => {
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }, { immediate: true })

  watch(user, (newUser) => {
    if (newUser) {
      localStorage.setItem('user', JSON.stringify(newUser))
    } else {
      localStorage.removeItem('user')
    }
  }, { immediate: true })

  watch(permissions, (newPermissions) => {
    if (newPermissions && newPermissions.length > 0) {
      localStorage.setItem('permissions', JSON.stringify(newPermissions))
    } else {
      localStorage.removeItem('permissions')
    }
  }, { immediate: true })

  async function login(username: string, password: string) {
    try {
      const response = await authApi.login(username, password)

      // 响应拦截器已经返回了 response.data
      // 后端返回格式: { success: true, data: { token: "...", user: {...}, permissions: [...] } }
      if ((response as any).success && (response as any).data) {
        token.value = response.data.token
        user.value = response.data.user
        permissions.value = response.data.permissions || []

        // localStorage自动保存由watch处理
        return { success: true }
      } else {
        return {
          success: false,
          message: (response as any).message || '登录失败'
        }
      }
    } catch (error) {
        const err = error as any
        return {
          success: false,
          message: err.response?.data?.detail || err.message || '登录失败'
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
      permissions.value = []
      // localStorage自动清除由watch处理
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
      token.value = (response as any).access_token  // 响应拦截器已经返回了 data
      // localStorage自动保存由watch处理
      return true
    } catch (error) {
      logout()
      return false
    }
  }

  return {
    token,
    user,
    permissions,
    isAuthenticated,
    login,
    logout,
    checkAuth,
    refreshToken
  }
})
