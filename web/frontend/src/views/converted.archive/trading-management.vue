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
                  v-for="(type, _idx) in orderTypes"
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
import { ref, computed, onMounted, onUnmounted } from 'vue'

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

const confirmOrderSubmit = async (orderData: unknown) => {
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

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.trading-management-page {
  position: relative;
  display: grid;
  grid-template-columns: calc((var(--artdeco-spacing-20) * 3) + var(--artdeco-spacing-10)) minmax(0, 1fr);
  min-height: 100%;
  background: var(--artdeco-bg-global);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: calc(var(--artdeco-spacing-px) * 2);
    background: linear-gradient(90deg, transparent, var(--artdeco-gold-primary), transparent);
  }
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
  padding: var(--artdeco-spacing-5);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc((var(--artdeco-spacing-20) * 3) + var(--artdeco-spacing-10)), 1fr));
  gap: var(--artdeco-spacing-6);
}

.trading-interface {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--artdeco-spacing-6);
}

.order-form-card {
  .card-header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .order-type-tabs {
    display: flex;
    gap: var(--artdeco-spacing-2);
  }

  .order-type-tab {
    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-4);
    background: transparent;
    border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
    border-radius: var(--artdeco-radius-none);
    color: var(--artdeco-fg-muted);
    cursor: pointer;
    font-family: var(--font-display);
    font-size: var(--artdeco-text-sm);
    font-weight: var(--artdeco-font-semibold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    transition:
      border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
      background var(--artdeco-transition-quick) var(--artdeco-ease-out),
      color var(--artdeco-transition-quick) var(--artdeco-ease-out);

    &.active {
      background: var(--artdeco-gold-primary);
      border-color: var(--artdeco-gold-primary);
      color: var(--artdeco-bg-global);
    }

    &:hover:not(.active) {
      border-color: var(--artdeco-gold-primary);
      color: var(--artdeco-gold-primary);
    }
  }

  .order-form {
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(calc((var(--artdeco-spacing-20) * 2) + var(--artdeco-spacing-10)), 1fr));
      gap: var(--artdeco-spacing-4);
      margin-bottom: var(--artdeco-spacing-6);
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-1);
    }
  }
}

.artdeco-label {
  color: var(--artdeco-gold-primary);
  font-family: var(--font-body);
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-semibold);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.order-summary {
  margin-bottom: var(--artdeco-spacing-6);
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-elevated);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 10%, transparent);
  border-radius: var(--artdeco-radius-none);

  .summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--artdeco-spacing-1);

    &:last-child {
      margin-bottom: 0;
    }
  }

  .summary-label {
    color: var(--artdeco-fg-muted);
    font-family: var(--font-body);
    font-size: var(--artdeco-text-sm);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }

  .summary-value {
    color: var(--artdeco-fg-primary);
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-base);
    font-weight: var(--artdeco-font-semibold);

    &.gold {
      color: var(--artdeco-gold-primary);
    }
  }
}

.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--artdeco-spacing-4);

  .submit-btn {
    min-width: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-20) + var(--artdeco-spacing-10));
  }
}

.orders-table-card {
  .table-actions {
    display: flex;
    gap: var(--artdeco-spacing-1);
  }
}

.risk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc((var(--artdeco-spacing-20) * 2) + var(--artdeco-spacing-10)), 1fr));
  gap: var(--artdeco-spacing-6);
}

.risk-metric {
  padding: var(--artdeco-spacing-4);
  text-align: center;
  background: var(--artdeco-bg-elevated);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 10%, transparent);
  border-radius: var(--artdeco-radius-none);

  .metric-label {
    margin-bottom: var(--artdeco-spacing-1);
    color: var(--artdeco-fg-muted);
    font-family: var(--font-body);
    font-size: var(--artdeco-text-sm);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }

  .metric-value {
    margin-bottom: var(--artdeco-spacing-1);
    font-family: var(--font-display);
    font-size: var(--artdeco-text-xl);
    font-weight: var(--artdeco-font-bold);

    &.warning { color: var(--artdeco-warning); }
    &.danger { color: var(--artdeco-down); }
    &.success { color: var(--artdeco-rise); }
    &.info { color: var(--artdeco-info); }
  }

  .metric-change {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-xs);

    &.positive { color: var(--artdeco-rise); }
    &.negative { color: var(--artdeco-down); }
    &.neutral { color: var(--artdeco-fg-muted); }
  }
}

@media (width <= calc((var(--artdeco-spacing-20) * 9) + var(--artdeco-spacing-6))) {
  .trading-management-page,
  .stats-grid,
  .risk-grid {
    grid-template-columns: 1fr;
  }

  .order-form {
    .form-grid {
      grid-template-columns: 1fr;
    }
  }

  .order-actions {
    flex-direction: column;

    .submit-btn {
      width: 100%;
    }
  }
}
</style>
