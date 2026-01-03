<template>
  <div class="artdeco-layout">
    <ArtDecoSidebar />
    <main class="artdeco-main">
      <ArtDecoTopBar />
      <div class="artdeco-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import ArtDecoSidebar from '@/components/artdeco/ArtDecoSidebar.vue'
import ArtDecoTopBar from '@/components/artdeco/ArtDecoTopBar.vue'
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-layout {
  display: flex;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

.artdeco-main {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.artdeco-content {
  flex: 1;
  padding: var(--artdeco-space-xl);
  overflow-y: auto;
}

@media (max-width: 768px) {
  .artdeco-main {
    margin-left: 0;
  }
}
</style>
