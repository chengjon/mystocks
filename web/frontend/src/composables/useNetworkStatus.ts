/**
 * 网络状态监听 Composable
 *
 * 监听网络连接状态变化，自动检测在线/离线状态
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'

// Network Connection API 类型定义
interface NetworkConnection {
    effectiveType?: string
    addEventListener?: (type: string, listener: () => void) => void
    removeEventListener?: (type: string, listener: () => void) => void
}

interface NavigatorWithConnection extends Navigator {
    connection?: NetworkConnection
    mozConnection?: NetworkConnection
    webkitConnection?: NetworkConnection
}

export function useNetworkStatus() {
    const isOnline = ref(navigator.onLine)
    const connectionType = ref('unknown')
    const lastStatusChange = ref(Date.now())

    // 更新网络状态
    const updateOnlineStatus = () => {
        const wasOnline = isOnline.value
        isOnline.value = navigator.onLine
        lastStatusChange.value = Date.now()

        // 如果状态发生变化，记录日志
        if (wasOnline !== isOnline.value) {
            console.log(
                `Network status changed: ${wasOnline ? 'online' : 'offline'} → ${isOnline.value ? 'online' : 'offline'}`
            )
        }

        // 更新连接类型
        updateConnectionType()
    }

    // 更新连接类型
    const updateConnectionType = () => {
        const nav = navigator as NavigatorWithConnection
        if ('connection' in nav && nav.connection) {
            connectionType.value = nav.connection.effectiveType || 'unknown'
        } else if ('mozConnection' in nav) {
            // Firefox
            connectionType.value = nav.mozConnection?.effectiveType || 'unknown'
        } else if ('webkitConnection' in nav) {
            // Safari
            connectionType.value = nav.webkitConnection?.effectiveType || 'unknown'
        } else {
            connectionType.value = 'unknown'
        }
    }

    // 获取连接质量描述
    const getConnectionQuality = () => {
        const type = connectionType.value
        switch (type) {
            case 'slow-2g':
            case '2g':
                return 'slow'
            case '3g':
                return 'moderate'
            case '4g':
                return 'fast'
            default:
                return 'unknown'
        }
    }

    // 获取状态描述
    const getStatusDescription = () => {
        if (!isOnline.value) {
            return '离线'
        }

        const quality = getConnectionQuality()
        switch (quality) {
            case 'slow':
                return '网络连接较慢'
            case 'moderate':
                return '网络连接一般'
            case 'fast':
                return '网络连接良好'
            default:
                return '网络连接未知'
        }
    }

    // 手动检查网络状态
    const checkConnectivity = async () => {
        if (!navigator.onLine) {
            return false
        }

        try {
            // 尝试连接到一个可靠的端点
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 5000)

            const response = await fetch('/health', {
                method: 'HEAD',
                cache: 'no-cache',
                signal: controller.signal
            })
            clearTimeout(timeoutId)
            return response.ok
        } catch (error) {
            console.warn('Connectivity check failed:', error)
            return false
        }
    }

    // 监听网络状态变化
    onMounted(() => {
        // 初始更新
        updateOnlineStatus()

        // 添加事件监听器
        window.addEventListener('online', updateOnlineStatus)
        window.addEventListener('offline', updateOnlineStatus)

        // 监听连接变化 (如果支持)
        if ('connection' in navigator) {
            const nav = navigator as NavigatorWithConnection
            if (nav.connection && nav.connection.addEventListener) {
                nav.connection.addEventListener('change', updateConnectionType)
            }
        }
    })

    onUnmounted(() => {
        // 移除事件监听器
        window.removeEventListener('online', updateOnlineStatus)
        window.removeEventListener('offline', updateOnlineStatus)

        if ('connection' in navigator) {
            const nav = navigator as NavigatorWithConnection
            if (nav.connection && nav.connection.removeEventListener) {
                nav.connection.removeEventListener('change', updateConnectionType)
            }
        }
    })

    return {
        // 响应式状态
        isOnline,
        connectionType,
        lastStatusChange,

        // 计算属性
        connectionQuality: computed(() => getConnectionQuality()),
        statusDescription: computed(() => getStatusDescription()),

        // 方法
        checkConnectivity,
        updateOnlineStatus
    }
}
