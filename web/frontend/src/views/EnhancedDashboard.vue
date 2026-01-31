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
import { watchlistApi } from '@/api' // Keep watchlistApi as it's separate
import { dashboardService } from '@/services/dashboardService' // Import new service
import { ElMessage } from 'element-plus'
import { Document, Money, PieChart, Grid } from '@element-plus/icons-vue'
import type { WatchlistItem } from '@/api/types/common' // Import existing type

// TypeScript 类型定义
interface StockData {
  symbol: string
  name: string
  price: number
  change: number
  volume?: number
  turnover?: number
  industry?: string
}

interface StrategyStock {
  symbol: string
  name: string
  price: number
  change: number
  strategy: string
  score: number
  signal: string
}

interface ChartDataPoint {
  name: string
  value: number
}

interface ChartOptions {
  [key: string]: any // Allow any chart options (xAxis, yAxis, tooltip, legend, series, etc.)
}

interface StatItem {
  title: string
  value: string
  icon: any
  color: string
  trend: string
  trendClass: string
}

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
const priceDistributionData = ref<ChartDataPoint[]>([])
const priceDistributionOptions = ref<ChartOptions>({})
const marketHeatData = ref<ChartDataPoint[]>([])
const marketHeatOptions = ref<ChartOptions>({})
const leadingSectorData = ref<ChartDataPoint[]>([])
const leadingSectorOptions = ref<ChartOptions>({})
const capitalFlowData = ref<ChartDataPoint[]>([])
const capitalFlowOptions = ref<ChartOptions>({})
const capitalFlowData2 = ref<ChartDataPoint[]>([])
const capitalFlowOptions2 = ref<ChartOptions>({})
const industryData = ref<ChartDataPoint[]>([])
const industryOptions = ref<ChartOptions>({})

// 页面数据
const stats = ref<StatItem[]>([
  { title: '总股票数', value: '0', icon: Document, color: '#409EFF', trend: '+0%', trendClass: 'neutral' },
  { title: '总市值', value: '0', icon: Money, color: '#67C23A', trend: '+0%', trendClass: 'up' },
  { title: '市场分布', value: '0', icon: PieChart, color: '#E6A23C', trend: '+0%', trendClass: 'up' },
  { title: '行业分布', value: '0', icon: Grid, color: '#F56C6C', trend: '+0%', trendClass: 'down' }
])

const hotIndustries = ref<Array<{ industry_name: string; avg_change: number; stock_count: number }>>([])
const hotConcepts = ref<Array<{ concept_name: string; avg_change: number; stock_count: number }>>([])
const watchlistStocks = ref<StockData[]>([])
const favoriteStocks = ref<StockData[]>([])
const strategyStocks = ref<StrategyStock[]>([])

// 添加关注对话框
const showAddDialog = ref(false)
const addForm = ref({
  symbol: '',
  display_name: ''
})

// 工具函数 - 图标组件映射
const getIconComponent = (iconComponent: any): any => {
  // Directly return the imported component
  return iconComponent
}

// 工具函数 - 颜色类型映射
const getColorType = (color: string): string => {
  if (color === '#67C23A') return 'green'
  if (color === '#F56C6C') return 'red'
  if (color === '#E6A23C') return 'orange'
  if (color === '#409EFF') return 'blue'
  return 'gold'
}

// 工具函数
const getPriceChangeClass = (change: number): string => {
  if (change > 0) return 'text-red'
  if (change < 0) return 'text-green'
  return ''
}

const formatPriceChange = (change: number | undefined | null): string => {
  if (change === undefined || change === null) return '--'
  return `${change > 0 ? '+' : ''}${change}%`
}

const formatVolume = (volume: number | undefined | null): string => {
  if (!volume) return '--'
  if (volume >= 10000) {
    return `${(volume / 10000).toFixed(1)}万`
  }
  return volume.toString()
}

const getSignalTagType = (signal: string): 'danger' | 'success' | 'info' => {
  if (signal === '买入') return 'danger'
  if (signal === '卖出') return 'success'
  return 'info'
}

// API加载函数
const loadMarketOverview = async () => {
  loading.overview = true
  try {
    const response = await dashboardService.getMarketOverview()

    if (response.success && response.data) { // Access response.data directly
      const marketData = response.data

      // 更新统计卡片数据 - 需要后端提供具体字段
      const marketStats = marketData.market_stats
      stats.value[0].value = marketStats?.total_stocks?.toString() || '0'
      stats.value[1].value = marketStats?.avg_change_percent?.toFixed(2) || '0.00' // 使用平均涨跌幅
      stats.value[2].value = `${marketStats?.rising_stocks || 0}涨 / ${marketStats?.falling_stocks || 0}跌`
      stats.value[3].value = '加载中...' // 行业数据从其他接口获取
    } else {
      ElMessage.error(response.message || '加载市场概览失败')
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
    const response = await dashboardService.getPriceDistribution()
    if (response.success && response.data) {
      updatePriceDistributionChart(response.data)
    } else {
      ElMessage.error(response.message || '加载涨跌分布失败')
    }
  } catch (error) {
    console.error('加载涨跌分布失败:', error)
    ElMessage.error('加载涨跌分布失败')
  }
}

const loadHotIndustries = async () => {
  try {
    const response = await dashboardService.getHotIndustries()
    if (response.success && response.data) {
      hotIndustries.value = response.data as Array<{ industry_name: string; avg_change: number; stock_count: number }>
    } else {
      ElMessage.error(response.message || '加载热门行业失败')
    }
  } catch (error) {
    console.error('加载热门行业失败:', error)
    ElMessage.error('加载热门行业失败')
  }
}

const loadHotConcepts = async () => {
  try {
    const response = await dashboardService.getHotConcepts()
    if (response.success && response.data) {
      // IndustryConceptData 使用 industry_name 字段（包括行业和概念）
      hotConcepts.value = response.data.map(item => ({
        concept_name: item.industry_name,
        avg_change: item.avg_change,
        stock_count: item.stock_count
      }))
    } else {
      ElMessage.error(response.message || '加载热门概念失败')
    }
  } catch (error) {
    console.error('加载热门概念失败:', error)
    ElMessage.error('加载热门概念失败')
  }
}

const loadWatchlist = async (): Promise<void> => {
  loading.watchlist = true
  try {
    const response = await watchlistApi.getWatchlist()
    // watchlistApi 返回的是 AxiosResponse，需要访问 response.data
    const apiResponse = response.data as { success?: boolean; data?: any; message?: string }
    if (apiResponse?.success && apiResponse.data) {
      // Use WatchlistItem type instead of any
      const data: WatchlistItem[] = apiResponse.data.items || apiResponse.data || []
      watchlistStocks.value = data.map((item: WatchlistItem): StockData => ({
        symbol: item.symbol || '',
        name: item.name || item.symbol || '',
        price: item.current_price || 0,
        change: item.change_percent || 0,
        volume: 0 // WatchlistItem 没有 volume 字段
      }))
    } else {
      ElMessage.error(apiResponse?.message || '加载自选股失败')
      watchlistStocks.value = []
    }
  } catch (error) {
    console.error('加载自选股失败:', error)
    ElMessage.error('加载自选股失败')
    watchlistStocks.value = []
  } finally {
    loading.watchlist = false
  }
}

const loadFavoriteStocks = async () => {
  try {
    const response = await dashboardService.getMarketOverview()
    if (response.success && response.data && response.data.top_etfs) {
      // 使用 top_etfs 作为自选股占位数据
      favoriteStocks.value = response.data.top_etfs.slice(0, 5).map((item: any): StockData => ({
        symbol: item.symbol || 'ETF',
        name: item.name || 'ETF基金',
        price: item.latest_price || 0,
        change: item.change_percent || 0,
        volume: item.volume || 0,
        turnover: item.turnover_rate || 0,
        industry: 'ETF'
      }))
    } else {
      ElMessage.error(response.message || '加载自选股失败')
    }
  } catch (error) {
    console.error('加载自选股失败:', error)
    ElMessage.error('加载自选股失败')
  }
}


const loadStrategyStocks = async () => {
  try {
    const response = await dashboardService.getMarketHeatChartData(); // Using another placeholder
    if (response.success && response.data) {
      // Assuming it returns data adaptable to StrategyStock
      strategyStocks.value = response.data.map((item: any): StrategyStock => ({
        symbol: item.name, // Assuming name is symbol
        name: item.name,
        price: 0, // Placeholder
        change: 0, // Placeholder
        strategy: '未知策略', // Placeholder
        score: item.value, // Using value as score
        signal: item.value > 80 ? '买入' : (item.value < 70 ? '卖出' : '持有') // Example signal
      }));
    } else {
      ElMessage.error(response.message || '加载策略选股失败');
    }
  } catch (error) {
    console.error('加载策略选股失败:', error);
    ElMessage.error('加载策略选股失败');
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
    const response = await watchlistApi.addToWatchlist({
      symbol: addForm.value.symbol.toUpperCase(),
      display_name: addForm.value.display_name
    })

    // watchlistApi 返回的是 AxiosResponse，需要访问 response.data
    const apiResponse = response.data as { success?: boolean; message?: string }
    if (apiResponse?.success) {
      ElMessage.success('添加自选股成功')
      showAddDialog.value = false
      await loadWatchlist()
    } else {
      ElMessage.error(apiResponse?.message || '添加自选股失败')
    }
  } catch (error) {
    console.error('添加自选股失败:', error)
    ElMessage.error('添加自选股失败')
  } finally {
    loading.addWatchlist = false
  }
}

const removeFromWatchlist = async (symbol: string): Promise<void> => {
  loading.removeWatchlist = true
  try {
    const response = await watchlistApi.removeFromWatchlist(symbol)
    // watchlistApi 返回的是 AxiosResponse，需要访问 response.data
    const apiResponse = response.data as { success?: boolean; message?: string }
    if (apiResponse?.success) {
      ElMessage.success('移除自选股成功')
      await loadWatchlist()
    } else {
      ElMessage.error(apiResponse?.message || '移除自选股失败')
    }
  } catch (error) {
    console.error('移除自选股失败:', error)
    ElMessage.error('移除自选股失败')
  } finally {
    loading.removeWatchlist = false
  }
}

// 图表初始化函数（更新数据给ChartContainer）
const updatePriceDistributionChart = (distributionData: Record<string, number>): void => {
  const data: ChartDataPoint[] = Object.entries(distributionData).map(([name, value]) => ({ name, value: Number(value) }))
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

// Chart init functions, now calling dashboardService for data
const initMarketHeatChart = async (): Promise<void> => {
  try {
    const response = await dashboardService.getMarketHeatChartData();
    if (response.success && response.data) {
      marketHeatData.value = response.data;
      marketHeatOptions.value = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        xAxis: { type: 'value', name: '热度指数' },
        yAxis: { type: 'category', data: response.data.map((item: ChartDataPoint) => item.name) },
        series: [{ name: '市场热度', type: 'bar', data: response.data.map((item: ChartDataPoint) => item.value) }]
      };
    } else {
      ElMessage.error(response.message || '加载市场热度失败');
    }
  } catch (error) {
    console.error('加载市场热度失败:', error);
    ElMessage.error('加载市场热度失败');
  }
};

const initLeadingSectorChart = async (): Promise<void> => {
  try {
    const response = await dashboardService.getLeadingSectorChartData();
    if (response.success && response.data) {
      leadingSectorData.value = response.data;
      leadingSectorOptions.value = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}: {c}%' },
        xAxis: { type: 'value', name: '涨幅(%)', axisLabel: { formatter: '{value}%' } },
        yAxis: { type: 'category', data: response.data.map((item: ChartDataPoint) => item.name) },
        series: [{ name: '涨幅', type: 'bar', data: response.data.map((item: ChartDataPoint) => item.value) }]
      };
    } else {
      ElMessage.error(response.message || '加载领涨板块失败');
    }
  } catch (error) {
    console.error('加载领涨板块失败:', error);
    ElMessage.error('加载领涨板块失败');
  }
};

const initCapitalFlowChart = async (): Promise<void> => {
  try {
    const response = await dashboardService.getCapitalFlowChartData();
    if (response.success && response.data) {
      capitalFlowData.value = response.data;
      capitalFlowOptions.value = {
        tooltip: {
          trigger: 'axis', axisPointer: { type: 'shadow' },
          formatter: (params: any) => {
            const value = params[0].value;
            const absValue = Math.abs(value);
            return `${params[0].name}: ${value > 0 ? '+' : ''}${value}亿 (${value > 0 ? '流入' : '流出'})`;
          }
        },
        xAxis: { type: 'value', name: '资金流向(亿元)', axisLabel: { formatter: (value: number) => value > 0 ? `+${value}` : value } },
        yAxis: { type: 'category', data: response.data.map((item: ChartDataPoint) => item.name) },
        series: [{ name: '资金流向', type: 'bar', data: response.data.map((item: ChartDataPoint) => item.value) }]
      };
    } else {
      ElMessage.error(response.message || '加载资金流向失败');
    }
  } catch (error) {
    console.error('加载资金流向失败:', error);
    ElMessage.error('加载资金流向失败');
  }
};

const initCapitalFlowChart2 = async (): Promise<void> => {
  try {
    const response = await dashboardService.getCapitalFlowChartData(); // Reusing the same service call for simplicity, ideally a different endpoint
    if (response.success && response.data) {
      capitalFlowData2.value = response.data;
      capitalFlowOptions2.value = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => `${params[0].name}: ${params[0].value > 0 ? '+' : ''}${params[0].value}亿` },
        xAxis: { type: 'value', name: '资金流向(亿元)' },
        yAxis: { type: 'category', data: response.data.map((item: ChartDataPoint) => item.name) },
        series: [{ name: '资金流向', type: 'bar', data: response.data.map((item: ChartDataPoint) => item.value) }]
      };
    } else {
      ElMessage.error(response.message || '加载资金流向失败');
    }
  } catch (error) {
    console.error('加载资金流向失败:', error);
    ElMessage.error('加载资金流向失败');
  }
};

const initIndustryChart = async (): Promise<void> => {
  try {
    const response = await dashboardService.getIndustryCapitalFlowChartData(industryStandard.value);
    if (response.success && response.data) {
      industryData.value = response.data;
      industryOptions.value = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => `${params[0].name}: ${params[0].value > 0 ? '+' : ''}${params[0].value}亿` },
        xAxis: { type: 'value', name: '资金流向(亿元)', axisLabel: { formatter: (value: number) => value > 0 ? `+${value}` : value } },
        yAxis: { type: 'category', data: response.data.map((item: ChartDataPoint) => item.name), axisLabel: { interval: 0, fontSize: 11 } },
        series: [{
          name: '资金流向', type: 'bar', data: response.data.map((item: ChartDataPoint) => item.value),
          label: {
            show: true, position: 'right',
            formatter: (params: any) => `${params.value > 0 ? '+' : ''}${params.value}亿`,
            fontSize: 10
          }
        }]
      };
    } else {
      ElMessage.error(response.message || '加载行业资金流向失败');
    }
  } catch (error) {
    console.error('加载行业资金流向失败:', error);
    ElMessage.error('加载行业资金流向失败');
  }
};


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
  // No direct data loading here, it's handled by individual chart init functions
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
