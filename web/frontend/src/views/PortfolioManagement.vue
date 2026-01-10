<template>
  <div class="portfolio-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>投资组合管理</h1>
      <p class="subtitle">智能量化 · 精准风控 · 价值发现</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value" :style="{ color: getHealthColor(portfolioSummary.total_score) }">
              {{ portfolioSummary.total_score?.toFixed(1) || '--' }}
            </div>
            <div class="stat-label">组合健康度</div>
            <el-icon class="stat-icon" :style="{ color: getHealthColor(portfolioSummary.total_score) }">
              <TrendCharts />
            </el-icon>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value" :style="{ color: getRiskColor(portfolioSummary.risk_score) }">
              {{ portfolioSummary.risk_score?.toFixed(1) || '--' }}
            </div>
            <div class="stat-label">风险评估</div>
            <el-icon class="stat-icon" :style="{ color: getRiskColor(portfolioSummary.risk_score) }">
              <DataLine />
            </el-icon>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ portfolioSummary.position_count || 0 }}</div>
            <div class="stat-label">持仓数量</div>
            <el-icon class="stat-icon" color="#409EFF">
              <Tickets />
            </el-icon>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card" :class="{ 'has-alert': alertSummary.critical > 0 }">
          <div class="stat-content">
            <div class="stat-value" :style="{ color: getAlertColor() }">
              {{ alertSummary.critical + alertSummary.warning + alertSummary.info }}
            </div>
            <div class="stat-label">预警数量</div>
            <el-icon class="stat-icon" :style="{ color: getAlertColor() }">
              <Bell />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主内容区 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧面板 -->
      <el-col :xs="24" :lg="14">
        <el-card shadow="hover">
          <el-tabs v-model="activeTab" class="portfolio-tabs">
            <!-- 清单管理Tab -->
            <el-tab-pane label="我的清单" name="watchlists">
              <template #label>
                <span class="tab-label">
                  <el-icon><List /></el-icon>
                  我的清单
                </span>
              </template>

              <div class="tab-actions">
                <el-button type="primary" @click="showCreateWatchlist">
                  <el-icon><Plus /></el-icon>
                  新建清单
                </el-button>
              </div>

              <div v-loading="loading" class="watchlist-list">
                <div
                  v-for="watchlist in watchlists"
                  :key="watchlist.id"
                  :class="['watchlist-item', { active: selectedWatchlist?.id === watchlist.id }]"
                  @click="selectWatchlist(watchlist)"
                >
                  <div class="watchlist-header">
                    <h3 class="watchlist-name">{{ watchlist.name }}</h3>
                    <el-tag :type="getTypeTagType(watchlist.watchlist_type)" size="small">
                      {{ getTypeText(watchlist.watchlist_type) }}
                    </el-tag>
                  </div>

                  <div class="watchlist-metrics">
                    <div class="metric">
                      <span class="metric-label">股票数</span>
                      <span class="metric-value">{{ watchlist.stocks_count || 0 }}</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">健康度</span>
                      <span class="metric-value score" :class="getScoreClass(watchlist.total_score)">
                        {{ watchlist.total_score?.toFixed(1) || '--' }}
                      </span>
                    </div>
                  </div>

                  <div class="watchlist-actions">
                    <el-button size="small" @click.stop="manageStocks(watchlist)">管理</el-button>
                    <el-button size="small" type="danger" @click.stop="deleteWatchlist(watchlist.id)">删除</el-button>
                  </div>
                </div>

                <el-empty v-if="watchlists.length === 0 && !loading" description="暂无清单，点击新建">
                  <el-button type="primary" @click="showCreateWatchlist">新建清单</el-button>
                </el-empty>
              </div>
            </el-tab-pane>

            <!-- 健康度分析Tab -->
            <el-tab-pane label="健康度分析" name="analysis">
              <template #label>
                <span class="tab-label">
                  <el-icon><TrendCharts /></el-icon>
                  健康度分析
                </span>
              </template>

              <div class="analysis-content">
                <div class="radar-section">
                  <h3>五维健康雷达</h3>
                  <HealthRadarChart
                    :scores="radarScores"
                    :height="320"
                    :show-legend="true"
                  />
                </div>

                <div class="scores-section">
                  <h3>评分明细</h3>
                  <el-table :data="getScoresTableData()" border stripe>
                    <el-table-column prop="label" label="维度" width="120" />
                    <el-table-column prop="score" label="评分">
                      <template #default="{ row }">
                        <el-progress
                          :percentage="row.score"
                          :color="getProgressColor(row.score)"
                          :stroke-width="12"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="value" label="分数" width="100">
                      <template #default="{ row }">
                        <span :class="getScoreClass(row.score)">{{ row.score.toFixed(1) }}</span>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>

                <div v-if="rebalanceSuggestions.length > 0" class="rebalance-section">
                  <h3>再平衡建议</h3>
                  <el-timeline>
                    <el-timeline-item
                      v-for="(suggestion, index) in rebalanceSuggestions"
                      :key="index"
                      :timestamp="suggestion.stock_code"
                      placement="top"
                    >
                      <el-card>
                        <div class="suggestion-header">
                          <span class="stock-code">{{ suggestion.stock_code }}</span>
                          <el-tag :type="getPriorityTagType(suggestion.priority)" size="small">
                            {{ suggestion.priority }}
                          </el-tag>
                        </div>
                        <p>{{ suggestion.message }}</p>
                        <div class="suggestion-footer">
                          <span class="cost-label">预估成本:</span>
                          <span class="cost-value">{{ (suggestion.estimated_cost * 10000).toFixed(2) }} BP</span>
                        </div>
                      </el-card>
                    </el-timeline-item>
                  </el-timeline>
                </div>
              </div>
            </el-tab-pane>

            <!-- 风险预警Tab -->
            <el-tab-pane label="风险预警" name="alerts">
              <template #label>
                <span class="tab-label">
                  <el-icon><Bell /></el-icon>
                  风险预警
                </span>
              </template>

              <div class="alerts-content">
                <div class="alerts-summary">
                  <el-statistic title="紧急预警" :value="alertSummary.critical">
                    <template #suffix>
                      <el-icon color="#F56C6C"><Warning /></el-icon>
                    </template>
                  </el-statistic>
                  <el-statistic title="风险提醒" :value="alertSummary.warning">
                    <template #suffix>
                      <el-icon color="#E6A23C"><Warning /></el-icon>
                    </template>
                  </el-statistic>
                  <el-statistic title="优化提示" :value="alertSummary.info">
                    <template #suffix>
                      <el-icon color="#67C23A"><InfoFilled /></el-icon>
                    </template>
                  </el-statistic>
                </div>

                <div v-if="allAlerts.length > 0" class="alerts-list">
                  <el-alert
                    v-for="(alert, index) in allAlerts"
                    :key="index"
                    :type="getAlertType(alert.level)"
                    :title="alert.stock_code"
                    :description="alert.message"
                    :closable="false"
                    show-icon
                    class="alert-item"
                  >
                    <template #default>
                      <div class="alert-meta">
                        <el-tag size="small">{{ getAlertTypeText(alert.type) }}</el-tag>
                      </div>
                    </template>
                  </el-alert>
                </div>
                <el-empty v-else description="暂无预警，一切正常" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 右侧面板 -->
      <el-col :xs="24" :lg="10">
        <el-card shadow="hover" class="detail-card">
          <template #header>
            <div v-if="selectedWatchlist" class="detail-header">
              <h2>{{ selectedWatchlist.name }}</h2>
              <el-tag :type="getTypeTagType(selectedWatchlist.watchlist_type)">
                {{ getTypeText(selectedWatchlist.watchlist_type) }}
              </el-tag>
            </div>
          </template>

          <div v-if="selectedWatchlist">
            <div class="detail-stats">
              <el-statistic title="持仓" :value="selectedWatchlist.stocks_count || 0" />
              <el-statistic title="健康度" :value="selectedWatchlist.total_score?.toFixed(1) || '--'" />
            </div>

            <el-divider />

            <h3>持仓股票</h3>
            <div class="stock-cards">
              <el-card
                v-for="stock in watchlistStocks"
                :key="stock.id"
                shadow="hover"
                class="stock-card"
              >
                <div class="stock-header">
                  <span class="stock-code">{{ stock.stock_code }}</span>
                  <el-tag size="small">{{ (stock.weight * 100).toFixed(1) }}%</el-tag>
                </div>

                <el-descriptions :column="3" size="small" border>
                  <el-descriptions-item label="入库价">
                    {{ stock.entry_price?.toFixed(2) || '--' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="止损价">
                    <span class="text-danger">{{ stock.stop_loss_price?.toFixed(2) || '--' }}</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="止盈价">
                    <span class="text-success">{{ stock.target_price?.toFixed(2) || '--' }}</span>
                  </el-descriptions-item>
                </el-descriptions>

                <div class="stock-actions">
                  <el-button type="primary" size="small" @click="calculateHealth(stock)">
                    <el-icon><TrendCharts /></el-icon>
                    健康度
                  </el-button>
                  <el-button size="small" type="danger" @click="removeStock(stock.id)">
                    <el-icon><Delete /></el-icon>
                    移除
                  </el-button>
                </div>
              </el-card>

              <el-empty v-if="watchlistStocks.length === 0" description="暂无持仓" />

              <el-button
                type="primary"
                plain
                class="add-stock-btn"
                @click="showAddStock"
              >
                <el-icon><Plus /></el-icon>
                添加股票
              </el-button>
            </div>
          </div>

          <el-empty v-else description="选择一个清单查看详情">
            <el-button type="primary" @click="showCreateWatchlist">新建清单</el-button>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建/编辑清单对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      :title="editingWatchlist ? '编辑清单' : '新建清单'"
      width="500px"
    >
      <el-form :model="watchlistForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="watchlistForm.name" placeholder="请输入清单名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="watchlistForm.watchlist_type" style="width: 100%">
            <el-option label="手动" value="manual" />
            <el-option label="策略" value="strategy" />
            <el-option label="基准" value="benchmark" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险偏好">
          <el-slider v-model="riskTolerance" :marks="{0: '保守', 50: '适中', 100: '激进'}" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateWatchlist">
          {{ editingWatchlist ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加股票对话框 -->
    <el-dialog
      v-model="addStockDialogVisible"
      title="添加股票"
      width="500px"
    >
      <el-form :model="stockForm" label-width="100px">
        <el-form-item label="股票代码" required>
          <el-input v-model="stockForm.stock_code" placeholder="如: 600519.SH" />
        </el-form-item>
        <el-form-item label="入库价格" required>
          <el-input-number v-model="stockForm.entry_price" :precision="2" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="入库理由">
          <el-select v-model="stockForm.entry_reason" style="width: 100%">
            <el-option label="MACD金叉" value="macd_gold_cross" />
            <el-option label="RSI超卖" value="rsi_oversold" />
            <el-option label="量能突破" value="volume_breakout" />
            <el-option label="手动精选" value="manual_pick" />
            <el-option label="价值投资" value="value_investment" />
          </el-select>
        </el-form-item>
        <el-form-item label="止损价格">
          <el-input-number v-model="stockForm.stop_loss_price" :precision="2" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="止盈价格">
          <el-input-number v-model="stockForm.target_price" :precision="2" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="权重">
          <el-slider v-model="stockForm.weight" :min="0" :max="1" :step="0.01" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addStockDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddStock">添加</el-button>
      </template>
    </el-dialog>

    <!-- 健康度详情对话框 -->
    <el-dialog
      v-model="healthDetailVisible"
      :title="`${currentStock?.stock_code} 健康度详情`"
      width="600px"
    >
      <div v-if="currentStockHealth" class="health-detail-content">
        <el-result :icon="getHealthResultIcon(currentStockHealth.total_score)" :title="`综合评分: ${currentStockHealth.total_score?.toFixed(1) || '--'}`" />

        <div class="radar-display">
          <HealthRadarChart
            :scores="currentStockHealth.radar_scores || {}"
            :height="240"
            :show-legend="false"
          />
        </div>

        <el-divider />

        <h3>高级风险指标</h3>
        <el-row :gutter="16" class="metrics-grid">
          <el-col :span="12">
            <el-statistic title="Sortino比率" :value="currentStockHealth.sortino_ratio?.toFixed(4) || '--'" />
          </el-col>
          <el-col :span="12">
            <el-statistic title="Calmar比率" :value="currentStockHealth.calmar_ratio?.toFixed(4) || '--'" />
          </el-col>
          <el-col :span="12">
            <el-statistic
              title="最大回撤"
              :value="currentStockHealth.max_drawdown ? (currentStockHealth.max_drawdown * 100).toFixed(2) : '--'"
              suffix="%"
            />
          </el-col>
          <el-col :span="12">
            <el-statistic
              title="回撤持续期"
              :value="currentStockHealth.max_drawdown_duration || '--'"
              suffix="天"
            />
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, List, TrendCharts, Bell, DataLine, Tickets,
  Delete, InfoFilled, Warning, CircleCheck, CircleClose
} from '@element-plus/icons-vue'
import HealthRadarChart from '@/components/chart/HealthRadarChart.vue'

// State
const loading = ref(false)
const activeTab = ref('watchlists')

// Data
const watchlists = ref([])
const selectedWatchlist = ref(null)
const watchlistStocks = ref([])
const portfolioSummary = ref({})
const radarScores = ref({ trend: 50, technical: 50, momentum: 50, volatility: 50, risk: 50 })
const allAlerts = ref([])
const alertSummary = ref({ critical: 0, warning: 0, info: 0 })
const rebalanceSuggestions = ref([])

// Dialogs
const createDialogVisible = ref(false)
const addStockDialogVisible = ref(false)
const healthDetailVisible = ref(false)
const editingWatchlist = ref(null)
const currentStock = ref(null)
const currentStockHealth = ref(null)

// Forms
const watchlistForm = reactive({
  name: '',
  watchlist_type: 'manual'
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

// API Base
const API_BASE = '/api/v1/monitoring'

// Load Functions
const loadWatchlists = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/watchlists?user_id=1`)
    const data = await res.json()
    if (data.success) {
      watchlists.value = data.data
      // Calculate portfolio summary
      if (data.data && data.data.length > 0) {
        const avgScore = data.data.reduce((sum, w) => sum + (w.total_score || 0), 0) / data.data.length
        portfolioSummary.value.total_score = avgScore
        portfolioSummary.value.position_count = data.data.reduce((sum, w) => sum + (w.stocks_count || 0), 0)
      }
    }
  } catch (error) {
    console.error('加载清单失败:', error)
    ElMessage.error('加载清单失败')
  } finally {
    loading.value = false
  }
}

const selectWatchlist = async (row) => {
  selectedWatchlist.value = row
  activeTab.value = 'analysis' // Switch to analysis tab to show radar chart
  await loadWatchlistDetails(row.id)
  await loadPortfolioAnalysis(row.id)
}

const loadWatchlistDetails = async (watchlistId) => {
  try {
    const res = await fetch(`${API_BASE}/watchlists/${watchlistId}/stocks`)
    const data = await res.json()
    if (data.success) {
      watchlistStocks.value = data.data
    }
  } catch (error) {
    console.error('加载持仓失败:', error)
  }
}

const loadPortfolioAnalysis = async (watchlistId) => {
  try {
    const [summaryRes, alertsRes, rebalanceRes] = await Promise.all([
      fetch(`${API_BASE}/analysis/portfolio/${watchlistId}/summary`),
      fetch(`${API_BASE}/analysis/portfolio/${watchlistId}/alerts`),
      fetch(`${API_BASE}/analysis/portfolio/${watchlistId}/rebalance`)
    ])

    const [summaryData, alertsData, rebalanceData] = await Promise.all([
      summaryRes.json(),
      alertsRes.json(),
      rebalanceRes.json()
    ])

    if (summaryData.success) {
      portfolioSummary.value = summaryData.data
      alertSummary.value = summaryData.data.alert_summary || { critical: 0, warning: 0, info: 0 }
    }

    if (alertsData.success) {
      allAlerts.value = alertsData.data || []
    }

    if (rebalanceData.success) {
      rebalanceSuggestions.value = rebalanceData.data || []
    }

    if (selectedWatchlist.value) {
      selectedWatchlist.value.total_score = summaryData.data?.total_score?.average
      selectedWatchlist.value.stocks_count = summaryData.data?.stocks_count
    }

    if (summaryData.data?.radar_averages) {
      radarScores.value = {
        trend: summaryData.data.radar_averages.trend || 50,
        technical: summaryData.data.radar_averages.technical || 50,
        momentum: summaryData.data.radar_averages.momentum || 50,
        volatility: summaryData.data.radar_averages.volatility || 50,
        risk: summaryData.data.radar_averages.risk || 50
      }
    }
  } catch (error) {
    console.error('加载组合分析失败:', error)
  }
}

// Watchlist CRUD
const showCreateWatchlist = () => {
  editingWatchlist.value = null
  watchlistForm.name = ''
  watchlistForm.watchlist_type = 'manual'
  riskTolerance.value = 50
  createDialogVisible.value = true
}

const handleCreateWatchlist = async () => {
  if (!watchlistForm.name) {
    ElMessage.warning('请输入清单名称')
    return
  }

  try {
    const url = editingWatchlist.value
      ? `${API_BASE}/watchlists/${editingWatchlist.value.id}`
      : `${API_BASE}/watchlists`
    const method = editingWatchlist.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(watchlistForm)
    })

    const data = await res.json()
    if (data.success) {
      ElMessage.success(editingWatchlist.value ? '更新成功' : '创建成功')
      createDialogVisible.value = false
      loadWatchlists()
    } else {
      ElMessage.error(data.message || '操作失败')
    }
  } catch (error) {
    console.error('保存清单失败:', error)
    ElMessage.error('操作失败')
  }
}

const deleteWatchlist = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除此清单？', '提示', { type: 'warning' })
    const res = await fetch(`${API_BASE}/watchlists/${id}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('删除成功')
      if (selectedWatchlist.value?.id === id) {
        selectedWatchlist.value = null
        watchlistStocks.value = []
        portfolioSummary.value = {}
      }
      loadWatchlists()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const manageStocks = (row) => {
  selectWatchlist(row)
}

// Stock Management
const showAddStock = () => {
  if (!selectedWatchlist.value) {
    ElMessage.warning('请先选择一个清单')
    return
  }
  stockForm.stock_code = ''
  stockForm.entry_price = null
  stockForm.entry_reason = null
  stockForm.stop_loss_price = null
  stockForm.target_price = null
  stockForm.weight = 0.1
  addStockDialogVisible.value = true
}

const handleAddStock = async () => {
  if (!stockForm.stock_code || !stockForm.entry_price) {
    ElMessage.warning('请填写股票代码和入库价格')
    return
  }

  try {
    const res = await fetch(`${API_BASE}/watchlists/${selectedWatchlist.value.id}/stocks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(stockForm)
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('添加成功')
      addStockDialogVisible.value = false
      await loadWatchlistDetails(selectedWatchlist.value.id)
      await loadPortfolioAnalysis(selectedWatchlist.value.id)
    } else {
      ElMessage.error(data.message || '添加失败')
    }
  } catch (error) {
    console.error('添加股票失败:', error)
    ElMessage.error('添加失败')
  }
}

const removeStock = async (stockId) => {
  try {
    await ElMessageBox.confirm('确定移除此股票？', '提示', { type: 'warning' })
    const res = await fetch(`${API_BASE}/watchlists/${selectedWatchlist.value.id}/stocks/${stockId}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('移除成功')
      await loadWatchlistDetails(selectedWatchlist.value.id)
      await loadPortfolioAnalysis(selectedWatchlist.value.id)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败')
    }
  }
}

// Health Calculation
const calculateHealth = async (stock) => {
  currentStock.value = stock
  try {
    const res = await fetch(`${API_BASE}/analysis/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        stock_code: stock.stock_code,
        close: stock.entry_price,
        market_regime: 'choppy'
      })
    })
    const data = await res.json()
    if (data.success) {
      currentStockHealth.value = data.data
      healthDetailVisible.value = true
    } else {
      ElMessage.error('计算失败')
    }
  } catch (error) {
    console.error('计算健康度失败:', error)
    ElMessage.error('计算失败')
  }
}

// Helper Functions
const getHealthColor = (score) => {
  if (!score) return '#909399'
  if (score >= 70) return '#67C23A'
  if (score >= 50) return '#E6A23C'
  return '#F56C6C'
}

const getRiskColor = (score) => {
  if (!score) return '#909399'
  if (score >= 70) return '#F56C6C'
  if (score >= 50) return '#E6A23C'
  return '#67C23A'
}

const getAlertColor = () => {
  const total = alertSummary.value.critical + alertSummary.value.warning + alertSummary.value.info
  if (alertSummary.value.critical > 0) return '#F56C6C'
  if (total > 0) return '#E6A23C'
  return '#67C23A'
}

const getTypeTagType = (type) => {
  const types = { manual: '', strategy: 'success', benchmark: 'info' }
  return types[type] || ''
}

const getTypeText = (type) => {
  const texts = { manual: '手动', strategy: '策略', benchmark: '基准' }
  return texts[type] || type
}

const getScoreClass = (score) => {
  if (!score) return ''
  if (score >= 70) return 'score-excellent'
  if (score >= 50) return 'score-good'
  return 'score-fair'
}

const getProgressColor = (score) => {
  if (score >= 70) return '#67C23A'
  if (score >= 50) return '#E6A23C'
  return '#F56C6C'
}

const getPriorityTagType = (priority) => {
  const types = { critical: 'danger', high: 'warning', medium: '' }
  return types[priority] || ''
}

const getAlertType = (level) => {
  const types = { critical: 'error', warning: 'warning', info: 'info' }
  return types[level] || 'info'
}

const getAlertTypeText = (type) => {
  const texts = {
    stop_loss: '止损触发',
    profit_target: '止盈目标',
    weight_drift: '权重偏离'
  }
  return texts[type] || type
}

const getHealthResultIcon = (score) => {
  if (!score) return undefined
  if (score >= 70) return CircleCheck
  if (score >= 50) return Warning
  return undefined
}

const getScoresTableData = () => {
  const labels = { trend: '趋势', technical: '技术', momentum: '动量', volatility: '波动', risk: '风险' }
  return Object.entries(radarScores.value).map(([key, value]) => ({
    label: labels[key] || key,
    score: value
  }))
}

onMounted(() => {
  loadWatchlists()
})
</script>

<style scoped lang="scss">
.portfolio-management {
  padding: 20px;

  .page-header {
    margin-bottom: 24px;

    h1 {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .stats-row {
    margin-bottom: 20px;

    .stat-card {
      :deep(.el-card__body) {
        padding: 20px;
      }

      .stat-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;

        .stat-value {
          font-size: 28px;
          font-weight: 600;
          line-height: 1;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
          flex: 1;
        }

        .stat-icon {
          font-size: 32px;
          opacity: 0.8;
        }
      }

      &.has-alert {
        animation: pulse 2s infinite;
      }
    }
  }

  .main-content {
    .portfolio-tabs {
      :deep(.el-tabs__header) {
        margin-bottom: 20px;
      }

      .tab-label {
        display: flex;
        align-items: center;
        gap: 6px;
      }

      .tab-actions {
        margin-bottom: 20px;
      }

      .watchlist-list {
        .watchlist-item {
          padding: 16px;
          border: 1px solid #EBEEF5;
          border-radius: 4px;
          margin-bottom: 12px;
          cursor: pointer;
          transition: all 0.3s;

          &:hover {
            border-color: #409EFF;
            background-color: #F5F7FA;
          }

          &.active {
            border-color: #409EFF;
            background-color: #ECF5FF;
          }

          .watchlist-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;

            .watchlist-name {
              font-size: 16px;
              font-weight: 600;
              color: #303133;
              margin: 0;
            }
          }

          .watchlist-metrics {
            display: flex;
            gap: 24px;
            margin-bottom: 12px;

            .metric {
              display: flex;
              gap: 8px;

              .metric-label {
                font-size: 12px;
                color: #909399;
              }

              .metric-value {
                font-weight: 600;
                color: #303133;
              }
            }
          }

          .watchlist-actions {
            display: flex;
            gap: 8px;
          }
        }
      }

      .analysis-content {
        .radar-section, .scores-section, .rebalance-section {
          margin-bottom: 32px;
          min-height: 400px; // Ensure container has height for chart rendering

          h3 {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
            margin: 0 0 16px 0;
          }
        }

        // Special handling for radar chart section
        .radar-section {
          display: flex;
          flex-direction: column;
          align-items: center;

          :deep(.health-radar-chart) {
            width: 100%;
            max-width: 500px;
          }
        }

        .score-excellent { color: #67C23A; }
        .score-good { color: #E6A23C; }
        .score-fair { color: #F56C6C; }

        .suggestion-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .stock-code {
            font-weight: 600;
            color: #303133;
          }
        }

        .suggestion-footer {
          display: flex;
          justify-content: space-between;
          margin-top: 12px;

          .cost-label { color: #909399; }
          .cost-value { font-weight: 600; color: #303133; }
        }
      }

      .alerts-content {
        .alerts-summary {
          display: flex;
          justify-content: space-around;
          margin-bottom: 24px;

          :deep(.el-statistic) {
            text-align: center;
          }
        }

        .alerts-list {
          .alert-item {
            margin-bottom: 12px;
          }
        }
      }
    }

    .detail-card {
      .detail-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        h2 {
          font-size: 20px;
          font-weight: 600;
          color: #303133;
          margin: 0;
        }
      }

      .detail-stats {
        display: flex;
        justify-content: space-around;
        margin-bottom: 16px;
      }

      .stock-cards {
        margin-top: 16px;

        .stock-card {
          margin-bottom: 12px;

          .stock-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;

            .stock-code {
              font-weight: 600;
              color: #303133;
            }
          }

          .stock-actions {
            margin-top: 12px;
            display: flex;
            gap: 8px;
          }
        }

        .add-stock-btn {
          width: 100%;
          margin-top: 16px;
        }
      }
    }
  }

  .text-success { color: #67C23A; }
  .text-danger { color: #F56C6C; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
