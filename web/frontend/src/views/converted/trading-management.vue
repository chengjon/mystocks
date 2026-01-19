<template>
  <div class="trading-management-page">
    <!-- Art Deco Sidebar -->
    <ArtDecoSidebar :menu="menuItems" />

    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Art Deco Header -->
      <ArtDecoHeader
        title="TRADING MANAGEMENT"
        subtitle="ORDER EXECUTION & RISK MONITORING"
        :show-breadcrumb="true"
        :breadcrumb-items="breadcrumbItems"
      />

      <!-- Quick Stats Cards -->
      <div class="stats-grid">
        <ArtDecoStatCard
          title="TOTAL ORDERS"
          :value="stats.totalOrders"
          icon="📊"
          color="gold"
          description="24H VOLUME"
        />
        <ArtDecoStatCard
          title="EXECUTED"
          :value="stats.executedOrders"
          icon="✅"
          color="success"
          description="SUCCESS RATE"
          :percentage="stats.successRate"
        />
        <ArtDecoStatCard
          title="PENDING"
          :value="stats.pendingOrders"
          icon="⏳"
          color="warning"
          description="WAITING EXECUTION"
        />
        <ArtDecoStatCard
          title="RISK LEVEL"
          :value="stats.riskLevel"
          icon="⚠️"
          :color="stats.riskColor"
          description="CURRENT EXPOSURE"
        />
      </div>

      <!-- Main Trading Interface -->
      <div class="trading-interface">
        <!-- Order Form Section -->
        <ArtDecoCard class="order-form-card" title="TRADE EXECUTION" :decorated="true">
          <template #header>
            <div class="card-header-content">
              <span>NEW ORDER</span>
              <div class="order-type-tabs">
                <button
                  v-for="type in orderTypes"
                  :key="type.key"
                  class="order-type-tab"
                  :class="{ active: activeOrderType === type.key }"
                  @click="activeOrderType = type.key"
                >
                  {{ type.label }}
                </button>
              </div>
            </div>
          </template>

          <!-- Order Form -->
          <div class="order-form">
            <div class="form-grid">
              <div class="form-group">
                <label class="artdeco-label">SYMBOL</label>
                <ArtDecoInput
                  v-model="orderForm.symbol"
                  placeholder="E.G: 600519"
                  @input="handleSymbolChange"
                />
              </div>

              <div class="form-group">
                <label class="artdeco-label">QUANTITY</label>
                <ArtDecoInput
                  v-model.number="orderForm.quantity"
                  type="number"
                  :min="100"
                  :step="100"
                  placeholder="MIN 100"
                />
              </div>

              <div class="form-group">
                <label class="artdeco-label">PRICE TYPE</label>
                <ArtDecoSelect
                  v-model="orderForm.priceType"
                  :options="priceTypes"
                />
              </div>

              <div class="form-group" v-if="orderForm.priceType === 'limit'">
                <label class="artdeco-label">LIMIT PRICE</label>
                <ArtDecoInput
                  v-model.number="orderForm.price"
                  type="number"
                  step="0.01"
                  :min="0.01"
                  placeholder="ENTER PRICE"
                />
              </div>
            </div>

            <!-- Order Summary -->
            <div class="order-summary">
              <div class="summary-row">
                <span class="summary-label">ESTIMATED VALUE:</span>
                <span class="summary-value gold">¥{{ estimatedValue.toFixed(2) }}</span>
              </div>
              <div class="summary-row">
                <span class="summary-label">AVAILABLE CASH:</span>
                <span class="summary-value">¥{{ availableCash.toFixed(2) }}</span>
              </div>
              <div class="summary-row">
                <span class="summary-label">RISK CHECK:</span>
                <ArtDecoBadge
                  :text="riskCheckStatus.text"
                  :variant="riskCheckStatus.variant"
                  size="sm"
                />
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="order-actions">
              <ArtDecoButton
                variant="secondary"
                @click="resetOrderForm"
                :disabled="submitting"
              >
                RESET
              </ArtDecoButton>

              <ArtDecoButton
                :variant="activeOrderType === 'buy' ? 'rise' : 'fall'"
                @click="submitOrder"
                :disabled="!isOrderValid || submitting"
                :loading="submitting"
                class="submit-btn"
              >
                {{ activeOrderType === 'buy' ? 'BUY ORDER' : 'SELL ORDER' }}
              </ArtDecoButton>
            </div>
          </div>
        </ArtDecoCard>

        <!-- Current Orders Table -->
        <ArtDecoCard class="orders-table-card" title="ACTIVE ORDERS" :decorated="true">
          <ArtDecoTable
            :columns="orderColumns"
            :data="activeOrders"
            :loading="loading"
            :actions="orderActions"
            striped
            hover
          >
            <template #status="{ row }">
              <ArtDecoBadge
                :text="row.status"
                :variant="getStatusVariant(row.status)"
                size="sm"
              />
            </template>

            <template #actions="{ row }">
              <div class="table-actions">
                <ArtDecoButton
                  size="sm"
                  variant="secondary"
                  @click="cancelOrder(row)"
                  v-if="row.status === 'pending'"
                >
                  CANCEL
                </ArtDecoButton>
                <ArtDecoButton
                  size="sm"
                  variant="primary"
                  @click="viewOrderDetail(row)"
                >
                  DETAIL
                </ArtDecoButton>
              </div>
            </template>
          </ArtDecoTable>
        </ArtDecoCard>
      </div>

      <!-- Risk Monitoring Section -->
      <div class="risk-monitoring">
        <ArtDecoCard class="risk-card" title="RISK METRICS" :decorated="true">
          <div class="risk-grid">
            <div class="risk-metric">
              <div class="metric-label">PORTFOLIO VaR (95%)</div>
              <div class="metric-value warning">{{ riskMetrics.var }}%</div>
              <div class="metric-change negative">{{ riskMetrics.varChange }}</div>
            </div>

            <div class="risk-metric">
              <div class="metric-label">MAX DRAWDOWN</div>
              <div class="metric-value danger">{{ riskMetrics.maxDrawdown }}%</div>
              <div class="metric-change neutral">{{ riskMetrics.drawdownChange }}</div>
            </div>

            <div class="risk-metric">
              <div class="metric-label">SHARPE RATIO</div>
              <div class="metric-value success">{{ riskMetrics.sharpeRatio }}</div>
              <div class="metric-change positive">{{ riskMetrics.sharpeChange }}</div>
            </div>

            <div class="risk-metric">
              <div class="metric-label">BETA EXPOSURE</div>
              <div class="metric-value info">{{ riskMetrics.beta }}</div>
              <div class="metric-change neutral">{{ riskMetrics.betaChange }}</div>
            </div>
          </div>
        </ArtDecoCard>
      </div>
    </div>

    <!-- Trade Confirmation Modal -->
    <ArtDecoTradeForm
      v-model:visible="tradeFormVisible"
      :trade-type="activeOrderType"
      :symbol="orderForm.symbol"
      :quantity="orderForm.quantity"
      :price="orderForm.price"
      :max-quantity="maxAvailableQuantity"
      :price-placeholder="pricePlaceholder"
      :disabled="!isOrderValid"
      :submitting="submitting"
      @submit="confirmOrderSubmit"
      @cancel="tradeFormVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

// ArtDeco Components
import {
  ArtDecoHeader,
  ArtDecoCard,
  ArtDecoStatCard,
  ArtDecoTable,
  ArtDecoInput,
  ArtDecoSelect,
  ArtDecoButton,
  ArtDecoBadge,
  ArtDecoSidebar,
  ArtDecoTradeForm
} from '@/components/artdeco'

// Types
interface OrderForm {
  symbol: string
  quantity: number
  price: number
  priceType: string
}

interface Order {
  id: string
  symbol: string
  type: 'buy' | 'sell'
  quantity: number
  price: number
  status: 'pending' | 'executed' | 'cancelled' | 'failed'
  timestamp: string
}

// Reactive Data
const pageTitle = ref('交易管理 - MyStocks 量化交易平台')

// Sidebar Menu
const menuItems = ref([
  { label: 'TRADE EXECUTION', icon: '📈', path: '/trading', active: true },
  { label: 'ORDER HISTORY', icon: '📋', path: '/trading/history' },
  { label: 'PORTFOLIO', icon: '💼', path: '/trading/portfolio' },
  { label: 'RISK MANAGEMENT', icon: '⚠️', path: '/trading/risk' }
])

// Breadcrumb
const breadcrumbItems = ref([
  { label: 'DASHBOARD', path: '/' },
  { label: 'TRADING', path: '/trading' },
  { label: 'MANAGEMENT', active: true }
])

// Statistics
const stats = ref({
  totalOrders: 156,
  executedOrders: 142,
  pendingOrders: 14,
  successRate: 91.0,
  riskLevel: 'MEDIUM',
  riskColor: 'warning'
})

// Order Form
const activeOrderType = ref<'buy' | 'sell'>('buy')
const orderForm = ref<OrderForm>({
  symbol: '',
  quantity: 100,
  price: 0,
  priceType: 'market'
})

const orderTypes = [
  { key: 'buy', label: 'BUY' },
  { key: 'sell', label: 'SELL' }
]

const priceTypes = [
  { label: 'MARKET PRICE', value: 'market' },
  { label: 'LIMIT ORDER', value: 'limit' }
]

// Trading Data
const availableCash = ref(50000)
const currentPrice = ref(0)
const maxAvailableQuantity = ref(0)
const tradeFormVisible = ref(false)
const submitting = ref(false)
const loading = ref(false)

// Active Orders
const activeOrders = ref<Order[]>([
  {
    id: 'ORD001',
    symbol: '600519',
    type: 'buy',
    quantity: 100,
    price: 125.50,
    status: 'pending',
    timestamp: '2024-01-20 14:30:00'
  },
  {
    id: 'ORD002',
    symbol: '000001',
    type: 'sell',
    quantity: 200,
    price: 18.30,
    status: 'executed',
    timestamp: '2024-01-20 13:45:00'
  }
])

// Risk Metrics
const riskMetrics = ref({
  var: '12.5',
  varChange: '-2.1%',
  maxDrawdown: '8.3',
  drawdownChange: '0.0%',
  sharpeRatio: '1.85',
  sharpeChange: '+0.15',
  beta: '0.92',
  betaChange: '-0.02'
})

// Table Columns
const orderColumns = [
  { key: 'symbol', label: 'SYMBOL', sortable: true },
  { key: 'type', label: 'TYPE', sortable: true },
  { key: 'quantity', label: 'QUANTITY', align: 'right' },
  { key: 'price', label: 'PRICE', align: 'right', format: 'currency' },
  { key: 'status', label: 'STATUS', slot: 'status' },
  { key: 'timestamp', label: 'TIME', sortable: true },
  { key: 'actions', label: 'ACTIONS', slot: 'actions', width: 150 }
]

// Computed Properties
const estimatedValue = computed(() => {
  const price = orderForm.value.priceType === 'market' ? currentPrice.value : orderForm.value.price
  return orderForm.value.quantity * price
})

const isOrderValid = computed(() => {
  return orderForm.value.symbol.trim() !== '' &&
         orderForm.value.quantity >= 100 &&
         (orderForm.value.priceType === 'market' || orderForm.value.price > 0) &&
         estimatedValue.value <= availableCash.value
})

const riskCheckStatus = computed(() => {
  if (estimatedValue.value > availableCash.value * 0.8) {
    return { text: 'HIGH RISK', variant: 'danger' }
  } else if (estimatedValue.value > availableCash.value * 0.5) {
    return { text: 'MEDIUM RISK', variant: 'warning' }
  } else {
    return { text: 'LOW RISK', variant: 'success' }
  }
})

const pricePlaceholder = computed(() => {
  return orderForm.value.priceType === 'market' ? 'MARKET PRICE' : 'ENTER LIMIT PRICE'
})

// Table Actions
const orderActions = [
  {
    label: 'Cancel',
    action: 'cancel',
    variant: 'danger',
    condition: (row: Order) => row.status === 'pending'
  },
  {
    label: 'Detail',
    action: 'detail',
    variant: 'primary'
  }
]

// Methods
const handleSymbolChange = async () => {
  if (orderForm.value.symbol.length === 6) {
    // Simulate API call to get current price and max quantity
    currentPrice.value = Math.random() * 200 + 10
    maxAvailableQuantity.value = activeOrderType.value === 'sell' ? 1000 : Math.floor(availableCash.value / currentPrice.value / 100) * 100

    if (orderForm.value.priceType === 'market') {
      orderForm.value.price = currentPrice.value
    }
  }
}

const resetOrderForm = () => {
  orderForm.value = {
    symbol: '',
    quantity: 100,
    price: 0,
    priceType: 'market'
  }
  currentPrice.value = 0
  maxAvailableQuantity.value = 0
}

const submitOrder = () => {
  if (!isOrderValid.value) return
  tradeFormVisible.value = true
}

const confirmOrderSubmit = async (orderData: any) => {
  submitting.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Add to active orders
    const newOrder: Order = {
      id: `ORD${Date.now()}`,
      symbol: orderData.symbol,
      type: orderData.type,
      quantity: orderData.quantity,
      price: orderData.price,
      status: 'pending',
      timestamp: new Date().toISOString().slice(0, 19).replace('T', ' ')
    }

    activeOrders.value.unshift(newOrder)

    // Update stats
    stats.value.totalOrders++
    stats.value.pendingOrders++

    // Reset form
    resetOrderForm()
    tradeFormVisible.value = false

  } finally {
    submitting.value = false
  }
}

const cancelOrder = async (order: Order) => {
  order.status = 'cancelled'
  stats.value.pendingOrders--
}

const viewOrderDetail = (order: Order) => {
  console.log('View order detail:', order)
}

const getStatusVariant = (status: string) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'executed': return 'success'
    case 'cancelled': return 'secondary'
    case 'failed': return 'danger'
    default: return 'secondary'
  }
}

// Lifecycle
onMounted(() => {
  // Initial data loading would go here
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.trading-management-page {
  @include artdeco-layout;

  .main-content {
    @include artdeco-content-spacing;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--artdeco-spacing-lg);
    margin-bottom: var(--artdeco-spacing-xl);
  }

  .trading-interface {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--artdeco-spacing-xl);
    margin-bottom: var(--artdeco-spacing-xl);
  }

  .order-form-card {
    .card-header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;

      .order-type-tabs {
        display: flex;
        gap: var(--artdeco-spacing-sm);

        .order-type-tab {
          padding: var(--artdeco-spacing-xs) var(--artdeco-spacing-md);
          background: transparent;
          border: 1px solid rgba(212, 175, 55, 0.2);
          color: var(--artdeco-fg-muted);
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-font-size-sm);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          cursor: pointer;
          transition: all var(--artdeco-transition-base);
          border-radius: 4px;

          &.active {
            background: var(--artdeco-accent-gold);
            color: var(--artdeco-bg-primary);
            border-color: var(--artdeco-accent-gold);
          }

          &:hover:not(.active) {
            border-color: var(--artdeco-accent-gold);
            color: var(--artdeco-accent-gold);
          }
        }
      }
    }

    .order-form {
      .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--artdeco-spacing-md);
        margin-bottom: var(--artdeco-spacing-lg);
      }

      .form-group {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-xs);
      }

      .artdeco-label {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-font-size-sm);
        font-weight: 600;
        color: var(--artdeco-accent-gold);
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .order-summary {
        background: var(--artdeco-bg-elevated);
        border: 1px solid rgba(212, 175, 55, 0.1);
        padding: var(--artdeco-spacing-md);
        border-radius: 4px;
        margin-bottom: var(--artdeco-spacing-lg);

        .summary-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--artdeco-spacing-xs);

          &:last-child {
            margin-bottom: 0;
          }

          .summary-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-font-size-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }

          .summary-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-font-size-base);
            font-weight: 600;
            color: var(--artdeco-fg-secondary);

            &.gold {
              color: var(--artdeco-accent-gold);
            }
          }
        }
      }

      .order-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--artdeco-spacing-md);

        .submit-btn {
          min-width: 140px;
        }
      }
    }
  }

  .orders-table-card {
    .table-actions {
      display: flex;
      gap: var(--artdeco-spacing-xs);
    }
  }

  .risk-monitoring {
    .risk-card {
      .risk-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--artdeco-spacing-lg);
      }

      .risk-metric {
        text-align: center;
        padding: var(--artdeco-spacing-md);
        background: var(--artdeco-bg-elevated);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: 4px;

        .metric-label {
          font-family: var(--artdeco-font-body);
          font-size: var(--artdeco-font-size-sm);
          color: var(--artdeco-fg-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: var(--artdeco-spacing-xs);
        }

        .metric-value {
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-font-size-xl);
          font-weight: 700;
          margin-bottom: var(--artdeco-spacing-xs);

          &.warning { color: var(--artdeco-warning); }
          &.danger { color: var(--artdeco-danger); }
          &.success { color: var(--artdeco-success); }
          &.info { color: var(--artdeco-info); }
        }

        .metric-change {
          font-family: var(--artdeco-font-mono);
          font-size: var(--artdeco-font-size-xs);

          &.positive { color: var(--artdeco-rise); }
          &.negative { color: var(--artdeco-fall); }
          &.neutral { color: var(--artdeco-fg-muted); }
        }
      }
    }
  }

  @media (max-width: 768px) {
    .stats-grid {
      grid-template-columns: 1fr;
    }

    .form-grid {
      grid-template-columns: 1fr !important;
    }

    .risk-grid {
      grid-template-columns: 1fr !important;
    }

    .order-actions {
      flex-direction: column;

      .submit-btn {
        width: 100%;
      }
    }
  }
    justify-content: center;
    color: var(--fg-muted);
  }
  
  // ArtDeco decorative elements
  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
  }
}
</style>