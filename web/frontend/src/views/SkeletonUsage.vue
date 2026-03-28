<template>
  <div class="skeleton-demo">
    <h1>Skeleton Loading States</h1>
    
    <div class="demo-section">
      <h2>Text Variants</h2>
      <div class="card">
        <ArtDecoSkeleton variant="text" width="60%" />
        <ArtDecoSkeleton variant="text" width="90%" />
        <ArtDecoSkeleton variant="text" width="80%" />
      </div>
    </div>

    <div class="demo-section">
      <h2>Profile Card</h2>
      <div class="card profile-card">
        <ArtDecoSkeleton
          variant="circle"
          :width="'var(--artdeco-spacing-16)'"
          :height="'var(--artdeco-spacing-16)'"
        />
        <div class="profile-info">
          <div class="profile-name-skeleton">
            <ArtDecoSkeleton
              variant="text"
              :width="'calc(var(--artdeco-spacing-24) + var(--artdeco-spacing-6))'"
              :height="'var(--artdeco-spacing-6)'"
            />
          </div>
          <ArtDecoSkeleton
            variant="text"
            :width="'calc(var(--artdeco-spacing-32) + var(--artdeco-spacing-8) + var(--artdeco-spacing-4) + var(--artdeco-spacing-2))'"
          />
        </div>
      </div>
    </div>

    <div class="demo-section">
      <h2>Chart Placeholder</h2>
      <div class="card">
        <div class="chart-header">
          <ArtDecoSkeleton
            variant="text"
            :width="'calc(var(--artdeco-spacing-32) + var(--artdeco-spacing-16) + var(--artdeco-spacing-8))'"
            :height="'calc(var(--artdeco-spacing-6) - var(--artdeco-spacing-px) * 2)'"
          />
          <div class="actions">
            <ArtDecoSkeleton variant="button" :width="'calc(var(--artdeco-spacing-16) + var(--artdeco-spacing-4))'" />
            <ArtDecoSkeleton variant="button" :width="'calc(var(--artdeco-spacing-16) + var(--artdeco-spacing-4))'" />
          </div>
        </div>
        <ArtDecoSkeleton
          variant="rect"
          width="100%"
          :height="'calc(var(--artdeco-spacing-32) * 2 + var(--artdeco-spacing-24) + var(--artdeco-spacing-4))'"
        />
      </div>
    </div>

    <div class="demo-section">
      <h2>Table Loading</h2>
      <div class="card">
        <div class="table-row" v-for="i in 5" :key="i">
          <ArtDecoSkeleton variant="text" :width="'calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-2))'" />
          <ArtDecoSkeleton variant="text" :width="'calc(var(--artdeco-spacing-24) + var(--artdeco-spacing-6))'" />
          <ArtDecoSkeleton variant="text" :width="'calc(var(--artdeco-spacing-16) + var(--artdeco-spacing-4))'" />
          <ArtDecoSkeleton variant="text" :width="'calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-3))'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.skeleton-demo {
  padding: var(--artdeco-spacing-8);
  color: var(--artdeco-fg-primary);
}

.demo-section {
  margin-bottom: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-2));
  
  h2 {
    margin-bottom: var(--artdeco-spacing-4);
    font-size: calc(var(--artdeco-font-size-base) + var(--artdeco-spacing-1) - var(--artdeco-spacing-px));
    color: var(--artdeco-gold-primary);
  }
}

.card {
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-6);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-5);
}

.profile-name-skeleton {
  margin-bottom: var(--artdeco-spacing-2);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--artdeco-spacing-5);
  
  .actions {
    display: flex;
    gap: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);
  }
}

.table-row {
  display: flex;
  justify-content: space-between;
  padding: var(--artdeco-spacing-3) 0;
  border-bottom: 1px solid var(--artdeco-border-subtle);
  
  &:last-child {
    border-bottom: none;
  }
}
</style>
