<template>
  <span :class="badgeClasses" class="status-badge">
    <slot></slot>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md'
})

const badgeClasses = computed(() => [
  `status-badge-${props.variant}`,
  `status-badge-${props.size}`
])
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--artdeco-spacing-1) calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px));
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-sm);
  font-weight: var(--artdeco-font-medium);
  line-height: var(--artdeco-leading-tight);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wider);
  border-radius: var(--artdeco-radius-sm);
  border: 1px solid var(--artdeco-border-default);
  background: var(--artdeco-bg-card);
  color: var(--artdeco-fg-muted);
  box-shadow: inset 0 0 0 var(--artdeco-spacing-px) color-mix(in srgb, var(--artdeco-border-default) 35%, transparent);
  transition:
    border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
    color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  --data-status-success: var(--artdeco-down);
  --data-status-danger: var(--artdeco-rise);
  --data-status-info: var(--artdeco-info);
  --data-status-warning: var(--artdeco-warning);

  &.status-badge-sm {
    padding: calc(var(--artdeco-spacing-1) / 2) calc(var(--artdeco-spacing-1) + var(--artdeco-spacing-px));
    font-size: var(--artdeco-text-compact-xs);
  }

  &.status-badge-md {
    padding: var(--artdeco-spacing-1) calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px));
    font-size: var(--artdeco-text-compact-sm);
  }

  &.status-badge-lg {
    padding: calc(var(--artdeco-spacing-1) + (var(--artdeco-spacing-px) * 2)) var(--artdeco-spacing-3);
    font-size: var(--artdeco-text-compact-base);
  }

  &.status-badge-default {
    background: color-mix(in srgb, var(--artdeco-bg-elevated) 45%, var(--artdeco-bg-card));
    color: var(--artdeco-fg-muted);
    border-color: var(--artdeco-border-default);
  }

  &.status-badge-success {
    background: color-mix(in srgb, var(--data-status-success) 12%, var(--artdeco-bg-card));
    color: var(--data-status-success);
    border-color: color-mix(in srgb, var(--data-status-success) 50%, var(--artdeco-border-default));
  }

  &.status-badge-warning {
    background: color-mix(in srgb, var(--data-status-warning) 12%, var(--artdeco-bg-card));
    color: var(--data-status-warning);
    border-color: color-mix(in srgb, var(--data-status-warning) 55%, var(--artdeco-border-default));
  }

  &.status-badge-danger {
    background: color-mix(in srgb, var(--data-status-danger) 12%, var(--artdeco-bg-card));
    color: var(--data-status-danger);
    border-color: color-mix(in srgb, var(--data-status-danger) 55%, var(--artdeco-border-default));
  }

  &.status-badge-info {
    background: color-mix(in srgb, var(--data-status-info) 12%, var(--artdeco-bg-card));
    color: var(--data-status-info);
    border-color: color-mix(in srgb, var(--data-status-info) 55%, var(--artdeco-border-default));
  }
}
</style>
