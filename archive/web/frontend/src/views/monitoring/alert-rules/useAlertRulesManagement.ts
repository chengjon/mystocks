import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { monitoringApi } from '@/api'

interface AlertRule {
  id: string
  rule_name: string
  symbol: string
  stock_name: string
  rule_type: string
  priority: number
  parameters: Record<string, unknown>
  notification_config: {
    level: string
    channels: string[]
  }
  is_active: boolean
}

interface RuleForm {
  id: string
  rule_name: string
  symbol: string
  stock_name: string
  rule_type: string
  parameters: {
    include_st: boolean
    change_percent_threshold: number | null
    volume_ratio_threshold: number | null
  }
  notification_config: {
    level: string
    channels: string[]
  }
  priority: number
  is_active: boolean
}

export function useAlertRulesManagement() {

const alertRules = ref<AlertRule[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const editingRule = ref<AlertRule | null>(null)

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const ruleTypes = [
  { value: 'limit_up', label: '涨停监控' },
  { value: 'limit_down', label: '跌停监控' },
  { value: 'volume_spike', label: '成交量激增' },
  { value: 'price_breakthrough', label: '价格突破' },
  { value: 'technical_signal', label: '技术信号' },
  { value: 'news_alert', label: '新闻告警' },
  { value: 'fund_flow', label: '资金流向' }
]

const ruleForm = reactive<RuleForm>({
  id: '',
  rule_name: '',
  symbol: '',
  stock_name: '',
  rule_type: 'limit_up',
  parameters: {
    include_st: false,
    change_percent_threshold: null,
    volume_ratio_threshold: null
  },
  notification_config: {
    level: 'warning',
    channels: ['ui', 'sound']
  },
  priority: 5,
  is_active: true
})

const tableColumns = computed((): unknown[] => [
  {
    prop: 'rule_name',
    label: '规则名称',
    width: 150
  },
  {
    prop: 'symbol',
    label: '股票代码',
    width: 120,
    className: 'mono'
  },
  {
    prop: 'stock_name',
    label: '股票名称',
    width: 120
  },
  {
    prop: 'rule_type',
    label: '规则类型',
    width: 120
  },
  {
    prop: 'priority',
    label: '优先级',
    width: 100,
    align: 'right',
    className: 'mono'
  },
  {
    prop: 'parameters',
    label: '参数',
    minWidth: 200
  },
  {
    prop: 'notification_config',
    label: '通知级别',
    width: 120
  },
  {
    prop: 'is_active',
    label: '状态',
    width: 100,
    align: 'center'
  },
  {
    prop: 'actions',
    label: '操作',
    width: 150,
    align: 'center'
  }
])

const paginatedRules = computed(() => {
  const start = (pagination.page - 1) * pagination.size
  const end = start + pagination.size
  return alertRules.value.slice(start, end)
})

const _getRuleTypeClass = (type: string): string => {
  switch (type) {
    case 'limit_up':
    case 'limit_down':
      return 'danger'
    case 'volume_spike':
      return 'warning'
    case 'price_breakthrough':
      return 'primary'
    case 'technical_signal':
      return 'success'
    default:
      return 'info'
  }
}

const getRuleTypeTag = (type: string): 'success' | 'warning' | 'danger' | 'info' => {
  switch (type) {
    case 'limit_up':
    case 'limit_down':
      return 'danger'
    case 'volume_spike':
      return 'warning'
    case 'price_breakthrough':
      return 'info'
    case 'technical_signal':
      return 'success'
    default:
      return 'info'
  }
}

const formatRuleType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'limit_up': '涨停监控',
    'limit_down': '跌停监控',
    'volume_spike': '成交量激增',
    'price_breakthrough': '价格突破',
    'technical_signal': '技术信号',
    'news_alert': '新闻告警',
    'fund_flow': '资金流向'
  }
  return typeMap[type] || type
}

const _getNotificationLevelClass = (level: string): string => {
  switch (level) {
    case 'info':
      return 'info'
    case 'warning':
      return 'warning'
    case 'error':
    case 'critical':
      return 'danger'
    default:
      return 'info'
  }
}

const getNotificationLevelType = (level: string): 'success' | 'warning' | 'danger' | 'info' => {
  switch (level) {
    case 'info':
      return 'info'
    case 'warning':
      return 'warning'
    case 'error':
    case 'critical':
      return 'danger'
    default:
      return 'info'
  }
}

const fetchAlertRules = async (): Promise<void> => {
  loading.value = true
  try {
    const response = await monitoringApi.getAlertRules()
    alertRules.value = (response.data || []) as unknown as AlertRule[]
    pagination.total = alertRules.value.length
  } catch (error) {
    console.error('获取告警规则失败:', error)
    ElMessage.error('获取告警规则失败')
  } finally {
    loading.value = false
  }
}

const editRule = (rule: AlertRule): void => {
  editingRule.value = rule
  Object.assign(ruleForm, {
    ...rule,
    parameters: { ...rule.parameters },
    notification_config: { ...rule.notification_config }
  })
  showCreateDialog.value = true
}

const saveRule = async (): Promise<void> => {
  try {
    if (editingRule.value) {
      await monitoringApi.updateAlertRule(editingRule.value.id, ruleForm)
      ElMessage.success('规则更新成功')
    } else {
      await monitoringApi.createAlertRule(ruleForm)
      ElMessage.success('规则创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    fetchAlertRules()
  } catch (error) {
    console.error('保存规则失败:', error)
    ElMessage.error('保存规则失败')
  }
}

const deleteRule = async (id: string): Promise<void> => {
  try {
    await ElMessageBox.confirm('确定要删除此告警规则吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await monitoringApi.deleteAlertRule(id)
    ElMessage.success('规则删除成功')
    fetchAlertRules()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除规则失败:', error)
      ElMessage.error('删除规则失败')
    }
  }
}

const resetForm = (): void => {
  Object.assign(ruleForm, {
    id: '',
    rule_name: '',
    symbol: '',
    stock_name: '',
    rule_type: 'limit_up',
    parameters: {
      include_st: false,
      change_percent_threshold: null,
      volume_ratio_threshold: null
    },
    notification_config: {
      level: 'warning',
      channels: ['ui', 'sound']
    },
    priority: 5,
    is_active: true
  })
  editingRule.value = null
}

const handleCloseDialog = (): void => {
  showCreateDialog.value = false
  resetForm()
}

const handleSizeChange = (size: number): void => {
  pagination.size = size
  pagination.page = 1
}

const handleCurrentChange = (page: number): void => {
  pagination.page = page
}

onMounted(() => {
  fetchAlertRules()
})

  return {
    alertRules,
    loading,
    showCreateDialog,
    editingRule,
    pagination,
    ruleTypes,
    ruleForm,
    tableColumns,
    paginatedRules,
    getRuleTypeTag,
    formatRuleType,
    getNotificationLevelType,
    fetchAlertRules,
    editRule,
    saveRule,
    deleteRule,
    resetForm,
    handleCloseDialog,
    handleSizeChange,
    handleCurrentChange,
  }
}
