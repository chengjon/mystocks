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
.loading-spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;

  &.loading-spinner-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    z-index: 9999;
  }
}

.spinner {
  border-radius: 50%;
  border: 3px solid #1A1A1A;
  border-top-color: #3B82F6;
  animation: spin 1s linear infinite;

  &.spinner-sm {
    width: 24px;
    height: 24px;
    border-width: 2px;
  }

  &.spinner-md {
    width: 32px;
    height: 32px;
    border-width: 3px;
  }

  &.spinner-lg {
    width: 40px;
    height: 40px;
    border-width: 4px;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 12px;
  color: #A0A0A0;
  margin: 0;
}
</style>
