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

const loading = ref(false)
const activeMarketTab = ref('heat')
const activeSectorTab = ref('favorites')
const industryStandard = ref('csrc')
const marketHeatChartRef = ref(null)
const leadingSectorChartRef = ref(null)
const priceDistributionChartRef = ref(null)
const capitalFlowChartRef = ref(null)
const industryChartRef = ref(null)

// Mock data for sector performance tabs
const favoriteStocks = ref([
  { symbol: '600519', name: '贵州茅台', price: 1680.50, change: 2.35, volume: '1.2万手', turnover: 0.85, industry: '白酒' },
  { symbol: '000858', name: '五粮液', price: 158.20, change: 1.85, volume: '8.5万手', turnover: 2.15, industry: '白酒' },
  { symbol: '300750', name: '宁德时代', price: 185.60, change: -1.25, volume: '15.2万手', turnover: 3.42, industry: '电池' },
  { symbol: '601012', name: '隆基绿能', price: 25.80, change: 0.78, volume: '22.5万手', turnover: 4.58, industry: '光伏' },
  { symbol: '002594', name: '比亚迪', price: 268.90, change: 3.15, volume: '18.9万手', turnover: 2.95, industry: '新能源车' }
])

const strategyStocks = ref([
  { symbol: '688981', name: '中芯国际', price: 45.80, change: 5.25, strategy: '突破策略', score: 88, signal: '买入' },
  { symbol: '002475', name: '立讯精密', price: 32.50, change: 3.85, strategy: '趋势跟踪', score: 85, signal: '买入' },
  { symbol: '300059', name: '东方财富', price: 15.20, change: 2.15, strategy: '均线策略', score: 82, signal: '持有' },
  { symbol: '600036', name: '招商银行', price: 38.90, change: -0.85, strategy: '价值投资', score: 78, signal: '持有' },
  { symbol: '000001', name: '平安银行', price: 12.50, change: -1.95, strategy: '价值投资', score: 65, signal: '卖出' }
])

const industryStocks = ref([
  { symbol: '600519', name: '贵州茅台', price: 1680.50, change: 2.35, industry: '白酒', industryRank: 1, marketCap: 21056 },
  { symbol: '000858', name: '五粮液', price: 158.20, change: 1.85, industry: '白酒', industryRank: 2, marketCap: 6125 },
  { symbol: '000568', name: '泸州老窖', price: 142.30, change: 1.55, industry: '白酒', industryRank: 3, marketCap: 2089 },
  { symbol: '002304', name: '洋河股份', price: 98.50, change: 0.95, industry: '白酒', industryRank: 4, marketCap: 1516 },
  { symbol: '600809', name: '山西汾酒', price: 185.60, change: 2.85, industry: '白酒', industryRank: 5, marketCap: 2268 }
])

const conceptStocks = ref([
  { symbol: '300750', name: '宁德时代', price: 185.60, change: 3.25, concepts: ['新能源', '电池', 'MSCI'], conceptHeat: 98 },
  { symbol: '688981', name: '中芯国际', price: 45.80, change: 5.25, concepts: ['芯片', '半导体', '华为概念'], conceptHeat: 95 },
  { symbol: '600276', name: '恒瑞医药', price: 45.20, change: 2.15, concepts: ['医药', '创新药', '抗癌'], conceptHeat: 88 },
  { symbol: '300122', name: '智飞生物', price: 78.50, change: 4.55, concepts: ['疫苗', '医药', '生物制品'], conceptHeat: 92 },
  { symbol: '002230', name: '科大讯飞', price: 42.30, change: 6.85, concepts: ['AI', '人工智能', '语音识别'], conceptHeat: 96 }
])

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

// 不同行业分类标准的数据
const industryData = {
  csrc: {
    categories: ['金融业', '房地产业', '制造业', '信息技术', '批发零售', '建筑业', '采矿业', '交通运输'],
    values: [185.5, 125.3, 98.7, 85.2, 52.8, 45.6, -38.5, -65.2]
  },
  sw_l1: {
    categories: ['计算机', '电子', '医药生物', '电力设备', '汽车', '食品饮料', '银行', '非银金融'],
    values: [165.8, 142.5, 118.9, 95.3, 78.6, 65.4, -45.8, -88.9]
  },
  sw_l2: {
    categories: ['半导体', '光学光电子', '计算机设备', '通信设备', '医疗器械', '化学制药', '白酒', '保险'],
    values: [195.2, 158.7, 125.6, 98.5, 85.3, 72.1, -52.3, -95.6]
  }
}

const updateIndustryChartData = () => {
  if (!industryChart) return

  const data = industryData[industryStandard.value]
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
  if (!leadingSectorChartRef.value) return

  leadingSectorChart = echarts.init(leadingSectorChartRef.value)
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
  if (!priceDistributionChartRef.value) return

  priceDistributionChart = echarts.init(priceDistributionChartRef.value)
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
  if (!capitalFlowChartRef.value) return

  capitalFlowChart = echarts.init(capitalFlowChartRef.value)
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

const loadData = async () => {
  loading.value = true
  try {
    const response = await dataApi.getStocksBasic({ limit: 10 })
    if (response.data && response.data.length > 0) {
      stats.value[0].value = response.total?.toString() || response.data.length.toString()
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
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
