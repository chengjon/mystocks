/**
 * Session恢复工具
 * Task 2.1.2: 应用启动时验证并恢复session
 */

import { useAuthStore } from '@/stores/auth'

/**
 * 恢复用户session
 * - 从localStorage读取token
 * - 验证token有效性 (调用 /api/auth/me)
 * - 如果token无效，清除localStorage并跳转登录页
 * - 如果token有效，恢复用户信息
 */
export async function restoreSession() {
  const token = localStorage.getItem('token')

  // 如果没有token，无需恢复
  if (!token) {
    console.log('📭 No token found in localStorage')
    return
  }

  try {
    // 验证token有效性
    const authStore = useAuthStore()

    // 如果已经有用户信息，说明已经恢复过了
    if (authStore.user) {
      console.log('✅ Session already restored')
      return
    }

    // 验证token并获取用户信息
    const isValid = await authStore.checkAuth()

    if (isValid) {
      console.log('✅ Session restored successfully')
    } else {
      console.warn('⚠️ Token invalid, clearing session')
      // checkAuth已经处理了logout逻辑
    }
  } catch (error) {
    console.error('❌ Session restore error:', error)
    // 发生错误时清除localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

/**
 * 检查是否需要重定向到登录页
 * @returns {boolean} 是否需要跳转
 */
export function shouldRedirectToLogin() {
  const token = localStorage.getItem('token')
  return !token
}
