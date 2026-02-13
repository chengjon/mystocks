<template>
    <div class="artdeco-market-data">
        <!-- Page Header -->
        <ArtDecoHeader
            title="市场数据分析中心"
            subtitle="深度分析市场资金动向，挖掘投资机会"
            :show-status="true"
            :status-text="lastUpdate ? `更新于 ${lastUpdate}` : '正在加载...'"
        >
            <template #actions>
                <ArtDecoButton variant="outline" size="sm" @click="refreshData" :loading="refreshing">
                    <template #icon>
                        <ArtDecoIcon name="refresh" />
                    </template>
                    刷新数据
                </ArtDecoButton>
            </template>
        </ArtDecoHeader>

        <!-- Main Navigation Tabs -->
        <nav class="main-tabs">
            <button
                v-for="tab in mainTabs"
                :key="tab.key"
                class="main-tab"
                :class="{ active: activeTab === tab.key }"
                @click="activeTab = tab.key"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
                <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
            </button>
        </nav>

        <!-- Tab Content -->
        <div class="tab-content">
            <transition name="fade" mode="out-in">
                <div :key="activeTab" class="tab-panel">
                    <!-- 1. 数据质量 -->
                    <DataQualityPanel
                        v-if="activeTab === 'data-quality'"
                        :quality-data="qualityData"
                        :data-sources="dataSources"
                    />

                    <!-- 2. 资金流向 -->
                    <FundFlowAnalysis
                        v-if="activeTab === 'fund-flow'"
                        :fund-data="fundData"
                        :stock-ranking="stockRanking"
                        :trend-data="trendData"
                        :active-time-filter="activeTimeFilter"
                        :ranking-type="rankingType"
                        @filter-change="activeTimeFilter = $event"
                        @ranking-change="rankingType = $event"
                    />

                    <!-- 3. ETF分析 -->
                    <ETFAnalysis
                        v-if="activeTab === 'etf'"
                        :etf-ranking="etfRanking"
                    />

                    <!-- 4. 概念板块 -->
                    <ConceptAnalysis
                        v-if="activeTab === 'concepts'"
                        :concept-ranking="conceptRanking"
                        :selected-concept="selectedConcept"
                        @select-concept="selectedConcept = $event"
                    />

                    <!-- 5. 龙虎榜 -->
                    <DragonTigerAnalysis
                        v-if="activeTab === 'lhb'"
                        :lhb-data="lhbData"
                        :lhb-date="lhbDate"
                        :active-filter="lhbFilter"
                        @date-change="lhbDate = $event"
                        @filter-change="lhbFilter = $event"
                    />

                    <!-- 6. 竞价抢筹 -->
                    <AuctionAnalysis
                        v-if="activeTab === 'auction'"
                        :auction-data="auctionData"
                    />

                    <!-- 7. 机构评级 -->
                    <div v-if="activeTab === 'institutions'" class="institutions-tab">
                        <ArtDecoCard title="机构评级统计" hoverable>
                            <div class="rating-overview">
                                <ArtDecoStatCard label="买入评级" :value="institutionData.buyRating.count" variant="rise" />
                                <ArtDecoStatCard label="增持评级" :value="institutionData.holdRating.count" variant="gold" />
                                <ArtDecoStatCard label="中性评级" :value="institutionData.neutralRating.count" variant="gold" />
                                <ArtDecoStatCard label="减持评级" :value="institutionData.reduceRating.count" variant="fall" />
                            </div>
                        </ArtDecoCard>
                        <ArtDecoCard title="最新机构评级" hoverable style="margin-top: 24px;">
                            <ArtDecoTable :data="latestRatings" :columns="ratingColumns" />
                        </ArtDecoCard>
                    </div>

                    <!-- 8. 问财搜索 -->
                    <div v-if="activeTab === 'wencai'" class="wencai-tab">
                        <ArtDecoCard title="智能问财搜索">
                            <div class="search-container">
                                <ArtDecoInput v-model="wencaiQuery" placeholder="搜索涨停股、创历史新高..." @enter="executeWencaiSearch" />
                                <div class="quick-tags">
                                    <ArtDecoButton v-for="tag in quickTags" :key="tag" variant="outline" size="sm" @click="wencaiQuery = tag">
                                        {{ tag }}
                                    </ArtDecoButton>
                                </div>
                            </div>
                        </ArtDecoCard>
                        <ArtDecoCard v-if="wencaiResults.length" title="搜索结果" style="margin-top: 24px;">
                            <ArtDecoTable :data="wencaiResults" :columns="wencaiColumns" />
                        </ArtDecoCard>
                    </div>
                </div>
            </transition>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { 
    ArtDecoHeader, ArtDecoButton, ArtDecoIcon, ArtDecoCard, 
    ArtDecoStatCard, ArtDecoTable, ArtDecoInput 
} from '@/components/artdeco'

// Sub-components
import DataQualityPanel from './market-data-tabs/DataQualityPanel.vue'
import FundFlowAnalysis from './market-data-tabs/FundFlowAnalysis.vue'
import ETFAnalysis from './market-data-tabs/ETFAnalysis.vue'
import ConceptAnalysis from './market-data-tabs/ConceptAnalysis.vue'
import DragonTigerAnalysis from './market-data-tabs/DragonTigerAnalysis.vue'
import AuctionAnalysis from './market-data-tabs/AuctionAnalysis.vue'

// API
import dashboardService from '@/api/services/dashboardService'
import { marketService } from '@/api/services/marketService'
import apiClient from '@/api/apiClient'

// State
const activeTab = ref('fund-flow')
const lastUpdate = ref('')
const refreshing = ref(false)
const activeTimeFilter = ref('today')
const rankingType = ref('main_force')
const lhbDate = ref('today')
const lhbFilter = ref('buy')
const selectedConcept = ref(null)
const wencaiQuery = ref('')
const wencaiResults = ref([])
const trendData = ref([])

// Data refs
const qualityData = ref({ integrity: 0, accuracy: 0, timeliness: 0, consistency: 0 })
const dataSources = ref([])
const fundData = ref({
    shanghai: { amount: '0', change: 0 },
    shenzhen: { amount: '0', change: 0 },
    north: { amount: '0', change: 0 },
    main: { amount: '0', change: 0 }
})
const stockRanking = ref([])
const etfRanking = ref([])
const conceptRanking = ref([])
const lhbData = ref([])
const auctionData = ref([])
const institutionData = ref({
    buyRating: { count: 0 }, holdRating: { count: 0 }, neutralRating: { count: 0 }, reduceRating: { count: 0 }
})
const latestRatings = ref([])

const mainTabs = [
    { key: 'data-quality', label: '数据质量', icon: '🛡️' },
    { key: 'fund-flow', label: '资金流向', icon: '💰' },
    { key: 'etf', label: 'ETF分析', icon: '🏷️' },
    { key: 'concepts', label: '概念板块', icon: '💡' },
    { key: 'lhb', label: '龙虎榜', icon: '🏆' },
    { key: 'auction', label: '竞价抢筹', icon: '⏰' },
    { key: 'institutions', label: '机构评级', icon: '🏢' },
    { key: 'wencai', label: '问财搜索', icon: '🔍' }
]

const quickTags = ['涨停股', '主力净流入', '突破平台', '均线多头']

const ratingColumns = [
    { key: 'stock', label: '代码' },
    { key: 'name', label: '名称' },
    { key: 'rating', label: '评级' },
    { key: 'institution', label: '机构' }
]

const wencaiColumns = [
    { key: 'code', label: '代码' },
    { key: 'name', label: '名称' },
    { key: 'price', label: '现价' },
    { key: 'change', label: '涨跌' }
]

// Methods
const refreshData = async () => {
    refreshing.value = true
    try {
        if (activeTab.value === 'fund-flow') {
            const [flowRes, rankingRes, trendRes] = await Promise.all([
                dashboardService.getFundFlow(),
                dashboardService.getStockFlowRanking(),
                marketService.getTrend('000001.SH')
            ])

            const flowPayload = flowRes?.data ?? flowRes
            if (flowPayload && typeof flowPayload === 'object') {
                fundData.value = {
                    ...fundData.value,
                    ...flowPayload
                }
            }

            const rankingPayload = rankingRes?.data ?? rankingRes
            const rankingList = Array.isArray(rankingPayload)
                ? rankingPayload
                : (Array.isArray(rankingPayload?.data) ? rankingPayload.data : [])
            stockRanking.value = rankingList

            const trendPayload = trendRes?.data ?? trendRes
            const trendList = Array.isArray(trendPayload?.data)
                ? trendPayload.data
                : (Array.isArray(trendPayload) ? trendPayload : [])
            trendData.value = trendList.map((v, i) => ({ date: i, value: Number(v) || 0 }))
        } else if (activeTab.value === 'etf') {
            const res = await dashboardService.getETFPerformance()
            const payload = res?.data ?? res
            etfRanking.value = Array.isArray(payload) ? payload : []
        } else if (activeTab.value === 'concepts') {
            const res = await dashboardService.getIndustryFlow()
            const payload = res?.data ?? res
            conceptRanking.value = Array.isArray(payload) ? payload : []
        } else if (activeTab.value === 'lhb') {
            const res = await dashboardService.getLongHuBang()
            const payload = res?.data ?? res
            lhbData.value = Array.isArray(payload) ? payload : []
        } else if (activeTab.value === 'auction') {
            const res = await dashboardService.getBlockTrading()
            const payload = res?.data ?? res
            auctionData.value = Array.isArray(payload) ? payload : []
        } else if (activeTab.value === 'data-quality') {
            const res = await apiClient.get('/api/monitoring/v2/data-quality')
            if (res.data?.success) {
                qualityData.value = res.data.data.metrics
                dataSources.value = res.data.data.sources
            }
        }
        lastUpdate.value = new Date().toLocaleTimeString()
    } catch (e) {
        console.error('Failed to refresh market data', e)
    } finally {
        refreshing.value = false
    }
}

const executeWencaiSearch = () => {
    wencaiResults.value = [{ code: '600519', name: '贵州茅台', price: 1850, change: '+2.1%', volume: '15万', score: 98 }]
}

onMounted(refreshData)
watch(activeTab, refreshData)
</script>

<style scoped lang="scss">
.artdeco-market-data {
    padding: var(--artdeco-spacing-6);
    background: var(--artdeco-bg-global);
    min-height: 100vh;
}

.main-tabs {
    display: flex;
    gap: var(--artdeco-spacing-2);
    margin: var(--artdeco-spacing-6) 0;
    border-bottom: 2px solid var(--artdeco-border-gold-subtle);
    padding-bottom: var(--artdeco-spacing-2);
}

.main-tab {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-border-gold-subtle);
    color: var(--artdeco-fg-primary);
    cursor: pointer;
    transition: all 0.3s;
    text-transform: uppercase;
    font-family: var(--artdeco-font-body);

    &:hover, &.active {
        border-color: var(--artdeco-accent-gold);
        background: rgba(212, 175, 55, 0.1);
    }

    &.active {
        box-shadow: var(--artdeco-glow-sm);
        color: var(--artdeco-accent-gold);
    }
}

.rating-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}

.search-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.quick-tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
