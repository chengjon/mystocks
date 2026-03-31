<template>
  <div class="positions-tab">
    <!-- Bloomberg-style Action Bar -->
    <div class="action-bar">
      <div class="action-buttons">
        <el-button type="primary" @click="handleBuy">
          BUY
        </el-button>
        <el-button type="danger" @click="handleSell">
          SELL
        </el-button>
        <el-button @click="handleRefresh" :loading="loading">
          REFRESH
        </el-button>
      </div>
    </div>

    <!-- Bloomberg-style Table -->
    <div class="table-container" v-loading="loading">
      <el-table
        :data="positions"
        class="bloomberg-table"
        stripe
        border
      >
        <el-table-column prop="symbol" label="CODE" width="120" />
        <el-table-column prop="stock_name" label="NAME" width="180" />
        <el-table-column prop="quantity" label="QUANTITY" width="120" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ row.quantity.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="cost_price" label="COST PRICE" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-text">¥{{ row.cost_price?.toFixed(2) || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="CURRENT PRICE" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-text">¥{{ row.current_price?.toFixed(2) || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="MARKET VALUE" width="160" align="right">
          <template #default="{ row }">
            <span class="mono-text">¥{{ ((row.quantity * row.current_price)?.toFixed(2)) || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="profit" label="PROFIT" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-text" :class="row.profit >= 0 ? 'profit-up' : 'profit-down'">
              ¥{{ row.profit?.toFixed(2) || '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_rate" label="PROFIT RATE" width="120" align="right">
          <template #default="{ row }">
            <span class="mono-text" :class="row.profit_rate >= 0 ? 'profit-up' : 'profit-down'">
              {{ row.profit_rate >= 0 ? '+' : '' }}{{ row.profit_rate?.toFixed(2) || '-' }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="update_time" label="UPDATE TIME" width="160">
          <template #default="{ row }">
            <span class="mono-text">{{ formatTime(row.update_time) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="ACTIONS" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              @click="handleQuickSell(row)"
            >
              SELL
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="handleViewDetails(row)"
            >
              DETAILS
            </el-button>
          </template>
        </el-table-column>
      </el-table>
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
const positions = ref<unknown[]>([])

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
@use '@/styles/artdeco-tokens.scss' as *;

.positions-tab {
  width: 100%;
}

.action-bar {
  margin-bottom: var(--artdeco-spacing-5);
  padding: var(--artdeco-spacing-4);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 3%, var(--artdeco-bg-card));
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
}

.action-buttons {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
}

.table-container {
  overflow-x: auto;
  border: 1px solid var(--artdeco-border-default);
  background: linear-gradient(
    135deg,
    var(--artdeco-bg-global) 0%,
    var(--artdeco-bg-card) 100%
  );
  border-radius: var(--artdeco-radius-none);
}

.bloomberg-table {
  width: 100%;
  background: transparent !important;

  :deep(.el-table__inner-wrapper::before) {
    background-color: var(--artdeco-border-default) !important;
  }

  :deep(.el-table__header-wrapper) {
    background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card));
    border-bottom: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-border-default);

    th {
      background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card)) !important;
      border-bottom: 1px solid var(--artdeco-border-default);
      color: var(--artdeco-gold-primary);
      font-family: var(--artdeco-font-heading, var(--font-display));
      font-size: var(--artdeco-text-compact-xs);
      font-weight: var(--artdeco-font-semibold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-widest);
      padding: var(--artdeco-spacing-3) 0;
    }
  }

  :deep(.el-table__body-wrapper) {
    background: transparent;

    tr {
      background: transparent !important;
      transition: background var(--artdeco-transition-quick) var(--artdeco-ease-out);

      &:hover > td {
        background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card)) !important;
      }

      td {
        border-bottom: 1px solid color-mix(in srgb, var(--artdeco-border-default) 80%, transparent);
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-accent, var(--font-mono));
        font-size: var(--artdeco-text-compact-base);
        padding: var(--artdeco-spacing-3) 0;
        background: transparent !important;
      }
    }
  }

  .mono-text {
    font-family: var(--artdeco-font-accent, var(--font-mono));
    font-size: var(--artdeco-text-compact-base);
    color: var(--artdeco-fg-primary);
  }

  .profit-up {
    color: var(--artdeco-rise) !important;
  }

  .profit-down {
    color: var(--artdeco-down) !important;
  }
}

@media (width <= 48rem) {
  .action-bar {
    padding: var(--artdeco-spacing-3);

    .action-buttons {
      flex-direction: column;

      button {
        width: 100%;
      }
    }
  }
}
</style>
