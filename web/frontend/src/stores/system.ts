// System Monitor Store - 专注于系统监控
// 负责监控面板、系统设置、系统健康状态等系统相关数据

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { tradingApiManager } from '@/services/TradingApiManager'
import type {
    MonitoringDashboardData,
    SystemSettings,
    SystemHealth
} from '@/services/TradingApiManager'

interface SystemState {
    monitoringDashboard: MonitoringDashboardData | null
    systemSettings: SystemSettings | null
    systemHealth: SystemHealth | null
    systemConfig: Record<string, any> | null
    lastUpdateTime: string
}

export const useSystemStore = defineStore('system', () => {
    const state = reactive<SystemState>({
        monitoringDashboard: null,
        systemSettings: null,
        systemHealth: null,
        systemConfig: null,
        lastUpdateTime: new Date().toLocaleTimeString('zh-CN')
    })

    const loadMonitoringDashboard = async () => {
        const data = await tradingApiManager.getMonitoringDashboard()
        state.monitoringDashboard = data
        state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
    }

    const loadSystemSettings = async () => {
        const data = await tradingApiManager.getSystemSettings()
        state.systemSettings = data
        state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
    }

    const checkSystemHealth = async () => {
        try {
            const health = await tradingApiManager.getSystemHealth()
            state.systemHealth = health
            return health
        } catch (error) {
            console.error('Failed to check system health:', error)
            state.systemHealth = {
                api: 'degraded',
                data: 'degraded',
                monitoring: 'degraded',
                overall: 'degraded'
            }
            throw error
        }
    }

    const updateSystemConfig = (config: Record<string, any>) => {
        state.systemConfig = { ...state.systemConfig, ...config }
        // 可以选择持久化到localStorage
        localStorage.setItem('systemConfig', JSON.stringify(state.systemConfig))
    }

    // 初始化时从localStorage加载配置
    const initialize = () => {
        const savedConfig = localStorage.getItem('systemConfig')
        if (savedConfig) {
            try {
                state.systemConfig = JSON.parse(savedConfig)
            } catch (error) {
                console.warn('Failed to parse saved system config:', error)
                state.systemConfig = {}
            }
        }
    }

    // 初始化
    initialize()

    return {
        state,
        loadMonitoringDashboard,
        loadSystemSettings,
        checkSystemHealth,
        updateSystemConfig,
        initialize
    }
})