<template>
  <div class="artdeco-status-indicator" :class="status">
    <span class="label">{{ label }}</span>
    <div class="indicator-dot"></div>
    <span class="value">{{ value }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  status: 'online' | 'offline' | 'degraded' | 'good' | 'warning' | 'error' | 'low' | 'medium' | 'high'
  value: string
}>()
</script>

<style scoped lang="scss">
.artdeco-status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-family-mono, monospace);
  font-size: 12px;

  .label {
    color: var(--artdeco-text-secondary, #888);
  }

  .indicator-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--status-color, #888);
    box-shadow: 0 0 4px var(--status-color, #888);
  }

  .value {
    color: var(--artdeco-text-primary, #ccc);
    font-weight: 500;
  }

  // Status mapping
  &.online, &.good, &.low {
    --status-color: #00ff9d;
  }
  
  &.degraded, &.warning, &.medium {
    --status-color: #ffd700;
  }
  
  &.offline, &.error, &.high {
    --status-color: #ff3e3e;
  }
}
</style>