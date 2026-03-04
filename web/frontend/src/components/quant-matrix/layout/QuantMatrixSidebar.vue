<template>
  <aside class="qm-sidebar" :class="{ 'qm-sidebar--collapsed': collapsed }" aria-label="Quant Matrix navigation">
    <div class="qm-sidebar__brand">
      <RouterLink to="/qm/dealing-room" class="qm-sidebar__brand-link">
        <span class="qm-sidebar__brand-main">{{ collapsed ? 'QM' : 'QUANT MATRIX' }}</span>
        <span v-if="!collapsed" class="qm-sidebar__brand-sub">PRO</span>
      </RouterLink>
    </div>

    <nav class="qm-sidebar__nav">
      <section v-for="domain in menus" :key="domain.businessKey" class="qm-sidebar__domain">
        <button
          type="button"
          class="qm-sidebar__domain-btn"
          :class="{ 'is-active': isDomainActive(domain.path) }"
          :aria-expanded="isExpanded(domain.path)"
          @click="toggleDomain(domain.path)"
        >
          <span class="qm-sidebar__domain-label">{{ domain.label }}</span>
          <span class="qm-sidebar__domain-arrow">{{ isExpanded(domain.path) ? '−' : '+' }}</span>
        </button>

        <ul v-if="isExpanded(domain.path) && !collapsed" class="qm-sidebar__children">
          <li v-for="item in domain.children" :key="item.businessKey">
            <RouterLink :to="item.path" class="qm-sidebar__child" active-class="is-active">
              <span>{{ item.label }}</span>
              <span v-if="item.badge" class="qm-sidebar__badge">{{ item.badge }}</span>
            </RouterLink>
          </li>
        </ul>
      </section>
    </nav>

    <div class="qm-sidebar__footer">
      <button
        type="button"
        class="qm-sidebar__collapse"
        @click="emit('toggle-collapse')"
        :aria-pressed="collapsed"
      >
        {{ collapsed ? '展开' : '折叠' }}
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import type { QuantMatrixMenuItem } from '@/layouts/QuantMatrixMenuConfig'

interface Props {
  collapsed: boolean
  expandedDomains: Record<string, boolean>
  menus: QuantMatrixMenuItem[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'toggle-collapse'): void
  (e: 'toggle-domain', path: string): void
}>()

const route = useRoute()

const isDomainActive = (path: string): boolean => route.path.startsWith(path)
const isExpanded = (path: string): boolean => props.expandedDomains[path] ?? false

const toggleDomain = (path: string): void => {
  emit('toggle-domain', path)
}
</script>

<style scoped lang="scss">
@import '@/styles/quant-matrix/layout/quant-matrix-sidebar.scss';
</style>
