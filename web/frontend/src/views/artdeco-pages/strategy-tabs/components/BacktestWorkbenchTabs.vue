<template>
  <section class="workbench-tabs artdeco-card">
    <div v-if="eyebrow || title || description || metaItems.length > 0" class="tabs-rail">
      <div class="tabs-rail-copy">
        <span v-if="eyebrow" class="tabs-rail-eyebrow">{{ eyebrow }}</span>
        <h3 v-if="title" class="tabs-rail-title">{{ title }}</h3>
        <p v-if="description" class="tabs-rail-description">{{ description }}</p>
      </div>
      <div v-if="metaItems.length > 0" class="tabs-rail-meta">
        <span v-for="item in metaItems" :key="item" class="tabs-rail-meta-item">{{ item }}</span>
      </div>
    </div>

    <div class="tabs-header">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="tab-btn"
        :class="{ active: tab.key === activeTab }"
        @click="$emit('update:activeTab', tab.key)"
      >
        <ArtDecoIcon v-if="tab.icon" :name="tab.icon" size="sm" />
        {{ tab.label }}
      </button>
    </div>
    <div class="tabs-content">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'

withDefaults(defineProps<{
  activeTab: string
  tabs: Array<{ key: string; label: string; icon?: string }>
  eyebrow?: string
  title?: string
  description?: string
  metaItems?: string[]
}>(), {
  eyebrow: '',
  title: '',
  description: '',
  metaItems: () => []
})

defineEmits<{
  'update:activeTab': [value: string]
}>()
</script>

<style scoped lang="scss">
@use './styles/BacktestWorkbenchTabs';
</style>
