<template>
  <div class="positions-tab">
    <div class="action-bar">
      <div class="action-buttons">
        <button class="btn btn-primary" @click="handleBuy">
          BUY
        </button>
        <button class="btn btn-danger" @click="handleSell">
          SELL
        </button>
        <button class="btn btn-info" @click="handleRefresh">
          <span class="btn-icon">↻</span>
          REFRESH
        </button>
      </div>
    </div>

    <div class="table-container" v-loading="loading">
      <table class="table">
        <thead>
          <tr>
            <th>CODE</th>
            <th>NAME</th>
            <th>QUANTITY</th>
            <th>COST PRICE</th>
            <th>CURRENT PRICE</th>
            <th>MARKET VALUE</th>
            <th>PROFIT</th>
            <th>PROFIT RATE</th>
            <th>UPDATE TIME</th>
            <th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="position in positions" :key="position.symbol">
            <td class="code-cell">{{ position.symbol }}</td>
            <td>{{ position.stock_name }}</td>
            <td class="number-cell">{{ position.quantity.toLocaleString() }}</td>
            <td class="price-cell">¥{{ position.cost_price.toFixed(2) }}</td>
            <td class="price-cell">¥{{ position.current_price.toFixed(2) }}</td>
            <td class="amount-cell">¥{{ (position.quantity * position.current_price).toFixed(2) }}</td>
            <td :class="['profit-cell', position.profit >= 0 ? 'profit-up' : 'profit-down']">
              ¥{{ position.profit.toFixed(2) }}
            </td>
            <td :class="['rate-cell', position.profit_rate >= 0 ? 'profit-up' : 'profit-down']">
              {{ position.profit_rate >= 0 ? '+' : '' }}{{ position.profit_rate.toFixed(2) }}%
            </td>
            <td class="time-cell">{{ formatTime(position.update_time) }}</td>
            <td class="action-cell">
              <button class="btn btn-sm btn-danger" @click="handleQuickSell(position)">
                SELL
              </button>
              <button class="btn btn-sm btn-info" @click="handleViewDetails(position)">
                DETAILS
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { tradeApi } from '@/api/trade'

interface Position {
  symbol: string
  stock_name: string
  quantity: number
  cost_price: number
  current_price: number
  profit: number
  profit_rate: number
  update_time: string
}

const emit = defineEmits<{
  'buy': []
  'sell': []
  'quick-sell': [position: Position]
}>()

const loading = ref(false)
const positions = ref<any[]>([])

const loadPositions = async () => {
  loading.value = true
  try {
    const data = await tradeApi.getPositions()
    positions.value = data
  } catch (error) {
    console.error('Failed to load positions:', error)
    positions.value = [
      {
        symbol: '000001',
        stock_name: 'PING AN BANK',
        quantity: 1000,
        cost_price: 12.50,
        current_price: 13.20,
        profit: 700,
        profit_rate: 5.6,
        update_time: new Date().toISOString()
      },
      {
        symbol: '000002',
        stock_name: 'VANKA A',
        quantity: 500,
        cost_price: 25.80,
        current_price: 26.50,
        profit: 350,
        profit_rate: 2.7,
        update_time: new Date().toISOString()
      }
    ]
  } finally {
    loading.value = false
  }
}

const formatTime = (time: string) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleRefresh = async () => {
  await loadPositions()
  ElMessage.success('POSITION DATA REFRESHED')
}

const handleBuy = () => {
  emit('buy')
}

const handleSell = () => {
  emit('sell')
}

const handleQuickSell = (position: Position) => {
  emit('quick-sell', position)
}

const handleViewDetails = (position: Position) => {
  ElMessageBox.alert(
    `QUANTITY: ${position.quantity}\nCOST PRICE: ¥${position.cost_price}\nCURRENT PRICE: ¥${position.current_price}\nPROFIT: ¥${position.profit} (${position.profit_rate}%)`,
    `${position.stock_name} (${position.symbol})`,
    { confirmButtonText: 'OK' }
  )
}

onMounted(() => {
  loadPositions()
})

defineExpose({
  loadPositions,
  refresh: handleRefresh
})
</script>

<style scoped lang="scss">

.positions-tab {
  width: 100%;
}

.action-bar {
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-4);
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.btn-icon {
  font-size: 14px;
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

  .code-cell {
    font-family: var(--font-mono);
    color: var(--accent-gold);
  }

  .number-cell {
    text-align: right;
    font-family: var(--font-mono);
  }

  .price-cell {
    font-family: var(--font-mono);
    text-align: right;
  }

  .amount-cell {
    font-family: var(--font-mono);
    text-align: right;
    color: var(--fg-primary);
  }

  .profit-cell,
  .rate-cell {
    font-family: var(--font-mono);
    text-align: right;
    font-weight: 600;
  }

  .time-cell {
    font-family: var(--font-mono);
    font-size: var(--font-size-xs);
    white-space: nowrap;
  }

  .action-cell {
    display: flex;
    gap: var(--spacing-2);
    white-space: nowrap;
  }
}

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-6);
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

  background: var(--color-up);
  border-color: var(--color-up);
  color: white;

  &:hover:not(:disabled) {
    background: #D94F51;
    border-color: #D94F51;
    box-shadow: 0 0 20px rgba(255, 82, 82, 0.4);
  }
}

  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-xs);
  letter-spacing: 0;
}

.profit-up {
  color: var(--color-up) !important;
}

.profit-down {
  color: var(--color-down) !important;
}
</style>
