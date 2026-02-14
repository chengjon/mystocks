import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { API_ENDPOINTS } from '@/config/api'
import {

export function useWencaiPanelV2() {
  Search,
  Refresh,
  Edit,
  Folder,
  Document,
  Download
} from '@element-plus/icons-vue'

// ============================================================================
// 数据状态
// ============================================================================

// 查询相关
const queries = ref([])
const loadingQueries = ref(false)
const customQueryText = ref('')
const executingCustomQuery = ref(false)

// 当前查询信息
const currentQueryName = ref('')
const currentQueryText = ref('')

// 表格数据
const tableData = ref([])
const loadingResults = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 分组相关
const groupDialogVisible = ref(false)
const selectedStock = ref(null)
const groupForm = ref({
  groupName: 'default'
})

// ============================================================================
// 树形数据
// ============================================================================

const treeProps = {
  children: 'children',
  label: 'label'
}

const treeData = computed(() => {
  const data = [
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
  queries.value.forEach(query => {
    defaultFolder.children.push({
      label: query.query_name,
      type: 'query',
      data: query
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
const loadQueries = async () => {
  loadingQueries.value = true
  try {
    const response = await fetch(API_ENDPOINTS.wencai.queries)
    if (!response.ok) throw new Error('加载失败')
    const data = await response.json()
    queries.value = data.queries || []
    ElMessage.success(`加载成功：${queries.value.length} 个查询`)
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loadingQueries.value = false
  }
}

// 树节点点击
const handleNodeClick = (data) => {
  if (data.type === 'query') {
    // 点击查询节点，显示查询语句但不执行
    currentQueryName.value = data.data.query_name
    currentQueryText.value = data.data.query_text
  }
}

// 执行预定义查询
const executeQuery = async (queryData) => {
  console.log('executeQuery called with:', queryData)

  loadingResults.value = true
  currentQueryName.value = queryData.query_name
  currentQueryText.value = queryData.query_text

  try {
    // 1. 执行查询
    console.log('Calling API with query_name:', queryData.query_name)

    const response = await fetch(API_ENDPOINTS.wencai.query, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_name: queryData.query_name, pages: 1 })
    })

    console.log('Response status:', response.status)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: '未知错误' }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()
    console.log('Query response:', data)

    ElMessage.success(`查询完成：${data.total_records || 0} 条数据`)

    // 2. 获取结果
    await loadResults(queryData.query_name)
  } catch (error) {
    console.error('Execute query error:', error)
    ElMessage.error('执行失败: ' + error.message)
  } finally {
    loadingResults.value = false
  }
}

// 执行自定义查询
const executeCustomQuery = async () => {
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
  } catch (error) {
    ElMessage.error('查询失败: ' + error.message)
  } finally {
    executingCustomQuery.value = false
    loadingResults.value = false
  }
}

// 处理自定义查询结果
const processCustomQueryResults = (data) => {
  const queryDate = new Date().toLocaleDateString('zh-CN')

  tableData.value = data.results.map((item, index) => ({
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
const loadResults = async (queryName) => {
  try {
    const response = await fetch(
      `${API_ENDPOINTS.wencai.results(queryName)}?limit=${pageSize.value}&offset=${(currentPage.value - 1) * pageSize.value}`
    )

    if (!response.ok) throw new Error('加载数据失败')
    const data = await response.json()

    // 处理结果
    processQueryResults(data)
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  }
}

// 处理查询结果
const processQueryResults = (data) => {
  const queryDate = new Date().toLocaleDateString('zh-CN')

  tableData.value = data.results.map((item, index) => ({
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
const formatNumber = (value, decimals = 3) => {
  if (value === null || value === undefined || value === '') return '-'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return value
  return num.toFixed(decimals)
}

// 格式化百分比（保留2位小数）
const formatPercent = (value) => {
  if (value === null || value === undefined || value === '') return '-'

  const num = typeof value === 'string' ? parseFloat(value.replace('%', '')) : value
  if (isNaN(num)) return value

  return `${num.toFixed(2)}%`
}

// 获取涨跌幅颜色class
const getPriceChangeClass = (value) => {
  if (!value) return ''
  const num = typeof value === 'string' ? parseFloat(value.replace('%', '')) : value
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
const showGroupDialog = (row) => {
  selectedStock.value = row
  groupDialogVisible.value = true
}

// 确认加入分组
const confirmAddToGroup = () => {
  if (!groupForm.value.groupName) {
    ElMessage.warning('请选择分组')
    return
  }

  // TODO: 实现实际的分组保存逻辑
  ElMessage.success(`已将 ${selectedStock.value['股票简称']} 加入到 ${groupForm.value.groupName} 分组`)
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
    data,
    defaultFolder,
    paginatedTableData,
    loadQueries,
    response,
    data,
    handleNodeClick,
    executeQuery,
    response,
    errorData,
    data,
    executeCustomQuery,
    response,
    data,
    processCustomQueryResults,
    queryDate,
    loadResults,
    response,
    data,
    processQueryResults,
    queryDate,
    formatNumber,
    num,
    formatPercent,
    num,
    getPriceChangeClass,
    num,
    handlePageChange,
    exportData,
    headers,
    csvContent,
    value,
    blob,
    link,
    url,
    showGroupDialog,
    confirmAddToGroup,
  }
}
