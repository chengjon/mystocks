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
  gap: var(--artdeco-spacing-2);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);

  .label {
    color: var(--artdeco-fg-muted);
  }

  .indicator-dot {
    width: calc(var(--artdeco-spacing-3) / 2);
    height: calc(var(--artdeco-spacing-3) / 2);
    border-radius: 50%;
    background-color: var(--status-color, var(--artdeco-fg-muted));
    box-shadow: 0 0 var(--artdeco-spacing-1) var(--status-color, var(--artdeco-fg-muted));
  }

  .value {
    color: var(--artdeco-fg-secondary);
    font-weight: 500;
  }

  // Size variants
  &.xs {
    font-size: calc(var(--artdeco-spacing-5) / 2);
    gap: var(--artdeco-spacing-1);

    .indicator-dot {
      width: var(--artdeco-spacing-1);
      height: var(--artdeco-spacing-1);
    }
  }

  &.sm {
    font-size: var(--artdeco-text-compact-xs);
    gap: calc(var(--artdeco-spacing-3) / 2);

    .indicator-dot {
      width: calc(var(--artdeco-spacing-5) / 4);
      height: calc(var(--artdeco-spacing-5) / 4);
    }
  }

  &.md {
    font-size: var(--artdeco-text-xs);
    gap: var(--artdeco-spacing-2);

    .indicator-dot {
      width: calc(var(--artdeco-spacing-3) / 2);
      height: calc(var(--artdeco-spacing-3) / 2);
    }
  }

  &.lg {
    font-size: var(--artdeco-text-sm);
    gap: calc(var(--artdeco-spacing-5) / 2);

    .indicator-dot {
      width: var(--artdeco-spacing-2);
      height: var(--artdeco-spacing-2);
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
