<template>
  <div class="trade-history-tab">
    <div class="filter-bar">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">TYPE</label>
          <select v-model="tradeFilter.type" class="select">
            <option value="">ALL</option>
            <option value="buy">BUY</option>
            <option value="sell">SELL</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">SYMBOL</label>
          <input v-model="tradeFilter.symbol" type="text" placeholder="SYMBOL" class="input" />
        </div>

        <div class="filter-group">
          <label class="filter-label">DATE RANGE</label>
          <div class="date-range-inputs">
            <input type="date" v-model="dateStart" class="input" />
            <span class="date-separator">TO</span>
            <input type="date" v-model="dateEnd" class="input" />
          </div>
        </div>

        <div class="filter-actions">
          <button class="btn btn-primary" @click="handleSearch">
            SEARCH
          </button>
          <button class="btn" @click="handleReset">
            RESET
          </button>
        </div>
      </div>
    </div>

    <div class="table-container">
      <table class="table" v-loading="loading">
        <thead>
          <tr>
            <th>TRADE TIME</th>
            <th>TYPE</th>
            <th>CODE</th>
            <th>NAME</th>
            <th>QUANTITY</th>
            <th>PRICE</th>
            <th>AMOUNT</th>
            <th>COMMISSION</th>
            <th>STATUS</th>
            <th>REMARK</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trade in trades" :key="trade.trade_time + trade.symbol">
            <td class="time-cell">{{ trade.trade_time }}</td>
            <td>
              <span class="badge" :class="trade.type === 'buy' ? 'badge-rise' : 'badge-fall'">
                {{ trade.type === 'buy' ? 'BUY' : 'SELL' }}
              </span>
            </td>
            <td class="code-cell">{{ trade.symbol }}</td>
            <td>{{ trade.stock_name }}</td>
            <td class="number-cell">{{ trade.quantity.toLocaleString() }}</td>
            <td class="price-cell">¥{{ trade.price.toFixed(2) }}</td>
            <td class="amount-cell">¥{{ (trade.quantity * trade.price).toFixed(2) }}</td>
            <td class="commission-cell">¥{{ trade.commission.toFixed(2) }}</td>
            <td>
              <span class="badge" :class="getStatusBadgeClass(trade.status)">
                {{ getStatusText(trade.status) }}
              </span>
            </td>
            <td class="remark-cell">{{ trade.remark || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination-container">
      <div class="pagination-info">
        TOTAL: {{ pagination.total }} RECORDS
      </div>
      <div class="pagination-controls">
        <button
          class="pagination-btn"
          :disabled="pagination.page <= 1"
          @click="goToPage(pagination.page - 1)"
        >
          PREV
        </button>
        <span class="page-number">PAGE {{ pagination.page }} / {{ totalPages }}</span>
        <button
          class="pagination-btn"
          :disabled="pagination.page >= totalPages"
          @click="goToPage(pagination.page + 1)"
        >
          NEXT
        </button>
        <select v-model="pagination.pageSize" class="select-small" @change="handleSearch">
          <option :value="20">20 / PAGE</option>
          <option :value="50">50 / PAGE</option>
          <option :value="100">100 / PAGE</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { tradeApi } from '@/api/trade'

interface TradeFilter {
  type: string
  symbol: string
  dateRange: string[]
}

interface Pagination {
  page: number
  pageSize: number
  total: number
}

const loading = ref(false)
const trades = ref<any[]>([])
const dateStart = ref('')
const dateEnd = ref('')

const tradeFilter = reactive<TradeFilter>({
  type: '',
  symbol: '',
  dateRange: []
})

const pagination = reactive<Pagination>({
  page: 1,
  pageSize: 20,
  total: 0
})

const totalPages = computed(() => Math.ceil(pagination.total / pagination.pageSize))

const loadTrades = async () => {
  loading.value = true
  try {
    tradeFilter.dateRange = []
    if (dateStart.value) tradeFilter.dateRange.push(dateStart.value)
    if (dateEnd.value) tradeFilter.dateRange.push(dateEnd.value)

    const params = {
      symbol: tradeFilter.symbol || undefined,
      side: tradeFilter.type || undefined,
      limit: pagination.pageSize
    }

    Object.keys(params).forEach((key) => {
      if (params[key as keyof typeof params] === undefined) {
        delete params[key as keyof typeof params]
      }
    })

    const data = await tradeApi.getTradeHistory(params)
    trades.value = data
    pagination.total = data.length
  } catch (error) {
    console.error('Load failed:', error)
    ElMessage.error('FAILED TO LOAD TRADE HISTORY')
    trades.value = [
      {
        trade_time: '2025-12-30 10:30:00',
        type: 'buy',
        symbol: '000001',
        stock_name: 'PING AN BANK',
        quantity: 1000,
        price: 12.50,
        commission: 5.0,
        status: 'completed',
        remark: 'NORMAL BUY'
      },
      {
        trade_time: '2025-12-29 14:20:00',
        type: 'buy',
        symbol: '000002',
        stock_name: 'VANKA A',
        quantity: 500,
        price: 25.80,
        commission: 5.0,
        status: 'completed',
        remark: 'NORMAL BUY'
      }
    ]
    pagination.total = trades.value.length
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  pagination.page = 1
  await loadTrades()
}

const handleReset = () => {
  tradeFilter.type = ''
  tradeFilter.symbol = ''
  tradeFilter.dateRange = []
  dateStart.value = ''
  dateEnd.value = ''
  pagination.page = 1
  loadTrades()
}

const goToPage = (page: number) => {
  pagination.page = page
  loadTrades()
}

const getStatusBadgeClass = (status: string) => {
  const classes: Record<string, string> = {
    pending: 'badge-warning',
    completed: 'badge-success',
    failed: 'badge-danger',
    cancelled: 'badge-info'
  }
  return classes[status] || 'badge-info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: 'PENDING',
    completed: 'COMPLETED',
    failed: 'FAILED',
    cancelled: 'CANCELLED'
  }
  return texts[status] || status
}

onMounted(() => {
  loadTrades()
})
</script>

<style scoped lang="scss">

.trade-history-tab {
  width: 100%;
}

.filter-bar {
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-5);
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-4);
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.filter-label {
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  color: var(--fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
}

.date-range-inputs {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.date-separator {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--fg-muted);
}

.filter-actions {
  display: flex;
  gap: var(--spacing-2);
  margin-left: auto;
}

.input {
  padding: var(--spacing-2) var(--spacing-3);
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--fg-primary);
  background: transparent;
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 0;
  min-width: 150px;

  &:focus {
    outline: none;
    border-color: var(--accent-gold);
    box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.1);
  }

  &::placeholder {
    color: var(--fg-muted);
  }
}

[type="date"] {
  font-family: var(--font-body);
  color: var(--fg-primary);
  background: transparent;
}

.select {
  padding: var(--spacing-2) var(--spacing-3);
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--fg-primary);
  background: transparent;
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 0;
  min-width: 120px;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: var(--accent-gold);
  }

  option {
    background: var(--bg-primary);
    color: var(--fg-primary);
  }
}

.select-small {
  padding: var(--spacing-1) var(--spacing-2);
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  color: var(--fg-primary);
  background: transparent;
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 0;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: var(--accent-gold);
  }
}

.table-container {
  overflow-x: auto;
  border: 1px solid rgba(212, 175, 55, 0.3);
  background: rgba(212, 175, 55, 0.02);
}

.table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;

  th {
    background: rgba(212, 175, 55, 0.1);
    color: var(--accent-gold);
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 2px solid var(--accent-gold);
    text-align: left;
    white-space: nowrap;
  }

  td {
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    color: var(--fg-secondary);
    font-size: var(--font-size-small);
  }

  tbody tr {
    transition: background var(--transition-base);

    &:hover {
      background: rgba(212, 175, 55, 0.05);
    }
  }

  .time-cell {
    font-family: var(--font-mono);
    font-size: var(--font-size-xs);
    white-space: nowrap;
  }

  .code-cell {
    font-family: var(--font-mono);
    color: var(--accent-gold);
  }

  .number-cell,
  .price-cell,
  .amount-cell,
  .commission-cell {
    font-family: var(--font-mono);
    text-align: right;
  }

  .price-cell {
    color: var(--fg-primary);
  }

  .amount-cell {
    color: var(--accent-gold);
  }

  .remark-cell {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-5);
  padding: var(--spacing-4);
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.pagination-info {
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  color: var(--fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.page-number {
  font-family: var(--font-mono);
  font-size: var(--font-size-small);
  color: var(--fg-primary);
}

  padding: var(--spacing-2) var(--spacing-4);
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 0;
  background: transparent;
  color: var(--accent-gold);
  cursor: pointer;
  transition: all var(--transition-base);

  &:hover:not(:disabled) {
    background: rgba(212, 175, 55, 0.1);
    border-color: var(--accent-gold);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.active {
    background: var(--accent-gold);
    color: var(--bg-primary);
    border-color: var(--accent-gold);
  }
}

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-5);
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border: 2px solid var(--accent-gold);
  border-radius: 0;
  cursor: pointer;
  transition: all var(--transition-base);

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

  background: var(--accent-gold);
  color: var(--bg-primary);

  &:hover:not(:disabled) {
    background: var(--accent-gold-light);
    box-shadow: var(--glow-medium);
  }
}

  background: transparent;
  color: var(--accent-gold);

  &:hover:not(:disabled) {
    background: rgba(212, 175, 55, 0.1);
    box-shadow: var(--glow-subtle);
  }
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border-radius: 0;
}

.badge-rise {
  background: rgba(255, 82, 82, 0.15);
  color: var(--color-up);
  border: 1px solid var(--color-up);
}

.badge-fall {
  background: rgba(0, 230, 118, 0.15);
  color: var(--color-down);
  border: 1px solid var(--color-down);
}

.badge-success {
  background: rgba(39, 174, 96, 0.15);
  color: #27AE60;
  border: 1px solid #27AE60;
}

.badge-warning {
  background: rgba(230, 126, 34, 0.15);
  color: #E67E22;
  border: 1px solid #E67E22;
}

.badge-danger {
  background: rgba(231, 76, 60, 0.15);
  color: #E74C3C;
  border: 1px solid #E74C3C;
}

.badge-info {
  background: rgba(74, 144, 226, 0.15);
  color: #4A90E2;
  border: 1px solid #4A90E2;
}
</style>
