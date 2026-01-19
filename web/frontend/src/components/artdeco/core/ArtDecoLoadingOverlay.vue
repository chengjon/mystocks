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
.artdeco-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(2px);

  .loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 24px;
    background-color: var(--artdeco-bg-secondary, #1a1a1a);
    border: 1px solid var(--artdeco-border-color, #333);
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    min-width: 200px;

    .spinner {
      width: 32px;
      height: 32px;
      border: 3px solid var(--artdeco-bg-tertiary, #333);
      border-top-color: var(--artdeco-accent-color, #d4af37);
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    .message {
      color: var(--artdeco-text-primary, #fff);
      font-size: 14px;
    }

    .progress-bar {
      width: 100%;
      height: 4px;
      background-color: var(--artdeco-bg-tertiary, #333);
      border-radius: 2px;
      overflow: hidden;

      .progress-fill {
        height: 100%;
        background-color: var(--artdeco-accent-color, #d4af37);
        transition: width 0.3s ease;
      }
    }
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>