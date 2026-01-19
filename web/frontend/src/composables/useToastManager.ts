/**
 * useToastManager - 全局Toast通知管理器
 *
 * 提供统一的Toast通知API，支持ArtDeco风格的通知组件
 *
 * @example
 * import { useToastManager } from '@/composables/useToastManager'
 *
 * const toast = useToastManager()
 * toast.showError('网络连接失败')
 * toast.showSuccess('数据保存成功')
 */

import { reactive, watch } from 'vue'
import type { ToastConfig } from '@/components/artdeco/core/ArtDecoToast.vue'

export interface ToastInstance extends Required<Pick<ToastConfig, 'type' | 'message'>> {
  id: string
  title?: string
  duration: number
  closable: boolean
  createdAt: number
}

// 全局Toast状态
const toasts = reactive<ToastInstance[]>([])

// 生成唯一ID
let toastIdCounter = 0
const generateToastId = (): string => {
  return `toast-${Date.now()}-${toastIdCounter++}`
}

// 添加Toast
const addToast = (config: ToastConfig): string => {
  const id = config.id || generateToastId()

  // 检查是否已存在相同ID的Toast
  const existingIndex = toasts.findIndex(t => t.id === id)
  if (existingIndex > -1) {
    // 移除已存在的Toast
    toasts.splice(existingIndex, 1)
  }

  const toast: ToastInstance = {
    id,
    type: config.type || 'info',
    title: config.title,
    message: config.message,
    duration: config.duration ?? 4000, // 默认4秒
    closable: config.closable ?? true,
    createdAt: Date.now()
  }

  toasts.push(toast)

  // 自动移除（如果duration > 0）
  if (toast.duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, toast.duration)
  }

  return id
}

// 移除Toast
export const removeToast = (id: string): void => {
  const index = toasts.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.splice(index, 1)
  }
}

// 清除所有Toast
export const clearAllToasts = (): void => {
  toasts.splice(0, toasts.length)
}

// Toast管理器API
export interface ToastManager {
  toasts: typeof toasts

  // 便捷方法
  showSuccess: (message: string, title?: string, duration?: number) => string
  showError: (message: string, title?: string, duration?: number) => string
  showWarning: (message: string, title?: string, duration?: number) => string
  showInfo: (message: string, title?: string, duration?: number) => string

  // 通用方法
  show: (config: ToastConfig) => string
  remove: (id: string) => void
  clearAll: () => void
}

/**
 * useToastManager Composable
 *
 * 提供全局Toast通知管理功能
 */
export function useToastManager(): ToastManager {
  return {
    toasts,

    // 成功通知
    showSuccess: (message: string, title?: string, duration?: number) => {
      return addToast({
        type: 'success',
        title: title || '操作成功',
        message,
        duration: duration ?? 3000
      })
    },

    // 错误通知
    showError: (message: string, title?: string, duration?: number) => {
      return addToast({
        type: 'error',
        title: title || '操作失败',
        message,
        duration: duration ?? 5000 // 错误消息显示更长时间
      })
    },

    // 警告通知
    showWarning: (message: string, title?: string, duration?: number) => {
      return addToast({
        type: 'warning',
        title: title || '注意事项',
        message,
        duration: duration ?? 4000
      })
    },

    // 信息通知
    showInfo: (message: string, title?: string, duration?: number) => {
      return addToast({
        type: 'info',
        title: title || '提示',
        message,
        duration: duration ?? 3000
      })
    },

    // 通用方法
    show: (config: ToastConfig) => {
      return addToast(config)
    },

    remove: removeToast,
    clearAll: clearAllToasts
  }
}

/**
 * 导出全局实例（可选）
 * 用于在非Vue组件中访问Toast管理器
 */
export const toastManager = useToastManager()

// 监听toasts变化，可用于调试
if (import.meta.env.DEV) {
  watch(toasts, (newToasts) => {
    console.log('[useToastManager] Active toasts:', newToasts.length)
  }, { deep: true })
}
