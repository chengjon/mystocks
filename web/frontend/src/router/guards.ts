import { useAuthStore } from '@/stores/auth'
import type { RouteLocationNormalized } from 'vue-router'
import { ElMessage } from 'element-plus'

/**
 * Authentication guard for Vue Router
 * Checks if user is authenticated before allowing access to protected routes
 */
export const authGuard = (to: RouteLocationNormalized) => {
  const authStore = useAuthStore()

  // Check if route requires authentication (default: true)
  const requiresAuth = to.meta.requiresAuth !== false

  // If route requires auth and user is not authenticated
  if (requiresAuth && !authStore.isAuthenticated) {
    // Show warning message
    ElMessage.warning('请先登录后再访问此页面')

    // Redirect to login with return URL
    return {
      name: 'login',
      query: { redirect: to.fullPath }
    }
  }

  // If user is authenticated and trying to access login page, redirect to dashboard
  if (authStore.isAuthenticated && to.name === 'login') {
    return { name: 'dashboard' }
  }

  // Allow navigation
  return true
}

/**
 * Global error handler for authentication-related errors
 */
export const handleAuthError = (error: any) => {
  const authStore = useAuthStore()

  // Handle 401 Unauthorized
  if (error?.response?.status === 401) {
    console.warn('Authentication token expired or invalid')
    authStore.logout()

    // Show user-friendly message
    ElMessage.error('您的登录已过期，请重新登录')

    // Redirect to login after a short delay
    setTimeout(() => {
      window.location.href = '/login'
    }, 1000)
    return
  }

  // Handle 403 Forbidden
  if (error?.response?.status === 403) {
    console.warn('Insufficient permissions for this action')
    ElMessage.error('您没有权限执行此操作')
    return
  }

  // Handle network errors
  if (error?.code === 'NETWORK_ERROR' || !error?.response) {
    ElMessage.error('网络连接失败，请检查网络连接')
    return
  }

  // Re-throw other errors
  throw error
}

/**
 * Helper function to check if current user has required permissions
 */
export const hasPermission = (permission: string): boolean => {
  const authStore = useAuthStore()
  return authStore.hasPermission(permission)
}

/**
 * Helper function to check if current user has admin role
 */
export const isAdmin = (): boolean => {
  const authStore = useAuthStore()
  return authStore.isAdmin
}