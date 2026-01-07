<template>
  <div class="monitoring-dashboard">

    <!-- Page Header -->
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-title-section">
          <div class="header-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
              <path d="M3 3v18h18"></path>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
            </svg>
          </div>
          <h1 class="header-title">监控中心</h1>
        </div>
        <div class="header-actions">
          <el-button variant="secondary" @click="refreshAll">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            刷新
          </el-button>
          <el-button :type="isMonitoring ? 'success' : 'info'" @click="toggleMonitoring">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon v-if="!isMonitoring" points="5,3 19,12 5,21 5,3"></polygon>
              <rect v-else x="6" y="4" width="4" height="16"></rect>
              <rect v-else x="14" y="4" width="4" height="16"></rect>
            </svg>
            {{ isMonitoring ? '停止监控' : '开始监控' }}
          </el-button>
        </div>
      </div>
      <p class="header-subtitle">实时监控股票市场动态，设置告警规则，跟踪龙虎榜数据</p>
    </el-card>

    <!-- Summary Stats -->
    <div class="stats-grid">
      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--gold-primary), #E5C158);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M3 3v18h18"></path>
            <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_stocks || 0 }}</div>
          <div class="stat-label">总股票数</div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--rise), #FF8A80);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polyline points="18,15 12,9 6,15"></polyline>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value" style="color: var(--rise);">{{ summary.limit_up_count || 0 }}</div>
          <div class="stat-label">涨停数</div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--fall), #69F0AE);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polyline points="6,9 12,15 18,9"></polyline>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value" style="color: var(--fall);">{{ summary.limit_down_count || 0 }}</div>
          <div class="stat-label">跌停数</div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--warning), #FFD54F);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value" style="color: var(--warning);">{{ summary.unread_alerts || 0 }}</div>
          <div class="stat-label">未读告警</div>
        </div>
      </el-card>
    </div>

    <!-- Real-time Data -->
    <el-card title="实时监控数据" :hoverable="false">
      <template #header-actions>
        <div class="live-indicator">
          <span class="live-dot"></span>
          <span>实时数据</span>
        </div>
      </template>
      <el-table
        :columns="realtimeColumns"
        :data="realtimeData"
        row-key="symbol"
        :loading="loading.realtime"
                :default-sort="{ prop: 'change_percent', order: 'descending' }"
                :default-sort="{ prop: 'change_percent', order: 'descending' }"
        @sort="handleRealtimeSort"
      >
        <template #cell-symbol="{ value }">
          <span class="text-mono">{{ value }}</span>
        </template>

        <template #cell-current_price="{ value }">
          <span class="text-mono">{{ value.toFixed(2) }}</span>
        </template>

        <template #cell-change_percent="{ row, value }">
          <span :class="value >= 0 ? 'data-rise' : 'data-fall'" class="text-mono">
            {{ value >= 0 ? '+' : '' }}{{ value.toFixed(2) }}%
          </span>
        </template>

        <template #cell-change_amount="{ value }">
          <span :class="value >= 0 ? 'data-rise' : 'data-fall'" class="text-mono">
            {{ value >= 0 ? '+' : '' }}{{ value.toFixed(2) }}
          </span>
        </template>

        <template #cell-volume="{ value }">
          <span class="text-mono">{{ formatNumber(value) }}</span>
        </template>

        <template #cell-amount="{ value }">
          <span class="text-mono">¥{{ formatAmount(value) }}</span>
        </template>

        <template #cell-timestamp="{ value }">
          <span class="text-mono">{{ value }}</span>
        </template>

        <template #cell-is_limit_up="{ row }">
          <el-tag
            v-if="row.is_limit_up"
            text="涨停"
            type="danger"
            size="small"
          />
          <el-tag
            v-else-if="row.is_limit_down"
            text="跌停"
            type="info"
            size="small"
          />
          <span v-else class="text-muted">-</span>
        </template>
      </el-table>
    </el-card>

    <!-- Alert Records -->
    <el-card title="告警记录" :hoverable="false">
      <el-table
        :columns="alertColumns"
        :data="alertRecords"
        row-key="id"
        :loading="loading.alerts"
      >
        <template #cell-symbol="{ value }">
          <span class="text-mono">{{ value }}</span>
        </template>

        <template #cell-level="{ value }">
          <el-tag
            :text="getAlertLevelText(value)"
            :type="getAlertLevelVariant(value)"
            size="small"
          />
        </template>

        <template #cell-timestamp="{ value }">
          <span class="text-mono">{{ value }}</span>
        </template>

        <template #cell-is_read="{ value }">
          <el-tag
            :text="value ? '已读' : '未读'"
            :type="value ? 'info' : 'warning'"
            size="small"
          />
        </template>
      </el-table>
    </el-card>

    <!-- Dragon Tiger List -->
    <el-card title="龙虎榜数据" :hoverable="false">
      <el-table
        :columns="dragonTigerColumns"
        :data="dragonTigerData"
        row-key="symbol"
        :loading="loading.dragonTiger"
                :default-sort="{ prop: 'net_amount', order: 'descending' }"
                :default-sort="{ prop: 'net_amount', order: 'descending' }"
        @sort="handleDragonTigerSort"
      >
        <template #cell-symbol="{ value }">
          <span class="text-mono">{{ value }}</span>
        </template>

        <template #cell-net_amount="{ value }">
          <span :class="value >= 0 ? 'data-rise' : 'data-fall'" class="text-mono">
            {{ value >= 0 ? '+' : '' }}¥{{ formatAmount(value) }}
          </span>
        </template>

        <template #cell-buy_amount="{ value }">
          <span class="text-mono">¥{{ formatAmount(value) }}</span>
        </template>

        <template #cell-sell_amount="{ value }">
          <span class="text-mono">¥{{ formatAmount(value) }}</span>
        </template>

        <template #cell-trade_date="{ value }">
          <span class="text-mono">{{ value }}</span>
        </template>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElCard } from 'element-plus'
import { ElTable, ElTableColumn } from 'element-plus'

interface Summary {
  total_stocks: number
  limit_up_count: number
  limit_down_count: number
  unread_alerts: number
}

interface RealtimeStock {
  symbol: string
  stock_name: string
  current_price: number
  change_percent: number
  change_amount: number
  volume: number
  amount: number
  timestamp: string
  is_limit_up: boolean
  is_limit_down: boolean
}

interface AlertRecord {
  id: string
  symbol: string
  stock_name: string
  alert_type: string
  level: 'info' | 'warning' | 'error' | 'critical'
  message: string
  timestamp: string
  is_read: boolean
}

interface DragonTigerRecord {
  symbol: string
  stock_name: string
  net_amount: number
  buy_amount: number
  sell_amount: number
  reason: string
  trade_date: string
}

interface Column {
  key: string
  label: string
  sortable?: boolean
}

const summary = ref<Summary>({
  total_stocks: 5216,
  limit_up_count: 45,
  limit_down_count: 12,
  unread_alerts: 8
})

const realtimeData = ref<RealtimeStock[]>([
  { symbol: '600519.SH', stock_name: '贵州茅台', current_price: 1678.50, change_percent: 1.23, change_amount: 20.35, volume: 2350000, amount: 3950000000, timestamp: '2024-01-15 14:30:25', is_limit_up: false, is_limit_down: false },
  { symbol: '000858.SZ', stock_name: '五粮液', current_price: 156.78, change_percent: -0.56, change_amount: -0.89, volume: 8450000, amount: 1320000000, timestamp: '2024-01-15 14:30:22', is_limit_up: false, is_limit_down: false },
  { symbol: '600036.SH', stock_name: '招商银行', current_price: 32.45, change_percent: 2.15, change_amount: 0.68, volume: 15600000, amount: 506000000, timestamp: '2024-01-15 14:30:18', is_limit_up: false, is_limit_down: false },
  { symbol: '300750.SZ', stock_name: '宁德时代', current_price: 198.50, change_percent: 3.45, change_amount: 6.62, volume: 28900000, amount: 5730000000, timestamp: '2024-01-15 14:30:15', is_limit_up: true, is_limit_down: false },
  { symbol: '000001.SZ', stock_name: '平安银行', current_price: 12.89, change_percent: -1.23, change_amount: -0.16, volume: 22300000, amount: 287000000, timestamp: '2024-01-15 14:30:10', is_limit_up: false, is_limit_down: false }
])

const alertRecords = ref<AlertRecord[]>([
  { id: '1', symbol: '600519.SH', stock_name: '贵州茅台', alert_type: '价格预警', level: 'info', message: '股价突破1700元关口', timestamp: '2024-01-15 14:25:00', is_read: false },
  { id: '2', symbol: '300750.SZ', stock_name: '宁德时代', alert_type: '涨停预警', level: 'warning', message: '距涨停仅差2%', timestamp: '2024-01-15 14:20:00', is_read: false },
  { id: '3', symbol: '000858.SZ', stock_name: '五粮液', alert_type: '量能预警', level: 'info', message: '成交量放大50%', timestamp: '2024-01-15 14:15:00', is_read: true },
  { id: '4', symbol: '600036.SH', stock_name: '招商银行', alert_type: '资金预警', level: 'error', message: '主力资金净流出超1亿', timestamp: '2024-01-15 14:10:00', is_read: false }
])

const dragonTigerData = ref<DragonTigerRecord[]>([
  { symbol: '600519.SH', stock_name: '贵州茅台', net_amount: 256000000, buy_amount: 389000000, sell_amount: 133000000, reason: '连续三日涨幅累计20%', trade_date: '2024-01-15' },
  { symbol: '300750.SZ', stock_name: '宁德时代', net_amount: 189000000, buy_amount: 312000000, sell_amount: 123000000, reason: '日内涨停收盘', trade_date: '2024-01-15' },
  { symbol: '000858.SZ', stock_name: '五粮液', net_amount: -45000000, buy_amount: 89000000, sell_amount: 134000000, reason: '资金净流出', trade_date: '2024-01-15' },
  { symbol: '600036.SH', stock_name: '招商银行', net_amount: 78000000, buy_amount: 156000000, sell_amount: 78000000, reason: '大单净买入', trade_date: '2024-01-15' }
])

const loading = ref({
  summary: false,
  realtime: false,
  alerts: false,
  dragonTiger: false
})

const isMonitoring = ref(false)

const realtimeColumns: Column[] = [
  { key: 'symbol', label: '代码', sortable: true },
  { key: 'stock_name', label: '名称', sortable: true },
  { key: 'current_price', label: '现价', sortable: true },
  { key: 'change_percent', label: '涨跌幅(%)', sortable: true },
  { key: 'change_amount', label: '涨跌额', sortable: true },
  { key: 'volume', label: '成交量', sortable: true },
  { key: 'amount', label: '成交额', sortable: true },
  { key: 'timestamp', label: '时间', sortable: true },
  { key: 'is_limit_up', label: '涨停' }
]

const alertColumns: Column[] = [
  { key: 'symbol', label: '代码' },
  { key: 'stock_name', label: '名称' },
  { key: 'alert_type', label: '告警类型' },
  { key: 'level', label: '级别' },
  { key: 'message', label: '消息' },
  { key: 'timestamp', label: '时间' },
  { key: 'is_read', label: '状态' }
]

const dragonTigerColumns: Column[] = [
  { key: 'symbol', label: '代码', sortable: true },
  { key: 'stock_name', label: '名称', sortable: true },
  { key: 'net_amount', label: '净买入额', sortable: true },
  { key: 'buy_amount', label: '买入额', sortable: true },
  { key: 'sell_amount', label: '卖出额', sortable: true },
  { key: 'reason', label: '上榜理由' },
  { key: 'trade_date', label: '日期', sortable: true }
]

function formatNumber(num: number): string {
  if (num >= 100000000) {
    return (num / 100000000).toFixed(2) + '亿'
  } else if (num >= 10000) {
    return (num / 10000).toFixed(2) + '万'
  }
  return num.toLocaleString()
}

function formatAmount(amount: number): string {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2)
}

function getAlertLevelText(level: string): string {
  switch (level) {
    case 'info': return '提示'
    case 'warning': return '警告'
    case 'error': return '错误'
    case 'critical': return '严重'
    default: return level
  }
}

function getAlertLevelVariant(level: string): 'warning' | 'danger' | 'info' | 'success' {
  switch (level) {
    case 'info': return 'info'
    case 'warning': return 'warning'
    case 'error': return 'danger'
    case 'critical': return 'danger'
    default: return 'info'
  }
}

function handleRealtimeSort(key: string, order: 'asc' | 'desc') {
  console.log('Sort realtime:', key, order)
}

function handleDragonTigerSort(key: string, order: 'asc' | 'desc') {
  console.log('Sort dragon tiger:', key, order)
}

function refreshAll() {
  console.log('Refreshing all data...')
}

function toggleMonitoring() {
  isMonitoring.value = !isMonitoring.value
  console.log('Monitoring:', isMonitoring.value ? 'started' : 'stopped')
}

onMounted(() => {
  console.log('Monitoring dashboard mounted')
})
</script>

<style scoped lang="scss">

  display: flex;
  flex-direction: column;
  gap: var(--space-section);
  padding: var(--space-xl);
  background: var(--bg-primary);
  min-height: 100vh;
}

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.03;
  background-image:
    repeating-linear-gradient(45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px);
}

  position: relative;
  z-index: 1;
}

.header-card {
  padding: var(--space-xl);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.header-title-section {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.header-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
}

.header-title {
  font-family: var(--font-display);
  font-size: 1.75rem;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--tracking-display);
  margin: 0;
  font-weight: 600;
}

.header-subtitle {
  font-family: var(--font-body);
  font-size: 0.875rem;
  color: var(--silver-muted);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-md);
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--fall);
  text-transform: uppercase;
  letter-spacing: var(--tracking-tight);
}

.live-dot {
  width: 8px;
  height: 8px;
  background: var(--fall);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-lg) !important;
}

  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-none);
}

  flex: 1;
}

  font-family: var(--font-mono);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--gold-primary);
  line-height: 1;
  margin-bottom: var(--space-xs);
}

  font-family: var(--font-body);
  font-size: 0.75rem;
  color: var(--silver-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-tight);
}

.text-mono {
  font-family: var(--font-mono);
}

.text-muted {
  color: var(--silver-muted);
}

.data-rise {
  color: var(--rise);
}

.data-fall {
  color: var(--fall);
}

/* Responsive */
@media (max-width: 1440px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1080px) {
    gap: var(--space-2xl);
    padding: var(--space-lg);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }
}
</style>
