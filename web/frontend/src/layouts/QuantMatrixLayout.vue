<template>
  <div class="qm-layout">
    <QuantMatrixSidebar
      :collapsed="sidebarCollapsed"
      :expanded-domains="expandedDomains"
      :menus="QUANT_MATRIX_MENU_ITEMS"
      @toggle-collapse="toggleSidebar"
      @toggle-domain="toggleDomain"
    />

    <main class="qm-layout__main" :class="{ 'qm-layout__main--collapsed': sidebarCollapsed }">
      <QuantMatrixHeader :title="pageTitle" :subtitle="pageSubtitle" />
      <section class="qm-layout__content">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import QuantMatrixSidebar from '@/components/quant-matrix/layout/QuantMatrixSidebar.vue'
import QuantMatrixHeader from '@/components/quant-matrix/layout/QuantMatrixHeader.vue'
import { QUANT_MATRIX_MENU_ITEMS } from '@/layouts/QuantMatrixMenuConfig'

const route = useRoute()
const sidebarCollapsed = ref(false)
const expandedDomains = reactive<Record<string, boolean>>({})

watch(
  () => route.path,
  () => {
    QUANT_MATRIX_MENU_ITEMS.forEach((domain) => {
      if (route.path.startsWith(domain.path)) {
        expandedDomains[domain.path] = true
      }
    })
  },
  { immediate: true }
)

const toggleSidebar = (): void => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const toggleDomain = (path: string): void => {
  expandedDomains[path] = !(expandedDomains[path] ?? false)
}

const pageTitle = computed(() => (typeof route.meta.title === 'string' ? route.meta.title : 'Quant Matrix Pro'))
const pageSubtitle = computed(() => 'Dual-style execution phase · Quant Matrix Pro')
</script>

<style scoped lang="scss">
@import '@/styles/quant-matrix/layout/quant-matrix-layout.scss';
</style>
