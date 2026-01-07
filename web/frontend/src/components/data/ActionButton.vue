<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="button-spinner"></span>
    <span v-if="$slots.prefix" class="button-prefix">
      <slot name="prefix"></slot>
    </span>
    <slot></slot>
    <span v-if="$slots.suffix" class="button-suffix">
      <slot name="suffix"></slot>
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'success'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  block?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'secondary',
  size: 'md',
  disabled: false,
  loading: false,
  block: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => [
  'action-button',
  `action-button-${props.variant}`,
  `action-button-${props.size}`,
  {
    'action-button-block': props.block,
    'action-button-disabled': props.disabled,
    'action-button-loading': props.loading
  }
])

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
.action-button {
  // 紧凑设计：最小化 padding
  padding: 0 16px;
  height: 36px; // md size

  font-family: 'Inter', system-ui, sans-serif;
  font-size: 13px; // 紧凑字体
  font-weight: 500;

  background: #1A1A1A;
  border: 1px solid #2A2A2A;
  border-radius: 4px;
  color: #E5E5E5;
  cursor: pointer;

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  transition: background 150ms ease, border-color 150ms ease, color 150ms ease;

  &:hover:not(:disabled) {
    background: #252525;
    border-color: #3A3A3A;
  }

  &:active:not(:disabled) {
    transform: translateY(1px);
  }

  &.action-button-block {
    width: 100%;
  }

  &.action-button-disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  // Sizes
  &.action-button-sm {
    height: 28px; // sm
    padding: 0 12px;
    font-size: 12px;
  }

  &.action-button-lg {
    height: 40px; // lg
    padding: 0 20px;
    font-size: 14px;
  }

  // Variants
  &.action-button-primary {
    background: #3B82F6;
    border-color: #3B82F6;

    &:hover:not(:disabled) {
      background: #2563EB;
      border-color: #2563EB;
    }
  }

  &.action-button-danger {
    background: #FF5252;
    border-color: #FF5252;

    &:hover:not(:disabled) {
      background: #E53935;
      border-color: #E53935;
    }
  }

  &.action-button-success {
    background: #00E676;
    border-color: #00E676;
    color: #000000;

    &:hover:not(:disabled) {
      background: #00C853;
      border-color: #00C853;
    }
  }

  // Loading spinner
  .button-spinner {
    width: 12px;
    height: 12px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
