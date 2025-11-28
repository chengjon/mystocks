<template>
  <div class="trade-management">
    <!-- 资产概览 -->
    <el-row :gutter="16" class="overview-section">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总资产" :value="portfolio.total_assets" :precision="2">
            <template #prefix>¥</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="可用资金" :value="portfolio.available_cash" :precision="2">
            <template #prefix>¥</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="持仓市值" :value="portfolio.position_value" :precision="2">
            <template #prefix>¥</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic
            title="总盈亏"
            :value="portfolio.total_profit"
            :precision="2"
            :value-style="{ color: portfolio.total_profit >= 0 ? '#f56c6c' : '#67c23a' }"
          >
            <template #prefix>¥</template>
            <template #suffix>
              <span :style="{ fontSize: '14px' }">
                ({{ portfolio.profit_rate }}%)
              </span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- Tab切换 -->
    <el-card class="main-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <!-- 持仓管理 -->
        <el-tab-pane label="持仓管理" name="positions">
          <div class="tab-actions">
            <el-button type="primary" @click="openTradeDialog('buy')">
              <el-icon><Plus /></el-icon> 买入
            </el-button>
            <el-button type="danger" @click="openTradeDialog('sell')">
              <el-icon><Minus /></el-icon> 卖出
            </el-button>
            <el-button @click="refreshPositions" :loading="loading">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>

          <el-table :data="positions" v-loading="loading" stripe border style="margin-top: 16px">
            <el-table-column prop="symbol" label="股票代码" width="100" />
            <el-table-column prop="stock_name" label="股票名称" width="120" />
            <el-table-column prop="quantity" label="持仓数量" width="100" align="right" />
            <el-table-column label="成本价" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.cost_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="现价" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.current_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="持仓市值" width="120" align="right">
              <template #default="scope">
                ¥{{ (scope.row.quantity * scope.row.current_price).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="盈亏金额" width="120" align="right">
              <template #default="scope">
                <span :class="getProfitClass(scope.row.profit)">
                  ¥{{ scope.row.profit.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="盈亏比例" width="100" align="right">
              <template #default="scope">
                <span :class="getProfitClass(scope.row.profit_rate)">
                  {{ scope.row.profit_rate.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="update_time" label="更新时间" width="180" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button size="small" type="primary" @click="quickSell(scope.row)">
                  卖出
                </el-button>
                <el-button size="small" @click="viewPositionDetail(scope.row)">
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 交易记录 -->
        <el-tab-pane label="交易记录" name="trades">
          <div class="tab-actions">
            <el-form :inline="true" :model="tradeFilter">
              <el-form-item label="交易类型">
                <el-select v-model="tradeFilter.type" placeholder="全部" clearable style="width: 120px">
                  <el-option label="买入" value="buy" />
                  <el-option label="卖出" value="sell" />
                </el-select>
              </el-form-item>
              <el-form-item label="股票代码">
                <el-input v-model="tradeFilter.symbol" placeholder="股票代码" clearable style="width: 150px" />
              </el-form-item>
              <el-form-item label="日期范围">
                <el-date-picker
                  v-model="tradeFilter.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 260px"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadTrades">查询</el-button>
                <el-button @click="resetTradeFilter">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table :data="trades" v-loading="loading" stripe border style="margin-top: 16px">
            <el-table-column prop="trade_time" label="交易时间" width="180" />
            <el-table-column label="类型" width="80" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.type === 'buy' ? 'success' : 'danger'" size="small">
                  {{ scope.row.type === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="symbol" label="股票代码" width="100" />
            <el-table-column prop="stock_name" label="股票名称" width="120" />
            <el-table-column prop="quantity" label="数量" width="100" align="right" />
            <el-table-column label="价格" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="金额" width="120" align="right">
              <template #default="scope">
                ¥{{ (scope.row.quantity * scope.row.price).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="手续费" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.commission.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)" size="small">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
          </el-table>

          <el-pagination
            v-model:current-page="tradePagination.page"
            v-model:page-size="tradePagination.pageSize"
            :page-sizes="[20, 50, 100]"
            :total="tradePagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadTrades"
            @current-change="loadTrades"
            style="margin-top: 16px; justify-content: center"
          />
        </el-tab-pane>

        <!-- 盈亏统计 -->
        <el-tab-pane label="盈亏统计" name="statistics">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>资产趋势</span>
                </template>
                <div id="assets-chart" style="height: 300px"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>持仓盈亏分布</span>
                </template>
                <div id="profit-chart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card>
                <template #header>
                  <span>交易统计</span>
                </template>
                <el-descriptions :column="4" border>
                  <el-descriptions-item label="总交易次数">{{ statistics.total_trades }}</el-descriptions-item>
                  <el-descriptions-item label="买入次数">{{ statistics.buy_count }}</el-descriptions-item>
                  <el-descriptions-item label="卖出次数">{{ statistics.sell_count }}</el-descriptions-item>
                  <el-descriptions-item label="持仓股票数">{{ statistics.position_count }}</el-descriptions-item>
                  <el-descriptions-item label="累计买入金额">¥{{ statistics.total_buy_amount.toFixed(2) }}</el-descriptions-item>
                  <el-descriptions-item label="累计卖出金额">¥{{ statistics.total_sell_amount.toFixed(2) }}</el-descriptions-item>
                  <el-descriptions-item label="累计手续费">¥{{ statistics.total_commission.toFixed(2) }}</el-descriptions-item>
                  <el-descriptions-item label="实现盈亏">
                    <span :class="getProfitClass(statistics.realized_profit)">
                      ¥{{ statistics.realized_profit.toFixed(2) }}
                    </span>
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 交易对话框 -->
    <el-dialog v-model="tradeDialogVisible" :title="tradeForm.type === 'buy' ? '买入股票' : '卖出股票'" width="500px">
      <el-form :model="tradeForm" label-width="80px">
        <el-form-item label="股票代码">
          <el-input v-model="tradeForm.symbol" placeholder="如: 600519" />
        </el-form-item>
        <el-form-item label="股票名称">
          <el-input v-model="tradeForm.stock_name" placeholder="自动获取" readonly />
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="tradeForm.quantity" :min="100" :step="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="tradeForm.price" :min="0.01" :step="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="交易金额">
          <span style="color: #409eff">¥{{ (tradeForm.quantity * tradeForm.price).toFixed(2) }}</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="tradeForm.remark" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tradeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTrade" :loading="submitting">
          确认{{ tradeForm.type === 'buy' ? '买入' : '卖出' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Minus, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const activeTab = ref('positions')
const tradeDialogVisible = ref(false)

let assetsChartInstance = null
let profitChartInstance = null

// 投资组合数据
const portfolio = reactive({
  total_assets: 0,
  available_cash: 0,
  position_value: 0,
  total_profit: 0,
  profit_rate: 0
})

// 持仓数据
const positions = ref([])

// 交易记录
const trades = ref([])

// 交易过滤
const tradeFilter = reactive({
  type: '',
  symbol: '',
  dateRange: []
})

// 分页
const tradePagination = reactive({
  page: 1,
  pageSize: 20,
  total: 2
})

// 交易表单
const tradeForm = reactive({
  type: 'buy',
  symbol: '',
  stock_name: '',
  quantity: 100,
  price: 0,
  remark: ''
})

// 统计数据
const statistics = reactive({
  total_trades: 0,
  buy_count: 0,
  sell_count: 0,
  position_count: 0,
  total_buy_amount: 0,
  total_sell_amount: 0,
  total_commission: 0,
  realized_profit: 0
})

// 初始化数据 - onMounted 会调用
const initializeData = async () => {
  await Promise.all([loadPortfolio(), loadPositions(), loadStatistics(), loadTrades()])
}

// 加载投资组合概览
const loadPortfolio = async () => {
  try {
    const response = await api.get('/trade/portfolio')
    if (response.success && response.data) {
      Object.assign(portfolio, response.data)
    }
  } catch (error) {
    console.error('加载投资组合失败:', error)
  }
}

// 加载持仓列表
const loadPositions = async () => {
  try {
    const response = await api.get('/trade/positions')
    if (response.success && response.data) {
      positions.value = response.data
    }
  } catch (error) {
    console.error('加载持仓失败:', error)
  }
}

// 刷新持仓
const refreshPositions = async () => {
  loading.value = true
  try {
    await loadPositions()
    ElMessage.success('持仓数据已刷新')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

// 加载交易记录
const loadTrades = async () => {
  loading.value = true
  try {
    const params = {
      trade_type: tradeFilter.type || undefined,
      symbol: tradeFilter.symbol || undefined,
      page: tradePagination.page,
      page_size: tradePagination.pageSize
    }

    // 移除undefined参数
    Object.keys(params).forEach(key => params[key] === undefined && delete params[key])

    const response = await api.get('/trade/trades', { params })
    if (response.success && response.data) {
      trades.value = response.data
      tradePagination.total = response.total || 0
    }
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载交易记录失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const response = await api.get('/trade/statistics')
    if (response.success && response.data) {
      Object.assign(statistics, response.data)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 重置过滤
const resetTradeFilter = () => {
  tradeFilter.type = ''
  tradeFilter.symbol = ''
  tradeFilter.dateRange = []
  loadTrades()
}

// 打开交易对话框
const openTradeDialog = (type) => {
  tradeForm.type = type
  tradeForm.symbol = ''
  tradeForm.stock_name = ''
  tradeForm.quantity = 100
  tradeForm.price = 0
  tradeForm.remark = ''
  tradeDialogVisible.value = true
}

// 快速卖出
const quickSell = (position) => {
  tradeForm.type = 'sell'
  tradeForm.symbol = position.symbol
  tradeForm.stock_name = position.stock_name
  tradeForm.quantity = position.quantity
  tradeForm.price = position.current_price
  tradeForm.remark = '清仓'
  tradeDialogVisible.value = true
}

// 提交交易
const submitTrade = async () => {
  if (!tradeForm.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }
  if (!tradeForm.quantity || tradeForm.quantity <= 0) {
    ElMessage.warning('请输入有效数量')
    return
  }
  if (!tradeForm.price || tradeForm.price <= 0) {
    ElMessage.warning('请输入有效价格')
    return
  }

  submitting.value = true
  try {
    const tradeData = {
      type: tradeForm.type,
      symbol: tradeForm.symbol,
      quantity: tradeForm.quantity,
      price: tradeForm.price,
      remark: tradeForm.remark
    }

    const response = await api.post('/trade/execute', tradeData)
    if (response.success) {
      ElMessage.success(`${tradeForm.type === 'buy' ? '买入' : '卖出'}成功: ${response.data.trade_id}`)
      tradeDialogVisible.value = false
      // 刷新数据
      await Promise.all([loadPortfolio(), loadPositions(), loadStatistics(), loadTrades()])
    } else {
      ElMessage.error(response.message || '交易失败')
    }
  } catch (error) {
    console.error('交易失败:', error)
    ElMessage.error('交易失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

// 查看持仓详情
const viewPositionDetail = (position) => {
  ElMessageBox.alert(
    `持仓数量: ${position.quantity}\n成本价: ¥${position.cost_price}\n现价: ¥${position.current_price}\n盈亏: ¥${position.profit} (${position.profit_rate}%)`,
    `${position.stock_name} (${position.symbol})`,
    { confirmButtonText: '确定' }
  )
}

// Tab切换
const handleTabClick = async (tab) => {
  if (tab.paneName === 'statistics') {
    await nextTick()
    renderCharts()
  }
}

// 渲染图表
const renderCharts = () => {
  renderAssetsChart()
  renderProfitChart()
}

// 资产趋势图
const renderAssetsChart = () => {
  const chartDom = document.getElementById('assets-chart')
  if (!chartDom) return

  if (!assetsChartInstance) {
    assetsChartInstance = echarts.init(chartDom)
  }

  const dates = []
  const values = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 29)

  for (let i = 0; i < 30; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)
    dates.push(date.toISOString().slice(5, 10))
    values.push(1000000 + Math.random() * 100000)
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>总资产: ¥{c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '总资产',
        type: 'line',
        data: values,
        smooth: true,
        itemStyle: { color: '#409eff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        }
      }
    ]
  }

  assetsChartInstance.setOption(option)
}

// 盈亏分布图
const renderProfitChart = () => {
  const chartDom = document.getElementById('profit-chart')
  if (!chartDom) return

  if (!profitChartInstance) {
    profitChartInstance = echarts.init(chartDom)
  }

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '持仓盈亏',
        type: 'pie',
        radius: '60%',
        data: positions.value.map(p => ({
          name: p.stock_name,
          value: p.profit
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  profitChartInstance.setOption(option)
}

// 工具函数
const getProfitClass = (value) => {
  return value >= 0 ? 'profit-positive' : 'profit-negative'
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待成交',
    completed: '已成交',
    failed: '失败',
    cancelled: '已取消'
  }
  return texts[status] || status
}

// 窗口resize处理
const handleResize = () => {
  if (assetsChartInstance) {
    assetsChartInstance.resize()
  }
  if (profitChartInstance) {
    profitChartInstance.resize()
  }
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  await initializeData()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (assetsChartInstance) {
    assetsChartInstance.dispose()
  }
  if (profitChartInstance) {
    profitChartInstance.dispose()
  }
})
</script>

<style scoped lang="scss">
.trade-management {
  .overview-section {
    margin-bottom: 16px;
  }

  .main-card {
    .tab-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;
    }
  }

  .profit-positive {
    color: #f56c6c;
    font-weight: 500;
  }

  .profit-negative {
    color: #67c23a;
    font-weight: 500;
  }
}
</style>
