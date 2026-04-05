<template>
  <div class="market-data-page">
    <ArtDecoHeader
      :title="pageTitle"
      subtitle="实时市场数据监控"
      variant="gold-accent"
      class="market-header"
    />

    <!-- Market Statistics Cards -->
    <div class="market-stats">
      <ArtDecoGrid columns="4" responsive class="stats-grid">
        <ArtDecoStatCard
          v-for="(stat, _idx) in marketStats"
          :key="stat.id"
          :title="stat.title"
          :value="stat.value"
          :change="stat.change"
          :changeType="stat.changeType"
          animated
          class="market-stat-card"
        />
      </ArtDecoGrid>
    </div>

    <div class="main-content">
      <!-- Filter Bar with Art Deco styling -->
      <ArtDecoFilterBar
        v-model="filters"
        :filters="filterOptions"
        @filter-change="handleFilterChange"
        class="market-filter-bar"
      >
        <template #actions>
          <ArtDecoButton
            variant="primary"
            @click="refreshData"
            class="refresh-btn"
          >
            <i class="fas fa-sync-alt"></i>
            刷新数据
          </ArtDecoButton>
          <ArtDecoButton
            variant="gold-glow"
            @click="exportData"
            animated
            class="export-btn"
          >
            <i class="fas fa-download"></i>
            导出数据
          </ArtDecoButton>
        </template>
      </ArtDecoFilterBar>

      <!-- Market Data Table with gold headers and striped rows -->
      <ArtDecoCard
        title="实时行情数据"
        variant="luxury"
        decorated
        class="market-table-card"
      >
        <ArtDecoTable
          :data="marketData"
          :columns="tableColumns"
          gold-headers
          striped
          hover
          sortable
          @sort-change="handleSortChange"
          @row-click="handleRowClick"
          class="market-data-table"
        >
          <!-- Custom column templates for real-time data -->
          <template #price="{ row }">
            <span
              class="price-cell"
              :class="getPriceClass(row)"
            >
              {{ formatPrice(row.price) }}
            </span>
          </template>

          <template #change="{ row }">
            <span
              class="change-cell"
              :class="getChangeClass(row)"
            >
              {{ formatChange(row.change) }}
            </span>
          </template>

          <template #volume="{ row }">
            <span class="volume-cell">
              {{ formatVolume(row.volume) }}
            </span>
          </template>

          <template #status="{ row }">
            <ArtDecoBadge
              :variant="getStatusVariant(row.status)"
              animated
            >
              {{ getStatusText(row.status) }}
            </ArtDecoBadge>
          </template>
        </ArtDecoTable>

        <!-- Loading state with Art Deco animation -->
        <div v-if="loading" class="loading-overlay">
          <ArtDecoLoader size="large" />
          <div class="loading-text">正在加载市场数据...</div>
        </div>
      </ArtDecoCard>

      <!-- Market Overview Chart -->
      <ArtDecoCard
        title="市场走势概览"
        variant="luxury"
        decorated
        class="market-chart-card"
      >
        <div class="chart-container">
          <div class="chart-placeholder">
            <!-- Chart will be rendered here -->
            <div class="market-indicators-overlay">
              <div class="indicator-item">
                <span class="indicator-label">上证指数</span>
                <span class="indicator-value positive">3128.45</span>
                <span class="indicator-change positive">+0.85%</span>
              </div>
              <div class="indicator-item">
                <span class="indicator-label">深证成指</span>
                <span class="indicator-value positive">10245.67</span>
                <span class="indicator-change positive">+1.12%</span>
              </div>
              <div class="indicator-item">
                <span class="indicator-label">创业板指</span>
                <span class="indicator-value negative">2156.89</span>
                <span class="indicator-change negative">-0.34%</span>
              </div>
            </div>
          </div>
        </div>
      </ArtDecoCard>

      <!-- Real-time Updates Section -->
      <ArtDecoCard
        title="实时更新日志"
        variant="luxury"
        decorated
        class="realtime-updates-card"
      >
        <div class="updates-list">
          <div
            v-for="(update, _idx) in realtimeUpdates"
            :key="update.id"
            class="update-item"
            :class="{ 'new-update': update.isNew }"
          >
            <div class="update-time">{{ update.time }}</div>
            <div class="update-content">
              <span class="update-symbol">{{ update.symbol }}</span>
              <span class="update-action">{{ update.action }}</span>
              <span class="update-details">{{ update.details }}</span>
            </div>
            <div class="update-indicator" :class="update.type"></div>
          </div>
        </div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
// ArtDeco component imports
import {
  ArtDecoHeader,
  ArtDecoCard,
  ArtDecoTable,
  ArtDecoGrid,
  ArtDecoStatCard,
  ArtDecoFilterBar,
  ArtDecoButton,
  ArtDecoBadge,
  ArtDecoLoader
} from '@/components/artdeco'

// Component logic
const pageTitle = ref('MARKET DATA')

// Loading state
const loading = ref(false)

// Market statistics
const marketStats = ref([
  {
    id: 'total-stocks',
    title: '总股票数',
    value: '4,862',
    change: '+12',
    changeType: 'positive'
  },
  {
    id: 'active-trades',
    title: '活跃交易',
    value: '1,245',
    change: '+8.5%',
    changeType: 'positive'
  },
  {
    id: 'market-cap',
    title: '总市值',
    value: '¥45.2T',
    change: '+2.1%',
    changeType: 'positive'
  },
  {
    id: 'volume',
    title: '成交量',
    value: '¥2.8T',
    change: '+15.3%',
    changeType: 'positive'
  }
])

// Filters
const filters = ref({
  exchange: '',
  sector: '',
  priceRange: '',
  volumeRange: ''
})

const filterOptions = ref([
  {
    key: 'exchange',
    label: '交易所',
    type: 'select',
    options: [
      { label: '上海证券交易所', value: 'SSE' },
      { label: '深圳证券交易所', value: 'SZSE' },
      { label: '北京证券交易所', value: 'BSE' }
    ]
  },
  {
    key: 'sector',
    label: '行业板块',
    type: 'select',
    options: [
      { label: '银行', value: 'bank' },
      { label: '房地产', value: 'real-estate' },
      { label: '科技', value: 'technology' },
      { label: '医药', value: 'pharmaceutical' }
    ]
  },
  {
    key: 'priceRange',
    label: '价格区间',
    type: 'range',
    min: 0,
    max: 1000,
    unit: '¥'
  },
  {
    key: 'volumeRange',
    label: '成交量区间',
    type: 'range',
    min: 0,
    max: 1000000000,
    unit: '手'
  }
])

// Table columns
const tableColumns = ref([
  { key: 'symbol', title: '股票代码', width: '12%', sortable: true },
  { key: 'name', title: '股票名称', width: '15%', sortable: true },
  { key: 'price', title: '最新价', width: '12%', sortable: true },
  { key: 'change', title: '涨跌幅', width: '12%', sortable: true },
  { key: 'volume', title: '成交量', width: '15%', sortable: true },
  { key: 'amount', title: '成交额', width: '15%', sortable: true },
  { key: 'status', title: '状态', width: '10%' }
])

// Market data
const marketData = ref([
  {
    symbol: '600000',
    name: '浦发银行',
    price: 8.45,
    change: 2.15,
    volume: 125000000,
    amount: 1056250000,
    status: 'active'
  },
  {
    symbol: '000001',
    name: '平安银行',
    price: 12.85,
    change: -0.85,
    volume: 98000000,
    amount: 1258830000,
    status: 'active'
  },
  {
    symbol: '000002',
    name: '万科A',
    price: 18.95,
    change: 1.25,
    volume: 156000000,
    amount: 2958200000,
    status: 'suspended'
  }
])

// Real-time updates
const realtimeUpdates = ref([
  {
    id: 1,
    time: '14:32:15',
    symbol: '600000',
    action: '买入',
    details: '1000股 @ ¥8.45',
    type: 'buy',
    isNew: true
  },
  {
    id: 2,
    time: '14:31:42',
    symbol: '000001',
    action: '卖出',
    details: '500股 @ ¥12.85',
    type: 'sell',
    isNew: true
  },
  {
    id: 3,
    time: '14:30:28',
    symbol: '000002',
    action: '停牌',
    details: '临时停牌处理',
    type: 'suspended',
    isNew: false
  }
])

// Methods
const handleFilterChange = (newFilters: unknown) => {
  console.log('Filters changed:', newFilters)
  // TODO: Apply filters to market data
}

const handleSortChange = (sortKey: string, sortOrder: string) => {
  console.log('Sort changed:', sortKey, sortOrder)
  // TODO: Sort market data
}

const handleRowClick = (row: unknown) => {
  console.log('Row clicked:', row)
  // TODO: Navigate to stock detail
}

const refreshData = async () => {
  loading.value = true
  try {
    // TODO: Refresh market data from API
    await new Promise(resolve => setTimeout(resolve, 2000))
    console.log('Market data refreshed')
  } catch (error) {
    console.error('Failed to refresh data:', error)
  } finally {
    loading.value = false
  }
}

const exportData = () => {
  console.log('Exporting market data...')
  // TODO: Implement data export
}

// Utility methods
const getPriceClass = (row: unknown) => {
  return row.change > 0 ? 'positive' : row.change < 0 ? 'negative' : 'neutral'
}

const getChangeClass = (row: unknown) => {
  return row.change > 0 ? 'positive' : row.change < 0 ? 'negative' : 'neutral'
}

const getStatusVariant = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'suspended': return 'warning'
    case 'delisted': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'active': return '正常'
    case 'suspended': return '停牌'
    case 'delisted': return '退市'
    default: return '未知'
  }
}

const formatPrice = (price: number) => {
  return `¥${price.toFixed(2)}`
}

const formatChange = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(1)}亿`
  } else if (volume >= 10000) {
    return `${(volume / 10000).toFixed(1)}万`
  }
  return volume.toString()
}

const loadData = async () => {
  loading.value = true
  try {
    // TODO: Load market data from API
    console.log('Loading market data...')
  } catch (error) {
    console.error('Failed to load market data:', error)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadData()
})

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped lang="scss">
@use './styles/market-data.scss' as *;
</style>
