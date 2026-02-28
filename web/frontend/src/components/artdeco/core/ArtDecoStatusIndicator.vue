<template>
  <div class="artdeco-status-indicator" :class="[status, size, { animated }]">
    <span v-if="label" class="label">{{ label }}</span>
    <div class="indicator-dot"></div>
    <span v-if="value" class="value">{{ value }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label?: string
  status: 'online' | 'offline' | 'degraded' | 'good' | 'warning' | 'error' | 'low' | 'medium' | 'high'
  value?: string
  animated?: boolean
  size?: 'xs' | 'sm' | 'md' | 'lg'
}

const _props = withDefaults(defineProps<Props>(), {
  label: '',
  value: '',
  animated: false,
  size: 'md'
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.artdeco-status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--artdeco-font-mono);
  font-size: 12px;

  .label {
    color: var(--artdeco-fg-muted);
  }

  .indicator-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--status-color, var(--artdeco-fg-muted));
    box-shadow: 0 0 4px var(--status-color, var(--artdeco-fg-muted));
  }

  .value {
    color: var(--artdeco-fg-secondary);
    font-weight: 500;
  }

  // Size variants
  &.xs {
    font-size: 10px;
    gap: 4px;

    .indicator-dot {
      width: 4px;
      height: 4px;
    }
  }

  &.sm {
    font-size: 11px;
    gap: 6px;

    .indicator-dot {
      width: 5px;
      height: 5px;
    }
  }

  &.md {
    font-size: 12px;
    gap: 8px;

    .indicator-dot {
      width: 6px;
      height: 6px;
    }
  }

  &.lg {
    font-size: 14px;
    gap: 10px;

    .indicator-dot {
      width: 8px;
      height: 8px;
    }
  }

  // Animated variant
  &.animated .indicator-dot {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 100%;
    }
    50% {
      opacity: 50%;
    }
  }

  // Status mapping
  &.online, &.good, &.low {
    --status-color: var(--artdeco-up);
  }

  &.degraded, &.warning, &.medium {
    --status-color: var(--artdeco-accent-gold);
  }

  &.offline, &.error, &.high {
    --status-color: var(--artdeco-down);
  }
}
</style>