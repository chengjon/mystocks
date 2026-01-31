<template>
  <div class="artdeco-loading" :class="sizeClass">
    <div class="loading-spinner">
      <div class="spinner-ring" v-for="i in 3" :key="i"></div>
    </div>
    <div v-if="text" class="loading-text">{{ text }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  size: 'md'
})

const sizeClass = computed(() => `artdeco-loading-${props.size}`)
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-8);
  min-height: 200px;

  .loading-spinner {
    display: flex;
    gap: var(--artdeco-spacing-2);
    align-items: center;
    justify-content: center;
  }

  .spinner-ring {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--artdeco-gold-primary);
    animation: artdeco-loading-bounce 1.4s ease-in-out infinite both;

    &:nth-child(1) {
      animation-delay: -0.32s;
    }

    &:nth-child(2) {
      animation-delay: -0.16s;
    }

    &:nth-child(3) {
      animation-delay: 0s;
    }
  }

  .loading-text {
    font-family: var(--artdeco-font-body);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    margin-top: var(--artdeco-spacing-2);
  }

  &.sm {
    min-height: 100px;
    padding: var(--artdeco-spacing-4);

    .spinner-ring {
      width: 8px;
      height: 8px;
    }

    .loading-text {
      font-size: var(--artdeco-text-xs);
    }
  }

  &.lg {
    min-height: 300px;
    padding: var(--artdeco-spacing-12);

    .spinner-ring {
      width: 16px;
      height: 16px;
    }

    .loading-text {
      font-size: var(--artdeco-text-base);
    }
  }
}

@keyframes artdeco-loading-bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
