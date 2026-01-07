<template>
  <div class="results-query">
    <div class="card">
      <PageHeader
        title="策略结果查询"
        subtitle="Strategy Results Query"
      />

      <div class="query-header">
        <FilterBar
          :filters="filterConfig"
          v-model="queryForm"
          @search="handleQuery"
          @reset="handleReset"
        >
          <template #actions>
            <button
              class="button"
              :disabled="results.length === 0"
              @click="handleExport"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7,10 12,15 17,10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              导出CSV
            </button>
          </template>
        </FilterBar>
      </div>

      <div class="table-container">
        <StockListTable
          v-if="results.length > 0"
          :columns="tableColumns"
          :data="results"
          :loading="loading"
          :row-clickable="false"
        >
          <template #cell-strategy_code="{ row }">
            <span class="tag">{{ getStrategyName(row.strategy_code) }}</span>
          </template>
          <template #cell-match_result="{ row }">
            <span class="status-badge" :class="row.match_result ? 'success' : 'info'">
              {{ row.match_result ? '✓ 匹配' : '✗ 不匹配' }}
            </span>
          </template>
          <template #cell-change_percent="{ row }">
            <span :class="getPriceClass(row.change_percent)">
              {{ row.change_percent ? row.change_percent + '%' : '-' }}
            </span>
          </template>
          <template #cell-actions="{ row }">
            <button class="table-action" @click="viewDetails(row)">详情</button>
            <button class="table-action primary" @click="rerun(row)">重新运行</button>
          </template>
        </StockListTable>

        <div v-else-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-dim)'" stroke-width="1">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
          </svg>
          <p>暂无数据</p>
        </div>
      </div>

      <PaginationBar
        v-if="results.length > 0"
        v-model:page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100, 200]"
        @page-change="handlePageChange"
        @size-change="handleQuery"
      />
    </div>

    <DetailDialog
      v-model:visible="detailsVisible"
      title="结果详情"
    >
      <div v-if="selectedResult" class="detail-content">
        <div class="detail-row">
          <div class="detail-item">
            <label>策略</label>
            <span>{{ getStrategyName(selectedResult.strategy_code) }}</span>
          </div>
          <div class="detail-item">
            <label>股票</label>
            <span>{{ selectedResult.symbol }} {{ selectedResult.stock_name }}</span>
          </div>
        </div>
        <div class="detail-row">
          <div class="detail-item">
            <label>检查日期</label>
            <span>{{ selectedResult.check_date }}</span>
          </div>
          <div class="detail-item">
            <label>匹配结果</label>
            <span class="status-badge" :class="selectedResult.match_result ? 'success' : 'info'">
              {{ selectedResult.match_result ? '✓ 匹配' : '✗ 不匹配' }}
            </span>
          </div>
        </div>
        <div class="detail-row">
          <div class="detail-item">
            <label>最新价</label>
            <span>{{ selectedResult.latest_price }}</span>
          </div>
          <div class="detail-item">
            <label>涨跌幅</label>
            <span :class="getPriceClass(selectedResult.change_percent)">
              {{ selectedResult.change_percent }}%
            </span>
          </div>
        </div>
        <div class="detail-row">
          <div class="detail-item">
            <label>匹配度评分</label>
            <span>{{ selectedResult.match_score || '-' }}</span>
          </div>
          <div class="detail-item">
            <label>创建时间</label>
            <span>{{ selectedResult.created_at }}</span>
          </div>
        </div>
        <div v-if="selectedResult.match_details" class="detail-full">
          <label>匹配详情</label>
          <pre>{{ JSON.stringify(selectedResult.match_details, null, 2) }}</pre>
        </div>
      </div>
    </DetailDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api'
import {
  PageHeader,
  FilterBar,
  StockListTable,
  PaginationBar,
  DetailDialog
} from '@/components/shared'

import type {
  FilterItem,
  TableColumn
} from '@/components/shared'

interface Strategy {
  strategy_code: string
  strategy_name_cn: string
}

interface QueryForm {
  strategy_code: string
  symbol: string
  check_date: string
  match_result: boolean | null
}

interface Pagination {
  page: number
  pageSize: number
  total: number
}

interface Result {
  check_date: string
  strategy_code: string
  symbol: string
  stock_name: string
  match_result: boolean
  latest_price: number
  change_percent: number | null
  match_score: number | null
  created_at: string
  match_details?: any
}

const strategies = ref<Strategy[]>([])
const loading = ref(false)
const results = ref<Result[]>([])
const detailsVisible = ref(false)
const selectedResult = ref<Result | null>(null)

const queryForm = ref<QueryForm>({
  strategy_code: '',
  symbol: '',
  check_date: '',
  match_result: null
})

const pagination = ref<Pagination>({
  page: 1,
  pageSize: 20,
  total: 0
})

const filterConfig = computed((): FilterItem[] => [
  {
    type: 'select',
    key: 'strategy_code',
    label: '策略',
    placeholder: '全部策略',
    options: [
      { value: '', label: '全部策略' },
      ...strategies.value.map(item => ({
        value: item.strategy_code,
        label: item.strategy_name_cn
      }))
    ]
  },
  {
    type: 'input',
    key: 'symbol',
    label: '股票代码',
    placeholder: '输入股票代码'
  },
  {
    type: 'date-picker',
    key: 'check_date',
    label: '检查日期',
    placeholder: '选择日期'
  },
  {
    type: 'select',
    key: 'match_result',
    label: '匹配结果',
    placeholder: '全部',
    options: [
      { value: null as any, label: '全部' },
      { value: true, label: '匹配' },
      { value: false, label: '不匹配' }
    ]
  }
])

const tableColumns = computed((): TableColumn[] => [
  {
    prop: 'check_date',
    label: '检查日期',
    width: 120
  },
  {
    prop: 'strategy_code',
    label: '策略',
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
    prop: 'match_result',
    label: '匹配结果',
    width: 100,
    align: 'center'
  },
  {
    prop: 'latest_price',
    label: '最新价',
    width: 100,
    align: 'right'
  },
  {
    prop: 'change_percent',
    label: '涨跌幅',
    width: 100,
    align: 'right'
  },
  {
    prop: 'match_score',
    label: '匹配度',
    width: 100,
    align: 'right'
  },
  {
    prop: 'created_at',
    label: '创建时间',
    width: 180
  },
  {
    prop: 'actions',
    label: '操作',
    width: 150,
    align: 'center'
  }
])

const loadStrategies = async (): Promise<void> => {
  try {
    const response = await strategyApi.getDefinitions()
    if (response.data.success) {
      strategies.value = response.data.data
    }
  } catch (error) {
    console.error('加载策略列表失败:', error)
  }
}

const getStrategyName = (code: string): string => {
  const strategy = strategies.value.find(s => s.strategy_code === code)
  return strategy ? strategy.strategy_name_cn : code
}

const getPriceClass = (changePercent: number | null): string => {
  if (!changePercent) return ''
  const value = parseFloat(String(changePercent))
  if (value > 0) return 'positive'
  if (value < 0) return 'negative'
  return ''
}

const handleQuery = async (): Promise<void> => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize
    }

    if (queryForm.value.strategy_code) {
      params.strategy_code = queryForm.value.strategy_code
    }
    if (queryForm.value.symbol) {
      params.symbol = queryForm.value.symbol
    }
    if (queryForm.value.check_date) {
      params.check_date = queryForm.value.check_date
    }
    if (queryForm.value.match_result !== null) {
      params.match_result = queryForm.value.match_result
    }

    const response = await strategyApi.getResults(params)
    if (response.data.success) {
      results.value = response.data.data
      pagination.value.total = response.data.total || results.value.length
      ElMessage.success(`查询成功，共${results.value.length}条结果`)
    } else {
      ElMessage.error(response.data.message || '查询失败')
    }
  } catch (error: any) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const handleReset = (): void => {
  queryForm.value = {
    strategy_code: '',
    symbol: '',
    check_date: '',
    match_result: null
  }
  pagination.value.page = 1
  handleQuery()
}

const handlePageChange = (page: number): void => {
  pagination.value.page = page
  handleQuery()
}

const viewDetails = (row: Result): void => {
  selectedResult.value = row
  detailsVisible.value = true
}

const rerun = (row: Result): void => {
  ElMessage.info(`重新运行策略：${row.strategy_code} on ${row.symbol}`)
}

const handleExport = (): void => {
  if (results.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  try {
    const headers = [
      '检查日期',
      '策略代码',
      '策略名称',
      '股票代码',
      '股票名称',
      '匹配结果',
      '最新价',
      '涨跌幅(%)',
      '匹配度评分',
      '创建时间'
    ]

    const rows = results.value.map(row => [
      row.check_date || '',
      row.strategy_code || '',
      getStrategyName(row.strategy_code),
      row.symbol || '',
      row.stock_name || '',
      row.match_result ? '匹配' : '不匹配',
      row.latest_price || '',
      row.change_percent || '',
      row.match_score || '',
      row.created_at || ''
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell =>
        `"${String(cell).replace(/"/g, '""')}"`
      ).join(','))
    ].join('\n')

    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })

    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `策略结果_${new Date().toISOString().slice(0, 10)}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success(`成功导出 ${results.value.length} 条记录`)
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + error.message)
  }
}

onMounted(() => {
  loadStrategies()
  handleQuery()
})
</script>

<style scoped lang="scss">

.results-query {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  padding: 30px;
  position: relative;
  border-radius: 0;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
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
}

.query-header {
  margin-bottom: 20px;
}

.table-container {
  min-height: 400px;
  margin-bottom: 20px;
}

.tag {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(212, 175, 55, 0.15);
  border: 1px solid var(--gold-dim);
  color: var(--gold-primary);
  font-family: var(--font-display);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  font-family: var(--font-display);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 0;

  &.success {
    background: rgba(0, 230, 118, 0.15);
    border: 1px solid rgba(0, 230, 118, 0.3);
    color: var(--fall);
  }

  &.info {
    background: rgba(212, 175, 55, 0.15);
    border: 1px solid var(--gold-dim);
    color: var(--gold-primary);
  }
}

.table-action {
  padding: 4px 12px;
  margin-right: 4px;
  background: transparent;
  border: 1px solid var(--gold-dim);
  color: var(--gold-primary);
  font-family: var(--font-display);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  border-radius: 0;
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--gold-primary);
    background: rgba(212, 175, 55, 0.1);
  }

  &.primary {
    background: rgba(212, 175, 55, 0.15);
    border-color: var(--gold-dim);

    &:hover {
      background: rgba(212, 175, 55, 0.25);
    }
  }
}

.positive {
  color: var(--rise);
  font-weight: 600;
}

.negative {
  color: var(--fall);
  font-weight: 600;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 20px;

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--gold-dim);
    border-top-color: var(--gold-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  p {
    color: var(--text-muted);
    font-family: var(--font-body);
    font-size: 14px;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 20px;

  p {
    color: var(--text-muted);
    font-family: var(--font-body);
    font-size: 14px;
  }
}

.detail-content {
  padding: 10px;
}

.detail-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.detail-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-family: var(--font-display);
    font-size: 11px;
    color: var(--gold-dim);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  span {
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: 14px;
  }
}

.detail-full {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--gold-dim);

  label {
    display: block;
    font-family: var(--font-display);
    font-size: 11px;
    color: var(--gold-dim);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
  }

  pre {
    background: var(--bg-primary);
    padding: 15px;
    font-size: 12px;
    color: var(--text-primary);
    font-family: 'Courier New', monospace;
    border: 1px solid var(--gold-dim);
    max-height: 250px;
    overflow: auto;
    border-radius: 0;
  }
}

@media (max-width: 768px) {
  .results-query {
    padding: 10px;
  }

  .card {
    padding: 15px;
  }

  .detail-row {
    flex-direction: column;
    gap: 15px;
  }
}
</style>
