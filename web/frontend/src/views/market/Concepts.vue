<template>
    <div class="concepts-container">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Box /></el-icon>
                    CONCEPT MARKET DATA
                </h1>
                <p class="page-subtitle">CONCEPT STOCK PLATES REAL-TIME ANALYSIS AND MONITORING</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshAllData" :loading="loading">
                    <template #icon>
                        <RefreshRight />
                    </template>
                    REFRESH ALL
                </el-button>
                <el-switch
                    v-model="autoRefresh"
                    active-text="AUTO"
                    inactive-text="MANUAL"
                    @change="toggleAutoRefresh"
                />
            </div>
        </div>

        <!-- Market Overview -->
        <div class="overview-section">
            <el-card class="overview-card" shadow="never">
                <div class="overview-grid">
                    <div class="overview-item">
                        <div class="overview-icon">🎯</div>
                        <div class="overview-data">
                            <div class="overview-value">{{ conceptStats.totalConcepts }}</div>
                            <div class="overview-label">TOTAL CONCEPTS</div>
                        </div>
                    </div>
                    <div class="overview-item">
                        <div class="overview-icon">📈</div>
                        <div class="overview-data">
                            <div class="overview-value">{{ conceptStats.activeConcepts }}</div>
                            <div class="overview-label">ACTIVE TODAY</div>
                        </div>
                    </div>
                    <div class="overview-item">
                        <div class="overview-icon">💰</div>
                        <div class="overview-data">
                            <div class="overview-value">{{ formatCurrency(conceptStats.totalVolume) }}</div>
                            <div class="overview-label">TOTAL VOLUME</div>
                        </div>
                    </div>
                    <div class="overview-item">
                        <div class="overview-icon">📊</div>
                        <div class="overview-data">
                            <div class="overview-value">{{ conceptStats.avgChange.toFixed(2) }}%</div>
                            <div class="overview-label">AVG CHANGE</div>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Hot Concepts Section -->
        <div class="hot-concepts-section">
            <el-card class="hot-concepts-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">HOT CONCEPTS</span>
                        <span class="timeframe">Real-time ranking</span>
                    </div>
                </template>

                <div class="concepts-grid">
                    <div
                        v-for="(concept, index) in hotConcepts"
                        :key="concept.name"
                        class="concept-item"
                        :class="{ 'top-concept': index < 3 }"
                        @click="selectConcept(concept)"
                    >
                        <div class="concept-rank">{{ index + 1 }}</div>
                        <div class="concept-info">
                            <div class="concept-name">{{ concept.name }}</div>
                            <div class="concept-description">{{ concept.description }}</div>
                            <div class="concept-stats">
                                <span class="stat-stocks">{{ concept.stockCount }} stocks</span>
                                <span class="stat-volume">{{ formatVolume(concept.volume) }}</span>
                            </div>
                        </div>
                        <div class="concept-change" :class="getChangeClass(concept.changePercent)">
                            {{ concept.changePercent >= 0 ? '+' : '' }}{{ concept.changePercent.toFixed(2) }}%
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Concept Details Section -->
        <div class="concept-details-section" v-if="selectedConcept">
            <el-card class="concept-details-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <div class="concept-title-info">
                            <span class="card-title">{{ selectedConcept.name }}</span>
                            <span class="concept-desc">{{ selectedConcept.description }}</span>
                        </div>
                        <div class="concept-actions">
                            <el-button type="primary" size="small" @click="viewConceptStocks">VIEW STOCKS</el-button>
                        </div>
                    </div>
                </template>

                <div class="concept-metrics">
                    <div class="metric-grid">
                        <div class="metric-item">
                            <span class="metric-label">Total Stocks</span>
                            <span class="metric-value">{{ selectedConcept.stockCount }}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Avg Change</span>
                            <span class="metric-value" :class="getChangeClass(selectedConcept.changePercent)">
                                {{ selectedConcept.changePercent >= 0 ? '+' : ''
                                }}{{ selectedConcept.changePercent.toFixed(2) }}%
                            </span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Total Volume</span>
                            <span class="metric-value">{{ formatVolume(selectedConcept.volume) }}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Leading Stock</span>
                            <span class="metric-value">{{ selectedConcept.leadingStock }}</span>
                        </div>
                    </div>
                </div>

                <!-- Concept Stocks Table -->
                <el-table
                    :data="selectedConcept.stocks"
                    :loading="conceptStocksLoading"
                    class="concept-stocks-table"
                    stripe
                    border
                    height="400"
                >
                    <el-table-column prop="code" label="CODE" width="100" />
                    <el-table-column prop="name" label="NAME" width="150" />
                    <el-table-column prop="price" label="PRICE" width="100" align="right">
                        <template #default="{ row }">
                            <span class="price-value">{{ row.price.toFixed(2) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="changePercent" label="CHANGE %" width="120" align="right">
                        <template #default="{ row }">
                            <span
                                class="change-percent"
                                :class="{ positive: row.changePercent >= 0, negative: row.changePercent < 0 }"
                            >
                                {{ row.changePercent >= 0 ? '+' : '' }}{{ row.changePercent.toFixed(2) }}%
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="volume" label="VOLUME" width="140" align="right">
                        <template #default="{ row }">
                            <span class="volume-value">{{ formatVolume(row.volume) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="amount" label="AMOUNT" width="160" align="right">
                        <template #default="{ row }">
                            <span class="amount-value">{{ formatAmount(row.amount) }}</span>
                        </template>
                    </el-table-column>
                </el-table>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, onMounted, onUnmounted } from 'vue'
    import { ElCard, ElButton, ElTable, ElTableColumn, ElSwitch, ElMessage } from 'element-plus'
    import { Box, RefreshRight } from '@element-plus/icons-vue'

    interface Concept {
        name: string
        description: string
        stockCount: number
        changePercent: number
        volume: number
        leadingStock: string
        stocks: unknown[]
    }

    interface ConceptStats {
        totalConcepts: number
        activeConcepts: number
        totalVolume: number
        avgChange: number
    }

    const loading = ref(false)
    const autoRefresh = ref(false)
    const conceptStocksLoading = ref(false)
    const refreshInterval = ref<NodeJS.Timeout | null>(null)
    const selectedConcept = ref<Concept | null>(null)

    const conceptStats = reactive<ConceptStats>({
        totalConcepts: 245,
        activeConcepts: 89,
        totalVolume: 45000000000, // 450亿
        avgChange: 1.23
    })

    const hotConcepts = ref<Concept[]>([
        {
            name: 'ChatGPT',
            description: '人工智能对话机器人',
            stockCount: 45,
            changePercent: 8.56,
            volume: 12500000000,
            leadingStock: '科大讯飞',
            stocks: []
        },
        {
            name: '新能源车',
            description: '新能源汽车产业链',
            stockCount: 67,
            changePercent: 6.34,
            volume: 9800000000,
            leadingStock: '比亚迪',
            stocks: []
        },
        {
            name: '半导体',
            description: '芯片半导体行业',
            stockCount: 38,
            changePercent: 5.78,
            volume: 8700000000,
            leadingStock: '中芯国际',
            stocks: []
        },
        {
            name: '医药',
            description: '医药生物科技',
            stockCount: 52,
            changePercent: 4.92,
            volume: 7600000000,
            leadingStock: '恒瑞医药',
            stocks: []
        },
        {
            name: '光伏',
            description: '太阳能光伏产业',
            stockCount: 41,
            changePercent: 4.15,
            volume: 6500000000,
            leadingStock: '隆基绿能',
            stocks: []
        },
        {
            name: '军工',
            description: '国防军工装备',
            stockCount: 33,
            changePercent: 3.87,
            volume: 5400000000,
            leadingStock: '中航沈飞',
            stocks: []
        },
        {
            name: '白酒',
            description: '白酒酿酒行业',
            stockCount: 28,
            changePercent: 2.94,
            volume: 4800000000,
            leadingStock: '贵州茅台',
            stocks: []
        },
        {
            name: '5G',
            description: '5G通信技术',
            stockCount: 36,
            changePercent: 2.67,
            volume: 4200000000,
            leadingStock: '中国移动',
            stocks: []
        }
    ])

    const refreshAllData = async (): Promise<void> => {
        loading.value = true
        try {
            await loadConceptData()
            ElMessage.success('Concept data refreshed')
        } catch (error) {
            console.error('Failed to refresh concept data:', error)
            ElMessage.error('Failed to refresh concept data')
        } finally {
            loading.value = false
        }
    }

    const loadConceptData = async (): Promise<void> => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))

        // Update concept data with random changes
        hotConcepts.value.forEach(concept => {
            const change = (Math.random() - 0.5) * 0.02
            concept.changePercent = parseFloat((concept.changePercent + change).toFixed(2))
            concept.volume = Math.round(concept.volume * (0.95 + Math.random() * 0.1))
        })

        // Update overall stats
        conceptStats.activeConcepts = Math.floor(Math.random() * 50) + 80
        conceptStats.totalVolume = Math.round(conceptStats.totalVolume * (0.98 + Math.random() * 0.04))
        conceptStats.avgChange = parseFloat((Math.random() * 4 - 1).toFixed(2))
    }

    const selectConcept = async (concept: Concept): Promise<void> => {
        selectedConcept.value = concept
        conceptStocksLoading.value = true

        try {
            // Simulate loading concept stocks
            await new Promise(resolve => setTimeout(resolve, 300))

            // Generate mock stocks for the concept
            selectedConcept.value.stocks = Array.from({ length: concept.stockCount }, (_, i) => ({
                code: `60${String(1000 + i).padStart(4, '0')}`,
                name: `概念股${i + 1}`,
                price: 10 + Math.random() * 50,
                changePercent: (Math.random() - 0.5) * 10,
                volume: Math.floor(Math.random() * 10000000) + 100000,
                amount: Math.floor(Math.random() * 500000000) + 50000000
            }))
        } catch (error) {
            console.error('Failed to load concept stocks:', error)
        } finally {
            conceptStocksLoading.value = false
        }
    }

    const viewConceptStocks = (): void => {
        // Navigate to stocks view with concept filter
        console.log('View concept stocks:', selectedConcept.value?.name)
    }

    const toggleAutoRefresh = (): void => {
        if (autoRefresh.value) {
            refreshInterval.value = setInterval(refreshAllData, 30000)
            ElMessage.success('Auto refresh enabled')
        } else {
            if (refreshInterval.value) {
                clearInterval(refreshInterval.value)
                refreshInterval.value = null
            }
            ElMessage.info('Auto refresh disabled')
        }
    }

    const getChangeClass = (changePercent: number): string => {
        if (changePercent > 0) return 'positive'
        if (changePercent < 0) return 'negative'
        return 'neutral'
    }

    const formatCurrency = (amount: number): string => {
        if (amount >= 100000000) {
            return (amount / 100000000).toFixed(1) + '亿'
        } else if (amount >= 10000) {
            return (amount / 10000).toFixed(1) + '万'
        }
        return amount.toString()
    }

    const formatVolume = (volume: number): string => {
        if (volume >= 100000000) {
            return (volume / 100000000).toFixed(1) + '亿'
        } else if (volume >= 10000) {
            return (volume / 10000).toFixed(1) + '万'
        }
        return volume.toString()
    }

    const formatAmount = (amount: number): string => {
        if (amount >= 100000000) {
            return (amount / 100000000).toFixed(2) + '亿'
        } else if (amount >= 10000) {
            return (amount / 10000).toFixed(2) + '万'
        }
        return amount.toString()
    }

    // Lifecycle
    onMounted(async () => {
        await loadConceptData()
    })

    onUnmounted(() => {
        if (refreshInterval.value) {
            clearInterval(refreshInterval.value)
        }
    })
</script>

<style scoped lang="scss">
@import "./styles/Concepts";
</style>
