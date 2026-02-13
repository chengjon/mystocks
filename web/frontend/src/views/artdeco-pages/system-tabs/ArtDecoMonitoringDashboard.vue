<template>
  <div class="monitoring-dashboard">
    <ArtDecoCard class="placeholder-card" variant="bordered">
      <template #header>
        <h2>监控面板</h2>
      </template>
      <p>监控面板模块正在重构中，基础页面已恢复可访问。</p>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoCard } from "@/components/artdeco"
</script>

<style scoped>
.monitoring-dashboard {
  min-height: 320px;
  padding: 16px;
}

.placeholder-card {
  max-width: 960px;
  margin: 0 auto;
}
</style>
