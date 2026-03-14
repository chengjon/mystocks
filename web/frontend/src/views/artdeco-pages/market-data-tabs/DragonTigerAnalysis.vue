<template>
  <div class="lhb-analysis">
    <ArtDecoCard title="龙虎榜数据" hoverable class="lhb-card">
      <div class="lhb-controls">
        <ArtDecoSelect
          :model-value="currentDate"
          :options="dateOptions"
          placeholder="选择日期"
          @update:model-value="handleDateChange"
        />
        <div class="lhb-filters">
          <button
            v-for="(f, _idx) in filters"
            :key="f.key"
            class="filter-btn"
            :class="{ active: currentFilter === f.key }"
            @click="handleFilterChange(f.key)"
          >
            {{ f.label }}
          </button>
        </div>
      </div>

      <ArtDecoTable :columns="columns" :data="displayRows" />
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { ArtDecoCard, ArtDecoSelect, ArtDecoTable } from '@/components/artdeco'
import { extractDragonTigerRows, type DragonTigerRow } from './dragonTigerData'

interface Props {
  lhbData: unknown[]
  lhbDate: string
  activeFilter: string
}

const props = withDefaults(defineProps<Props>(), {
  lhbData: () => [],
  lhbDate: 'today',
  activeFilter: 'buy'
})
const emit = defineEmits(['date-change', 'filter-change'])
const { exec } = useArtDecoApi()
const internalRows = ref<DragonTigerRow[]>([])
const currentDate = ref(props.lhbDate)
const currentFilter = ref(props.activeFilter)

watch(() => props.lhbDate, (value) => {
  currentDate.value = value
})

watch(() => props.activeFilter, (value) => {
  currentFilter.value = value
})

const hasExternalRows = computed(() => Array.isArray(props.lhbData) && props.lhbData.length > 0)
const displayRows = computed(() => {
  if (hasExternalRows.value) {
    return extractDragonTigerRows(props.lhbData, currentFilter.value, currentDate.value)
  }
  return internalRows.value
})

const dateOptions = [
  { label: '今日', value: 'today' },
  { label: '昨日', value: 'yesterday' },
  { label: '前日', value: 'dayBefore' }
]

const filters = [
  { key: 'buy', label: '买入榜' },
  { key: 'sell', label: '卖出榜' },
  { key: 'institution', label: '机构榜' }
]

const columns = [
  { key: 'rank', label: '排名', width: '60px' },
  { key: 'tradeDate', label: '交易日', width: '120px' },
  { key: 'stockInfo', label: '股票信息' },
  { key: 'reason', label: '上榜原因' },
  { key: 'buyAmount', label: '买入金额', align: 'right' },
  { key: 'sellAmount', label: '卖出金额', align: 'right' },
  { key: 'netBuy', label: '净买入', variant: 'color', align: 'right' },
  { key: 'turnoverRate', label: '换手率', align: 'right' }
]

const fetchDragonTigerRows = async () => {
  const data = await exec(() => apiClient.get('/v2/market/lhb', { params: { limit: 100 } }), {
    silent: true,
  })

  internalRows.value = extractDragonTigerRows(
    data && typeof data === 'object' ? (data as { data?: unknown[] }).data ?? data : data,
    currentFilter.value,
    currentDate.value,
  )
}

function handleDateChange(value: string) {
  currentDate.value = value
  emit('date-change', value)
  if (!hasExternalRows.value) {
    void fetchDragonTigerRows()
  }
}

function handleFilterChange(value: string) {
  currentFilter.value = value
  emit('filter-change', value)
  if (!hasExternalRows.value) {
    void fetchDragonTigerRows()
  }
}

onMounted(() => {
  if (!hasExternalRows.value) {
    void fetchDragonTigerRows()
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.lhb-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
}

.lhb-filters {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.filter-btn {
  background: transparent;
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;
  transition: all var(--artdeco-duration-base);

  &.active {
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
  }
}
</style>
