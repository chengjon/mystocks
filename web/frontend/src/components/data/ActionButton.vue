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
@use '@/styles/artdeco-tokens.scss' as *;

.action-button {
  padding: 0 var(--artdeco-spacing-4);
  height: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-1));
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-base);
  font-weight: var(--artdeco-font-medium);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--artdeco-bg-elevated) 55%, var(--artdeco-bg-card)) 0%,
    var(--artdeco-bg-card) 100%
  );
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
  color: var(--artdeco-fg-primary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  box-shadow: inset 0 0 0 var(--artdeco-spacing-px) color-mix(in srgb, var(--artdeco-gold-opacity-10) 70%, transparent);
  transition:
    transform var(--artdeco-transition-quick) var(--artdeco-ease-out),
    background var(--artdeco-transition-quick) var(--artdeco-ease-out),
    border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
    color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  --data-action-success: var(--artdeco-down);
  --data-action-danger: var(--artdeco-rise);

  &:hover:not(:disabled) {
    border-color: var(--artdeco-border-hover);
    color: var(--artdeco-gold-light);
    box-shadow: var(--artdeco-glow-subtle);
  }

  &:active:not(:disabled) {
    transform: translateY(var(--artdeco-spacing-px));
  }

  &.action-button-block {
    width: 100%;
  }

  &.action-button-disabled {
    opacity: 50%;
    cursor: not-allowed;
    box-shadow: none;
  }

  &.action-button-sm {
    height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-px));
    padding: 0 var(--artdeco-spacing-3);
    font-size: var(--artdeco-text-compact-sm);
  }

  &.action-button-lg {
    height: var(--artdeco-spacing-10);
    padding: 0 var(--artdeco-spacing-5);
    font-size: var(--artdeco-text-sm);
  }

  &.action-button-primary {
    background: linear-gradient(
      135deg,
      var(--artdeco-gold-light) 0%,
      var(--artdeco-gold-primary) 55%,
      var(--artdeco-bronze) 100%
    );
    border-color: var(--artdeco-gold-light);
    color: var(--artdeco-bg-global);
    box-shadow: 0 0 var(--artdeco-spacing-4) color-mix(in srgb, var(--artdeco-gold-primary) 26%, transparent);

    &:hover:not(:disabled) {
      background: linear-gradient(
        135deg,
        var(--artdeco-champagne) 0%,
        var(--artdeco-gold-light) 50%,
        var(--artdeco-gold-primary) 100%
      );
      border-color: var(--artdeco-champagne);
      color: var(--artdeco-bg-global);
    }
  }

  &.action-button-danger {
    background: color-mix(in srgb, var(--data-action-danger) 12%, var(--artdeco-bg-card));
    border-color: color-mix(in srgb, var(--data-action-danger) 55%, var(--artdeco-border-default));
    color: var(--data-action-danger);

    &:hover:not(:disabled) {
      background: color-mix(in srgb, var(--data-action-danger) 18%, var(--artdeco-bg-card));
      border-color: var(--data-action-danger);
      color: var(--artdeco-fg-primary);
    }
  }

  &.action-button-success {
    background: color-mix(in srgb, var(--data-action-success) 12%, var(--artdeco-bg-card));
    border-color: color-mix(in srgb, var(--data-action-success) 55%, var(--artdeco-border-default));
    color: var(--data-action-success);

    &:hover:not(:disabled) {
      background: color-mix(in srgb, var(--data-action-success) 18%, var(--artdeco-bg-card));
      border-color: var(--data-action-success);
      color: var(--artdeco-fg-primary);
    }
  }

  .button-spinner {
    width: var(--artdeco-spacing-3);
    height: var(--artdeco-spacing-3);
    border: var(--artdeco-spacing-px) solid transparent;
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
