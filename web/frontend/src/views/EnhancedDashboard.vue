<template>
  <div class="dashboard">
    <!-- 统计卡片行 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="stat in stats" :key="stat.title">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: stat.color }">
              <el-icon :size="24"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-title">{{ stat.title }}</p>
              <h3 class="stat-value">{{ stat.value }}</h3>
              <span class="stat-trend" :class="stat.trendClass">
                {{ stat.trend }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 市场概览模块 -->
    <el-row :gutter="20" class="market-overview-section">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="flex-between">
              <span>市场概览</span>
              <el-button type="primary" size="small" @click="loadMarketOverview" :loading="loading.overview">
                刷新
              </el-button>
            </div>
          </template>
          <div class="market-overview-content">
            <!-- 全市场涨跌分布 -->
            <div class="overview-item">
              <h4>涨跌分布</h4>
              <div ref="priceDistributionChartRef" class="mini-chart"></div>
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
            <div class="flex-between">
              <span>个人关注股票</span>
              <div>
                <el-button type="success" size="small" @click="handleAddToWatchlist" :loading="loading.addWatchlist">
                  添加关注
                </el-button>
                <el-button type="primary" size="small" @click="loadWatchlist" :loading="loading.watchlist" style="margin-left: 8px">
                  刷新
                </el-button>
              </div>
            </div>
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

          <!-- 添加关注对话框 -->
          <el-dialog v-model="showAddDialog" title="添加关注股票" width="400px">
            <el-form :model="addForm" label-width="80px">
              <el-form-item label="股票代码">
                <el-input v-model="addForm.symbol" placeholder="请输入股票代码，如：600000"></el-input>
              </el-form-item>
              <el-form-item label="显示名称">
                <el-input v-model="addForm.display_name" placeholder="可选，默认使用股票代码"></el-input>
              </el-form-item>
            </el-form>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="showAddDialog = false">取消</el-button>
                <el-button type="primary" @click="confirmAddToWatchlist" :loading="loading.addWatchlist">
                  确认添加
                </el-button>
              </span>
            </template>
          </el-dialog>
        </el-card>
      </el-col>
    </el-row>

    <!-- 市场热度中心 -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="16">
        <el-card class="chart-card">
          <template #header>
            <div class="flex-between">
              <span>市场热度中心</span>
              <el-button type="warning" size="small" @click="handleRetry" :loading="loading.main">
                重试
              </el-button>
            </div>
          </template>
          <el-tabs v-model="activeMarketTab" class="market-tabs">
            <el-tab-pane label="市场热度" name="heat">
              <div ref="marketHeatChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="领涨板块" name="leading">
              <div ref="leadingSectorChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="涨跌分布" name="distribution">
              <div ref="capitalFlowChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="资金流向" name="capital">
              <div ref="capitalFlowChartRef2" style="height: 350px"></div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card class="chart-card">
          <template #header>
            <div class="flex-between">
              <span>资金流向</span>
              <el-select v-model="industryStandard" size="small" style="width: 120px" @change="updateIndustryChart">
                <el-option label="证监会" value="csrc" />
                <el-option label="申万一级" value="sw_l1" />
                <el-option label="申万二级" value="sw_l2" />
              </el-select>
            </div>
          </template>
          <div ref="industryChartRef" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 板块表现 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="flex-between">
              <span>板块表现</span>
              <div>
                <el-button type="primary" size="small" @click="handleRefresh">刷新</el-button>
                <el-button type="warning" size="small" @click="handleRetry" :loading="loading.main" style="margin-left: 10px">
                  重试
                </el-button>
              </div>
            </div>
          </template>
          <el-tabs v-model="activeSectorTab" class="sector-tabs">
            <el-tab-pane label="自选股" name="favorites">
              <el-table :data="favoriteStocks" stripe v-loading="loading.main" max-height="400">
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
              <el-table :data="strategyStocks" stripe v-loading="loading.main" max-height="400">
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
                    <el-tag :type="getSignalTagType(row.signal)" size="small">
                      {{ row.signal }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, reactive } from 'vue'
import { dataApi, dashboardApi } from '@/api'
import cacheManager from '@/utils/cache'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

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

// 图表引用
const marketHeatChartRef = ref(null)
const leadingSectorChartRef = ref(null)
const priceDistributionChartRef = ref(null)
const capitalFlowChartRef = ref(null)
const capitalFlowChartRef2 = ref(null)
const industryChartRef = ref(null)

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

// 图表实例
let marketHeatChart = null
let leadingSectorChart = null
let priceDistributionChart = null
let capitalFlowChart = null
let capitalFlowChart2 = null
let industryChart = null

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

// 缓存相关函数
const getCachedData = (funcName, params = {}) => {
  return cacheManager.get(funcName, params)
}

const setCachedData = (funcName, data, params = {}, ttl) => {
  cacheManager.set(funcName, data, params, ttl)
}

// API加载函数（使用缓存）
const loadMarketOverview = async () => {
  loading.overview.value = true
  try {
    const data = await cacheManager.withCache(
      async () => dashboardApi.getMarketOverview(),
      'marketOverview'
    )

    if (data.success && data.data) {
      const marketData = data.data

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
    loading.overview.value = false
  }
}

const loadPriceDistribution = async () => {
  try {
    const data = await cacheManager.withCache(
      async () => dashboardApi.getPriceDistribution(),
      'priceDistribution',
      {},
      1800000 // 30分钟缓存
    )

    if (data.success && data.data) {
      updatePriceDistributionChart(data.data)
    }
  } catch (error) {
    console.error('加载涨跌分布失败:', error)
  }
}

const loadHotIndustries = async () => {
  try {
    const data = await cacheManager.withCache(
      async () => dashboardApi.getHotIndustries(5),
      'hotIndustries',
      {},
      1800000 // 30分钟缓存
    )

    if (data.success && data.data) {
      hotIndustries.value = data.data
    }
  } catch (error) {
    console.error('加载热门行业失败:', error)
  }
}

const loadHotConcepts = async () => {
  try {
    const data = await cacheManager.withCache(
      async () => dashboardApi.getHotConcepts(5),
      'hotConcepts',
      {},
      1800000 // 30分钟缓存
    )

    if (data.success && data.data) {
      hotConcepts.value = data.data
    }
  } catch (error) {
    console.error('加载热门概念失败:', error)
  }
}

const loadWatchlist = async () => {
  loading.watchlist.value = true
  try {
    const data = await dashboardApi.getWatchlist()
    if (data && data.length > 0) {
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
    loading.watchlist.value = false
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

  loading.addWatchlist.value = true
  try {
    await dashboardApi.addToWatchlist({
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
    loading.addWatchlist.value = false
  }
}

const removeFromWatchlist = async (symbol) => {
  loading.removeWatchlist.value = true
  try {
    await dashboardApi.removeFromWatchlist(symbol)
    ElMessage.success('移除自选股成功')
    await loadWatchlist()
  } catch (error) {
    console.error('移除自选股失败:', error)
    ElMessage.error('移除自选股失败')
  } finally {
    loading.removeWatchlist.value = false
  }
}

// 图表初始化函数
const updatePriceDistributionChart = (distributionData) => {
  if (!priceDistributionChartRef.value) return

  if (priceDistributionChart) {
    priceDistributionChart.dispose()
  }

  priceDistributionChart = echarts.init(priceDistributionChartRef.value)

  const data = Object.entries(distributionData).map(([name, value]) => ({ name, value }))

  const option = {
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

  priceDistributionChart.setOption(option)
}

const initMarketHeatChart = async () => {
  if (!marketHeatChartRef.value) return

  marketHeatChart = echarts.init(marketHeatChartRef.value)

  try {
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

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
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
          data: heatData.map(item => item.value),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          },
          emphasis: {
            focus: 'series'
          }
        }
      ]
    }
    marketHeatChart.setOption(option)
  } catch (error) {
    console.error('加载市场热度数据失败:', error)
  }
}

const initLeadingSectorChart = async () => {
  if (!leadingSectorChartRef.value) return

  leadingSectorChart = echarts.init(leadingSectorChartRef.value)

  try {
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

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: '{b}: {c}%'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
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
          data: sectorData.map(item => item.change),
          itemStyle: {
            color: (params) => {
              return params.value > 0 ? '#f56c6c' : '#67c23a'
            }
          }
        }
      ]
    }
    leadingSectorChart.setOption(option)
  } catch (error) {
    console.error('加载领涨板块数据失败:', error)
  }
}

const initCapitalFlowChart = async () => {
  if (!capitalFlowChartRef.value) return

  capitalFlowChart = echarts.init(capitalFlowChartRef.value)

  try {
    const flowData = [
      { name: '主力资金', value: 120 },
      { name: '散户资金', value: -80 },
      { name: '机构资金', value: 90 },
      { name: '北向资金', value: 60 },
      { name: '南向资金', value: -30 },
      { name: '融资融券', value: 40 }
    ]

    const option = {
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
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
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
          data: flowData.map(item => item.value),
          itemStyle: {
            color: (params) => {
              return params.value > 0 ? '#f56c6c' : '#67c23a'
            }
          }
        }
      ]
    }
    capitalFlowChart.setOption(option)
  } catch (error) {
    console.error('加载资金流向数据失败:', error)
  }
}

const initIndustryChart = async () => {
  if (!industryChartRef.value) return

  industryChart = echarts.init(industryChartRef.value)

  try {
    const mockData = {
      categories: ['银行', '房地产', '医药生物', '食品饮料', '电子', '计算机', '机械', '化工', '汽车', '家电'],
      values: [120, -50, 80, 65, -30, 90, 45, -20, 70, 55]
    }

    const option = {
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
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '10%',
        containLabel: true
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
          itemStyle: {
            color: (params) => {
              return params.value > 0 ? '#f56c6c' : '#67c23a'
            }
          },
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
    industryChart.setOption(option)
  } catch (error) {
    console.error('加载行业资金流向数据失败:', error)
  }
}

const initCharts = async () => {
  await nextTick()

  // 初始化图表
  await initMarketHeatChart()
  await initLeadingSectorChart()
  await initCapitalFlowChart()
  await initIndustryChart()

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    marketHeatChart?.resize()
    leadingSectorChart?.resize()
    priceDistributionChart?.resize()
    capitalFlowChart?.resize()
    industryChart?.resize()
  })
}

// 事件处理函数
const handleRetry = async () => {
  try {
    cacheManager.clearAll()
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
  loading.main.value = true
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
    loading.main.value = false
  }
}

// 监听tab切换
import { watch } from 'vue'

watch(activeMarketTab, async () => {
  await nextTick()
  switch (activeMarketTab.value) {
    case 'heat':
      marketHeatChart?.resize()
      break
    case 'leading':
      leadingSectorChart?.resize()
      break
    case 'distribution':
      priceDistributionChart?.resize()
      break
    case 'capital':
      capitalFlowChart?.resize()
      break
  }
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
.dashboard {
  .stats-row {
    margin-bottom: 20px;

    .stat-card {
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .stat-info {
          flex: 1;

          .stat-title {
            margin: 0 0 8px;
            font-size: 14px;
            color: #909399;
          }

          .stat-value {
            margin: 0 0 8px;
            font-size: 24px;
            font-weight: bold;
            color: #303133;
          }

          .stat-trend {
            font-size: 12px;

            &.up {
              color: #67c23a;
            }

            &.down {
              color: #f56c6c;
            }

            &.neutral {
              color: #909399;
            }
          }
        }
      }
    }
  }

  .market-overview-section {
    margin-bottom: 20px;
  }

  .market-overview-content {
    .overview-item {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      h4 {
        margin: 0 0 10px;
        font-size: 16px;
        color: #303133;
        font-weight: 600;
      }

      .mini-chart {
        height: 150px;
        border: 1px solid #ebeef5;
        border-radius: 4px;
      }
    }
  }

  .watchlist-content {
    .el-table {
      .text-red {
        color: #f56c6c;
      }

      .text-green {
        color: #67c23a;
      }
    }
  }

  .chart-card {
    margin-bottom: 20px;

    .market-tabs {
      :deep(.el-tabs__content) {
        padding-top: 10px;
      }
    }
  }

  .sector-tabs {
    :deep(.el-tabs__content) {
      padding-top: 10px;
    }
  }

  .text-red {
    color: #f56c6c;
  }

  .text-green {
    color: #67c23a;
  }

  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}

.dialog-footer {
  .el-button {
    margin-left: 8px;
  }
}
</style>
