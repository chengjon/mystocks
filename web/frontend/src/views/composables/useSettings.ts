import { ref, computed, onMounted, onUnmounted, watch, type Ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiClient } from '@/api/apiClient'

interface DatabaseInfo {
  id: string
  name: string
  host: string
  port: string
  status: 'success' | 'error' | 'testing' | 'unknown'
  message: string
}

interface DisplaySettings {
  fontFamily: string
  fontSize: 'small' | 'default' | 'large' | 'extra-large'
}

interface LogEntry {
  id?: number
  timestamp: string
  level: string
  category: string
  operation: string
  message: string
  duration_ms?: number | null
  details?: Record<string, unknown>
}

interface LogSummary {
  total_logs: number
  recent_errors_1h: number
  level_counts: Record<string, number>
}

export function useSettings() {

const defaultDbHost =
  import.meta.env.VITE_DB_HOST ||
  (typeof window !== 'undefined' ? window.location.hostname : 'localhost')
const defaultMysqlPort = import.meta.env.VITE_MYSQL_PORT || '3306'
const defaultPostgresqlPort = import.meta.env.VITE_POSTGRESQL_PORT || '5432'
const defaultTdenginePort = import.meta.env.VITE_TDENGINE_PORT || '6030'
const defaultRedisPort = import.meta.env.VITE_REDIS_PORT || '6379'

const activeTab: Ref<string> = ref('basic')

watch(activeTab, (newTab: string) => {
  if (newTab === 'logs') {
    fetchLogs()
    fetchLogSummary()
  }
})

const displaySettings: Ref<DisplaySettings> = ref({
  fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto",
  fontSize: 'default'
})

const fontSizeMap: Record<string, string> = {
  'small': '12px',
  'default': '14px',
  'large': '16px',
  'extra-large': '18px'
}

const previewStyle = computed(() => ({
  fontFamily: displaySettings.value.fontFamily,
  fontSize: fontSizeMap[displaySettings.value.fontSize],
  padding: '20px',
  border: '1px solid rgb(212 175 55 / 30%)',
  borderRadius: '0',
  backgroundColor: 'rgb(212 175 55 / 5%)'
}))

const applyDisplaySettings = (): void => {
  const root = document.documentElement
  root.style.setProperty('--font-family', displaySettings.value.fontFamily)
  root.style.setProperty('--font-size', fontSizeMap[displaySettings.value.fontSize])

  document.body.style.fontFamily = displaySettings.value.fontFamily
  document.body.style.fontSize = fontSizeMap[displaySettings.value.fontSize]
}

const _saveDisplaySettings = (): void => {
  localStorage.setItem('displaySettings', JSON.stringify(displaySettings.value))
  applyDisplaySettings()
  ElMessage.success('DISPLAY SETTINGS SAVED')
}

const _resetDisplaySettings = (): void => {
  displaySettings.value = {
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto",
    fontSize: 'default'
  }
  localStorage.removeItem('displaySettings')
  applyDisplaySettings()
  ElMessage.success('SETTINGS RESET TO DEFAULT')
}

const loadDisplaySettings = (): void => {
  const saved = localStorage.getItem('displaySettings')
  if (saved) {
    try {
      displaySettings.value = JSON.parse(saved)
      applyDisplaySettings()
    } catch (e) {
      console.error('Failed to load display settings:', e)
    }
  }
}

const databases: Ref<DatabaseInfo[]> = ref([
  {
    id: 'mysql',
    name: 'MySQL',
    host: defaultDbHost,
    port: defaultMysqlPort,
    status: 'unknown',
    message: ''
  },
  {
    id: 'postgresql',
    name: 'PostgreSQL',
    host: defaultDbHost,
    port: defaultPostgresqlPort,
    status: 'unknown',
    message: ''
  },
  {
    id: 'tdengine',
    name: 'TDengine',
    host: defaultDbHost,
    port: defaultTdenginePort,
    status: 'unknown',
    message: ''
  },
  {
    id: 'redis',
    name: 'Redis',
    host: defaultDbHost,
    port: defaultRedisPort,
    status: 'unknown',
    message: ''
  }
])

const testConnection = async (database: DatabaseInfo): Promise<void> => {
  database.status = 'testing'
  database.message = ''

  try {
    const response = await apiClient.post('/api/system/test-connection', {
      db_type: database.id,
      host: database.host,
      port: parseInt(database.port)
    })

    const result = (response as unknown as Record<string, any>)?.data || response
    if (result && result.success !== false) {
      database.status = 'success'
      database.message = result.message || 'CONNECTION SUCCESSFUL'
      ElMessage.success(`${database.name} CONNECTED`)
    } else {
      database.status = 'error'
      database.message = result.error || 'CONNECTION FAILED'
      ElMessage.error(`${database.name} CONNECTION FAILED`)
    }
  } catch (error: unknown) {
    database.status = 'error'
    const err = error as Record<string, any>
    database.message = err?.response?.data?.detail || err?.message || 'NETWORK ERROR'
    ElMessage.error(`${database.name} CONNECTION FAILED`)
  }
}

const _testAllConnections = async (): Promise<void> => {
  ElMessage.info('TESTING ALL DATABASE CONNECTIONS...')
  for (const db of databases.value) {
    await testConnection(db)
  }
  ElMessage.success('ALL DATABASE CONNECTIONS TESTED')
}

const logs: Ref<LogEntry[]> = ref([])
const logSummary: Ref<LogSummary> = ref({
  total_logs: 0,
  recent_errors_1h: 0,
  level_counts: {}
})
const logsLoading: Ref<boolean> = ref(false)
const filterErrors: Ref<boolean> = ref(false)
const selectedLevel: Ref<string> = ref('')
const selectedCategory: Ref<string> = ref('')
const currentPage: Ref<number> = ref(1)
const pageSize: Ref<number> = ref(20)
const totalLogs: Ref<number> = ref(0)
let autoRefreshTimer: NodeJS.Timeout | null = null

const fetchLogs = async (): Promise<void> => {
  logsLoading.value = true
  try {
    const params: Record<string, unknown> = {
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      filter_errors: filterErrors.value
    }

    if (selectedLevel.value) params.level = selectedLevel.value
    if (selectedCategory.value) params.category = selectedCategory.value

    const response = await apiClient.get('/api/system/logs', { params })
    const data = (response as unknown as Record<string, any>)?.data || response

    if (Array.isArray(data)) {
      logs.value = data
      totalLogs.value = data.length
    } else {
      logs.value = data?.logs || data || []
      totalLogs.value = data?.total || logs.value.length
    }
  } catch (error: unknown) {
    console.error('Error fetching logs:', error)
    ElMessage.error('FAILED TO FETCH LOGS')
    logs.value = generateMockLogs()
    totalLogs.value = logs.value.length
  } finally {
    logsLoading.value = false
  }
}

const generateMockLogs = (): LogEntry[] => {
  const logs: LogEntry[] = []
  const levels = ['INFO', 'WARNING', 'ERROR']
  const categories = ['database', 'api', 'adapter', 'system']
  const operations = ['query', 'insert', 'update', 'delete', 'connect']

  for (let i = 0; i < 10; i++) {
    logs.push({
      id: i + 1,
      timestamp: new Date(Date.now() - i * 3600000).toISOString(),
      level: levels[i % levels.length],
      category: categories[i % categories.length],
      operation: operations[i % operations.length],
      message: `MOCK LOG ENTRY ${i + 1}`,
      duration_ms: Math.floor(Math.random() * 100)
    })
  }
  return logs
}

const fetchLogSummary = async (): Promise<void> => {
  try {
    const response = await apiClient.get('/api/system/logs/summary')
    const data = (response as unknown as Record<string, any>)?.data || response

    if (typeof data === 'object' && data !== null) {
      const d = data as Record<string, any>
      logSummary.value = {
        total_logs: d.total_logs || d.total || 0,
        recent_errors_1h: d.recent_errors_1h || d.errors || 0,
        level_counts: d.level_counts || {}
      }
    }
  } catch (error: unknown) {
    console.error('Error fetching log summary:', error)
    logSummary.value = { total_logs: 156, recent_errors_1h: 3, level_counts: { INFO: 120, WARNING: 25, ERROR: 11 } }
  }
}

const _toggleFilter = (): void => {
  filterErrors.value = !filterErrors.value
  currentPage.value = 1
  fetchLogs()
}

const _refreshLogs = (): void => {
  fetchLogs()
  fetchLogSummary()
  ElMessage.success('LOGS REFRESHED')
}

const handleSizeChange = (val: number): void => {
  pageSize.value = val
  currentPage.value = 1
  fetchLogs()
}

const handleCurrentChange = (val: number): void => {
  currentPage.value = val
  fetchLogs()
}

const viewLogDetails = (log: LogEntry): void => {
  const details = log.details
    ? JSON.stringify(log.details, null, 2)
    : 'NO ADDITIONAL DETAILS'

  ElMessageBox.alert(
    `
    <div style="text-align: left;">
      <p><strong>TIMESTAMP:</strong> ${log.timestamp}</p>
      <p><strong>LEVEL:</strong> ${log.level}</p>
      <p><strong>CATEGORY:</strong> ${log.category}</p>
      <p><strong>OPERATION:</strong> ${log.operation}</p>
      <p><strong>MESSAGE:</strong> ${log.message}</p>
      ${log.duration_ms ? `<p><strong>DURATION:</strong> ${log.duration_ms}ms</p>` : ''}
      <p><strong>DETAILS:</strong></p>
      <pre style="max-height: 300px; overflow: auto; background: rgb(0 0 0 / 5%); padding: 10px; border-radius: 4px;">${details}</pre>
    </div>
    `,
    'LOG DETAILS',
    {
      dangerouslyUseHTMLString: true,
      customClass: 'log-details-dialog'
    }
  )
}

const getStatusBadgeClass = (status: string) => {
  const classes: Record<string, string> = {
    success: 'badge-success',
    error: 'badge-danger',
    testing: 'badge-warning',
    unknown: 'badge-info'
  }
  return classes[status] || 'badge-info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    success: 'CONNECTED',
    error: 'FAILED',
    testing: 'TESTING...',
    unknown: 'NOT TESTED'
  }
  return texts[status] || status
}

const getLevelBadgeClass = (level: string) => {
  const classes: Record<string, string> = {
    'INFO': 'badge-info',
    'WARNING': 'badge-warning',
    'ERROR': 'badge-danger',
    'CRITICAL': 'badge-danger'
  }
  return classes[level] || 'badge-info'
}

const formatTime = (timestamp: string): string => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const _showLogDetails = (row: LogEntry): void => {
  const detailsHtml = `
    <div style="text-align: left;">
      <p><strong>ID:</strong> ${row.id}</p>
      <p><strong>TIME:</strong> ${formatTime(row.timestamp)}</p>
      <p><strong>LEVEL:</strong> ${row.level}</p>
      <p><strong>CATEGORY:</strong> ${row.category}</p>
      <p><strong>OPERATION:</strong> ${row.operation}</p>
      <p><strong>MESSAGE:</strong> ${row.message}</p>
      ${row.duration_ms ? `<p><strong>DURATION:</strong> ${row.duration_ms}ms</p>` : ''}
    </div>
  `

  ElMessageBox.alert(detailsHtml, 'LOG DETAILS', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: 'OK'
  })
}

onMounted((): void => {
  loadDisplaySettings()

  if (activeTab.value === 'logs') {
    fetchLogs()
    fetchLogSummary()
  }

  autoRefreshTimer = setInterval(() => {
    if (activeTab.value === 'logs') {
      fetchLogs()
      fetchLogSummary()
    }
  }, 30000)
})

onUnmounted((): void => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
  }
})

  return {
    activeTab,
    displaySettings,
    fontSizeMap,
    previewStyle,
    applyDisplaySettings,
    _saveDisplaySettings,
    _resetDisplaySettings,
    loadDisplaySettings,
    databases,
    testConnection,
    _testAllConnections,
    logs,
    logSummary,
    logsLoading,
    filterErrors,
    selectedLevel,
    selectedCategory,
    currentPage,
    pageSize,
    totalLogs,
    fetchLogs,
    generateMockLogs,
    fetchLogSummary,
    _toggleFilter,
    _refreshLogs,
    handleSizeChange,
    handleCurrentChange,
    viewLogDetails,
    getStatusBadgeClass,
    getStatusText,
    getLevelBadgeClass,
    formatTime,
    _showLogDetails,
  }
}
