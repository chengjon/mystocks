<template>
  <div v-if="preferenceStore.showPerformance" class="performance-monitor">
    <div class="metric-row">
      <span class="label">FPS</span>
      <span class="value" :class="fpsColor">{{ metrics.fps }}</span>
    </div>
    <div v-if="metrics.memory" class="metric-row">
      <span class="label">MEM</span>
      <span class="value">{{ metrics.memory.used }}MB</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePerformanceMonitor } from '@/composables/usePerformanceMonitor'
import { usePreferenceStore } from '@/stores/preferenceStore'

const { metrics } = usePerformanceMonitor()
const preferenceStore = usePreferenceStore()

const fpsColor = computed(() => {
  if (metrics.value.fps >= 50) return 'good'
  if (metrics.value.fps >= 30) return 'ok'
  return 'bad'
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.performance-monitor {
  position: fixed;
  bottom: var(--artdeco-spacing-2);
  right: var(--artdeco-spacing-2);
  background: color-mix(in srgb, var(--artdeco-bg-global) 70%, transparent);
  padding: calc(var(--artdeco-spacing-px) * 6) calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);
  border-radius: var(--artdeco-radius-sm);
  color: var(--artdeco-fg-primary);
  font-family: var(--font-mono);
  font-size: calc(var(--artdeco-text-xs) - var(--artdeco-spacing-px) * 2);
  z-index: calc(var(--artdeco-z-fixed) + 10);
  pointer-events: none;
  display: flex;
  gap: var(--artdeco-spacing-3);
  border: 1px solid var(--artdeco-gold-opacity-10);
  backdrop-filter: blur(var(--artdeco-spacing-px) * 2);
}

.metric-row {
  display: flex;
  gap: var(--artdeco-spacing-1);
}

.label {
  color: var(--artdeco-fg-muted);
}

.value {
  font-weight: bold;
  
  &.good { color: var(--artdeco-success); }
  &.ok { color: var(--artdeco-warning); }
  &.bad { color: var(--artdeco-error); }
}
</style>
