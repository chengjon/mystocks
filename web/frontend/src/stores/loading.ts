import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'

/**
 * 全局加载状态管理 Store
 *
 * 用于管理API请求的加载状态，提供统一的加载状态查询和管理
 */

// 类型定义
interface LoadingStats {
  total: number
  active: number
  activeKeys: string[]
}

export const useLoadingStore = defineStore('loading', () => {
    // 加载状态映射表 - key: string, value: boolean
    const loadingStates = ref<Map<string, boolean>>(new Map())

    // 当前活跃的加载状态数量
    const activeLoadingCount = computed((): number => {
        let count = 0
        for (const isLoading of loadingStates.value.values()) {
            if (isLoading) count++
        }
        return count
    })

    // 是否有任何加载状态处于活跃状态
    const hasActiveLoading = computed((): boolean => activeLoadingCount.value > 0)

    // 获取特定key的加载状态
    const isLoading = (key: string): boolean => {
        return loadingStates.value.get(key) || false
    }

    // 设置加载状态
    const setLoading = (key: string, loading: boolean): void => {
        if (loading) {
            loadingStates.value.set(key, true)
        } else {
            loadingStates.value.delete(key)
        }
    }

    // 批量设置加载状态
    const setMultipleLoading = (states: Record<string, boolean>): void => {
        Object.entries(states).forEach(([key, loading]) => {
            setLoading(key, loading)
        })
    }

    // 清除特定key的加载状态
    const clearLoading = (key: string): void => {
        loadingStates.value.delete(key)
    }

    // 清除所有加载状态
    const clearAllLoading = (): void => {
        loadingStates.value.clear()
    }

    // 获取所有活跃的加载状态keys
    const getActiveLoadingKeys = (): string[] => {
        const activeKeys: string[] = []
        for (const [key, isLoading] of loadingStates.value.entries()) {
            if (isLoading) {
                activeKeys.push(key)
            }
        }
        return activeKeys
    }

    // 获取加载状态统计信息
    const getLoadingStats = (): LoadingStats => {
        return {
            total: loadingStates.value.size,
            active: activeLoadingCount.value,
            activeKeys: getActiveLoadingKeys()
        }
    }

    return {
        // 状态
        loadingStates: readonly(loadingStates),
        activeLoadingCount,
        hasActiveLoading,

        // 方法
        isLoading,
        setLoading,
        setMultipleLoading,
        clearLoading,
        clearAllLoading,
        getActiveLoadingKeys,
        getLoadingStats
    }
})