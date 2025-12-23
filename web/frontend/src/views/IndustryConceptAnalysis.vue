<template>
  <div class="industry-concept-analysis">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span>行业/概念分析</span>
          <el-button type="primary" @click="refreshData" :loading="loading">
            刷新数据
          </el-button>
        </div>
      </template>

      <!-- 顶部筛选区 -->
      <div class="filter-section">
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <el-tab-pane label="行业分析" name="industry"></el-tab-pane>
          <el-tab-pane label="概念分析" name="concept"></el-tab-pane>
        </el-tabs>

        <div class="filter-controls">
          <el-select
            v-if="activeTab === 'industry'"
            v-model="selectedIndustry"
            placeholder="请选择行业"
            filterable
            clearable
            @change="handleIndustryChange"
            class="filter-select"
          >
            <el-option
              v-for="item in industryList"
              :key="item.industry_code"
              :label="item.industry_name"
              :value="item.industry_code"
            />
          </el-select>

          <el-select
            v-if="activeTab === 'concept'"
            v-model="selectedConcept"
            placeholder="请选择概念"
            filterable
            clearable
            @change="handleConceptChange"
            class="filter-select"
          >
            <el-option
              v-for="item in conceptList"
              :key="item.concept_code"
              :label="item.concept_name"
              :value="item.concept_code"
            />
          </el-select>

          <el-button @click="resetFilters" type="info" plain>
            重置筛选
          </el-button>
        </div>
      </div>

      <!-- 中间统计区 -->
      <div class="stats-section" v-if="currentCategory">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-label">名称</div>
                <div class="stat-value">{{ currentCategory.category_name }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-label">涨跌幅</div>
                <div
                  class="stat-value"
                  :class="{
                    'positive': currentCategory.change_percent > 0,
                    'negative': currentCategory.change_percent < 0
                  }"
                >
                  {{ formatPercent(currentCategory.change_percent) }}
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-label">成分股</div>
                <div class="stat-value">{{ currentCategory.stock_count }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-label">领涨股</div>
                <div class="stat-value">{{ currentCategory.leader_stock }}</div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 图表区域 -->
        <div class="chart-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="chart-card">
                <template #header>
                  <div class="chart-header">
                    <span>涨跌分布</span>
                  </div>
                </template>
                <div ref="pieChartRef" class="chart-container"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="chart-card">
                <template #header>
                  <div class="chart-header">
                    <span>平均涨跌幅</span>
                  </div>
                </template>
                <div ref="barChartRef" class="chart-container"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 底部成分股列表 -->
      <div class="stocks-section">
        <el-card class="stocks-card">
          <template #header>
            <div class="stocks-header">
              <span>成分股列表</span>
              <div class="stocks-header-actions">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索股票代码或名称"
                  clearable
                  style="width: 200px; margin-right: 10px;"
                />
                <el-button @click="exportStocks" type="primary" plain>
                  导出数据
                </el-button>
              </div>
            </div>
          </template>

          <el-table
            :data="filteredStocks"
            style="width: 100%"
            :loading="stocksLoading"
            stripe
            @row-click="handleStockClick"
          >
            <el-table-column prop="symbol" label="股票代码" width="120">
              <template #default="{ row }">
                <el-link @click.stop="handleStockClick(row)">{{ row.symbol }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="股票名称" width="120" />
            <el-table-column prop="latest_price" label="最新价" width="100" align="right">
              <template #default="{ row }">
                {{ formatPrice(row.latest_price) }}
              </template>
            </el-table-column>
            <el-table-column prop="change_percent" label="涨跌幅" width="100" align="right">
              <template #default="{ row }">
                <span
                  :class="{
                    'positive': row.change_percent > 0,
                    'negative': row.change_percent < 0
                  }"
                >
                  {{ formatPercent(row.change_percent) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="成交量" width="120" align="right">
              <template #default="{ row }">
                {{ formatVolume(row.volume) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="成交额" align="right">
              <template #default="{ row }">
                {{ formatAmount(row.amount) }}
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="stocks.length"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { useRouter } from 'vue-router'
import {
  getIndustryList,
  getConceptList,
  getIndustryStocks,
  getConceptStocks,
  getIndustryPerformance
} from '@/api/industryConcept.js'

// 路由
const router = useRouter()

// 响应式数据
const activeTab = ref('industry')
const loading = ref(false)
const stocksLoading = ref(false)

// 行业/概念数据
const industryList = ref([])
const conceptList = ref([])
const selectedIndustry = ref('')
const selectedConcept = ref('')

// 当前选中的分类数据
const currentCategory = ref(null)

// 成分股数据
const stocks = ref([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 图表引用
const pieChartRef = ref(null)
const barChartRef = ref(null)
let pieChart = null
let barChart = null

// 计算属性
const filteredStocks = computed(() => {
  let result = stocks.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(stock =>
      stock.symbol.toLowerCase().includes(keyword) ||
      (stock.name && stock.name.toLowerCase().includes(keyword))
    )
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 格式化函数
const formatPercent = (value) => {
  if (value === null || value === undefined) return '--'
  return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
}

const formatPrice = (value) => {
  if (value === null || value === undefined) return '--'
  return value.toFixed(2)
}

const formatVolume = (value) => {
  if (value === null || value === undefined) return '--'
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`
  }
  return value.toLocaleString()
}

const formatAmount = (value) => {
  if (value === null || value === undefined) return '--'
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`
  }
  return value.toLocaleString()
}

// 方法
const refreshData = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'industry') {
      await loadIndustryList()
      if (selectedIndustry.value) {
        await loadIndustryStocks(selectedIndustry.value)
      }
    } else {
      await loadConceptList()
      if (selectedConcept.value) {
        await loadConceptStocks(selectedConcept.value)
      }
    }
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const loadIndustryList = async () => {
  try {
    const response = await getIndustryList()
    if (response.success) {
      industryList.value = response.data.industries || []
    }
  } catch (error) {
    ElMessage.error('加载行业列表失败: ' + error.message)
  }
}

const loadConceptList = async () => {
  try {
    const response = await getConceptList()
    if (response.success) {
      conceptList.value = response.data.concepts || []
    }
  } catch (error) {
    ElMessage.error('加载概念列表失败: ' + error.message)
  }
}

const loadIndustryStocks = async (industryCode) => {
  stocksLoading.value = true
  try {
    const response = await getIndustryStocks(industryCode)
    if (response.success) {
      stocks.value = response.data.stocks || []

      // 获取行业表现数据
      const perfResponse = await getIndustryPerformance(industryCode)
      if (perfResponse.success) {
        currentCategory.value = {
          category_code: industryCode,
          category_name: perfResponse.data.industry.industry_name,
          ...perfResponse.data.industry
        }
        // 更新图表
        await nextTick()
        updateCharts(perfResponse.data)
      }
    }
  } catch (error) {
    ElMessage.error('加载行业成分股失败: ' + error.message)
  } finally {
    stocksLoading.value = false
  }
}

const loadConceptStocks = async (conceptCode) => {
  stocksLoading.value = true
  try {
    const response = await getConceptStocks(conceptCode)
    if (response.success) {
      stocks.value = response.data.stocks || []

      // 概念数据简化处理
      const concept = conceptList.value.find(c => c.concept_code === conceptCode)
      if (concept) {
        currentCategory.value = {
          category_code: conceptCode,
          category_name: concept.concept_name,
          ...concept
        }
      }
    }
  } catch (error) {
    ElMessage.error('加载概念成分股失败: ' + error.message)
  } finally {
    stocksLoading.value = false
  }
}

const handleTabChange = (tabName) => {
  resetFilters()
  if (tabName === 'industry') {
    loadIndustryList()
  } else {
    loadConceptList()
  }
}

const handleIndustryChange = (industryCode) => {
  if (industryCode) {
    loadIndustryStocks(industryCode)
  } else {
    stocks.value = []
    currentCategory.value = null
  }
}

const handleConceptChange = (conceptCode) => {
  if (conceptCode) {
    loadConceptStocks(conceptCode)
  } else {
    stocks.value = []
    currentCategory.value = null
  }
}

const resetFilters = () => {
  selectedIndustry.value = ''
  selectedConcept.value = ''
  stocks.value = []
  currentCategory.value = null
  searchKeyword.value = ''
  currentPage.value = 1
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const handleStockClick = (row) => {
  router.push(`/stock-detail/${row.symbol}`)
}

const exportStocks = () => {
  ElMessageBox.alert('导出功能待实现', '提示', {
    type: 'info'
  })
}

const updateCharts = (performanceData) => {
  // 更新饼图
  if (pieChartRef.value) {
    if (!pieChart) {
      pieChart = echarts.init(pieChartRef.value)
    }

    const option = {
      title: {
        text: '涨跌分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '涨跌分布',
          type: 'pie',
          radius: '50%',
          data: [
            { value: performanceData.up_count, name: '上涨' },
            { value: performanceData.down_count, name: '下跌' },
            { value: performanceData.stock_count - performanceData.up_count - performanceData.down_count, name: '平盘' }
          ],
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

    pieChart.setOption(option, true)
  }

  // 更新柱状图
  if (barChartRef.value) {
    if (!barChart) {
      barChart = echarts.init(barChartRef.value)
    }

    const option = {
      title: {
        text: '行业表现对比',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['当前行业']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '涨跌幅',
          type: 'bar',
          data: [performanceData.industry.change_percent],
          itemStyle: {
            color: performanceData.industry.change_percent > 0 ? '#e74c3c' : '#3498db'
          }
        }
      ]
    }

    barChart.setOption(option, true)
  }
}

// 监听窗口大小变化，重置图表
const handleResize = () => {
  if (pieChart) {
    pieChart.resize()
  }
  if (barChart) {
    barChart.resize()
  }
}

// 生命周期
onMounted(() => {
  loadIndustryList()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (pieChart) {
    pieChart.dispose()
  }
  if (barChart) {
    barChart.dispose()
  }
})
</script>

<style scoped>
.industry-concept-analysis {
  padding: 20px;
}

.main-card {
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-controls {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  align-items: center;
}

.filter-select {
  width: 200px;
}

.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
}

.stat-value.positive {
  color: #e74c3c;
}

.stat-value.negative {
  color: #3498db;
}

.chart-section {
  margin-top: 20px;
}

.chart-card {
  height: 300px;
}

.chart-container {
  height: 250px;
}

.stocks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
