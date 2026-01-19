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
          v-for="stat in marketStats"
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
            v-for="update in realtimeUpdates"
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
import { ref, onMounted, computed } from 'vue'
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

// Computed properties
const activeUpdates = computed(() =>
  realtimeUpdates.value.filter(update => update.isNew)
)

// Methods
const handleFilterChange = (newFilters: any) => {
  console.log('Filters changed:', newFilters)
  // TODO: Apply filters to market data
}

const handleSortChange = (sortKey: string, sortOrder: string) => {
  console.log('Sort changed:', sortKey, sortOrder)
  // TODO: Sort market data
}

const handleRowClick = (row: any) => {
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
const getPriceClass = (row: any) => {
  return row.change > 0 ? 'positive' : row.change < 0 ? 'negative' : 'neutral'
}

const getChangeClass = (row: any) => {
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
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.market-data-page {
  @include artdeco-layout;
  position: relative;

  // Art Deco geometric corner decorations
  @include artdeco-geometric-corners(var(--artdeco-gold-primary));

  // Gold accent top border
  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg,
      transparent 0%,
      var(--artdeco-gold-primary) 20%,
      var(--artdeco-gold-hover) 50%,
      var(--artdeco-gold-primary) 80%,
      transparent 100%
    );
    z-index: var(--artdeco-z-10);
  }

  .market-header {
    margin-bottom: var(--artdeco-spacing-8);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
    font-weight: var(--artdeco-font-bold);
  }

  // Market statistics section
  .market-stats {
    margin-bottom: var(--artdeco-spacing-12);

    .stats-grid {
      gap: var(--artdeco-spacing-6);
    }

    .market-stat-card {
      @include artdeco-hover-lift-glow;
      background: var(--artdeco-bg-card);
      border: 1px solid var(--artdeco-gold-dim);
      transition: all var(--artdeco-transition-base);
    }
  }

  .main-content {
    @include artdeco-content-spacing;
  }

  // Filter bar with Art Deco styling
  .market-filter-bar {
    margin-bottom: var(--artdeco-spacing-8);
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-dim);
    border-radius: var(--artdeco-radius-md);
    padding: var(--artdeco-spacing-6);
    @include artdeco-geometric-corners(var(--artdeco-gold-primary), 12px);

    :deep(.filter-actions) {
      display: flex;
      gap: var(--artdeco-spacing-4);
      align-items: center;

      .refresh-btn {
        background: var(--artdeco-gold-primary);
        color: var(--artdeco-bg-global);
        border: none;
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
        border-radius: var(--artdeco-radius-sm);
        font-family: var(--artdeco-font-body);
        font-weight: var(--artdeco-font-medium);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        transition: all var(--artdeco-transition-fast);

        &:hover {
          background: var(--artdeco-gold-hover);
          transform: translateY(-2px);
          box-shadow: var(--artdeco-glow-intense);
        }

        i {
          margin-right: var(--artdeco-spacing-2);
        }
      }

      .export-btn {
        background: linear-gradient(135deg,
          var(--artdeco-gold-primary),
          var(--artdeco-gold-hover)
        );
        color: var(--artdeco-bg-global);
        border: none;
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
        border-radius: var(--artdeco-radius-sm);
        font-family: var(--artdeco-font-body);
        font-weight: var(--artdeco-font-medium);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        position: relative;
        overflow: hidden;

        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
          );
          transition: left var(--artdeco-transition-slow);
        }

        &:hover {
          transform: translateY(-2px);
          box-shadow: var(--artdeco-glow-max);

          &::before {
            left: 100%;
          }
        }

        i {
          margin-right: var(--artdeco-spacing-2);
        }
      }
    }
  }

  // Market table card with geometric decorations
  .market-table-card {
    @include artdeco-hover-lift-glow;
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-dim);
    position: relative;
    margin-bottom: var(--artdeco-spacing-8);

    // Enhanced geometric frame decorations
    @include artdeco-geometric-corners(var(--artdeco-gold-primary), 16px);

    &::after {
      content: '';
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      background: linear-gradient(45deg,
        transparent 0%,
        var(--artdeco-gold-dim) 25%,
        transparent 50%,
        var(--artdeco-gold-dim) 75%,
        transparent 100%
      );
      border-radius: var(--artdeco-radius-md);
      z-index: -1;
      opacity: 0.3;
    }

    .market-data-table {
      :deep(.table-header) {
        background: linear-gradient(135deg,
          var(--artdeco-gold-primary),
          var(--artdeco-gold-hover)
        );
        color: var(--artdeco-bg-global);
        font-family: var(--artdeco-font-display);
        font-weight: var(--artdeco-font-bold);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        font-size: var(--artdeco-text-sm);
      }

      :deep(.table-row) {
        transition: all var(--artdeco-transition-fast);

        &:nth-child(even) {
          background: rgba(212, 175, 55, 0.02);
        }

        &:hover {
          background: rgba(212, 175, 55, 0.08);
          transform: translateX(4px);
        }

        .price-cell {
          font-family: var(--artdeco-font-mono);
          font-weight: var(--artdeco-font-bold);
          font-size: var(--artdeco-text-base);

          &.positive {
            color: var(--artdeco-up);
          }

          &.negative {
            color: var(--artdeco-down);
          }

          &.neutral {
            color: var(--artdeco-fg-primary);
          }
        }

        .change-cell {
          font-family: var(--artdeco-font-accent);
          font-weight: var(--artdeco-font-medium);
          font-size: var(--artdeco-text-sm);

          &.positive {
            color: var(--artdeco-up);
          }

          &.negative {
            color: var(--artdeco-down);
          }

          &.neutral {
            color: var(--artdeco-fg-muted);
          }
        }

        .volume-cell {
          font-family: var(--artdeco-font-mono);
          color: var(--artdeco-fg-primary);
          font-size: var(--artdeco-text-sm);
        }
      }
    }

    // Loading overlay with Art Deco animation
    .loading-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(10, 10, 10, 0.8);
      backdrop-filter: blur(4px);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: var(--artdeco-z-modal);

      .loading-text {
        margin-top: var(--artdeco-spacing-4);
        color: var(--artdeco-gold-primary);
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-lg);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        animation: artdeco-pulse-text 2s ease-in-out infinite;
      }
    }
  }

  // Market chart card
  .market-chart-card {
    @include artdeco-hover-lift-glow;
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-dim);
    margin-bottom: var(--artdeco-spacing-8);

    .chart-container {
      position: relative;
      height: 400px;

      .chart-placeholder {
        height: 100%;
        background: linear-gradient(135deg,
          var(--artdeco-bg-card) 0%,
          rgba(212, 175, 55, 0.05) 50%,
          var(--artdeco-bg-card) 100%
        );
        border-radius: var(--artdeco-radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--artdeco-fg-muted);
        position: relative;
        overflow: hidden;

        .market-indicators-overlay {
          position: absolute;
          top: var(--artdeco-spacing-6);
          right: var(--artdeco-spacing-6);
          display: flex;
          flex-direction: column;
          gap: var(--artdeco-spacing-3);
          background: rgba(10, 10, 10, 0.8);
          backdrop-filter: blur(8px);
          padding: var(--artdeco-spacing-4);
          border-radius: var(--artdeco-radius-md);
          border: 1px solid var(--artdeco-gold-dim);

          .indicator-item {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-1);
            min-width: 120px;

            .indicator-label {
              font-family: var(--artdeco-font-accent);
              font-size: var(--artdeco-text-xs);
              color: var(--artdeco-fg-muted);
              text-transform: uppercase;
              letter-spacing: var(--artdeco-tracking-wide);
            }

            .indicator-value {
              font-family: var(--artdeco-font-mono);
              font-weight: var(--artdeco-font-bold);
              font-size: var(--artdeco-text-lg);

              &.positive {
                color: var(--artdeco-up);
              }

              &.negative {
                color: var(--artdeco-down);
              }
            }

            .indicator-change {
              font-family: var(--artdeco-font-accent);
              font-size: var(--artdeco-text-sm);

              &.positive {
                color: var(--artdeco-up);
              }

              &.negative {
                color: var(--artdeco-down);
              }
            }
          }
        }
      }
    }
  }

  // Real-time updates card
  .realtime-updates-card {
    @include artdeco-hover-lift-glow;
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-dim);

    .updates-list {
      max-height: 300px;
      overflow-y: auto;

      &::-webkit-scrollbar {
        width: 6px;
      }

      &::-webkit-scrollbar-track {
        background: var(--artdeco-bg-card);
      }

      &::-webkit-scrollbar-thumb {
        background: var(--artdeco-gold-dim);
        border-radius: 3px;
      }

      .update-item {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);
        padding: var(--artdeco-spacing-3);
        border-bottom: 1px solid var(--artdeco-border-default);
        transition: all var(--artdeco-transition-fast);

        &:hover {
          background: rgba(212, 175, 55, 0.05);
        }

        &.new-update {
          background: rgba(39, 174, 96, 0.1);
          border-left: 3px solid var(--artdeco-success);

          .update-indicator {
            background: var(--artdeco-success);
            box-shadow: 0 0 8px rgba(39, 174, 96, 0.6);
          }
        }

        .update-time {
          font-family: var(--artdeco-font-mono);
          font-size: var(--artdeco-text-sm);
          color: var(--artdeco-fg-muted);
          min-width: 80px;
        }

        .update-content {
          flex: 1;
          display: flex;
          gap: var(--artdeco-spacing-2);
          align-items: center;

          .update-symbol {
            font-family: var(--artdeco-font-mono);
            font-weight: var(--artdeco-font-bold);
            color: var(--artdeco-gold-primary);
            background: rgba(212, 175, 55, 0.1);
            padding: 2px 6px;
            border-radius: var(--artdeco-radius-sm);
            font-size: var(--artdeco-text-xs);
          }

          .update-action {
            font-family: var(--artdeco-font-body);
            font-weight: var(--artdeco-font-medium);
            color: var(--artdeco-fg-primary);
            font-size: var(--artdeco-text-sm);
          }

          .update-details {
            font-family: var(--artdeco-font-accent);
            color: var(--artdeco-fg-muted);
            font-size: var(--artdeco-text-sm);
          }
        }

        .update-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          flex-shrink: 0;

          &.buy {
            background: var(--artdeco-up);
            box-shadow: 0 0 6px rgba(255, 82, 82, 0.6);
          }

          &.sell {
            background: var(--artdeco-down);
            box-shadow: 0 0 6px rgba(0, 230, 118, 0.6);
          }

          &.suspended {
            background: var(--artdeco-warning);
            box-shadow: 0 0 6px rgba(255, 215, 0, 0.6);
          }
        }
      }
    }
  }
}

// Art Deco animations
@keyframes artdeco-pulse-text {
  0%, 100% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
}

// Responsive design for Art Deco market data
@media (max-width: 1200px) {
  .market-data-page {
    .stats-grid {
      grid-template-columns: 1fr 1fr;
    }
  }
}

@media (max-width: 768px) {
  .market-data-page {
    .market-stats {
      .stats-grid {
        grid-template-columns: 1fr;
      }
    }

    .market-filter-bar {
      :deep(.filter-actions) {
        flex-direction: column;
        gap: var(--artdeco-spacing-3);

        .refresh-btn,
        .export-btn {
          width: 100%;
          justify-content: center;
        }
      }
    }

    .market-table-card {
      .market-data-table {
        :deep(.table-row) {
          &:hover {
            transform: none;
          }
        }
      }
    }

    .market-chart-card {
      .chart-container {
        height: 300px;

        .chart-placeholder {
          .market-indicators-overlay {
            position: static;
            margin-top: var(--artdeco-spacing-4);
            width: 100%;
            flex-direction: row;
            justify-content: space-around;
            flex-wrap: wrap;
          }
        }
      }
    }
  }
}
</style>