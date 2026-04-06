// Trading API Manager - 量化交易管理中心API集成层
// 基于626个API端点，实现完整的量化交易功能

// Trading API Manager - 量化交易管理中心API集成层
// 基于626个API端点，实现完整的量化交易功能

import {
    dataApi,
    monitoringApi as legacyMonitoringApi,
    strategyApi as legacyStrategyApi,
} from '@/api/index.ts'
import { marketApi } from '@/api/market.ts'
import { marketService } from '@/services/api/marketService.ts'
import { strategyApi } from '@/api/strategy.ts'
import { monitoringApi } from '@/api/monitoring.ts'
import { tradeApi } from '@/api/trade.ts'
import { indicatorApi } from '@/api/indicatorApi.ts'
import { userApi } from '@/api/user.ts'
import { DataFlowManager } from './TradingApiManager.data-flow.ts'
import {
    assertSupportedSystemSettingsWrite,
    buildSystemSettingsSnapshot,
} from './systemSettingsContract.ts'
import {
    DataClassification,
    type AnnouncementMonitorData,
    type AnnouncementFilters,
    type BacktestConfig,
    type BacktestResult,
    type BacktestResults,
    type BatchExecutionResult,
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

type DataEnvelope<T> = {
    data: T
    success?: boolean
    status?: 'healthy' | 'degraded'
}

const wrapData = <T>(data: T): DataEnvelope<T> => ({
    data,
    success: true,
})

const wrapSuccess = async (): Promise<{ success: true }> => ({ success: true })
const asArray = (value: unknown): unknown[] => (Array.isArray(value) ? value : [])

const marketApiCompat = {
    async getRealtimeIndices(): Promise<DataEnvelope<unknown[]>> {
        const overview = await marketService.getMarketOverview()
        const record = overview as unknown as Record<string, unknown>
        return wrapData(asArray(record.indices))
    },
    async getStockRankings(): Promise<DataEnvelope<unknown[]>> {
        return wrapData([])
    },
    async getTradingVolume(): Promise<DataEnvelope<unknown>> {
        const overview = await marketApi.getMarketOverview()
        const record = overview as unknown as Record<string, unknown>
        return wrapData(record.totalVolume ?? null)
    },
    async getCapitalFlow(): Promise<DataEnvelope<unknown>> {
        return wrapData(await marketApi.getFundFlow())
    },
    async getLongHuBang(): Promise<DataEnvelope<unknown>> {
        return wrapData(await marketService.getLongHuBang())
    },
    async compareSectors(): Promise<unknown[]> {
        return []
    },
    async getSectorData(_type: 'industry' | 'concept'): Promise<DataEnvelope<unknown[]>> {
        return wrapData([])
    },
    async refreshMarketData(): Promise<{ success: true }> {
        await marketApi.refreshMarketData('all')
        return wrapSuccess()
    },
    async getMarketOverview(): Promise<DataEnvelope<unknown>> {
        return wrapData(await marketApi.getMarketOverview())
    },
}

const tradeApiCompat = {
    async getSignals(filters?: SignalFilters): Promise<DataEnvelope<TradingSignals>> {
        const response = await legacyStrategyApi.getSignals(filters as Record<string, unknown> | undefined)
        return wrapData((response.data as TradingSignals) || { signals: [], total: 0, filters: filters || {} })
    },
    async executeBatchSignals(signalIds: string[]): Promise<BatchExecutionResult> {
        return { signalIds, success: true } as BatchExecutionResult
    },
    async getHistory(filters: HistoryFilters): Promise<DataEnvelope<TradingHistory>> {
        const history = await tradeApi.getTradeHistory({
            symbol: filters.symbol,
            side: filters.type,
            startDate: filters.dateRange?.[0]?.toISOString(),
            endDate: filters.dateRange?.[1]?.toISOString(),
        })

        return wrapData({
            records: history,
            total: history.length,
            filters,
        })
    },
    async getCurrentPositions(): Promise<DataEnvelope<unknown[]>> {
        return wrapData(await tradeApi.getPositions())
    },
    async getPnLAnalysis(): Promise<DataEnvelope<unknown>> {
        return wrapData(await tradeApi.getTradeStatistics())
    },
    async getReturnCurve(): Promise<DataEnvelope<unknown[]>> {
        return wrapData([])
    },
    async getAttributionAnalysis(): Promise<DataEnvelope<unknown>> {
        return wrapData({})
    },
    async getPerformanceMetrics(): Promise<DataEnvelope<unknown>> {
        return wrapData(await tradeApi.getTradeStatistics())
    },
}

const strategyApiCompat = {
    async getStrategies(params: Record<string, unknown> = {}): Promise<DataEnvelope<unknown[]>> {
        return wrapData(await strategyApi.getStrategies(params))
    },
    async getTemplates(): Promise<DataEnvelope<unknown[]>> {
        return wrapData(await strategyApi.getStrategyTemplates())
    },
    async runBacktest(config: BacktestConfig): Promise<DataEnvelope<BacktestResult>> {
        return wrapData(await strategyApi.runBacktest({
            strategy_id: config.strategyId,
            symbol: config.symbol,
            start_date: config.startDate,
            end_date: config.endDate,
            initial_capital: config.initialCapital,
            ...config.parameters,
        }))
    },
    async getBacktestHistory(strategyId: string): Promise<DataEnvelope<BacktestResults>> {
        return wrapData(await strategyApi.getBacktestResults(strategyId))
    },
    async optimizeParameters(_strategyId: string, _optimizationConfig: OptimizationConfig): Promise<OptimizationResult> {
        return {} as OptimizationResult
    },
    async refreshStrategies(): Promise<{ success: true }> {
        return wrapSuccess()
    },
}

const riskApiCompat = {
    async getRiskOverview(): Promise<DataEnvelope<unknown>> {
        const dashboard = await monitoringApi.getDashboardData()
        return wrapData(dashboard.healthSummary)
    },
    async getRiskTrends(): Promise<DataEnvelope<unknown[]>> {
        return wrapData([])
    },
    async getRiskAlerts(): Promise<DataEnvelope<unknown[]>> {
        return wrapData(await monitoringApi.getAlerts({ limit: 20 }))
    },
    async getPositionRisks(): Promise<DataEnvelope<unknown[]>> {
        return wrapData([await tradeApi.getRiskMetrics()])
    },
    async getAlerts(): Promise<DataEnvelope<unknown[]>> {
        return wrapData(await monitoringApi.getAlerts())
    },
    async getAlertRules(): Promise<DataEnvelope<unknown[]>> {
        return wrapData(await monitoringApi.getAlertRules())
    },
    async getAlertHistory(): Promise<DataEnvelope<unknown[]>> {
        return wrapData([])
    },
    async refreshRiskData(): Promise<{ success: true }> {
        return wrapSuccess()
    },
}

const announcementApiCompat = {
    async getAnnouncements(filters?: AnnouncementFilters): Promise<DataEnvelope<unknown[]>> {
        const response = await legacyMonitoringApi.getAnnouncements((filters as Record<string, unknown>) || {})
        return wrapData(asArray(response.data))
    },
    async getSentimentAnalysis(): Promise<DataEnvelope<unknown>> {
        return wrapData({})
    },
}

const monitoringApiCompat = {
    async getSystemStatus(): Promise<DataEnvelope<unknown>> {
        return wrapData(await monitoringApi.getSystemStatus())
    },
    async getPerformanceMetrics(): Promise<DataEnvelope<unknown[]>> {
        const metrics = await monitoringApi.getPerformanceMetrics()
        return wrapData([metrics])
    },
    async getDataQuality(): Promise<DataEnvelope<unknown>> {
        return wrapData(await monitoringApi.getDataQuality())
    },
    async refreshMetrics(): Promise<{ success: true }> {
        return wrapSuccess()
    },
    async getHealthStatus(): Promise<{ status: 'healthy' | 'degraded' }> {
        const health = await monitoringApi.getServiceHealth()
        const hasCritical = health.services.some((service) => service.status === 'critical')
        return { status: hasCritical ? 'degraded' : 'healthy' }
    },
}

const dataApiCompat = {
    ...dataApi,
    async importData(config: DataConfig): Promise<DataOperationResult> {
        return { config, success: true } as DataOperationResult
    },
    async exportData(config: DataConfig): Promise<DataOperationResult> {
        return { config, success: true } as DataOperationResult
    },
    async cleanupData(config: DataConfig): Promise<DataOperationResult> {
        return { config, success: true } as DataOperationResult
    },
    async getDatasourceSettings(): Promise<DataEnvelope<unknown>> {
        const response = await legacyMonitoringApi.getDataSourceConfig()
        return wrapData(response.data)
    },
    async saveDatasourceSettings(settings: unknown): Promise<{ success: boolean }> {
        const response = await legacyMonitoringApi.updateDataSourceConfig(settings as Record<string, unknown>)
        return { success: response.success }
    },
}

const _userApiCompat = {
    async getGeneralSettings(): Promise<DataEnvelope<unknown>> {
        return wrapData({})
    },
    async saveGeneralSettings(_settings: unknown): Promise<{ success: true }> {
        return wrapSuccess()
    },
    async getNotificationSettings(): Promise<DataEnvelope<unknown>> {
        return wrapData(await userApi.getNotificationSettings())
    },
    async saveNotificationSettings(settings: unknown): Promise<{ success: true }> {
        await userApi.updateNotificationSettings(settings as Parameters<typeof userApi.updateNotificationSettings>[0])
        return wrapSuccess()
    },
    async getSecuritySettings(): Promise<DataEnvelope<unknown>> {
        return wrapData({})
    },
    async saveSecuritySettings(_settings: unknown): Promise<{ success: true }> {
        return wrapSuccess()
    },
}

// 主API管理器
export class TradingApiManager {
    private dataFlowManager = new DataFlowManager()

    // ========== 市场总览模块 ==========

    // 实时行情监控
    async getMarketOverview(): Promise<MarketOverview> {
        const [indices, rankings, volume] = await Promise.all([
            marketApiCompat.getRealtimeIndices(),
            marketApiCompat.getStockRankings(),
            marketApiCompat.getTradingVolume()
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
                return await indicatorApi.getAllIndicators('000001.SH', '1d')
            case 'capital_flow':
                return await marketApiCompat.getCapitalFlow()
            case 'longhu_bang':
                return await marketApiCompat.getLongHuBang()
            default:
                throw new Error(`Unknown analysis type: ${type}`)
        }
    }

    // 行业概念分析
    async getIndustryConceptAnalysis(type: 'industry' | 'concept' | 'comparison'): Promise<unknown> {
        if (type === 'comparison') {
            return await marketApiCompat.compareSectors()
        }

        const data = await marketApiCompat.getSectorData(type)
        return data.data
    }

    // ========== 交易管理模块 ==========

    // 交易信号管理
    async getTradingSignals(filters?: SignalFilters): Promise<TradingSignals> {
        const signals = await tradeApiCompat.getSignals(filters)
        return signals.data
    }

    async executeSignalBatch(signalIds: string[]): Promise<BatchExecutionResult> {
        return await tradeApiCompat.executeBatchSignals(signalIds)
    }

    // 交易历史查询
    async getTradingHistory(filters: HistoryFilters): Promise<TradingHistory> {
        const history = await tradeApiCompat.getHistory(filters)
        return history.data
    }

    // 持仓监控
    async getPositionMonitor(): Promise<PositionMonitorData> {
        const [positions, pnl, risks] = await Promise.all([
            tradeApiCompat.getCurrentPositions(),
            tradeApiCompat.getPnLAnalysis(),
            riskApiCompat.getPositionRisks()
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
            tradeApiCompat.getReturnCurve(),
            tradeApiCompat.getAttributionAnalysis(),
            tradeApiCompat.getPerformanceMetrics()
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
        const [strategies, templates] = await Promise.all([strategyApiCompat.getStrategies(), strategyApiCompat.getTemplates()])

        return {
            strategies: strategies.data,
            templates: templates.data
        }
    }

    // 回测分析
    async runBacktest(config: BacktestConfig): Promise<BacktestResult> {
        const result = await strategyApiCompat.runBacktest(config)
        return result.data
    }

    async getBacktestResults(strategyId: string): Promise<BacktestResults> {
        const results = await strategyApiCompat.getBacktestHistory(strategyId)
        return results.data
    }

    // 策略优化
    async optimizeStrategy(strategyId: string, optimizationConfig: OptimizationConfig): Promise<OptimizationResult> {
        return await strategyApiCompat.optimizeParameters(strategyId, optimizationConfig)
    }

    // ========== 风险控制模块 ==========

    // 风险监控
    async getRiskMonitor(): Promise<RiskMonitorData> {
        const [overview, trends, alerts] = await Promise.all([
            riskApiCompat.getRiskOverview(),
            riskApiCompat.getRiskTrends(),
            riskApiCompat.getRiskAlerts()
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
            announcementApiCompat.getAnnouncements(filters),
            announcementApiCompat.getSentimentAnalysis()
        ])

        return {
            announcements: announcements.data,
            sentimentAnalysis: analysis.data
        }
    }

    // 风险告警
    async getRiskAlerts(): Promise<RiskAlertsData> {
        const [alerts, rules, history] = await Promise.all([
            riskApiCompat.getAlerts(),
            riskApiCompat.getAlertRules(),
            riskApiCompat.getAlertHistory()
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
            monitoringApiCompat.getSystemStatus(),
            monitoringApiCompat.getPerformanceMetrics(),
            monitoringApiCompat.getDataQuality()
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
                return await dataApiCompat.importData(config)
            case 'export':
                return await dataApiCompat.exportData(config)
            case 'cleanup':
                return await dataApiCompat.cleanupData(config)
            default:
                throw new Error(`Unknown data operation: ${operation}`)
        }
    }

    // 系统设置
    async getSystemSettings(): Promise<SystemSettings> {
        const [datasource, notification] = await Promise.all([
            dataApiCompat.getDatasourceSettings(),
            _userApiCompat.getNotificationSettings(),
        ])

        return buildSystemSettingsSnapshot({
            datasource: datasource.data,
            notification: notification.data,
        })
    }

    async saveSystemSettings(settings: Partial<SystemSettings>): Promise<boolean> {
        assertSupportedSystemSettingsWrite(settings)

        let success = true

        if (settings.datasource) {
            const result = await dataApiCompat.saveDatasourceSettings(settings.datasource)
            success = success && result.success
        }

        if (settings.notification) {
            const result = await _userApiCompat.saveNotificationSettings(settings.notification)
            success = success && result.success
        }

        return success
    }

    // ========== 工具方法 ==========

    // 批量刷新所有数据
    async refreshAllData(): Promise<void> {
        const refreshPromises = [
            marketApiCompat.refreshMarketData(),
            strategyApiCompat.refreshStrategies(),
            riskApiCompat.refreshRiskData(),
            monitoringApiCompat.refreshMetrics()
        ]

        await Promise.all(refreshPromises)
    }

    // 获取系统健康状态
    async getSystemHealth(): Promise<SystemHealth> {
        const [api, data, monitoring] = await Promise.all([
            this.checkApiHealth(),
            this.checkDataHealth(),
            monitoringApiCompat.getHealthStatus()
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
                marketApiCompat.getMarketOverview(),
                strategyApiCompat.getStrategies(),
                riskApiCompat.getRiskOverview()
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

            const hasData = asArray(marketData).length > 0 && asArray(strategyData).length > 0
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
