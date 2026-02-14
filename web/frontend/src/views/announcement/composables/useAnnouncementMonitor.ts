import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
import axios from 'axios'

export function useAnnouncementMonitor() {
  Document, Calendar, Warning, Bell, Search, Refresh,
  Setting, Plus, Collection, Lightning
} from '@element-plus/icons-vue'

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 响应式数据
const stats = ref({})
const announcements = ref([])
const monitorRules = ref([])
const triggeredRecords = ref([])

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

// 规则对话框
const showRuleDialog = ref(false)
const ruleFormRef = ref(null)
const editingRule = ref({
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
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/stats`)
    stats.value = response.data
  } catch (error) {
    console.error('获取统计信息失败:', error)
    ElMessage.error('获取统计信息失败')
  }
}

// 获取公告列表
const fetchAnnouncements = async () => {
  loading.announcements = true
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
      announcements.value = response.data.data
      pagination.total = response.data.total
    } else {
      ElMessage.error(response.data.error || '获取公告列表失败')
    }
  } catch (error) {
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
      announcements.value = response.data.announcements
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
      announcements.value = response.data.announcements
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
    monitorRules.value = response.data
  } catch (error) {
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
    } else {
      ElMessage.error(response.data.error || '获取触发记录失败')
    }
  } catch (error) {
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
const editRule = (rule) => {
  editingRule.value = {
    ...rule,
    stock_codes_str: rule.stock_codes ? rule.stock_codes.join(',') : '',
    keywords_str: rule.keywords ? rule.keywords.join(',') : ''
  }
  showRuleDialog.value = true
}

// 删除规则
const deleteRule = async (id) => {
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

    let response
    if (editingRule.value.id) {
      // 更新规则
      response = await axios.put(`${API_BASE_URL}/api/announcement/monitor-rules/${editingRule.value.id}`, ruleData)
      ElMessage.success('更新成功')
    } else {
      // 创建规则
      _response = await axios.post(`${API_BASE_URL}/api/announcement/monitor-rules`, ruleData)
      ElMessage.success('创建成功')
    }

    // 重新获取规则列表
    fetchMonitorRules()
    showRuleDialog.value = false
  } catch (error) {
    console.error('保存规则失败:', error)
    ElMessage.error('保存规则失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 打开公告原文
const openAnnouncement = (url) => {
  if (url) {
    window.open(url, '_blank')
  }
}

// 获取重要性级别样式类
const getImportanceClass = (level) => {
  if (level >= 4) return 'text-important'
  if (level >= 3) return 'text-medium'
  return 'text-normal'
}

// 获取情感倾向类型
const getSentimentType = (sentiment) => {
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
const formatSentiment = (sentiment) => {
  const map = {
    'positive': '正面',
    'negative': '负面',
    'neutral': '中性'
  }
  return map[sentiment] || sentiment
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchAnnouncements()
}

// 处理当前页变化
const handleCurrentChange = (page) => {
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
    API_BASE_URL,
    stats,
    announcements,
    monitorRules,
    triggeredRecords,
    loading,
    searchForm,
    pagination,
    showRuleDialog,
    ruleFormRef,
    editingRule,
    ruleFormRules,
    fetchStats,
    response,
    fetchAnnouncements,
    params,
    response,
    fetchTodayAnnouncements,
    response,
    fetchImportantAnnouncements,
    response,
    fetchMonitorRules,
    response,
    fetchTriggeredRecords,
    response,
    evaluateRules,
    response,
    editRule,
    deleteRule,
    response,
    saveRule,
    stockCodes,
    keywords,
    ruleData,
    response,
    openAnnouncement,
    getImportanceClass,
    getSentimentType,
    formatSentiment,
    map,
    handleSizeChange,
    handleCurrentChange,
    refreshData,
  }
}
