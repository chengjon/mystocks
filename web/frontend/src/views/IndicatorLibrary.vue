<template>
  <div class="indicator-library">

    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">INDICATOR LIBRARY</h1>
      <p class="page-subtitle">{{ registry?.total_count || 0 }} TECHNICAL INDICATORS ACROSS 5 CATEGORIES</p>
    </div>

    <!-- Statistics Cards -->
    <el-card class="stats-section">
      <div class="stats-content">
        <div class="stat-item">
          <span class="stat-label">TOTAL INDICATORS</span>
          <span class="stat-value gold">{{ registry?.total_count || 0 }}</span>
        </div>
        <div v-for="(count, category) in (registry as any)?.categories" :key="category" class="stat-item">
          <span class="stat-label">{{ getCategoryLabel(String(category)) }}</span>
          <span class="stat-value">{{ count }}</span>
        </div>
      </div>
    </el-card>

    <!-- Search and Filter -->
    <el-card class="filter-section">
      <template #header>
        <div class="card-header">
          <span class="card-title">INDICATOR FILTERS</span>
        </div>
      </template>

      <div class="filter-content">
        <div class="filter-row">
          <el-input
            v-model="searchQuery"
            placeholder="SEARCH INDICATOR NAME, ABBREVIATION OR DESCRIPTION..."
            class="search-input"
            @input="handleFilterChange"
          />

          <select v-model="selectedCategory" @change="handleFilterChange" class="category-select">
            <option value="">ALL CATEGORIES</option>
            <option value="trend">TREND</option>
            <option value="momentum">MOMENTUM</option>
            <option value="volatility">VOLATILITY</option>
            <option value="volume">VOLUME</option>
            <option value="candlestick">CANDLESTICK</option>
          </select>
        </div>

        <div class="quick-filters">
          <el-button
            v-for="filter in quickFilters"
            :key="filter.key"
            :type="isActiveFilter(filter) ? 'primary' : 'default'"
            :plain="!isActiveFilter(filter)"
            size="small"
            @click="applyQuickFilter(filter)"
          >
            {{ filter.label }}
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- Indicators List -->
    <div v-loading="loading" class="indicators-container">
      <el-card
        v-for="indicator in filteredIndicators"
        :key="indicator.abbreviation"
        class="indicator-card hover-lift"
      >
        <template #header>
          <div class="indicator-header">
            <span class="indicator-abbr">{{ indicator.abbreviation }}</span>
            <div class="indicator-badges">
              <span class="web3-tag category-tag">{{ getCategoryLabel(indicator.category) }}</span>
              <span class="web3-tag panel-tag">{{ getPanelLabel(indicator.panel_type) }}</span>
            </div>
          </div>
        </template>

        <div class="indicator-content">
          <div class="info-section">
            <h3>{{ indicator.full_name }}</h3>
            <h4>{{ indicator.chinese_name }}</h4>
            <p class="description">{{ indicator.description }}</p>
          </div>

          <div v-if="indicator.parameters && indicator.parameters.length > 0" class="params-section">
            <h4 class="section-title">
              <span class="section-icon">⚙</span>
              PARAMETERS
            </h4>
            <div class="params-grid">
              <div v-for="param in indicator.parameters" :key="param.name" class="param-item">
                <span class="param-label mono">{{ param.display_name }}</span>
                <span class="param-type mono">{{ param.type }}</span>
                <span class="param-default mono">{{ param.default }}</span>
                <span class="param-range mono">
                  {{ param.min !== undefined ? `[${param.min}, ${param.max}]` : '-' }}
                </span>
              </div>
            </div>
          </div>

          <div class="outputs-section">
            <h4 class="section-title">
              <span class="section-icon">📊</span>
              OUTPUT FIELDS
            </h4>
            <div class="outputs-grid">
              <div
                v-for="(output, idx) in indicator.outputs"
                :key="idx"
                class="output-item"
              >
                <span class="output-label">{{ output.name }}</span>
                <span class="output-desc">{{ output.description }}</span>
              </div>
            </div>
          </div>

          <div v-if="indicator.reference_lines && indicator.reference_lines.length > 0" class="reference-section">
            <h4 class="section-title">
              <span class="section-icon">📍</span>
              REFERENCE LINES
            </h4>
             <div class="reference-tags">
               <span
                 v-for="(line, idx) in indicator.reference_lines"
                 :key="idx"
                 class="web3-tag reference-tag"
               >
                 {{ line }}
               </span>
             </div>
          </div>

          <div class="min-data-section">
            <span class="min-data-icon">ℹ</span>
            <span class="min-data-text mono">MINIMUM DATA POINTS: {{ indicator.min_data_points_formula }}</span>
          </div>
        </div>
      </el-card>

      <!-- Empty State -->
      <div v-if="filteredIndicators.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>NO MATCHING INDICATORS FOUND</h3>
        <p>Try adjusting your search or filter criteria</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Ref, type ComputedRef } from 'vue'
import { ElMessage } from 'element-plus'
import { indicatorService } from '@/services/indicatorService'
import type { IndicatorMetadata, IndicatorRegistryResponse } from '@/api/types/generated-types'

interface IndicatorParameters {
  name: string
  display_name: string
  type: string
  default: any
  min?: number
  max?: number
  description?: string
}

interface IndicatorOutput {
  name: string
  description: string
}

interface IndicatorData extends Omit<IndicatorMetadata, 'parameters' | 'outputs'> {
  parameters: IndicatorParameters[]
  outputs: IndicatorOutput[]
}

const loading: Ref<boolean> = ref(false)
const registry: Ref<IndicatorRegistryResponse | null> = ref(null)
const searchQuery: Ref<string> = ref('')
const selectedCategory: Ref<string> = ref('')

const indicatorFilters = [
  {
    key: 'search',
    label: 'SEARCH',
    type: 'text' as const,
    placeholder: 'SEARCH INDICATOR NAME, ABBREVIATION OR DESCRIPTION...'
  },
  {
    key: 'category',
    label: 'CATEGORY',
    type: 'select' as const,
    placeholder: 'SELECT CATEGORY',
    options: [
      { label: 'ALL CATEGORIES', value: '' },
      { label: 'TREND', value: 'trend' },
      { label: 'MOMENTUM', value: 'momentum' },
      { label: 'VOLATILITY', value: 'volatility' },
      { label: 'VOLUME', value: 'volume' },
      { label: 'CANDLESTICK', value: 'candlestick' }
    ]
  }
]

const quickFilters = [
  {
    key: 'all',
    label: 'ALL',
    filters: { search: '', category: '' }
  },
  {
    key: 'trend',
    label: 'TREND',
    filters: { search: '', category: 'trend' }
  },
  {
    key: 'momentum',
    label: 'MOMENTUM',
    filters: { search: '', category: 'momentum' }
  },
  {
    key: 'volatility',
    label: 'VOLATILITY',
    filters: { search: '', category: 'volatility' }
  }
]

onMounted(async (): Promise<void> => {
  await fetchIndicatorRegistry()
})

const fetchIndicatorRegistry = async (): Promise<void> => {
  loading.value = true
  try {
    registry.value = await indicatorService.getRegistry()
  } catch (error: any) {
    console.error('Failed to fetch indicator registry:', error)
    ElMessage.error('FAILED TO LOAD INDICATOR LIBRARY')
  } finally {
    loading.value = false
  }
}

const filteredIndicators: ComputedRef<IndicatorData[]> = computed(() => {
  if (!registry.value?.indicators) return []

  let indicators = registry.value.indicators as IndicatorData[]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    indicators = indicators.filter((ind: any) => {
      return (
        ind.abbreviation.toLowerCase().includes(query) ||
        ind.full_name.toLowerCase().includes(query) ||
        ind.chinese_name.includes(query) ||
        ind.description.toLowerCase().includes(query)
      )
    })
  }

  if (selectedCategory.value) {
    indicators = indicators.filter((ind: any) => ind.category === selectedCategory.value)
  }

  return indicators as IndicatorData[]
})

const handleFilterChange = (filters: Record<string, any>) => {
  searchQuery.value = filters.search || ''
  selectedCategory.value = filters.category || ''
}

const getCategoryLabel = (category: string | undefined): string => {
  if (!category) return ''
  const labelMap: Record<string, string> = {
    trend: 'TREND',
    momentum: 'MOMENTUM',
    volatility: 'VOLATILITY',
    volume: 'VOLUME',
    candlestick: 'CANDLESTICK'
  }
  return labelMap[category] || category
}

const getStatVariant = (category: string | undefined): 'default' | 'gold' | 'rise' | 'fall' => {
  if (!category) return 'default'
  const variantMap: Record<string, 'default' | 'gold' | 'rise' | 'fall'> = {
    trend: 'gold',
    momentum: 'rise',
    volatility: 'fall',
    volume: 'gold',
    candlestick: 'fall'
  }
  return variantMap[category] || 'gold'
}

const getBadgeVariant = (category: string): 'gold' | 'rise' | 'fall' | 'info' | 'warning' | 'success' | 'danger' => {
  const variantMap: Record<string, 'gold' | 'rise' | 'fall' | 'info' | 'warning' | 'success' | 'danger'> = {
    trend: 'gold',
    momentum: 'rise',
    volatility: 'fall',
    volume: 'info',
    candlestick: 'warning'
  }
  return variantMap[category] || 'info'
}

const getPanelLabel = (panelType: string | undefined): string => {
  if (!panelType) return ''
  return panelType === 'overlay' ? 'MAIN OVERLAY' : 'SEPARATE PANEL'
}

const isActiveFilter = (filter: any): boolean => {
  return filter.filters.search === searchQuery.value && filter.filters.category === selectedCategory.value
}

const applyQuickFilter = (filter: any): void => {
  searchQuery.value = filter.filters.search
  selectedCategory.value = filter.filters.category
  // 不需要调用 handleFilterChange，因为已经直接设置了值
}
</script>

<style scoped>

.indicator-library {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  padding: var(--space-xl);
  position: relative;
}

/* Background pattern */
.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 10px,
      rgba(212, 175, 55, 0.02) 10px,
      rgba(212, 175, 55, 0.02) 11px
    );
  pointer-events: none;
  z-index: -1;
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #F7931A 0%, #FFD600 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  margin: 0 0 16px 0;
  text-shadow: 0 0 20px rgba(247, 147, 26, 0.3);
}

.page-subtitle {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1rem;
  color: #94A3B8;
  letter-spacing: 0.1em;
  margin: 0;
}

/* Stats Section */
.stats-section {
  background: rgba(15, 17, 21, 0.8);
  border: 1px solid rgba(247, 147, 26, 0.3);
  border-radius: 8px;
  margin-bottom: 24px;
}

.stats-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  padding: 20px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.stat-value {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 24px;
  font-weight: 700;
  color: #E5E7EB;

  &.gold {
    color: #F7931A;
  }
}

/* Filter Section */
.filter-section {
  margin-bottom: 24px;
}

.filter-content {
  padding: 20px;
}

.filter-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
}

.category-select {
  min-width: 180px;
  padding: 8px 12px;
  background: rgba(15, 17, 21, 0.8);
  border: 1px solid rgba(247, 147, 26, 0.3);
  border-radius: 6px;
  color: #E5E7EB;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.category-select:focus {
  outline: none;
  border-color: #F7931A;
  box-shadow: 0 0 0 2px rgba(247, 147, 26, 0.2);
}

.quick-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Indicators Container */
.indicators-container {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: var(--space-lg);
}

/* Indicator Card */
.indicator-card {
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.indicator-card:hover {
  transform: translateY(-4px);
  border-color: rgba(247, 147, 26, 0.5);
  box-shadow: 0 0 30px -10px rgba(247, 147, 26, 0.2);
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.indicator-abbr {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.25rem;
  font-weight: 700;
  color: #F7931A;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0;
}

.indicator-badges {
  display: flex;
  gap: 8px;
}

.web3-tag {
  display: inline-block;
  padding: 4px 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-radius: 4px;
}

.category-tag {
  background: rgba(247, 147, 26, 0.1);
  color: #F7931A;
  border: 1px solid rgba(247, 147, 26, 0.3);
}

.panel-tag {
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.reference-tag {
  background: rgba(245, 101, 101, 0.1);
  color: #F56565;
  border: 1px solid rgba(245, 101, 101, 0.3);
}

.indicator-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  flex: 1;
}

/* Info Section */
.info-section {
  margin-bottom: var(--space-md);
  border-bottom: 1px solid rgba(212, 175, 55, 0.2);
  padding-bottom: var(--space-md);
}

.info-section h3 {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--silver-text);
  margin: 0 0 var(--space-xs) 0;
}

.info-section h4 {
  font-family: var(--font-body);
  font-size: 1rem;
  color: var(--silver-muted);
  margin: 0 0 var(--space-sm) 0;
}

.info-section .description {
  font-family: var(--font-body);
  font-size: 0.875rem;
  color: var(--silver-muted);
  line-height: 1.6;
  margin: 0;
}

/* Parameters Section */
.params-section,
.outputs-section,
.reference-section {
  margin-bottom: var(--space-md);
  border-bottom: 1px solid rgba(212, 175, 55, 0.2);
  padding-bottom: var(--space-md);
}

.section-title {
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0 0 var(--space-md) 0;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.section-icon {
  font-size: 1rem;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-sm);
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.param-label,
.param-type,
.param-default,
.param-range {
  font-family: var(--font-mono);
  font-size: 0.75rem;
}

.param-label {
  color: var(--gold-primary);
  font-weight: 600;
}

.param-type,
.param-default,
.param-range {
  color: var(--silver-muted);
}

/* Outputs Grid */
.outputs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
}

.output-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.output-label {
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.output-desc {
  font-family: var(--font-body);
  font-size: 0.875rem;
  color: var(--silver-muted);
  line-height: 1.4;
}

/* Reference Tags */
.reference-tags {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

/* Min Data Section */
.min-data-section {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  margin-top: var(--space-md);
}

.min-data-icon {
  font-size: 1.25rem;
}

.min-data-text {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--silver-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Card Header */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(247, 147, 26, 0.3);

  .card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #F7931A;
  }
}

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 48px;
  background: rgba(15, 17, 21, 0.8);
  border: 1px solid rgba(247, 147, 26, 0.3);
  border-radius: 8px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.empty-state h3 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.25rem;
  font-weight: 600;
  color: #E5E7EB;
  margin: 0 0 16px 0;
 }

.empty-state p {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  color: #94A3B8;
  margin: 0;
}

.mono {
  font-family: 'JetBrains Mono', monospace;
}

.gold {
  color: #F7931A;
}

/* Loading Override */
:deep(.el-loading-mask) {
  background-color: rgba(15, 17, 21, 0.8) !important;
}

:deep(.el-loading-spinner .path) {
  stroke: #F7931A;
}

:deep(.el-loading-text) {
  color: #F7931A;
}
</style>
