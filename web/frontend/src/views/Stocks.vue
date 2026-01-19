<template>
    <!-- Art Deco Header -->
    <ArtDecoHeader
      :title="'PORTFOLIO MANAGEMENT'"
      subtitle="STOCK PORTFOLIO | WATCHLIST | PERFORMANCE TRACKING"
      variant="gold-accent"
    />

    <!-- Art Deco Filter Bar -->
    <ArtDecoFilterBar
      :filters="filterConfig"
      @search="handleSearch"
      @reset="handleReset"
      @change="handleFilterChange"
    >
      <template #actions>
        <ArtDecoButton
          variant="primary"
          :glow="true"
          :loading="loading"
          @click="handleRefresh"
        >
          <template #icon>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6"></path>
              <path d="M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </template>
          REFRESH DATA
        </ArtDecoButton>
      </template>
    </ArtDecoFilterBar>

    <!-- Art Deco Portfolio Table -->
    <ArtDecoCard variant="luxury" :decorated="true">
      <template #header>
        <div class="table-header-section">
          <ArtDecoBadge variant="gold">PORTFOLIO ASSETS</ArtDecoBadge>
          <div class="portfolio-stats">
            <span class="stat-label">TOTAL STOCKS:</span>
            <span class="stat-value">{{ total }}</span>
          </div>
        </div>
      </template>

      <ArtDecoTable
        :data="stocks"
        :loading="loading"
        gold-headers
        striped
        :row-clickable="true"
        @row-click="handleRowClick"
        @selection-change="handleSelectionChange"
      >
        <template #columns>
          <ArtDecoTableColumn prop="symbol" label="SYMBOL" width="120" sortable>
            <template #default="{ row }">
              <span class="artdeco-mono">{{ row.symbol }}</span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="name" label="NAME" width="150" sortable />

          <ArtDecoTableColumn prop="price" label="PRICE" width="100" align="right" sortable>
            <template #default="{ row }">
              <span class="artdeco-price">{{ row.price || '--' }}</span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="change" label="CHANGE" width="100" align="right" sortable>
            <template #default="{ row }">
              <span :class="getArtDecoChangeClass(row.change)">
                {{ row.change ? (row.change > 0 ? '+' : '') + row.change : '--' }}
              </span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="change_pct" label="CHANGE %" width="120" align="right" sortable>
            <template #default="{ row }">
              <span :class="getArtDecoChangeClass(row.change_pct)">
                {{ row.change_pct ? (row.change_pct > 0 ? '+' : '') + row.change_pct + '%' : '--' }}
              </span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="volume" label="VOLUME" width="120" align="right" sortable>
            <template #default="{ row }">
              <span class="artdeco-mono">{{ row.volume ? formatVolume(row.volume) : '--' }}</span>
            </template>
          </ArtDecoTableColumn>

          <ArtDecoTableColumn prop="market" label="MARKET" width="80" sortable>
            <template #default="{ row }">
              <ArtDecoBadge :variant="getMarketBadgeVariant(row.market)">
                {{ row.market }}
              </ArtDecoBadge>
            </template>
          </ArtDecoTableColumn>
        </template>

        <template #actions="{ row }">
          <ArtDecoButton
            variant="outline"
            size="small"
            @click="handleView(row)"
          >
            VIEW
          </ArtDecoButton>

          <ArtDecoButton
            variant="gold"
            size="small"
            @click="handleAnalyze(row)"
          >
            ANALYZE
          </ArtDecoButton>
        </template>
      </ArtDecoTable>

      <!-- Art Deco Pagination -->
      <template #footer>
        <div class="pagination-section">
          <ArtDecoPagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            @page-change="handlePageChange"
            @size-change="handleSizeChange"
          />
        </div>
      </template>
    </ArtDecoCard>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, type Ref } from 'vue'
import { dataApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
// Import Art Deco components
import {
  ArtDecoHeader,
  ArtDecoFilterBar,
  ArtDecoTable,
  ArtDecoTableColumn,
  ArtDecoPagination,
  ArtDecoButton,
  ArtDecoBadge,
  ArtDecoCard
} from '@/components/artdeco'

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

// Table columns are now defined inline in template using ArtDecoTableColumn

// Table actions are now defined inline in template using ArtDecoButton

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

// Legacy change class function (for backward compatibility)
const getChangeClass = (value: number | string | null | undefined) => {
  if (value === null || value === undefined || value === '--') return ''
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return numValue > 0 ? 'positive' : numValue < 0 ? 'negative' : ''
}

// Art Deco change class function
const getArtDecoChangeClass = (value: number | string | null | undefined) => {
  if (value === null || value === undefined || value === '--') return ''
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return numValue > 0 ? 'artdeco-positive' : numValue < 0 ? 'artdeco-negative' : ''
}

// Market badge variant function
const getMarketBadgeVariant = (market: string) => {
  return market.toLowerCase() === 'sh' ? 'success' : 'primary'
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
// Art Deco Design System Integration
@import '@/styles/artdeco-tokens.scss';

.stocks-page {
  @include artdeco-crosshatch-bg(); // Diagonal crosshatch background
  min-height: 100vh;
  padding: $artdeco-spacing-xl;

  .table-header-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;

    .portfolio-stats {
      display: flex;
      align-items: center;
      gap: $artdeco-spacing-sm;
      font-family: 'Marcellus', serif;
      text-transform: uppercase;
      letter-spacing: 0.2em;
      font-size: $artdeco-font-size-sm;
      color: $artdeco-text-muted;

      .stat-label {
        font-weight: 400;
      }

      .stat-value {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: $artdeco-accent-gold;
        font-size: $artdeco-font-size-lg;
      }
    }
  }

  .pagination-section {
    display: flex;
    justify-content: center;
    padding: $artdeco-spacing-lg;
    border-top: 2px solid $artdeco-accent-gold;
  }

  // Art Deco specific styling
  .artdeco-mono {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
  }

  .artdeco-price {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: $artdeco-font-size-base;
  }

  .artdeco-positive {
    color: $artdeco-color-up; // Red for gains
    font-weight: 600;
  }

  .artdeco-negative {
    color: $artdeco-color-down; // Green for losses
    font-weight: 600;
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

// Art Deco responsive design
@media (max-width: 768px) {
  .stocks-page {
    padding: $artdeco-spacing-lg;

    .table-header-section {
      flex-direction: column;
      gap: $artdeco-spacing-md;
      align-items: flex-start;

      .portfolio-stats {
        font-size: $artdeco-font-size-xs;
      }
    }

    .pagination-section {
      padding: $artdeco-spacing-md;
    }
  }
}

// Art Deco animations
@keyframes artdeco-fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes artdeco-glow-pulse {
  0%, 100% {
    box-shadow: 0 0 5px rgba(212, 175, 55, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.6), 0 0 30px rgba(212, 175, 55, 0.4);
  }
}

  .table-header {
      padding: var(--spacing-md) var(--spacing-md);
    }

    .table-footer {
      padding: var(--spacing-md) var(--spacing-md);
    }
  }
</style>
