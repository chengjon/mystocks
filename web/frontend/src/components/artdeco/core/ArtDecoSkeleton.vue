<template>
  <div 
    class="artdeco-skeleton"
    :class="[
      `skeleton-${variant}`,
      { 'skeleton-animated': animated }
    ]"
    :style="{
      width: width,
      height: height,
      borderRadius: radius
    }"
    role="status"
    aria-label="Loading..."
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'text', // text, rect, circle, button
    validator: (val: string) => ['text', 'rect', 'circle', 'button', 'image'].includes(val)
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: 'auto'
  },
  animated: {
    type: Boolean,
    default: true
  }
})

const radius = computed(() => {
  if (props.variant === 'circle') return '50%'
  if (props.variant === 'button') return '4px'
  if (props.variant === 'image') return '8px'
  return '2px' // text/rect default
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-skeleton {
  background-color: var(--artdeco-bg-elevated);
  display: inline-block;
  
  &.skeleton-text {
    height: 1em;
    margin-bottom: 0.5em;
    &:last-child { margin-bottom: 0; }
  }
  
  &.skeleton-button {
    height: 32px;
  }
  
  &.skeleton-animated {
    position: relative;
    overflow: hidden;
    
    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      transform: translateX(-100%);
      background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.05),
        transparent
      );
      animation: skeleton-loading 1.5s infinite;
    }
  }
}

@keyframes skeleton-loading {
  100% {
    transform: translateX(100%);
  }
}
</style>
