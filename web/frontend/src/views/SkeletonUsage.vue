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
        <ArtDecoSkeleton variant="circle" width="64px" height="64px" />
        <div class="profile-info">
          <ArtDecoSkeleton variant="text" width="120px" style="height: 24px; margin-bottom: 8px;" />
          <ArtDecoSkeleton variant="text" width="180px" />
        </div>
      </div>
    </div>

    <div class="demo-section">
      <h2>Chart Placeholder</h2>
      <div class="card">
        <div class="chart-header">
          <ArtDecoSkeleton variant="text" width="200px" style="height: 28px;" />
          <div class="actions">
            <ArtDecoSkeleton variant="button" width="80px" />
            <ArtDecoSkeleton variant="button" width="80px" />
          </div>
        </div>
        <ArtDecoSkeleton variant="rect" width="100%" height="300px" />
      </div>
    </div>

    <div class="demo-section">
      <h2>Table Loading</h2>
      <div class="card">
        <div class="table-row" v-for="i in 5" :key="i">
          <ArtDecoSkeleton variant="text" width="40px" />
          <ArtDecoSkeleton variant="text" width="120px" />
          <ArtDecoSkeleton variant="text" width="80px" />
          <ArtDecoSkeleton variant="text" width="60px" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ArtDecoSkeleton from '@/components/artdeco/core/ArtDecoSkeleton.vue'
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.skeleton-demo {
  padding: 32px;
  color: var(--artdeco-fg-primary);
}

.demo-section {
  margin-bottom: 40px;
  
  h2 {
    margin-bottom: 16px;
    font-size: 18px;
    color: var(--artdeco-gold-primary);
  }
}

.card {
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-default);
  border-radius: 8px;
  padding: 24px;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  
  .actions {
    display: flex;
    gap: 10px;
  }
}

.table-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--artdeco-border-subtle);
  
  &:last-child {
    border-bottom: none;
  }
}
</style>
