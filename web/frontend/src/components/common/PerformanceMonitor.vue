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
@import '@/styles/artdeco-tokens.scss';

.performance-monitor {
  position: fixed;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 6px 10px;
  border-radius: 4px;
  color: #fff;
  font-family: monospace;
  font-size: 10px;
  z-index: 9999;
  pointer-events: none;
  display: flex;
  gap: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(2px);
}

.metric-row {
  display: flex;
  gap: 4px;
}

.label {
  color: #aaa;
}

.value {
  font-weight: bold;
  
  &.good { color: #4caf50; }
  &.ok { color: #ff9800; }
  &.bad { color: #f44336; }
}
</style>