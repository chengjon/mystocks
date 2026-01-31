<template>
  <div class="market-quotes-page">
    <ArtDecoHeader
      :title="pageTitle"
      subtitle="实时市场行情监控"
      variant="gold-accent"
      class="quotes-header"
    />

    <!-- Market Status Overview -->
    <div class="market-overview">
      <ArtDecoGrid columns="4" responsive class="overview-grid">
        <ArtDecoStatCard
          v-for="index in marketIndices"
          :key="index.code"
          :title="index.name"
          :value="index.value"
          :change="index.change"
          :changeType="index.changeType"
          animated
          class="index-card"
        />
      </ArtDecoGrid>
    </div>

    <!-- Market Status Badges -->
    <div class="market-status">
      <ArtDecoBadge
        v-for="status in marketStatuses"
        :key="status.id"
        :variant="status.variant"
        animated
        class="status-badge"
      >
        <i :class="status.icon"></i>
        {{ status.text }}
      </ArtDecoBadge>
    </div>

    <div class="main-content">
      <!-- Real-time Ticker List with Art Deco styling -->
      <ArtDecoCard
        title="实时行情列表"
        variant="luxury"
        decorated
        class="ticker-list-card"
      >
        <ArtDecoTickerList
          :tickers="tickerData"
          :columns="tickerColumns"
          gold-headers
          hover-effects
          animated
          @ticker-click="handleTickerClick"
          @sort-change="handleSortChange"
          class="quotes-ticker-list"
        >
          <!-- Custom price change indicators -->
          <template #price-change="{ ticker }">
            <div class="price-change-indicator">
              <span
                class="current-price"
                :class="getPriceClass(ticker)"
              >
                {{ formatPrice(ticker.price) }}
              </span>
              <span
                class="price-change"
                :class="getChangeClass(ticker)"
              >
                {{ formatChange(ticker.change) }}
                <i
                  :class="getChangeIcon(ticker)"
                  class="change-icon"
                ></i>
              </span>
            </div>
          </template>

          <!-- Volume with Art Deco styling -->
          <template #volume="{ ticker }">
            <span class="volume-display">
              {{ formatVolume(ticker.volume) }}
            </span>
          </template>

          <!-- Market cap display -->
          <template #market-cap="{ ticker }">
            <span class="market-cap-display">
              {{ formatMarketCap(ticker.marketCap) }}
            </span>
          </template>
        </ArtDecoTickerList>

        <!-- Real-time update indicator -->
        <div class="realtime-indicator">
          <div class="indicator-dot" :class="{ active: isConnected }"></div>
          <span class="indicator-text">
            {{ isConnected ? '实时数据连接正常' : '连接中...' }}
          </span>
          <span class="last-update-time">
            最后更新: {{ lastUpdateTime }}
          </span>
        </div>
      </ArtDecoCard>

      <!-- Top Gainers/Losers Section -->
      <div class="gainers-losers-section">
        <ArtDecoGrid columns="2" responsive class="gainers-losers-grid">
          <!-- Top Gainers -->
          <ArtDecoCard
            title="涨幅榜"
            variant="luxury"
            decorated
            class="gainers-card"
          >
            <div class="gainers-list">
              <div
                v-for="stock in topGainers"
                :key="stock.symbol"
                class="gainer-item"
                @click="handleStockClick(stock)"
              >
                <div class="stock-info">
                  <span class="stock-symbol">{{ stock.symbol }}</span>
                  <span class="stock-name">{{ stock.name }}</span>
                </div>
                <div class="stock-prices">
                  <span class="current-price positive">{{ formatPrice(stock.price) }}</span>
                  <span class="change-amount positive">
                    +{{ formatChange(stock.change) }}
                    <i class="fas fa-arrow-up change-icon"></i>
                  </span>
                </div>
              </div>
            </div>
          </ArtDecoCard>

          <!-- Top Losers -->
          <ArtDecoCard
            title="跌幅榜"
            variant="luxury"
            decorated
            class="losers-card"
          >
            <div class="losers-list">
              <div
                v-for="stock in topLosers"
                :key="stock.symbol"
                class="loser-item"
                @click="handleStockClick(stock)"
              >
                <div class="stock-info">
                  <span class="stock-symbol">{{ stock.symbol }}</span>
                  <span class="stock-name">{{ stock.name }}</span>
                </div>
                <div class="stock-prices">
                  <span class="current-price negative">{{ formatPrice(stock.price) }}</span>
                  <span class="change-amount negative">
                    {{ formatChange(stock.change) }}
                    <i class="fas fa-arrow-down change-icon"></i>
                  </span>
                </div>
              </div>
            </div>
          </ArtDecoCard>
        </ArtDecoGrid>
      </div>

      <!-- Market Heat Map -->
      <ArtDecoCard
        title="市场热度图"
        variant="luxury"
        decorated
        class="heatmap-card"
      >
        <div class="heatmap-container">
          <div class="heatmap-placeholder">
            <!-- Heatmap will be rendered here -->
            <div class="sector-indicators">
              <div
                v-for="sector in marketSectors"
                :key="sector.name"
                class="sector-item"
                :style="{ backgroundColor: getSectorColor(sector) }"
              >
                <span class="sector-name">{{ sector.name }}</span>
                <span class="sector-change" :class="getChangeClass(sector)">
                  {{ formatChange(sector.change) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </ArtDecoCard>

      <!-- Market Alerts Section -->
      <ArtDecoCard
        title="市场提醒"
        variant="luxury"
        decorated
        class="alerts-card"
      >
        <div class="market-alerts">
          <div
            v-for="alert in marketAlerts"
            :key="alert.id"
            class="alert-item"
            :class="alert.type"
          >
            <div class="alert-icon">
              <i :class="alert.icon"></i>
            </div>
            <div class="alert-content">
              <div class="alert-title">{{ alert.title }}</div>
              <div class="alert-message">{{ alert.message }}</div>
              <div class="alert-time">{{ alert.time }}</div>
            </div>
            <ArtDecoBadge
              :variant="alert.badgeVariant"
              class="alert-badge"
            >
              {{ alert.badgeText }}
            </ArtDecoBadge>
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
  ArtDecoGrid,
  ArtDecoStatCard,
  ArtDecoBadge,
  ArtDecoTickerList
} from '@/components/artdeco'

// Component logic
const pageTitle = ref('LIVE MARKET QUOTES')

// WebSocket connection status
const isConnected = ref(false)
const lastUpdateTime = ref('--:--:--')

// Market indices
const marketIndices = ref([
  {
    code: '000001',
    name: '上证指数',
    value: '3,128.45',
    change: '+0.85%',
    changeType: 'positive'
  },
  {
    code: '399001',
    name: '深证成指',
    value: '10,245.67',
    change: '+1.12%',
    changeType: 'positive'
  },
  {
    code: '399006',
    name: '创业板指',
    value: '2,156.89',
    change: '-0.34%',
    changeType: 'negative'
  },
  {
    code: '000300',
    name: '沪深300',
    value: '3,845.23',
    change: '+0.92%',
    changeType: 'positive'
  }
])

// Market statuses
const marketStatuses = ref([
  {
    id: 'market-open',
    text: '市场开盘',
    variant: 'success',
    icon: 'fas fa-play-circle'
  },
  {
    id: 'data-flow',
    text: '数据正常',
    variant: 'info',
    icon: 'fas fa-wifi'
  },
  {
    id: 'alerts-active',
    text: '提醒激活',
    variant: 'warning',
    icon: 'fas fa-bell'
  }
])

// Ticker columns configuration
const tickerColumns = ref([
  { key: 'symbol', title: '股票代码', width: '15%' },
  { key: 'name', title: '股票名称', width: '20%' },
  { key: 'price', title: '最新价', width: '15%' },
  { key: 'change', title: '涨跌幅', width: '12%' },
  { key: 'volume', title: '成交量', width: '15%' },
  { key: 'marketCap', title: '市值', width: '15%' },
  { key: 'pe', title: '市盈率', width: '8%' }
])

// Ticker data with real-time updates
const tickerData = ref([
  {
    symbol: '600000',
    name: '浦发银行',
    price: 8.45,
    change: 2.15,
    volume: 125000000,
    marketCap: 245000000000,
    pe: 6.8,
    trend: 'up',
    lastUpdate: Date.now()
  },
  {
    symbol: '000001',
    name: '平安银行',
    price: 12.85,
    change: -0.85,
    volume: 98000000,
    marketCap: 320000000000,
    pe: 8.2,
    trend: 'down',
    lastUpdate: Date.now()
  },
  {
    symbol: '000002',
    name: '万科A',
    price: 18.95,
    change: 1.25,
    volume: 156000000,
    marketCap: 285000000000,
    pe: 9.5,
    trend: 'up',
    lastUpdate: Date.now()
  },
  {
    symbol: '600036',
    name: '招商银行',
    price: 42.85,
    change: 3.45,
    volume: 89000000,
    marketCap: 1250000000000,
    pe: 11.2,
    trend: 'up',
    lastUpdate: Date.now()
  },
  {
    symbol: '000858',
    name: '五粮液',
    price: 128.50,
    change: -2.15,
    volume: 45000000,
    marketCap: 580000000000,
    pe: 25.8,
    trend: 'down',
    lastUpdate: Date.now()
  }
])

// Top gainers and losers
const topGainers = ref([
  { symbol: '600036', name: '招商银行', price: 42.85, change: 3.45 },
  { symbol: '000002', name: '万科A', price: 18.95, change: 1.25 },
  { symbol: '600000', name: '浦发银行', price: 8.45, change: 2.15 }
])

const topLosers = ref([
  { symbol: '000858', name: '五粮液', price: 128.50, change: -2.15 },
  { symbol: '000001', name: '平安银行', price: 12.85, change: -0.85 }
])

// Market sectors for heatmap
const marketSectors = ref([
  { name: '银行', change: 1.85, performance: 'good' },
  { name: '房地产', change: 0.95, performance: 'neutral' },
  { name: '科技', change: -0.45, performance: 'poor' },
  { name: '医药', change: 2.15, performance: 'good' },
  { name: '新能源', change: 1.25, performance: 'good' },
  { name: '消费', change: -0.85, performance: 'poor' }
])

// Market alerts
const marketAlerts = ref([
  {
    id: 1,
    title: '重要公告',
    message: '浦发银行发布2024年Q1业绩报告',
    time: '10:30:15',
    type: 'announcement',
    icon: 'fas fa-bullhorn',
    badgeVariant: 'warning',
    badgeText: '公告'
  },
  {
    id: 2,
    title: '价格异动',
    message: '招商银行涨幅超过5%',
    time: '10:25:42',
    type: 'price-alert',
    icon: 'fas fa-exclamation-triangle',
    badgeVariant: 'danger',
    badgeText: '异动'
  },
  {
    id: 3,
    title: '成交量激增',
    message: '万科A成交量突破历史新高',
    time: '10:20:18',
    type: 'volume-alert',
    icon: 'fas fa-chart-bar',
    badgeVariant: 'success',
    badgeText: '活跃'
  }
])

// WebSocket connection
let wsConnection: WebSocket | null = null
let updateInterval: NodeJS.Timeout | null = null

// Methods
const handleTickerClick = (ticker: any) => {
  console.log('Ticker clicked:', ticker)
  // TODO: Navigate to stock detail page
}

const handleSortChange = (sortKey: string, sortOrder: string) => {
  console.log('Sort changed:', sortKey, sortOrder)
  // TODO: Sort ticker data
}

const handleStockClick = (stock: any) => {
  console.log('Stock clicked:', stock)
  // TODO: Navigate to stock detail
}

// Utility methods
const getPriceClass = (ticker: any) => {
  return ticker.change > 0 ? 'positive' : ticker.change < 0 ? 'negative' : 'neutral'
}

const getChangeClass = (item: any) => {
  const change = item.change || item
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

const getChangeIcon = (ticker: any) => {
  return ticker.change > 0 ? 'fas fa-arrow-up' : ticker.change < 0 ? 'fas fa-arrow-down' : 'fas fa-minus'
}

const getSectorColor = (sector: any) => {
  if (sector.change > 1.5) return 'rgba(0, 230, 118, 0.8)'
  if (sector.change > 0) return 'rgba(255, 215, 0, 0.8)'
  if (sector.change > -1) return 'rgba(158, 158, 158, 0.8)'
  return 'rgba(255, 82, 82, 0.8)'
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

const formatMarketCap = (marketCap: number) => {
  if (marketCap >= 1000000000000) {
    return `${(marketCap / 1000000000000).toFixed(1)}万亿`
  } else if (marketCap >= 100000000) {
    return `${(marketCap / 100000000).toFixed(1)}亿`
  }
  return `${(marketCap / 10000).toFixed(1)}万`
}

// WebSocket connection management
const connectWebSocket = () => {
  try {
    // TODO: Implement actual WebSocket connection
    // wsConnection = new WebSocket('ws://localhost:8000/ws/market-quotes')
    isConnected.value = true
    lastUpdateTime.value = new Date().toLocaleTimeString()
    console.log('WebSocket connected')
  } catch (error) {
    console.error('WebSocket connection failed:', error)
    isConnected.value = false
  }
}

const disconnectWebSocket = () => {
  if (wsConnection) {
    wsConnection.close()
    wsConnection = null
  }
  isConnected.value = false
}

// Simulate real-time updates
const startRealtimeUpdates = () => {
  updateInterval = setInterval(() => {
    if (isConnected.value) {
      // Simulate price updates
      tickerData.value.forEach((ticker, index) => {
        const randomChange = (Math.random() - 0.5) * 0.1
        ticker.price += randomChange
        ticker.change += randomChange
        ticker.lastUpdate = Date.now()
      })

      lastUpdateTime.value = new Date().toLocaleTimeString()
    }
  }, 2000) // Update every 2 seconds
}

const stopRealtimeUpdates = () => {
  if (updateInterval) {
    clearInterval(updateInterval)
    updateInterval = null
  }
}

const loadData = async () => {
  try {
    // TODO: Load initial market data
    console.log('Loading market quotes data...')
    connectWebSocket()
    startRealtimeUpdates()
  } catch (error) {
    console.error('Failed to load market quotes:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadData()
})

onUnmounted(() => {
  disconnectWebSocket()
  stopRealtimeUpdates()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.market-quotes-page {
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

  .quotes-header {
    margin-bottom: var(--artdeco-spacing-8);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
    font-weight: var(--artdeco-font-bold);
  }

  // Market overview section
  .market-overview {
    margin-bottom: var(--artdeco-spacing-12);

    .overview-grid {
      gap: var(--artdeco-spacing-6);
    }

    .index-card {
      @include artdeco-hover-lift-glow;
      background: var(--artdeco-bg-card);
      border: 1px solid var(--artdeco-gold-dim);
      transition: all var(--artdeco-transition-base);
    }
  }

  // Market status badges
  .market-status {
    display: flex;
    gap: var(--artdeco-spacing-4);
    margin-bottom: var(--artdeco-spacing-8);
    flex-wrap: wrap;
    justify-content: center;

    .status-badge {
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
      font-family: var(--artdeco-font-body);
      font-weight: var(--artdeco-font-medium);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      font-size: var(--artdeco-text-sm);

      i {
        margin-right: var(--artdeco-spacing-2);
      }
    }
  }

  .main-content {
    @include artdeco-content-spacing;
  }

  // Ticker list card with real-time updates
  .ticker-list-card {
    @include artdeco-hover-lift-glow;
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-dim);
    margin-bottom: var(--artdeco-spacing-8);
    position: relative;

    // Enhanced geometric frame decorations
    @include artdeco-geometric-corners(var(--artdeco-gold-primary), 16px);

    .quotes-ticker-list {
      :deep(.ticker-header) {
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

      :deep(.ticker-row) {
        transition: all var(--artdeco-transition-fast);

        &:nth-child(even) {
          background: rgba(212, 175, 55, 0.02);
        }

        &:hover {
          background: rgba(212, 175, 55, 0.08);
          transform: translateX(4px);
          box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
        }

        .price-change-indicator {
          display: flex;
          flex-direction: column;
          gap: var(--artdeco-spacing-1);

          .current-price {
            font-family: var(--artdeco-font-mono);
            font-weight: var(--artdeco-font-bold);
            font-size: var(--artdeco-text-base);

            &.positive {
              color: var(--artdeco-up);
              animation: artdeco-price-flash-up 0.5s ease-out;
            }

            &.negative {
              color: var(--artdeco-down);
              animation: artdeco-price-flash-down 0.5s ease-out;
            }

            &.neutral {
              color: var(--artdeco-fg-primary);
            }
          }

          .price-change {
            font-family: var(--artdeco-font-accent);
            font-weight: var(--artdeco-font-medium);
            font-size: var(--artdeco-text-sm);
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-1);

            &.positive {
              color: var(--artdeco-up);
            }

            &.negative {
              color: var(--artdeco-down);
            }

            &.neutral {
              color: var(--artdeco-fg-muted);
            }

            .change-icon {
              font-size: var(--artdeco-text-xs);
            }
          }
        }

        .volume-display {
          font-family: var(--artdeco-font-mono);
          color: var(--artdeco-fg-primary);
          font-size: var(--artdeco-text-sm);
        }

        .market-cap-display {
          font-family: var(--artdeco-font-mono);
          font-weight: var(--artdeco-font-medium);
          color: var(--artdeco-fg-primary);
          font-size: var(--artdeco-text-sm);
        }
      }
    }

    // Real-time indicator
    .realtime-indicator {
      position: absolute;
      bottom: var(--artdeco-spacing-4);
      right: var(--artdeco-spacing-4);
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-3);
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
      background: rgba(10, 10, 10, 0.8);
      backdrop-filter: blur(8px);
      border-radius: var(--artdeco-radius-md);
      border: 1px solid var(--artdeco-gold-dim);

      .indicator-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--artdeco-danger);

        &.active {
          background: var(--artdeco-success);
          box-shadow: 0 0 8px rgba(39, 174, 96, 0.6);
          animation: artdeco-pulse-dot 2s ease-in-out infinite;
        }
      }

      .indicator-text {
        font-family: var(--artdeco-font-accent);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-primary);
        font-weight: var(--artdeco-font-medium);
      }

      .last-update-time {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
      }
    }
  }

  // Gainers and losers section
  .gainers-losers-section {
    margin-bottom: var(--artdeco-spacing-8);

    .gainers-losers-grid {
      gap: var(--artdeco-spacing-6);
    }

    .gainers-card,
    .losers-card {
      @include artdeco-hover-lift-glow;
      background: var(--artdeco-bg-card);
      border: 1px solid var(--artdeco-gold-dim);

      .gainers-list,
      .losers-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);

        .gainer-item,
        .loser-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--artdeco-spacing-4);
          background: rgba(212, 175, 55, 0.05);
          border-radius: var(--artdeco-radius-sm);
          cursor: pointer;
          transition: all var(--artdeco-transition-fast);

          &:hover {
            background: rgba(212, 175, 55, 0.1);
            transform: translateY(-2px);
            box-shadow: var(--artdeco-glow-subtle);
          }

          .stock-info {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-1);

            .stock-symbol {
              font-family: var(--artdeco-font-mono);
              font-weight: var(--artdeco-font-bold);
              color: var(--artdeco-gold-primary);
              font-size: var(--artdeco-text-sm);
            }

            .stock-name {
              font-family: var(--artdeco-font-body);
              color: var(--artdeco-fg-primary);
              font-size: var(--artdeco-text-sm);
            }
          }

          .stock-prices {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: var(--artdeco-spacing-1);

            .current-price {
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

            .change-amount {
              font-family: var(--artdeco-font-accent);
              font-size: var(--artdeco-text-sm);
              display: flex;
              align-items: center;
              gap: var(--artdeco-spacing-1);

              &.positive {
                color: var(--artdeco-up);
              }

              &.negative {
                color: var(--artdeco-down);
              }

              .change-icon {
                font-size: var(--artdeco-text-xs);
              }
            }
          }
        }
      }
    }
  }

  // Heatmap card
  .heatmap-card {
    @include artdeco-hover-lift-glow;
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-dim);
    margin-bottom: var(--artdeco-spacing-8);

    .heatmap-container {
      position: relative;
      height: 300px;

      .heatmap-placeholder {
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
        position: relative;

        .sector-indicators {
          position: absolute;
          top: var(--artdeco-spacing-4);
          left: var(--artdeco-spacing-4);
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: var(--artdeco-spacing-3);
          width: calc(100% - 2 * var(--artdeco-spacing-4));
          height: calc(100% - 2 * var(--artdeco-spacing-4));

          .sector-item {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: var(--artdeco-spacing-2);
            padding: var(--artdeco-spacing-3);
            border-radius: var(--artdeco-radius-sm);
            border: 1px solid var(--artdeco-gold-dim);
            transition: all var(--artdeco-transition-fast);

            &:hover {
              transform: scale(1.05);
              box-shadow: var(--artdeco-glow-subtle);
            }

            .sector-name {
              font-family: var(--artdeco-font-display);
              font-weight: var(--artdeco-font-bold);
              color: var(--artdeco-bg-global);
              font-size: var(--artdeco-text-sm);
              text-transform: uppercase;
              letter-spacing: var(--artdeco-tracking-wide);
              text-align: center;
            }

            .sector-change {
              font-family: var(--artdeco-font-mono);
              font-weight: var(--artdeco-font-bold);
              font-size: var(--artdeco-text-base);
              color: var(--artdeco-bg-global);

              &.positive {
                color: var(--artdeco-bg-global);
              }

              &.negative {
                color: var(--artdeco-bg-global);
              }

              &.neutral {
                color: var(--artdeco-bg-global);
              }
            }
          }
        }
      }
    }
  }

  // Alerts card
  .alerts-card {
    @include artdeco-hover-lift-glow;
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-dim);

    .market-alerts {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-4);

      .alert-item {
        display: flex;
        align-items: flex-start;
        gap: var(--artdeco-spacing-4);
        padding: var(--artdeco-spacing-4);
        border-radius: var(--artdeco-radius-sm);
        border-left: 4px solid;
        transition: all var(--artdeco-transition-fast);

        &.announcement {
          background: rgba(255, 215, 0, 0.1);
          border-left-color: var(--artdeco-warning);
        }

        &.price-alert {
          background: rgba(255, 82, 82, 0.1);
          border-left-color: var(--artdeco-danger);
        }

        &.volume-alert {
          background: rgba(39, 174, 96, 0.1);
          border-left-color: var(--artdeco-success);
        }

        &:hover {
          transform: translateX(4px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .alert-icon {
          width: 40px;
          height: 40px;
          background: var(--artdeco-gold-primary);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--artdeco-bg-global);
          flex-shrink: 0;

          i {
            font-size: var(--artdeco-text-lg);
          }
        }

        .alert-content {
          flex: 1;

          .alert-title {
            font-family: var(--artdeco-font-body);
            font-weight: var(--artdeco-font-semibold);
            color: var(--artdeco-fg-primary);
            margin-bottom: var(--artdeco-spacing-1);
            font-size: var(--artdeco-text-base);
          }

          .alert-message {
            font-family: var(--artdeco-font-accent);
            color: var(--artdeco-fg-muted);
            margin-bottom: var(--artdeco-spacing-1);
            font-size: var(--artdeco-text-sm);
            line-height: 1.4;
          }

          .alert-time {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-subtle);
          }
        }

        .alert-badge {
          flex-shrink: 0;
          font-size: var(--artdeco-text-xs);
          padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
        }
      }
    }
  }
}

// Art Deco animations for market quotes
@keyframes artdeco-price-flash-up {
  0% { background-color: rgba(0, 230, 118, 0.2); }
  100% { background-color: transparent; }
}

@keyframes artdeco-price-flash-down {
  0% { background-color: rgba(255, 82, 82, 0.2); }
  100% { background-color: transparent; }
}

@keyframes artdeco-pulse-dot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

// Responsive design for Art Deco market quotes
@media (max-width: 1200px) {
  .market-quotes-page {
    .overview-grid {
      grid-template-columns: 1fr 1fr;
    }

    .gainers-losers-grid {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .market-quotes-page {
    .market-status {
      justify-content: flex-start;
    }

    .overview-grid {
      grid-template-columns: 1fr;
    }

    .ticker-list-card {
      .realtime-indicator {
        position: static;
        margin-top: var(--artdeco-spacing-4);
        justify-content: center;
      }
    }

    .heatmap-card {
      .sector-indicators {
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-2);
      }
    }

    .alerts-card {
      .alert-item {
        flex-direction: column;
        text-align: center;

        .alert-icon {
          align-self: center;
        }

        .alert-content {
          text-align: center;
        }
      }
    }
  }
}
</style>