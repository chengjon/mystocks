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
@use '@/styles/artdeco-tokens.scss' as *;

.artdeco-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--ad-overlay-bg);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--ad-overlay-z);
  backdrop-filter: blur(var(--ad-overlay-blur));

  .loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--artdeco-spacing-4);
    padding: var(--artdeco-spacing-6);
    background-color: var(--ad-card-bg-elevated);
    border: 1px solid var(--ad-card-border-hover);
    border-radius: var(--ad-tooltip-radius);
    box-shadow: var(--ad-card-shadow-hover);
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
      color: var(--ad-tooltip-text);
      font-size: var(--ad-tooltip-font-size);
      font-weight: var(--ad-tooltip-font-weight);
      max-width: var(--ad-tooltip-max-width);
      text-align: center;
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
