import { ref, computed, onMounted, _watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { TableColumn } from '@/components/shared'
import {

export function useIndustryConceptAnalysis() {
  getIndustryList,
  getConceptList,
  getIndustryStocks,
  getConceptStocks,
  getIndustryPerformance
} from '@/api/industryConcept.js'

const activeTab = ref<'industry' | 'concept'>('industry')
const loading = ref(false)
const stocksLoading = ref(false)

const industryList = ref<unknown[]>([])
const conceptList = ref<unknown[]>([])
const selectedIndustry = ref('')
const selectedConcept = ref('')

const currentCategory = ref<unknown>(null)
const stocks = ref<unknown[]>([])

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
    colorClass: (row: unknown) => getChangeColorClass(row.change_percent),
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
    result = stocks.value.filter((stock: unknown) =>
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
  } catch (error: unknown) {
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

  return {
    activeTab,
    loading,
    stocksLoading,
    industryList,
    conceptList,
    selectedIndustry,
    selectedConcept,
    currentCategory,
    stocks,
    searchKeyword,
    currentPage,
    pageSize,
    stats,
    pieChartData,
    data,
    pieChartOptions,
    barChartData,
    barChartOptions,
    tableColumns,
    paginatedStocks,
    start,
    end,
    result,
    keyword,
    formatPercent,
    formatPrice,
    formatVolume,
    formatAmount,
    getChangeColor,
    getChangeColorClass,
    refreshData,
    loadIndustryList,
    response,
    loadConceptList,
    response,
    loadIndustryStocks,
    loadConceptStocks,
    response,
    concept,
    handleTabChange,
    handleIndustryChange,
    handleConceptChange,
    resetFilters,
    handleSizeChange,
    handleCurrentChange,
    exportStocks,
  }
}
