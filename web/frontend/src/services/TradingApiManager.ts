// Trading API Manager - 量化交易管理中心API集成层
// 基于626个API端点，实现完整的量化交易功能

// @ts-nocheck
// Trading API Manager - 量化交易管理中心API集成层
// 基于626个API端点，实现完整的量化交易功能

import {
    marketApi,
    strategyApi,
    riskApi,
    monitoringApi,
    dataApi,
    tradeApi,
    indicatorApi,
    userApi,
    announcementApi,
    _watchlistApi
} from '@/api/index.ts'
import { DataFlowManager } from './TradingApiManager.data-flow.ts'
import {
    DataClassification,
    type AnnouncementFilters,
    type BacktestConfig,
    type BacktestResult,
    type BacktestResults,
    type DataConfig,
    type DataOperation,
    type DataOperationResult,
    type HistoryFilters,
    type MarketOverview,
    type MonitoringDashboardData,
    type OptimizationConfig,
    type OptimizationResult,
    type PerformanceAnalysis,
    type PositionMonitorData,
    type RealtimeUpdateConfig,
    type RiskAlertsData,
    type RiskMonitorData,
    type SignalFilters,
    type StrategyManagementData,
    type SystemHealth,
    type SystemSettings,
    type TradingHistory,
    type TradingSignals
} from './TradingApiManager.types.ts'

// 主API管理器
export class TradingApiManager {
    private dataFlowManager = new DataFlowManager()

    // ========== 市场总览模块 ==========

    // 实时行情监控
    async getMarketOverview(): Promise<MarketOverview> {
        const [indices, rankings, volume] = await Promise.all([
            marketApi.getRealtimeIndices(),
            marketApi.getStockRankings(),
            marketApi.getTradingVolume()
        ])

        return {
            indices: indices.data,
            rankings: rankings.data,
            volume: volume.data,
            lastUpdate: new Date().toISOString()
        }
    }

    // 市场数据分析
    async getMarketAnalysis(type: 'technical' | 'capital_flow' | 'longhu_bang'): Promise<unknown> {
        switch (type) {
            case 'technical':
                return await indicatorApi.getTechnicalAnalysis()
            case 'capital_flow':
                return await marketApi.getCapitalFlow()
            case 'longhu_bang':
                return await marketApi.getLongHuBang()
            default:
                throw new Error(`Unknown analysis type: ${type}`)
        }
    }

    // 行业概念分析
    async getIndustryConceptAnalysis(type: 'industry' | 'concept' | 'comparison'): Promise<unknown> {
        if (type === 'comparison') {
            return await marketApi.compareSectors()
        }

        const data = await marketApi.getSectorData(type)
        return data.data
    }

    // ========== 交易管理模块 ==========

    // 交易信号管理
    async getTradingSignals(filters?: SignalFilters): Promise<TradingSignals> {
        const signals = await tradeApi.getSignals(filters)
        return signals.data
    }

    async executeSignalBatch(signalIds: string[]): Promise<BatchExecutionResult> {
        return await tradeApi.executeBatchSignals(signalIds)
    }

    // 交易历史查询
    async getTradingHistory(filters: HistoryFilters): Promise<TradingHistory> {
        const history = await tradeApi.getHistory(filters)
        return history.data
    }

    // 持仓监控
    async getPositionMonitor(): Promise<PositionMonitorData> {
        const [positions, pnl, risks] = await Promise.all([
            tradeApi.getCurrentPositions(),
            tradeApi.getPnLAnalysis(),
            riskApi.getPositionRisks()
        ])

        return {
            positions: positions.data,
            pnlAnalysis: pnl.data,
            riskMetrics: risks.data
        }
    }

    // 绩效分析
    async getPerformanceAnalysis(): Promise<PerformanceAnalysis> {
        const [returns, attribution, metrics] = await Promise.all([
            tradeApi.getReturnCurve(),
            tradeApi.getAttributionAnalysis(),
            tradeApi.getPerformanceMetrics()
        ])

        return {
            returnCurve: returns.data,
            attribution: attribution.data,
            metrics: metrics.data
        }
    }

    // ========== 策略中心模块 ==========

    // 策略管理
    async getStrategyManagement(): Promise<StrategyManagementData> {
        const [strategies, templates] = await Promise.all([strategyApi.getStrategies(), strategyApi.getTemplates()])

        return {
            strategies: strategies.data,
            templates: templates.data
        }
    }

    // 回测分析
    async runBacktest(config: BacktestConfig): Promise<BacktestResult> {
        const result = await strategyApi.runBacktest(config)
        return result.data
    }

    async getBacktestResults(strategyId: string): Promise<BacktestResults[]> {
        const results = await strategyApi.getBacktestHistory(strategyId)
        return results.data
    }

    // 策略优化
    async optimizeStrategy(strategyId: string, optimizationConfig: OptimizationConfig): Promise<OptimizationResult> {
        return await strategyApi.optimizeParameters(strategyId, optimizationConfig)
    }

    // ========== 风险控制模块 ==========

    // 风险监控
    async getRiskMonitor(): Promise<RiskMonitorData> {
        const [overview, trends, alerts] = await Promise.all([
            riskApi.getRiskOverview(),
            riskApi.getRiskTrends(),
            riskApi.getRiskAlerts()
        ])

        return {
            overview: overview.data,
            trends: trends.data,
            alerts: alerts.data
        }
    }

    // 公告监控
    async getAnnouncementMonitor(filters?: AnnouncementFilters): Promise<AnnouncementMonitorData> {
        const [announcements, analysis] = await Promise.all([
            announcementApi.getAnnouncements(filters),
            announcementApi.getSentimentAnalysis()
        ])

        return {
            announcements: announcements.data,
            sentimentAnalysis: analysis.data
        }
    }

    // 风险告警
    async getRiskAlerts(): Promise<RiskAlertsData> {
        const [alerts, rules, history] = await Promise.all([
            riskApi.getAlerts(),
            riskApi.getAlertRules(),
            riskApi.getAlertHistory()
        ])

        return {
            activeAlerts: alerts.data,
            alertRules: rules.data,
            alertHistory: history.data
        }
    }

    // ========== 系统管理模块 ==========

    // 监控面板
    async getMonitoringDashboard(): Promise<MonitoringDashboardData> {
        const [system, performance, quality] = await Promise.all([
            monitoringApi.getSystemStatus(),
            monitoringApi.getPerformanceMetrics(),
            monitoringApi.getDataQuality()
        ])

        return {
            systemStatus: system.data,
            performanceMetrics: performance.data,
            dataQuality: quality.data
        }
    }

    // 数据管理
    async manageData(operation: DataOperation, config: DataConfig): Promise<DataOperationResult> {
        switch (operation) {
            case 'import':
                return await dataApi.importData(config)
            case 'export':
                return await dataApi.exportData(config)
            case 'cleanup':
                return await dataApi.cleanupData(config)
            default:
                throw new Error(`Unknown data operation: ${operation}`)
        }
    }

    // 系统设置
    async getSystemSettings(): Promise<SystemSettings> {
        const [general, datasource, notification, security] = await Promise.all([
            userApi.getGeneralSettings(),
            dataApi.getDatasourceSettings(),
            userApi.getNotificationSettings(),
            userApi.getSecuritySettings()
        ])

        return {
            general: general.data,
            datasource: datasource.data,
            notification: notification.data,
            security: security.data
        }
    }

    async saveSystemSettings(settings: Partial<SystemSettings>): Promise<boolean> {
        const promises = []

        if (settings.general) promises.push(userApi.saveGeneralSettings(settings.general))
        if (settings.datasource) promises.push(dataApi.saveDatasourceSettings(settings.datasource))
        if (settings.notification) promises.push(userApi.saveNotificationSettings(settings.notification))
        if (settings.security) promises.push(userApi.saveSecuritySettings(settings.security))

        const results = await Promise.all(promises)
        return results.every(result => result.success)
    }

    // ========== 工具方法 ==========

    // 批量刷新所有数据
    async refreshAllData(): Promise<void> {
        const refreshPromises = [
            marketApi.refreshMarketData(),
            strategyApi.refreshStrategies(),
            riskApi.refreshRiskData(),
            monitoringApi.refreshMetrics()
        ]

        await Promise.all(refreshPromises)
    }

    // 获取系统健康状态
    async getSystemHealth(): Promise<SystemHealth> {
        const [api, data, monitoring] = await Promise.all([
            this.checkApiHealth(),
            this.checkDataHealth(),
            monitoringApi.getHealthStatus()
        ])

        return {
            api: api.status,
            data: data.status,
            monitoring: monitoring.status,
            overall:
                api.status === 'healthy' && data.status === 'healthy' && monitoring.status === 'healthy'
                    ? 'healthy'
                    : 'degraded'
        }
    }

    private async checkApiHealth(): Promise<{ status: 'healthy' | 'degraded' }> {
        try {
            // 检查核心API端点
            const responses = await Promise.allSettled([
                marketApi.getMarketOverview(),
                strategyApi.getStrategies(),
                riskApi.getRiskOverview()
            ])

            const successCount = responses.filter(r => r.status === 'fulfilled').length
            return { status: successCount >= 2 ? 'healthy' : 'degraded' }
        } catch {
            return { status: 'degraded' }
        }
    }

    private async checkDataHealth(): Promise<{ status: 'healthy' | 'degraded' }> {
        try {
            // 检查数据连接和质量
            const [marketData, strategyData] = await Promise.all([
                this.dataFlowManager.loadData(DataClassification.SYMBOLS_INFO, { limit: 1 }),
                this.dataFlowManager.loadData(DataClassification.STRATEGY_PARAMS, { limit: 1 })
            ])

            const hasData = marketData && marketData.length > 0 && strategyData && strategyData.length > 0
            return { status: hasData ? 'healthy' : 'degraded' }
        } catch {
            return { status: 'degraded' }
        }
    }

    // 设置实时数据更新
    setupRealtimeUpdates(updates: RealtimeUpdateConfig[]): () => void {
        const cleanupFunctions: (() => void)[] = []

        updates.forEach(update => {
            const cleanup = this.dataFlowManager.setupRealtimeUpdates(update.channel, update.callback)
            cleanupFunctions.push(cleanup)
        })

        return () => {
            cleanupFunctions.forEach(cleanup => cleanup())
        }
    }
}

// 导出单例实例
export const tradingApiManager = new TradingApiManager()
export { DataClassification }
export type {
    AnnouncementFilters,
    BacktestConfig,
    BacktestResult,
    BacktestResults,
    DataConfig,
    DataOperation,
    DataOperationResult,
    HistoryFilters,
    MarketOverview,
    MonitoringDashboardData,
    OptimizationConfig,
    OptimizationResult,
    PerformanceAnalysis,
    PositionMonitorData,
    RealtimeUpdateConfig,
    RiskAlertsData,
    RiskMonitorData,
    SignalFilters,
    StrategyManagementData,
    SystemHealth,
    SystemSettings,
    TradingHistory,
    TradingSignals
} from './TradingApiManager.types.ts'
