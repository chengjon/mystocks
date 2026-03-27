<template>
  <div class="loading-spinner-wrapper" :class="wrapperClasses">
    <div class="spinner" :class="spinnerClasses"></div>
    <p v-if="text" class="loading-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  size?: 'sm' | 'md' | 'lg'
  overlay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  size: 'md',
  overlay: false
})

const wrapperClasses = computed(() => ({
  'loading-spinner-overlay': props.overlay
}))

const spinnerClasses = computed(() => `spinner-${props.size}`)
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.loading-spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-6);

  --data-loading-spinner-border-width: calc(var(--artdeco-spacing-3) / 4);
  --data-loading-spinner-overlay: color-mix(in srgb, var(--artdeco-bg-global) 84%, transparent);

  &.loading-spinner-overlay {
    position: fixed;
    inset: 0 0 0 0;
    background: var(--data-loading-spinner-overlay);
    z-index: 9999;
    backdrop-filter: blur(var(--artdeco-spacing-1));
  }
}

.spinner {
  border-radius: 50%;
  border: var(--data-loading-spinner-border-width) solid color-mix(in srgb, var(--artdeco-border-default) 70%, transparent);
  border-top-color: var(--artdeco-gold-primary);
  animation: spin 1s linear infinite;
  box-shadow: 0 0 var(--artdeco-spacing-3) color-mix(in srgb, var(--artdeco-gold-primary) 28%, transparent);

  &.spinner-sm {
    width: var(--artdeco-spacing-6);
    height: var(--artdeco-spacing-6);
    border-width: var(--artdeco-spacing-px);
  }

  &.spinner-md {
    width: var(--artdeco-spacing-8);
    height: var(--artdeco-spacing-8);
    border-width: var(--data-loading-spinner-border-width);
  }

  &.spinner-lg {
    width: var(--artdeco-spacing-10);
    height: var(--artdeco-spacing-10);
    border-width: var(--artdeco-spacing-1);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-sm);
  color: var(--artdeco-fg-muted);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
  margin: 0;
}
</style>
