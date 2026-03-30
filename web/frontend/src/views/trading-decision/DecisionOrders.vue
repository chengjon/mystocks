<template>
  <div>
        <div v-if="activeTab === 'orders'" class="tab-content">
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
                <el-button type="success" size="small" @click="handleQuickBuy" plain>
                  买入
                </el-button>
                <el-button type="danger" size="small" @click="handleQuickSell" plain>
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
import { ref, reactive } from 'vue'
import { Search } from '@element-plus/icons-vue'
import ArtDecoCardCompact from '@/components/artdeco/ArtDecoCardCompact.vue'

defineProps<{
  activeTab?: string
}>()

const currentPrice = ref('0.00')

const orderForm = reactive({
  symbol: '',
  orderType: 'market',
  quantity: 100
})

interface OrderHistoryItem {
  symbol: string
  name: string
  orderType: string
  quantity: number
  price: number
  status: string
  time: string
}

const orderHistory = ref<OrderHistoryItem[]>([])

const handleQuickAction = (_action: string): void => {
}

const handleQuickBuy = (): void => {
}

const handleQuickSell = (): void => {
}

const handleRefreshOrders = (): void => {
}

const getStatusVariant = (status: string): 'success' | 'info' | 'warning' | 'danger' | 'primary' | undefined => {
  if (status === '已成交') return 'success'
  if (status === '已撤销') return 'info'
  if (status === '待成交') return 'warning'
  return undefined
}
</script>
