<template>
    <div class="industry-container">
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Box /></el-icon>
                    INDUSTRY STOCK POOLS
                </h1>
                <p class="page-subtitle">STOCKS GROUPED BY INDUSTRY SECTORS</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshData">
                    <template #icon><RefreshRight /></template>
                    REFRESH
                </el-button>
            </div>
        </div>

        <div class="industries-grid">
            <el-card
                v-for="industry in industries"
                :key="industry.name"
                class="industry-card"
                @click="selectIndustry(industry)"
            >
                <div class="industry-header">
                    <div class="industry-icon">{{ industry.icon }}</div>
                    <div class="industry-info">
                        <h3 class="industry-name">{{ industry.name }}</h3>
                        <p class="industry-desc">{{ industry.description }}</p>
                    </div>
                </div>

                <div class="industry-stats">
                    <div class="stat-item">
                        <span class="stat-value">{{ industry.stockCount }}</span>
                        <span class="stat-label">Stocks</span>
                    </div>
                    <div class="stat-item">
                        <span
                            class="stat-value"
                            :class="{ positive: industry.avgChange >= 0, negative: industry.avgChange < 0 }"
                        >
                            {{ industry.avgChange >= 0 ? '+' : '' }}{{ industry.avgChange.toFixed(2) }}%
                        </span>
                        <span class="stat-label">Avg Change</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{ formatMarketCap(industry.totalMarketCap) }}</span>
                        <span class="stat-label">Total Cap</span>
                    </div>
                </div>

                <div class="industry-performance">
                    <div class="performance-bar">
                        <div
                            class="performance-fill"
                            :class="{ positive: industry.avgChange >= 0, negative: industry.avgChange < 0 }"
                            :style="{ width: Math.abs(industry.avgChange) * 2 + '%' }"
                        ></div>
                    </div>
                </div>
            </el-card>
        </div>

        <div v-if="selectedIndustry" class="industry-detail">
            <el-card class="detail-card">
                <template #header>
                    <div class="detail-header">
                        <span class="detail-title">{{ selectedIndustry.icon }} {{ selectedIndustry.name }}</span>
                        <span class="detail-subtitle">{{ selectedIndustry.stockCount }} stocks</span>
                    </div>
                </template>

                <el-table :data="selectedIndustry.stocks" class="industry-table" stripe border height="400">
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
                    <el-table-column prop="marketCap" label="MARKET CAP" width="140" align="right" />
                </el-table>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive } from 'vue'
    import { ElCard, ElButton, ElTable, ElTableColumn, ElMessage } from 'element-plus'
    import { Box, RefreshRight } from '@element-plus/icons-vue'

    interface Stock {
        symbol: string
        name: string
        price: number
        changePercent: number
        volume: number
        marketCap: number
    }

    interface Industry {
        name: string
        icon: string
        description: string
        stockCount: number
        avgChange: number
        totalMarketCap: number
        stocks: Stock[]
    }

    const selectedIndustry = ref<Industry | null>(null)

    const industries = ref([
        {
            name: 'Banking & Finance',
            icon: '🏦',
            description: 'Commercial banks and financial institutions',
            stockCount: 45,
            avgChange: 1.23,
            totalMarketCap: 8500000000000,
            stocks: [
                {
                    symbol: '000001',
                    name: '平安银行',
                    price: 12.85,
                    changePercent: 1.18,
                    volume: 125000000,
                    marketCap: 350000000000
                },
                {
                    symbol: '600036',
                    name: '招商银行',
                    price: 42.8,
                    changePercent: 2.03,
                    volume: 45000000,
                    marketCap: 950000000000
                }
            ]
        },
        {
            name: 'Technology',
            icon: '💻',
            description: 'Technology and software companies',
            stockCount: 67,
            avgChange: 2.45,
            totalMarketCap: 12000000000000,
            stocks: [
                {
                    symbol: '000002',
                    name: '万科A',
                    price: 18.95,
                    changePercent: -1.3,
                    volume: 98000000,
                    marketCap: 280000000000
                }
            ]
        },
        {
            name: 'Healthcare',
            icon: '🏥',
            description: 'Pharmaceuticals and healthcare services',
            stockCount: 38,
            avgChange: -0.87,
            totalMarketCap: 6500000000000,
            stocks: [
                {
                    symbol: '000858',
                    name: '五粮液',
                    price: 128.5,
                    changePercent: -1.76,
                    volume: 12000000,
                    marketCap: 480000000000
                }
            ]
        },
        {
            name: 'Energy',
            icon: '⚡',
            description: 'Oil, gas and renewable energy',
            stockCount: 29,
            avgChange: 0.95,
            totalMarketCap: 7800000000000,
            stocks: [
                {
                    symbol: '300750',
                    name: '宁德时代',
                    price: 245.8,
                    changePercent: 2.16,
                    volume: 35000000,
                    marketCap: 1200000000000
                }
            ]
        }
    ])

    const refreshData = async () => {
        await new Promise(resolve => setTimeout(resolve, 500))
        ElMessage.success('Industry data refreshed')
    }

    const selectIndustry = (industry: any) => {
        selectedIndustry.value = industry
    }

    const formatMarketCap = (cap: number) => {
        if (cap >= 1000000000000) return (cap / 1000000000000).toFixed(1) + '万亿'
        if (cap >= 100000000) return (cap / 100000000).toFixed(1) + '亿'
        return cap.toString()
    }
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .industry-container {
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

    .industries-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: var(--spacing-lg);
    }

    .industry-card {
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px var(--color-accent-alpha-50);
      }

      :deep(.el-card__body) {
        padding: var(--spacing-lg);
      }
    }

    .industry-header {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-lg);
    }

    .industry-icon {
      font-size: var(--font-size-3xl);
      width: 60px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--color-accent-alpha-90);
      border-radius: 50%;
    }

    .industry-info {
      flex: 1;
    }

    .industry-name {
      font-family: var(--font-family-sans);
      font-size: var(--font-size-lg);
      font-weight: 600;
      color: var(--color-text-primary);
      margin: 0 0 var(--spacing-xs) 0;
    }

    .industry-desc {
      font-family: var(--font-family-sans);
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);
      margin: 0;
    }

    .industry-stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-lg);
    }

    .stat-item {
      text-align: center;
    }

    .stat-value {
      display: block;
      font-family: var(--font-family-mono);
      font-size: var(--font-size-lg);
      font-weight: 700;
      color: var(--color-text-primary);

      &.positive { color: var(--color-stock-up); }
      &.negative { color: var(--color-stock-down); }
    }

    .stat-label {
      font-family: var(--font-family-sans);
      font-size: var(--font-size-xs);
      color: var(--color-text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .industry-performance {
      .performance-bar {
        height: 8px;
        background: var(--color-bg-secondary);
        border-radius: 4px;
        overflow: hidden;
      }

      .performance-fill {
        height: 100%;
        border-radius: 4px;

        &.positive { background: var(--color-stock-up); }
        &.negative { background: var(--color-stock-down); }
      }
    }

    .industry-detail {
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

      .detail-title {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--color-accent);
      }

      .detail-subtitle {
        font-family: var(--font-family-mono);
        font-size: var(--font-size-sm);
        color: var(--color-text-tertiary);
      }

      .industry-table :deep(.el-table__header th) {
        background: var(--color-bg-secondary);
      }
    }

    .positive { color: var(--color-stock-up); }
    .negative { color: var(--color-stock-down); }

    @media (max-width: 1200px) {
      .industries-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
    }

    @media (max-width: 768px) {
      .industry-container { padding: var(--spacing-md); }
      .page-header { flex-direction: column; align-items: flex-start; gap: var(--spacing-md); }
      .industries-grid { grid-template-columns: 1fr; }
      .industry-header { flex-direction: column; text-align: center; }
      .industry-stats { grid-template-columns: 1fr; }
    }
</style>
