<template>
  <div class="web3-risk-monitor">
    <!-- Page Header with Gradient Text -->
    <div class="page-header">
      <h1 class="text-4xl font-heading font-semibold">
        <span class="bg-gradient-to-r from-[#F7931A] to-[#FFD600] bg-clip-text text-transparent">
          RISK MANAGEMENT DASHBOARD
        </span>
      </h1>
      <p class="subtitle">REAL-TIME RISK MONITORING | VaR | CVaR | BETA ANALYSIS</p>
    </div>

    <!-- Key Metrics Overview with Web3 Cards -->
    <el-row :gutter="20" class="metrics-overview">
      <el-col :span="6">
        <Web3Card class="metric-card hover-lift">
          <div class="metric-content">
            <div class="metric-icon-wrapper risk-var">
              <el-icon class="metric-icon"><TrendCharts /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">VaR (95%)</div>
              <div class="metric-value orange-glow">{{ dashboard.var_95.toFixed(2) }}%</div>
              <div class="metric-description">Value at Risk</div>
            </div>
          </div>
        </Web3Card>
      </el-col>
      <el-col :span="6">
        <Web3Card class="metric-card hover-lift">
          <div class="metric-content">
            <div class="metric-icon-wrapper risk-cvar">
              <el-icon class="metric-icon"><Warning /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">CVaR (95%)</div>
              <div class="metric-value yellow-glow">{{ dashboard.cvar_95.toFixed(2) }}%</div>
              <div class="metric-description">Conditional VaR</div>
            </div>
          </div>
        </Web3Card>
      </el-col>
      <el-col :span="6">
        <Web3Card class="metric-card hover-lift">
          <div class="metric-content">
            <div class="metric-icon-wrapper risk-beta">
              <el-icon class="metric-icon"><DataLine /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">BETA COEFFICIENT</div>
              <div class="metric-value blue-glow">{{ dashboard.beta.toFixed(3) }}</div>
              <div class="metric-description">Market Volatility</div>
            </div>
          </div>
        </Web3Card>
      </el-col>
      <el-col :span="6">
        <Web3Card class="metric-card hover-lift">
          <div class="metric-content">
            <div class="metric-icon-wrapper risk-alert">
              <el-icon class="metric-icon"><BellFilled /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">ACTIVE ALERTS</div>
              <div class="metric-value green-glow">{{ dashboard.alert_count }}</div>
              <div class="metric-description">Risk Warnings</div>
            </div>
          </div>
        </Web3Card>
      </el-col>
    </el-row>

    <!-- Main Content Area -->
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- Left: Risk Metrics History Chart -->
      <el-col :span="16">
        <Web3Card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="section-title">I. RISK METRICS HISTORY</span>
              <div class="card-actions">
                <el-select v-model="historyPeriod" @change="loadMetricsHistory" class="web3-select" style="width: 120px">
                  <el-option label="7 DAYS" value="7d" />
                  <el-option label="30 DAYS" value="30d" />
                  <el-option label="90 DAYS" value="90d" />
                </el-select>
                <Web3Button variant="outline" size="sm" @click="loadMetricsHistory" :loading="historyLoading">
                  <el-icon><Refresh /></el-icon> REFRESH
                </Web3Button>
              </div>
            </div>
          </template>

          <div v-if="historyLoading" style="height: 300px; display: flex; align-items: center; justify-content: center">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="metricsHistory.length > 0" class="chart-container grid-bg">
            <div id="risk-chart" style="height: 300px"></div>
          </div>

          <el-empty v-else description="NO HISTORICAL DATA AVAILABLE" />
        </Web3Card>
      </el-col>

      <!-- Right: Risk Alerts -->
      <el-col :span="8">
        <Web3Card class="alerts-card">
          <template #header>
            <div class="card-header">
              <span class="section-title">II. RISK ALERTS</span>
              <Web3Button variant="primary" size="sm" @click="showCreateAlertDialog">
                <el-icon><Plus /></el-icon> NEW ALERT
              </Web3Button>
            </div>
          </template>

          <el-scrollbar max-height="300px">
            <div v-if="alertsLoading" class="alerts-loading">
              <el-skeleton :rows="3" animated />
            </div>

            <div v-else-if="alerts.length > 0" class="alerts-list">
              <div v-for="alert in alerts" :key="alert.id" class="alert-item corner-border">
                <div class="alert-header">
                  <el-tag :type="getAlertType(alert.level)" size="small" class="web3-tag">
                    {{ alert.level }}
                  </el-tag>
                  <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
                </div>
                <div class="alert-content">
                  <p class="alert-title">{{ alert.title }}</p>
                  <p class="alert-description">{{ alert.description }}</p>
                </div>
                <div class="alert-actions">
                  <Web3Button variant="ghost" size="sm" @click="viewAlertDetail(alert)">
                    VIEW DETAILS
                  </Web3Button>
                </div>
              </div>
            </div>

            <el-empty v-else description="NO ACTIVE ALERTS" :image-size="80" />
          </el-scrollbar>
        </Web3Card>
      </el-col>
    </el-row>

    <!-- VaR/CVaR Detailed Analysis -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <Web3Card class="var-card">
          <template #header>
            <div class="card-header">
              <span class="section-title">III. VaR RISK ANALYSIS</span>
              <Web3Button variant="outline" size="sm" @click="loadVarCvar">
                <el-icon><Refresh /></el-icon> REFRESH
              </Web3Button>
            </div>
          </template>

          <el-table :data="varData" v-loading="varLoading" class="web3-table">
            <el-table-column prop="confidence_level" label="CONFIDENCE" width="100">
              <template #default="scope">
                {{ scope.row.confidence_level }}%
              </template>
            </el-table-column>
            <el-table-column prop="var" label="VaR" align="right">
              <template #default="scope">
                <span :class="getRiskClass(scope.row.var)">
                  {{ scope.row.var?.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="cvar" label="CVaR" align="right">
              <template #default="scope">
                <span :class="getRiskClass(scope.row.cvar)">
                  {{ scope.row.cvar?.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="RISK LEVEL" align="center">
              <template #default="scope">
                <el-tag :type="getRiskLevelType(scope.row.var)" size="small" class="web3-tag">
                  {{ getRiskLevel(scope.row.var) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </Web3Card>
      </el-col>

      <el-col :span="12">
        <Web3Card class="beta-card">
          <template #header>
            <div class="card-header">
              <span class="section-title">IV. BETA COEFFICIENT</span>
              <Web3Button variant="outline" size="sm" @click="loadBeta">
                <el-icon><Refresh /></el-icon> REFRESH
              </Web3Button>
            </div>
          </template>

          <el-table :data="betaData" v-loading="betaLoading" class="web3-table">
            <el-table-column prop="symbol" label="SYMBOL" width="100" />
            <el-table-column prop="stock_name" label="NAME" width="120" />
            <el-table-column prop="beta" label="BETA" align="right">
              <template #default="scope">
                <span :class="getBetaClass(scope.row.beta)">
                  {{ scope.row.beta?.toFixed(3) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="VOLATILITY" align="center">
              <template #default="scope">
                <el-tag :type="getBetaType(scope.row.beta)" size="small" class="web3-tag">
                  {{ getBetaDescription(scope.row.beta) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </Web3Card>
      </el-col>
    </el-row>

    <!-- Create Alert Dialog -->
    <el-dialog
      v-model="createAlertVisible"
      title="CREATE RISK ALERT RULE"
      width="500px"
      class="web3-dialog"
    >
      <el-form :model="alertForm" label-width="100px">
        <el-form-item label="ALERT NAME">
          <Web3Input v-model="alertForm.title" placeholder="ENTER ALERT NAME" />
        </el-form-item>

        <el-form-item label="METRIC TYPE">
          <el-select v-model="alertForm.metric_type" placeholder="SELECT MONITORING METRIC" class="web3-select" style="width: 100%">
            <el-option label="VaR (95%)" value="var_95" />
            <el-option label="CVaR (95%)" value="cvar_95" />
            <el-option label="Beta Coefficient" value="beta" />
            <el-option label="Volatility" value="volatility" />
          </el-select>
        </el-form-item>

        <el-form-item label="THRESHOLD">
          <el-input-number v-model="alertForm.threshold" :precision="2" :step="0.1" class="web3-input-number" />
        </el-form-item>

        <el-form-item label="ALERT LEVEL">
          <el-select v-model="alertForm.level" class="web3-select" style="width: 100%">
            <el-option label="LOW" value="low" />
            <el-option label="MEDIUM" value="medium" />
            <el-option label="HIGH" value="high" />
            <el-option label="CRITICAL" value="critical" />
          </el-select>
        </el-form-item>

        <el-form-item label="DESCRIPTION">
          <Web3Input
            v-model="alertForm.description"
            type="textarea"
            :rows="3"
            placeholder="ALERT RULE DESCRIPTION"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <Web3Button variant="ghost" @click="createAlertVisible = false">CANCEL</Web3Button>
        <Web3Button variant="primary" @click="handleCreateAlert" :loading="createAlertLoading">
          CREATE ALERT
        </Web3Button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  Warning,
  DataLine,
  BellFilled,
  Refresh,
  Plus
} from '@element-plus/icons-vue'
import { riskApi } from '@/api'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import type { EChartsOption } from '@/types/echarts'
import { Web3Button, Web3Card, Web3Input } from '@/components/web3'

// Type definitions remain the same
interface RiskDashboard {
  var_95: number
  cvar_95: number
  beta: number
  alert_count: number
}

interface MetricsHistoryPoint {
  date: string
  var_95: number
  cvar_95: number
  beta: number
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
  symbol: string
  var_95: number
  cvar_95: number
  date: string
}

interface BetaData {
  symbol: string
  beta: number
  date: string
  stock_name?: string
}

interface AlertForm {
  title: string
  metric_type: string
  threshold: number
  level: AlertLevel
  description: string
}

type TagType = "primary" | "success" | "warning" | "info" | "danger"
type RiskLevel = '低' | '中' | '高' | '极高' | '未知'

// Reactive state
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

let chartInstance: ECharts | null = null

// Data loading methods
const loadDashboard = async (): Promise<void> => {
  try {
    const response = await riskApi.getDashboard()
    if (response.data.success) {
      dashboard.value = response.data.data
    }
  } catch (error: any) {
    console.error('Failed to load dashboard:', error)
  }
}

const loadMetricsHistory = async (): Promise<void> => {
  historyLoading.value = true
  try {
    const response = await riskApi.getMetricsHistory({
      period: historyPeriod.value
    })
    if (response.data.success) {
      metricsHistory.value = response.data.data
      renderChart()
    }
  } catch (error: any) {
    console.error('Failed to load history:', error)
    ElMessage.error('FAILED TO LOAD HISTORICAL DATA')
  } finally {
    historyLoading.value = false
  }
}

const loadAlerts = async (): Promise<void> => {
  alertsLoading.value = true
  try {
    const response = await riskApi.getAlerts({ limit: 10 })
    if (response.data.success) {
      alerts.value = response.data.data
    }
  } catch (error: any) {
    console.error('Failed to load alerts:', error)
  } finally {
    alertsLoading.value = false
  }
}

const loadVarCvar = async (): Promise<void> => {
  varLoading.value = true
  try {
    const response = await riskApi.getVarCvar()
    if (response.data.success) {
      varData.value = response.data.data
    }
  } catch (error: any) {
    console.error('Failed to load VaR/CVaR:', error)
  } finally {
    varLoading.value = false
  }
}

const loadBeta = async (): Promise<void> => {
  betaLoading.value = true
  try {
    const response = await riskApi.getBeta()
    if (response.data.success) {
      betaData.value = response.data.data
    }
  } catch (error: any) {
    console.error('Failed to load Beta:', error)
  } finally {
    betaLoading.value = false
  }
}

// Chart rendering with Web3 colors
const renderChart = (): void => {
  if (!metricsHistory.value || metricsHistory.value.length === 0) return

  const chartDom = document.getElementById('risk-chart')
  if (!chartDom) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartDom)
  }

  const dates = metricsHistory.value.map(item => item.date)
  const varValues = metricsHistory.value.map(item => item.var_95)
  const cvarValues = metricsHistory.value.map(item => item.cvar_95)
  const betaValues = metricsHistory.value.map(item => item.beta * 10)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(3, 3, 4, 0.95)',
      borderColor: '#F7931A',
      textStyle: { color: '#E5E7EB' }
    },
    legend: {
      data: ['VaR (95%)', 'CVaR (95%)', 'Beta×10'],
      textStyle: { color: '#E5E7EB' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(30, 41, 59, 0.5)' } },
      axisLabel: { color: '#94A3B8', fontFamily: 'JetBrains Mono' }
    },
    yAxis: {
      type: 'value',
      name: 'RISK VALUE (%)',
      axisLine: { lineStyle: { color: 'rgba(30, 41, 59, 0.5)' } },
      axisLabel: { color: '#94A3B8', fontFamily: 'JetBrains Mono' },
      splitLine: { lineStyle: { color: 'rgba(30, 41, 59, 0.3)' } }
    },
    series: [
      {
        name: 'VaR (95%)',
        type: 'line',
        data: varValues,
        smooth: true,
        itemStyle: { color: '#F7931A' }
      },
      {
        name: 'CVaR (95%)',
        type: 'line',
        data: cvarValues,
        smooth: true,
        itemStyle: { color: '#FFD600' }
      },
      {
        name: 'Beta×10',
        type: 'line',
        data: betaValues,
        smooth: true,
        itemStyle: { color: '#22C55E' }
      }
    ]
  }

  chartInstance?.setOption(option)
}

// Alert management
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
    if (response.data.success) {
      ElMessage.success('ALERT CREATED SUCCESSFULLY')
      createAlertVisible.value = false
      loadAlerts()
    } else {
      ElMessage.error(response.data.message || 'CREATION FAILED')
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

const getAlertType = (level: AlertLevel): TagType => {
  const typeMap: Record<AlertLevel, TagType> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return typeMap[level] || 'info'
}

// Utility functions
const formatTime = (time: string | Date): string => {
  if (!time) return '-'
  const date = new Date(time)
  return `${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

const getRiskLevel = (var95: number | null): RiskLevel => {
  if (!var95) return '未知'
  if (var95 > 10) return '极高'
  if (var95 > 7) return '高'
  if (var95 > 5) return '中'
  return '低'
}

const getRiskLevelType = (var95: number | null): TagType => {
  if (!var95) return 'info'
  if (var95 > 10) return 'danger'
  if (var95 > 7) return 'warning'
  if (var95 > 5) return 'info'
  return 'success'
}

const getRiskClass = (value: number | null): string => {
  if (!value) return ''
  if (value > 10) return 'risk-critical'
  if (value > 7) return 'risk-high'
  if (value > 5) return 'risk-medium'
  return 'risk-low'
}

const getBetaClass = (beta: number | null): string => {
  if (!beta) return ''
  if (beta > 1.5) return 'beta-high'
  if (beta < 0.5) return 'beta-low'
  return 'beta-normal'
}

const getBetaType = (beta: number | null): TagType => {
  if (!beta) return 'info'
  if (beta > 1.5) return 'danger'
  if (beta > 1.2) return 'warning'
  if (beta < 0.8) return 'success'
  return 'primary'
}

const getBetaDescription = (beta: number | null): string => {
  if (!beta) return 'UNKNOWN'
  if (beta > 1.5) return 'HIGH VOLATILITY'
  if (beta > 1.2) return 'MODERATE HIGH'
  if (beta > 0.8) return 'NORMAL'
  if (beta > 0.5) return 'LOW VOLATILITY'
  return 'VERY LOW'
}

// Lifecycle
onMounted((): void => {
  loadDashboard()
  loadMetricsHistory()
  loadAlerts()
  loadVarCvar()
  loadBeta()

  window.addEventListener('resize', (): void => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
})

onUnmounted((): void => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped lang="scss">
.web3-risk-monitor {
  min-height: 100vh;
  padding: 24px;
  background: #030304;

  // Grid pattern background mixin equivalent
  .grid-bg {
    position: relative;
    background-image:
      linear-gradient(rgba(247, 147, 26, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(247, 147, 26, 0.03) 1px, transparent 1px);
    background-size: 20px 20px;
  }

  .page-header {
    margin-bottom: 32px;
    text-align: center;

    .subtitle {
      margin-top: 8px;
      font-size: 14px;
      color: #94A3B8;
      font-family: 'JetBrains Mono', monospace;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
  }

  .metrics-overview {
    margin-bottom: 24px;

    .metric-card {
      position: relative;
      transition: all 0.3s ease;

      &.hover-lift:hover {
        transform: translateY(-4px);
        border-color: rgba(247, 147, 26, 0.5);
        box-shadow: 0 0 30px -10px rgba(247, 147, 26, 0.2);
      }

      .metric-content {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px;

        .metric-icon-wrapper {
          width: 56px;
          height: 56px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 12px;
          background: rgba(247, 147, 26, 0.1);

          .metric-icon {
            font-size: 28px;
            color: #F7931A;
          }

          &.risk-cvar .metric-icon { color: #FFD600; }
          &.risk-beta .metric-icon { color: #3B82F6; }
          &.risk-alert .metric-icon { color: #22C55E; }
        }

        .metric-info {
          flex: 1;

          .metric-label {
            font-size: 12px;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
          }

          .metric-value {
            font-size: 24px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: 4px;

            &.orange-glow { color: #F7931A; }
            &.yellow-glow { color: #FFD600; }
            &.blue-glow { color: #3B82F6; }
            &.green-glow { color: #22C55E; }
          }

          .metric-description {
            font-size: 11px;
            color: #64748B;
          }
        }
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .section-title {
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      font-weight: 600;
      color: #F7931A;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }

    .card-actions {
      display: flex;
      gap: 8px;
    }
  }

  .chart-container {
    padding: 16px;
    border-radius: 8px;
  }

  .alerts-list {
    .alert-item {
      padding: 12px;
      border: 1px solid rgba(30, 41, 59, 0.5);
      border-radius: 8px;
      margin-bottom: 12px;
      transition: all 0.2s ease;

      &.corner-border {
        position: relative;

        &::before,
        &::after {
          content: '';
          position: absolute;
          width: 8px;
          height: 8px;
          border-color: #F7931A;
          border-style: solid;
        }

        &::before {
          top: -1px;
          left: -1px;
          border-width: 2px 0 0 2px;
          border-radius: 4px 0 0 0;
        }

        &::after {
          bottom: -1px;
          right: -1px;
          border-width: 0 2px 2px 0;
          border-radius: 0 0 4px 0;
        }

        &:hover {
          border-color: rgba(247, 147, 26, 0.3);
        }
      }

      &:last-child {
        margin-bottom: 0;
      }

      .alert-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .alert-time {
          font-size: 12px;
          color: #94A3B8;
          font-family: 'JetBrains Mono', monospace;
        }
      }

      .alert-content {
        margin-bottom: 8px;

        .alert-title {
          font-size: 14px;
          font-weight: 500;
          color: #E5E7EB;
          margin: 0 0 4px 0;
        }

        .alert-description {
          font-size: 12px;
          color: #94A3B8;
          margin: 0;
        }
      }

      .alert-actions {
        text-align: right;
      }
    }
  }

  .alerts-loading {
    padding: 20px;
  }

  // Risk level colors
  .risk-critical {
    color: #F7931A;
    font-weight: 600;
  }

  .risk-high {
    color: #FFD600;
    font-weight: 600;
  }

  .risk-medium {
    color: #3B82F6;
  }

  .risk-low {
    color: #22C55E;
  }

  // Beta coefficient colors
  .beta-high {
    color: #F7931A;
    font-weight: 600;
  }

  .beta-low {
    color: #22C55E;
    font-weight: 600;
  }

  .beta-normal {
    color: #94A3B8;
  }

  // Web3 table styling
  .web3-table {
    background: transparent;

    :deep(.el-table__header) {
      th {
        background: rgba(30, 41, 59, 0.5) !important;
        color: #F7931A !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        text-transform: uppercase;
        border-bottom: 1px solid rgba(247, 147, 26, 0.3) !important;
      }
    }

    :deep(.el-table__body) {
      tr {
        background: transparent !important;
        transition: background 0.2s ease;

        &:hover {
          background: rgba(247, 147, 26, 0.05) !important;
        }

        td {
          border-bottom: 1px solid rgba(30, 41, 59, 0.5) !important;
          color: #E5E7EB;
        }
      }
    }
  }

  .web3-select,
  .web3-input-number {
    :deep(.el-input__wrapper) {
      background: rgba(30, 41, 59, 0.5);
      border: 1px solid rgba(30, 41, 59, 0.5);
      box-shadow: none;

      &:hover {
        border-color: rgba(247, 147, 26, 0.3);
      }
    }

    :deep(.el-input__inner) {
      color: #E5E7EB;
      font-family: 'JetBrains Mono', monospace;
    }
  }

  .web3-tag {
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    font-size: 11px;
    border: 1px solid rgba(247, 147, 26, 0.3);
    background: rgba(247, 147, 26, 0.1);
  }
}
</style>
