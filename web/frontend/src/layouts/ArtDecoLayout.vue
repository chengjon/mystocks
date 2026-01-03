<template>
  <div class="artdeco-layout">
    <!-- Background pattern overlay -->
    <div class="artdeco-bg-pattern"></div>

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
  /* Add subtle noise texture */
  background-color: var(--artdeco-bg-global);
}

.artdeco-main {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
  z-index: 2; /* Above background pattern */
}

.artdeco-content {
  flex: 1;
  padding: var(--artdeco-space-section); /* 128px - Generous section padding */
  padding-top: var(--artdeco-space-2xl); /* 64px - Slightly less top padding */
  padding-bottom: var(--artdeco-space-section); /* 128px - Generous bottom padding */
  overflow-y: auto;
  /* Smooth scrolling */
  scroll-behavior: smooth;
}

/* Responsive Design */
@media (max-width: 768px) {
  .artdeco-main {
    margin-left: 0;
  }

  .artdeco-content {
    padding: var(--artdeco-space-xl); /* 48px on mobile */
    padding-top: var(--artdeco-space-lg); /* 32px */
    padding-bottom: var(--artdeco-space-xl);
  }
}
</style>
