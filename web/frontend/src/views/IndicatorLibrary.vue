<template>
  <div class="web3-indicator-library">
    <!-- Page header with gradient text -->
    <div class="web3-page-header">
      <h1 class="web3-page-title">
        <span class="gradient-text">TECHNICAL INDICATOR LIBRARY</span>
      </h1>
      <p class="web3-page-subtitle">161 TA-LIB TECHNICAL INDICATORS ACROSS 5 CATEGORIES</p>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <Web3Card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon-wrapper">
            <el-icon :size="48" color="#F7931A"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value gradient-text">{{ registry?.total_count || 0 }}</div>
            <div class="stat-label">TOTAL INDICATORS</div>
          </div>
        </div>
      </Web3Card>

      <Web3Card
        v-for="(count, category) in (registry as any)?.categories"
        :key="category"
        class="stat-card"
        hoverable
      >
        <div class="stat-content">
          <div class="stat-icon-wrapper">
            <el-icon :size="48" :color="getCategoryColor(String(category))">
              <component :is="getCategoryIcon(String(category))" />
            </el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value gradient-text">{{ count }}</div>
            <div class="stat-label">{{ getCategoryLabel(String(category)) }}</div>
          </div>
        </div>
      </Web3Card>
    </div>

    <!-- Search and Filter -->
    <Web3Card class="search-card" hoverable>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-input
            v-model="searchQuery"
            placeholder="SEARCH INDICATOR NAME, ABBREVIATION OR DESCRIPTION..."
            :prefix-icon="Search"
            clearable
            size="large"
          />
        </el-col>
        <el-col :span="12">
          <el-select
            v-model="selectedCategory"
            placeholder="SELECT CATEGORY"
            clearable
            size="large"
            style="width: 100%"
          >
            <el-option label="ALL CATEGORIES" value="" />
            <el-option label="TREND" value="trend" />
            <el-option label="MOMENTUM" value="momentum" />
            <el-option label="VOLATILITY" value="volatility" />
            <el-option label="VOLUME" value="volume" />
            <el-option label="CANDLESTICK" value="candlestick" />
          </el-select>
        </el-col>
      </el-row>
    </Web3Card>

    <!-- Indicators List -->
    <div v-loading="loading" class="indicators-container">
      <Web3Card
        v-for="indicator in filteredIndicators"
        :key="indicator.abbreviation"
        class="indicator-detail-card"
        hoverable
      >
        <template #header>
          <div class="indicator-header">
            <div class="indicator-title-group">
              <span class="indicator-abbr gradient-text">{{ indicator.abbreviation }}</span>
              <el-tag :type="getCategoryTagType(indicator.category)" size="small" class="web3-tag">
                {{ getCategoryLabel(indicator.category) }}
              </el-tag>
              <el-tag :type="getPanelTagType(indicator.panel_type as any)" size="small" class="web3-tag">
                {{ getPanelLabel(indicator.panel_type as any) }}
              </el-tag>
            </div>
          </div>
        </template>

        <div class="indicator-content">
          <!-- Basic Information -->
          <div class="info-section">
            <h3>{{ indicator.full_name }}</h3>
            <h4>{{ indicator.chinese_name }}</h4>
            <p class="description">{{ indicator.description }}</p>
          </div>

          <!-- Parameters -->
          <div v-if="indicator.parameters && indicator.parameters.length > 0" class="params-section">
            <h4 class="section-title">
              <el-icon><Setting /></el-icon>
              PARAMETERS
            </h4>
            <el-table :data="indicator.parameters" size="small" border class="web3-table">
              <el-table-column prop="display_name" label="NAME" width="120" />
              <el-table-column prop="type" label="TYPE" width="80" />
              <el-table-column prop="default" label="DEFAULT" width="80" />
              <el-table-column label="RANGE" width="100">
                <template #default="{ row }">
                  {{ row.min !== undefined ? `[${row.min}, ${row.max}]` : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="description" label="DESCRIPTION" />
            </el-table>
          </div>

          <!-- Outputs -->
          <div class="outputs-section">
            <h4 class="section-title">
              <el-icon><TrendCharts /></el-icon>
              OUTPUT FIELDS
            </h4>
            <el-descriptions :column="2" size="small" border class="web3-descriptions">
              <el-descriptions-item
                v-for="(output, idx) in indicator.outputs"
                :key="idx"
                :label="output.name"
              >
                {{ output.description }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- Reference Lines -->
          <div v-if="indicator.reference_lines && indicator.reference_lines.length > 0" class="reference-section">
            <h4 class="section-title">
              <el-icon><Position /></el-icon>
              REFERENCE LINES
            </h4>
            <el-space wrap>
              <el-tag
                v-for="(line, idx) in indicator.reference_lines"
                :key="idx"
                type="info"
                effect="plain"
                class="web3-tag"
              >
                {{ line }}
              </el-tag>
            </el-space>
          </div>

          <!-- Minimum Data Points -->
          <div class="min-data-section">
            <el-text size="small" type="info">
              <el-icon><InfoFilled /></el-icon>
              MINIMUM DATA POINTS: {{ indicator.min_data_points_formula }}
            </el-text>
          </div>
        </div>
      </Web3Card>

      <!-- No Results Message -->
      <el-empty v-if="filteredIndicators.length === 0 && !loading" description="NO MATCHING INDICATORS FOUND" />
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck

import { ref, computed, onMounted, type Ref, type ComputedRef } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search,
  DataLine,
  TrendCharts,
  Setting,
  Position,
  InfoFilled,
  Histogram,
  Connection,
  Timer,
  PieChart
} from '@element-plus/icons-vue'
import { indicatorService } from '@/services/indicatorService'
import type { IndicatorMetadata, IndicatorRegistryResponse } from '@/api/types/generated-types'
import { Web3Card } from '@/components/web3'

// Type definitions
type CategoryType = 'trend' | 'momentum' | 'volatility' | 'volume' | 'candlestick'
type PanelType = 'overlay' | 'separate'
type TagType = 'primary' | 'success' | 'warning' | 'info' | 'danger'

// State
const loading: Ref<boolean> = ref(false)
const registry: Ref<IndicatorRegistryResponse | null> = ref(null)
const searchQuery: Ref<string> = ref('')
const selectedCategory: Ref<string> = ref('')

// Lifecycle
onMounted(async (): Promise<void> => {
  await fetchIndicatorRegistry()
})

// Methods
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

const filteredIndicators: ComputedRef<IndicatorMetadata[]> = computed(() => {
  if (!registry.value?.indicators) return []

  let indicators = registry.value.indicators

  // Category filter
  if (selectedCategory.value) {
    indicators = indicators.filter(ind => ind.category === selectedCategory.value)
  }

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    indicators = indicators.filter(ind => {
      return (
        (ind as any).abbreviation.toLowerCase().includes(query) ||
        (ind as any).full_name.toLowerCase().includes(query) ||
        (ind as any).chinese_name.includes(query) ||
        ind.description.toLowerCase().includes(query)
      )
    })
  }

  return indicators
})

const getCategoryTagType = (category: string): TagType => {
  const typeMap: Record<string, TagType> = {
    trend: 'primary',
    momentum: 'success',
    volatility: 'warning',
    volume: 'info',
    candlestick: 'danger'
  }
  return typeMap[category] || 'info'
}

const getPanelTagType = (panelType: string): TagType => {
  return panelType === 'overlay' ? 'info' : 'warning'
}

const getPanelLabel = (panelType: PanelType): string => {
  return panelType === 'overlay' ? 'MAIN OVERLAY' : 'SEPARATE PANEL'
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

const getCategoryColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    trend: '#F7931A',
    momentum: '#00E676',
    volatility: '#FFD700',
    volume: '#6B7280',
    candlestick: '#EF4444'
  }
  return colorMap[category] || '#6B7280'
}

const getCategoryIcon = (category: string): Component => {
  const iconMap: Record<string, Component> = {
    trend: TrendCharts,
    momentum: Connection,
    volatility: Histogram,
    volume: PieChart,
    candlestick: Timer
  }
  return iconMap[category] || DataLine
}
</script>

<style scoped lang="scss">
@import '@/styles/web3-tokens.scss';
@import '@/styles/web3-global.scss';

.web3-indicator-library {
  @include web3-grid-bg;
  min-height: 100vh;
  padding: var(--web3-spacing-6);

  .web3-page-header {
    text-align: center;
    padding: var(--web3-spacing-10) 0;
    margin-bottom: var(--web3-spacing-8);

    .web3-page-title {
      font-family: var(--web3-font-heading);
      font-size: var(--web3-text-4xl);
      font-weight: var(--web3-weight-bold);
      margin: 0 0 var(--web3-spacing-3) 0;
      line-height: var(--web3-leading-tight);

      .gradient-text {
        background: var(--web3-gradient-orange);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }

    .web3-page-subtitle {
      font-family: var(--web3-font-body);
      font-size: var(--web3-text-sm);
      color: var(--web3-fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--web3-tracking-wide);
      margin: 0;
    }
  }

  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--web3-spacing-4);
    margin-bottom: var(--web3-spacing-6);

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: var(--web3-spacing-4);

        .stat-icon-wrapper {
          .el-icon {
            font-size: 48px;
          }
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: var(--web3-text-3xl);
            font-weight: var(--web3-weight-bold);
            color: var(--web3-fg-primary);
            line-height: 1.2;
            font-family: var(--web3-font-mono);

            &.gradient-text {
              background: var(--web3-gradient-orange);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              background-clip: text;
            }
          }

          .stat-label {
            margin-top: var(--web3-spacing-1);
            font-size: var(--web3-text-xs);
            text-transform: uppercase;
            letter-spacing: var(--web3-tracking-wide);
            color: var(--web3-fg-muted);
          }
        }
      }
    }
  }

  .search-card {
    margin-bottom: var(--web3-spacing-6);
  }

  .indicators-container {
    display: grid;
    gap: var(--web3-spacing-5);

    .indicator-detail-card {
      .indicator-header {
        .indicator-title-group {
          display: flex;
          align-items: center;
          gap: var(--web3-spacing-3);

          .indicator-abbr {
            font-size: var(--web3-text-xl);
            font-weight: var(--web3-weight-bold);
            font-family: var(--web3-font-heading);

            &.gradient-text {
              background: var(--web3-gradient-orange);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              background-clip: text;
            }
          }
        }
      }

      .indicator-content {
        display: flex;
        flex-direction: column;
        gap: var(--web3-spacing-5);

        .info-section {
          h3 {
            margin: 0 0 var(--web3-spacing-1) 0;
            font-size: var(--web3-text-lg);
            font-weight: var(--web3-weight-semibold);
            color: var(--web3-fg-primary);
          }

          h4 {
            margin: 0 0 var(--web3-spacing-3) 0;
            font-size: var(--web3-text-base);
            font-weight: var(--web3-weight-normal);
            color: var(--web3-fg-secondary);
          }

          .description {
            margin: 0;
            font-size: var(--web3-text-sm);
            color: var(--web3-fg-muted);
            line-height: 1.8;
          }
        }

        .section-title {
          display: flex;
          align-items: center;
          gap: var(--web3-spacing-2);
          margin: 0 0 var(--web3-spacing-3) 0;
          font-size: var(--web3-text-base);
          font-weight: var(--web3-weight-semibold);
          color: var(--web3-fg-primary);

          .el-icon {
            color: #F7931A;
          }
        }

        .min-data-section {
          padding: var(--web3-spacing-3);
          background: rgba(255, 255, 255, 0.02);
          border-radius: var(--web3-radius-md);
          border: 1px solid var(--web3-border-subtle);

          .el-text {
            display: flex;
            align-items: center;
            gap: var(--web3-spacing-1);
          }
        }
      }
    }
  }

  .web3-table {
    :deep(.el-table__header) {
      th {
        background: rgba(255, 255, 255, 0.02) !important;
        color: var(--web3-fg-secondary) !important;
        font-family: var(--web3-font-heading);
        font-weight: var(--web3-weight-semibold);
        text-transform: uppercase;
        border-bottom: 1px solid var(--web3-border-subtle) !important;
      }
    }

    :deep(.el-table__body) {
      tr {
        background: transparent !important;
        transition: background var(--web3-duration-fast);

        &:hover {
          background: rgba(247, 147, 26, 0.05) !important;
        }

        td {
          border-bottom: 1px solid var(--web3-border-subtle) !important;
          color: var(--web3-fg-primary);
        }
      }
    }
  }

  .web3-descriptions {
    :deep(.el-descriptions__label) {
      font-family: var(--web3-font-body);
      text-transform: uppercase;
      letter-spacing: var(--web3-tracking-wide);
      color: var(--web3-fg-muted);
    }

    :deep(.el-descriptions__content) {
      font-family: var(--web3-font-body);
      color: var(--web3-fg-primary);
    }
  }

  .gradient-text {
    background: var(--web3-gradient-orange);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .web3-tag {
    font-family: var(--web3-font-body);
    text-transform: uppercase;
    letter-spacing: var(--web3-tracking-wide);
  }
}

// Responsive
@media (max-width: 768px) {
  .web3-indicator-library {
    padding: var(--web3-spacing-4);

    .web3-page-header {
      .web3-page-title {
        font-size: var(--web3-text-2xl);
      }
    }

    .stats-cards {
      grid-template-columns: 1fr;
    }
  }
}
</style>
