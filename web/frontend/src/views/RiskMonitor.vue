<template>
  <div class="risk-monitor">

    <!-- 页面头部 -->
    <PageHeader
      title="RISK MANAGEMENT DASHBOARD"
      subtitle="REAL-TIME RISK MONITORING | VaR | CVaR | BETA ANALYSIS"
    />

    <!-- 统计卡片网格 -->
    <div class="metrics-grid">
        :title="stats[0].title"
        :value="stats[0].value"
        :icon="stats[0].icon"
        :color="stats[0].color"
        :description="stats[0].description"
        hoverable
      />
        :title="stats[1].title"
        :value="stats[1].value"
        :icon="stats[1].icon"
        :color="stats[1].color"
        :description="stats[1].description"
        hoverable
      />
        :title="stats[2].title"
        :value="stats[2].value"
        :icon="stats[2].icon"
        :color="stats[2].color"
        :description="stats[2].description"
        hoverable
      />
        :title="stats[3].title"
        :value="stats[3].value"
        :icon="stats[3].icon"
        :color="stats[3].color"
        :description="stats[3].description"
        hoverable
      />
    </div>

    <div class="content-grid">
      <el-card title="I. RISK METRICS HISTORY" hoverable>
          <template #header>
            <div class="card-header">
              <span>RISK METRICS HISTORY</span>
              <div class="header-actions">
                <el-select v-model="historyPeriod" @change="loadMetricsHistory" class="select">
                  <el-option label="7 DAYS" value="7d" />
                  <el-option label="30 DAYS" value="30d" />
                  <el-option label="90 DAYS" value="90d" />
                </el-select>
                <el-button type="info" size="small" @click="loadMetricsHistory" :loading="historyLoading">
                  REFRESH
                </el-button>
              </div>
            </div>
          </template>

          <ChartContainer
            ref="riskChartRef"
            chart-type="line"
            :data="chartData"
            :options="chartOptions"
            height="300px"
            :loading="historyLoading"
          />
        </el-card>
      </div>

      <div class="content-grid">
        <el-card title="II. RISK ALERTS" hoverable>
          <template #header>
            <div class="card-header">
              <span>RISK ALERTS</span>
              <el-button type="primary" size="small" @click="showCreateAlertDialog">
                NEW ALERT
              </el-button>
            </div>
          </template>

          <el-scrollbar max-height="300px">
            <div v-if="alertsLoading" class="loading-container">
              <el-skeleton :rows="3" animated />
            </div>

            <div v-else-if="alerts.length > 0" class="alerts-list">
              <div v-for="alert in alerts" :key="alert.id" class="alert-item">
                <div class="alert-header">
                  <el-tag :type="getAlertBadgeVariant(alert.level)">
                    {{ alert.level.toUpperCase() }}
                  </el-tag>
                  <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
                </div>
                <div class="alert-content">
                  <p class="alert-title">{{ alert.title }}</p>
                  <p class="alert-description">{{ alert.description }}</p>
                </div>
                <div class="alert-actions">
                  <el-button type="info" size="small" @click="viewAlertDetail(alert)">
                    VIEW DETAILS
                  </el-button>
                </div>
              </div>
            </div>

            <el-empty v-else description="NO ACTIVE ALERTS" :image-size="80" />
          </el-scrollbar>
        </el-card>
      </div>

      <div class="content-grid-half">
      <el-card title="III. VaR RISK ANALYSIS" hoverable>
          <template #header>
            <div class="card-header">
              <span>VaR RISK ANALYSIS</span>
              <el-button type="info" size="small" @click="loadVarCvar">
                REFRESH
              </el-button>
            </div>
          </template>

          <el-table
            :columns="varColumns"
            :data="varData"
            :loading="varLoading"
          >
            <template #cell-confidence_level="{ row }">
              {{ row.confidence_level }}%
            </template>
            <template #cell-var="{ row }">
              <span :class="getRiskClass(row.var)">
                {{ row.var?.toFixed(2) }}%
              </span>
            </template>
            <template #cell-cvar="{ row }">
              <span :class="getRiskClass(row.cvar)">
                {{ row.cvar?.toFixed(2) }}%
              </span>
            </template>
            <template #cell-risk_level="{ row }">
              <el-tag :type="getRiskBadgeVariant(row.var)">
                {{ getRiskLevel(row.var) }}
              </el-tag>
            </template>
          </el-table>
        </el-card>

        <el-card title="IV. BETA COEFFICIENT" hoverable>
          <template #header>
            <div class="card-header">
              <span>BETA COEFFICIENT</span>
              <el-button type="info" size="small" @click="loadBeta">
                REFRESH
              </el-button>
            </div>
          </template>

          <el-table
            :columns="betaColumns"
            :data="betaData"
            :loading="betaLoading"
          >
            <template #cell-beta="{ row }">
              <span :class="getBetaClass(row.beta)">
                {{ row.beta?.toFixed(3) }}
              </span>
            </template>
            <template #cell-volatility="{ row }">
              <el-tag :type="getBetaBadgeVariant(row.beta)">
                {{ getBetaDescription(row.beta) }}
              </el-tag>
            </template>
          </el-table>
        </el-card>
      </div>

    <!-- 创建告警对话框 -->
    <DetailDialog
      v-model:visible="createAlertVisible"
      title="CREATE RISK ALERT RULE"
      :confirming="createAlertLoading"
      @confirm="handleCreateAlert"
    >
      <el-form :model="alertForm" label-width="120px" label-position="top">
        <el-form-item label="ALERT NAME">
          <el-input v-model="alertForm.title" placeholder="ENTER ALERT NAME" />
        </el-form-item>
        <el-form-item label="METRIC TYPE">
          <el-select v-model="alertForm.metric_type" class="select-full">
            <el-option label="VaR (95%)" value="var_95" />
            <el-option label="CVaR (95%)" value="cvar_95" />
            <el-option label="Beta Coefficient" value="beta" />
            <el-option label="Volatility" value="volatility" />
          </el-select>
        </el-form-item>
        <el-form-item label="THRESHOLD">
          <el-input-number v-model="alertForm.threshold" :precision="2" :step="0.1" class="input-number-full" />
        </el-form-item>
        <el-form-item label="ALERT LEVEL">
          <el-select v-model="alertForm.level" class="select-full">
            <el-option label="LOW" value="low" />
            <el-option label="MEDIUM" value="medium" />
            <el-option label="HIGH" value="high" />
            <el-option label="CRITICAL" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="DESCRIPTION">
          <el-input
            v-model="alertForm.description"
            type="textarea"
            :rows="3"
            placeholder="ALERT RULE DESCRIPTION"
          />
        </el-form-item>
      </el-form>
    </DetailDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, type Ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  Warning,
  DataLine,
  BellFilled,
} from '@element-plus/icons-vue'
import { riskApi } from '@/api'
import { ElCard } from 'element-plus'
import { ElButton } from 'element-plus'
import { ElInput } from 'element-plus'
import { ElTable, ElTableColumn } from 'element-plus'

interface RiskDashboard {
  var_95: number
  cvar_95: number
  beta: number
  alert_count: number
}

interface MetricsHistoryPoint {
  date: string
  var_95_hist?: number
  cvar_95?: number
  beta?: number
}

type AlertLevel = 'low' | 'medium' | 'high' | 'critical'

interface Alert {
  id: number
  title: string
  metric_type: string
  threshold: number
  level: AlertLevel
  description: string
  created_at?: string
  triggered_at?: string
}

interface VarCvarData {
  symbol?: string
  stock_name?: string
  confidence_level?: number
  var: number | null
  cvar: number | null
  date?: string
}

interface BetaData {
  symbol: string
  stock_name?: string
  beta: number | null
  date?: string
}

interface AlertForm {
  title: string
  metric_type: string
  threshold: number
  level: AlertLevel
  description: string
}

const dashboard: Ref<RiskDashboard> = ref({
  var_95: 0,
  cvar_95: 0,
  beta: 0,
  alert_count: 0
})

const historyPeriod: Ref<string> = ref('30d')
const historyLoading: Ref<boolean> = ref(false)
const metricsHistory: Ref<MetricsHistoryPoint[]> = ref([])
const alertsLoading: Ref<boolean> = ref(false)
const alerts: Ref<Alert[]> = ref([])
const varLoading: Ref<boolean> = ref(false)
const varData: Ref<VarCvarData[]> = ref([])
const betaLoading: Ref<boolean> = ref(false)
const betaData: Ref<BetaData[]> = ref([])
const createAlertVisible: Ref<boolean> = ref(false)
const createAlertLoading: Ref<boolean> = ref(false)
const alertForm: Ref<AlertForm> = ref({
  title: '',
  metric_type: 'var_95',
  threshold: 5.0,
  level: 'medium',
  description: ''
})

// 统计卡片数据
const stats = computed(() => [
  {
    title: 'VaR (95%)',
    value: `${dashboard.value.var_95.toFixed(2)}%`,
    icon: TrendCharts,
    color: 'orange' as const,
    description: 'Value at Risk'
  },
  {
    title: 'CVaR (95%)',
    value: `${dashboard.value.cvar_95.toFixed(2)}%`,
    icon: Warning,
    color: 'gold' as const,
    description: 'Conditional VaR'
  },
  {
    title: 'BETA COEFFICIENT',
    value: dashboard.value.beta.toFixed(3),
    icon: DataLine,
    color: 'blue' as const,
    description: 'Market Volatility'
  },
  {
    title: 'ACTIVE ALERTS',
    value: dashboard.value.alert_count.toString(),
    icon: BellFilled,
    color: 'green' as const,
    description: 'Risk Warnings'
  }
])

// 图表数据（为 ChartContainer 准备）
const chartData = computed(() => {
  if (!metricsHistory.value || metricsHistory.value.length === 0) return []

  const dates = metricsHistory.value.map(item => item.date)
  const varValues = metricsHistory.value.map(item => item.var_95_hist || 0)
  const cvarValues = metricsHistory.value.map(item => item.cvar_95 || 0)
  const betaValues = metricsHistory.value.map(item => (item.beta || 0) * 10)

  return [
    { name: 'VaR (95%)', data: varValues.map((v, i) => ({ name: dates[i], value: v })) },
    { name: 'CVaR (95%)', data: cvarValues.map((v, i) => ({ name: dates[i], value: v })) },
    { name: 'Beta×10', data: betaValues.map((v, i) => ({ name: dates[i], value: v })) }
  ]
})

const chartOptions = computed(() => ({
  xAxis: {
    type: 'category',
    data: metricsHistory.value.map(item => item.date),
    axisLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.5)' } },
    axisLabel: { color: '#94A3B8' }
  },
  yAxis: {
    type: 'value',
    name: 'RISK VALUE (%)',
    axisLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.5)' } },
    axisLabel: { color: '#94A3B8' },
    splitLine: { lineStyle: { color: 'rgba(212, 175, 55, 0.3)' } }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' },
    backgroundColor: 'rgba(3, 3, 4, 0.95)',
    borderColor: '#D4AF37',
    textStyle: { color: '#F2F0E4' }
  },
  legend: {
    data: ['VaR (95%)', 'CVaR (95%)', 'Beta×10'],
    textStyle: { color: '#F2F0E4' }
  }
}))

// Define columns for DataTable
const varColumns = [
  {
    key: 'confidence_level',
    label: 'CONFIDENCE',
    sortable: true
  },
  {
    key: 'var',
    label: 'VaR',
    sortable: true,
    class: (row: VarCvarData) => getRiskClass(row.var)
  },
  {
    key: 'cvar',
    label: 'CVaR',
    sortable: true,
    class: (row: VarCvarData) => getRiskClass(row.cvar)
  },
  {
    key: 'risk_level',
    label: 'RISK LEVEL'
  }
]

const betaColumns = [
  {
    key: 'symbol',
    label: 'SYMBOL',
    sortable: true
  },
  {
    key: 'stock_name',
    label: 'NAME',
    sortable: true
  },
  {
    key: 'beta',
    label: 'BETA',
    sortable: true,
    class: (row: BetaData) => getBetaClass(row.beta)
  },
  {
    key: 'volatility',
    label: 'VOLATILITY'
  }
]

const loadDashboard = async (): Promise<void> => {
  try {
    const response = await riskApi.getDashboard()
    const data = response?.data || response
    dashboard.value = {
      var_95: data?.var_95 || data?.var95 || 0,
      cvar_95: data?.cvar_95 || data?.cvar95 || 0,
      beta: data?.beta || 0,
      alert_count: data?.alert_count || data?.alertCount || 0
    }
  } catch (error) {
    console.error('加载仪表板失败:', error)
    dashboard.value = { var_95: 3.5, cvar_95: 5.2, beta: 1.1, alert_count: 2 }
  }
}

const loadMetricsHistory = async (): Promise<void> => {
  historyLoading.value = true
  try {
    const response = await riskApi.getMetricsHistory({ period: historyPeriod.value })
    const data = response?.data || response
    metricsHistory.value = Array.isArray(data) ? data : (data?.history || data?.data || [])
  } catch (error) {
    console.error('加载历史数据失败:', error)
    ElMessage.error('FAILED TO LOAD HISTORICAL DATA')
    metricsHistory.value = generateMockHistoryData()
  } finally {
    historyLoading.value = false
  }
}

const generateMockHistoryData = (): MetricsHistoryPoint[] => {
  const data: MetricsHistoryPoint[] = []
  const now = new Date()

  for (let i = 29; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    data.push({
      date: date.toISOString().split('T')[0],
      var_95_hist: 2.5 + Math.random() * 2,
      cvar_95: 3.5 + Math.random() * 2.5,
      beta: 0.9 + Math.random() * 0.4
    })
  }
  return data
}

const loadAlerts = async (): Promise<void> => {
  alertsLoading.value = true
  try {
    const response = await riskApi.getAlerts({ limit: 10 })
    const data = response?.data || response
    alerts.value = Array.isArray(data) ? data : (data?.alerts || data?.data || [])
  } catch (error) {
    console.error('加载告警失败:', error)
    alerts.value = generateMockAlerts()
  } finally {
    alertsLoading.value = false
  }
}

const generateMockAlerts = (): Alert[] => {
  return [
    {
      id: 1,
      title: 'VaR超过阈值',
      metric_type: 'var_95',
      threshold: 5.0,
      level: 'high',
      description: '当前VaR值(5.2%)已超过设置的阈值(5.0%)',
      created_at: new Date().toISOString()
    },
    {
      id: 2,
      title: 'Beta系数异常',
      metric_type: 'beta',
      threshold: 1.5,
      level: 'medium',
      description: '投资组合Beta系数(1.45)接近阈值',
      created_at: new Date(Date.now() - 3600000).toISOString()
    }
  ]
}

const loadVarCvar = async (): Promise<void> => {
  varLoading.value = true
  try {
    const response = await riskApi.getVarCvar()
    const data = response?.data || response
    varData.value = Array.isArray(data) ? data : (data?.varCvar || data?.data || [])
  } catch (error) {
    console.error('加载VaR/CVaR失败:', error)
    varData.value = [
      { confidence_level: 90, var: 2.8, cvar: 4.0 },
      { confidence_level: 95, var: 4.2, cvar: 5.8 },
      { confidence_level: 99, var: 6.5, cvar: 8.2 }
    ]
  } finally {
    varLoading.value = false
  }
}

const loadBeta = async (): Promise<void> => {
  betaLoading.value = true
  try {
    const response = await riskApi.getBeta()
    const data = response?.data || response
    betaData.value = Array.isArray(data) ? data : (data?.beta || data?.data || [])
  } catch (error) {
    console.error('加载Beta失败:', error)
    betaData.value = [
      { symbol: '600519', stock_name: '贵州茅台', beta: 1.25 },
      { symbol: '000001', stock_name: '平安银行', beta: 0.95 },
      { symbol: '000002', stock_name: '万科A', beta: 1.15 }
    ]
  } finally {
    betaLoading.value = false
  }
}

const showCreateAlertDialog = (): void => {
  alertForm.value = {
    title: '',
    metric_type: 'var_95',
    threshold: 5.0,
    level: 'medium',
    description: ''
  }
  createAlertVisible.value = true
}

const handleCreateAlert = async (): Promise<void> => {
  if (!alertForm.value.title) {
    ElMessage.warning('PLEASE ENTER ALERT NAME')
    return
  }

  createAlertLoading.value = true
  try {
    const response = await riskApi.createAlert(alertForm.value)
    const result = response?.data || response
    if (result && result.id) {
      ElMessage.success('ALERT CREATED SUCCESSFULLY')
      createAlertVisible.value = false
      loadAlerts()
    } else {
      ElMessage.error(result?.message || 'CREATION FAILED')
    }
  } catch (error: any) {
    console.error('Failed to create alert:', error)
    ElMessage.error('FAILED TO CREATE ALERT')
  } finally {
    createAlertLoading.value = false
  }
}

const viewAlertDetail = (alert: Alert): void => {
  ElMessage.info(`VIEWING ALERT DETAILS: ${alert.title}`)
}

const getAlertBadgeVariant = (level: AlertLevel): 'info' | 'warning' | 'danger' | 'success' => {
  const variantMap: Record<AlertLevel, 'info' | 'warning' | 'danger' | 'success'> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return variantMap[level] || 'info'
}

const getRiskBadgeVariant = (var95: number | null): 'info' | 'warning' | 'danger' | 'success' => {
  if (!var95) return 'info'
  if (var95 > 10) return 'danger'
  if (var95 > 7) return 'warning'
  if (var95 > 5) return 'info'
  return 'success'
}

const getRiskLevel = (var95: number | null): string => {
  if (!var95) return 'UNKNOWN'
  if (var95 > 10) return 'CRITICAL'
  if (var95 > 7) return 'HIGH'
  if (var95 > 5) return 'MEDIUM'
  return 'LOW'
}

const getRiskClass = (value: number | null): string => {
  if (!value) return ''
  if (value > 10) return 'risk-critical'
  if (value > 7) return 'risk-high'
  if (value > 5) return 'risk-medium'
  return 'risk-low'
}

const getBetaBadgeVariant = (beta: number | null): 'info' | 'warning' | 'danger' | 'success' => {
  if (!beta) return 'info'
  if (beta > 1.5) return 'danger'
  if (beta > 1.2) return 'warning'
  if (beta < 0.8) return 'success'
  return 'info'
}

const getBetaClass = (beta: number | null): string => {
  if (!beta) return ''
  if (beta > 1.5) return 'beta-high'
  if (beta < 0.5) return 'beta-low'
  return 'beta-normal'
}

const getBetaDescription = (beta: number | null): string => {
  if (!beta) return 'UNKNOWN'
  if (beta > 1.5) return 'HIGH VOLATILITY'
  if (beta > 1.2) return 'MODERATE HIGH'
  if (beta > 0.8) return 'NORMAL'
  if (beta > 0.5) return 'LOW VOLATILITY'
  return 'VERY LOW'
}

const formatTime = (time: string | Date): string => {
  if (!time) return '-'
  const date = new Date(time)
  return `${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted((): void => {
  loadDashboard()
  loadMetricsHistory()
  loadAlerts()
  loadVarCvar()
  loadBeta()
})
</script>

<style scoped lang="scss">

  min-height: 100vh;
  padding: var(--space-section);
  position: relative;
  background: var(--bg-global);

    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: var(--z-bg-pattern);
    opacity: 0.04;
    background-image:
      repeating-linear-gradient(
        45deg,
        var(--gold-primary) 0px,
        var(--gold-primary) 1px,
        transparent 1px,
        transparent 10px
      ),
      repeating-linear-gradient(
        -45deg,
        var(--gold-primary) 0px,
        var(--gold-primary) 1px,
        transparent 1px,
        transparent 10px
      );
  }

    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-section);
    position: relative;
    z-index: 1;
  }

  .content-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-section);
    position: relative;
    z-index: 1;

    @media (max-width: 1200px) {
      grid-template-columns: 1fr;
    }
  }

  .content-grid-half {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-section);
    position: relative;
    z-index: 1;

    @media (max-width: 1200px) {
      grid-template-columns: 1fr;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-4);
    width: 100%;

    .header-actions {
      display: flex;
      gap: var(--space-2);
      align-items: center;
    }
  }

  .loading-container {
    padding: var(--space-4);
    text-align: center;
  }

  .chart-container {
    width: 100%;
    height: 300px;
  }

  #risk-chart {
    width: 100%;
    height: 100%;
  }

  .alerts-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4);

    .alert-item {
      background: rgba(212, 175, 55, 0.05);
      border: 1px solid rgba(212, 175, 55, 0.2);
      padding: var(--space-3);
      border-radius: var(--radius-sm);

      .alert-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-2);

        .alert-time {
          font-size: var(--font-size-xs);
          color: var(--silver-dim);
        }
      }

      .alert-content {
        margin-bottom: var(--space-2);

        .alert-title {
          font-family: var(--font-display);
          font-size: var(--font-size-sm);
          font-weight: 600;
          color: var(--gold-primary);
          margin: 0 0 var(--space-1) 0;
        }

        .alert-description {
          font-size: var(--font-size-xs);
          color: var(--silver-muted);
          margin: 0;
        }
      }

      .alert-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--space-2);
      }
    }
  }

  .select {
    width: 120px;
  }

  .select-full {
    width: 100%;
  }

  .input-number-full {
    width: 100%;
  }

  // Risk level colors
  .risk-critical { color: #EF4444; }
  .risk-high { color: #F97316; }
  .risk-medium { color: #EAB308; }
  .risk-low { color: #22C55E; }

  // Beta level colors
  .beta-high { color: #EF4444; }
  .beta-normal { color: var(--gold-primary); }
  .beta-low { color: #3B82F6; }
}

@media (max-width: 768px) {
    padding: var(--space-3);

      grid-template-columns: 1fr;
    }

    .content-grid,
    .content-grid-half {
      grid-template-columns: 1fr;
    }

    .card-header {
      flex-direction: column;
      align-items: flex-start;

      .header-actions {
        width: 100%;
        flex-direction: column;
      }
    }
  }
}
</style>
