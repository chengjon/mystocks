<template>
  <ArtDecoCard title="个股风险分析" hoverable>
    <div class="stock-panel">
      <p>选择持仓股票查看详细风险分析。</p>
      <ArtDecoButton variant="solid" size="sm" @click="$emit('open-stock-modal')">选择股票</ArtDecoButton>
    </div>
  </ArtDecoCard>
</template>

<script setup lang="ts">
import { ArtDecoButton, ArtDecoCard } from '@/components/artdeco'

defineEmits<{
  'open-stock-modal': []
}>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.stock-panel {
  display: grid;
  gap: var(--artdeco-spacing-3);

  p {
    margin: 0;
    color: var(--artdeco-fg-muted);
  }
}
</style>
