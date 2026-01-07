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
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 12px;
  font-weight: 500;
  border-radius: 3px;
  border: 1px solid transparent;

  // Sizes
  &.status-badge-sm {
    padding: 2px 6px;
    font-size: 11px;
  }

  &.status-badge-md {
    padding: 4px 10px;
    font-size: 12px;
  }

  &.status-badge-lg {
    padding: 6px 12px;
    font-size: 13px;
  }

  // Variants
  &.status-badge-default {
    background: #1A1A1A;
    color: #A0A0A0;
    border-color: #2A2A2A;
  }

  &.status-badge-success {
    background: rgba(0, 230, 118, 0.1);
    color: #00E676;
    border-color: rgba(0, 230, 118, 0.2);
  }

  &.status-badge-warning {
    background: rgba(255, 193, 7, 0.1);
    color: #FFC107;
    border-color: rgba(255, 193, 7, 0.2);
  }

  &.status-badge-danger {
    background: rgba(255, 82, 82, 0.1);
    color: #FF5252;
    border-color: rgba(255, 82, 82, 0.2);
  }

  &.status-badge-info {
    background: rgba(59, 130, 246, 0.1);
    color: #3B82F6;
    border-color: rgba(59, 130, 246, 0.2);
  }
}
</style>
