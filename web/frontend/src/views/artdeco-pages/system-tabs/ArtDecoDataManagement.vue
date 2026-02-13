<template>
  <div class="data-management">
    <ArtDecoCard class="placeholder-card" variant="bordered">
      <template #header>
        <h2>数据管理</h2>
      </template>
      <p>数据管理模块正在重构中，基础页面已恢复可访问。</p>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoCard } from "@/components/artdeco"
</script>

<style scoped>
.data-management {
  min-height: 320px;
  padding: 16px;
}

.placeholder-card {
  max-width: 960px;
  margin: 0 auto;
}
</style>
