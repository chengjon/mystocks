<template>
  <div>
        <div v-if="isVisible" class="tab-content">
          <!-- Order Entry Panel -->
          <ArtDecoCardCompact>
            <template #header>
              <div class="card-header-flex">
                <h3>委托下单</h3>
                <div class="header-actions">
                  <el-button class="artdeco-gold-cta" size="small" @click="handleQuickAction('create-order')">
                    新建委托
                  </el-button>
                </div>
              </div>
            </template>
            <div class="order-entry-panel">
              <!-- Symbol Search -->
              <div class="search-row">
                <el-input
                  v-model="orderForm.symbol"
                  placeholder="股票代码/名称"
                  clearable
                  size="small"
                  @keyup.enter="handleQuickAction('search-stock')"
                  class="artdeco-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button type="primary" size="small" @click="handleQuickAction('search-stock')">
                  搜索
                </el-button>
              </div>

              <!-- Order Type & Quantity -->
              <div class="order-options">
                <el-select v-model="orderForm.orderType" placeholder="订单类型" size="small">
                  <el-option label="市价单" value="market"></el-option>
                  <el-option label="限价单" value="limit"></el-option>
                </el-select>

                <el-input-number
                  v-model="orderForm.quantity"
                  :min="1"
                  :max="1000000"
                  :step="100"
                  placeholder="数量"
                  size="small"
                  controls-position="right"
                  class="artdeco-input-number"
                />
                <span class="quantity-unit">股</span>
              </div>

              <!-- Quick Action Buttons -->
              <div class="quick-action-buttons">
                <el-button type="success" size="small" :loading="submitting" @click="handleQuickBuy" plain>
                  买入
                </el-button>
                <el-button type="danger" size="small" :loading="submitting" @click="handleQuickSell" plain>
                  卖出
                </el-button>
              </div>

              <!-- Price Display -->
              <div class="price-display" v-if="orderForm.symbol">
                <div class="price-label">当前价：</div>
                <div class="price-value">{{ currentPrice }}</div>
              </div>
            </div>
          </ArtDecoCardCompact>

          <!-- Order History List -->
          <div class="order-history-list">
            <ArtDecoCardCompact>
              <template #header>
                <h3>委托历史</h3>
              </template>
              <el-table
                :data="orderHistory"
                size="small"
                stripe
                max-height="400"
                class="artdeco-table-compact"
              >
                <el-table-column prop="symbol" label="代码" width="100" />
                <el-table-column prop="name" label="名称" width="120" />
                <el-table-column prop="orderType" label="类型" width="80" />
                <el-table-column prop="quantity" label="数量" width="80" align="right" />
                <el-table-column prop="price" label="价格" width="100" align="right" />
                <el-table-column prop="status" label="状态" width="80" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getStatusVariant(row.status)" size="small">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="time" label="时间" width="140" sortable />
              </el-table>
            <div class="refresh-section">
              <el-button size="small" @click="handleRefreshOrders" plain>
                刷新列表
              </el-button>
            </div>
          </ArtDecoCardCompact>
        </div>
    </div>

        <!-- Portfolio Tab -->
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import ArtDecoCardCompact from '@/components/artdeco/ArtDecoCardCompact.vue'
import { marketApi } from '@/api/market.ts'
import { tradeApi } from '@/api/trade.ts'
import type { OrderRequest } from '@/api/types/additional-types.ts'

const AUTO_REFRESH_EVENT = 'trading-decision:auto-refresh'

const props = defineProps<{
  activeTab?: string
}>()

const currentPrice = ref('0.00')
const isVisible = computed(() => !props.activeTab || props.activeTab === 'orders')

const orderForm = reactive<{
  symbol: string
  orderType: NonNullable<OrderRequest['type']>
  quantity: number
}>({
  symbol: '',
  orderType: 'market',
  quantity: 100
})

interface OrderHistoryItem {
  id: string
  symbol: string
  name: string
  orderType: string
  quantity: number
  price: number
  status: string
  time: string
}

const orderHistory = ref<OrderHistoryItem[]>([])
const submitting = ref(false)

const loadOrders = async (): Promise<void> => {
  const orders = await tradeApi.getOrders({
    symbol: orderForm.symbol || undefined,
    limit: 20
  })

  orderHistory.value = orders.map((order) => ({
    id: order.orderId,
    symbol: order.symbol,
    name: order.name,
    orderType: order.type,
    quantity: order.quantity,
    price: order.price,
    status: order.status,
    time: order.orderTime
  }))
}

const handleQuickAction = async (action: string): Promise<void> => {
  if (action === 'search-stock') {
    await handleSearchStock()
    return
  }

  if (action === 'create-order') {
    ElMessage.info('请使用买入或卖出按钮提交委托')
  }
}

const handleSearchStock = async (): Promise<void> => {
  const query = orderForm.symbol.trim()
  if (!query) {
    ElMessage.warning('请输入股票代码或名称')
    return
  }

  try {
    const results = await marketApi.searchStocks(query, 10)
    const firstMatch = results[0]

    if (!firstMatch) {
      currentPrice.value = '0.00'
      ElMessage.warning(`未找到 ${query} 的行情信息`)
      return
    }

    orderForm.symbol = firstMatch.symbol
    currentPrice.value = firstMatch.current.toFixed(2)
    ElMessage.success(`已载入 ${firstMatch.name} (${firstMatch.symbol})`)
    await loadOrders()
  } catch (error) {
    currentPrice.value = '0.00'
    ElMessage.error(error instanceof Error ? error.message : '股票搜索失败')
  }
}

const normalizeOrderSymbol = (symbol: string): string => {
  const trimmed = symbol.trim().toUpperCase()
  if (/^\d{6}\.(SH|SZ)$/.test(trimmed)) {
    return trimmed
  }

  if (/^\d{6}$/.test(trimmed)) {
    return `${trimmed}.${trimmed.startsWith('6') ? 'SH' : 'SZ'}`
  }

  return trimmed
}

const submitOrder = async (side: 'buy' | 'sell'): Promise<void> => {
  if (!orderForm.symbol) {
    ElMessage.warning('请先搜索股票')
    return
  }

  if (!orderForm.quantity || orderForm.quantity <= 0 || orderForm.quantity % 100 !== 0) {
    ElMessage.warning('委托数量必须是大于 0 的 100 整数倍')
    return
  }

  const price = Number.parseFloat(currentPrice.value)
  if (!Number.isFinite(price) || price <= 0) {
    ElMessage.warning('请先获取有效价格后再提交委托')
    return
  }

  const requestPayload: OrderRequest = {
    symbol: normalizeOrderSymbol(orderForm.symbol),
    side,
    type: orderForm.orderType,
    quantity: orderForm.quantity,
    price
  }

  submitting.value = true
  try {
    await tradeApi.createOrder(requestPayload)
    ElMessage.success(`${side === 'buy' ? '买入' : '卖出'}委托已提交`)
    await handleRefreshOrders(false)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '委托提交失败')
  } finally {
    submitting.value = false
  }
}

const handleQuickBuy = (): void => {
  void submitOrder('buy')
}

const handleQuickSell = (): void => {
  void submitOrder('sell')
}

const handleRefreshOrders = async (showSuccess = true): Promise<void> => {
  try {
    await loadOrders()
    if (showSuccess) {
      ElMessage.success('委托列表已刷新')
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '委托列表刷新失败')
  }
}

const handleAutoRefresh = (): void => {
  void handleRefreshOrders(false)
}

onMounted(() => {
  window.addEventListener(AUTO_REFRESH_EVENT, handleAutoRefresh)
  void handleRefreshOrders(false)
})

onBeforeUnmount(() => {
  window.removeEventListener(AUTO_REFRESH_EVENT, handleAutoRefresh)
})

const getStatusVariant = (status: string): 'success' | 'info' | 'warning' | 'danger' | 'primary' | undefined => {
  if (status === '已成交' || status === 'filled') return 'success'
  if (status === '已撤销' || status === 'cancelled') return 'info'
  if (status === '待成交' || status === 'pending' || status === 'partial') return 'warning'
  if (status === 'rejected') return 'danger'
  return undefined
}
</script>
