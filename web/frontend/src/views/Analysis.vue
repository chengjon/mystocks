<template>
    <PageHeader
      title="数据分析"
      subtitle="DATA ANALYSIS CENTER"
    />

    <div class="card config-card">
      <div class="card-header">
        <div class="header-title">
          <div class="title-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M3 3v18h18"></path>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
            </svg>
          </div>
          <span class="title-text">分析配置</span>
          <span class="title-sub">ANALYSIS CONFIGURATION</span>
        </div>
        <button class="button button-primary" @click="runAnalysis" :class="{ loading: loading }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          开始分析
        </button>
      </div>
      <div class="card-body">
        <div class="analysis-form">
          <div class="form-row">
            <label class="form-label">股票代码</label>
            <input type="text" v-model="form.symbol" placeholder="如: 600519" class="input" />
          </div>

          <div class="form-row">
            <label class="form-label">分析类型</label>
            <select v-model="form.analysisType" class="select">
              <option value="indicators">技术指标分析</option>
              <option value="trend">趋势分析</option>
              <option value="momentum">动量分析</option>
              <option value="volatility">波动率分析</option>
              <option value="volume">成交量分析</option>
              <option value="signals">信号综合</option>
            </select>
          </div>

          <div class="form-row">
            <label class="form-label">时间周期</label>
            <select v-model="form.period" class="select">
              <option value="daily">日线</option>
              <option value="weekly">周线</option>
              <option value="monthly">月线</option>
            </select>
          </div>

          <div class="form-row">
            <label class="form-label">数据范围</label>
            <div class="number-input">
              <input type="number" v-model="form.days" :min="30" :max="365" :step="30" class="input" />
              <span>天</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="analysisResult" class="analysis-results">
      <div class="card result-card">
        <div class="card-header">
          <div class="header-title">
            <div class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
            </div>
            <span class="title-text">{{ getAnalysisTitle() }} - {{ form.symbol }}</span>
          </div>
          <el-tag :type="getSignalTagType(analysisResult.overall_signal)">
            {{ analysisResult.overall_signal || '中性' }}
          </el-tag>
        </div>
        <div class="card-body">
          <div class="metrics-grid">
            <div v-for="metric in keyMetrics" :key="metric.key" :class="['metric-card', metric.class]">
              <div class="metric-value">{{ metric.value }}</div>
              <div class="metric-label">{{ metric.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card detail-card">
        <div class="card-header">
          <div class="header-title">
            <span class="title-text">指标详情</span>
            <span class="title-sub">INDICATOR DETAILS</span>
          </div>
        </div>
        <div class="card-body">
          <StockListTable
            :columns="tableColumns"
            :data="indicatorDetails"
            :loading="false"
            :row-clickable="false"
          >
            <template #cell-signal="{ row }">
              <el-tag :type="getSignalTagType(row.signal)">
                {{ row.signal }}
              </el-tag>
            </template>
          </StockListTable>
        </div>
      </div>

      <div class="card chart-card">
        <div class="card-header">
          <div class="header-title">
            <span class="title-text">趋势图表</span>
            <span class="title-sub">TREND CHART</span>
          </div>
        </div>
        <div class="card-body">
          <ChartContainer
            chart-type="line"
            :data="chartData"
            :options="chartOptions"
            height="400px"
            :loading="loading"
          />
        </div>
      </div>

      <div class="card advice-card">
        <div class="card-header">
          <div class="header-title">
            <div class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 11l3 3L22 4"></path>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
            </div>
            <span class="title-text">分析建议</span>
            <span class="title-sub">ANALYSIS ADVICE</span>
          </div>
        </div>
        <div class="card-body">
          <div v-if="analysisResult.advices && analysisResult.advices.length" class="advice-list">
            <div v-for="(advice, index) in analysisResult.advices" :key="index" :class="['advice-item', advice.type || 'info']">
              <div class="advice-icon">
                <svg v-if="advice.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <svg v-else-if="advice.type === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
              </div>
              <div class="advice-content">
                <div class="advice-title">{{ advice.title }}</div>
                <div class="advice-desc">{{ advice.description }}</div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p>暂无分析建议</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="card empty-card">
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 3v18h18"></path>
          <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
        </svg>
        <p>请选择股票并开始分析</p>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { technicalApi } from '@/api'
import { PageHeader, StockListTable, ChartContainer } from '@/components/shared'
import type { TableColumn } from '@/components/shared'

interface AnalysisForm {
  symbol: string
  analysisType: string
  period: string
  days: number
}

interface AnalysisResult {
  price?: number
  change_percent?: number
  ma5?: number
  ma20?: number
  rsi?: number
  volatility?: number
  overall_signal?: string
  indicators?: IndicatorDetail[]
  chart_data?: ChartData
  advices?: Advice[]
}

interface IndicatorDetail {
  name: string
  value: string | number
  signal: string
  description: string
}

interface ChartData {
  legend?: string[]
  dates?: string[]
  prices?: number[]
  ma5?: number[]
  ma20?: number[]
  series?: any[]
}

interface Advice {
  type?: string
  title: string
  description: string
}

interface Metric {
  key: string
  label: string
  value: string
  class: string
}

const loading = ref(false)
const analysisResult = ref<AnalysisResult | null>(null)

const form = ref<AnalysisForm>({
  symbol: '',
  analysisType: 'indicators',
  period: 'daily',
  days: 60
})

const tableColumns = computed((): TableColumn[] => [
  {
    prop: 'name',
    label: '指标',
    width: 150
  },
  {
    prop: 'value',
    label: '数值',
    width: 120,
    className: 'mono'
  },
  {
    prop: 'signal',
    label: '信号',
    width: 120
  },
  {
    prop: 'description',
    label: '说明',
    minWidth: 200
  }
])

const keyMetrics = computed((): Metric[] => {
  if (!analysisResult.value) return []
  const result = analysisResult.value
  const metrics: Metric[] = []

  if (result.price !== undefined) {
    metrics.push({
      key: 'price',
      label: '当前价格',
      value: `¥${result.price.toFixed(2)}`,
      class: ''
    })
  }

  if (result.change_percent !== undefined) {
    const change = result.change_percent
    metrics.push({
      key: 'change',
      label: '涨跌幅',
      value: `${change > 0 ? '+' : ''}${change.toFixed(2)}%`,
      class: change > 0 ? 'positive' : change < 0 ? 'negative' : ''
    })
  }

  if (result.ma5 !== undefined) {
    metrics.push({
      key: 'ma5',
      label: 'MA5',
      value: result.ma5.toFixed(2),
      class: result.price !== undefined && result.price > result.ma5 ? 'positive' : 'negative'
    })
  }

  if (result.ma20 !== undefined) {
    metrics.push({
      key: 'ma20',
      label: 'MA20',
      value: result.ma20.toFixed(2),
      class: result.price !== undefined && result.price > result.ma20 ? 'positive' : 'negative'
    })
  }

  if (result.rsi !== undefined) {
    metrics.push({
      key: 'rsi',
      label: 'RSI',
      value: result.rsi.toFixed(2),
      class: result.rsi > 70 ? 'negative' : result.rsi < 30 ? 'positive' : ''
    })
  }

  if (result.volatility !== undefined) {
    metrics.push({
      key: 'volatility',
      label: '波动率',
      value: `${(result.volatility * 100).toFixed(2)}%`,
      class: ''
    })
  }

  return metrics.slice(0, 4)
})

const indicatorDetails = computed((): IndicatorDetail[] => {
  if (!analysisResult.value?.indicators) return []
  return analysisResult.value.indicators
})

const chartData = computed((): any[] => {
  if (!analysisResult.value?.chart_data) return []

  const chartInfo = analysisResult.value.chart_data
  return [
    {
      name: '价格',
      data: (chartInfo.dates || []).map((date: string, index: number) => ({
        name: date,
        value: chartInfo.prices?.[index] || 0
      }))
    },
    {
      name: 'MA5',
      data: (chartInfo.dates || []).map((date: string, index: number) => ({
        name: date,
        value: chartInfo.ma5?.[index] || 0
      }))
    },
    {
      name: 'MA20',
      data: (chartInfo.dates || []).map((date: string, index: number) => ({
        name: date,
        value: chartInfo.ma20?.[index] || 0
      }))
    }
  ]
})

const chartOptions = computed((): Record<string, any> => {
  return {
    tooltip: {
      trigger: 'axis' as const,
      axisPointer: { type: 'cross' as const },
      backgroundColor: 'rgba(10, 10, 10, 0.95)',
      borderColor: '#D4AF37',
      textStyle: { color: '#E5E7EB' }
    },
    legend: {
      data: ['价格', 'MA5', 'MA20'],
      textStyle: { color: '#D4AF37' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category' as const,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#9CA3AF' }
    },
    yAxis: {
      type: 'value' as const,
      scale: true,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#9CA3AF' }
    },
    color: ['#FF5252', '#D4AF37', '#67C23A']
  }
})

const getAnalysisTitle = (): string => {
  const titles: Record<string, string> = {
    indicators: '技术指标分析',
    trend: '趋势分析',
    momentum: '动量分析',
    volatility: '波动率分析',
    volume: '成交量分析',
    signals: '信号综合分析'
  }
  return titles[form.value.analysisType] || '数据分析'
}

const getSignalBadgeClass = (signal?: string): string => {
  if (!signal) return 'neutral'
  const signalLower = signal.toLowerCase()
  if (signalLower.includes('买') || signalLower.includes('buy') || signalLower.includes('强')) {
    return 'success'
  }
  if (signalLower.includes('卖') || signalLower.includes('sell') || signalLower.includes('弱')) {
    return 'danger'
  }
  return 'warning'
}

const getSignalTagType = (signal?: string): 'success' | 'danger' | 'warning' | 'info' => {
  if (!signal) return 'info'
  const signalLower = signal.toLowerCase()
  if (signalLower.includes('买') || signalLower.includes('buy') || signalLower.includes('强')) {
    return 'success'
  }
  if (signalLower.includes('卖') || signalLower.includes('sell') || signalLower.includes('弱')) {
    return 'danger'
  }
  return 'warning'
}

const getSignalTagClass = (signal: string): string => {
  if (!signal) return 'neutral'
  const signalLower = signal.toLowerCase()
  if (signalLower.includes('买') || signalLower.includes('buy') || signalLower.includes('强')) {
    return 'success'
  }
  if (signalLower.includes('卖') || signalLower.includes('sell') || signalLower.includes('弱')) {
    return 'danger'
  }
  return 'warning'
}

const runAnalysis = async (): Promise<void> => {
  if (!form.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  loading.value = true
  try {
    let response
    const params = {
      period: form.value.period,
      days: form.value.days
    }

    switch (form.value.analysisType) {
      case 'indicators':
        response = await technicalApi.getIndicators(form.value.symbol, params)
        break
      case 'trend':
        response = await technicalApi.getTrend(form.value.symbol, params)
        break
      case 'momentum':
        response = await technicalApi.getMomentum(form.value.symbol, params)
        break
      case 'volatility':
        response = await technicalApi.getVolatility(form.value.symbol, params)
        break
      case 'volume':
        response = await technicalApi.getVolume(form.value.symbol, params)
        break
      case 'signals':
        response = await technicalApi.getSignals(form.value.symbol, params)
        break
      default:
        response = await technicalApi.getIndicators(form.value.symbol, params)
    }

    if (response.data?.success) {
      analysisResult.value = response.data.data
      ElMessage.success('分析完成')
    } else {
      ElMessage.error(response.data?.message || '分析失败')
    }
  } catch (error: any) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">

  padding: 24px;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
  min-height: 100vh;

  .config-card {
    margin-bottom: 24px;

    .analysis-form {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;

      .form-row {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .form-label {
          font-family: var(--font-body);
          font-size: 12px;
          color: var(--gold-muted);
          text-transform: uppercase;
          letter-spacing: 2px;
        }

        .input {
          background: transparent;
          border: none;
          border-bottom: 2px solid var(--gold-dim);
          padding: 8px 0;
          font-family: var(--font-body);
          font-size: 14px;
          color: var(--text-primary);
          transition: all 0.3s ease;

          &:focus {
            outline: none;
            border-bottom-color: var(--gold-primary);
            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
          }

          &::placeholder {
            color: var(--text-muted);
          }
        }

        .select {
          background: transparent;
          border: none;
          border-bottom: 2px solid var(--gold-dim);
          padding: 8px 0;
          font-family: var(--font-body);
          font-size: 14px;
          color: var(--text-primary);
          cursor: pointer;
          transition: all 0.3s ease;

          &:focus {
            outline: none;
            border-bottom-color: var(--gold-primary);
            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
          }

          option {
            background: var(--bg-card);
            color: var(--text-primary);
          }
        }

        .number-input {
          display: flex;
          align-items: center;
          gap: 8px;

          .input {
            width: 100px;
          }

          span {
            font-family: var(--font-body);
            font-size: 14px;
            color: var(--text-muted);
          }
        }
      }
    }
  }

  .analysis-results {
    .result-card {
      margin-bottom: 24px;

      .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;

        .metric-card {
          background: rgba(212, 175, 55, 0.05);
          border: 1px solid var(--gold-dim);
          padding: 20px;
          text-align: center;
          position: relative;

          &::before {
            content: '';
            position: absolute;
            top: 8px;
            left: 8px;
            width: 6px;
            height: 6px;
            background: var(--gold-primary);
          }

          .metric-value {
            font-family: var(--font-mono);
            font-size: 24px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 8px;

            &.positive {
              color: var(--rise);
            }

            &.negative {
              color: var(--fall);
            }
          }

          .metric-label {
            font-family: var(--font-body);
            font-size: 12px;
            color: var(--gold-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
          }
        }
      }
    }

    .detail-card {
      margin-bottom: 24px;
    }

    .chart-card {
      margin-bottom: 24px;
    }

    .advice-card {
      margin-bottom: 24px;

      .advice-list {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .advice-item {
          background: rgba(212, 175, 55, 0.05);
          border-left: 4px solid var(--gold-primary);
          padding: 16px;
          display: flex;
          gap: 16px;
          align-items: flex-start;

          &.success {
            border-left-color: var(--fall);
            background: rgba(0, 230, 118, 0.05);
          }

          &.warning {
            border-left-color: #e6a23c;
            background: rgba(230, 162, 60, 0.05);
          }

          &.info {
            border-left-color: var(--gold-primary);
          }

          .advice-icon {
            flex-shrink: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--gold-primary);
          }

          .advice-content {
            flex: 1;

            .advice-title {
              font-family: var(--font-body);
              font-size: 14px;
              font-weight: 600;
              color: var(--gold-primary);
              margin-bottom: 4px;
            }

            .advice-desc {
              font-family: var(--font-body);
              font-size: 13px;
              color: var(--text-secondary);
              line-height: 1.6;
            }
          }
        }
      }

      .empty-state {
        text-align: center;
        padding: 40px 20px;

        svg {
          width: 60px;
          height: 60px;
          margin: 0 auto 16px;
          color: var(--gold-primary);
        }

        p {
          font-family: var(--font-body);
          font-size: 14px;
          color: var(--text-muted);
          margin: 0;
        }
      }
    }
  }

  .empty-card {
    .empty-state {
      text-align: center;
      padding: 80px 20px;

      svg {
        width: 80px;
        height: 80px;
        margin: 0 auto 24px;
        color: var(--gold-muted);
      }

      p {
        font-family: var(--font-body);
        font-size: 16px;
        color: var(--text-secondary);
        margin: 0;
      }
    }
  }
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
  position: relative;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
    z-index: 1;
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }

  .card-header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--gold-dim);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;

    .header-title {
      display: flex;
      align-items: center;
      gap: 12px;

      .title-icon {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--gold-primary);
        flex-shrink: 0;
      }

      .title-text {
        font-family: var(--font-body);
        font-size: 16px;
        font-weight: 600;
        color: var(--gold-primary);
        text-transform: uppercase;
        letter-spacing: 2px;
      }

      .title-sub {
        font-family: var(--font-body);
        font-size: 10px;
        color: var(--gold-muted);
        text-transform: uppercase;
        letter-spacing: 3px;
        display: block;
        margin-top: 2px;
      }
    }

    .badge {
      font-family: var(--font-body);
      font-size: 11px;
      padding: 6px 16px;
      border: 1px solid var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;

      &.success {
        background: var(--fall);
        color: var(--bg-primary);
        border-color: var(--fall);
      }

      &.danger {
        background: var(--rise);
        color: var(--bg-primary);
        border-color: var(--rise);
      }

      &.warning {
        background: #e6a23c;
        color: var(--bg-primary);
        border-color: #e6a23c;
      }

      &.neutral {
        background: rgba(212, 175, 55, 0.1);
        color: var(--gold-primary);
      }
    }
  }

  .card-body {
    padding: 24px;
  }
}

.button {
  padding: 12px 24px;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 2px;
  border: 2px solid var(--gold-primary);
  background: transparent;
  color: var(--gold-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  position: relative;

  svg {
    width: 18px;
    height: 18px;
  }

  &:hover:not(.loading) {
    background: var(--gold-primary);
    color: var(--bg-primary);
  }

  &.loading {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &::before {
    content: '';
    position: absolute;
    top: 4px;
    left: 4px;
    width: 8px;
    height: 8px;
    border-left: 1px solid var(--gold-primary);
    border-top: 1px solid var(--gold-primary);
  }

  &.button-primary {
    border-color: var(--rise);
    color: var(--rise);

    &::before {
      border-color: var(--rise);
    }

    &:hover:not(.loading) {
      background: var(--rise);
      color: var(--bg-primary);
    }
  }
}

.tag {
  font-family: var(--font-body);
  font-size: 11px;
  padding: 4px 12px;
  text-transform: uppercase;
  letter-spacing: 1px;

  &.success {
    background: rgba(0, 230, 118, 0.1);
    color: var(--fall);
    border: 1px solid var(--fall);
  }

  &.danger {
    background: rgba(255, 82, 82, 0.1);
    color: var(--rise);
    border: 1px solid var(--rise);
  }

  &.warning {
    background: rgba(230, 162, 60, 0.1);
    color: #e6a23c;
    border: 1px solid #e6a23c;
  }

  &.neutral {
    background: rgba(212, 175, 55, 0.1);
    color: var(--gold-primary);
    border: 1px solid var(--gold-primary);
  }
}

@media (max-width: 768px) {
    padding: 16px;

    .config-card {
      .analysis-form {
        grid-template-columns: 1fr;
      }
    }

    .analysis-results {
      .result-card {
        .metrics-grid {
          grid-template-columns: repeat(2, 1fr);
        }
      }
    }
  }
}
</style>
