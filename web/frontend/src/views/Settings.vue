<template>
  <div class="settings">

    <div class="page-header">
      <h1 class="page-title">SYSTEM SETTINGS</h1>
      <p class="page-subtitle">CONFIGURATION | DISPLAY | DATABASE | LOGS</p>
    </div>

    <div class="main-card">
      <el-tabs v-model="activeTab" class="tabs">
        <el-tab-pane label="BASIC" name="basic">
          <div class="form">
            <div class="form-group">
              <label class="label">SYSTEM NAME</label>
              <input class="input" value="MyStocks" readonly>
            </div>
            <div class="form-group">
              <label class="label">VERSION</label>
              <input class="input" value="1.0.0" readonly>
            </div>
            <div class="form-group">
              <label class="label">API URL</label>
              <input class="input" value="http://localhost:8000" readonly>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="DISPLAY" name="display">
          <div class="form">
            <div class="form-group">
              <label class="label">FONT FAMILY</label>
              <el-select v-model="displaySettings.fontFamily" @change="applyDisplaySettings">
                <el-option label="SYSTEM DEFAULT" value="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto" />
                <el-option label="MICROSOFT YAHEI" value="'Microsoft YaHei', sans-serif" />
                <el-option label="PINGFANG SC" value="'PingFang SC', sans-serif" />
                <el-option label="SOURCE HAN SANS" value="'Source Han Sans CN', sans-serif" />
                <el-option label="SIMSUN" value="SimSun, serif" />
                <el-option label="SIMHEI" value="SimHei, sans-serif" />
                <el-option label="ARIAL" value="Arial, sans-serif" />
                <el-option label="HELVETICA" value="Helvetica, sans-serif" />
              </el-select>
            </div>
            <div class="form-group">
              <label class="label">FONT SIZE</label>
              <el-radio-group v-model="displaySettings.fontSize" @change="applyDisplaySettings">
                <el-radio label="small">SMALL (12px)</el-radio>
                <el-radio label="default">DEFAULT (14px)</el-radio>
                <el-radio label="large">LARGE (16px)</el-radio>
                <el-radio label="extra-large">EXTRA LARGE (18px)</el-radio>
              </el-radio-group>
            </div>
            <div class="form-group">
              <label class="label">PREVIEW</label>
              <div class="font-preview" :style="previewStyle">
                <p>THIS IS A FONT PREVIEW TEXT - 这是字体预览效果</p>
                <p>NUMBERS: 0123456789</p>
                <p>STOCK CODE: 600519 / 000858 / 300750</p>
              </div>
            </div>
            <div class="form-actions">
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="DATABASE" name="database">
          <el-table :data="databases" stripe border class="table">
            <el-table-column prop="name" label="TYPE" width="150" />
            <el-table-column prop="host" label="HOST" width="200" />
            <el-table-column prop="port" label="PORT" width="100" />
            <el-table-column prop="status" label="STATUS" width="120">
              <template #default="{ row }">
                <span class="badge" :class="getStatusBadgeClass(row.status)">
                  {{ getStatusText(row.status) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="ACTIONS" width="150">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="testConnection(row)">
                  TEST
                </el-button>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="MESSAGE" min-width="200" />
          </el-table>
          <div class="table-actions">
          </div>
        </el-tab-pane>

        <el-tab-pane label="USERS" name="users">
          <div class="table-actions">
          </div>
          <el-table :data="[]" stripe border class="table">
            <el-table-column prop="username" label="USERNAME" />
            <el-table-column prop="email" label="EMAIL" />
            <el-table-column prop="role" label="ROLE" />
            <el-table-column label="ACTIONS" width="200">
              <template #default>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="LOGS" name="logs">
          <div class="logs-toolbar">
            <el-button @click="filterErrors = !filterErrors" size="small">
              {{ filterErrors ? 'SHOW ALL' : 'ERRORS ONLY' }}
            </el-button>
            <el-select v-model="selectedLevel" placeholder="LEVEL" clearable @change="fetchLogs">
              <el-option label="INFO" value="INFO"></el-option>
              <el-option label="WARNING" value="WARNING"></el-option>
              <el-option label="ERROR" value="ERROR"></el-option>
              <el-option label="CRITICAL" value="CRITICAL"></el-option>
            </el-select>
            <el-select v-model="selectedCategory" placeholder="CATEGORY" clearable @change="fetchLogs">
              <el-option label="DATABASE" value="database"></el-option>
              <el-option label="API" value="api"></el-option>
              <el-option label="ADAPTER" value="adapter"></el-option>
              <el-option label="SYSTEM" value="system"></el-option>
            </el-select>
            <el-button @click="fetchLogs" size="small" :loading="logsLoading">
              REFRESH
            </el-button>
          </div>

          <div class="subcard" v-if="logSummary.total_logs">
            <el-row :gutter="24">
              <el-col :span="6">
                <div class="stat-item">
                  <span class="stat-label">TOTAL LOGS</span>
                  <span class="stat-value gold">{{ logSummary.total_logs }}</span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <span class="stat-label">RECENT ERRORS</span>
                  <span class="stat-value profit-up">{{ logSummary.recent_errors_1h }}</span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <span class="stat-label">INFO</span>
                  <span class="stat-value">{{ logSummary.level_counts?.INFO || 0 }}</span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <span class="stat-label">WARNING</span>
                  <span class="stat-value">{{ logSummary.level_counts?.WARNING || 0 }}</span>
                </div>
              </el-col>
            </el-row>
          </div>

          <el-table :data="logs" stripe border class="table" v-loading="logsLoading">
            <el-table-column prop="timestamp" label="TIME" width="180">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="level" label="LEVEL" width="100">
              <template #default="{ row }">
                <span class="badge" :class="getLevelBadgeClass(row.level)">
                  {{ row.level }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="CATEGORY" width="100" />
            <el-table-column prop="operation" label="OPERATION" width="150" />
            <el-table-column prop="message" label="MESSAGE" min-width="200" />
            <el-table-column label="ACTIONS" width="100">
              <template #default="{ row }">
                <el-button size="small" type="info" @click="viewLogDetails(row)">
                  DETAILS
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[20, 50, 100, 200]"
            :page-size="pageSize"
            :total="totalLogs"
            layout="total, sizes, prev, pager, next, jumper"
            class="pagination"
          />
        </el-tab-pane>

        <el-tab-pane label="ABOUT" name="about">
          <el-descriptions :column="1" border class="descriptions">
            <el-descriptions-item label="PROJECT NAME">MyStocks QUANTITATIVE TRADING SYSTEM</el-descriptions-item>
            <el-descriptions-item label="VERSION">v2.2.0</el-descriptions-item>
            <el-descriptions-item label="TECH STACK">FastAPI + Vue3 + Element Plus</el-descriptions-item>
            <el-descriptions-item label="DATABASE">MySQL + PostgreSQL + TDengine + Redis</el-descriptions-item>
            <el-descriptions-item label="DESCRIPTION">
              PROFESSIONAL QUANTITATIVE TRADING DATA MANAGEMENT SYSTEM, SUPPORTS MULTIPLE DATA SOURCES, INTELLIGENT CLASSIFICATION STORAGE, REAL-TIME MONITORING AND ANALYSIS
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, type Ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

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
  details?: Record<string, any>
}

interface LogSummary {
  total_logs: number
  recent_errors_1h: number
  level_counts: Record<string, number>
}

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
  border: '1px solid rgba(212, 175, 55, 0.3)',
  borderRadius: '0',
  backgroundColor: 'rgba(212, 175, 55, 0.05)'
}))

const applyDisplaySettings = (): void => {
  const root = document.documentElement
  root.style.setProperty('--font-family', displaySettings.value.fontFamily)
  root.style.setProperty('--font-size', fontSizeMap[displaySettings.value.fontSize])

  document.body.style.fontFamily = displaySettings.value.fontFamily
  document.body.style.fontSize = fontSizeMap[displaySettings.value.fontSize]
}

const saveDisplaySettings = (): void => {
  localStorage.setItem('displaySettings', JSON.stringify(displaySettings.value))
  applyDisplaySettings()
  ElMessage.success('DISPLAY SETTINGS SAVED')
}

const resetDisplaySettings = (): void => {
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
    host: '192.168.123.104',
    port: '3306',
    status: 'unknown',
    message: ''
  },
  {
    id: 'postgresql',
    name: 'PostgreSQL',
    host: '192.168.123.104',
    port: '5438',
    status: 'unknown',
    message: ''
  },
  {
    id: 'tdengine',
    name: 'TDengine',
    host: '192.168.123.104',
    port: '6030',
    status: 'unknown',
    message: ''
  },
  {
    id: 'redis',
    name: 'Redis',
    host: '192.168.123.104',
    port: '6379',
    status: 'unknown',
    message: ''
  }
])

const testConnection = async (database: DatabaseInfo): Promise<void> => {
  database.status = 'testing'
  database.message = ''

  try {
    const response = await api.post('/api/system/test-connection', {
      db_type: database.id,
      host: database.host,
      port: parseInt(database.port)
    })

    const result = (response as any)?.data || response
    if (result && result.success !== false) {
      database.status = 'success'
      database.message = result.message || 'CONNECTION SUCCESSFUL'
      ElMessage.success(`${database.name} CONNECTED`)
    } else {
      database.status = 'error'
      database.message = result.error || 'CONNECTION FAILED'
      ElMessage.error(`${database.name} CONNECTION FAILED`)
    }
  } catch (error: any) {
    database.status = 'error'
    database.message = error.response?.data?.detail || error.message || 'NETWORK ERROR'
    ElMessage.error(`${database.name} CONNECTION FAILED`)
  }
}

const testAllConnections = async (): Promise<void> => {
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
    const params: Record<string, any> = {
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      filter_errors: filterErrors.value
    }

    if (selectedLevel.value) params.level = selectedLevel.value
    if (selectedCategory.value) params.category = selectedCategory.value

    const response = await api.get('/api/system/logs', { params })
    const data = (response as any)?.data || response

    if (Array.isArray(data)) {
      logs.value = data
      totalLogs.value = data.length
    } else {
      logs.value = data?.logs || data || []
      totalLogs.value = data?.total || logs.value.length
    }
  } catch (error: any) {
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
    const response = await api.get('/api/system/logs/summary')
    const data = (response as any)?.data || response

    if (typeof data === 'object' && data !== null) {
      logSummary.value = {
        total_logs: data.total_logs || data.total || 0,
        recent_errors_1h: data.recent_errors_1h || data.errors || 0,
        level_counts: data.level_counts || {}
      }
    }
  } catch (error: any) {
    console.error('Error fetching log summary:', error)
    logSummary.value = { total_logs: 156, recent_errors_1h: 3, level_counts: { INFO: 120, WARNING: 25, ERROR: 11 } }
  }
}

const toggleFilter = (): void => {
  filterErrors.value = !filterErrors.value
  currentPage.value = 1
  fetchLogs()
}

const refreshLogs = (): void => {
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
      <pre style="max-height: 300px; overflow: auto; background: rgba(0,0,0,0.05); padding: 10px; border-radius: 4px;">${details}</pre>
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

const showLogDetails = (row: LogEntry): void => {
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
</script>

<style scoped lang="scss">
// Phase 3.3: Design Token Migration
@import '@/styles/theme-tokens.scss';


.settings {
  min-height: 100vh;
  padding: var(--spacing-6);
  position: relative;
  background: var(--bg-primary);

  .background-pattern {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.04;
    background-image:
      repeating-linear-gradient(
        45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      ),
      repeating-linear-gradient(
        -45deg,
        var(--accent-gold) 0px,
        var(--accent-gold) 1px,
        transparent 1px,
        transparent 10px
      );
  }

  .page-header {
    text-align: center;
    margin-bottom: var(--spacing-8);
    position: relative;
    z-index: 1;

    .page-title {
      font-family: var(--font-display);
      font-size: var(--font-size-h2);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-widest);
      color: var(--accent-gold);
      margin: 0 0 var(--spacing-2) 0;
    }

    .page-subtitle {
      font-family: var(--font-body);
      font-size: var(--font-size-small);
      color: var(--fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      margin: 0;
    }
  }

  .settings-card {
    background: var(--bg-card);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: var(--radius-none);
    padding: var(--spacing-6);
    position: relative;
    z-index: 1;
  }

  .settings-container {
    max-width: 600px;
    margin: 0 auto;

    .form-group {
      margin-bottom: var(--spacing-5);

      .input {
        width: 100%;
        padding: var(--spacing-2) var(--spacing-3);
        font-family: var(--font-body);
        font-size: var(--font-size-body);
        color: var(--fg-primary);
        background: transparent;
        border: none;
        border-bottom: 2px solid var(--accent-gold);
        border-radius: var(--radius-none);
        transition: all var(--transition-base);

        &[readonly] {
          color: var(--fg-muted);
          background: rgba(212, 175, 55, 0.05);
          border-bottom-color: rgba(212, 175, 55, 0.2);
        }

        &:focus {
          outline: none;
          border-bottom-color: var(--accent-gold-light);
          box-shadow: 0 4px 10px rgba(212, 175, 55, 0.2);
        }
      }

      .font-preview {
        padding: var(--spacing-5);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: var(--radius-none);
        background: rgba(212, 175, 55, 0.05);

        p {
          margin: var(--spacing-2) 0;
          line-height: 1.8;
        }
      }

      .form-actions {
        display: flex;
        gap: var(--spacing-3);
        margin-top: var(--spacing-5);
      }
    }
  }

  .table-actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-3);
    margin-bottom: var(--spacing-4);
  }

  .stats-grid {
    background: rgba(212, 175, 55, 0.05);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: var(--radius-none);
    padding: var(--spacing-5);
    margin-bottom: var(--spacing-4);

    .stat-item {
      text-align: center;

      .stat-label {
        display: block;
        font-family: var(--font-display);
        font-size: var(--font-size-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wider);
        color: var(--fg-muted);
        margin-bottom: var(--spacing-2);
      }

      .stat-value {
        display: block;
        font-family: var(--font-mono);
        font-size: var(--font-size-h4);
        font-weight: 700;
        color: var(--fg-primary);
      }
    }
  }

  .logs-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--spacing-3);
    margin-bottom: var(--spacing-4);
    flex-wrap: wrap;
  }

  .tabs {
    :deep(.el-tabs__nav-wrap) {
      &::after {
        background: rgba(212, 175, 55, 0.3);
      }
    }

    :deep(.el-tabs__item) {
      color: var(--fg-muted);
      font-family: var(--font-display);
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      font-weight: 600;

      &:hover {
        color: var(--accent-gold);
      }

      &.is-active {
        color: var(--accent-gold);
        border-bottom: 2px solid var(--accent-gold) !important;
      }
    }

    :deep(.el-tabs__active-bar) {
      background: var(--accent-gold);
    }
  }

  .table {
    background: transparent;

    :deep(.el-table__header) {
      th {
        background: rgba(212, 175, 55, 0.1) !important;
        color: var(--accent-gold) !important;
        font-family: var(--font-display);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--tracking-wider);
        border-bottom: 2px solid var(--accent-gold) !important;
      }
    }

    :deep(.el-table__body) {
      tr {
        background: transparent !important;
        transition: background var(--transition-base);

        &:hover {
          background: rgba(212, 175, 55, 0.05) !important;
        }

        td {
          border-bottom: 1px solid rgba(212, 175, 55, 0.2) !important;
          color: var(--fg-primary);
        }
      }
    }
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: var(--spacing-6);

    :deep(.el-pagination) {
      .btn-prev,
      .btn-next,
      .el-pager li {
        background: transparent !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: var(--radius-none) !important;
        color: var(--fg-primary) !important;
        font-family: var(--font-display) !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;

        &:hover {
          background: rgba(212, 175, 55, 0.1) !important;
          border-color: var(--accent-gold) !important;
        }

        &.active {
          background: var(--accent-gold) !important;
          border-color: var(--accent-gold) !important;
          color: var(--bg-primary) !important;
        }
      }

      .el-pagination__total,
      .el-pagination__sizes,
      .el-pagination__jump {
        color: var(--fg-primary) !important;
        font-family: var(--font-body) !important;
      }
    }
  }

  .btn-gold {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-2);
    padding: var(--spacing-3) var(--spacing-6);
    font-family: var(--font-display);
    font-size: var(--font-size-body);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    border: 2px solid var(--accent-gold);
    border-radius: var(--radius-none);
    background: transparent;
    color: var(--accent-gold);
    cursor: pointer;
    transition: all var(--transition-base);

    &:hover {
      background: var(--bg-secondary);
      box-shadow: var(--glow-subtle);
    }
  }

  .btn-gold-primary {
    background: var(--accent-gold);
    color: var(--bg-primary);

    &:hover {
      background: var(--accent-gold-light);
      box-shadow: var(--glow-medium);
    }
  }

  .btn-success {
    background: var(--color-up);
    border-color: var(--color-up);
    color: white;

    &:hover {
      background: #D94F51;
      box-shadow: 0 0 20px rgba(255, 82, 82, 0.4);
    }
  }

  .btn-gold-small {
    padding: var(--spacing-2) var(--spacing-4);
    font-size: var(--font-size-small);
  }

  .badge {
    display: inline-block;
    padding: 4px 12px;
    font-family: var(--font-display);
    font-size: var(--font-size-xs);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    border-radius: var(--radius-none);
  }

  .badge-success {
    background: rgba(39, 174, 96, 0.15);
    color: #27AE60;
    border: 1px solid #27AE60;
  }

  .badge-danger {
    background: rgba(231, 76, 60, 0.15);
    color: #E74C3C;
    border: 1px solid #E74C3C;
  }

  .badge-warning {
    background: rgba(230, 126, 34, 0.15);
    color: #E67E22;
    border: 1px solid #E67E22;
  }

  .badge-info {
    background: rgba(74, 144, 226, 0.15);
    color: #4A90E2;
    border: 1px solid #4A90E2;
  }

    :deep(.el-descriptions__label) {
      background: rgba(212, 175, 55, 0.1) !important;
      color: var(--fg-muted) !important;
      font-family: var(--font-display);
      font-size: var(--font-size-xs);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      border-color: rgba(212, 175, 55, 0.3) !important;
    }

    :deep(.el-descriptions__content) {
      background: transparent !important;
      color: var(--fg-primary) !important;
      font-family: var(--font-body);
      border-color: rgba(212, 175, 55, 0.3) !important;
    }
  }

  .gold {
    color: var(--accent-gold) !important;
  }

  .profit-up {
    color: var(--color-up) !important;
  }
</style>
