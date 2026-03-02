<template>
  <section class="kpi-grid">
    <ArtDecoStatCard
      v-for="item in items"
      :key="item.label"
      :label="item.label"
      :value="item.value"
      :variant="item.variant"
    />
  </section>
</template>

<script setup lang="ts">
import { ArtDecoStatCard } from '@/components/artdeco'

interface KpiItem {
  label: string
  value: string | number
  variant?: 'gold' | 'rise' | 'fall'
}

defineProps<{
  items: KpiItem[]
}>()
</script>

<style scoped lang="scss">
@import './styles/BacktestKpiGrid';
</style>
