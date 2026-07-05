<template>
  <div class="fund-flow-analysis">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">capital flow desk</span>
          <div class="hero-meta">
            <span>WINDOW: {{ currentTimeFilterLabel }}</span>
            <span>RANKING: {{ currentRankingLabel }}</span>
            <span>ROWS: {{ displayStockRanking.length }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="资金流向工作台"
        subtitle="统一审查北向资金、主力净流入和个股排行，形成资金动向的总览入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" @click="fetchFundFlowData">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新资金流
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section :class="isEmbedded ? 'fund-overview embedded-summary' : 'stats-strip artdeco-card-shell fund-overview'">
      <ArtDecoStatCard
        label="沪股通净流入"
        :value="safeFundData.shanghai.amount"
        :change="safeFundData.shanghai.change"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="深股通净流入"
        :value="safeFundData.shenzhen.amount"
        :change="safeFundData.shenzhen.change"
        change-percent
        variant="gold"
      />
      <ArtDecoStatCard
        label="北向资金总额"
        :value="safeFundData.north.amount"
        :change="safeFundData.north.change"
        change-percent
        :variant="safeFundData.north.change > 0 ? 'rise' : 'fall'"
      />
      <ArtDecoStatCard
        label="主力净流入"
        :value="safeFundData.main.amount"
        :change="safeFundData.main.change"
        change-percent
        variant="gold"
      />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">flow ranking route</span>
          <h3 class="content-shell-title">趋势与排行面板</h3>
          <p class="content-shell-subtitle">结合近 30 日资金流向趋势和个股排行，观察主力资金在不同时间窗口下的迁移方向。</p>
        </div>
        <div class="content-shell-meta">
          <span>WINDOW: {{ currentTimeFilterLabel }}</span>
          <span>MODE: {{ currentRankingLabel }}</span>
        </div>
      </div>

      <ArtDecoCard title="近30日资金流向趋势" hoverable class="fund-chart-card">
        <div class="chart-container">
          <ArtDecoChart :option="trendChartOption" height="300px" />
        </div>
      </ArtDecoCard>

      <ArtDecoCard title="个股资金流向排行" hoverable class="fund-ranking-card">
        <div class="ranking-controls">
          <div class="time-filters">
            <button
              v-for="(filter, _idx) in timeFilters"
              :key="filter.key"
              class="filter-btn"
              :class="{ active: currentTimeFilter === filter.key }"
              @click="handleFilterChange(filter.key)"
            >
              {{ filter.label }}
            </button>
          </div>
          <ArtDecoSelect
            :model-value="currentRankingType"
            :options="rankingOptions"
            placeholder="选择排序方式"
            class="ranking-select"
            @update:model-value="handleRankingChange"
          />
        </div>

        <ArtDecoTable :columns="columns" :data="displayStockRanking" />

        <div v-if="fetchErrorMessage" class="fund-error-banner" role="alert">
          <ArtDecoIcon name="alert" />
          <span>{{ fetchErrorMessage }}</span>
        </div>
      </ArtDecoCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, ref, watch } from 'vue'
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import ArtDecoChart from '@/components/artdeco/charts/ArtDecoChart.vue'
import {
  buildFundOverview,
  buildFundTrend,
  buildStockRanking,
  type FundData,
  type TrendItem,
  type StockRankingRow,
} from './fundFlowPageData'

interface Props {
  fundData?: Partial<FundData>
  stockRanking?: unknown[]
  trendData?: TrendItem[]
  activeTimeFilter?: string
  rankingType?: string
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const defaultFundData = (): FundData => ({
  shanghai: { amount: 0, change: 0 },
  shenzhen: { amount: 0, change: 0 },
  north: { amount: 0, change: 0 },
  main: { amount: 0, change: 0 }
})

const props = withDefaults(defineProps<Props>(), {
  fundData: () => ({
    shanghai: { amount: 0, change: 0 },
    shenzhen: { amount: 0, change: 0 },
    north: { amount: 0, change: 0 },
    main: { amount: 0, change: 0 }
  }),
  stockRanking: () => [],
  trendData: () => [],
  activeTimeFilter: 'today',
  rankingType: 'main_force',
  functionKey: '',
  userPermissions: () => [],
  systemConfig: undefined
})
const emit = defineEmits(['filter-change', 'ranking-change'])
const instance = getCurrentInstance()
const internalFundData = ref<FundData>(defaultFundData())
const internalStockRanking = ref<StockRankingRow[]>([])
const internalTrendData = ref<TrendItem[]>([])
const fetchErrorMessage = ref('')
const currentTimeFilter = ref(props.activeTimeFilter)
const currentRankingType = ref(props.rankingType)

watch(() => props.activeTimeFilter, (value) => {
  currentTimeFilter.value = value
})

watch(() => props.rankingType, (value) => {
  currentRankingType.value = value
    // ... 329 lines omitted
  }
    // ... 328 lines omitted
  }
    // ... 327 lines omitted
  }
    // ... 326 lines omitted
interface ChartParams {
    // ... 325 lines omitted
}
    // ... 324 lines omitted
      }
    // ... 323 lines omitted
  }
    // ... 322 lines omitted
function formatDate(value: Date): string {
    // ... 321 lines omitted
}
    // ... 320 lines omitted
interface UnifiedResponseLike {
    // ... 319 lines omitted
}
    // ... 318 lines omitted
async function fetchFundFlowData() {
    // ... 317 lines omitted
  }
    // ... 316 lines omitted
  }
    // ... 315 lines omitted
    }
    // ... 314 lines omitted
  }
    // ... 313 lines omitted
}
    // ... 312 lines omitted
function handleFilterChange(value: string) {
    // ... 311 lines omitted
}
    // ... 310 lines omitted
function handleRankingChange(value: string) {
    // ... 309 lines omitted
}
    // ... 308 lines omitted
  }
    // ... 307 lines omitted
}
    // ... 306 lines omitted
}
    // ... 305 lines omitted
}
    // ... 304 lines omitted
}
    // ... 303 lines omitted
}
    // ... 302 lines omitted
}
    // ... 301 lines omitted
}
    // ... 300 lines omitted
}
    // ... 299 lines omitted
}
    // ... 298 lines omitted
}
    // ... 297 lines omitted
}
    // ... 296 lines omitted
}
    // ... 295 lines omitted
}
    // ... 294 lines omitted
}
    // ... 293 lines omitted
  }
}
    // ... 291 lines omitted
}
    // ... 290 lines omitted
}
    // ... 289 lines omitted
  }
    // ... 288 lines omitted
  }
    // ... 287 lines omitted
  }
    // ... 286 lines omitted
  }
}
// ... 284 more lines (total: 506)
<style scoped lang="scss">
@import "./styles/FundFlow.scss";
</style>
