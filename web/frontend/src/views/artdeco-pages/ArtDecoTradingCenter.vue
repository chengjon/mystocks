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
    
    // ========== 配置系统集成 ==========
    import { getPageConfig, getTabConfig } from '@/config/pageConfig'
    
    const routeName = 'artdeco-trading-center'
    const pageConfig = ref(getPageConfig(routeName))
    
    console.log('Trading Center - 配置系统已就绪')
    
    // ========== 配置系统集成 ==========
    import { useTradingStore } from '@/stores/trading'
    import { useAuthStore } from '@/stores/auth'
    // 导入所有功能组件（均为@ts-ignore状态）
    // @ts-ignore - Component not implemented yet
    import ArtDecoMarketOverview from './market-data-tabs/ArtDecoMarketOverview.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoRealtimeMonitor from './market-data-tabs/ArtDecoRealtimeMonitor.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoMarketAnalysis from './market-data-tabs/ArtDecoMarketAnalysis.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoIndustryAnalysis from './market-data-tabs/ArtDecoIndustryAnalysis.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoSignalsView from './trading-tabs/ArtDecoSignalsView.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoHistoryView from './trading-tabs/ArtDecoHistoryView.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoPositionMonitor from './trading-tabs/ArtDecoPositionMonitor.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoPerformanceAnalysis from './trading-tabs/ArtDecoPerformanceAnalysis.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoStrategyManagement from './strategy-tabs/ArtDecoStrategyManagement.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoBacktestAnalysis from './strategy-tabs/ArtDecoBacktestAnalysis.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoStrategyOptimization from './strategy-tabs/ArtDecoStrategyOptimization.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoRiskMonitor from './risk-tabs/ArtDecoRiskMonitor.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoAnnouncementMonitor from './risk-tabs/ArtDecoAnnouncementMonitor.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoRiskAlerts from './risk-tabs/ArtDecoRiskAlerts.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoMonitoringDashboard from './system-tabs/ArtDecoMonitoringDashboard.vue'
    // @ts-ignore - Component not implemented yet
    import ArtDecoDataManagement from './system-tabs/ArtDecoDataManagement.vue'
    import ArtDecoSystemSettings from './system-tabs/ArtDecoSystemSettings.vue'

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

    // 从 Trading Store 获取系统状态
    const systemStatus = computed(() => tradingStore.systemStatus)
    const statusType = computed(() => tradingStore.statusType)
    const apiStatus = computed(() => tradingStore.apiStatus)
    const apiStatusText = computed(() => tradingStore.apiStatusText)
    const dataQualityStatus = computed(() => tradingStore.dataQualityStatus)
    const dataQualityScore = computed(() => tradingStore.dataQualityScore)
    const systemLoadStatus = computed(() => tradingStore.systemLoadStatus)
    const systemLoadPercent = computed(() => tradingStore.systemLoadPercent)
    const version = computed(() => tradingStore.version)
    const lastUpdateTime = computed(() => tradingStore.lastUpdateTime)

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
        globalLoading.value = true
        globalLoadingProgress.value = 0
        
        try {
            // 配置系统集成 - 并行加载真实API数据
            const progressSteps = [
                { step: 'market', label: '正在加载市场数据...', weight: 25 },
                { step: 'trading', label: '正在加载交易数据...', weight: 25 },
                { step: 'strategy', label: '正在加载策略数据...', weight: 25 },
                { step: 'system', label: '正在加载系统状态...', weight: 25 }
            ]
            
            let totalProgress = 0
            
            // 并行加载市场数据
            const marketPromise = marketService.getMarketOverview()
            const fundFlowPromise = marketService.getFundFlow()
            const industryPromise = marketService.getIndustryFlow()
            
            // 并行加载交易数据
            const strategiesPromise = strategyService.getStrategyList({ status: 'active', pageSize: 10 })
            
            // 等待市场数据
            const marketResult = await marketPromise
            totalProgress += 25
            globalLoadingProgress.value = totalProgress
            tradingStore.updateMarketData(marketResult.data)
            
            // 等待交易数据
            const tradingResult = await strategiesPromise
            totalProgress += 25
            globalLoadingProgress.value = totalProgress
            tradingStore.updateTradingData(tradingResult.data)
            
            // 等待策略数据
            const strategyResult = await strategyService.getStrategyList({ status: 'all' })
            totalProgress += 25
            globalLoadingProgress.value = totalProgress
            tradingStore.updateStrategyData(strategyResult.data)
            
            // 完成
            totalProgress = 100
            globalLoadingProgress.value = totalProgress
            
            console.log('✅ Trading Center 数据刷新完成')
        } catch (error) {
            console.error('Failed to refresh data:', error)
        } finally {
            refreshing.value = false
            globalLoading.value = false
            globalLoadingProgress.value = 100
        }
    }

    const openSettings = () => {
        activeFunction.value = 'system-settings'
    }

    // 生命周期
    onMounted(() => {
        // fetchSystemStatus is called on store creation and via setInterval in store
    })

    // 清理定时器 (The setInterval is now handled within the store, but good to keep this pattern if there were other local timers)
    onUnmounted(() => {
        // clearInterval(updateTimer) // No longer needed here
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
