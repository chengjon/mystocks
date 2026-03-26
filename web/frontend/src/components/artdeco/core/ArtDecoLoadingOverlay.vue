<template>
  <div class="artdeco-loading-overlay">
    <div class="loading-content">
      <div class="spinner"></div>
      <div class="message">{{ message }}</div>
      <div v-if="progress !== undefined && progress > 0" class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message?: string
  progress?: number
}>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.artdeco-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: color-mix(in srgb, var(--artdeco-bg-global) 70%, transparent);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(calc(var(--artdeco-spacing-1) / 2));

  .loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--artdeco-spacing-4);
    padding: var(--artdeco-spacing-6);
    background-color: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-opacity-20);
    border-radius: var(--artdeco-spacing-1);
    box-shadow: var(--artdeco-shadow-lg);
    min-width: calc(var(--artdeco-spacing-20) * 2 + var(--artdeco-spacing-10));

    .spinner {
      width: var(--artdeco-spacing-8);
      height: var(--artdeco-spacing-8);
      border: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-bg-secondary);
      border-top-color: var(--artdeco-accent-gold);
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    .message {
      color: var(--artdeco-fg-primary);
      font-size: var(--artdeco-text-sm);
    }

    .progress-bar {
      width: 100%;
      height: var(--artdeco-spacing-1);
      background-color: var(--artdeco-bg-secondary);
      border-radius: calc(var(--artdeco-spacing-1) / 2);
      overflow: hidden;

      .progress-fill {
        height: 100%;
        background-color: var(--artdeco-accent-gold);
        transition: width 0.3s ease;
      }
    }
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
