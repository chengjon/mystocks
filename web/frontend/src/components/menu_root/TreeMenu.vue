<template>
  <div class="tree-menu">
    <div
      v-for="domain in menuDomains"
      :key="domain.key || domain.path"
      class="menu-domain"
    >
      <div
        class="domain-header"
        @click="toggleDomain(domain.key || domain.path)"
        :class="{ expanded: expandedDomains[domain.key || domain.path] }"
      >
        <span class="domain-icon">{{ domain.icon || '📁' }}</span>
        <span class="domain-label">{{ domain.label }}</span>
        <span class="toggle-icon">
          {{ expandedDomains[domain.key || domain.path] ? '▼' : '▶' }}
        </span>
      </div>

      <transition name="slide">
        <div v-if="expandedDomains[domain.key || domain.path]" class="domain-items">
          <div
            v-for="item in domain.children || []"
            :key="item.path"
            class="menu-item"
            :class="{ active: isActive(item.path) }"
            @click="navigateTo(item.path)"
          >
            <span class="item-icon">{{ item.icon || '📄' }}</span>
            <span class="item-label">{{ item.label }}</span>
            <span v-if="item.badge" class="item-badge">{{ item.badge }}</span>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ARTDECO_MENU_ENHANCED, type MenuItem } from '@/layouts/MenuConfig.enhanced'

const route = useRoute()
const router = useRouter()

// Menu domains
const menuDomains = computed(() => ARTDECO_MENU_ENHANCED)

// Expanded state for each domain
const expandedDomains = ref<Record<string, boolean>>({})

// Initialize expanded state - expand current domain
const initializeExpandedState = () => {
  const currentPath = route.path

  ARTDECO_MENU_ENHANCED.forEach(domain => {
    // Check if current path belongs to this domain
    const isInDomain = domain.children?.some(child => currentPath.startsWith(child.path))
    expandedDomains.value[domain.path] = isInDomain || false
  })
}

// Toggle domain expansion
const toggleDomain = (domainKey: string | number) => {
  const key = String(domainKey)
  expandedDomains.value[key] = !expandedDomains.value[key]
}

// Check if menu item is active
const isActive = (path: string): boolean => {
  return route.path === path || route.path.startsWith(path + '/')
}

// Navigate to menu item
const navigateTo = (path: string) => {
  if (path !== route.path) {
    router.push(path)
  }
}

// Watch route changes to update active state
watch(() => route.path, () => {
  initializeExpandedState()
})

// Initialize on mount
onMounted(() => {
  initializeExpandedState()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.tree-menu {
  padding: var(--artdeco-spacing-4);
}

.menu-domain {
  margin-bottom: var(--artdeco-spacing-2);

  &:last-child {
    margin-bottom: 0;
  }
}

.domain-header {
  display: flex;
  align-items: center;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-primary);
  border-radius: var(--artdeco-radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
  color: var(--artdeco-text-primary);

  &:hover {
    background: var(--artdeco-bg-surface-hover);
    border-color: var(--artdeco-border-hover);
  }

  &.expanded {
    background: var(--artdeco-bg-primary);
    border-color: var(--artdeco-border-active);
    color: var(--artdeco-text-on-primary);
  }
}

.domain-icon {
  margin-right: var(--artdeco-spacing-3);
  font-size: var(--artdeco-font-size-lg);
}

.domain-label {
  flex: 1;
  font-size: var(--artdeco-font-size-base);
}

.toggle-icon {
  margin-left: var(--artdeco-spacing-3);
  font-size: var(--artdeco-font-size-sm);
  transition: transform 0.2s ease;
}

.domain-items {
  margin-top: var(--artdeco-spacing-2);
  margin-left: var(--artdeco-spacing-6);
  border-left: 2px solid var(--artdeco-border-secondary);
  padding-left: var(--artdeco-spacing-4);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-1);
  border-radius: var(--artdeco-radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--artdeco-text-secondary);

  &:hover {
    background: var(--artdeco-bg-surface-hover);
    color: var(--artdeco-text-primary);
  }

  &.active {
    background: var(--artdeco-bg-active);
    color: var(--artdeco-text-on-active);
    border: 1px solid var(--artdeco-border-active);
  }

  &:last-child {
    margin-bottom: 0;
  }
}

.item-icon {
  margin-right: var(--artdeco-spacing-3);
  font-size: var(--artdeco-font-size-base);
  opacity: 0.8;
}

.item-label {
  flex: 1;
  font-size: var(--artdeco-font-size-sm);
}

.item-badge {
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
  background: var(--artdeco-bg-accent);
  color: var(--artdeco-text-on-accent);
  border-radius: var(--artdeco-radius-full);
  font-size: var(--artdeco-font-size-xs);
  font-weight: 600;
}

// Slide transition for menu items
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.slide-enter-to,
.slide-leave-from {
  max-height: 500px;
  opacity: 1;
}
</style>