<template>
  <section class="kpi-grid">
    <ArtDecoStatCard
      v-for="item in normalizedItems"
      :key="item.label"
      :label="item.label"
      :value="item.value"
      :variant="item.variant"
      :show-change="false"
    />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoStatCard } from '@/components/artdeco'

interface KpiItem {
  label: string
  value: string | number
  variant?: 'gold' | 'rise' | 'fall'
}

const props = defineProps<{
  items: KpiItem[]
}>()

const normalizedItems = computed(() =>
  props.items.map((item) => ({
    ...item,
    value: typeof item.value === 'number' && Number.isFinite(item.value) ? String(item.value) : item.value,
  })),
)
</script>

<style scoped lang="scss">
@use './styles/BacktestKpiGrid';
</style>
