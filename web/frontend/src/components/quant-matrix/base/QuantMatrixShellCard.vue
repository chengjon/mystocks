<template>
  <section class="qm-shell-card" :aria-label="title">
    <header v-if="title" class="qm-shell-card__header">
      <h3 class="qm-shell-card__title">{{ title }}</h3>
      <slot name="extra" />
    </header>
    <div class="qm-shell-card__body">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
}>()
</script>

<style scoped lang="scss">
@import '@/styles/quant-matrix/components/quant-matrix-shell-card.scss';
</style>
