<template>
  <div class="app-container">
    <!-- RESTORED: 使用路由视图，恢复 ArtDeco 3.1 布局系统 -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
// 已恢复路由控制
</script>

<style lang="scss">
@import '@/styles/artdeco-tokens.scss';

.app-container {
  min-height: 100vh;
  background: var(--artdeco-bg-global);
  color: var(--artdeco-fg-primary);
}
</style>
