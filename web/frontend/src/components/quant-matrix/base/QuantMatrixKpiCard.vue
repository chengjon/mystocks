<template>
  <article class="qm-kpi-card" :aria-label="label">
    <p class="qm-kpi-card__label">{{ label }}</p>
    <p class="qm-kpi-card__value">{{ value }}</p>
    <p class="qm-kpi-card__delta" :class="deltaClass">{{ delta }}</p>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label: string
  value: string
  delta: string
  trend?: 'up' | 'down' | 'neutral'
}

const props = withDefaults(defineProps<Props>(), {
  trend: 'neutral'
})

const deltaClass = computed(() => `qm-kpi-card__delta--${props.trend}`)
</script>

<style scoped lang="scss">
@import '@/styles/quant-matrix/components/quant-matrix-kpi-card.scss';
</style>
