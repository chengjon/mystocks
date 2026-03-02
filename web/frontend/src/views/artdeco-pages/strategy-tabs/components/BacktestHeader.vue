<template>
  <header class="backtest-header artdeco-card">
    <div class="header-main">
      <p class="eyebrow">Strategy Lab</p>
      <h2 class="section-title">策略回测管理中心</h2>
      <p class="subtitle">{{ subtitle }}</p>
    </div>

    <div class="header-meta">
      <div class="status-block">
        <span class="label">系统状态</span>
        <span class="value">{{ statusText }}</span>
      </div>
      <div class="status-block">
        <span class="label">最后更新</span>
        <span class="value">{{ lastUpdated }}</span>
      </div>
      <div class="header-actions">
        <ArtDecoButton variant="outline" size="sm" @click="$emit('reset')">重置参数</ArtDecoButton>
        <ArtDecoButton variant="solid" size="sm" @click="$emit('run')">启动回测</ArtDecoButton>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ArtDecoButton } from '@/components/artdeco'

defineProps<{
  subtitle: string
  statusText: string
  lastUpdated: string
}>()

defineEmits<{
  reset: []
  run: []
}>()
</script>

<style scoped lang="scss">
@import './styles/BacktestHeader';
</style>
