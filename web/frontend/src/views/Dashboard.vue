<template>
  <div class="dashboard">
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
            <span>市场热度中心</span>
          </template>
          <el-tabs v-model="activeMarketTab" class="market-tabs">
            <el-tab-pane label="市场热度" name="heat">
              <div ref="marketHeatChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="领涨板块" name="leading">
              <div ref="leadingSectorChartRef" style="height: 350px"></div>
            </el-tab-pane>
            <el-tab-pane label="涨跌分布" name="distribution">
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
              <el-button type="primary" size="small" @click="handleRefresh">刷新</el-button>
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

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { dataApi } from '@/api'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { handleApiError } from '@/utils/errorHandler'

const loading = ref(false)
const activeMarketTab = ref('heat')
const activeSectorTab = ref('favorites')
const industryStandard = ref('csrc')
const marketHeatChartRef = ref(null)
const leadingSectorChartRef = ref(null)
const priceDistributionChartRef = ref(null)
const capitalFlowChartRef = ref(null)
const industryChartRef = ref(null)

// Real data from API (replaces mock data)
const favoriteStocks = ref([])
const strategyStocks = ref([])
const industryStocks = ref([])
const conceptStocks = ref([])  // TODO: Implement in future phase

const stats = ref([
  {
    title: '总股票数',
    value: '0',
    trend: '较昨日 +0',
    trendClass: 'up',
    icon: 'TrendCharts',
    color: '#409eff'
  },
  {
    title: '活跃股票',
    value: '0',
    trend: '较昨日 +0',
    trendClass: 'up',
    icon: 'DataLine',
    color: '#67c23a'
  },
  {
    title: '数据更新',
    value: '0',
    trend: '今日更新',
    trendClass: 'neutral',
    icon: 'Refresh',
    color: '#e6a23c'
  },
  {
    title: '系统状态',
    value: '正常',
    trend: '所有服务运行中',
    trendClass: 'up',
    icon: 'CircleCheck',
    color: '#67c23a'
  }
])

let marketHeatChart = null
let leadingSectorChart = null
let priceDistributionChart = null
let capitalFlowChart = null
let industryChart = null

// Real fund flow data from API
const industryData = ref({
  csrc: { categories: [], values: [] },
  sw_l1: { categories: [], values: [] },
  sw_l2: { categories: [], values: [] }
})

// Load dashboard data from API
const loadDashboardData = async () => {
  loading.value = true
  try {
    // Call dashboard summary API
    const response = await dataApi.getDashboardSummary()

    if (response.success) {
      // Update stats cards
      stats.value[0].value = response.stats.totalStocks.toString()
      stats.value[1].value = response.stats.activeStocks.toString()
      stats.value[2].value = response.stats.dataUpdates.toString()
      stats.value[3].value = response.stats.systemStatus

      // Update table data
      favoriteStocks.value = response.favorites || []
      strategyStocks.value = response.strategyStocks || []
      industryStocks.value = response.industryStocks || []

      // Update fund flow data
      industryData.value.csrc = response.fundFlow.csrc
      industryData.value.sw_l1 = response.fundFlow.sw_l1
      industryData.value.sw_l2 = response.fundFlow.sw_l2

      // Update industry chart if visible
      if (industryChart) {
        updateIndustryChartData()
      }
    }
  } catch (error) {
    handleApiError(error, '加载Dashboard数据失败')
  } finally {
    loading.value = false
  }
}

const updateIndustryChartData = () => {
  if (!industryChart) return

  const data = industryData.value[industryStandard.value]
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
      data: data.categories,
      axisLabel: {
        interval: 0,
        fontSize: 11
      }
    },
    series: [
      {
        name: '资金流向',
        type: 'bar',
        data: data.values,
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
}

const updateIndustryChart = () => {
  updateIndustryChartData()
}

const initMarketHeatChart = () => {
  if (!marketHeatChartRef.value) return

  marketHeatChart = echarts.init(marketHeatChartRef.value)
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
      data: ['人工智能', '新能源车', '芯片半导体', '医药生物', '5G通信', '军工', '白酒', '光伏']
    },
    series: [
      {
        name: '市场热度',
        type: 'bar',
        data: [95, 88, 82, 78, 75, 72, 68, 65],
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
}

const initLeadingSectorChart = () => {
  if (!leadingSectorChartRef.value) {
    console.warn('leadingSectorChartRef is not available yet')
    return
  }

  // Check if DOM element has valid dimensions
  const element = leadingSectorChartRef.value
  if (element.clientWidth === 0 || element.clientHeight === 0) {
    console.warn('leadingSectorChart DOM has zero dimensions, delaying initialization')
    setTimeout(initLeadingSectorChart, 100)
    return
  }

  leadingSectorChart = echarts.init(element)
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
      data: ['人工智能', '芯片', '新能源', '医疗', '5G', '军工', '消费', '金融']
    },
    series: [
      {
        name: '涨幅',
        type: 'bar',
        data: [8.5, 7.2, 6.8, 5.5, 4.9, 4.2, 3.8, 2.1],
        itemStyle: {
          color: (params) => {
            return params.value > 0 ? '#f56c6c' : '#67c23a'
          }
        }
      }
    ]
  }
  leadingSectorChart.setOption(option)
}

const initPriceDistributionChart = () => {
  if (!priceDistributionChartRef.value) {
    console.warn('priceDistributionChartRef is not available yet')
    return
  }

  // Check if DOM element has valid dimensions
  const element = priceDistributionChartRef.value
  if (element.clientWidth === 0 || element.clientHeight === 0) {
    console.warn('priceDistributionChart DOM has zero dimensions, delaying initialization')
    setTimeout(initPriceDistributionChart, 100)
    return
  }

  priceDistributionChart = echarts.init(element)
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
        data: [
          { value: 450, name: '涨停', itemStyle: { color: '#f56c6c' } },
          { value: 1250, name: '上涨', itemStyle: { color: '#fca5a5' } },
          { value: 800, name: '平盘', itemStyle: { color: '#909399' } },
          { value: 1150, name: '下跌', itemStyle: { color: '#86efac' } },
          { value: 350, name: '跌停', itemStyle: { color: '#67c23a' } }
        ]
      }
    ]
  }
  priceDistributionChart.setOption(option)
}

const initCapitalFlowChart = () => {
  if (!capitalFlowChartRef.value) {
    console.warn('capitalFlowChartRef is not available yet')
    return
  }

  // Check if DOM element has valid dimensions
  const element = capitalFlowChartRef.value
  if (element.clientWidth === 0 || element.clientHeight === 0) {
    console.warn('capitalFlowChart DOM has zero dimensions, delaying initialization')
    setTimeout(initCapitalFlowChart, 100)
    return
  }

  capitalFlowChart = echarts.init(element)
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
      data: ['超大单', '大单', '中单', '小单']
    },
    series: [
      {
        name: '资金流向',
        type: 'bar',
        data: [125.5, 85.3, -45.2, -165.6],
        itemStyle: {
          color: (params) => {
            return params.value > 0 ? '#f56c6c' : '#67c23a'
          }
        }
      }
    ]
  }
  capitalFlowChart.setOption(option)
}

const initCharts = async () => {
  await nextTick()

  // 初始化市场热度中心的各个图表
  initMarketHeatChart()
  initLeadingSectorChart()
  initPriceDistributionChart()
  initCapitalFlowChart()

  // 初始化资金流向图表
  if (industryChartRef.value) {
    industryChart = echarts.init(industryChartRef.value)
    updateIndustryChartData()
  }

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    marketHeatChart?.resize()
    leadingSectorChart?.resize()
    priceDistributionChart?.resize()
    capitalFlowChart?.resize()
    industryChart?.resize()
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
      priceDistributionChart?.resize()
      break
    case 'capital':
      capitalFlowChart?.resize()
      break
  }
})

const loadData = loadDashboardData

const handleRefresh = async () => {
  await loadDashboardData()
  ElMessage.success('数据已刷新')
}

onMounted(() => {
  initCharts()
  loadDashboardData()
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
