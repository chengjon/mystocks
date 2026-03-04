<template>
  <header class="qm-header">
    <div>
      <h1 class="qm-header__title">{{ props.title }}</h1>
      <p class="qm-header__subtitle">{{ props.subtitle }}</p>
    </div>
    <div class="qm-header__meta" aria-live="polite">
      <span class="qm-header__pill">LIVE</span>
      <span class="qm-header__time">{{ nowText }}</span>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

interface Props {
  title: string
  subtitle: string
}

const props = defineProps<Props>()

const nowText = ref('')
let timer: ReturnType<typeof setInterval> | null = null

const refreshNowText = (): void => {
  nowText.value = new Date().toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  refreshNowText()
  timer = setInterval(refreshNowText, 1000)
})

onUnmounted(() => {
  if (timer !== null) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/quant-matrix/layout/quant-matrix-header.scss';
</style>
