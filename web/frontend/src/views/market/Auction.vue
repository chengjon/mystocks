<template>
    <div class="auction-container">
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><ShoppingCart /></el-icon>
                    AUCTION BIDDING DATA
                </h1>
                <p class="page-subtitle">OPENING CALL AUCTION ANALYSIS AND MONITORING</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshData" :loading="loading">
                    <template #icon><RefreshRight /></template>
                    REFRESH
                </el-button>
            </div>
        </div>

        <div class="auction-overview">
            <el-card class="overview-card">
                <div class="overview-stats">
                    <div class="stat-item">
                        <span class="stat-label">TOTAL AUCTION VOLUME</span>
                        <span class="stat-value">{{ formatVolume(auctionStats.totalVolume) }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">PARTICIPATING STOCKS</span>
                        <span class="stat-value">{{ auctionStats.participatingStocks }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">AUCTION SUCCESS RATE</span>
                        <span class="stat-value">{{ auctionStats.successRate.toFixed(1) }}%</span>
                    </div>
                </div>
            </el-card>
        </div>

        <el-card class="auction-data-card">
            <template #header>
                <span class="card-title">AUCTION BIDDING DETAILS</span>
            </template>

            <el-table :data="auctionData" class="auction-table" stripe border>
                <el-table-column prop="symbol" label="SYMBOL" width="100" />
                <el-table-column prop="name" label="NAME" width="150" />
                <el-table-column prop="auctionPrice" label="AUCTION PRICE" width="140" align="right" />
                <el-table-column prop="bidVolume" label="BID VOLUME" width="140" align="right" />
                <el-table-column prop="askVolume" label="ASK VOLUME" width="140" align="right" />
                <el-table-column prop="matchedVolume" label="MATCHED VOLUME" width="160" align="right" />
                <el-table-column label="STATUS" width="120" align="center">
                    <template #default="{ row }">
                        <el-tag :type="row.status === 'matched' ? 'success' : 'warning'">
                            {{ row.status === 'matched' ? 'MATCHED' : 'PENDING' }}
                        </el-tag>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, onMounted } from 'vue'
    import { ElCard, ElButton, ElTable, ElTableColumn, ElTag, ElMessage } from 'element-plus'
    import { ShoppingCart, RefreshRight } from '@element-plus/icons-vue'

    interface AuctionItem {
        symbol: string
        name: string
        auctionPrice: number
        bidVolume: number
        askVolume: number
        matchedVolume: number
        status: 'matched' | 'pending'
    }

    const loading = ref(false)

    const auctionStats = reactive({
        totalVolume: 15000000000,
        participatingStocks: 4567,
        successRate: 94.2
    })

    const auctionData = ref<AuctionItem[]>([
        {
            symbol: '000001',
            name: '平安银行',
            auctionPrice: 12.85,
            bidVolume: 1250000,
            askVolume: 980000,
            matchedVolume: 980000,
            status: 'matched'
        },
        {
            symbol: '000002',
            name: '万科A',
            auctionPrice: 18.95,
            bidVolume: 890000,
            askVolume: 750000,
            matchedVolume: 750000,
            status: 'matched'
        },
        {
            symbol: '600519',
            name: '贵州茅台',
            auctionPrice: 1850.0,
            bidVolume: 45000,
            askVolume: 38000,
            matchedVolume: 38000,
            status: 'matched'
        }
    ])

    const refreshData = async () => {
        loading.value = true
        await new Promise(resolve => setTimeout(resolve, 500))
        loading.value = false
        ElMessage.success('Auction data refreshed')
    }

    const formatVolume = (volume: number) => {
        if (volume >= 100000000) return (volume / 100000000).toFixed(1) + '亿'
        if (volume >= 10000) return (volume / 10000).toFixed(1) + '万'
        return volume.toString()
    }

    onMounted(() => {
        refreshData()
    })
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .auction-container {
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

    .auction-overview .overview-card :deep(.el-card__body) { padding: var(--spacing-lg); }
    .overview-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-lg); }
    .stat-item { text-align: center; padding: var(--spacing-md); background: var(--color-bg-secondary); border-radius: var(--border-radius-md); }
    .stat-label { display: block; font-size: var(--font-size-xs); color: var(--color-text-tertiary); margin-bottom: var(--spacing-xs); }
    .stat-value { font-size: var(--font-size-xl); font-weight: 700; color: var(--color-text-primary); }

    .auction-data-card :deep(.el-card__header) { padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--color-border); }
    .auction-table :deep(.el-table__header th) { background: var(--color-bg-secondary); }
</style>
