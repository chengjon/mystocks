<template>
    <!-- 页面头部 -->
    <PageHeader
      title="股票列表"
      subtitle="STOCK LIST"
    />

    <!-- 筛选栏 -->
    <FilterBar
      :filters="filterConfig"
      @search="handleSearch"
      @reset="handleReset"
      @change="handleFilterChange"
    >
      <template #actions>
        <button class="button button-success" @click="handleRefresh" :class="{ loading: loading }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          刷新
        </button>
      </template>
    </FilterBar>

    <!-- 股票列表表格 -->
    <div class="card table-card">
      <div class="table-header">
        <div class="table-options">
          <div class="total-info">
            <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            共找到 <span class="total-number">{{ total }}</span> 只股票
          </div>
        </div>
      </div>

      <div class="card-body table-body">
        <StockListTable
          :columns="tableColumns"
          :data="stocks"
          :loading="loading"
          :actions="tableActions"
          :row-clickable="true"
          @selection-change="handleSelectionChange"
          @row-click="handleRowClick"
        >
          <template #cell-symbol="{ row }">
            <span class="mono">{{ row.symbol }}</span>
          </template>
          <template #cell-price="{ row }">
            <span class="price">{{ row.price || '--' }}</span>
          </template>
          <template #cell-change="{ row }">
            <span :class="getChangeClass(row.change)">
              {{ row.change ? (row.change > 0 ? '+' : '') + row.change : '--' }}
            </span>
          </template>
          <template #cell-change_pct="{ row }">
            <span :class="getChangeClass(row.change_pct)">
              {{ row.change_pct ? (row.change_pct > 0 ? '+' : '') + row.change_pct + '%' : '--' }}
            </span>
          </template>
          <template #cell-volume="{ row }">
            <span class="mono">{{ row.volume ? formatVolume(row.volume) : '--' }}</span>
          </template>
          <template #cell-turnover="{ row }">
            <span>{{ row.turnover ? row.turnover + '%' : '--' }}</span>
          </template>
          <template #cell-market="{ row }">
            <span :class="['market-badge', row.market.toLowerCase()]">
              {{ row.market }}
            </span>
          </template>
        </StockListTable>
      </div>

      <!-- 分页 -->
      <div class="table-footer">
        <PaginationBar
          v-model:page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          @page-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, type Ref } from 'vue'
import { dataApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { PageHeader, FilterBar, StockListTable, PaginationBar } from '@/components/shared'
import type { FilterItem, TableColumn, TableAction } from '@/components/shared'

const router = useRouter()
const loading = ref(false)
const currentRow: Ref<string | null> = ref(null)

const filters = reactive({
  search: '',
  industry: '',
  concept: '',
  market: ''
})

const industries = ref<Array<{ industry_name: string }>>([])
const concepts = ref<Array<{ concept_name: string }>>([])

const pagination = reactive({
  currentPage: 1,
  pageSize: 20
})

const stocks = ref([])
const total = ref(0)

// FilterBar 配置
const filterConfig = computed((): FilterItem[] => [
  {
    type: 'input',
    key: 'search',
    label: '搜索',
    placeholder: '股票代码或名称'
  },
  {
    type: 'select',
    key: 'industry',
    label: '行业',
    placeholder: '全部行业',
    options: [
      { value: '', label: '全部' },
      ...industries.value.map(item => ({
        value: item.industry_name || '',
        label: item.industry_name || '未命名行业'
      }))
    ]
  },
  {
    type: 'select',
    key: 'concept',
    label: '概念',
    placeholder: '全部概念',
    options: [
      { value: '', label: '全部' },
      ...concepts.value.map(item => ({
        value: item.concept_name || '',
        label: item.concept_name || '未命名概念'
      }))
    ]
  },
  {
    type: 'select',
    key: 'market',
    label: '市场',
    placeholder: '全部市场',
    options: [
      { value: '', label: '全部' },
      { value: 'SH', label: '上海' },
      { value: 'SZ', label: '深圳' }
    ]
  }
])

// StockListTable 列配置
const tableColumns = computed((): TableColumn[] => [
  {
    prop: 'symbol',
    label: '股票代码',
    width: 120,
    sortable: true,
    className: 'mono'
  },
  {
    prop: 'name',
    label: '股票名称',
    width: 120,
    sortable: true
  },
  {
    prop: 'industry',
    label: '行业',
    width: 150,
    sortable: true
  },
  {
    prop: 'market',
    label: '市场',
    width: 80,
    sortable: true
  },
  {
    prop: 'price',
    label: '价格',
    width: 100,
    sortable: true,
    align: 'right'
  },
  {
    prop: 'change',
    label: '涨跌额',
    width: 100,
    sortable: true,
    align: 'right',
    colorClass: (row) => getChangeClass(row.change)
  },
  {
    prop: 'change_pct',
    label: '涨跌幅(%)',
    width: 120,
    sortable: true,
    align: 'right',
    colorClass: (row) => getChangeClass(row.change_pct)
  },
  {
    prop: 'volume',
    label: '成交量',
    width: 120,
    sortable: true,
    align: 'right'
  },
  {
    prop: 'turnover',
    label: '换手率(%)',
    width: 120,
    sortable: true,
    align: 'right'
  }
])

// StockListTable 操作按钮
const tableActions = computed((): TableAction[] => [
  {
    key: 'view',
    text: '查看',
    type: 'button',
    variant: 'primary',
    size: 'small',
    handler: (row) => handleView(row)
  },
  {
    key: 'analyze',
    text: '分析',
    type: 'button',
    variant: 'default',
    size: 'small',
    handler: (row) => handleAnalyze(row)
  }
])

const loadFilterOptions = async () => {
  try {
    const [industriesRes, conceptsRes] = await Promise.all([
      dataApi.getStocksIndustries(),
      dataApi.getStocksConcepts()
    ])

    if (industriesRes.success) {
      industries.value = industriesRes.data
    }

    if (conceptsRes.success) {
      concepts.value = conceptsRes.data
    }
  } catch (error) {
    console.error('加载筛选选项失败:', error)
    ElMessage.error('加载筛选选项失败')
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      limit: pagination.pageSize,
      offset: (pagination.currentPage - 1) * pagination.pageSize
    }

    if (filters.search) {
      params.search = filters.search
    }
    if (filters.industry) {
      params.industry = filters.industry
    }
    if (filters.concept) {
      params.concept = filters.concept
    }
    if (filters.market) {
      params.market = filters.market
    }

    const response = await dataApi.getStocksBasic(params)
    if (response.success && response.data) {
      stocks.value = response.data
      total.value = response.total || response.data.length
    } else {
      throw new Error(response.msg || 'API返回数据格式错误')
    }
  } catch (error: unknown) {
    console.error('加载数据失败:', error)

    if (error && typeof error === 'object' && 'response' in error) {
      // Axios错误
      const axiosError = error as any
      ElMessage.error(`加载数据失败: ${axiosError.response.data?.msg || axiosError.response.data?.detail || '服务器错误'}`)
    } else if (error instanceof Error) {
      // 标准Error
      ElMessage.error(`加载数据失败: ${error.message}`)
    } else {
      // 未知错误
      ElMessage.error('加载数据失败: 未知错误')
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  filters.search = ''
  filters.industry = ''
  filters.concept = ''
  filters.market = ''
  pagination.currentPage = 1
  loadData()
}

const handleFilterChange = () => {
  pagination.currentPage = 1
  loadData()
}

const handleRefresh = () => {
  loadData()
}

const handlePageChange = (page: number) => {
  pagination.currentPage = page
  loadData()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadData()
}

const handleView = (row: { symbol: string; name: string }) => {
  router.push({ name: 'stock-detail', params: { symbol: row.symbol }, query: { name: row.name } })
}

const handleAnalyze = (row: { symbol: string; name: string }) => {
  ElMessage.info(`分析股票: ${row.name} (${row.symbol})`)
}

const handleRowClick = (row: { symbol: string; name: string }) => {
  currentRow.value = row.symbol
  handleView(row)
}

const handleSelectionChange = (selection: any[]) => {
  console.log('Selection changed:', selection)
}

const getChangeClass = (value: number | string | null | undefined) => {
  if (value === null || value === undefined || value === '--') return ''
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return numValue > 0 ? 'positive' : numValue < 0 ? 'negative' : ''
}

const formatVolume = (volume: number | null | undefined) => {
  if (!volume) return '--'
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(1) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(1) + '万'
  }
  return volume.toString()
}

onMounted(async () => {
  await loadFilterOptions()
  await loadData()
})
</script>

<style scoped lang="scss">
// Phase 3.3: Design Token Migration
@use 'sass:color';
@import '@/styles/theme-tokens.scss';

.stocks {
  padding: var(--spacing-lg);
  background: var(--color-bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
  min-height: 100vh;

  .table-card {
    margin-top: var(--spacing-lg);
  }

  .table-header {
    padding: var(--spacing-md) var(--spacing-lg);
    border-bottom: 1px solid var(--color-border);

    .table-options {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .total-info {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        font-family: var(--font-family-sans);
        font-size: var(--font-size-sm);
        color: var(--color-text-tertiary);

        .info-icon {
          width: 16px;
          height: 16px;
        }

        .total-number {
          font-family: var(--font-family-mono);
          font-weight: 600;
          color: var(--color-accent);
        }
      }
    }
  }

  .table-body {
    min-height: 400px;

    .mono {
      font-family: var(--font-family-mono);
    }

    .price {
      font-family: var(--font-family-mono);
      font-weight: 600;
    }

    .positive {
      color: var(--color-stock-down);
    }

    .negative {
      color: var(--color-stock-up);
    }

    .market-badge {
      display: inline-block;
      padding: 2px var(--spacing-sm);
      font-size: var(--font-size-xs);
      border-radius: var(--border-radius-sm);
      font-weight: 500;

      &.sh {
        background: var(--color-stock-down-alpha-90);
        color: var(--color-stock-down);
      }

      &.sz {
        background: var(--color-accent-alpha-90);
        color: var(--color-accent);
      }
    }
  }

  .table-footer {
    padding: var(--spacing-md) var(--spacing-lg);
    border-top: 1px solid var(--color-border);
  }

  .button {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    font-family: var(--font-family-sans);
    font-size: var(--font-size-sm);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    background: transparent;
    border: 2px solid var(--color-border);
    color: var(--color-accent);
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 0;

    svg {
      width: 16px;
      height: 16px;
    }

    &:hover:not(:disabled) {
      background: var(--color-accent-alpha-90);
      border-color: var(--color-accent);
      box-shadow: 0 4px 12px var(--color-accent-alpha-80);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    &.button-primary {
      background: var(--color-accent);
      color: var(--color-bg-primary);
      border-color: var(--color-accent);

      &:hover:not(:disabled) {
        background: var(--color-accent-hover);
        box-shadow: 0 4px 12px var(--color-accent-alpha-70);
      }
    }

    &.button-success {
      border-color: var(--color-stock-up);
      color: var(--color-stock-up);

      &:hover:not(:disabled) {
        background: var(--color-stock-up-alpha-90);
        border-color: var(--color-stock-up);
      }
    }

    &.loading {
      position: relative;
      pointer-events: none;

      &::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 14px;
        height: 14px;
        margin: -7px 0 0 -7px;
        border: 2px solid transparent;
        border-top-color: currentColor;
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
      }
    }
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
}

@media (max-width: 768px) {
  .stocks {
    padding: var(--spacing-md);
  }

  .table-header {
      padding: var(--spacing-md) var(--spacing-md);
    }

    .table-footer {
      padding: var(--spacing-md) var(--spacing-md);
    }
  }
</style>
