<template>
    <div class="artdeco-trading-center">
        <!-- ArtDeco 页面头部 -->
        <ArtDecoHeader
            title="量化交易管理中心"
            subtitle="集成市场分析、策略交易、风险控制的全功能量化平台"
            :show-status="true"
            :status-text="systemStatus"
            :status-type="statusType"
        >
            <template #actions>
                <ArtDecoButton variant="outline" size="sm" @click="refreshAllData" :loading="refreshing">
                    <ArtDecoIcon name="refresh" />
                    刷新数据
                </ArtDecoButton>

                <ArtDecoButton variant="default" size="sm" @click="openSettings">
                    <ArtDecoIcon name="settings" />
                    系统设置
                </ArtDecoButton>
            </template>
        </ArtDecoHeader>

        <!-- 主内容区域 -->
        <div class="trading-center-content">
            <!-- 左侧功能树导航 -->
            <div class="function-tree-panel">
                <ArtDecoFunctionTree
                    v-model="activeFunction"
                    :tree-data="functionTreeData"
                    :expanded-nodes="expandedNodes"
                    @select="handleFunctionSelect"
                    @expand="handleNodeExpand"
                />
            </div>

            <!-- 右侧内容区域 -->
            <div class="content-panel">
                <!-- 面包屑导航 -->
                <ArtDecoBreadcrumb :breadcrumbs="currentBreadcrumbs" @navigate="handleBreadcrumbNavigate" />

                <!-- 动态内容区域 -->
                <div class="dynamic-content">
                    <component
                        :is="currentComponent"
                        v-bind="currentComponentProps"
                        @action="handleComponentAction"
                        @navigate="handleInternalNavigate"
                    />
                </div>
            </div>
        </div>

        <!-- 底部状态栏 -->
        <ArtDecoFooter>
            <template #left>
                <div class="status-indicators">
                    <ArtDecoStatusIndicator label="API状态" :status="apiStatus" :value="apiStatusText" />
                    <ArtDecoStatusIndicator label="数据质量" :status="dataQualityStatus" :value="dataQualityScore" />
                    <ArtDecoStatusIndicator label="系统负载" :status="systemLoadStatus" :value="systemLoadPercent" />
                </div>
            </template>

            <template #right>
                <div class="footer-info">
                    <span class="last-update">最后更新: {{ lastUpdateTime }}</span>
                    <span class="version-info">v{{ version }}</span>
                </div>
            </template>
        </ArtDecoFooter>

        <!-- 全局加载遮罩 -->
        <ArtDecoLoadingOverlay
            v-if="globalLoading"
            :progress="globalLoadingProgress"
            message="正在加载量化交易数据..."
        />
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
    import { useTradingStore } from '@/stores/trading'
    import { useAuthStore } from '@/stores/auth'
    import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
    import ArtDecoFunctionTree from '@/components/artdeco/core/ArtDecoFunctionTree.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoBreadcrumb from '@/components/artdeco/core/ArtDecoBreadcrumb.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoFooter from '@/components/artdeco/core/ArtDecoFooter.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
    import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoStatusIndicator from '@/components/artdeco/core/ArtDecoStatusIndicator.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoLoadingOverlay from '@/components/artdeco/core/ArtDecoLoadingOverlay.vue'

    // 导入所有功能组件
    // @ts-ignore - Component not implemented yet
    import ArtDecoMarketOverview from './components/market/ArtDecoMarketOverview.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoRealtimeMonitor from './components/market/ArtDecoRealtimeMonitor.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoMarketAnalysis from './components/market/ArtDecoMarketAnalysis.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoIndustryAnalysis from './components/market/ArtDecoIndustryAnalysis.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoSignalsView from './components/trading/ArtDecoSignalsView.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoHistoryView from './components/trading/ArtDecoHistoryView.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoPositionMonitor from './components/trading/ArtDecoPositionMonitor.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoPerformanceAnalysis from './components/trading/ArtDecoPerformanceAnalysis.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoStrategyManagement from './components/strategy/ArtDecoStrategyManagement.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoBacktestAnalysis from './components/strategy/ArtDecoBacktestAnalysis.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoStrategyOptimization from './components/strategy/ArtDecoStrategyOptimization.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoRiskMonitor from './components/risk/ArtDecoRiskMonitor.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoAnnouncementMonitor from './components/risk/ArtDecoAnnouncementMonitor.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoRiskAlerts from './components/risk/ArtDecoRiskAlerts.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoMonitoringDashboard from './components/system/ArtDecoMonitoringDashboard.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoDataManagement from './components/system/ArtDecoDataManagement.vue'
    import ArtDecoSystemSettings from './components/system/ArtDecoSystemSettings.vue'

    // 组合式API
    const tradingStore = useTradingStore()
    const authStore = useAuthStore()

    // 响应式数据
    const activeFunction = ref('market-overview')
    const expandedNodes = ref(
        new Set(['market-overview', 'trading-management', 'strategy-center', 'risk-control', 'system-management'])
    )
    const refreshing = ref(false)
    const globalLoading = ref(false)
    const globalLoadingProgress = ref(0)

    // 系统状态
    const systemStatus = ref('正常运行')
    const statusType = ref<'success' | 'warning' | 'error'>('success')
    const apiStatus = ref<'online' | 'offline' | 'degraded'>('online')
    const apiStatusText = ref('626个端点正常')
    const dataQualityStatus = ref<'good' | 'warning' | 'error'>('good')
    const dataQualityScore = ref('98.5%')
    const systemLoadStatus = ref<'low' | 'medium' | 'high'>('medium')
    const systemLoadPercent = ref('45%')
    const lastUpdateTime = ref('--:--:--')
    const version = ref('2.0.0')

    // 功能树数据结构
    const functionTreeData = ref([
        {
            key: 'market-overview',
            label: '市场总览',
            icon: 'trend-charts',
            children: [
                {
                    key: 'realtime-monitor',
                    label: '实时行情监控',
                    icon: 'monitor'
                },
                {
                    key: 'market-analysis',
                    label: '市场数据分析',
                    icon: 'data-line'
                },
                {
                    key: 'industry-analysis',
                    label: '行业概念分析',
                    icon: 'box'
                }
            ]
        },
        {
            key: 'trading-management',
            label: '交易管理',
            icon: 'tickets',
            children: [
                {
                    key: 'trading-signals',
                    label: '交易信号',
                    icon: 'notification'
                },
                {
                    key: 'trading-history',
                    label: '交易历史',
                    icon: 'timer'
                },
                {
                    key: 'position-monitor',
                    label: '持仓监控',
                    icon: 'pie-chart'
                },
                {
                    key: 'performance-analysis',
                    label: '绩效分析',
                    icon: 'trend-charts'
                }
            ]
        },
        {
            key: 'strategy-center',
            label: '策略中心',
            icon: 'management',
            children: [
                {
                    key: 'strategy-management',
                    label: '策略管理',
                    icon: 'setting'
                },
                {
                    key: 'backtest-analysis',
                    label: '回测分析',
                    icon: 'histogram'
                },
                {
                    key: 'strategy-optimization',
                    label: '策略优化',
                    icon: 'aim'
                }
            ]
        },
        {
            key: 'risk-control',
            label: '风险控制',
            icon: 'warning',
            children: [
                {
                    key: 'risk-monitor',
                    label: '风险监控',
                    icon: 'warning'
                },
                {
                    key: 'announcement-monitor',
                    label: '公告监控',
                    icon: 'document'
                },
                {
                    key: 'risk-alerts',
                    label: '风险告警',
                    icon: 'bell'
                }
            ]
        },
        {
            key: 'system-management',
            label: '系统管理',
            icon: 'grid',
            children: [
                {
                    key: 'monitoring-dashboard',
                    label: '监控面板',
                    icon: 'monitor'
                },
                {
                    key: 'data-management',
                    label: '数据管理',
                    icon: 'database'
                },
                {
                    key: 'system-settings',
                    label: '系统设置',
                    icon: 'setting'
                }
            ]
        }
    ])

    // 组件映射
    const componentMap: Record<string, any> = {
        'market-overview': ArtDecoMarketOverview,
        'realtime-monitor': ArtDecoRealtimeMonitor,
        'market-analysis': ArtDecoMarketAnalysis,
        'industry-analysis': ArtDecoIndustryAnalysis,
        'trading-signals': ArtDecoSignalsView,
        'trading-history': ArtDecoHistoryView,
        'position-monitor': ArtDecoPositionMonitor,
        'performance-analysis': ArtDecoPerformanceAnalysis,
        'strategy-management': ArtDecoStrategyManagement,
        'backtest-analysis': ArtDecoBacktestAnalysis,
        'strategy-optimization': ArtDecoStrategyOptimization,
        'risk-monitor': ArtDecoRiskMonitor,
        'announcement-monitor': ArtDecoAnnouncementMonitor,
        'risk-alerts': ArtDecoRiskAlerts,
        'monitoring-dashboard': ArtDecoMonitoringDashboard,
        'data-management': ArtDecoDataManagement,
        'system-settings': ArtDecoSystemSettings
    }

    // 当前组件
    const currentComponent = computed(() => componentMap[activeFunction.value] || ArtDecoMarketOverview)

    // 当前组件属性
    const currentComponentProps = computed(() => ({
        functionKey: activeFunction.value,
        userPermissions: authStore.user?.permissions || [],
        systemConfig: tradingStore.systemConfig
    }))

    // 当前面包屑
    const currentBreadcrumbs = computed(() => {
        const breadcrumbs = []
        const findNode = (nodes: any[], targetKey: string): any[] => {
            for (const node of nodes) {
                if (node.key === targetKey) {
                    return [node]
                }
                if (node.children) {
                    const childResult = findNode(node.children, targetKey)
                    if (childResult.length > 0) {
                        return [node, ...childResult]
                    }
                }
            }
            return []
        }

        const path = findNode(functionTreeData.value, activeFunction.value)
        return path.map(node => ({
            key: node.key,
            label: node.label,
            icon: node.icon
        }))
    })

    // 事件处理
    const handleFunctionSelect = (functionKey: string) => {
        activeFunction.value = functionKey
        tradingStore.switchActiveFunction(functionKey)
    }

    const handleNodeExpand = (nodeKey: string, expanded: boolean) => {
        if (expanded) {
            expandedNodes.value.add(nodeKey)
        } else {
            expandedNodes.value.delete(nodeKey)
        }
    }

    const handleBreadcrumbNavigate = (breadcrumbKey: string) => {
        activeFunction.value = breadcrumbKey
    }

    const handleComponentAction = (action: any) => {
        // 处理子组件的动作
        console.log('Component action:', action)
    }

    const handleInternalNavigate = (target: string) => {
        activeFunction.value = target
    }

    const refreshAllData = async () => {
        refreshing.value = true
        try {
            await tradingStore.refreshAllData()
            updateLastUpdateTime()
        } catch (error) {
            console.error('Failed to refresh data:', error)
        } finally {
            refreshing.value = false
        }
    }

    const openSettings = () => {
        activeFunction.value = 'system-settings'
    }

    const updateLastUpdateTime = () => {
        const now = new Date()
        lastUpdateTime.value = now.toLocaleTimeString('zh-CN', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    // 生命周期
    onMounted(() => {
        // 初始化数据
        updateLastUpdateTime()

        // 定时更新
        const updateTimer = setInterval(updateLastUpdateTime, 1000)

        // 清理定时器
        onUnmounted(() => {
            clearInterval(updateTimer)
        })
    })

    // 监听功能切换
    watch(activeFunction, newValue => {
        tradingStore.switchActiveFunction(newValue)
    })
</script>

<style scoped lang="scss">
    .artdeco-trading-center {
        display: flex;
        flex-direction: column;
        height: 100vh;
        background: var(--artdeco-bg-primary);
        color: var(--artdeco-fg-primary);
    }

    .trading-center-content {
        display: flex;
        flex: 1;
        overflow: hidden;
    }

    .function-tree-panel {
        width: 320px;
        border-right: 1px solid var(--artdeco-bg-tertiary);
        background: var(--artdeco-bg-secondary);
        overflow-y: auto;
    }

    .content-panel {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .dynamic-content {
        flex: 1;
        padding: var(--artdeco-spacing-4);
        overflow-y: auto;
    }

    .status-indicators {
        display: flex;
        gap: var(--artdeco-spacing-6);
    }

    .footer-info {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);

        .last-update {
            color: var(--artdeco-fg-muted);
            font-size: 12px;
        }

        .version-info {
            color: var(--artdeco-gold-primary);
            font-weight: 600;
            font-size: 12px;
        }
    }

    // 响应式设计
    @media (max-width: 1024px) {
        .function-tree-panel {
            width: 280px;
        }
    }

    @media (max-width: 768px) {
        .trading-center-content {
            flex-direction: column;
        }

        .function-tree-panel {
            width: 100%;
            height: 200px;
            border-right: none;
            border-bottom: 1px solid var(--artdeco-bg-tertiary);
        }
    }
</style>
