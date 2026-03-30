import { ref, computed, onMounted, type Ref, type ComputedRef } from 'vue'
import { ElMessage } from 'element-plus'
import { API_ENDPOINTS } from '@/config/api'

// Type definitions
interface WencaiQuery {
  query_name: string
  query_text: string
  id?: string
  [key: string]: unknown
}

interface TreeNode {
  label: string
  type: string
  data?: WencaiQuery
  children: TreeNode[]
}

interface TableDataItem {
  [key: string]: unknown
}

interface SelectedStock {
  symbol: string
  name: string
  [key: string]: unknown
}

export function useWencaiPanelV2() {
// ============================================================================
// 数据状态
// ============================================================================

// 查询相关
const queries: Ref<WencaiQuery[]> = ref([])
const loadingQueries: Ref<boolean> = ref(false)
const customQueryText: Ref<string> = ref('')
const executingCustomQuery: Ref<boolean> = ref(false)

// 当前查询信息
const currentQueryName: Ref<string> = ref('')
const currentQueryText: Ref<string> = ref('')

// 表格数据
const tableData: Ref<TableDataItem[]> = ref([])
const loadingResults: Ref<boolean> = ref(false)
const currentPage: Ref<number> = ref(1)
const pageSize: Ref<number> = ref(20)
const total: Ref<number> = ref(0)

// 分组相关
const groupDialogVisible: Ref<boolean> = ref(false)
const selectedStock: Ref<SelectedStock | null> = ref(null)
const groupForm: Ref<{ groupName: string }> = ref({
  groupName: 'default'
})

// ============================================================================
// 树形数据
// ============================================================================

const treeProps = {
  children: 'children',
  label: 'label'
}

const treeData: ComputedRef<TreeNode[]> = computed(() => {
  const data: TreeNode[] = [
    {
      label: '默认查询',
      type: 'folder',
      children: []
    },
    {
      label: '分组 A',
      type: 'folder',
      children: []
    },
    {
      label: '分组 B',
      type: 'folder',
      children: []
    },
    {
      label: '分组 C',
      type: 'folder',
      children: []
    }
  ]

  // 将 qs_1 到 qs_9 放入默认查询
  const defaultFolder = data[0]
  queries.value.forEach((query: WencaiQuery) => {
    defaultFolder.children.push({
      label: query.query_name,
      type: 'query',
      data: query,
      children: []
    })
  })

  return data
})

// ============================================================================
// 计算属性
// ============================================================================

const paginatedTableData = computed(() => {
  return tableData.value
})

// ============================================================================
// 方法
// ============================================================================

// 加载查询列表
const loadQueries = async (): Promise<void> => {
  loadingQueries.value = true
  try {
    const response = await fetch(API_ENDPOINTS.wencai.queries)
    if (!response.ok) throw new Error('加载失败')
    const data: { queries?: WencaiQuery[] } = await response.json()
    queries.value = data.queries || []
    ElMessage.success(`加载成功：${queries.value.length} 个查询`)
  } catch (error: unknown) {
    const errorMsg = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('加载失败: ' + errorMsg)
  } finally {
    loadingQueries.value = false
  }
}

// 树节点点击
const handleNodeClick = (nodeData: TreeNode): void => {
  if (nodeData.type === 'query' && nodeData.data) {
    // 点击查询节点，显示查询语句但不执行
    currentQueryName.value = nodeData.data.query_name
    currentQueryText.value = nodeData.data.query_text
  }
}

// 执行预定义查询
const executeQuery = async (queryData: WencaiQuery): Promise<void> => {
  loadingResults.value = true
  currentQueryName.value = queryData.query_name
  currentQueryText.value = queryData.query_text

  try {
    // 1. 执行查询
    const response = await fetch(API_ENDPOINTS.wencai.query, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_name: queryData.query_name, pages: 1 })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: '未知错误' }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()
    ElMessage.success(`查询完成：${data.total_records || 0} 条数据`)

    // 2. 获取结果
    await loadResults(queryData.query_name)
  } catch (error: unknown) {
    console.error('Execute query error:', error)
    const errorMsg = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('执行失败: ' + errorMsg)
  } finally {
    loadingResults.value = false
  }
}

// 执行自定义查询
const executeCustomQuery = async (): Promise<void> => {
  if (!customQueryText.value) {
    ElMessage.warning('请输入查询条件')
    return
  }

  executingCustomQuery.value = true
  loadingResults.value = true
  currentQueryName.value = '自定义查询'
  currentQueryText.value = customQueryText.value

  try {
    const response = await fetch(API_ENDPOINTS.wencai.customQuery, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query_text: customQueryText.value,
        pages: 1
      })
    })

    if (!response.ok) throw new Error('查询失败')
    const data = await response.json()

    if (data.success) {
      // 处理结果数据
      processCustomQueryResults(data)
      ElMessage.success(`查询成功：${data.total_records} 条数据`)
    } else {
      ElMessage.warning(data.message || '查询失败')
    }
  } catch (error: unknown) {
    const errorMsg = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('查询失败: ' + errorMsg)
  } finally {
    executingCustomQuery.value = false
    loadingResults.value = false
  }
}

// 处理自定义查询结果
const processCustomQueryResults = (data: { results: Record<string, unknown>[]; total_records: number }): void => {
  const queryDate = new Date().toLocaleDateString('zh-CN')

  tableData.value = data.results.map((item: Record<string, unknown>, index: number): TableDataItem => ({
    序号: index + 1,
    股票代码: item['股票代码'] || item.code,
    股票简称: item['股票简称'] || item.name,
    最新价: item['最新价'] || item.price,
    涨跌幅: item['涨跌幅'] || item['最新涨跌幅'],
    涨停次数: item['涨停次数'] || 0,
    量比: item['量比'] || 0,
    换手率: item['换手率'] || 0,
    振幅: item['振幅'] || 0,
    查询日期: queryDate
  }))

  total.value = data.total_records
  currentPage.value = 1
}

// 加载预定义查询结果
const loadResults = async (queryName: string): Promise<void> => {
  try {
    const response = await fetch(
      `${API_ENDPOINTS.wencai.results(queryName)}?limit=${pageSize.value}&offset=${(currentPage.value - 1) * pageSize.value}`
    )

    if (!response.ok) throw new Error('加载数据失败')
    const data = await response.json()

    // 处理结果
    processQueryResults(data)
  } catch (error: unknown) {
    const errorMsg = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('加载失败: ' + errorMsg)
  }
}

// 处理查询结果
const processQueryResults = (data: { results: Record<string, unknown>[]; total: number }): void => {
  const queryDate = new Date().toLocaleDateString('zh-CN')

  tableData.value = data.results.map((item: Record<string, unknown>, index: number): TableDataItem => ({
    序号: (currentPage.value - 1) * pageSize.value + index + 1,
    股票代码: item['股票代码'] || item.code,
    股票简称: item['股票简称'] || item.name,
    最新价: item['最新价'] || item.price,
    涨跌幅: item['涨跌幅'] || item['最新涨跌幅'],
    涨停次数: item['涨停次数'] || 0,
    量比: item['量比'] || 0,
    换手率: item['换手率'] || 0,
    振幅: item['振幅'] || 0,
    查询日期: queryDate
  }))

  total.value = data.total
}

// 格式化数字（保留3位小数）
const formatNumber = (value: unknown, decimals = 3): string => {
  if (value === null || value === undefined || value === '') return '-'
  const num = typeof value === 'string' ? parseFloat(value) : (value as number)
  if (isNaN(num)) return String(value)
  return num.toFixed(decimals)
}

// 格式化百分比（保留2位小数）
const formatPercent = (value: unknown): string => {
  if (value === null || value === undefined || value === '') return '-'

  const num = typeof value === 'string' ? parseFloat(value.replace('%', '')) : (value as number)
  if (isNaN(num)) return String(value)

  return `${num.toFixed(2)}%`
}

// 获取涨跌幅颜色class
const getPriceChangeClass = (value: unknown): string => {
  if (!value) return ''
  const num = typeof value === 'string' ? parseFloat((value as string).replace('%', '')) : (value as number)
  if (num > 0) return 'price-up'
  if (num < 0) return 'price-down'
  return ''
}

// 分页变化
const handlePageChange = () => {
  if (currentQueryName.value && currentQueryName.value !== '自定义查询') {
    loadResults(currentQueryName.value)
  }
}

// 导出数据
const exportData = () => {
  if (tableData.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  const headers = ['序号', '股票代码', '股票简称', '最新价', '涨跌幅', '涨停次数', '量比', '换手率', '振幅', '查询日期']
  const csvContent = [
    headers.join(','),
    ...tableData.value.map(row =>
      headers.map(header => {
        const value = row[header]
        return typeof value === 'string' && value.includes(',') ? `"${value}"` : value
      }).join(',')
    )
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `${currentQueryName.value || '查询结果'}_${new Date().toISOString().split('T')[0]}.csv`)
  link.click()

  ElMessage.success('数据已导出')
}

// 显示分组对话框
const showGroupDialog = (row: Record<string, unknown>) => {
  selectedStock.value = {
    symbol: String(row['股票代码'] || row['symbol'] || ''),
    name: String(row['股票简称'] || row['name'] || ''),
    ...row
  }
  groupDialogVisible.value = true
}

// 确认加入分组
const confirmAddToGroup = () => {
  if (!groupForm.value.groupName) {
    ElMessage.warning('请选择分组')
    return
  }

  // TODO: 实现实际的分组保存逻辑
  ElMessage.success(`已将 ${selectedStock.value?.['股票简称'] || ''} 加入到 ${groupForm.value.groupName} 分组`)
  groupDialogVisible.value = false
}

// ============================================================================
// 生命周期
// ============================================================================

onMounted(() => {
  loadQueries()
})

  return {
    queries,
    loadingQueries,
    customQueryText,
    executingCustomQuery,
    currentQueryName,
    currentQueryText,
    tableData,
    loadingResults,
    currentPage,
    pageSize,
    total,
    groupDialogVisible,
    selectedStock,
    groupForm,
    treeProps,
    treeData,
    paginatedTableData,
    loadQueries,
    handleNodeClick,
    executeQuery,
    executeCustomQuery,
    processCustomQueryResults,
    loadResults,
    processQueryResults,
    formatNumber,
    formatPercent,
    getPriceChangeClass,
    handlePageChange,
    exportData,
    showGroupDialog,
    confirmAddToGroup,
  }
}
