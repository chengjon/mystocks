<template>
  <div class="artdeco-trade-station">
    <!-- Account Overview -->
    <div class="artdeco-grid-3">
      <div class="artdeco-card">
        <div class="artdeco-stat-value">¥{{ formatCurrency(accountOverview.totalAssets) }}</div>
        <div class="artdeco-stat-label">总资产</div>
      </div>
      <div class="artdeco-card">
        <div class="artdeco-stat-value">¥{{ formatCurrency(accountOverview.positionValue) }}</div>
        <div class="artdeco-stat-label">持仓市值</div>
      </div>
      <div class="artdeco-card">
        <div class="artdeco-stat-value">¥{{ formatCurrency(accountOverview.availableCash) }}</div>
        <div class="artdeco-stat-label">可用资金</div>
      </div>
    </div>

    <!-- Orders & Positions -->
    <div class="artdeco-grid-2">
      <div class="artdeco-card">
        <h3>当前订单</h3>
        <table class="artdeco-table">
          <thead>
            <tr>
              <th>订单号</th>
              <th>代码</th>
              <th>类型</th>
              <th>数量</th>
              <th>价格</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.id">
              <td style="font-family: var(--artdeco-font-mono);">{{ order.id }}</td>
              <td style="font-family: var(--artdeco-font-mono);">{{ order.code }}</td>
              <td :style="{ color: order.type === '买入' ? 'var(--artdeco-rise)' : 'var(--artdeco-fall)' }">
                {{ order.type }}
              </td>
              <td style="font-family: var(--artdeco-font-mono); text-align: right;">{{ order.quantity }}</td>
              <td style="font-family: var(--artdeco-font-mono); text-align: right;">{{ order.price.toFixed(2) }}</td>
              <td>
                <span
                  class="artdeco-badge"
                  :class="order.status === 'filled' ? 'artdeco-badge-success' : order.status === 'pending' ? 'artdeco-badge-warning' : 'artdeco-badge-info'"
                >
                  {{ order.status === 'filled' ? '已成交' : order.status === 'pending' ? '待成交' : '已撤销' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="artdeco-card">
        <h3>当前持仓</h3>
        <table class="artdeco-table">
          <thead>
            <tr>
              <th>代码</th>
              <th>名称</th>
              <th>持仓</th>
              <th>成本</th>
              <th>现价</th>
              <th>盈亏</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="position in positions" :key="position.code">
              <td style="font-family: var(--artdeco-font-mono);">{{ position.code }}</td>
              <td>{{ position.name }}</td>
              <td style="font-family: var(--artdeco-font-mono); text-align: right;">{{ position.quantity }}</td>
              <td style="font-family: var(--artdeco-font-mono); text-align: right;">{{ position.cost.toFixed(2) }}</td>
              <td style="font-family: var(--artdeco-font-mono); text-align: right;">{{ position.current.toFixed(2) }}</td>
              <td
                style="font-family: var(--artdeco-font-mono); text-align: right;"
                :class="position.profit >= 0 ? 'artdeco-data-rise' : 'artdeco-data-fall'"
              >
                {{ position.profit >= 0 ? '+' : '' }}{{ position.profit.toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Trade History -->
    <div class="artdeco-card">
      <h3>成交记录</h3>
      <table class="artdeco-table">
        <thead>
          <tr>
            <th>成交时间</th>
            <th>代码</th>
            <th>名称</th>
            <th>操作</th>
            <th>数量</th>
            <th>价格</th>
            <th>金额</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trade in tradeHistory" :key="trade.time + trade.code">
            <td style="font-family: var(--artdeco-font-mono);">{{ trade.time }}</td>
            <td style="font-family: var(--artdeco-font-mono);">{{ trade.code }}</td>
            <td>{{ trade.name }}</td>
            <td :style="{ color: trade.action === '买入' ? 'var(--artdeco-rise)' : 'var(--artdeco-fall)' }">
              {{ trade.action }}
            </td>
            <td style="font-family: var(--artdeco-font-mono); text-align: right;">{{ trade.quantity }}</td>
            <td style="font-family: var(--artdeco-font-mono); text-align: right;">{{ trade.price.toFixed(2) }}</td>
            <td style="font-family: var(--artdeco-font-mono); text-align: right;">{{ trade.amount.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

// Types
interface AccountOverview {
  totalAssets: number
  positionValue: number
  availableCash: number
}

interface Order {
  id: string
  code: string
  type: '买入' | '卖出'
  quantity: number
  price: number
  status: 'pending' | 'filled' | 'cancelled'
}

interface Position {
  code: string
  name: string
  quantity: number
  cost: number
  current: number
  profit: number
}

interface TradeHistory {
  time: string
  code: string
  name: string
  action: '买入' | '卖出'
  quantity: number
  price: number
  amount: number
}

// State
const accountOverview = ref<AccountOverview>({
  totalAssets: 1234567.89,
  positionValue: 856789.12,
  availableCash: 377778.77
})

const orders = ref<Order[]>([
  { id: 'ORD20240115001', code: '600519.SH', type: '买入', quantity: 100, price: 1678.50, status: 'pending' },
  { id: 'ORD20240115002', code: '000858.SZ', type: '卖出', quantity: 500, price: 156.78, status: 'filled' },
  { id: 'ORD20240115003', code: '600036.SH', type: '买入', quantity: 2000, price: 32.45, status: 'cancelled' }
])

const positions = ref<Position[]>([
  { code: '600519.SH', name: '贵州茅台', quantity: 500, cost: 1650.00, current: 1678.50, profit: 14250.00 },
  { code: '000858.SZ', name: '五粮液', quantity: 2000, cost: 158.00, current: 156.78, profit: -2440.00 },
  { code: '600036.SH', name: '招商银行', quantity: 10000, cost: 31.50, current: 32.45, profit: 9500.00 }
])

const tradeHistory = ref<TradeHistory[]>([
  { time: '2024-01-15 09:32:15', code: '600519.SH', name: '贵州茅台', action: '买入', quantity: 100, price: 1678.50, amount: 167850.00 },
  { time: '2024-01-15 10:15:32', code: '000858.SZ', name: '五粮液', action: '卖出', quantity: 500, price: 156.78, amount: 78390.00 },
  { time: '2024-01-15 13:45:08', code: '600036.SH', name: '招商银行', action: '买入', quantity: 2000, price: 32.45, amount: 64900.00 },
  { time: '2024-01-15 14:20:45', code: '000001.SZ', name: '平安银行', action: '买入', quantity: 5000, price: 12.34, amount: 61700.00 }
])

// Methods
function formatCurrency(value: number): string {
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// API Integration (for future use)
async function fetchOrders() {
  try {
    // const response = await axios.get('/api/v1/trade/orders')
    // orders.value = response.data
  } catch (error) {
    console.error('Failed to fetch orders:', error)
  }
}

async function fetchPositions() {
  try {
    // const response = await axios.get('/api/v1/trade/positions')
    // positions.value = response.data
  } catch (error) {
    console.error('Failed to fetch positions:', error)
  }
}

async function fetchTradeHistory() {
  try {
    // const response = await axios.get('/api/v1/trade/history')
    // tradeHistory.value = response.data
  } catch (error) {
    console.error('Failed to fetch trade history:', error)
  }
}

// Initialize data on mount
fetchOrders()
fetchPositions()
fetchTradeHistory()
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-trade-station {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-lg);
}

.artdeco-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-space-lg);
}

.artdeco-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--artdeco-space-lg);
}

.artdeco-card {
  background: var(--artdeco-bg-card);
  border: 2px solid var(--artdeco-gold-primary);
  padding: var(--artdeco-space-lg);
  position: relative;
}

.artdeco-card::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 1px solid rgba(212, 175, 55, 0.3);
  pointer-events: none;
}

.artdeco-card h3 {
  font-family: var(--artdeco-font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-space-md);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.artdeco-stat-value {
  font-size: 2rem;
  font-family: var(--artdeco-font-mono);
  font-weight: 700;
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-space-xs);
}

.artdeco-stat-label {
  font-size: 0.875rem;
  color: var(--artdeco-silver-dim);
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
}

.artdeco-table th {
  background: var(--artdeco-bg-header);
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-display);
  font-weight: 600;
  text-align: left;
  padding: 12px var(--artdeco-space-md);
  border-bottom: 2px solid var(--artdeco-gold-primary);
}

.artdeco-table td {
  padding: 12px var(--artdeco-space-md);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  color: var(--artdeco-silver-text);
}

.artdeco-table tr:hover td {
  background: var(--artdeco-bg-hover);
}

.artdeco-badge {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 2px;
}

.artdeco-badge-success {
  background: var(--artdeco-rise);
  color: white;
}

.artdeco-badge-warning {
  background: var(--artdeco-warning);
  color: white;
}

.artdeco-badge-info {
  background: var(--artdeco-info);
  color: white;
}

.artdeco-data-rise {
  color: var(--artdeco-rise);
}

.artdeco-data-fall {
  color: var(--artdeco-fall);
}

@media (max-width: 1440px) {
  .artdeco-grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .artdeco-grid-2,
  .artdeco-grid-3 {
    grid-template-columns: 1fr;
  }
}
</style>
