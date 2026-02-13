<template>
  <div class="strategy-management">
    <ArtDecoCard class="placeholder-card" variant="bordered">
      <template #header>
        <h2>策略管理</h2>
      </template>
      <p>策略管理模块正在重构中，基础页面已恢复可访问。</p>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoCard } from "@/components/artdeco"
</script>

<style scoped>
.strategy-management {
  min-height: 320px;
  padding: 16px;
}

.placeholder-card {
  max-width: 960px;
  margin: 0 auto;
}
</style>
