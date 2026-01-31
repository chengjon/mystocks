<template>
  <div class="tree-menu">
    <!-- Search Input -->
    <div class="search-container">
      <ArtDecoIcon name="Search" size="sm" class="search-icon" />
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        placeholder="搜索菜单..."
        @input="handleSearch"
        @keyup.esc="clearSearch"
      />
      <button
        v-if="searchQuery"
        class="clear-search-btn"
        @click="clearSearch"
      >
        <ArtDecoIcon name="X" size="xs" />
      </button>
    </div>

    <div
      v-for="domain in filteredMenuDomains"
      :key="domain.key || domain.path"
      class="menu-domain"
    >
      <div
        class="domain-header"
        @click="handleDomainClick(domain)"
        :class="{
          expanded: expandedDomains[String(domain.key || domain.path)],
          active: !domain.children?.length && isActive(domain.path)
        }"
      >
        <span class="domain-icon">
          <ArtDecoIcon :name="domain.icon" size="sm" />
        </span>
        <span class="domain-label">{{ domain.label }}</span>
        <span v-if="domain.children?.length" class="toggle-icon">
          <ArtDecoIcon :name="expandedDomains[domain.key || domain.path] ? 'ChevronDown' : 'ChevronRight'" size="xs" />
        </span>
      </div>

      <transition name="slide">
        <div v-if="expandedDomains[String(domain.key || domain.path)]" class="domain-items">
          <div
            v-for="item in filteredMenuItems(domain)"
            :key="item.path"
            class="menu-item"
            :class="{
              active: isActive(item.path),
              highlighted: isHighlighted(item),
              selected: isSelected(domain, item)
            }"
            @click="navigateTo(item.path)"
          >
            <span class="item-icon">
              <ArtDecoIcon :name="item.icon" size="xs" />
            </span>
            <span class="item-label">{{ item.label }}</span>
            <span v-if="item.badge" class="item-badge">{{ item.badge }}</span>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import { ARTDECO_MENU_ENHANCED, type MenuItem } from '@/layouts/MenuConfig.enhanced'

const route = useRoute()
const router = useRouter()

// Menu domains
const menuDomains = computed(() => ARTDECO_MENU_ENHANCED)

// Search query
const searchQuery = ref<string>('')

// Expanded state for each domain
const expandedDomains = ref<Record<string, boolean>>({})

// Keyboard navigation
const selectedDomainIndex = ref<number>(0)
const selectedItemIndex = ref<number>(-1)
const flatMenuItems = computed(() => {
  const items: { item: MenuItem; domainIndex: number; itemIndex: number; path: string }[] = []
  filteredMenuDomains.value.forEach((domain, dIndex) => {
    const filteredChildren = filteredMenuItems(domain)
    filteredChildren.forEach((child, cIndex) => {
      items.push({
        item: child,
        domainIndex: dIndex,
        itemIndex: cIndex,
        path: child.path
      })
    })
  })
  return items
})

// Filtered menu domains based on search query
const filteredMenuDomains = computed(() => {
  if (!searchQuery.value.trim()) {
    return menuDomains.value
  }

  const query = searchQuery.value.toLowerCase().trim()

  // Flatten all menu items for searching
  const allMenuItems: { item: MenuItem; domain: MenuItem; domainKey: string }[] = []

  ARTDECO_MENU_ENHANCED.forEach(domain => {
    // Check if domain label matches
    if (domain.label.toLowerCase().includes(query)) {
      allMenuItems.push({
        item: domain,
        domain,
        domainKey: String(domain.key || domain.path)
      })
    }

    // Check if any children match
    if (domain.children) {
      domain.children.forEach(child => {
        if (child.label.toLowerCase().includes(query)) {
          allMenuItems.push({
            item: child,
            domain,
            domainKey: String(domain.key || domain.path)
          })
        }
      })
    }
  })

  // If no matches, return empty array
  if (allMenuItems.length === 0) {
    return []
  }

  // Group matched items by domain
  const matchedDomainKeys = new Set(allMenuItems.map(m => m.domainKey))
  return ARTDECO_MENU_ENHANCED.filter(domain => {
    const key = String(domain.key || domain.path)
    return matchedDomainKeys.has(key)
  })
})

// Initialize expanded state - expand current domain
const initializeExpandedState = () => {
  const currentPath = route.path

  ARTDECO_MENU_ENHANCED.forEach(domain => {
    // Check if current path belongs to this domain
    const isInDomain = domain.children?.some(child => currentPath.startsWith(child.path))
    const key = String(domain.key || domain.path)
    expandedDomains.value[key] = isInDomain || false
  })
}

// Handle domain click (navigate if leaf, toggle if branch)
const handleDomainClick = (domain: MenuItem) => {
  if (domain.children?.length) {
    const key = String(domain.key || domain.path)
    expandedDomains.value[key] = !expandedDomains.value[key]
  } else {
    navigateTo(domain.path)
  }
}

// Toggle domain expansion (kept for internal use if needed)
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

// Handle search input
const handleSearch = () => {
  // When searching, expand all domains that have matching children
  if (searchQuery.value.trim()) {
    ARTDECO_MENU_ENHANCED.forEach(domain => {
      const key = String(domain.key || domain.path)
      expandedDomains.value[key] = true
    })
  }
}

// Clear search
const clearSearch = () => {
  searchQuery.value = ''
  initializeExpandedState()
}

// Filter menu items within a domain based on search query
const filteredMenuItems = (domain: MenuItem): MenuItem[] => {
  if (!searchQuery.value.trim()) {
    return domain.children || []
  }

  const query = searchQuery.value.toLowerCase().trim()
  return (domain.children || []).filter(item =>
    item.label.toLowerCase().includes(query)
  )
}

// Check if menu item is currently selected via keyboard
const isSelected = (domain: MenuItem, item: MenuItem): boolean => {
  const domainIdx = filteredMenuDomains.value.findIndex(d =>
    (d.key || d.path) === (domain.key || domain.path)
  )
  if (domainIdx === selectedDomainIndex.value) {
    const children = filteredMenuItems(domain)
    const itemIdx = children.findIndex(child => child.path === item.path)
    return itemIdx === selectedItemIndex.value
  }
  return false
}

// Check if menu item should be highlighted (matches search query)
const isHighlighted = (item: MenuItem): boolean => {
  if (!searchQuery.value.trim()) {
    return false
  }
  const query = searchQuery.value.toLowerCase().trim()
  return item.label.toLowerCase().includes(query)
}

// Keyboard navigation handlers
const handleKeydown = (event: KeyboardEvent) => {
  const items = flatMenuItems.value

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (selectedItemIndex.value < items.length - 1) {
        selectedItemIndex.value++
        const selected = items[selectedItemIndex.value]
        selectedDomainIndex.value = selected.domainIndex
      }
      break

    case 'ArrowUp':
      event.preventDefault()
      if (selectedItemIndex.value > 0) {
        selectedItemIndex.value--
        const selected = items[selectedItemIndex.value]
        selectedDomainIndex.value = selected.domainIndex
      }
      break

    case 'ArrowRight':
      event.preventDefault()
      const currentDomain = filteredMenuDomains.value[selectedDomainIndex.value]
      if (currentDomain && currentDomain.children) {
        const key = String(currentDomain.key || currentDomain.path)
        expandedDomains.value[key] = true
      }
      break

    case 'ArrowLeft':
      event.preventDefault()
      const domainToCollapse = filteredMenuDomains.value[selectedDomainIndex.value]
      if (domainToCollapse) {
        const key = String(domainToCollapse.key || domainToCollapse.path)
        if (expandedDomains.value[key]) {
          expandedDomains.value[key] = false
        }
      }
      break

    case 'Enter':
      event.preventDefault()
      if (selectedItemIndex.value >= 0 && selectedItemIndex.value < items.length) {
        navigateTo(items[selectedItemIndex.value].path)
      }
      break
  }
}

// Initialize on mount
onMounted(() => {
  initializeExpandedState()
  window.addEventListener('keydown', handleKeydown)
})

// Cleanup on unmount
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.tree-menu {
  padding: var(--artdeco-spacing-4);
}

.search-container {
  display: flex;
  align-items: center;
  padding: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-primary);
  border-radius: var(--artdeco-radius-md);
  transition: all 0.2s ease;

  &:focus-within {
    border-color: var(--artdeco-border-active);
    box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
  }
}

.search-icon {
  color: var(--artdeco-text-tertiary);
  margin-right: var(--artdeco-spacing-3);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: var(--artdeco-font-size-sm);
  color: var(--artdeco-text-primary);
  outline: none;
  padding: 0;

  &::placeholder {
    color: var(--artdeco-text-tertiary);
  }
}

.clear-search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--artdeco-spacing-1);
  background: transparent;
  border: none;
  color: var(--artdeco-text-tertiary);
  cursor: pointer;
  border-radius: var(--artdeco-radius-sm);
  transition: all 0.2s ease;

  &:hover {
    background: var(--artdeco-bg-surface-hover);
    color: var(--artdeco-text-primary);
  }
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

  &.active {
    background: var(--artdeco-bg-active);
    color: var(--artdeco-text-on-active);
    border-color: var(--artdeco-border-active);
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

  &.highlighted {
    background: var(--artdeco-bg-surface-hover);
    font-weight: 600;
  }

  &.selected {
    background: var(--artdeco-bg-primary-light);
    border-color: var(--artdeco-border-active);
    color: var(--artdeco-text-primary);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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