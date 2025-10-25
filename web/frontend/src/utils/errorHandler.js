/**
 * 错误处理工具 - Week 3
 * 提供统一的错误处理和用户友好的错误提示
 */

import { ElMessage, ElNotification } from 'element-plus'

/**
 * 显示错误消息
 * @param {string|Error} error - 错误对象或错误消息
 * @param {object} options - 配置选项
 * @param {string} options.title - 通知标题（可选）
 * @param {boolean} options.useNotification - 是否使用通知而不是消息（可选）
 * @param {number} options.duration - 显示时长，毫秒（可选）
 */
export function showError(error, options = {}) {
  const {
    title = '错误',
    useNotification = false,
    duration = 3000
  } = options

  // 提取错误消息
  let message = '发生未知错误'

  if (typeof error === 'string') {
    message = error
  } else if (error?.response?.data?.error) {
    // 后端返回的用户友好消息
    message = error.response.data.error
  } else if (error?.message) {
    message = error.message
  } else if (error?.response?.data?.message) {
    message = error.response.data.message
  } else if (error?.response?.data?.detail) {
    message = error.response.data.detail
  }

  // 显示消息或通知
  if (useNotification) {
    ElNotification({
      title,
      message,
      type: 'error',
      duration
    })
  } else {
    ElMessage({
      message,
      type: 'error',
      duration
    })
  }

  // 开发环境下打印完整错误到控制台
  if (import.meta.env.DEV) {
    console.error('[ErrorHandler]', error)
  }
}

/**
 * 显示成功消息
 * @param {string} message - 成功消息
 * @param {number} duration - 显示时长，毫秒（可选）
 */
export function showSuccess(message, duration = 2000) {
  ElMessage({
    message,
    type: 'success',
    duration
  })
}

/**
 * 显示警告消息
 * @param {string} message - 警告消息
 * @param {number} duration - 显示时长，毫秒（可选）
 */
export function showWarning(message, duration = 3000) {
  ElMessage({
    message,
    type: 'warning',
    duration
  })
}

/**
 * 显示信息消息
 * @param {string} message - 信息消息
 * @param {number} duration - 显示时长，毫秒（可选）
 */
export function showInfo(message, duration = 2000) {
  ElMessage({
    message,
    type: 'info',
    duration
  })
}

/**
 * 处理API错误（包装函数）
 * 用于try-catch块中统一处理错误
 *
 * @param {Error} error - 错误对象
 * @param {string} defaultMessage - 默认错误消息（可选）
 * @param {object} options - 配置选项
 * @returns {void}
 *
 * @example
 * try {
 *   await api.getData()
 * } catch (error) {
 *   handleApiError(error, '获取数据失败')
 * }
 */
export function handleApiError(error, defaultMessage = '操作失败', options = {}) {
  // 如果错误已经被axios拦截器处理，不再重复显示
  if (error.handled) {
    return
  }

  // 检查是否有后端返回的用户友好消息
  const hasBackendMessage = error?.response?.data?.error

  // 如果后端没有返回友好消息，使用默认消息
  if (!hasBackendMessage) {
    showError(defaultMessage, options)
  } else {
    showError(error, options)
  }

  // 标记错误已处理，避免重复显示
  error.handled = true
}

/**
 * 处理加载状态的错误
 * 通常用于数据加载失败的场景
 *
 * @param {Error} error - 错误对象
 * @param {string} dataName - 数据名称（如"股票列表"、"K线数据"）
 * @returns {void}
 */
export function handleLoadError(error, dataName = '数据') {
  handleApiError(error, `${dataName}加载失败，请刷新重试`)
}

/**
 * 处理表单提交错误
 * 通常用于表单提交失败的场景
 *
 * @param {Error} error - 错误对象
 * @param {string} actionName - 操作名称（如"保存"、"删除"）
 * @returns {void}
 */
export function handleSubmitError(error, actionName = '提交') {
  handleApiError(error, `${actionName}失败，请检查后重试`, { useNotification: true })
}

/**
 * 错误日志记录
 * 记录错误到控制台或远程日志系统
 *
 * @param {Error} error - 错误对象
 * @param {object} context - 上下文信息（可选）
 * @returns {void}
 */
export function logError(error, context = {}) {
  const errorInfo = {
    message: error.message || String(error),
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent
  }

  // 开发环境：打印到控制台
  if (import.meta.env.DEV) {
    console.group('🔴 Error Log')
    console.error('Error:', errorInfo.message)
    console.error('Stack:', errorInfo.stack)
    console.error('Context:', errorInfo.context)
    console.groupEnd()
  } else {
    // 生产环境：发送到远程日志服务（待实现）
    // TODO: 集成远程日志服务（如Sentry）
    console.error('[Production Error]', errorInfo)
  }
}

export default {
  showError,
  showSuccess,
  showWarning,
  showInfo,
  handleApiError,
  handleLoadError,
  handleSubmitError,
  logError
}
