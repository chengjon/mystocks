<template>
  <div class="app-container">
    <!-- FORCE RENDER: 直接渲染指挥中心，绕过路由 -->
    <ArtDecoDashboard />
  </div>
</template>

<script setup>
import ArtDecoDashboard from '@/views/artdeco-pages/ArtDecoDashboard.vue'
console.log('🔥 FORCE RENDER: ArtDecoDashboard')
</script>

<style>
.app-container { min-height: 100vh; background: #0a0a0f; color: gold; }
</style>
