<template>
  <div class="watchlist-management fintech-bg-primary">
    <!-- 顶部标题栏 -->
    <div class="fintech-card elevated header-section">
      <div class="header-content">
        <div class="title-section">
          <h1 class="fintech-text-primary page-title">MONITORING PORTFOLIOS</h1>
          <p class="fintech-text-secondary page-subtitle">智能量化监控组合管理</p>
        </div>
        <div class="actions-section">
          <button class="fintech-btn primary" @click="showCreateModal">
            <plus-outlined />
            <span>CREATE PORTFOLIO</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 统计面板 -->
    <div class="stats-grid">
      <div class="fintech-card stat-card">
        <div class="stat-content">
          <div class="stat-value fintech-text-primary">{{ watchlists.length }}</div>
          <div class="stat-label fintech-text-secondary">ACTIVE PORTFOLIOS</div>
        </div>
        <div class="stat-icon">
          <folder-open-outlined />
        </div>
      </div>

      <div class="fintech-card stat-card">
        <div class="stat-content">
          <div class="stat-value fintech-text-primary">{{ totalStocks }}</div>
          <div class="stat-label fintech-text-secondary">TOTAL STOCKS</div>
        </div>
        <div class="stat-icon">
          <stock-outlined />
        </div>
      </div>

      <div class="fintech-card stat-card">
        <div class="stat-content">
          <div class="stat-value fintech-text-primary">{{ activeAlerts }}</div>
          <div class="stat-label fintech-text-secondary">ACTIVE ALERTS</div>
        </div>
        <div class="stat-icon">
          <alert-outlined />
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="content-grid">
      <!-- 组合列表 -->
      <div class="fintech-card main-content">
        <div class="card-header">
          <h3 class="fintech-text-primary card-title">PORTFOLIO LIST</h3>
          <div class="card-actions">
            <button class="fintech-btn" @click="refreshData">
              <reload-outlined />
            </button>
          </div>
        </div>

        <div class="portfolio-list" v-if="watchlists.length > 0">
          <div
            v-for="portfolio in watchlists"
            :key="portfolio.id"
            class="portfolio-item fintech-card interactive"
            @click="handlePortfolioClick(portfolio)"
          >
            <div class="portfolio-header">
              <div class="portfolio-info">
                <h4 class="portfolio-name fintech-text-primary">{{ portfolio.name }}</h4>
                <div class="portfolio-meta">
                  <span class="portfolio-type" :class="getTypeClass(portfolio.watchlist_type)">
                    {{ getTypeText(portfolio.watchlist_type) }}
                  </span>
                  <span class="portfolio-count fintech-text-secondary">
                    {{ portfolio.stocks_count || 0 }} STOCKS
                  </span>
                </div>
              </div>
              <div class="portfolio-status">
                <span class="status-indicator" :class="portfolio.is_active ? 'active' : 'inactive'">
                  {{ portfolio.is_active ? 'ACTIVE' : 'INACTIVE' }}
                </span>
              </div>
            </div>

            <div class="portfolio-actions">
              <button class="fintech-btn" @click.stop="editWatchlist(portfolio)">
                <edit-outlined />
              </button>
              <button class="fintech-btn" @click.stop="manageStocks(portfolio)">
                <setting-outlined />
              </button>
              <button class="fintech-btn danger" @click.stop="confirmDelete(portfolio)">
                <delete-outlined />
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-content">
            <folder-open-outlined class="empty-icon" />
            <h3 class="fintech-text-secondary">NO PORTFOLIOS YET</h3>
            <p class="fintech-text-tertiary">Create your first monitoring portfolio to get started</p>
            <button class="fintech-btn primary" @click="showCreateModal">
              <plus-outlined />
              CREATE FIRST PORTFOLIO
            </button>
          </div>
        </div>
      </div>

      <!-- 快速概览面板 -->
      <div class="fintech-card sidebar">
        <div class="card-header">
          <h3 class="fintech-text-primary card-title">QUICK OVERVIEW</h3>
        </div>

        <div class="overview-content">
          <div class="overview-item">
            <div class="overview-label fintech-text-secondary">TOTAL VALUE</div>
            <div class="overview-value fintech-text-primary">{{ formatCurrency(totalValue) }}</div>
          </div>

          <div class="overview-item">
            <div class="overview-label fintech-text-secondary">DAY P&L</div>
            <div class="overview-value" :class="totalPnL >= 0 ? 'fintech-text-up' : 'fintech-text-down'">
              {{ formatCurrency(totalPnL) }}
            </div>
          </div>

          <div class="overview-item">
            <div class="overview-label fintech-text-secondary">WIN RATE</div>
            <div class="overview-value fintech-text-primary">{{ winRate }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 股票管理抽屉 -->
    <div class="stock-drawer-overlay" v-if="stockDrawerVisible" @click="stockDrawerVisible = false">
      <div class="stock-drawer fintech-card elevated" @click.stop>
        <div class="drawer-header">
          <h2 class="fintech-text-primary drawer-title">
            STOCK MANAGEMENT - {{ currentWatchlist?.name }}
          </h2>
          <div class="drawer-actions">
            <button class="fintech-btn" @click="stockDrawerVisible = false">
              <close-outlined />
            </button>
            <button class="fintech-btn primary" @click="showAddStockModal">
              <plus-outlined />
              ADD STOCK
            </button>
          </div>
        </div>

        <div class="drawer-content">
          <div class="stock-table-container">
            <table class="fintech-table stock-table">
              <thead>
                <tr>
                  <th>SYMBOL</th>
                  <th>ENTRY PRICE</th>
                  <th>CURRENT PRICE</th>
                  <th>P&L</th>
                  <th>REASON</th>
                  <th>STOP LOSS</th>
                  <th>TARGET</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="stock in watchlistStocks" :key="stock.id" class="stock-row">
                  <td class="fintech-text-data">{{ stock.stock_code }}</td>
                  <td class="fintech-text-data">{{ formatPrice(stock.entry_price) }}</td>
                  <td class="fintech-text-data">{{ formatPrice(stock.current_price || stock.entry_price) }}</td>
                  <td :class="getPnlClass(stock)">
                    {{ getPnlPercent(stock) }}
                  </td>
                  <td>
                    <span class="reason-tag" :class="getReasonClass(stock.entry_reason)">
                      {{ getReasonText(stock.entry_reason) }}
                    </span>
                  </td>
                  <td class="fintech-text-data">{{ formatPrice(stock.stop_loss_price) }}</td>
                  <td class="fintech-text-data">{{ formatPrice(stock.target_price) }}</td>
                  <td>
                    <button class="fintech-btn danger" @click="confirmRemoveStock(stock)">
                      <delete-outlined />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建/编辑组合弹窗 -->
    <div class="modal-overlay" v-if="createModalVisible" @click="createModalVisible = false">
      <div class="modal fintech-card elevated" @click.stop>
        <div class="modal-header">
          <h2 class="fintech-text-primary modal-title">
            {{ editingWatchlist ? 'EDIT PORTFOLIO' : 'CREATE PORTFOLIO' }}
          </h2>
          <button class="modal-close" @click="createModalVisible = false">
            <close-outlined />
          </button>
        </div>

        <form class="modal-form" @submit.prevent="handleCreateOrUpdate">
          <div class="form-group">
            <label class="form-label fintech-text-primary">PORTFOLIO NAME</label>
            <input
              v-model="watchlistForm.name"
              type="text"
              class="form-input fintech-text-primary"
              placeholder="Enter portfolio name"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label fintech-text-primary">PORTFOLIO TYPE</label>
            <select v-model="watchlistForm.watchlist_type" class="form-select fintech-text-primary">
              <option value="manual">MANUAL</option>
              <option value="strategy">STRATEGY</option>
              <option value="benchmark">BENCHMARK</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label fintech-text-primary">RISK TOLERANCE</label>
            <div class="slider-container">
              <input
                v-model="riskTolerance"
                type="range"
                min="0"
                max="100"
                step="10"
                class="form-slider"
              />
              <div class="slider-labels">
                <span class="fintech-text-tertiary">CONSERVATIVE</span>
                <span class="fintech-text-primary">{{ riskTolerance }}%</span>
                <span class="fintech-text-tertiary">AGGRESSIVE</span>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="fintech-btn" @click="createModalVisible = false">
              CANCEL
            </button>
            <button type="submit" class="fintech-btn primary">
              {{ editingWatchlist ? 'UPDATE' : 'CREATE' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 添加股票弹窗 -->
    <div class="modal-overlay" v-if="addStockModalVisible" @click="addStockModalVisible = false">
      <div class="modal fintech-card elevated" @click.stop>
        <div class="modal-header">
          <h2 class="fintech-text-primary modal-title">ADD STOCK</h2>
          <button class="modal-close" @click="addStockModalVisible = false">
            <close-outlined />
          </button>
        </div>

        <form class="modal-form" @submit.prevent="handleAddStock">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label fintech-text-primary">SYMBOL</label>
              <input
                v-model="stockForm.stock_code"
                type="text"
                class="form-input fintech-text-primary"
                placeholder="e.g. 600519.SH"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label fintech-text-primary">ENTRY PRICE</label>
              <input
                v-model="stockForm.entry_price"
                type="number"
                step="0.01"
                class="form-input fintech-text-primary"
                placeholder="0.00"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label fintech-text-primary">ENTRY REASON</label>
            <select v-model="stockForm.entry_reason" class="form-select fintech-text-primary">
              <option value="macd_gold_cross">MACD GOLD CROSS</option>
              <option value="rsi_oversold">RSI OVERSOLD</option>
              <option value="volume_breakout">VOLUME BREAKOUT</option>
              <option value="manual_pick">MANUAL PICK</option>
              <option value="value_investment">VALUE INVESTMENT</option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label fintech-text-primary">STOP LOSS</label>
              <input
                v-model="stockForm.stop_loss_price"
                type="number"
                step="0.01"
                class="form-input fintech-text-primary"
                placeholder="0.00"
              />
            </div>
            <div class="form-group">
              <label class="form-label fintech-text-primary">TARGET PRICE</label>
              <input
                v-model="stockForm.target_price"
                type="number"
                step="0.01"
                class="form-input fintech-text-primary"
                placeholder="0.00"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label fintech-text-primary">WEIGHT</label>
            <div class="slider-container">
              <input
                v-model="stockForm.weight"
                type="range"
                min="0"
                max="1"
                step="0.01"
                class="form-slider"
              />
              <div class="slider-value fintech-text-primary">
                {{ (stockForm.weight * 100).toFixed(1) }}%
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="fintech-btn" @click="addStockModalVisible = false">
              CANCEL
            </button>
            <button type="submit" class="fintech-btn primary">
              ADD STOCK
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div class="modal-overlay" v-if="deleteConfirmVisible" @click="deleteConfirmVisible = false">
      <div class="modal fintech-card elevated" @click.stop>
        <div class="modal-header">
          <h2 class="fintech-text-primary modal-title">CONFIRM DELETE</h2>
          <button class="modal-close" @click="deleteConfirmVisible = false">
            <close-outlined />
          </button>
        </div>

        <div class="modal-content">
          <p class="fintech-text-primary confirm-message">
            Are you sure you want to delete portfolio "{{ portfolioToDelete?.name }}"?
          </p>
          <p class="fintech-text-secondary confirm-warning">
            This action cannot be undone.
          </p>
        </div>

        <div class="modal-actions">
          <button class="fintech-btn" @click="deleteConfirmVisible = false">
            CANCEL
          </button>
          <button class="fintech-btn danger" @click="deleteWatchlist(portfolioToDelete.id)">
            DELETE
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SettingOutlined,
  CloseOutlined,
  FolderOpenOutlined,
  StockOutlined,
  AlertOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

const loading = ref(false)
const watchlists = ref([])
const watchlistStocks = ref([])
const stockDrawerVisible = ref(false)
const createModalVisible = ref(false)
const addStockModalVisible = ref(false)
const deleteConfirmVisible = ref(false)
const currentWatchlist = ref(null)
const editingWatchlist = ref(null)
const portfolioToDelete = ref(null)

const watchlistForm = reactive({
  name: '',
  watchlist_type: 'manual',
  risk_profile: {}
})

const stockForm = reactive({
  stock_code: '',
  entry_price: null,
  entry_reason: null,
  stop_loss_price: null,
  target_price: null,
  weight: 0.1
})

const riskTolerance = ref(50)

// 计算属性
const totalStocks = computed(() => {
  return watchlists.value.reduce((sum, wl) => sum + (wl.stocks_count || 0), 0)
})

const totalValue = computed(() => {
  return watchlistStocks.value.reduce((sum, stock) => {
    const price = stock.current_price || stock.entry_price || 0
    return sum + (price * (stock.weight || 1))
  }, 0)
})

const totalPnL = computed(() => {
  return watchlistStocks.value.reduce((sum, stock) => {
    const current = stock.current_price || stock.entry_price || 0
    const entry = stock.entry_price || 0
    const pnl = (current - entry) * (stock.weight || 1)
    return sum + pnl
  }, 0)
})

const winRate = computed(() => {
  if (watchlistStocks.value.length === 0) return 0
  const winners = watchlistStocks.value.filter(stock => {
    const current = stock.current_price || stock.entry_price || 0
    const entry = stock.entry_price || 0
    return current > entry
  }).length
  return Math.round((winners / watchlistStocks.value.length) * 100)
})

const activeAlerts = computed(() => {
  // 计算活跃告警数量（模拟数据）
  return Math.floor(Math.random() * 5)
})

// 工具函数
const getTypeClass = (type) => {
  const classes = {
    manual: 'type-manual',
    strategy: 'type-strategy',
    benchmark: 'type-benchmark'
  }
  return classes[type] || 'type-manual'
}

const getTypeText = (type) => {
  const texts = {
    manual: 'MANUAL',
    strategy: 'STRATEGY',
    benchmark: 'BENCHMARK'
  }
  return texts[type] || type
}

const getPnlClass = (stock) => {
  const current = stock.current_price || stock.entry_price || 0
  const entry = stock.entry_price || 0
  const pnl = ((current - entry) / entry) * 100
  return pnl >= 0 ? 'fintech-text-up' : 'fintech-text-down'
}

const getPnlPercent = (stock) => {
  const current = stock.current_price || stock.entry_price || 0
  const entry = stock.entry_price || 0
  if (entry === 0) return '0.00%'
  const pnl = ((current - entry) / entry) * 100
  return `${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}%`
}

const getReasonClass = (reason) => {
  const classes = {
    'macd_gold_cross': 'reason-technical',
    'rsi_oversold': 'reason-technical',
    'volume_breakout': 'reason-volume',
    'manual_pick': 'reason-manual',
    'value_investment': 'reason-value'
  }
  return classes[reason] || 'reason-manual'
}

const getReasonText = (reason) => {
  const texts = {
    'macd_gold_cross': 'MACD CROSS',
    'rsi_oversold': 'RSI OVERSOLD',
    'volume_breakout': 'VOL BREAKOUT',
    'manual_pick': 'MANUAL',
    'value_investment': 'VALUE'
  }
  return texts[reason] || reason || 'UNKNOWN'
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(value || 0)
}

const formatPrice = (price) => {
  return price ? price.toFixed(2) : '-'
}

// 数据获取函数
const fetchWatchlists = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/monitoring/watchlists')
    const data = await res.json()
    if (data.success) {
      watchlists.value = data.data
    }
  } catch (error) {
    console.error('获取清单列表失败:', error)
    message.error('获取清单列表失败')
  } finally {
    loading.value = false
  }
}

const fetchWatchlistStocks = async (watchlistId) => {
  try {
    const res = await fetch(`/api/monitoring/watchlists/${watchlistId}/stocks`)
    const data = await res.json()
    if (data.success) {
      watchlistStocks.value = data.data
    }
  } catch (error) {
    console.error('获取股票列表失败:', error)
  }
}

const refreshData = async () => {
  await fetchWatchlists()
  if (currentWatchlist.value) {
    await fetchWatchlistStocks(currentWatchlist.value.id)
  }
  message.success('数据已刷新')
}

// 事件处理函数
const handlePortfolioClick = (portfolio) => {
  currentWatchlist.value = portfolio
  stockDrawerVisible.value = true
  fetchWatchlistStocks(portfolio.id)
}

const showCreateModal = () => {
  editingWatchlist.value = null
  watchlistForm.name = ''
  watchlistForm.watchlist_type = 'manual'
  riskTolerance.value = 50
  createModalVisible.value = true
}

const editWatchlist = (record) => {
  editingWatchlist.value = record
  watchlistForm.name = record.name
  watchlistForm.watchlist_type = record.watchlist_type
  riskTolerance.value = record.risk_profile?.risk_tolerance || 50
  createModalVisible.value = true
}

const handleCreateOrUpdate = async () => {
  try {
    watchlistForm.risk_profile = { risk_tolerance: riskTolerance.value }

    const url = editingWatchlist.value
      ? `/api/monitoring/watchlists/${editingWatchlist.value.id}`
      : '/api/monitoring/watchlists'

    const method = editingWatchlist.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(watchlistForm)
    })

    const data = await res.json()
    if (data.success) {
      message.success(editingWatchlist.value ? '更新成功' : '创建成功')
      createModalVisible.value = false
      await fetchWatchlists()
    } else {
      message.error(data.message || '操作失败')
    }
  } catch (error) {
    console.error('保存清单失败:', error)
    message.error('保存失败')
  }
}

const confirmDelete = (portfolio) => {
  portfolioToDelete.value = portfolio
  deleteConfirmVisible.value = true
}

const deleteWatchlist = async (id) => {
  try {
    const res = await fetch(`/api/monitoring/watchlists/${id}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.success) {
      message.success('删除成功')
      deleteConfirmVisible.value = false
      portfolioToDelete.value = null
      await fetchWatchlists()
    } else {
      message.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除清单失败:', error)
    message.error('删除失败')
  }
}

const manageStocks = (record) => {
  currentWatchlist.value = record
  stockDrawerVisible.value = true
  fetchWatchlistStocks(record.id)
}

const showAddStockModal = () => {
  stockForm.stock_code = ''
  stockForm.entry_price = null
  stockForm.entry_reason = null
  stockForm.stop_loss_price = null
  stockForm.target_price = null
  stockForm.weight = 0.1
  addStockModalVisible.value = true
}

const handleAddStock = async () => {
  try {
    const res = await fetch(`/api/monitoring/watchlists/${currentWatchlist.value.id}/stocks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(stockForm)
    })

    const data = await res.json()
    if (data.success) {
      message.success('添加成功')
      addStockModalVisible.value = false
      await fetchWatchlistStocks(currentWatchlist.value.id)
      await fetchWatchlists()
    } else {
      message.error(data.message || '添加失败')
    }
  } catch (error) {
    console.error('添加股票失败:', error)
    message.error('添加失败')
  }
}

const confirmRemoveStock = (stock) => {
  // 简化版：直接删除
  removeStock(stock.id)
}

const removeStock = async (stockId) => {
  try {
    const res = await fetch(`/api/monitoring/watchlists/${currentWatchlist.value.id}/stocks/${stockId}`, {
      method: 'DELETE'
    })

    const data = await res.json()
    if (data.success) {
      message.success('移除成功')
      await fetchWatchlistStocks(currentWatchlist.value.id)
      await fetchWatchlists()
    } else {
      message.error(data.message || '移除失败')
    }
  } catch (error) {
    console.error('移除股票失败:', error)
    message.error('移除失败')
  }
}

onMounted(() => {
  fetchWatchlists()
})
</script>

<style scoped>
/* ========================================
   Bloomberg-Level Financial Terminal UI
   ======================================== */

.watchlist-management {
  min-height: 100vh;
  padding: var(--fintech-space-4);
  background: var(--fintech-bg-primary);
}

/* 标题栏样式 */
.header-section {
  margin-bottom: var(--fintech-space-6);
  background: linear-gradient(135deg, var(--fintech-bg-elevated) 0%, var(--fintech-bg-secondary) 100%);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fintech-space-6);
}

.title-section h1 {
  margin: 0 0 var(--fintech-space-2) 0;
  font-size: var(--fintech-font-size-3xl);
  font-weight: 600;
  letter-spacing: 0.02em;
}

.page-subtitle {
  margin: 0;
  font-size: var(--fintech-font-size-md);
  opacity: 0.8;
}

.actions-section .fintech-btn {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-2);
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* 统计面板网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--fintech-space-4);
  margin-bottom: var(--fintech-space-6);
}

.stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--fintech-space-5);
  background: linear-gradient(135deg, var(--fintech-bg-secondary) 0%, var(--fintech-bg-tertiary) 100%);
  border: 1px solid var(--fintech-border-base);
  transition: all var(--fintech-transition-base);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--fintech-shadow-base);
  border-color: var(--fintech-accent-primary);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: var(--fintech-font-size-3xl);
  font-weight: 600;
  font-family: var(--fintech-font-family-data);
  margin-bottom: var(--fintech-space-1);
  letter-spacing: 0.01em;
}

.stat-label {
  font-size: var(--fintech-font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.8;
}

.stat-icon {
  font-size: 32px;
  opacity: 0.6;
  color: var(--fintech-accent-primary);
}

/* 主内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--fintech-space-6);
  align-items: start;
}

.main-content {
  background: var(--fintech-bg-secondary);
  border: 1px solid var(--fintech-border-base);
}

.sidebar {
  position: sticky;
  top: var(--fintech-space-4);
  background: var(--fintech-bg-secondary);
  border: 1px solid var(--fintech-border-base);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fintech-space-4) var(--fintech-space-5);
  border-bottom: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

.card-title {
  margin: 0;
  font-size: var(--fintech-font-size-lg);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.card-actions .fintech-btn {
  padding: var(--fintech-space-2);
  min-width: auto;
}

/* 组合列表 */
.portfolio-list {
  max-height: 600px;
  overflow-y: auto;
}

.portfolio-item {
  margin: var(--fintech-space-3);
  padding: var(--fintech-space-4);
  border: 1px solid var(--fintech-border-dark);
  background: var(--fintech-bg-tertiary);
  cursor: pointer;
  transition: all var(--fintech-transition-fast);
}

.portfolio-item:hover {
  border-color: var(--fintech-accent-primary);
  background: var(--fintech-bg-elevated);
  transform: translateY(-1px);
}

.portfolio-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--fintech-space-3);
}

.portfolio-info {
  flex: 1;
}

.portfolio-name {
  margin: 0 0 var(--fintech-space-2) 0;
  font-size: var(--fintech-font-size-lg);
  font-weight: 500;
}

.portfolio-meta {
  display: flex;
  gap: var(--fintech-space-4);
  align-items: center;
}

.portfolio-type {
  padding: var(--fintech-space-1) var(--fintech-space-2);
  border-radius: var(--fintech-radius-sm);
  font-size: var(--fintech-font-size-xs);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.portfolio-type.type-manual {
  background: var(--fintech-accent-primary);
  color: white;
}

.portfolio-type.type-strategy {
  background: var(--fintech-accent-success);
  color: white;
}

.portfolio-type.type-benchmark {
  background: var(--fintech-accent-warning);
  color: var(--fintech-bg-primary);
}

.portfolio-count {
  font-size: var(--fintech-font-size-sm);
  font-family: var(--fintech-font-family-data);
}

.portfolio-status .status-indicator {
  padding: var(--fintech-space-1) var(--fintech-space-3);
  border-radius: var(--fintech-radius-sm);
  font-size: var(--fintech-font-size-xs);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.portfolio-status .active {
  background: var(--fintech-accent-success);
  color: white;
}

.portfolio-status .inactive {
  background: var(--fintech-gray-6);
  color: white;
}

.portfolio-actions {
  display: flex;
  gap: var(--fintech-space-2);
  justify-content: flex-end;
}

.portfolio-actions .fintech-btn {
  padding: var(--fintech-space-2);
  min-width: auto;
}

/* 空状态 */
.empty-state {
  padding: var(--fintech-space-8);
  text-align: center;
}

.empty-content .empty-icon {
  font-size: 64px;
  color: var(--fintech-gray-6);
  margin-bottom: var(--fintech-space-4);
  opacity: 0.5;
}

.empty-content h3 {
  margin: 0 0 var(--fintech-space-2) 0;
  font-size: var(--fintech-font-size-xl);
  font-weight: 500;
}

.empty-content p {
  margin: 0 0 var(--fintech-space-6) 0;
  font-size: var(--fintech-font-size-base);
}

/* 快速概览 */
.overview-content {
  padding: var(--fintech-space-4);
}

.overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fintech-space-3) 0;
  border-bottom: 1px solid var(--fintech-border-dark);
}

.overview-item:last-child {
  border-bottom: none;
}

.overview-label {
  font-size: var(--fintech-font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.overview-value {
  font-size: var(--fintech-font-size-lg);
  font-weight: 500;
  font-family: var(--fintech-font-family-data);
}

/* 抽屉样式 */
.stock-drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.stock-drawer {
  width: 90vw;
  max-width: 1200px;
  max-height: 90vh;
  overflow: hidden;
  background: var(--fintech-bg-secondary);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fintech-space-5);
  border-bottom: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

.drawer-title {
  margin: 0;
  font-size: var(--fintech-font-size-xl);
  font-weight: 600;
}

.drawer-actions {
  display: flex;
  gap: var(--fintech-space-3);
}

.drawer-content {
  padding: var(--fintech-space-5);
  max-height: calc(90vh - 120px);
  overflow-y: auto;
}

.stock-table-container {
  background: var(--fintech-bg-primary);
  border-radius: var(--fintech-radius-base);
  overflow: hidden;
  border: 1px solid var(--fintech-border-base);
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
}

.stock-table th {
  padding: var(--fintech-space-3) var(--fintech-space-4);
  text-align: left;
  font-weight: 600;
  font-size: var(--fintech-font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--fintech-bg-tertiary);
  border-bottom: 1px solid var(--fintech-border-base);
  white-space: nowrap;
}

.stock-table td {
  padding: var(--fintech-space-3) var(--fintech-space-4);
  border-bottom: 1px solid var(--fintech-border-dark);
  font-family: var(--fintech-font-family-data);
}

.stock-row:hover {
  background: var(--fintech-bg-tertiary);
}

.reason-tag {
  padding: var(--fintech-space-1) var(--fintech-space-2);
  border-radius: var(--fintech-radius-sm);
  font-size: var(--fintech-font-size-xs);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.reason-technical {
  background: var(--fintech-accent-primary);
  color: white;
}

.reason-volume {
  background: var(--fintech-accent-success);
  color: white;
}

.reason-manual {
  background: var(--fintech-accent-warning);
  color: var(--fintech-bg-primary);
}

.reason-value {
  background: var(--fintech-accent-info);
  color: white;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal {
  width: 90vw;
  max-width: 600px;
  background: var(--fintech-bg-secondary);
  border: 1px solid var(--fintech-border-base);
  border-radius: var(--fintech-radius-lg);
  box-shadow: var(--fintech-shadow-xl);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fintech-space-5);
  border-bottom: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

.modal-title {
  margin: 0;
  font-size: var(--fintech-font-size-xl);
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  color: var(--fintech-text-secondary);
  cursor: pointer;
  padding: var(--fintech-space-2);
  border-radius: var(--fintech-radius-sm);
  transition: all var(--fintech-transition-fast);
}

.modal-close:hover {
  background: var(--fintech-bg-primary);
  color: var(--fintech-text-primary);
}

.modal-content {
  padding: var(--fintech-space-5);
}

.confirm-message {
  margin: 0 0 var(--fintech-space-3) 0;
  font-size: var(--fintech-font-size-base);
}

.confirm-warning {
  margin: 0;
  font-size: var(--fintech-font-size-sm);
}

.modal-form {
  padding: var(--fintech-space-5);
}

.form-group {
  margin-bottom: var(--fintech-space-4);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--fintech-space-4);
  margin-bottom: var(--fintech-space-4);
}

.form-label {
  display: block;
  margin-bottom: var(--fintech-space-2);
  font-size: var(--fintech-font-size-sm);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.form-input,
.form-select {
  width: 100%;
  padding: var(--fintech-space-3);
  background: var(--fintech-bg-tertiary);
  border: 1px solid var(--fintech-border-base);
  border-radius: var(--fintech-radius-sm);
  color: var(--fintech-text-primary);
  font-size: var(--fintech-font-size-base);
  font-family: var(--fintech-font-family-ui);
  transition: all var(--fintech-transition-fast);
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--fintech-accent-primary);
  box-shadow: 0 0 0 2px rgba(0, 128, 255, 0.2);
}

.slider-container {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-4);
}

.form-slider {
  flex: 1;
  height: 6px;
  background: var(--fintech-bg-tertiary);
  border-radius: var(--fintech-radius-sm);
  outline: none;
  -webkit-appearance: none;
}

.form-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  background: var(--fintech-accent-primary);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: var(--fintech-shadow-sm);
}

.form-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: var(--fintech-accent-primary);
  border-radius: 50%;
  cursor: pointer;
  border: none;
  box-shadow: var(--fintech-shadow-sm);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  width: 120px;
  font-size: var(--fintech-font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.slider-value {
  font-family: var(--fintech-font-family-data);
  font-weight: 500;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--fintech-space-3);
  padding: var(--fintech-space-5);
  border-top: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

/* 响应式设计 */
@media (max-width: 1280px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  }
}

/* 高分辨率优化 */
@media (min-width: 1920px) {
  .watchlist-management {
    padding: var(--fintech-space-6);
  }

  .portfolio-name {
    font-size: var(--fintech-font-size-xl);
  }

  .stat-value {
    font-size: 48px;
  }
}
</style>
