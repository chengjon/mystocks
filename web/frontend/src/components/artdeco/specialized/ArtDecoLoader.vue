<template>
    <div class="artdeco-loader-container" :class="{ fullscreen: fullscreen }">
        <div class="artdeco-loader-wrapper">
            <div class="artdeco-loader" :style="loaderStyle"></div>
            <div v-if="text" class="artdeco-loader-text">{{ text }}</div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Props {
        text?: string
        size?: number
        fullscreen?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        text: 'COMPUTING...',
        size: 40,
        fullscreen: false
    })

    const loaderStyle = computed(() => ({
        width: `${props.size}px`,
        height: `${props.size}px`
    }))
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-loader-container {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: var(--artdeco-spacing-5);
    }

    .artdeco-loader-container.fullscreen {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(10, 12, 14, 0.9);
      z-index: var(--artdeco-z-modal);
    }

    .artdeco-loader-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: var(--artdeco-spacing-4);
    }

    .artdeco-loader {
      border: 2px solid rgba(212, 175, 55, 0.2);
      position: relative;
      animation: artdeco-spin 3s linear infinite;
    }

    .artdeco-loader::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 50%;
      height: 50%;
      background: var(--artdeco-accent-gold);
      animation: artdeco-pulse 1.5s ease-in-out infinite alternate;
    }

    .artdeco-loader-text {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      color: var(--artdeco-accent-gold);
      letter-spacing: 3px;
      text-transform: uppercase;
      text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }

    @keyframes artdeco-spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    @keyframes artdeco-pulse {
      0% {
        opacity: 0.2;
        transform: translate(-50%, -50%) scale(0.7) rotate(45deg);
      }
      100% {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1.1) rotate(45deg);
        box-shadow: 0 0 15px var(--artdeco-accent-gold);
      }
    }
</style>
