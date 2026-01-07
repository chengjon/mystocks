<template>
  <div class="enhanced-dashboard">

    <div class="page-header">
      <h1 class="page-title">ENHANCED DASHBOARD</h1>
      <p class="page-subtitle">MARKET OVERVIEW | WATCHLIST | SECTOR PERFORMANCE</p>
    </div>

    <div class="stats-grid">
      <el-col :xs="24" :sm="12" :md="6" v-for="stat in stats" :key="stat.title">
          :title="stat.title"
          :value="stat.value"
          :icon="getIconComponent(stat.icon)"
          :color="getColorType(stat.color)"
          :trend="stat.trend"
          :trend-up="stat.trendClass === 'up'"
          hoverable
        />
    </div>

    <div class="market-grid">
      <el-card class="chart-card">
          <template #header>
            <PageHeader
              title="市场概览"
              :actions="[{ text: '刷新', variant: 'primary', handler: loadMarketOverview }]"
              :show-divider="false"
            />
          </template>
          <div class="market-overview-content">
            <!-- 全市场涨跌分布 -->
            <div class="overview-item">
              <h4>涨跌分布</h4>
              <ChartContainer
                ref="priceDistributionChartRef"
                chart-type="pie"
                :data="priceDistributionData"
                :options="priceDistributionOptions"
                height="150px"
                :loading="loading.overview"
              />
            </div>

            <!-- 热门行业TOP5 -->
            <div class="overview-item">
              <h4>热门行业 TOP5</h4>
              <el-table :data="hotIndustries" size="small" max-height="250">
                <el-table-column prop="industry_name" label="行业" width="80" />
                <el-table-column prop="avg_change" label="平均涨幅" width="80">
                  <template #default="{ row }">
                    <span :class="row.avg_change > 0 ? 'text-red' : 'text-green'">
                      {{ row.avg_change > 0 ? '+' : '' }}{{ row.avg_change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="stock_count" label="股票数" width="60" />
              </el-table>
            </div>

            <!-- 热门概念TOP5 -->
            <div class="overview-item">
              <h4>热门概念 TOP5</h4>
              <el-table :data="hotConcepts" size="small" max-height="250">
                <el-table-column prop="concept_name" label="概念" width="80" />
                <el-table-column prop="avg_change" label="平均涨幅" width="80">
                  <template #default="{ row }">
                    <span :class="row.avg_change > 0 ? 'text-red' : 'text-green'">
                      {{ row.avg_change > 0 ? '+' : '' }}{{ row.avg_change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="stock_count" label="股票数" width="60" />
              </el-table>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <PageHeader
              title="个人关注股票"
              subtitle="自选股管理"
              :actions="[
                { text: '添加关注', variant: 'success', handler: handleAddToWatchlist },
                { text: '刷新', variant: 'primary', handler: loadWatchlist }
              ]"
              :show-divider="false"
            />
          </template>

          <!-- 个人关注股票列表 -->
          <div class="watchlist-content">
            <el-table
              :data="watchlistStocks"
              stripe
              v-loading="loading.watchlist"
              max-height="400"
              empty-text="暂无关注股票，点击添加按钮开始关注"
            >
              <el-table-column prop="symbol" label="代码" width="100" />
              <el-table-column prop="display_name" label="名称" width="120" />
              <el-table-column prop="price" label="现价" width="80" align="right">
                <template #default="{ row }">
                  <span :class="getPriceChangeClass(row.change)">
                    {{ row.price || '--' }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change" label="涨跌幅" width="100" align="right">
                <template #default="{ row }">
                  <span :class="getPriceChangeClass(row.change)">
                    {{ formatPriceChange(row.change) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" width="100" align="right">
                <template #default="{ row }">
                  {{ formatVolume(row.volume) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeFromWatchlist(row.symbol)"
                    :loading="loading.removeWatchlist"
                  >
                    移除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 添加关注对话框 - 使用 DetailDialog -->
          <DetailDialog
            v-model:visible="showAddDialog"
            title="添加关注股票"
            :confirming="loading.addWatchlist"
            @confirm="confirmAddToWatchlist"
          >
            <el-form :model="addForm" label-width="80px">
              <el-form-item label="股票代码">
                <el-input v-model="addForm.symbol" placeholder="请输入股票代码，如：600000"></el-input>
              </el-form-item>
              <el-form-item label="显示名称">
                <el-input v-model="addForm.display_name" placeholder="可选，默认使用股票代码"></el-input>
              </el-form-item>
            </el-form>
          </DetailDialog>
        </el-card>
      </div>

      <el-card class="chart-card">
          <template #header>
            <PageHeader
              title="个人关注股票"
              subtitle="自选股管理"
              :actions="[
                { text: '添加关注', variant: 'success', handler: handleAddToWatchlist },
                { text: '刷新', variant: 'primary', handler: loadWatchlist }
              ]"
              :show-divider="false"
            />
          </template>

          <div class="watchlist-content">
            <el-table
              :data="watchlistStocks"
              v-loading="loading.watchlist"
              empty-text="暂无关注股票，点击添加按钮开始关注"
            >
              <el-table-column prop="symbol" label="代码" width="100" />
              <el-table-column prop="display_name" label="名称" width="120" />
              <el-table-column prop="price" label="现价" width="80" align="right">
                <template #default="{ row }">
                  <span :class="getPriceChangeClass(row.change)">
                    {{ row.price || '--' }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change" label="涨跌幅" width="100" align="right">
                <template #default="{ row }">
                  <span :class="getPriceChangeClass(row.change)">
                    {{ formatPriceChange(row.change) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" width="100" align="right">
                <template #default="{ row }">
                  {{ formatVolume(row.volume) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button type="danger" size="small" @click="removeFromWatchlist(row.symbol)" :loading="loading.removeWatchlist">
                    移除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <DetailDialog
            v-model:visible="showAddDialog"
            title="添加关注股票"
            :confirming="loading.addWatchlist"
            @confirm="confirmAddToWatchlist"
          >
            <el-form :model="addForm" label-width="80px">
              <el-form-item label="股票代码">
                <el-input v-model="addForm.symbol" placeholder="请输入股票代码，如：600000" />
              </el-form-item>
              <el-form-item label="显示名称">
                <el-input v-model="addForm.display_name" placeholder="可选，默认使用股票代码" />
              </el-form-item>
            </el-form>
          </DetailDialog>
        </el-card>
      </div>
    </div>

    <div class="content-grid-16-8">
      <el-card class="chart-card">
            <template #header>
              <PageHeader
                title="市场热度中心"
                :actions="[{ text: '重试', variant: 'warning', handler: handleRetry }]"
                :show-divider="false"
              />
            </template>
            <el-tabs v-model="activeMarketTab" class="tabs">
              <el-tab-pane label="市场热度" name="heat">
                <ChartContainer
                  ref="marketHeatChartRef"
                  chart-type="bar"
                  :data="marketHeatData"
                  :options="marketHeatOptions"
                  height="350px"
                />
              </el-tab-pane>
              <el-tab-pane label="领涨板块" name="leading">
                <ChartContainer
                  ref="leadingSectorChartRef"
                  chart-type="bar"
                  :data="leadingSectorData"
                  :options="leadingSectorOptions"
                  height="350px"
                />
              </el-tab-pane>
              <el-tab-pane label="涨跌分布" name="distribution">
                <ChartContainer
                  ref="capitalFlowChartRef"
                  chart-type="bar"
                  :data="capitalFlowData"
                  :options="capitalFlowOptions"
                  height="350px"
                />
              </el-tab-pane>
              <el-tab-pane label="资金流向" name="capital">
                <ChartContainer
                  ref="capitalFlowChartRef2"
                  chart-type="bar"
                  :data="capitalFlowData2"
                  :options="capitalFlowOptions2"
                  height="350px"
                />
              </el-tab-pane>
            </el-tabs>
          </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="flex-between">
            <PageHeader
              title="资金流向"
              subtitle="行业分析"
              :show-divider="false"
            />
            <el-select v-model="industryStandard" size="small" class="select-sm">
              <el-option label="证监会" value="csrc" />
              <el-option label="申万一级" value="sw_l1" />
              <el-option label="申万二级" value="sw_l2" />
            </el-select>
          </div>
        </template>
        <ChartContainer
          ref="industryChartRef"
          chart-type="bar"
          :data="industryData"
          :options="industryOptions"
          height="400px"
        />
      </el-card>
    </div>

    <el-card class="chart-card">
      <template #header>
        <PageHeader
          title="板块表现"
          :actions="[
            { text: '刷新', variant: 'primary', handler: handleRefresh },
            { text: '重试', variant: 'warning', handler: handleRetry }
          ]"
          :show-divider="false"
        />
      </template>
      <el-tabs v-model="activeSectorTab" class="tabs">
        <el-tab-pane label="自选股" name="favorites">
          <el-table :data="favoriteStocks" v-loading="loading.main" empty-text="暂无数据">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="price" label="现价" width="100" align="right">
              <template #default="{ row }">
                <span :class="getPriceChangeClass(row.change)">
                  {{ row.price }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌幅" width="100" align="right">
              <template #default="{ row }">
                <span :class="getPriceChangeClass(row.change)">
                  {{ formatPriceChange(row.change) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="成交量" width="120" align="right" />
            <el-table-column prop="turnover" label="换手率" width="100" align="right">
              <template #default="{ row }">{{ row.turnover }}%</template>
            </el-table-column>
            <el-table-column prop="industry" label="所属行业" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="策略选股" name="strategy">
          <el-table :data="strategyStocks" v-loading="loading.main" empty-text="暂无数据">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="price" label="现价" width="100" align="right">
              <template #default="{ row }">
                <span :class="getPriceChangeClass(row.change)">
                  {{ row.price }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌幅" width="100" align="right">
              <template #default="{ row }">
                <span :class="getPriceChangeClass(row.change)">
                  {{ formatPriceChange(row.change) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="strategy" label="策略名称" width="120" />
            <el-table-column prop="score" label="评分" width="80" align="right" />
            <el-table-column prop="signal" label="信号" width="100">
              <template #default="{ row }">
                <el-tag :type="getSignalTagType(row.signal)">
                  {{ row.signal }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, reactive, watch } from 'vue'
import { dataApi, watchlistApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Document, Money, PieChart, Grid } from '@element-plus/icons-vue'

// 响应式数据
const loading = reactive({
  main: false,
  overview: false,
  watchlist: false,
  addWatchlist: false,
  removeWatchlist: false
})

const activeMarketTab = ref('heat')
const activeSectorTab = ref('favorites')
const industryStandard = ref('csrc')

// 图表数据（为ChartContainer准备）
const priceDistributionData = ref([])
const priceDistributionOptions = ref({})
const marketHeatData = ref([])
const marketHeatOptions = ref({})
const leadingSectorData = ref([])
const leadingSectorOptions = ref({})
const capitalFlowData = ref([])
const capitalFlowOptions = ref({})
const capitalFlowData2 = ref([])
const capitalFlowOptions2 = ref({})
const industryData = ref([])
const industryOptions = ref({})

// 页面数据
const stats = ref([
  { title: '总股票数', value: '0', icon: 'Document', color: '#409EFF', trend: '+0%', trendClass: 'neutral' },
  { title: '总市值', value: '0', icon: 'Money', color: '#67C23A', trend: '+0%', trendClass: 'up' },
  { title: '市场分布', value: '0', icon: 'PieChart', color: '#E6A23C', trend: '+0%', trendClass: 'up' },
  { title: '行业分布', value: '0', icon: 'Grid', color: '#F56C6C', trend: '+0%', trendClass: 'down' }
])

const hotIndustries = ref([])
const hotConcepts = ref([])
const watchlistStocks = ref([])
const favoriteStocks = ref([])
const strategyStocks = ref([])

// 添加关注对话框
const showAddDialog = ref(false)
const addForm = ref({
  symbol: '',
  display_name: ''
})

// 工具函数 - 图标组件映射
const getIconComponent = (iconName: string) => {
  const iconMap = {
    'Document': Document,
    'Money': Money,
    'PieChart': PieChart,
    'Grid': Grid
  }
  return iconMap[iconName] || Document
}

// 工具函数 - 颜色类型映射
const getColorType = (color: string) => {
  if (color === '#67C23A') return 'green'
  if (color === '#F56C6C') return 'red'
  if (color === '#E6A23C') return 'orange'
  if (color === '#409EFF') return 'blue'
  return 'gold'
}

// 工具函数
const getPriceChangeClass = (change) => {
  if (change > 0) return 'text-red'
  if (change < 0) return 'text-green'
  return ''
}

const formatPriceChange = (change) => {
  if (change === undefined || change === null) return '--'
  return `${change > 0 ? '+' : ''}${change}%`
}

const formatVolume = (volume) => {
  if (!volume) return '--'
  if (volume >= 10000) {
    return `${(volume / 10000).toFixed(1)}万`
  }
  return volume.toString()
}

const getSignalTagType = (signal) => {
  if (signal === '买入') return 'danger'
  if (signal === '卖出') return 'success'
  return 'info'
}

// API加载函数
const loadMarketOverview = async () => {
  loading.overview = true
  try {
    const response = await dataApi.getMarketOverview()

    if (response && response.data) {
      const marketData = response.data

      // 更新统计卡片数据
      stats.value[0].value = marketData.total_stocks?.toString() || '0'
      stats.value[1].value = marketData.total_stocks?.toString() || '0'

      if (marketData.by_market) {
        const marketEntries = Object.entries(marketData.by_market)
        if (marketEntries.length > 0) {
          const [market, count] = marketEntries[0]
          stats.value[2].value = `${market}: ${count}`
        }
      }

      if (marketData.by_industry) {
        const industryEntries = Object.entries(marketData.by_industry)
        if (industryEntries.length > 0) {
          const [industry, count] = industryEntries[0]
          stats.value[3].value = `${industry}: ${count}`
        }
      }
    }

    // 加载涨跌分布
    await loadPriceDistribution()

    // 加载热门行业和概念
    await Promise.all([
      loadHotIndustries(),
      loadHotConcepts()
    ])

  } catch (error) {
    console.error('加载市场概览失败:', error)
    ElMessage.error('加载市场概览失败')
  } finally {
    loading.overview = false
  }
}

const loadPriceDistribution = async () => {
  try {
    // 涨跌分布数据暂时模拟
    const mockData = { '上涨': 120, '下跌': 80, '平盘': 50 }
    updatePriceDistributionChart(mockData)
  } catch (error) {
    console.error('加载涨跌分布失败:', error)
  }
}

const loadHotIndustries = async () => {
  try {
    // 模拟热门行业数据
    hotIndustries.value = [
      { industry_name: '半导体', avg_change: 5.2, stock_count: 45 },
      { industry_name: '新能源车', avg_change: 4.8, stock_count: 38 },
      { industry_name: '光伏', avg_change: 4.5, stock_count: 32 },
      { industry_name: '医药', avg_change: 3.9, stock_count: 56 },
      { industry_name: '白酒', avg_change: 3.6, stock_count: 18 }
    ]
  } catch (error) {
    console.error('加载热门行业失败:', error)
  }
}

const loadHotConcepts = async () => {
  try {
    // 模拟热门概念数据
    hotConcepts.value = [
      { concept_name: '人工智能', avg_change: 6.2, stock_count: 62 },
      { concept_name: '芯片', avg_change: 5.8, stock_count: 48 },
      { concept_name: '锂电池', avg_change: 5.1, stock_count: 35 },
      { concept_name: '碳中和', avg_change: 4.3, stock_count: 89 },
      { concept_name: '元宇宙', avg_change: 3.9, stock_count: 27 }
    ]
  } catch (error) {
    console.error('加载热门概念失败:', error)
  }
}

const loadWatchlist = async () => {
  loading.watchlist = true
  try {
    const response = await watchlistApi.getWatchlist()
    const data = response.data || []
    if (data.length > 0) {
      watchlistStocks.value = data.map(item => ({
        symbol: item.symbol,
        display_name: item.display_name || item.symbol,
        price: '--',
        change: 0,
        volume: 0
      }))
    } else {
      watchlistStocks.value = []
    }
  } catch (error) {
    console.error('加载自选股失败:', error)
    watchlistStocks.value = []
  } finally {
    loading.watchlist = false
  }
}

const loadFavoriteStocks = async () => {
  try {
    // 这里应该从数据库或API加载自选股数据
    // 暂时使用模拟数据
    favoriteStocks.value = [
      {
        symbol: '000001',
        name: '平安银行',
        price: 12.50,
        change: 2.1,
        volume: 123456,
        turnover: 1.2,
        industry: '银行'
      },
      {
        symbol: '600000',
        name: '浦发银行',
        price: 8.90,
        change: -1.5,
        volume: 234567,
        turnover: 0.8,
        industry: '银行'
      }
    ]
  } catch (error) {
    console.error('加载自选股失败:', error)
  }
}

const loadStrategyStocks = async () => {
  try {
    // 这里应该从数据库或API加载策略选股数据
    // 暂时使用模拟数据
    strategyStocks.value = [
      {
        symbol: '300750',
        name: '宁德时代',
        price: 245.60,
        change: 5.2,
        strategy: '新能源策略',
        score: 85,
        signal: '买入'
      },
      {
        symbol: '002415',
        name: '海康威视',
        price: 32.80,
        change: -2.1,
        strategy: 'AI策略',
        score: 78,
        signal: '持有'
      }
    ]
  } catch (error) {
    console.error('加载策略选股失败:', error)
  }
}

// 自选股操作函数
const handleAddToWatchlist = () => {
  addForm.value = {
    symbol: '',
    display_name: ''
  }
  showAddDialog.value = true
}

const confirmAddToWatchlist = async () => {
  if (!addForm.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  loading.addWatchlist = true
  try {
    await watchlistApi.addToWatchlist({
      symbol: addForm.value.symbol.toUpperCase(),
      display_name: addForm.value.display_name
    })

    ElMessage.success('添加自选股成功')
    showAddDialog.value = false
    await loadWatchlist()
  } catch (error) {
    console.error('添加自选股失败:', error)
    ElMessage.error('添加自选股失败')
  } finally {
    loading.addWatchlist = false
  }
}

const removeFromWatchlist = async (symbol) => {
  loading.removeWatchlist = true
  try {
    await watchlistApi.removeFromWatchlist(symbol)
    ElMessage.success('移除自选股成功')
    await loadWatchlist()
  } catch (error) {
    console.error('移除自选股失败:', error)
    ElMessage.error('移除自选股失败')
  } finally {
    loading.removeWatchlist = false
  }
}

// 图表初始化函数（更新数据给ChartContainer）
const updatePriceDistributionChart = (distributionData) => {
  const data = Object.entries(distributionData).map(([name, value]) => ({ name, value }))
  priceDistributionData.value = data
  priceDistributionOptions.value = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}只 ({d}%)'
    },
    legend: {
      bottom: '5%',
      left: 'center'
    },
    series: [
      {
        name: '涨跌分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}只'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: data
      }
    ]
  }
}

const initMarketHeatChart = async () => {
  const heatData = [
    { name: '上证指数', value: 95 },
    { name: '深证成指', value: 88 },
    { name: '创业板指', value: 82 },
    { name: '沪深300', value: 91 },
    { name: '中证500', value: 78 },
    { name: '中证1000', value: 72 },
    { name: '科创板', value: 85 },
    { name: '新三板', value: 65 }
  ]

  marketHeatData.value = heatData
  marketHeatOptions.value = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'value',
      name: '热度指数'
    },
    yAxis: {
      type: 'category',
      data: heatData.map(item => item.name)
    },
    series: [
      {
        name: '市场热度',
        type: 'bar',
        data: heatData.map(item => item.value)
      }
    ]
  }
}

const initLeadingSectorChart = async () => {
  const sectorData = [
    { name: '半导体', change: 5.2 },
    { name: '新能源车', change: 4.8 },
    { name: '光伏', change: 4.5 },
    { name: '医药', change: 3.9 },
    { name: '白酒', change: 3.6 },
    { name: '银行', change: 2.8 },
    { name: '保险', change: 2.5 },
    { name: '证券', change: 2.1 }
  ]

  leadingSectorData.value = sectorData
  leadingSectorOptions.value = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}: {c}%'
    },
    xAxis: {
      type: 'value',
      name: '涨幅(%)',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    yAxis: {
      type: 'category',
      data: sectorData.map(item => item.name)
    },
    series: [
      {
        name: '涨幅',
        type: 'bar',
        data: sectorData.map(item => item.change)
      }
    ]
  }
}

const initCapitalFlowChart = async () => {
  const flowData = [
    { name: '主力资金', value: 120 },
    { name: '散户资金', value: -80 },
    { name: '机构资金', value: 90 },
    { name: '北向资金', value: 60 },
    { name: '南向资金', value: -30 },
    { name: '融资融券', value: 40 }
  ]

  capitalFlowData.value = flowData
  capitalFlowOptions.value = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const value = params[0].value
        const absValue = Math.abs(value)
        return `${params[0].name}: ${value > 0 ? '+' : ''}${value}亿 (${value > 0 ? '流入' : '流出'})`
      }
    },
    xAxis: {
      type: 'value',
      name: '资金流向(亿元)',
      axisLabel: {
        formatter: (value) => value > 0 ? `+${value}` : value
      }
    },
    yAxis: {
      type: 'category',
      data: flowData.map(item => item.name)
    },
    series: [
      {
        name: '资金流向',
        type: 'bar',
        data: flowData.map(item => item.value)
      }
    ]
  }
}

const initCapitalFlowChart2 = async () => {
  const flowData = [
    { name: '主力资金', value: 150 },
    { name: '散户资金', value: -90 },
    { name: '机构资金', value: 110 }
  ]

  capitalFlowData2.value = flowData
  capitalFlowOptions2.value = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const value = params[0].value
        return `${params[0].name}: ${value > 0 ? '+' : ''}${value}亿`
      }
    },
    xAxis: {
      type: 'value',
      name: '资金流向(亿元)'
    },
    yAxis: {
      type: 'category',
      data: flowData.map(item => item.name)
    },
    series: [
      {
        name: '资金流向',
        type: 'bar',
        data: flowData.map(item => item.value)
      }
    ]
  }
}

const initIndustryChart = async () => {
  const mockData = {
    categories: ['银行', '房地产', '医药生物', '食品饮料', '电子', '计算机', '机械', '化工', '汽车', '家电'],
    values: [120, -50, 80, 65, -30, 90, 45, -20, 70, 55]
  }

  industryData.value = mockData.categories.map((name, index) => ({
    name,
    value: mockData.values[index]
  }))

  industryOptions.value = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const value = params[0].value
        return `${params[0].name}: ${value > 0 ? '+' : ''}${value}亿`
      }
    },
    xAxis: {
      type: 'value',
      name: '资金流向(亿元)',
      axisLabel: {
        formatter: (value) => value > 0 ? `+${value}` : value
      }
    },
    yAxis: {
      type: 'category',
      data: mockData.categories,
      axisLabel: {
        interval: 0,
        fontSize: 11
      }
    },
    series: [
      {
        name: '资金流向',
        type: 'bar',
        data: mockData.values,
        label: {
          show: true,
          position: 'right',
          formatter: (params) => {
            const value = params.value
            return value > 0 ? `+${value}亿` : `${value}亿`
          },
          fontSize: 10
        }
      }
    ]
  }
}

const initCharts = async () => {
  await nextTick()

  // 初始化图表数据
  await initMarketHeatChart()
  await initLeadingSectorChart()
  await initCapitalFlowChart()
  await initCapitalFlowChart2()
  await initIndustryChart()
}

// 事件处理函数
const handleRetry = async () => {
  try {
    // Clear cache and reload data
    await loadData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败，请稍后重试')
  }
}

const handleRefresh = () => {
  ElMessage.success('数据已刷新')
  loadData()
}

const loadData = async () => {
  loading.main = true
  try {
    await Promise.all([
      loadMarketOverview(),
      loadFavoriteStocks(),
      loadStrategyStocks(),
      loadWatchlist()
    ])
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.main = false
  }
}

const updateIndustryChart = async () => {
  await initIndustryChart()
}

// 监听tab切换
watch(activeMarketTab, async () => {
  await nextTick()
  // ChartContainer 会自动处理 resize
})

watch(industryStandard, async () => {
  await initIndustryChart()
})

// 组件挂载时执行
onMounted(() => {
  initCharts()
  loadData()
})
</script>

<style scoped lang="scss">

  min-height: 100vh;
  padding: var(--spacing-6);
  position: relative;
  background: var(--bg-primary);

    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.04;
    background-image:
      repeating-linear-gradient(
        45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      ),
      repeating-linear-gradient(
        -45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      );
  }

  .page-header {
    margin-bottom: var(--spacing-6);
    position: relative;
    z-index: 1;

    .page-title {
      font-family: var(--font-display);
      font-size: var(--font-size-h2);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-widest);
      color: var(--accent-gold);
      margin: 0 0 var(--spacing-2) 0;
    }

    .page-subtitle {
      font-family: var(--font-body);
      font-size: var(--font-size-small);
      color: var(--fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      margin: 0;
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-6);
    margin-bottom: var(--spacing-6);
    position: relative;
    z-index: 1;
  }

    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-6);
    margin-bottom: var(--spacing-6);
    position: relative;
    z-index: 1;
  }

  .content-grid-16-8 {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--spacing-6);
    margin-bottom: var(--spacing-6);
    position: relative;
    z-index: 1;
  }

  .market-overview-content {
    .overview-item {
      margin-bottom: var(--spacing-6);

      &:last-child {
        margin-bottom: 0;
      }

      h4 {
        margin: 0 0 var(--spacing-3);
        font-family: var(--font-display);
        font-size: var(--font-size-body);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wider);
        color: var(--accent-gold);
      }
    }
  }

  .watchlist-content {
    :deep(.el-table) {
      .text-red {
        color: var(--color-up);
      }

      .text-green {
        color: var(--color-down);
      }
    }
  }

  .chart-card {
    margin-bottom: var(--spacing-6);
  }

  .tabs {
    :deep(.el-tabs__content) {
      padding-top: var(--spacing-4);
    }
  }

  .text-red {
    color: var(--color-up);
  }

  .text-green {
    color: var(--color-down);
  }

  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .select-sm {
    width: 120px;
  }

    background: var(--color-up);
    border-color: var(--color-up);
    color: white;

    &:hover {
      background: #D94F51;
      border-color: #D94F51;
    }
  }
}
</style>
