<template>
  <section class="workbench-tabs artdeco-card">
    <div class="tabs-header">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="tab-btn"
        :class="{ active: tab.key === activeTab }"
        @click="$emit('update:activeTab', tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>
    <div class="tabs-content">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  activeTab: string
  tabs: Array<{ key: string; label: string }>
}>()

defineEmits<{
  'update:activeTab': [value: string]
}>()
</script>

<style scoped lang="scss">
@import './styles/BacktestWorkbenchTabs';
</style>
