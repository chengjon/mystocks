<template>
    <div class="screener-container">
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Search /></el-icon>
                    STOCK SCREENER
                </h1>
                <p class="page-subtitle">ADVANCED STOCK FILTERING AND SELECTION TOOLS</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="runScreening">
                    <template #icon><Search /></template>
                    RUN SCREENING
                </el-button>
                <el-button @click="clearFilters">CLEAR FILTERS</el-button>
            </div>
        </div>

        <div class="filters-section">
            <el-card class="filters-card">
                <template #header>
                    <span class="card-title">SCREENING CRITERIA</span>
                </template>

                <div class="filters-grid">
                    <div class="filter-group">
                        <h4 class="filter-title">Price & Valuation</h4>
                        <div class="filter-row">
                            <el-input-number
                                v-model="filters.priceMin"
                                :min="0"
                                :precision="2"
                                placeholder="Min Price"
                                size="small"
                            />
                            <span>to</span>
                            <el-input-number
                                v-model="filters.priceMax"
                                :min="0"
                                :precision="2"
                                placeholder="Max Price"
                                size="small"
                            />
                        </div>
                        <div class="filter-row">
                            <el-input-number
                                v-model="filters.peMin"
                                :min="0"
                                :precision="1"
                                placeholder="Min P/E"
                                size="small"
                            />
                            <span>to</span>
                            <el-input-number
                                v-model="filters.peMax"
                                :min="0"
                                :precision="1"
                                placeholder="Max P/E"
                                size="small"
                            />
                        </div>
                    </div>

                    <div class="filter-group">
                        <h4 class="filter-title">Volume & Liquidity</h4>
                        <div class="filter-row">
                            <el-input-number
                                v-model="filters.volumeMin"
                                :min="0"
                                placeholder="Min Volume"
                                size="small"
                            />
                            <span>to</span>
                            <el-input-number
                                v-model="filters.volumeMax"
                                :min="0"
                                placeholder="Max Volume"
                                size="small"
                            />
                        </div>
                        <div class="filter-row">
                            <el-input-number
                                v-model="filters.amountMin"
                                :min="0"
                                placeholder="Min Amount"
                                size="small"
                            />
                            <span>to</span>
                            <el-input-number
                                v-model="filters.amountMax"
                                :min="0"
                                placeholder="Max Amount"
                                size="small"
                            />
                        </div>
                    </div>

                    <div class="filter-group">
                        <h4 class="filter-title">Performance</h4>
                        <div class="filter-row">
                            <el-select v-model="filters.changeType" size="small">
                                <el-option label="Any Change" value="any" />
                                <el-option label="Gainers Only" value="positive" />
                                <el-option label="Losers Only" value="negative" />
                            </el-select>
                        </div>
                        <div class="filter-row">
                            <el-input-number
                                v-model="filters.changePercentMin"
                                :precision="2"
                                placeholder="Min % Change"
                                size="small"
                            />
                            <span>to</span>
                            <el-input-number
                                v-model="filters.changePercentMax"
                                :precision="2"
                                placeholder="Max % Change"
                                size="small"
                            />
                        </div>
                    </div>

                    <div class="filter-group">
                        <h4 class="filter-title">Market Cap</h4>
                        <div class="filter-row">
                            <el-select v-model="filters.marketCapRange" size="small">
                                <el-option label="Any Size" value="any" />
                                <el-option label="Large Cap (>500亿)" value="large" />
                                <el-option label="Mid Cap (50-500亿)" value="mid" />
                                <el-option label="Small Cap (<50亿)" value="small" />
                            </el-select>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <div class="results-section">
            <el-card class="results-card">
                <template #header>
                    <div class="results-header">
                        <span class="card-title">SCREENING RESULTS</span>
                        <span class="results-count">({{ filteredStocks.length }} stocks found)</span>
                    </div>
                </template>

                <el-table :data="filteredStocks" class="results-table" stripe border height="500">
                    <el-table-column prop="symbol" label="SYMBOL" width="100" fixed />
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
                    <el-table-column prop="amount" label="AMOUNT" width="140" align="right" />
                    <el-table-column prop="pe" label="P/E" width="100" align="right" />
                    <el-table-column prop="marketCap" label="MARKET CAP" width="140" align="right" />
                </el-table>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, computed } from 'vue'
    import {
        ElCard,
        ElButton,
        ElInputNumber,
        ElSelect,
        ElOption,
        ElTable,
        ElTableColumn,
        ElMessage
    } from 'element-plus'
    import { Search } from '@element-plus/icons-vue'

    const filters = reactive({
        priceMin: undefined,
        priceMax: undefined,
        peMin: undefined,
        peMax: undefined,
        volumeMin: undefined,
        volumeMax: undefined,
        amountMin: undefined,
        amountMax: undefined,
        changeType: 'any',
        changePercentMin: undefined,
        changePercentMax: undefined,
        marketCapRange: 'any'
    })

    const allStocks = ref([
        {
            symbol: '000001',
            name: '平安银行',
            price: 12.85,
            changePercent: 1.18,
            volume: 125000000,
            amount: 1606250000,
            pe: 8.5,
            marketCap: 350000000000
        },
        {
            symbol: '000002',
            name: '万科A',
            price: 18.95,
            changePercent: -1.3,
            volume: 98000000,
            amount: 1859100000,
            pe: 12.3,
            marketCap: 280000000000
        },
        {
            symbol: '600036',
            name: '招商银行',
            price: 42.8,
            changePercent: 2.03,
            volume: 45000000,
            amount: 1926000000,
            pe: 11.2,
            marketCap: 950000000000
        },
        {
            symbol: '000858',
            name: '五粮液',
            price: 128.5,
            changePercent: -1.76,
            volume: 12000000,
            amount: 1542000000,
            pe: 25.8,
            marketCap: 480000000000
        },
        {
            symbol: '300750',
            name: '宁德时代',
            price: 245.8,
            changePercent: 2.16,
            volume: 35000000,
            amount: 8623000000,
            pe: 45.6,
            marketCap: 1200000000000
        }
    ])

    const filteredStocks = computed(() => {
        return allStocks.value.filter(stock => {
            // Price filter
            if (filters.priceMin && stock.price < filters.priceMin) return false
            if (filters.priceMax && stock.price > filters.priceMax) return false

            // P/E filter
            if (filters.peMin && stock.pe < filters.peMin) return false
            if (filters.peMax && stock.pe > filters.peMax) return false

            // Volume filter
            if (filters.volumeMin && stock.volume < filters.volumeMin) return false
            if (filters.volumeMax && stock.volume > filters.volumeMax) return false

            // Amount filter
            if (filters.amountMin && stock.amount < filters.amountMin) return false
            if (filters.amountMax && stock.amount > filters.amountMax) return false

            // Change type filter
            if (filters.changeType === 'positive' && stock.changePercent < 0) return false
            if (filters.changeType === 'negative' && stock.changePercent > 0) return false

            // Change percent filter
            if (filters.changePercentMin && stock.changePercent < filters.changePercentMin) return false
            if (filters.changePercentMax && stock.changePercent > filters.changePercentMax) return false

            // Market cap filter
            const capRanges = {
                large: stock.marketCap > 50000000000,
                mid: stock.marketCap >= 5000000000 && stock.marketCap <= 50000000000,
                small: stock.marketCap < 5000000000
            }
            if (filters.marketCapRange !== 'any' && !(capRanges as any)[filters.marketCapRange]) return false

            return true
        })
    })

    const runScreening = async () => {
        await new Promise(resolve => setTimeout(resolve, 500))
        ElMessage.success(`Found ${filteredStocks.value.length} stocks matching criteria`)
    }

    const clearFilters = () => {
        Object.keys(filters).forEach(key => {
            ;(filters as any)[key] = key.includes('Type') || key.includes('Range') ? 'any' : undefined
        })
        ElMessage.info('Filters cleared')
    }
</script>

<style scoped lang="scss">
    @import '@/styles/theme-tokens.scss';

    .screener-container {
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

    .filters-section .filters-card :deep(.el-card__header) { padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--color-border); }
    .card-title { font-family: var(--font-family-sans); font-size: var(--font-size-sm); font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--color-accent); }

    .filters-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--spacing-lg); }
    .filter-group { background: var(--color-bg-secondary); padding: var(--spacing-lg); border-radius: var(--border-radius-md); }
    .filter-title { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-accent); margin: 0 0 var(--spacing-md) 0; }
    .filter-row { display: flex; align-items: center; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); }

    .results-section .results-card :deep(.el-card__header) { padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--color-border); }
    .results-header { display: flex; align-items: center; justify-content: space-between; }
    .results-count { font-family: var(--font-family-mono); font-size: var(--font-size-xs); color: var(--color-text-tertiary); }

    .results-table :deep(.el-table__header th) { background: var(--color-bg-secondary); }
    .positive { color: var(--color-stock-up); }
    .negative { color: var(--color-stock-down); }

    @media (max-width: 1200px) {
      .filters-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 768px) {
      .screener-container { padding: var(--spacing-md); }
      .page-header { flex-direction: column; align-items: flex-start; gap: var(--spacing-md); }
      .filter-row { flex-direction: column; align-items: stretch; }
    }
</style>
