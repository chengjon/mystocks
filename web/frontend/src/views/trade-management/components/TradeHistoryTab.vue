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

interface TradeRecord {
  trade_time: string
  type: 'buy' | 'sell'
  symbol: string
  stock_name: string
  quantity: number
  price: number
  commission: number
  status: 'pending' | 'completed' | 'failed' | 'cancelled'
  remark?: string
}

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
const trades = ref<TradeRecord[]>([])
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

    // TODO: Transform TradeHistoryVM to TradeRecord format when API is ready
    // For now, the API returns a different structure, so we use mock data
    const _apiData = await tradeApi.getTradeHistory(params)
    // Transform API data to component format (API returns grouped by date)
    // Using mock data until API response format is aligned
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

// Expose methods to parent component
defineExpose({
  loadTrades
})
</script>

<style scoped lang="scss">
@use "./styles/TradeHistoryTab.scss" as *;
</style>
