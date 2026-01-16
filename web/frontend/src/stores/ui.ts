// UI State Store - 专注于UI状态管理
// 负责界面功能切换、节点展开状态、加载状态、缓存管理等UI相关状态

import { defineStore } from 'pinia'
import { ref, reactive, computed, watch } from 'vue'

interface CachedData<T = any> {
    data: T
    timestamp: number
    ttl: number
}

interface RealtimeUpdate {
    type: string
    data: any
    timestamp: number
}

interface UiState {
    // 功能状态
    activeFunction: string
    expandedNodes: Set<string>
    loadingStates: Record<string, boolean>

    // 数据缓存
    cache: Map<string, CachedData>

    // 最后更新时间
    lastUpdateTime: string
}

export const useUiStore = defineStore('ui', () => {
    // 从localStorage初始化UI状态
    const savedActiveFunction = localStorage.getItem('ui_activeFunction')
    const savedExpandedNodes = localStorage.getItem('ui_expandedNodes')

    const state = reactive<UiState>({
        activeFunction: savedActiveFunction || 'market-overview',
        expandedNodes: savedExpandedNodes ? new Set(JSON.parse(savedExpandedNodes)) : new Set(['market-overview', 'trading-management']),
        loadingStates: {},
        cache: new Map(),
        lastUpdateTime: new Date().toLocaleTimeString('zh-CN')
    })

    // 持久化activeFunction
    watch(() => state.activeFunction, (newValue) => {
        localStorage.setItem('ui_activeFunction', newValue)
    }, { immediate: true })

    // 持久化expandedNodes
    watch(() => state.expandedNodes, (newValue) => {
        localStorage.setItem('ui_expandedNodes', JSON.stringify(Array.from(newValue)))
    }, { immediate: true, deep: true })

    // 计算属性
    const isLoading = computed((): boolean => {
        return Object.values(state.loadingStates).some(loading => loading)
    })

    const hasValidCache = computed(() => (key: string, maxAge: number = 300000): boolean => {
        const cached = state.cache.get(key)
        if (!cached) return false
        return Date.now() - cached.timestamp < maxAge
    })

    // 方法
    const switchActiveFunction = (functionKey: string): void => {
        state.activeFunction = functionKey
    }

    const toggleNodeExpansion = (nodeKey: string): void => {
        if (state.expandedNodes.has(nodeKey)) {
            state.expandedNodes.delete(nodeKey)
        } else {
            state.expandedNodes.add(nodeKey)
        }
    }

    const setLoading = (key: string, loading: boolean): void => {
        if (loading) {
            state.loadingStates[key] = true
        } else {
            delete state.loadingStates[key]
        }
    }

    const cacheData = <T>(key: string, data: T, ttl: number = 300000): void => {
        state.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl
        } as CachedData<T>)
    }

    const getCachedData = <T>(key: string): T | null => {
        const cached = state.cache.get(key)
        if (!cached) return null

        if (Date.now() - cached.timestamp > cached.ttl) {
            state.cache.delete(key)
            return null
        }

        return cached.data
    }

    const clearCache = (key?: string): void => {
        if (key) {
            state.cache.delete(key)
        } else {
            state.cache.clear()
        }
    }

    const setupRealtimeUpdates = (updates: RealtimeUpdate[]): any => {
        // 这里可以实现实时更新逻辑
        console.log('Setting up realtime updates:', updates)
        return {
            start: () => console.log('Started realtime updates'),
            stop: () => console.log('Stopped realtime updates')
        }
    }

    return {
        // 状态
        state,

        // 计算属性
        isLoading,
        hasValidCache,

        // 方法
        switchActiveFunction,
        toggleNodeExpansion,
        setLoading,
        cacheData,
        getCachedData,
        clearCache,
        setupRealtimeUpdates
    }
})