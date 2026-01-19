<template>
  <div class="dashboard-page">
    <!-- ArtDecoHeader with gold-accent variant and luxury subtitle -->
    <ArtDecoHeader
      :title="pageTitle"
      subtitle="专业量化交易数据管理系统"
      variant="gold-accent"
      class="dashboard-header"
    />

    <div class="main-content">
      <!-- Statistics Section with ArtDecoStatCard components -->
      <div class="stats-section">
        <ArtDecoGrid columns="3" responsive class="stats-grid">
          <ArtDecoStatCard
            v-for="stat in statistics"
            :key="stat.id"
            :title="stat.title"
            :value="stat.value"
            :change="stat.change"
            :changeType="stat.changeType"
            animated
            class="stat-card"
          />
        </ArtDecoGrid>
      </div>

      <!-- Main Dashboard Content with 3-column responsive layout -->
      <ArtDecoGrid columns="3" responsive class="dashboard-grid">
        <!-- Market Overview with geometric decorations -->
        <ArtDecoCard
          title="市场概览"
          variant="luxury"
          decorated
          class="market-overview-card"
        >
          <div class="market-indicators">
            <div v-for="indicator in marketIndicators" :key="indicator.symbol" class="indicator-item">
              <span class="symbol">{{ indicator.symbol }}</span>
              <span class="price" :class="indicator.trend">{{ indicator.price }}</span>
              <span class="change" :class="indicator.trend">{{ indicator.change }}</span>
            </div>
          </div>
        </ArtDecoCard>

        <!-- Data Visualization with sunburst background patterns -->
        <ArtDecoCard
          title="数据可视化"
          variant="luxury"
          decorated
          class="chart-card"
        >
          <div class="chart-container">
            <div class="chart-placeholder">
              <!-- Chart content will be rendered here -->
              <div class="sunburst-pattern"></div>
            </div>
          </div>
        </ArtDecoCard>

        <!-- Recent Activity with Art Deco styling -->
        <ArtDecoCard
          title="近期活动"
          variant="luxury"
          decorated
          class="activity-card"
        >
          <div class="activity-list">
            <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
              <div class="activity-icon">
                <i :class="activity.icon"></i>
              </div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </ArtDecoCard>

        <!-- Portfolio Performance -->
        <ArtDecoCard
          title="投资组合表现"
          variant="luxury"
          decorated
          class="portfolio-card"
        >
          <ArtDecoTable
            :data="portfolioData"
            :columns="portfolioColumns"
            gold-headers
          />
        </ArtDecoCard>

        <!-- Risk Metrics -->
        <ArtDecoCard
          title="风险指标"
          variant="luxury"
          decorated
          class="risk-card"
        >
          <div class="risk-metrics">
            <div v-for="metric in riskMetrics" :key="metric.id" class="metric-item">
              <div class="metric-label">{{ metric.label }}</div>
              <div class="metric-value" :class="metric.status">{{ metric.value }}</div>
            </div>
          </div>
        </ArtDecoCard>

        <!-- System Status -->
        <ArtDecoCard
          title="系统状态"
          variant="luxury"
          decorated
          class="status-card"
        >
          <div class="system-status">
            <div v-for="service in systemServices" :key="service.id" class="service-item">
              <div class="service-name">{{ service.name }}</div>
              <div class="service-status">
                <span class="status-dot" :class="service.status"></span>
                <span class="status-text">{{ service.statusText }}</span>
              </div>
            </div>
          </div>
        </ArtDecoCard>
      </ArtDecoGrid>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
// ArtDeco component imports
import {
  ArtDecoHeader,
  ArtDecoCard,
  ArtDecoTable,
  ArtDecoGrid,
  ArtDecoStatCard
} from '@/components/artdeco'

// Component logic
const pageTitle = ref('MYSTOCKS DASHBOARD')

// Statistics data with animated changes
const statistics = ref([
  {
    id: 'total-portfolio',
    title: '总资产',
    value: '¥2,450,000',
    change: '+5.2%',
    changeType: 'positive'
  },
  {
    id: 'daily-pnl',
    title: '日盈亏',
    value: '+¥12,340',
    change: '+2.1%',
    changeType: 'positive'
  },
  {
    id: 'win-rate',
    title: '胜率',
    value: '68.5%',
    change: '+1.3%',
    changeType: 'positive'
  }
])

// Market indicators
const marketIndicators = ref([
  { symbol: '沪指', price: '3128.45', change: '+0.85%', trend: 'positive' },
  { symbol: '深指', price: '10245.67', change: '+1.12%', trend: 'positive' },
  { symbol: '创业板', price: '2156.89', change: '-0.34%', trend: 'negative' }
])

// Recent activities
const recentActivities = ref([
  {
    id: 1,
    title: '执行买入订单',
    time: '2分钟前',
    icon: 'fas fa-shopping-cart'
  },
  {
    id: 2,
    title: '策略回测完成',
    time: '15分钟前',
    icon: 'fas fa-chart-line'
  },
  {
    id: 3,
    title: '风险警报触发',
    time: '1小时前',
    icon: 'fas fa-exclamation-triangle'
  }
])

// Portfolio data
const portfolioData = ref([
  { symbol: '000001', name: '平安银行', shares: 1000, avgPrice: 12.50, currentPrice: 13.20, pnl: '+¥700' },
  { symbol: '600000', name: '浦发银行', shares: 800, avgPrice: 8.90, currentPrice: 9.15, pnl: '+¥200' },
  { symbol: '000002', name: '万科A', shares: 500, avgPrice: 18.50, currentPrice: 17.80, pnl: '-¥350' }
])

const portfolioColumns = ref([
  { key: 'symbol', title: '代码', width: '20%' },
  { key: 'name', title: '名称', width: '25%' },
  { key: 'shares', title: '持股', width: '15%' },
  { key: 'pnl', title: '盈亏', width: '20%' }
])

// Risk metrics
const riskMetrics = ref([
  { id: 'sharpe', label: '夏普比率', value: '1.85', status: 'good' },
  { id: 'max-drawdown', label: '最大回撤', value: '-8.2%', status: 'warning' },
  { id: 'var', label: 'VaR(95%)', value: '¥45,200', status: 'neutral' }
])

// System services
const systemServices = ref([
  { id: 'market-data', name: '市场数据', status: 'online', statusText: '正常' },
  { id: 'trading-engine', name: '交易引擎', status: 'online', statusText: '正常' },
  { id: 'risk-monitor', name: '风险监控', status: 'warning', statusText: '警告' },
  { id: 'backtest-service', name: '回测服务', status: 'online', statusText: '正常' }
])

// Methods
const loadData = async () => {
  // Load dashboard data from API
  try {
    // TODO: Implement API calls for real data
    console.log('Loading dashboard data...')
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.dashboard-page {
  @include artdeco-layout;
  position: relative;
  min-height: 100vh;

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

  .dashboard-header {
    margin-bottom: var(--artdeco-spacing-8);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
    font-weight: var(--artdeco-font-bold);
  }

  .main-content {
    @include artdeco-content-spacing;
    position: relative;
  }

  // Statistics section with gold theme
  .stats-section {
    margin-bottom: var(--artdeco-spacing-12);
    position: relative;

    .stats-grid {
      gap: var(--artdeco-spacing-6);
    }

    .stat-card {
      @include artdeco-hover-lift-glow;
      background: var(--artdeco-bg-card);
      border: 1px solid var(--artdeco-border-accent);
      transition: all var(--artdeco-transition-base);
    }
  }

  // Dashboard grid with Art Deco spacing
  .dashboard-grid {
    gap: var(--artdeco-spacing-8);

    // Luxury variant cards with gold accents
    .market-overview-card,
    .chart-card,
    .activity-card,
    .portfolio-card,
    .risk-card,
    .status-card {
      @include artdeco-hover-lift-glow;
      background: var(--artdeco-bg-card);
      border: 1px solid var(--artdeco-gold-dim);
      position: relative;

      // Sunburst background pattern for chart card
      &.chart-card {
        .chart-container {
          position: relative;
          height: 300px;

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

            // Sunburst radial pattern
            .sunburst-pattern {
              position: absolute;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
              width: 200px;
              height: 200px;
              background: radial-gradient(circle,
                transparent 30%,
                rgba(212, 175, 55, 0.1) 50%,
                transparent 70%
              );
              border-radius: 50%;
              animation: artdeco-pulse 4s ease-in-out infinite;
            }
          }
        }
      }

      // Market indicators styling
      .market-indicators {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);

        .indicator-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--artdeco-spacing-3);
          background: rgba(212, 175, 55, 0.05);
          border-radius: var(--artdeco-radius-sm);

          .symbol {
            font-family: var(--artdeco-font-mono);
            font-weight: var(--artdeco-font-semibold);
            color: var(--artdeco-fg-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
          }

          .price {
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

          .change {
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

      // Activity list styling
      .activity-list {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);

        .activity-item {
          display: flex;
          align-items: center;
          gap: var(--artdeco-spacing-4);
          padding: var(--artdeco-spacing-3);
          background: rgba(212, 175, 55, 0.05);
          border-radius: var(--artdeco-radius-sm);
          transition: all var(--artdeco-transition-fast);

          &:hover {
            background: rgba(212, 175, 55, 0.1);
            transform: translateX(4px);
          }

          .activity-icon {
            width: 40px;
            height: 40px;
            background: var(--artdeco-gold-primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--artdeco-bg-global);

            i {
              font-size: var(--artdeco-text-lg);
            }
          }

          .activity-content {
            flex: 1;

            .activity-title {
              font-family: var(--artdeco-font-body);
              font-weight: var(--artdeco-font-medium);
              color: var(--artdeco-fg-primary);
              margin-bottom: var(--artdeco-spacing-1);
            }

            .activity-time {
              font-family: var(--artdeco-font-accent);
              font-size: var(--artdeco-text-sm);
              color: var(--artdeco-fg-muted);
            }
          }
        }
      }

      // Risk metrics styling
      .risk-metrics {
        display: grid;
        grid-template-columns: 1fr;
        gap: var(--artdeco-spacing-4);

        .metric-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--artdeco-spacing-4);
          background: rgba(212, 175, 55, 0.05);
          border-radius: var(--artdeco-radius-sm);

          .metric-label {
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
          }

          .metric-value {
            font-family: var(--artdeco-font-mono);
            font-weight: var(--artdeco-font-bold);
            font-size: var(--artdeco-text-lg);

            &.good {
              color: var(--artdeco-success);
            }

            &.warning {
              color: var(--artdeco-warning);
            }

            &.neutral {
              color: var(--artdeco-fg-primary);
            }
          }
        }
      }

      // System status styling
      .system-status {
        display: grid;
        grid-template-columns: 1fr;
        gap: var(--artdeco-spacing-3);

        .service-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--artdeco-spacing-3);
          background: rgba(212, 175, 55, 0.05);
          border-radius: var(--artdeco-radius-sm);

          .service-name {
            font-family: var(--artdeco-font-body);
            font-weight: var(--artdeco-font-medium);
            color: var(--artdeco-fg-primary);
          }

          .service-status {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-2);

            .status-dot {
              width: 8px;
              height: 8px;
              border-radius: 50%;

              &.online {
                background: var(--artdeco-success);
                box-shadow: 0 0 8px rgba(76, 175, 80, 0.6);
              }

              &.warning {
                background: var(--artdeco-warning);
                box-shadow: 0 0 8px rgba(255, 193, 7, 0.6);
              }

              &.offline {
                background: var(--artdeco-danger);
                box-shadow: 0 0 8px rgba(244, 67, 54, 0.6);
              }
            }

            .status-text {
              font-family: var(--artdeco-font-accent);
              font-size: var(--artdeco-text-sm);
              color: var(--artdeco-fg-muted);
            }
          }
        }
      }
    }
  }
}

// Art Deco pulse animation for decorative elements
@keyframes artdeco-pulse {
  0%, 100% {
    opacity: 0.3;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1.05);
  }
}

// Responsive design for Art Deco dashboard
@media (max-width: 1200px) {
  .dashboard-page {
    .dashboard-grid {
      grid-template-columns: 1fr 1fr;
    }
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    .stats-grid {
      grid-template-columns: 1fr;
    }

    .dashboard-grid {
      grid-template-columns: 1fr;
    }

    .dashboard-header {
      margin-bottom: var(--artdeco-spacing-6);
    }
  }
}
</style>