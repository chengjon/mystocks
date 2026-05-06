import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

type AnnouncementAuxSliceState = 'idle' | 'ready' | 'unavailable' | 'stale'
type AnnouncementPrimarySliceState = 'idle' | 'ready' | 'unavailable' | 'stale'
type AnnouncementRow = Record<string, unknown>

interface AnnouncementMonitorRule {
  id?: number | null
  rule_name?: string
  stock_codes?: string[]
  keywords?: string[]
  min_importance_level?: number
  notify_enabled?: boolean
  is_active?: boolean
}

interface AnnouncementMonitorError {
  response?: {
    data?: {
      detail?: string
    }
  }
  message?: string
}

interface EditingRuleState {
  id: number | null
  rule_name: string
  stock_codes_str: string
  keywords_str: string
  min_importance_level: number
  notify_enabled: boolean
  is_active: boolean
}

interface AnnouncementListSnapshot {
  rows: AnnouncementRow[]
  total: number
}

function readAnnouncementString(row: AnnouncementRow, primaryKey: string, fallbackKey: string): string | undefined {
  const primaryValue = row[primaryKey]
  if (typeof primaryValue === 'string' && primaryValue.trim()) {
    return primaryValue
  }

  const fallbackValue = row[fallbackKey]
  if (typeof fallbackValue === 'string' && fallbackValue.trim()) {
    return fallbackValue
  }

  return undefined
}

function normalizeAnnouncementRow(row: AnnouncementRow): AnnouncementRow {
  const title = readAnnouncementString(row, 'title', 'announcement_title')
  const type = readAnnouncementString(row, 'type', 'announcement_type')

  return {
    ...row,
    ...(title ? { title } : {}),
    ...(type ? { type } : {}),
  }
}

function normalizeAnnouncementRows(payload: unknown): AnnouncementRow[] {
  if (!Array.isArray(payload)) {
    return []
  }

  return payload
    .filter((item): item is AnnouncementRow => item !== null && typeof item === 'object')
    .map(normalizeAnnouncementRow)
}

export function useAnnouncementMonitor() {
const route = useRoute()

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 响应式数据
const stats = ref({})
const verifiedStatsSnapshots = ref<Record<string, Record<string, unknown>>>({})
const announcements = ref<AnnouncementRow[]>([])
const announcementSliceState = ref<AnnouncementPrimarySliceState>('idle')
const monitorRules = ref([])
const triggeredRecords = ref([])
const monitorRulesSliceState = ref<AnnouncementAuxSliceState>('idle')
const triggeredRecordsSliceState = ref<AnnouncementAuxSliceState>('idle')
const lastVerifiedAnnouncementSelectorKey = ref<string | null>(null)
const verifiedAnnouncementSnapshots = ref<Record<string, AnnouncementListSnapshot>>({})
const hasVerifiedMonitorRulesSnapshot = ref(false)
const hasVerifiedTriggeredRecordsSnapshot = ref(false)

const loading = reactive({
  announcements: false,
  rules: false,
  records: false,
  evaluation: false
})

// 搜索表单
const searchForm = reactive({
  stock_code: '',
  announcement_type: '',
  min_importance: 0,
  dateRange: []
})

// 分页信息
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const buildAnnouncementSelectorKey = (): string => JSON.stringify({
  stock_code: searchForm.stock_code || '',
  announcement_type: searchForm.announcement_type || '',
  min_importance: searchForm.min_importance || 0,
  date_range: Array.isArray(searchForm.dateRange) ? [...searchForm.dateRange] : [],
  page: pagination.page,
  page_size: pagination.pageSize,
})

const buildStatsSelectorKey = (): string => {
  const symbol = typeof route.params.symbol === 'string' ? route.params.symbol.trim() : ''
  return symbol ? `detail:${symbol}` : 'global'
}

const syncAnnouncementSelectorSnapshot = (selectorKey: string): boolean => {
  const snapshot = verifiedAnnouncementSnapshots.value[selectorKey]
  if (!snapshot) {
    announcements.value = []
    pagination.total = 0
    return false
  }

  announcements.value = snapshot.rows
  pagination.total = snapshot.total
  return true
}

const syncStatsSelectorSnapshot = (selectorKey: string): boolean => {
  const snapshot = verifiedStatsSnapshots.value[selectorKey]
  if (!snapshot) {
    stats.value = {}
    return false
  }

  stats.value = snapshot
  return true
}

// 规则对话框
const showRuleDialog = ref(false)
const ruleFormRef = ref(null)
const editingRule = ref<EditingRuleState>({
  id: null,
  rule_name: '',
  stock_codes_str: '',
  keywords_str: '',
  min_importance_level: 3,
  notify_enabled: true,
  is_active: true
})

// 规则表单验证
const ruleFormRules = {
  rule_name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  keywords_str: [
    { required: true, message: '请输入关键词', trigger: 'blur' }
  ]
}

// 获取统计信息
const fetchStats = async () => {
  const selectorKey = buildStatsSelectorKey()
  syncStatsSelectorSnapshot(selectorKey)
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/stats`)
    if (response.data?.success === false) {
      stats.value = {}
      ElMessage.error(response.data.message || '获取统计信息失败')
      return
    }

    stats.value = response.data
    verifiedStatsSnapshots.value = {
      ...verifiedStatsSnapshots.value,
      [selectorKey]: response.data,
    }
  } catch (error) {
    stats.value = {}
    console.error('获取统计信息失败:', error)
    ElMessage.error('获取统计信息失败')
  }
}

// 获取公告列表
const fetchAnnouncements = async () => {
  loading.announcements = true
  const selectorKey = buildAnnouncementSelectorKey()
  const hasVerifiedSelectorSnapshot = syncAnnouncementSelectorSnapshot(selectorKey)
  try {
    const params = {
      stock_code: searchForm.stock_code || undefined,
      announcement_type: searchForm.announcement_type || undefined,
      min_importance: searchForm.min_importance > 0 ? searchForm.min_importance : undefined,
      start_date: searchForm.dateRange ? searchForm.dateRange[0] : undefined,
      end_date: searchForm.dateRange ? searchForm.dateRange[1] : undefined,
      page: pagination.page,
      page_size: pagination.pageSize
    }

    const response = await axios.get(`${API_BASE_URL}/api/announcement/list`, { params })

    if (response.data.success) {
      const normalizedRows = normalizeAnnouncementRows(response.data.data)
      announcements.value = normalizedRows
      pagination.total = response.data.total
      verifiedAnnouncementSnapshots.value = {
        ...verifiedAnnouncementSnapshots.value,
        [selectorKey]: {
          rows: normalizedRows,
          total: response.data.total,
        },
      }
      lastVerifiedAnnouncementSelectorKey.value = selectorKey
      announcementSliceState.value = 'ready'
    } else {
      throw new Error(response.data.error || '获取公告列表失败')
    }
  } catch (error) {
    if (hasVerifiedSelectorSnapshot) {
      syncAnnouncementSelectorSnapshot(selectorKey)
      announcementSliceState.value = 'stale'
    } else {
      announcements.value = []
      pagination.total = 0
      announcementSliceState.value = 'unavailable'
    }
    console.error('获取公告列表失败:', error)
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.announcements = false
  }
}

// 获取今日公告
const fetchTodayAnnouncements = async () => {
  loading.announcements = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/today`)

    if (response.data.success) {
      announcements.value = normalizeAnnouncementRows(response.data.announcements)
      pagination.total = response.data.count
      ElMessage.success(`获取今日公告 ${response.data.count} 条`)
    } else {
      ElMessage.error(response.data.error || '获取今日公告失败')
    }
  } catch (error) {
    console.error('获取今日公告失败:', error)
    ElMessage.error('获取今日公告失败')
  } finally {
    loading.announcements = false
  }
}

// 获取重要公告
const fetchImportantAnnouncements = async () => {
  loading.announcements = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/important`)

    if (response.data.success) {
      announcements.value = normalizeAnnouncementRows(response.data.announcements)
      pagination.total = response.data.count
      ElMessage.success(`获取重要公告 ${response.data.count} 条`)
    } else {
      ElMessage.error(response.data.error || '获取重要公告失败')
    }
  } catch (error) {
    console.error('获取重要公告失败:', error)
    ElMessage.error('获取重要公告失败')
  } finally {
    loading.announcements = false
  }
}

// 获取监控规则
const fetchMonitorRules = async () => {
  loading.rules = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/monitor-rules`)
    if (response.data?.success === false) {
      throw new Error(response.data.error || response.data.message || '获取监控规则失败')
    }

    monitorRules.value = Array.isArray(response.data?.data)
      ? response.data.data
      : Array.isArray(response.data)
        ? response.data
        : []
    hasVerifiedMonitorRulesSnapshot.value = true
    monitorRulesSliceState.value = 'ready'
  } catch (error) {
    if (!hasVerifiedMonitorRulesSnapshot.value) {
      monitorRules.value = []
      monitorRulesSliceState.value = 'unavailable'
    } else {
      monitorRulesSliceState.value = 'stale'
    }
    console.error('获取监控规则失败:', error)
    ElMessage.error('获取监控规则失败')
  } finally {
    loading.rules = false
  }
}

// 获取触发记录
const fetchTriggeredRecords = async () => {
  loading.records = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/triggered-records`)

    if (response.data.success) {
      triggeredRecords.value = response.data.data
      hasVerifiedTriggeredRecordsSnapshot.value = true
      triggeredRecordsSliceState.value = 'ready'
    } else {
      throw new Error(response.data.error || '获取触发记录失败')
    }
  } catch (error) {
    if (!hasVerifiedTriggeredRecordsSnapshot.value) {
      triggeredRecords.value = []
      triggeredRecordsSliceState.value = 'unavailable'
    } else {
      triggeredRecordsSliceState.value = 'stale'
    }
    console.error('获取触发记录失败:', error)
    ElMessage.error('获取触发记录失败')
  } finally {
    loading.records = false
  }
}

// 评估监控规则
const evaluateRules = async () => {
  loading.evaluation = true
  try {
    const response = await axios.post(`${API_BASE_URL}/api/announcement/monitor/evaluate`)

    if (response.data.success) {
      ElMessage.success(`评估完成，触发 ${response.data.triggered_count} 条规则`)
      fetchTriggeredRecords() // 重新获取触发记录
    } else {
      ElMessage.error(response.data.error || '评估失败')
    }
  } catch (error) {
    console.error('评估监控规则失败:', error)
    ElMessage.error('评估监控规则失败')
  } finally {
    loading.evaluation = false
  }
}

// 编辑规则
const editRule = (rule: AnnouncementMonitorRule): void => {
  editingRule.value = {
    id: rule.id ?? null,
    rule_name: rule.rule_name || '',
    stock_codes_str: rule.stock_codes ? rule.stock_codes.join(',') : '',
    keywords_str: rule.keywords ? rule.keywords.join(',') : '',
    min_importance_level: rule.min_importance_level || 3,
    notify_enabled: rule.notify_enabled !== false,
    is_active: rule.is_active !== false
  }
  showRuleDialog.value = true
}

// 删除规则
const deleteRule = async (id: number): Promise<void> => {
  try {
    await ElMessageBox.confirm('确定要删除这个监控规则吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await axios.delete(`${API_BASE_URL}/api/announcement/monitor-rules/${id}`)

    if (response.data.success) {
      ElMessage.success('删除成功')
      fetchMonitorRules() // 重新获取规则列表
    } else {
      ElMessage.error(response.data.error || '删除失败')
    }
  } catch (error) {
    console.error('删除规则失败:', error)
    ElMessage.error('删除规则失败')
  }
}

// 保存规则
const saveRule = async () => {
  if (!editingRule.value.rule_name || !editingRule.value.keywords_str) {
    ElMessage.error('请填写必填字段')
    return
  }

  try {
    // 解析股票代码和关键词
    const stockCodes = editingRule.value.stock_codes_str
      ? editingRule.value.stock_codes_str.split(',').map(s => s.trim()).filter(s => s)
      : []
    const keywords = editingRule.value.keywords_str
      .split(',').map(s => s.trim()).filter(s => s)

    const ruleData = {
      rule_name: editingRule.value.rule_name,
      stock_codes: stockCodes,
      keywords: keywords,
      min_importance_level: editingRule.value.min_importance_level,
      notify_enabled: editingRule.value.notify_enabled,
      is_active: editingRule.value.is_active
    }

    if (editingRule.value.id) {
      // 更新规则
      await axios.put(`${API_BASE_URL}/api/announcement/monitor-rules/${editingRule.value.id}`, ruleData)
      ElMessage.success('更新成功')
    } else {
      // 创建规则
      await axios.post(`${API_BASE_URL}/api/announcement/monitor-rules`, ruleData)
      ElMessage.success('创建成功')
    }

    // 重新获取规则列表
    fetchMonitorRules()
    showRuleDialog.value = false
  } catch (error: unknown) {
    console.error('保存规则失败:', error)
    const errorObj = error as AnnouncementMonitorError
    ElMessage.error('保存规则失败: ' + (errorObj?.response?.data?.detail || errorObj?.message || 'Unknown error'))
  }
}

// 打开公告原文
const openAnnouncement = (url: string): void => {
  if (url) {
    window.open(url, '_blank')
  }
}

// 获取重要性级别样式类
const getImportanceClass = (level: number): string => {
  if (level >= 4) return 'text-important'
  if (level >= 3) return 'text-medium'
  return 'text-normal'
}

// 获取情感倾向类型
const getSentimentType = (sentiment: string): string => {
  switch (sentiment) {
    case 'positive':
      return 'success'
    case 'negative':
      return 'danger'
    default:
      return 'info'
  }
}

// 格式化情感倾向
const formatSentiment = (sentiment: string): string => {
  const map: Record<string, string> = {
    'positive': '正面',
    'negative': '负面',
    'neutral': '中性'
  }
  return map[sentiment] || sentiment
}

// 处理分页大小变化
const handleSizeChange = (size: number): void => {
  pagination.pageSize = size
  pagination.page = 1
  fetchAnnouncements()
}

// 处理当前页变化
const handleCurrentChange = (page: number): void => {
  pagination.page = page
  fetchAnnouncements()
}

// 刷新所有数据
const refreshData = () => {
  fetchStats()
  fetchAnnouncements()
  fetchMonitorRules()
  fetchTriggeredRecords()
}

// 页面加载时获取数据
onMounted(() => {
  refreshData()
})

  return {
    stats,
    announcements,
    announcementSliceState,
    monitorRules,
    monitorRulesSliceState,
    triggeredRecords,
    triggeredRecordsSliceState,
    loading,
    searchForm,
    pagination,
    showRuleDialog,
    ruleFormRef,
    editingRule,
    ruleFormRules,
    fetchStats,
    fetchAnnouncements,
    fetchTodayAnnouncements,
    fetchImportantAnnouncements,
    fetchMonitorRules,
    fetchTriggeredRecords,
    evaluateRules,
    editRule,
    deleteRule,
    saveRule,
    openAnnouncement,
    getImportanceClass,
    getSentimentType,
    formatSentiment,
    handleSizeChange,
    handleCurrentChange,
    refreshData,
  }
}
