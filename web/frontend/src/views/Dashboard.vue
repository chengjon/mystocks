<template>
  <div class="dashboard">
    <!-- 页面标题栏 - 包含智能数据源指示器 -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="page-title">仪表盘</h1>
        <p class="page-subtitle">实时市场概览与投资组合监控</p>
      </div>
      <div class="header-right">
        <SmartDataIndicator ref="dataIndicator" />
      </div>
    </div>

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

    <el-row :gutter="20">
      <el-col :xs="24" :md="16">
        <el-card class="chart-card">
          <template #header>
            <div class="flex-between">
              <span>市场热度中心</span>
              <el-button type="warning" size="small" @click="handleRetry" :loading="loading">重试</el-button>
            </div>
          </template>
          <el-tabs v-model="activeMarketTab" class="market-tabs">
            <el-tab-pane label="市场热度" name="heat">
              <div ref="marketHeatChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="领涨板块" name="leading">
              <div ref="leadingSectorChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="市场分布" name="distribution">
              <div ref="priceDistributionChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="资金流向" name="capital">
              <div ref="capitalFlowChartRef" style="height: 350px"></div>
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

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="flex-between">
              <span>板块表现</span>
              <div>
                <el-button type="primary" size="small" @click="handleRefresh">刷新</el-button>
                <el-button type="warning" size="small" @click="handleRetry" :loading="loading" style="margin-left: 10px">重试</el-button>
              </div>
            </div>
          </template>
          <el-tabs v-model="activeSectorTab" class="sector-tabs">
            <el-tab-pane label="自选股" name="favorites">
              <el-table :data="favoriteStocks" stripe v-loading="loading" max-height="400">
                <el-table-column prop="symbol" label="代码" width="100" />
                <el-table-column prop="name" label="名称" width="120" />
                <el-table-column prop="price" label="现价" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-red' : row.change < 0 ? 'text-green' : ''">
                      {{ row.price }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="change" label="涨跌幅" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-red' : row.change < 0 ? 'text-green' : ''">
                      {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
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
              <el-table :data="strategyStocks" stripe v-loading="loading" max-height="400">
                <el-table-column prop="symbol" label="代码" width="100" />
                <el-table-column prop="name" label="名称" width="120" />
                <el-table-column prop="price" label="现价" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-red' : row.change < 0 ? 'text-green' : ''">
                      {{ row.price }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="change" label="涨跌幅" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-red' : row.change < 0 ? 'text-green' : ''">
                      {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="strategy" label="策略名称" width="120" />
                <el-table-column prop="score" label="评分" width="80" align="right" />
                <el-table-column prop="signal" label="信号" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.signal === '买入' ? 'danger' : row.signal === '卖出' ? 'success' : 'info'" size="small">
                      {{ row.signal }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="行业选股" name="industry">
              <el-table :data="industryStocks" stripe v-loading="loading" max-height="400">
                <el-table-column prop="symbol" label="代码" width="100" />
                <el-table-column prop="name" label="名称" width="120" />
                <el-table-column prop="price" label="现价" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-red' : row.change < 0 ? 'text-green' : ''">
                      {{ row.price }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="change" label="涨跌幅" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-red' : row.change < 0 ? 'text-green' : ''">
                      {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="industry" label="所属行业" width="120" />
                <el-table-column prop="industryRank" label="行业排名" width="100" align="center" />
                <el-table-column prop="marketCap" label="市值(亿)" width="120" align="right" />
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="概念选股" name="concept">
              <el-table :data="conceptStocks" stripe v-loading="loading" max-height="400">
                <el-table-column prop="symbol" label="代码" width="100" />
                <el-table-column prop="name" label="名称" width="120" />
                <el-table-column prop="price" label="现价" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-red' : row.change < 0 ? 'text-green' : ''">
                      {{ row.price }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="change" label="涨跌幅" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.change > 0 ? 'text-red' : row.change < 0 ? 'text-green' : ''">
                      {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="concepts" label="热门概念" min-width="200">
                  <template #default="{ row }">
                    <el-tag v-for="concept in row.concepts" :key="concept" size="small" style="margin-right: 5px">
                      {{ concept }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="conceptHeat" label="概念热度" width="100" align="right" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck

import { ref, onMounted, nextTick, watch, type Ref } from 'vue'
import { dataApi } from '@/api'
import * as echarts from 'echarts'
import type { ECharts, EChartOption } from 'echarts'
import { ElMessage } from 'element-plus'
import SmartDataIndicator from '@/components/common/SmartDataIndicator.vue'
import type { StockList, MarketOverview } from '@/types'

// 统计数据类型
interface StatItem {
  title: string
  value: string
  icon: string
  color: string
  trend: string
  trendClass: 'up' | 'down' | 'neutral'
}

// 股票表格数据类型
interface StockTableRow {
  symbol: string
  name: string
  price: string
  change: number
  volume?: string
  turnover?: string
  industry?: string
  strategy?: string
  score?: number
  signal?: string
  industryRank?: number
  marketCap?: number
  concepts?: string[]
  conceptHeat?: number
}

// 图表引用类型
type ChartRef = Ref<HTMLDivElement | null>

const loading: Ref<boolean> = ref(false)
const activeMarketTab: Ref<string> = ref('heat')
const activeSectorTab: Ref<string> = ref('favorites')
const industryStandard: Ref<string> = ref('csrc')
const marketHeatChartRef: ChartRef = ref(null)
const leadingSectorChartRef: ChartRef = ref(null)
const priceDistributionChartRef: ChartRef = ref(null)
const capitalFlowChartRef: ChartRef = ref(null)
const industryChartRef: ChartRef = ref(null)

// 初始化数据为空
const favoriteStocks: Ref<StockTableRow[]> = ref([])
const strategyStocks: Ref<StockTableRow[]> = ref([])
const industryStocks: Ref<StockTableRow[]> = ref([])
const conceptStocks: Ref<StockTableRow[]> = ref([])
const stats: Ref<StatItem[]> = ref([
  { title: '总股票数', value: '0', icon: 'Document', color: '#409EFF', trend: '+0%', trendClass: 'neutral' },
  { title: '总市值', value: '0', icon: 'Money', color: '#67C23A', trend: '+0%', trendClass: 'up' },
  { title: '市场分布', value: '0', icon: 'PieChart', color: '#E6A23C', trend: '+0%', trendClass: 'up' },
  { title: '行业分布', value: '0', icon: 'Grid', color: '#F56C6C', trend: '+0%', trendClass: 'down' }
])

let marketHeatChart: ECharts | null = null
let leadingSectorChart: ECharts | null = null
let priceDistributionChart: ECharts | null = null
let capitalFlowChart: ECharts | null = null
let industryChart: ECharts | null = null

// 更新行业资金流向图表
const updateIndustryChart = async (): Promise<void> => {
  if (!industryChartRef.value) return

  // 如果图表已存在，销毁重新创建
  if (industryChart) {
    industryChart.dispose()
  }

  industryChart = echarts.init(industryChartRef.value)

  try {
    // 这里应该从API获取真实的行业资金流向数据
    // 暂时使用模拟数据展示效果
    const mockData = {
      categories: ['银行', '房地产', '医药生物', '食品饮料', '电子', '计算机', '机械', '化工', '汽车', '家电'],
      values: [120, -50, 80, 65, -30, 90, 45, -20, 70, 55]
    }

    const option: EChartOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params: any) => {
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
          formatter: (value: number) => value > 0 ? `+${value}` : value
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
            color: (params: any) => {
              return params.value > 0 ? '#f56c6c' : '#67c23a'
            }
          },
          label: {
            show: true,
            position: 'right',
            formatter: (params: any) => {
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
    ElMessage.error('加载行业资金流向数据失败')
  }
}

// 更新市场分布图表
const updateMarketDistributionChart = (marketData: MarketOverview): void => {
  // 注意：这个图表现在在"市场分布"tab中，使用priceDistributionChartRef
  if (!priceDistributionChartRef.value) return

  // 创建专用的市场分布图表实例
  if ((window as any).marketDistributionChartInstance) {
    (window as any).marketDistributionChartInstance.dispose()
  }

  (window as any).marketDistributionChartInstance = echarts.init(priceDistributionChartRef.value)

  // 准备市场分布数据
  const marketDistribution = marketData.by_market || {}
  const marketNames = Object.keys(marketDistribution)
  const marketValues = Object.values(marketDistribution)

  // 如果没有市场数据，显示提示信息
  if (marketNames.length === 0) {
    ((window as any).marketDistributionChartInstance as ECharts).setOption({
      title: {
        text: '暂无市场分布数据',
        left: 'center',
        top: 'center'
      }
    })
    return
  }

  const option: EChartOption = {
    title: {
      text: 'A股市场分布',
      left: 'center',
      top: 20
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}只股票 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 60
    },
    series: [
      {
        name: '市场分布',
        type: 'pie',
        radius: ['30%', '70%'],
        center: ['60%', '50%'],
        data: marketNames.map((name: string, index: number) => ({
          value: marketValues[index],
          name: name === 'SH' ? '上海证券交易所' : name === 'SZ' ? '深圳证券交易所' : name
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: true,
          formatter: '{b}\n{c}只\n{d}%'
        }
      }
    ]
  }

  ((window as any).marketDistributionChartInstance as ECharts).setOption(option)
}

// 更新行业分布图表
const updateIndustryDistributionChart = (marketData: MarketOverview): void => {
  // 这里可以更新其他图表，比如行业分布柱状图
  // 由于当前只有一个资金流向图表，我们暂时不实现这个功能
  // 后续可以添加更多图表展示行业分布数据
}

const initMarketHeatChart = async (): Promise<void> => {
  if (!marketHeatChartRef.value) return

  marketHeatChart = echarts.init(marketHeatChartRef.value)

  try {
    // 这里应该从API获取真实的市场热度数据
    // 暂时使用模拟数据展示效果
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

    const option: EChartOption = {
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
        data: heatData.map((item) => item.name)
      },
      series: [
        {
          name: '市场热度',
          type: 'bar',
          data: heatData.map((item) => item.value),
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
    ElMessage.error('加载市场热度数据失败')
  }
}

const initLeadingSectorChart = async (): Promise<void> => {
  if (!leadingSectorChartRef.value) return

  leadingSectorChart = echarts.init(leadingSectorChartRef.value)

  try {
    // 这里应该从API获取真实的领涨板块数据
    // 暂时使用模拟数据展示效果
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

    const option: EChartOption = {
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
        data: sectorData.map((item) => item.name)
      },
      series: [
        {
          name: '涨幅',
          type: 'bar',
          data: sectorData.map((item) => item.change),
          itemStyle: {
            color: (params: any) => {
              return params.value > 0 ? '#f56c6c' : '#67c23a'
            }
          }
        }
      ]
    }
    leadingSectorChart.setOption(option)
  } catch (error) {
    console.error('加载领涨板块数据失败:', error)
    ElMessage.error('加载领涨板块数据失败')
  }
}

const initPriceDistributionChart = async (): Promise<void> => {
  if (!priceDistributionChartRef.value) return

  priceDistributionChart = echarts.init(priceDistributionChartRef.value)

  try {
    // 这里应该从API获取真实的涨跌分布数据
    // 暂时使用模拟数据展示效果
    const distributionData = [
      { name: '上涨>5%', value: 120 },
      { name: '上涨0-5%', value: 340 },
      { name: '平盘', value: 80 },
      { name: '下跌0-5%', value: 280 },
      { name: '下跌>5%', value: 180 }
    ]

    const option: EChartOption = {
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
          data: distributionData
        }
      ]
    }
    priceDistributionChart.setOption(option)
  } catch (error) {
    console.error('加载涨跌分布数据失败:', error)
    ElMessage.error('加载涨跌分布数据失败')
  }
}

const initCapitalFlowChart = async (): Promise<void> => {
  if (!capitalFlowChartRef.value) return

  capitalFlowChart = echarts.init(capitalFlowChartRef.value)

  try {
    // 这里应该从API获取真实的资金流向数据
    // 暂时使用模拟数据展示效果
    const flowData = [
      { name: '主力资金', value: 120 },
      { name: '散户资金', value: -80 },
      { name: '机构资金', value: 90 },
      { name: '北向资金', value: 60 },
      { name: '南向资金', value: -30 },
      { name: '融资融券', value: 40 }
    ]

    const option: EChartOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params: any) => {
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
          formatter: (value: number) => value > 0 ? `+${value}` : value
        }
      },
      yAxis: {
        type: 'category',
        data: flowData.map((item) => item.name)
      },
      series: [
        {
          name: '资金流向',
          type: 'bar',
          data: flowData.map((item) => item.value),
          itemStyle: {
            color: (params: any) => {
              return params.value > 0 ? '#f56c6c' : '#67c23a'
            }
          }
        }
      ]
    }
    capitalFlowChart.setOption(option)
  } catch (error) {
    console.error('加载资金流向数据失败:', error)
    ElMessage.error('加载资金流向数据失败')
  }
}

const initCharts = async (): Promise<void> => {
  await nextTick()

  // 初始化市场热度中心的各个图表
  await initMarketHeatChart()
  await initLeadingSectorChart()
  await initPriceDistributionChart()
  await initCapitalFlowChart()

  // 初始化资金流向图表
  if (industryChartRef.value) {
    await updateIndustryChart()
  }

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    marketHeatChart?.resize()
    leadingSectorChart?.resize()
    priceDistributionChart?.resize()
    capitalFlowChart?.resize()
    industryChart?.resize()
    ;(window as any).marketDistributionChartInstance?.resize()
  })
}

// 监听 tab 切换，确保图表正确渲染
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
      // 对于市场分布图表，需要调整专用实例的大小
      ;(window as any).marketDistributionChartInstance?.resize()
      break
    case 'capital':
      capitalFlowChart?.resize()
      break
  }
})

// 监听行业标准切换
watch(industryStandard, async () => {
  await updateIndustryChart()
})

const loadData = async (): Promise<void> => {
  loading.value = true
  try {
    // 获取股票基本信息
    const stocksResponse = await dataApi.getStocksBasic({ limit: 10 })
    if (stocksResponse.success && stocksResponse.data && stocksResponse.data.length > 0) {
      stats.value[0].value = stocksResponse.total?.toString() || stocksResponse.data.length.toString()
    } else {
      throw new Error(stocksResponse.msg || 'API返回数据格式错误')
    }

    // 获取市场概览数据
    const marketResponse = await dataApi.getMarketOverview()
    if (marketResponse.success && marketResponse.data) {
      const marketData = marketResponse.data

      // 更新统计卡片数据
      if (marketData.total_market_cap !== undefined) {
        // 显示真实的总市值数据（单位：万亿元）
        stats.value[1].value = `${marketData.total_market_cap}万亿`
      } else {
        // 如果没有市值数据，显示总股票数
        stats.value[1].value = marketData.total_stocks?.toString() || '0'
      }

      // 如果有市场分布数据，更新第三个统计卡片
      if (marketData.by_market) {
        const marketEntries = Object.entries(marketData.by_market)
        if (marketEntries.length > 0) {
          const [market, count] = marketEntries[0]
          stats.value[2].value = `${market}: ${count}`
        }
      }

      // 如果有行业分布数据，更新第四个统计卡片
      if (marketData.by_industry) {
        const industryEntries = Object.entries(marketData.by_industry)
        if (industryEntries.length > 0) {
          const [industry, count] = industryEntries[0]
          stats.value[3].value = `${industry}: ${count}`
        }
      }

      // 更新图表数据
      updateMarketDistributionChart(marketData)
      updateIndustryDistributionChart(marketData)
    } else {
      throw new Error(marketResponse.msg || 'API返回数据格式错误')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    // 提供更友好的错误信息
    if (error instanceof Error) {
      if ('response' in error) {
        const err = error as any
        ElMessage.error(`加载数据失败: ${err.response?.data?.msg || err.response?.data?.detail || '服务器错误'}`)
      } else if ('request' in error) {
        ElMessage.error('网络连接失败，请检查服务是否正常运行')
      } else {
        ElMessage.error(`加载数据失败: ${error.message}`)
      }
    }
  } finally {
    loading.value = false
  }
}

// 添加重试机制
const handleRetry = async (): Promise<void> => {
  try {
    await loadData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败，请稍后重试')
  }
}

const handleRefresh = (): void => {
  ElMessage.success('数据已刷新')
  loadData()
}

onMounted(() => {
  initCharts()
  loadData()
})
</script>

<style scoped lang="scss">
.dashboard {
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 16px 0;
    border-bottom: 1px solid #ebeef5;

    .header-left {
      .page-title {
        margin: 0 0 4px 0;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }

      .page-subtitle {
        margin: 0;
        font-size: 14px;
        color: #909399;
      }
    }

    .header-right {
      display: flex;
      align-items: center;
    }
  }

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
</style>
