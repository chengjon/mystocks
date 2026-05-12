import { useAuthStore } from '@/stores/auth'
import type { RouteLocationNormalized } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getActivePinia } from 'pinia'
import { HOME_ROUTE_NAME } from './homeRoute'

interface AuthErrorLike {
  response?: {
    status?: number
  }
  code?: string
}

interface PermissionRouteMeta {
  permission?: string
  permissions?: string[]
  roles?: string[]
}

function isOptionalStringArray(value: unknown) {
  return value === undefined || (Array.isArray(value) && value.every((item) => typeof item === 'string'))
}

function hasValidAuthSession(authStore: ReturnType<typeof useAuthStore>) {
  const currentUser = authStore.user

  return (
    authStore.isAuthenticated &&
    typeof authStore.token === 'string' &&
    authStore.token.trim().length > 0 &&
    !!currentUser &&
    typeof currentUser.id === 'number' &&
    typeof currentUser.username === 'string' &&
    currentUser.username.trim().length > 0 &&
    (currentUser.email === undefined || typeof currentUser.email === 'string') &&
    (currentUser.role === undefined || typeof currentUser.role === 'string') &&
    isOptionalStringArray(currentUser.permissions) &&
    isOptionalStringArray(currentUser.roles)
  )
}

/**
 * Authentication guard for Vue Router
 * Checks if user is authenticated before allowing access to protected routes
 */
export const authGuard = (to: RouteLocationNormalized) => {
  const isLhciBypass = import.meta.env.VITE_LHCI_AUTH_BYPASS === 'true'

  // 检查 Pinia 是否已初始化（使用官方 API）
  const pinia = getActivePinia()
  if (!pinia) {
    // Pinia 未初始化，允许导航（在应用启动阶段）
    // 这是正常行为，因为路由可能在 Pinia 之前初始化
    return true
  }

  let authStore: ReturnType<typeof useAuthStore>
  try {
    authStore = useAuthStore()
  } catch (error) {
    // Store 访问失败，允许导航
    console.warn('[authGuard] Failed to access auth store:', error)
    return true
  }

  if (isLhciBypass) {
    authStore.initializeAuth()
  }

  // Check if route requires authentication (default: true)
  const requiresAuth = to.meta.requiresAuth !== false
  const hasValidSession = hasValidAuthSession(authStore)

  // If route requires auth and user is not authenticated
  if (requiresAuth && !hasValidSession) {
    // Show warning message
    ElMessage.warning('请先登录后再访问此页面')

    // Redirect to login with return URL
    return {
      name: 'login',
      query: { redirect: to.fullPath }
    }
  }

  const permissionMeta = to.meta as PermissionRouteMeta
  const hasMalformedPermissionMeta =
    (permissionMeta.permission !== undefined && typeof permissionMeta.permission !== 'string') ||
    !isOptionalStringArray(permissionMeta.permissions) ||
    !isOptionalStringArray(permissionMeta.roles)

  if (requiresAuth && hasMalformedPermissionMeta) {
    ElMessage.error('您没有权限访问此页面')
    return { path: '/403' }
  }

  const requiredPermissions = [
    ...(typeof permissionMeta.permission === 'string' && permissionMeta.permission ? [permissionMeta.permission] : []),
    ...(Array.isArray(permissionMeta.permissions) ? permissionMeta.permissions : [])
  ]

  if (requiresAuth && requiredPermissions.some((permission) => !authStore.hasPermission(permission))) {
    ElMessage.error('您没有权限访问此页面')
    return { path: '/403' }
  }

  const allowedRoles = Array.isArray(permissionMeta.roles) ? permissionMeta.roles : []
  const userRoles = [
    ...(authStore.user?.role ? [authStore.user.role] : []),
    ...(authStore.user?.roles ?? [])
  ]

  if (requiresAuth && allowedRoles.length > 0 && !allowedRoles.some((role) => userRoles.includes(role))) {
    ElMessage.error('您没有权限访问此页面')
    return { path: '/403' }
  }

  // If user is authenticated and trying to access login page, redirect to main page
  if (isLhciBypass && to.name === 'login') {
    return true
  }

  if (hasValidSession && to.name === 'login') {
    return { name: HOME_ROUTE_NAME }
  }

  // Allow navigation
  return true
}

/**
 * Global error handler for authentication-related errors
 */
export const handleAuthError = (error: unknown) => {
  const authStore = useAuthStore()
  const err: AuthErrorLike =
    typeof error === 'object' && error !== null ? (error as AuthErrorLike) : {}

  // Handle 401 Unauthorized
  if (err?.response?.status === 401) {
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
  if (err?.response?.status === 403) {
    console.warn('Insufficient permissions for this action')
    ElMessage.error('您没有权限执行此操作')
    return
  }

  // Handle network errors
  if (err?.code === 'NETWORK_ERROR' || !err?.response) {
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
