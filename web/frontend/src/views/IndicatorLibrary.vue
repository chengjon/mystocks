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
        <div v-for="(count, category) in categoryCounts" :key="category" class="stat-item">
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
          />

          <select v-model="selectedCategory" class="category-select">
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
            v-for="(filter, _idx) in quickFilters"
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
        v-for="(indicator, _idx) in filteredIndicators"
        :key="indicator.abbreviation"
        class="indicator-card hover-lift"
      >
        <template #header>
          <div class="indicator-header">
            <span class="indicator-abbr">{{ indicator.abbreviation }}</span>
            <div class="indicator-badges">
              <span class="web3-tag category-tag">{{ getCategoryLabel(indicator.category) }}</span>
              <span class="web3-tag panel-tag">{{ getPanelLabel(indicator.panel_type || indicator.panelType) }}</span>
            </div>
          </div>
        </template>

        <div class="indicator-content">
          <div class="info-section">
            <h3>{{ indicator.full_name || indicator.fullName }}</h3>
            <h4>{{ indicator.chinese_name || indicator.chineseName }}</h4>
            <p class="description">{{ indicator.description }}</p>
          </div>

          <div v-if="indicator.parameters && indicator.parameters.length > 0" class="params-section">
            <h4 class="section-title">
              <span class="section-icon">⚙</span>
              PARAMETERS
            </h4>
            <div class="params-grid">
              <div v-for="param in indicator.parameters" :key="param.name" class="param-item">
                <span class="param-label mono">{{ param.display_name || param.displayName }}</span>
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
  display_name?: string
  displayName?: string
  type: string
  default: unknown
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
  // Optional camelCase aliases for snake_case properties
  fullName?: string
  chineseName?: string
  panelType?: string
}

const loading: Ref<boolean> = ref(false)
const registry: Ref<IndicatorRegistryResponse | null> = ref(null)
const searchQuery: Ref<string> = ref('')
const selectedCategory: Ref<string> = ref('')

const _indicatorFilters = [
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

interface QuickFilter {
  key: string
  label: string
  filters: { search: string; category: string }
}

const quickFilters: QuickFilter[] = [
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
  } catch (error: unknown) {
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
    indicators = indicators.filter((ind: IndicatorData) => {
      return (
        (ind.abbreviation ?? '').toLowerCase().includes(query) ||
        (ind.full_name ?? ind.fullName ?? '').toLowerCase().includes(query) ||
        (ind.chinese_name ?? ind.chineseName ?? '').includes(query) ||
        (ind.description ?? '').toLowerCase().includes(query)
      )
    })
  }

  if (selectedCategory.value) {
    indicators = indicators.filter((ind: IndicatorData) => ind.category === selectedCategory.value)
  }

  return indicators as IndicatorData[]
})

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

// Computed property for category counts
const categoryCounts: ComputedRef<Record<string, number>> = computed(() => {
  if (!registry.value?.indicators) return {}
  const counts: Record<string, number> = {}
  for (const ind of registry.value.indicators as IndicatorData[]) {
    const cat = ind.category || 'other'
    counts[cat] = (counts[cat] || 0) + 1
  }
  return counts
})

const _getStatVariant = (category: string | undefined): 'default' | 'gold' | 'rise' | 'fall' => {
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

const _getBadgeVariant = (category: string): 'gold' | 'rise' | 'fall' | 'info' | 'warning' | 'success' | 'danger' => {
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

const isActiveFilter = (filter: QuickFilter): boolean => {
  return filter.filters.search === searchQuery.value && filter.filters.category === selectedCategory.value
}

const applyQuickFilter = (filter: QuickFilter): void => {
  searchQuery.value = filter.filters.search
  selectedCategory.value = filter.filters.category
  // 不需要调用 handleFilterChange，因为已经直接设置了值
}
</script>

<style scoped>
@import "./styles/IndicatorLibrary.css";
</style>
