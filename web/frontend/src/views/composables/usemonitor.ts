import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useApiService } from '@/composables/useApiService'
import { PageHeader, StockListTable } from '@/components/shared'
import type { TableColumn } from '@/components/shared'

// Define service status type instead of using any
interface ServiceStatus {
  frontend: 'normal' | 'warning'
  api: 'normal' | 'warning'
  postgresql: 'normal' | 'warning'
  tdengine: 'normal' | 'warning'
  overallStatus: 'normal' | 'warning'
}

interface HealthData {
  frontend: number
  frontendResponseTime: number
  api: number
  postgresql: string
  tdengine: string
  [key: string]: unknown
}

interface HistoryRow {
  timestamp: number
  frontend: number | string
  api: number | string
  postgresql: number | string
  tdengine: number | string
  overallStatus: 'normal' | 'warning'
  [key: string]: unknown
}

export function usemonitor() {

const { getHealthData } = useApiService()

const autoRefresh = ref(false)
const refreshInterval = ref(60000)
const isLoading = ref(false)
const error = ref<string | null>(null)

const services = ref({
  frontend: 'normal' as 'normal' | 'warning',
  api: 'normal' as 'normal' | 'warning',
  postgresql: 'normal' as 'normal' | 'warning',
  tdengine: 'warning' as 'normal' | 'warning'
})

const servicesData = ref<{
  frontend: { responseTime: number } | null
  api: { status: string } | null
  postgresql: { status: string } | null
  tdengine: { status: string } | null
}>({
  frontend: null,
  api: null,
  postgresql: null,
  tdengine: null
})

const historyData = ref<unknown[]>([])

const FRONTEND_URL = 'http://localhost:3000'
const API_BASE_URL = 'http://localhost:8000'

// 历史表格列配置
const historyColumns = computed((): unknown[] => [
  {
    prop: 'timestamp',
    label: '时间',
    width: 180,
    formatter: (row: HistoryRow, column: TableColumn, cellValue: number, _index: number) => formatDateTime(cellValue)
  },
  {
    prop: 'frontend',
    label: '前端',
    width: 80,
    align: 'center',
    formatter: (row: HistoryRow, column: TableColumn, cellValue: number | string, _index: number) => getStatusText(cellValue)
  },
  {
    prop: 'api',
    label: 'API',
    width: 80,
    align: 'center',
    formatter: (row: HistoryRow, column: TableColumn, cellValue: number | string, _index: number) => getStatusText(cellValue)
  },
  {
    prop: 'postgresql',
    label: 'PostgreSQL',
    width: 100,
    align: 'center',
    formatter: (row: HistoryRow, column: TableColumn, cellValue: number | string, _index: number) => getStatusText(cellValue)
  },
  {
    prop: 'tdengine',
    label: 'TDengine',
    width: 100,
    align: 'center',
    formatter: (row: HistoryRow, column: TableColumn, cellValue: number | string, _index: number) => getStatusText(cellValue)
  },
  {
    prop: 'overallStatus',
    label: '整体状态',
    width: 100,
    align: 'center',
    colorClass: (row: HistoryRow) => row.overallStatus === 'normal' ? 'status-normal' : 'status-warning',
    formatter: (row: HistoryRow, column: TableColumn, cellValue: string, _index: number) => cellValue === 'normal' ? '正常' : '异常'
  }
])

const isSystemHealthy = computed(() => {
  return Object.values(services.value).every(status => status === 'normal')
})

const systemStatusMessage = computed(() => {
  if (isSystemHealthy.value) {
    return '所有服务运行正常，没有检测到问题'
  } else {
    const issues = Object.entries(services.value)
      .filter(([_, value]) => value !== 'normal')
      .map(([key]) => {
        switch(key) {
          case 'frontend': return '前端服务'
          case 'api': return 'API服务'
          case 'postgresql': return 'PostgreSQL'
          case 'tdengine': return 'TDengine'
          default: return key
        }
      })
      .join('、')

    return `检测到问题: ${issues}`
  }
})

const formatDateTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

const getStatusText = (status: number | string): string => {
  if (typeof status === 'number') {
    return status === 200 ? '✓' : '⚠'
  }
  return status === 'normal' ? '✓' : '⚠'
}

const getServiceStatusText = (status: 'normal' | 'warning'): string => {
  return status === 'normal' ? '正常' : '警告'
}

const checkService = async (serviceName: 'frontend' | 'api' | 'postgresql' | 'tdengine') => {
  try {
    isLoading.value = true
    error.value = null

    const healthData = await getHealthData() as HealthData

    if (serviceName === 'frontend') {
      services.value.frontend = healthData.frontend === 200 ? 'normal' : 'warning'
      servicesData.value.frontend = {
        responseTime: healthData.frontendResponseTime
      }
    } else if (serviceName === 'api') {
      services.value.api = healthData.api === 200 ? 'normal' : 'warning'
      servicesData.value.api = {
        status: healthData.api === 200 ? '正常' : '异常'
      }
    } else if (serviceName === 'postgresql') {
      services.value.postgresql = healthData.postgresql === '正常' ? 'normal' : 'warning'
      servicesData.value.postgresql = {
        status: healthData.postgresql
      }
    } else if (serviceName === 'tdengine') {
      services.value.tdengine = healthData.tdengine === '可访问' ? 'normal' : 'warning'
      servicesData.value.tdengine = {
        status: healthData.tdengine
      }
    }

    addToHistory(healthData)
  } catch (err: unknown) {
    console.error(`检查服务 ${serviceName} 失败:`, err)
    const errorMsg = err instanceof Error ? err.message : String(err)
    error.value = `检查服务 ${serviceName} 失败: ${errorMsg}`
  } finally {
    isLoading.value = false
  }
}

const refreshData = async () => {
  try {
    isLoading.value = true
    error.value = null

    const healthData = await getHealthData() as HealthData

    services.value.frontend = healthData.frontend === 200 ? 'normal' : 'warning'
    services.value.api = healthData.api === 200 ? 'normal' : 'warning'
    services.value.postgresql = healthData.postgresql === '正常' ? 'normal' : 'warning'
    services.value.tdengine = healthData.tdengine === '可访问' ? 'normal' : 'warning'

    servicesData.value.frontend = {
      responseTime: healthData.frontendResponseTime
    }
    servicesData.value.api = {
      status: healthData.api === 200 ? '正常' : '异常'
    }
    servicesData.value.postgresql = {
      status: healthData.postgresql
    }
    servicesData.value.tdengine = {
      status: healthData.tdengine
    }

    addToHistory(healthData)
  } catch (err: unknown) {
    console.error('刷新数据失败:', err)
    const errorMsg = err instanceof Error ? err.message : String(err)
    error.value = `刷新数据失败: ${errorMsg}`
  } finally {
    isLoading.value = false
  }
}

const addToHistory = (healthData: HealthData) => {
  historyData.value.unshift({
    timestamp: healthData.timestamp as number,
    frontend: healthData.frontend,
    api: healthData.api,
    postgresql: healthData.postgresql,
    tdengine: healthData.tdengine,
    overallStatus: (healthData.overallStatus as 'normal' | 'warning') || 'normal'
  })

  if (historyData.value.length > 10) {
    historyData.value.pop()
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value

  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

let refreshTimer: number | null = null

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer = window.setInterval(() => {
    refreshData()
  }, refreshInterval.value)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  refreshData()

  for (let i = 1; i <= 3; i++) {
    const timestamp = Date.now() - (i * 3600000)
    const healthData: HealthData = {
      timestamp,
      frontend: 200,
      frontendResponseTime: 200,
      api: 200,
      postgresql: '正常',
      tdengine: '不可访问'
    }
    addToHistory(healthData)
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})

  return {
    autoRefresh,
    refreshInterval,
    isLoading,
    error,
    services,
    servicesData,
    historyData,
    FRONTEND_URL,
    API_BASE_URL,
    historyColumns,
    isSystemHealthy,
    systemStatusMessage,
    formatDateTime,
    getStatusText,
    getServiceStatusText,
    checkService,
    refreshData,
    addToHistory,
    toggleAutoRefresh,
    startAutoRefresh,
    stopAutoRefresh,
  }
}
