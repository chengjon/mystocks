<template>
  <div class="qm-scaffold">
    <QuantMatrixShellCard :title="props.title">
      <p class="qm-scaffold__text">{{ props.description }}</p>
      <p class="qm-scaffold__hint">该页面已恢复为可渲染路由骨架，后续按 V3 策略补齐业务能力。</p>
    </QuantMatrixShellCard>
  </div>
</template>

<script setup lang="ts">
import QuantMatrixShellCard from '@/components/quant-matrix/base/QuantMatrixShellCard.vue'

interface Props {
  title: string
  description: string
}

const props = defineProps<Props>()
</script>

<style scoped lang="scss">
@import '@/styles/quant-matrix/views/quant-matrix-scaffold.scss';
</style>
