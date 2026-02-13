<template>
  <div class="risk-monitor">
    <div class="page-header">
      <h1 class="page-title">RISK MONITOR</h1>
      <p class="page-subtitle">PORTFOLIO RISK ANALYSIS | POSITION MONITORING | STRESS TESTING</p>
    </div>

    <!-- Risk Summary Cards -->
    <div class="risk-summary">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="risk-card">
            <div class="risk-metric">
              <div class="metric-icon">📊</div>
              <div class="metric-content">
                <div class="metric-label">Portfolio Value</div>
                <div class="metric-value">{{ formatCurrency(portfolioValue) }}</div>
                <div class="metric-change" :class="portfolioChange >= 0 ? 'positive' : 'negative'">
                  {{ formatPercent(portfolioChange) }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="risk-card">
            <div class="risk-metric">
              <div class="metric-icon">⚠️</div>
              <div class="metric-content">
                <div class="metric-label">VaR (95%)</div>
                <div class="metric-value negative">{{ formatCurrency(var95) }}</div>
                <div class="metric-subtitle">1-day loss potential</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="risk-card">
            <div class="risk-metric">
              <div class="metric-icon">📉</div>
              <div class="metric-content">
                <div class="metric-label">Max Drawdown</div>
                <div class="metric-value negative">{{ formatPercent(maxDrawdown) }}</div>
                <div class="metric-subtitle">Peak to trough</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="risk-card">
            <div class="risk-metric">
              <div class="metric-icon">🔴</div>
              <div class="metric-content">
                <div class="metric-label">Risk Level</div>
                <div class="metric-value" :class="getRiskLevelClass(riskLevel)">
                  {{ riskLevel }}
                </div>
                <div class="metric-subtitle">Current assessment</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Risk Charts and Analysis -->
    <el-row :gutter="20" style="margin-top: 30px;">
      <!-- Portfolio Risk Distribution -->
      <el-col :span="12">
        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <el-icon class="card-icon"><PieChart /></el-icon>
              <span>Risk Distribution</span>
            </div>
          </template>
          <div class="chart-container">
            <div id="risk-distribution-chart" class="chart">
              <div style="text-align: center; padding: 40px; color: #666;">
                Risk Distribution Chart<br/>
                <small>Market Risk: 45% | Credit Risk: 25% | Liquidity Risk: 20% | Operational Risk: 10%</small>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- VaR Over Time -->
      <el-col :span="12">
        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <el-icon class="card-icon"><TrendCharts /></el-icon>
              <span>VaR Trend (30 Days)</span>
            </div>
          </template>
          <div class="chart-container">
            <div id="var-trend-chart" class="chart">
              <div style="text-align: center; padding: 40px; color: #666;">
                VaR Trend Chart (30 Days)<br/>
                <small>Historical VaR values over the past month</small>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Position Risk Table -->
    <el-card class="positions-card" style="margin-top: 30px;">
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><List /></el-icon>
          <span>Position Risk Details</span>
        </div>
      </template>

      <el-table :data="positionRisks" style="width: 100%">
        <el-table-column prop="symbol" label="Symbol" width="100" />
        <el-table-column prop="position" label="Position" width="120">
          <template #default="scope">
            {{ scope.row.position.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="currentPrice" label="Current Price" width="120">
          <template #default="scope">
            {{ scope.row.currentPrice.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="unrealizedPnL" label="Unrealized P&L" width="140">
          <template #default="scope">
            <span :class="scope.row.unrealizedPnL >= 0 ? 'positive' : 'negative'">
              {{ formatCurrency(scope.row.unrealizedPnL) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="varContribution" label="VaR Contribution" width="140">
          <template #default="scope">
            <span class="negative">
              {{ formatCurrency(scope.row.varContribution) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="beta" label="Beta" width="100">
          <template #default="scope">
            {{ scope.row.beta.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="stressTest" label="Stress Test" width="120">
          <template #default="scope">
            <el-tag :type="getStressTestType(scope.row.stressTest)">
              {{ formatPercent(scope.row.stressTest) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Risk Alerts -->
    <el-card class="alerts-card" style="margin-top: 30px;">
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Warning /></el-icon>
          <span>Risk Alerts</span>
        </div>
      </template>

      <el-alert
        v-for="alert in riskAlerts"
        :key="alert.id"
        :title="alert.title"
        :description="alert.description"
        :type="alert.type"
        show-icon
        style="margin-bottom: 10px;"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  PieChart,
  TrendCharts,
  List,
  Warning
} from '@element-plus/icons-vue'

// Alert type interface (using string as type for simplicity)
interface RiskAlert {
  id: number
  title: string
  description: string
  type: 'error' | 'success' | 'info' | 'warning' | 'primary'
}

const riskAlerts = ref<RiskAlert[]>([
  {
    id: 1,
    title: 'High Concentration Risk',
    description: 'Portfolio exposure to banking sector exceeds 40%',
    type: 'warning'
  },
  {
    id: 2,
    title: 'VaR Threshold Exceeded',
    description: 'Daily VaR has exceeded the 5% threshold for 3 consecutive days',
    type: 'error'
  },
  {
    id: 3,
    title: 'Market Volatility Alert',
    description: 'Market volatility has increased 25% in the last week',
    type: 'info'
  }
])

// Reactive data
const portfolioValue = ref(1250000)
const portfolioChange = ref(0.023) // 2.3%
const var95 = ref(-45000) // -$45,000
const maxDrawdown = ref(-0.156) // -15.6%
const riskLevel = ref('Moderate')

const positionRisks = ref([
  {
    symbol: '600000',
    position: 50000,
    currentPrice: 10.50,
    unrealizedPnL: 12500,
    varContribution: -8500,
    beta: 0.95,
    stressTest: -0.12
  },
  {
    symbol: '000001',
    position: 30000,
    currentPrice: 15.75,
    unrealizedPnL: -2250,
    varContribution: -6200,
    beta: 1.12,
    stressTest: -0.08
  },
  {
    symbol: '000002',
    position: 25000,
    currentPrice: 8.90,
    unrealizedPnL: 8900,
    varContribution: -4100,
    beta: 0.87,
    stressTest: -0.15
  }
])

// Methods
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const formatPercent = (value: number) => {
  return (value * 100).toFixed(1) + '%'
}

const getRiskLevelClass = (level: string) => {
  switch (level.toLowerCase()) {
    case 'low': return 'positive'
    case 'moderate': return 'neutral'
    case 'high': return 'negative'
    default: return 'neutral'
  }
}

const getStressTestType = (value: number) => {
  if (value < -0.15) return 'danger'
  if (value < -0.10) return 'warning'
  return 'info'
}

const initializeCharts = () => {
  // Risk Distribution Chart
  const riskDistContainer = document.getElementById('risk-distribution-chart')
  if (riskDistContainer) {
    // Content handled in template
  }

  // VaR Trend Chart
  const varTrendContainer = document.getElementById('var-trend-chart')
  if (varTrendContainer) {
    // Content handled in template
  }
}

onMounted(() => {
  // Initialize charts after component mounts
  setTimeout(() => {
    initializeCharts()
  }, 100)

  // Simulate real-time updates
  setInterval(() => {
    // Update portfolio value slightly
    const change = (Math.random() - 0.5) * 0.001
    portfolioValue.value *= (1 + change)
    portfolioChange.value = (portfolioValue.value - 1250000) / 1250000
  }, 5000)
})
</script>

<style scoped>
.risk-monitor {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1a1a1a;
  margin: 0;
  letter-spacing: 2px;
}

.page-subtitle {
  font-size: 1rem;
  color: #666;
  margin: 10px 0 0 0;
  letter-spacing: 1px;
}

.risk-summary {
  margin-bottom: 20px;
}

.risk-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.risk-card:hover {
  transform: translateY(-2px);
}

.risk-metric {
  display: flex;
  align-items: center;
  gap: 15px;
}

.metric-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.metric-content {
  flex: 1;
}

.metric-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #303133;
}

.metric-value.positive {
  color: #67c23a;
}

.metric-value.negative {
  color: #f56c6c;
}

.metric-value.neutral {
  color: #e6a23c;
}

.metric-change {
  font-size: 0.8rem;
  margin-top: 2px;
}

.metric-subtitle {
  font-size: 0.75rem;
  color: #909399;
  margin-top: 2px;
}

.analysis-card, .positions-card, .alerts-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-icon {
  font-size: 18px;
  color: #409eff;
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart {
  width: 100%;
  height: 100%;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}
</style>