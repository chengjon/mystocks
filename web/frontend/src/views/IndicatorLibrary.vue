<template>
  <div class="indicator-library">

    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">INDICATOR LIBRARY</h1>
      <p class="page-subtitle">{{ registry?.total_count || 0 }} TECHNICAL INDICATORS ACROSS 5 CATEGORIES</p>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-section">
        :label="'TOTAL'"
        :value="registry?.total_count || 0"
        type="warning"
      />

        v-for="(count, category) in (registry as any)?.categories"
        :key="category"
        :label="getCategoryLabel(String(category))"
        :value="count"
        type="getStatVariant(String(category))"
      /> -->
      <p>TOTAL: {{ registry?.total_count || 0 }} indicators</p>
      <div v-for="(count, category) in (registry as any)?.categories" :key="category">
        {{ getCategoryLabel(String(category)) }}: {{ count }}
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="filter-section">
        title="INDICATOR FILTERS"
        :filters="indicatorFilters"
        :quick-filters="quickFilters"
        @filter-change="handleFilterChange"
      /> -->
    </div>

    <!-- Indicators List -->
    <div v-loading="loading" class="indicators-container">
      <el-card
        v-for="indicator in filteredIndicators"
        :key="indicator.abbreviation"
        class="indicator-card"
        :hoverable="true"
      >
        <template #header>
          <div class="indicator-header">
            <span class="indicator-abbr gold">{{ indicator.abbreviation }}</span>
            <div class="indicator-badges">
              <!-- <el-tag :text="getCategoryLabel(indicator.category)" type="getBadgeVariant(indicator.category)" />
              <el-tag :text="getPanelLabel(indicator.panel_type)" type="info" /> -->
              <el-tag>{{ getCategoryLabel(indicator.category) }}</el-tag>
              <el-tag type="info">{{ getPanelLabel(indicator.panel_type) }}</el-tag>
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
              <!-- <el-tag
                v-for="(line, idx) in indicator.reference_lines"
                :key="idx"
                :text="String(line)"
                type="warning"
              /> -->
              <el-tag
                v-for="(line, idx) in indicator.reference_lines"
                :key="idx"
                type="warning"
              >
                {{ line }}
              </el-tag>
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
import { ElCard } from 'element-plus'
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

const getCategoryLabel = (category: string): string => {
  const labelMap: Record<string, string> = {
    trend: 'TREND',
    momentum: 'MOMENTUM',
    volatility: 'VOLATILITY',
    volume: 'VOLUME',
    candlestick: 'CANDLESTICK'
  }
  return labelMap[category] || category
}

const getStatVariant = (category: string): 'default' | 'gold' | 'rise' | 'fall' => {
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

const getPanelLabel = (panelType: string): string => {
  return panelType === 'overlay' ? 'MAIN OVERLAY' : 'SEPARATE PANEL'
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
  margin-bottom: var(--space-lg);
}

.page-title {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.2em;
  margin: 0 0 var(--space-md) 0;
  text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}

.page-subtitle {
  font-family: var(--font-body);
  font-size: 1rem;
  color: var(--silver-muted);
  letter-spacing: 0.1em;
  margin: 0;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}

/* Filter Section */
.filter-section {
  margin-bottom: var(--space-lg);
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
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.indicator-abbr {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0;
}

.indicator-badges {
  display: flex;
  gap: var(--space-sm);
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

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--space-2xl);
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: var(--space-lg);
}

.empty-state h3 {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--silver-text);
  margin: 0 0 var(--space-md) 0;
}

.empty-state p {
  font-family: var(--font-body);
  font-size: 0.875rem;
  color: var(--silver-muted);
  margin: 0;
}

.mono {
  font-family: var(--font-mono);
}

.gold {
  color: var(--gold-primary);
}

/* Loading Override */
:deep(.el-loading-mask) {
  background-color: var(--bg-card) !important;
}

:deep(.el-loading-spinner .path) {
  stroke: var(--gold-primary);
}

:deep(.el-loading-text) {
  color: var(--gold-primary);
}
</style>
