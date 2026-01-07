<template>
    <!-- 页面头部 -->
    <PageHeader
      title="行业概念分析"
      subtitle="INDUSTRY CONCEPT ANALYSIS"
    />

    <!-- 主卡片 -->
    <div class="card main-card">
      <div class="card-header">
        <div class="header-title">
          <div class="title-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <line x1="8" y1="6" x2="21" y2="6"></line>
              <line x1="8" y1="12" x2="21" y2="12"></line>
              <line x1="8" y1="18" x2="21" y2="18"></line>
              <line x1="3" y1="6" x2="3.01" y2="6"></line>
              <line x1="3" y1="12" x2="3.01" y2="12"></line>
              <line x1="3" y1="18" x2="3.01" y2="18"></line>
            </svg>
          </div>
          <span class="title-text">分析面板</span>
          <span class="title-sub">ANALYSIS PANEL</span>
        </div>
        <button class="button button-primary" @click="refreshData" :class="{ loading: loading }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          刷新数据
        </button>
      </div>

      <div class="card-body">
        <!-- 筛选区域 -->
        <div class="filter-section">
          <div class="tabs">
            <button
              :class="['tab-button', { active: activeTab === 'industry' }]"
              @click="handleTabChange('industry')"
            >
              <span class="tab-icon">🏭</span>
              <span class="tab-text">行业分析</span>
            </button>
            <button
              :class="['tab-button', { active: activeTab === 'concept' }]"
              @click="handleTabChange('concept')"
            >
              <span class="tab-icon">💡</span>
              <span class="tab-text">概念分析</span>
            </button>
          </div>

          <div class="filter-controls">
            <select v-if="activeTab === 'industry'" v-model="selectedIndustry" class="select" @change="(e: Event) => handleIndustryChange((e.target as HTMLSelectElement).value)">
              <option value="">请选择行业</option>
              <option v-for="item in industryList" :key="item.industry_code" :value="item.industry_code">
                {{ item.industry_name }}
              </option>
            </select>

            <select v-if="activeTab === 'concept'" v-model="selectedConcept" class="select" @change="(e: Event) => handleConceptChange((e.target as HTMLSelectElement).value)">
              <option value="">请选择概念</option>
              <option v-for="item in conceptList" :key="item.concept_code" :value="item.concept_code">
                {{ item.concept_name }}
              </option>
            </select>

            <button class="button button-info" @click="resetFilters">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-9.75 9 9 9 0 0 0 9.75-9.75 0 0 0-9.75-9 9 0 0 0-9.75z"></path>
              </svg>
              重置筛选
            </button>
          </div>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-section" v-if="currentCategory">
          <div class="stats-grid">
            <!-- TEMP: ArtDecoStatCard removed - awaiting UI/UX migration -->
            <div class="stat-item">
              <div class="stat-label">{{ stats[0]?.title || 'N/A' }}</div>
              <div class="stat-value" :style="{ color: stats[0]?.color || '#D4AF37' }">{{ stats[0]?.value || '-' }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">{{ stats[1]?.title || 'N/A' }}</div>
              <div class="stat-value" :style="{ color: stats[1]?.color || '#D4AF37' }">{{ stats[1]?.value || '-' }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">{{ stats[2]?.title || 'N/A' }}</div>
              <div class="stat-value" :style="{ color: stats[2]?.color || '#D4AF37' }">{{ stats[2]?.value || '-' }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">{{ stats[3]?.title || 'N/A' }}</div>
              <div class="stat-value" :style="{ color: stats[3]?.color || '#D4AF37' }">{{ stats[3]?.value || '-' }}</div>
            </div>
          </div>

          <!-- 图表区域 -->
          <div class="chart-section">
            <ChartContainer
              chart-type="pie"
              :data="pieChartData"
              :options="pieChartOptions"
              height="280px"
              :loading="stocksLoading"
            />
            <ChartContainer
              chart-type="bar"
              :data="barChartData"
              :options="barChartOptions"
              height="280px"
              :loading="stocksLoading"
            />
          </div>
        </div>

        <!-- 成分股列表 -->
        <div class="stocks-section" v-if="stocks.length > 0">
          <div class="card stocks-card">
            <div class="card-header">
              <div class="header-title">
                <span class="title-text">成分股列表</span>
              </div>
              <div class="stocks-header-actions">
                <input
                  v-model="searchKeyword"
                  placeholder="搜索股票代码或名称"
                  class="input"
                />
                <button class="button button-primary" @click="exportStocks">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                  </svg>
                  导出数据
                </button>
              </div>
            </div>
            <div class="card-body">
              <StockListTable
                :columns="tableColumns"
                :data="paginatedStocks"
                :loading="stocksLoading"
                :row-clickable="false"
              />

              <!-- 分页 -->
              <PaginationBar
                v-model:page="currentPage"
                v-model:page-size="pageSize"
                :total="stocks.length"
                :page-sizes="[10, 20, 50, 100]"
                @page-change="handleCurrentChange"
                @size-change="handleSizeChange"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { TableColumn } from '@/components/shared'
import {
  getIndustryList,
  getConceptList,
  getIndustryStocks,
  getConceptStocks,
  getIndustryPerformance
} from '@/api/industryConcept.js'

const activeTab = ref<'industry' | 'concept'>('industry')
const loading = ref(false)
const stocksLoading = ref(false)

const industryList = ref<any[]>([])
const conceptList = ref<any[]>([])
const selectedIndustry = ref('')
const selectedConcept = ref('')

const currentCategory = ref<any>(null)
const stocks = ref<any[]>([])

const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 统计卡片数据
const stats = computed(() => [
  {
    title: '名称',
    value: currentCategory.value?.category_name || '--',
    color: 'gold' as const
  },
  {
    title: '涨跌幅',
    value: formatPercent(currentCategory.value?.change_percent),
    color: getChangeColor(currentCategory.value?.change_percent)
  },
  {
    title: '成分股',
    value: currentCategory.value?.stock_count?.toString() || '--',
    color: 'blue' as const
  },
  {
    title: '领涨股',
    value: currentCategory.value?.leader_stock || '--',
    color: 'green' as const
  }
])

// 饼图数据
const pieChartData = computed(() => {
  if (!currentCategory.value) return []

  const data = currentCategory.value
  return [
    {
      name: '上涨',
      value: data.up_count || 0
    },
    {
      name: '下跌',
      value: data.down_count || 0
    },
    {
      name: '平盘',
      value: data.flat_count || 0
    }
  ]
})

const pieChartOptions = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c}只 ({d}%)'
  },
  legend: {
    bottom: '5%',
    left: 'center'
  }
}))

// 柱状图数据
const barChartData = computed(() => {
  if (!currentCategory.value) return []

  return [
    {
      name: '涨跌幅',
      data: [{ name: '当前', value: currentCategory.value.change_percent || 0 }]
    }
  ]
})

const barChartOptions = computed(() => ({
  xAxis: {
    type: 'category',
    data: ['当前']
  },
  yAxis: {
    type: 'value'
  }
}))

// 表格列配置
const tableColumns = computed((): TableColumn[] => [
  {
    prop: 'symbol',
    label: '股票代码',
    width: 120,
    className: 'mono'
  },
  {
    prop: 'name',
    label: '股票名称',
    width: 120
  },
  {
    prop: 'latest_price',
    label: '最新价',
    width: 100,
    align: 'right',
    formatter: (value: number) => formatPrice(value)
  },
  {
    prop: 'change_percent',
    label: '涨跌幅',
    width: 120,
    align: 'right',
    colorClass: (_value: any, row: any) => getChangeColorClass(row.change_percent),
    formatter: (value: number) => formatPercent(value)
  },
  {
    prop: 'volume',
    label: '成交量',
    width: 120,
    align: 'right',
    formatter: (value: number) => formatVolume(value)
  },
  {
    prop: 'amount',
    label: '成交额',
    width: 120,
    align: 'right',
    formatter: (value: number) => formatAmount(value)
  }
])

const paginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  let result = stocks.value.slice(start, end)

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = stocks.value.filter((stock: any) =>
      stock.symbol.toLowerCase().includes(keyword) ||
      (stock.name && stock.name.toLowerCase().includes(keyword))
    )
  }

  return result
})

const formatPercent = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '--'
  return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
}

const formatPrice = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '--'
  return value.toFixed(2)
}

const formatVolume = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '--'
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`
  }
  return value.toString()
}

const formatAmount = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '--'
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`
  }
  return value.toString()
}

const getChangeColor = (value: number | null | undefined): 'red' | 'green' | 'gold' => {
  if (value === null || value === undefined) return 'gold'
  return value > 0 ? 'red' : value < 0 ? 'green' : 'gold'
}

const getChangeColorClass = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return ''
  return value > 0 ? 'positive' : value < 0 ? 'negative' : ''
}

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
  } catch (error: any) {
    console.error('数据刷新失败:', error)
    ElMessage.error('数据刷新失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const loadIndustryList = async () => {
  try {
    const response = await getIndustryList()
    if (response.data?.success) {
      industryList.value = response.data.data.industries || []
    }
  } catch (error) {
    console.error('加载行业列表失败:', error)
  }
}

const loadConceptList = async () => {
  try {
    const response = await getConceptList()
    if (response.data?.success) {
      conceptList.value = response.data.data.concepts || []
    }
  } catch (error) {
    console.error('加载概念列表失败:', error)
  }
}

const loadIndustryStocks = async (industryCode: string) => {
  stocksLoading.value = true
  try {
    const [stocksRes, perfRes] = await Promise.all([
      getIndustryStocks(industryCode),
      getIndustryPerformance(industryCode)
    ])

    if (stocksRes.data?.success) {
      stocks.value = stocksRes.data.data.stocks || []

      if (perfRes.data?.success) {
        currentCategory.value = {
          category_code: industryCode,
          category_name: perfRes.data.data.industry.industry_name,
          ...perfRes.data.data.industry
        }
      }
    }
  } catch (error) {
    console.error('加载行业成分股失败:', error)
    ElMessage.error('加载行业成分股失败')
  } finally {
    stocksLoading.value = false
  }
}

const loadConceptStocks = async (conceptCode: string) => {
  stocksLoading.value = true
  try {
    const response = await getConceptStocks(conceptCode)

    if (response.data?.success) {
      stocks.value = response.data.data.stocks || []

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
    console.error('加载概念成分股失败:', error)
    ElMessage.error('加载概念成分股失败')
  } finally {
    stocksLoading.value = false
  }
}

const handleTabChange = (tabName: 'industry' | 'concept') => {
  activeTab.value = tabName
  resetFilters()
}

const handleIndustryChange = (industryCode: string) => {
  if (industryCode) {
    loadIndustryStocks(industryCode)
  }
}

const handleConceptChange = (conceptCode: string) => {
  if (conceptCode) {
    loadConceptStocks(conceptCode)
  }
}

const resetFilters = () => {
  selectedIndustry.value = ''
  selectedConcept.value = ''
  stocks.value = []
  currentCategory.value = null
  currentPage.value = 1
  searchKeyword.value = ''
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const exportStocks = () => {
  ElMessage.info('导出功能待实现')
}

onMounted(() => {
  loadIndustryList()
  loadConceptList()
})
</script>

<style scoped lang="scss">

  padding: 24px;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
  min-height: 100vh;

  .card {
    background: var(--bg-card);
    border: 1px solid var(--gold-dim);
    position: relative;

    &::before,
    &::after {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      border: 2px solid var(--gold-primary);
      z-index: 1;
    }

    &::before {
      top: 12px;
      left: 12px;
      border-right: none;
      border-bottom: none;
    }

    &::after {
      bottom: 12px;
      right: 12px;
      border-left: none;
      border-top: none;
    }

    .card-header {
      padding: 16px 24px;
      border-bottom: 1px solid var(--gold-dim);

      .header-title {
        display: flex;
        align-items: center;
        gap: 12px;

        .title-icon {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--gold-primary);
          flex-shrink: 0;

          svg {
            width: 24px;
            height: 24px;
          }
        }

        .title-text {
          font-family: var(--font-body);
          font-size: 16px;
          font-weight: 600;
          color: var(--gold-primary);
          text-transform: uppercase;
          letter-spacing: 2px;
        }

        .title-sub {
          font-family: var(--font-body);
          font-size: 10px;
          color: var(--gold-muted);
          text-transform: uppercase;
          letter-spacing: 3px;
          display: block;
          margin-top: 2px;
        }
      }
    }

    .card-body {
      padding: 24px;
    }
  }

  .filter-section {
    margin-bottom: 32px;

    .tabs {
      display: flex;
      gap: 4px;
      margin-bottom: 20px;
      border-bottom: 1px solid var(--gold-dim);

      .tab-button {
        padding: 12px 24px;
        font-family: var(--font-body);
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: none;
        background: transparent;
        color: var(--text-muted);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.3s ease;
        position: relative;
        border-bottom: 2px solid transparent;

        .tab-icon {
          font-size: 16px;
        }

        &:hover {
          color: var(--gold-primary);
        }

        &.active {
          color: var(--gold-primary);
          border-bottom-color: var(--gold-primary);

          &::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - 24px);
            height: 2px;
            background: var(--gold-primary);
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
          }
        }
      }
    }

    .filter-controls {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .select,
  .select-sm {
    background: transparent;
    border: none;
    border-bottom: 2px solid var(--gold-dim);
    padding: 10px 0;
    font-family: var(--font-body);
    font-size: 14px;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.3s ease;

    &:focus {
      outline: none;
      border-bottom-color: var(--gold-primary);
      box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
    }

    option {
      background: var(--bg-card);
      color: var(--text-primary);
    }
  }

  .button {
    padding: 10px 20px;
    font-family: var(--font-body);
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    border: 2px solid var(--gold-primary);
    background: transparent;
    color: var(--gold-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.3s ease;
    position: relative;

    svg {
      width: 16px;
      height: 16px;
    }

    &:hover:not(.loading) {
      background: var(--gold-primary);
      color: var(--bg-primary);
    }

    &.loading {
      opacity: 0.6;
      cursor: not-allowed;
    }

    &::before {
      content: '';
      position: absolute;
      top: 4px;
      left: 4px;
      width: 6px;
      height: 6px;
      border-left: 1px solid currentColor;
      border-top: 1px solid currentColor;
    }

    &.button-primary {
      border-color: var(--rise);
      color: var(--rise);

      &::before {
        border-color: var(--rise);
      }

      &:hover:not(.loading) {
        background: var(--rise);
        color: var(--bg-primary);
      }
    }

    &.button-info {
      border-color: #409eff;
      color: #409eff;

      &::before {
        border-color: #409eff;
      }

      &:hover:not(.loading) {
        background: #409eff;
        color: var(--bg-primary);
      }
    }
  }

  .input {
    flex: 1;
    padding: 10px 16px;
    font-family: var(--font-body);
    font-size: 14px;
    background: transparent;
    border: 1px solid var(--gold-dim);
    color: var(--text-primary);
    transition: all 0.3s ease;

    &:focus {
      outline: none;
      border-color: var(--gold-primary);
      box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
    }
  }

  .stats-section {
    margin-bottom: 32px;

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }

    .chart-section {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 20px;
    }
  }

  .stocks-section {
    .stocks-card {
      .card-header {
        .header-title {
          .title-text {
            font-family: var(--font-body);
            font-size: 14px;
            font-weight: 600;
            color: var(--gold-primary);
            text-transform: uppercase;
            letter-spacing: 2px;
          }
        }

        .stocks-header-actions {
          display: flex;
          gap: 12px;
          align-items: center;
        }
      }
    }
  }

  @media (max-width: 768px) {
    padding: 16px;

    .filter-section {
      .filter-controls {
        flex-direction: column;
        align-items: stretch;

        .select,
        .button {
          width: 100%;
        }
      }

      .stats-section {
        .stats-grid {
          grid-template-columns: repeat(2, 1fr);
        }

        .chart-section {
          grid-template-columns: 1fr;
        }
      }

      .stocks-card {
        .card-header {
          flex-direction: column;
          align-items: flex-start;
          gap: 16px;

          .stocks-header-actions {
            width: 100%;
            flex-wrap: wrap;
            gap: 8px;

            .input {
              flex: 1;
            }

            .button {
              flex: 1;
            }
          }
        }
      }
    }
  }
}
</style>
