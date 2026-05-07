<script setup lang="ts">
import { ArtDecoStatCard } from '@/components/artdeco'

defineProps<{
  cards: Array<{
    label: string
    value: string
    variant: 'gold' | 'rise' | 'fall'
  }>
}>()
</script>

<template>
  <section class="stats-strip artdeco-card-shell">
    <ArtDecoStatCard
      v-for="card in cards"
      :key="card.label"
      :label="card.label"
      :value="card.value"
      :variant="card.variant"
      :show-change="false"
    />
  </section>
</template>
