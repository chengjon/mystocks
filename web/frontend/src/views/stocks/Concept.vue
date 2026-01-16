<template>
    <div class="concept-container">
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Box /></el-icon>
                    CONCEPT STOCK POOLS
                </h1>
                <p class="page-subtitle">STOCKS GROUPED BY MARKET THEMES AND CONCEPTS</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshData">
                    <template #icon><RefreshRight /></template>
                    REFRESH
                </el-button>
            </div>
        </div>

        <div class="concepts-overview">
            <el-card class="overview-card">
                <div class="overview-stats">
                    <div class="stat-item">
                        <span class="stat-label">ACTIVE CONCEPTS</span>
                        <span class="stat-value">{{ conceptStats.activeConcepts }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">TOTAL STOCKS</span>
                        <span class="stat-value">{{ conceptStats.totalStocks }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">HOT CONCEPTS</span>
                        <span class="stat-value">{{ conceptStats.hotConcepts }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">AVG PERFORMANCE</span>
                        <span class="stat-value">{{ conceptStats.avgPerformance.toFixed(2) }}%</span>
                    </div>
                </div>
            </el-card>
        </div>

        <div class="concepts-grid">
            <el-card
                v-for="concept in concepts"
                :key="concept.name"
                class="concept-card"
                :class="{ 'hot-concept': concept.isHot }"
                @click="selectConcept(concept)"
            >
                <div class="concept-header">
                    <div class="concept-badge" :class="{ hot: concept.isHot }">
                        {{ concept.isHot ? '🔥' : '📈' }}
                    </div>
                    <div class="concept-info">
                        <h3 class="concept-name">{{ concept.name }}</h3>
                        <p class="concept-description">{{ concept.description }}</p>
                    </div>
                </div>

                <div class="concept-metrics">
                    <div class="metric-row">
                        <div class="metric-item">
                            <span class="metric-value">{{ concept.stockCount }}</span>
                            <span class="metric-label">Stocks</span>
                        </div>
                        <div class="metric-item">
                            <span
                                class="metric-value"
                                :class="{ positive: concept.changePercent >= 0, negative: concept.changePercent < 0 }"
                            >
                                {{ concept.changePercent >= 0 ? '+' : '' }}{{ concept.changePercent.toFixed(2) }}%
                            </span>
                            <span class="metric-label">Change</span>
                        </div>
                    </div>

                    <div class="metric-row">
                        <div class="metric-item">
                            <span class="metric-value">{{ formatVolume(concept.volume) }}</span>
                            <span class="metric-label">Volume</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-value">{{ concept.heatIndex }}/100</span>
                            <span class="metric-label">Heat</span>
                        </div>
                    </div>
                </div>

                <div class="concept-trend">
                    <div class="trend-bar">
                        <div
                            class="trend-fill"
                            :class="{ rising: concept.changePercent >= 0, falling: concept.changePercent < 0 }"
                            :style="{ width: Math.min(Math.abs(concept.changePercent) * 3, 100) + '%' }"
                        ></div>
                    </div>
                    <div class="trend-label">
                        {{ concept.changePercent >= 0 ? 'Rising' : 'Falling' }}
                    </div>
                </div>
            </el-card>
        </div>

        <div v-if="selectedConcept" class="concept-detail">
            <el-card class="detail-card">
                <template #header>
                    <div class="detail-header">
                        <div class="concept-title-section">
                            <span class="concept-icon">{{ selectedConcept.isHot ? '🔥' : '📈' }}</span>
                            <span class="detail-title">{{ selectedConcept.name }}</span>
                            <el-tag :type="selectedConcept.isHot ? 'danger' : 'warning'" size="small">
                                {{ selectedConcept.isHot ? 'HOT' : 'ACTIVE' }}
                            </el-tag>
                        </div>
                        <div class="concept-meta">
                            <span class="meta-item">{{ selectedConcept.stockCount }} stocks</span>
                            <span class="meta-item">Heat: {{ selectedConcept.heatIndex }}/100</span>
                        </div>
                    </div>
                </template>

                <div class="concept-description-full">
                    {{ selectedConcept.description }}
                </div>

                <div class="concept-stocks-section">
                    <h4 class="section-title">Related Stocks</h4>
                    <el-table :data="selectedConcept.stocks" class="concept-stocks-table" stripe border height="350">
                        <el-table-column prop="symbol" label="SYMBOL" width="100" />
                        <el-table-column prop="name" label="NAME" width="150" />
                        <el-table-column prop="price" label="PRICE" width="100" align="right" />
                        <el-table-column prop="changePercent" label="CHANGE %" width="120" align="right">
                            <template #default="{ row }">
                                <span :class="{ positive: row.changePercent >= 0, negative: row.changePercent < 0 }">
                                    {{ row.changePercent >= 0 ? '+' : '' }}{{ row.changePercent.toFixed(2) }}%
                                </span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="volume" label="VOLUME" width="120" align="right" />
                        <el-table-column prop="weight" label="WEIGHT" width="100" align="right">
                            <template #default="{ row }">{{ row.weight.toFixed(1) }}%</template>
                        </el-table-column>
                    </el-table>
                </div>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive } from 'vue'
    import { ElCard, ElButton, ElTable, ElTableColumn, ElTag, ElMessage } from 'element-plus'
    import { Box, RefreshRight } from '@element-plus/icons-vue'

    interface Stock {
        symbol: string
        name: string
        price: number
        changePercent: number
        volume: number
        weight: number
    }

    interface Concept {
        name: string
        description: string
        stockCount: number
        changePercent: number
        volume: number
        heatIndex: number
        isHot: boolean
        stocks: Stock[]
    }

    const selectedConcept = ref<Concept | null>(null)

    const conceptStats = reactive({
        activeConcepts: 245,
        totalStocks: 3456,
        hotConcepts: 23,
        avgPerformance: 1.67
    })

    const concepts = ref([
        {
            name: 'ChatGPT',
            description: 'AI chatbot and conversational AI technology',
            stockCount: 45,
            changePercent: 8.56,
            volume: 12500000000,
            heatIndex: 95,
            isHot: true,
            stocks: [
                {
                    symbol: '000001',
                    name: '平安银行',
                    price: 12.85,
                    changePercent: 1.18,
                    volume: 125000000,
                    weight: 15.2
                },
                { symbol: '000002', name: '万科A', price: 18.95, changePercent: -1.3, volume: 98000000, weight: 12.8 }
            ]
        },
        {
            name: 'New Energy Vehicles',
            description: 'Electric vehicles and related technologies',
            stockCount: 67,
            changePercent: 6.34,
            volume: 9800000000,
            heatIndex: 88,
            isHot: true,
            stocks: [
                {
                    symbol: '300750',
                    name: '宁德时代',
                    price: 245.8,
                    changePercent: 2.16,
                    volume: 35000000,
                    weight: 28.5
                }
            ]
        },
        {
            name: 'Semiconductors',
            description: 'Chip manufacturing and semiconductor industry',
            stockCount: 38,
            changePercent: 5.78,
            volume: 8700000000,
            heatIndex: 82,
            isHot: false,
            stocks: [
                { symbol: '600036', name: '招商银行', price: 42.8, changePercent: 2.03, volume: 45000000, weight: 18.9 }
            ]
        },
        {
            name: 'Healthcare',
            description: 'Medical technology and pharmaceutical companies',
            stockCount: 52,
            changePercent: -0.23,
            volume: 5600000000,
            heatIndex: 67,
            isHot: false,
            stocks: [
                { symbol: '000858', name: '五粮液', price: 128.5, changePercent: -1.76, volume: 12000000, weight: 9.7 }
            ]
        },
        {
            name: '5G Technology',
            description: '5G infrastructure and telecommunications',
            stockCount: 41,
            changePercent: 3.45,
            volume: 7200000000,
            heatIndex: 76,
            isHot: false,
            stocks: [
                {
                    symbol: '000001',
                    name: '平安银行',
                    price: 12.85,
                    changePercent: 1.18,
                    volume: 125000000,
                    weight: 22.1
                }
            ]
        },
        {
            name: 'Military Industry',
            description: 'Defense and military equipment manufacturing',
            stockCount: 33,
            changePercent: 2.89,
            volume: 4800000000,
            heatIndex: 71,
            isHot: false,
            stocks: [
                { symbol: '600036', name: '招商银行', price: 42.8, changePercent: 2.03, volume: 45000000, weight: 16.8 }
            ]
        }
    ])

    const refreshData = async () => {
        await new Promise(resolve => setTimeout(resolve, 500))

        // Update concept data
        concepts.value.forEach(concept => {
            const change = (Math.random() - 0.5) * 0.05
            concept.changePercent = parseFloat((concept.changePercent + change).toFixed(2))
            concept.volume = Math.round(concept.volume * (0.98 + Math.random() * 0.04))
            concept.heatIndex = Math.min(100, Math.max(0, concept.heatIndex + Math.floor((Math.random() - 0.5) * 10)))
        })

        ElMessage.success('Concept data refreshed')
    }

    const selectConcept = (concept: any) => {
        selectedConcept.value = concept
    }

    const formatVolume = (volume: number) => {
        if (volume >= 100000000) return (volume / 100000000).toFixed(1) + '亿'
        if (volume >= 10000) return (volume / 10000).toFixed(1) + '万'
        return volume.toString()
    }
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .concept-container {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-lg);
      padding: var(--spacing-lg);
      background: var(--color-bg-primary);
      min-height: 100vh);
    }

    .page-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: var(--spacing-lg);
      border-bottom: 2px solid var(--color-border);

      .page-title {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        font-family: var(--font-family-sans);
        font-size: var(--font-size-2xl);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: var(--color-accent);

        .el-icon { font-size: var(--font-size-3xl); color: var(--color-accent); }
      }

      .page-subtitle {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-xs);
        color: var(--color-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin: var(--spacing-sm) 0 0 0;
      }
    }

    .concepts-overview .overview-card :deep(.el-card__body) { padding: var(--spacing-lg); }
    .overview-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--spacing-lg); }
    .stat-item { text-align: center; padding: var(--spacing-md); background: var(--color-bg-secondary); border-radius: var(--border-radius-md); }
    .stat-label { display: block; font-size: var(--font-size-xs); color: var(--color-text-tertiary); margin-bottom: var(--spacing-xs); }
    .stat-value { font-size: var(--font-size-xl); font-weight: 700; color: var(--color-text-primary); }

    .concepts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: var(--spacing-lg);
    }

    .concept-card {
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px var(--color-accent-alpha-50);
      }

      &.hot-concept {
        border: 2px solid var(--color-stock-up);
        background: linear-gradient(135deg, var(--color-stock-up-alpha-95), var(--color-bg-secondary));
      }

      :deep(.el-card__body) {
        padding: var(--spacing-lg);
      }
    }

    .concept-header {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-lg);
    }

    .concept-badge {
      font-size: var(--font-size-2xl);
      width: 50px;
      height: 50px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;

      &.hot {
        background: linear-gradient(135deg, #ff6b6b, #ffa726);
        color: white;
      }
    }

    .concept-info {
      flex: 1;
    }

    .concept-name {
      font-family: var(--font-family-sans);
      font-size: var(--font-size-lg);
      font-weight: 600;
      color: var(--color-text-primary);
      margin: 0 0 var(--spacing-xs) 0;
    }

    .concept-description {
      font-family: var(--font-family-sans);
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);
      margin: 0;
    }

    .concept-metrics {
      margin-bottom: var(--spacing-lg);
    }

    .metric-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: var(--spacing-md);

      &:last-child {
        margin-bottom: 0;
      }
    }

    .metric-item {
      text-align: center;
      flex: 1;
    }

    .metric-value {
      display: block;
      font-family: var(--font-family-mono);
      font-size: var(--font-size-lg);
      font-weight: 700;
      color: var(--color-text-primary);

      &.positive { color: var(--color-stock-up); }
      &.negative { color: var(--color-stock-down); }
    }

    .metric-label {
      font-family: var(--font-family-sans);
      font-size: var(--font-size-xs);
      color: var(--color-text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .concept-trend {
      .trend-bar {
        height: 6px;
        background: var(--color-bg-secondary);
        border-radius: 3px;
        overflow: hidden;
        margin-bottom: var(--spacing-xs);
      }

      .trend-fill {
        height: 100%;
        border-radius: 3px;

        &.rising { background: var(--color-stock-up); }
        &.falling { background: var(--color-stock-down); }
      }

      .trend-label {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-xs);
        color: var(--color-text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        text-align: center;
      }
    }

    .concept-detail {
      .detail-card :deep(.el-card__header) {
        padding: var(--spacing-md) var(--spacing-lg);
        border-bottom: 1px solid var(--color-border);
      }

      .detail-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--spacing-lg);
      }

      .concept-title-section {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
      }

      .concept-icon {
        font-size: var(--font-size-xl);
      }

      .detail-title {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--color-accent);
      }

      .concept-meta {
        display: flex;
        gap: var(--spacing-lg);
      }

      .meta-item {
        font-family: var(--font-family-mono);
        font-size: var(--font-size-sm);
        color: var(--color-text-tertiary);
      }

      .concept-description-full {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-sm);
        color: var(--color-text-secondary);
        margin-bottom: var(--spacing-lg);
        line-height: 1.6;
      }

      .concept-stocks-section {
        .section-title {
          font-family: var(--font-family-sans);
          font-size: var(--font-size-sm);
          font-weight: 600;
          color: var(--color-accent);
          margin: 0 0 var(--spacing-md) 0;
          text-transform: uppercase;
          letter-spacing: 0.1em;
        }
      }

      .concept-stocks-table :deep(.el-table__header th) {
        background: var(--color-bg-secondary);
      }
    }

    .positive { color: var(--color-stock-up); }
    .negative { color: var(--color-stock-down); }

    @media (max-width: 1200px) {
      .concepts-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
    }

    @media (max-width: 768px) {
      .concept-container { padding: var(--spacing-md); }
      .page-header { flex-direction: column; align-items: flex-start; gap: var(--spacing-md); }
      .concepts-grid { grid-template-columns: 1fr; }
      .overview-stats { grid-template-columns: 1fr; }
      .concept-header { flex-direction: column; text-align: center; }
      .metric-row { flex-direction: column; gap: var(--spacing-sm); }
      .detail-header { flex-direction: column; align-items: flex-start; gap: var(--spacing-md); }
      .concept-meta { justify-content: space-between; width: 100%; }
    }
</style>
