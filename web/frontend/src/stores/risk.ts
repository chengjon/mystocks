// Risk Monitor Store - 专注于风险监控
// 负责风险监控、公告监控、风险告警等风险相关数据

import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { tradingApiManager } from '@/services/TradingApiManager'
import type {
    RiskMonitorData,
    AnnouncementMonitorData,
    RiskAlertsData
} from '@/services/TradingApiManager'

interface RiskState {
    riskMonitor: RiskMonitorData | null
    announcementMonitor: AnnouncementMonitorData | null
    riskAlerts: RiskAlertsData | null
    lastUpdateTime: string
}

export const useRiskStore = defineStore('risk', () => {
    const state = reactive<RiskState>({
        riskMonitor: null,
        announcementMonitor: null,
        riskAlerts: null,
        lastUpdateTime: new Date().toLocaleTimeString('zh-CN')
    })

    const loadRiskMonitor = async () => {
        const data = await tradingApiManager.getRiskMonitor()
        state.riskMonitor = data
        state.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
    }

    const loadAnnouncementMonitor = async () => {
        // 假设有一个获取公告监控的API
        // const data = await tradingApiManager.getAnnouncementMonitor()
        // state.announcementMonitor = data
    }

    const loadRiskAlerts = async () => {
        // 假设有一个获取风险告警的API
        // const data = await tradingApiManager.getRiskAlerts()
        // state.riskAlerts = data
    }

    return {
        state,
        loadRiskMonitor,
        loadAnnouncementMonitor,
        loadRiskAlerts
    }
})