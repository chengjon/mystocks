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
  font-family: Inter, system-ui, sans-serif;
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
    background: rgb(0 230 118 / 10%);
    color: #00E676;
    border-color: rgb(0 230 118 / 20%);
  }

  &.status-badge-warning {
    background: rgb(255 193 7 / 10%);
    color: #FFC107;
    border-color: rgb(255 193 7 / 20%);
  }

  &.status-badge-danger {
    background: rgb(255 82 82 / 10%);
    color: #FF5252;
    border-color: rgb(255 82 82 / 20%);
  }

  &.status-badge-info {
    background: rgb(59 130 246 / 10%);
    color: #3B82F6;
    border-color: rgb(59 130 246 / 20%);
  }
}
</style>
