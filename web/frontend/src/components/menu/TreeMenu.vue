<template>
  <nav 
    class="tree-menu" 
    aria-label="Main Navigation"
    role="navigation"
  >
    <!-- Search Input -->
    <div class="search-container" role="search">
      <ArtDecoIcon name="Search" size="sm" class="search-icon" aria-hidden="true" />
      <input
        ref="searchInputRef"
        v-model="menuStore.searchQuery"
        type="search"
        class="search-input"
        placeholder="搜索菜单 (Ctrl+K)"
        aria-label="Search menu"
        @input="handleSearch"
        @keydown="handleSearchKeydown"
      />
      <button
        v-if="menuStore.searchQuery"
        class="clear-search-btn"
        @click="clearSearch"
        aria-label="Clear search"
      >
        <ArtDecoIcon name="X" size="xs" aria-hidden="true" />
      </button>
    </div>

    <!-- Menu Tree -->
    <ul class="menu-root" role="tree">
      <li 
        v-for="(domain, dIndex) in filteredMenuDomains"
        :key="domain.key || domain.path"
        class="menu-domain"
        role="presentation"
      >
        <!-- Domain Header (Collapsible) -->
        <button
          class="domain-header"
          :class="{
            expanded: menuStore.expandedKeys.includes(String(domain.key || domain.path)),
            active: !domain.children?.length && isActive(domain.path),
            focused: isDomainFocused(dIndex)
          }"
          @click="handleDomainClick(domain)"
          :aria-expanded="menuStore.expandedKeys.includes(String(domain.key || domain.path))"
          :aria-selected="!domain.children?.length && isActive(domain.path)"
          role="treeitem"
          tabindex="-1"
        >
          <span class="domain-icon" aria-hidden="true">
            <ArtDecoIcon :name="domain.icon" size="sm" />
          </span>
          <span class="domain-label">{{ domain.label }}</span>
          <span v-if="domain.children?.length" class="toggle-icon" aria-hidden="true">
            <ArtDecoIcon :name="menuStore.expandedKeys.includes(String(domain.key || domain.path)) ? 'ChevronDown' : 'ChevronRight'" size="xs" />
          </span>
        </button>

        <!-- Domain Children -->
        <transition name="slide">
          <ul 
            v-if="menuStore.expandedKeys.includes(String(domain.key || domain.path))" 
            class="domain-items"
            role="group"
          >
            <li 
              v-for="(item, cIndex) in filteredMenuItems(domain)"
              :key="item.path"
              role="presentation"
            >
              <router-link
                :to="item.path"
                custom
                v-slot="{ href, navigate, isActive: isLinkActive }"
              >
                <a
                  :href="href"
                  class="menu-item"
                  :class="{
                    active: isLinkActive,
                    highlighted: isHighlighted(item),
                    selected: isItemSelected(dIndex, cIndex)
                  }"
                  @click="navigate"
                  role="treeitem"
                  :aria-selected="isLinkActive"
                  :aria-current="isLinkActive ? 'page' : undefined"
                  tabindex="-1"
                >
                  <span class="item-icon" aria-hidden="true">
                    <ArtDecoIcon :item-icon="item.icon" :name="item.icon" size="xs" />
                  </span>
                  <span class="item-label">{{ item.label }}</span>
                  <span v-if="item.badge" class="item-badge">{{ item.badge }}</span>
                </a>
              </router-link>
            </li>
          </ul>
        </transition>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMenuStore } from '@/stores/menuStore'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import { ARTDECO_MENU_ENHANCED, type MenuItem } from '@/layouts/MenuConfig.enhanced'

const route = useRoute()
const router = useRouter()
const menuStore = useMenuStore()
const searchInputRef = ref<HTMLInputElement | null>(null)

// ==========================================
// Data & State
// ==========================================
// const searchQuery = ref<string>('') // Moved to Store
// const expandedDomains = ref<Record<string, boolean>>({}) // Moved to Store

// Keyboard Navigation State
const focusState = ref({
  domainIndex: 0,
  itemIndex: -1,
  active: false
})

// ==========================================
// Filtering Logic
// ==========================================
const filteredMenuDomains = computed(() => {
  if (!menuStore.searchQuery.trim()) {
    return ARTDECO_MENU_ENHANCED
  }

  const query = menuStore.searchQuery.toLowerCase().trim()
  
  return ARTDECO_MENU_ENHANCED.filter(domain => {
    const domainMatch = domain.label.toLowerCase().includes(query)
    const childrenMatch = domain.children?.some(child => 
      child.label.toLowerCase().includes(query)
    )
    return domainMatch || childrenMatch
  })
})

const filteredMenuItems = (domain: MenuItem): MenuItem[] => {
  if (!menuStore.searchQuery.trim()) {
    return domain.children || []
  }
  const query = menuStore.searchQuery.toLowerCase().trim()
  return (domain.children || []).filter(item =>
    item.label.toLowerCase().includes(query)
  )
}

// ==========================================
// Navigation & Expansion Logic
// ==========================================
const handleDomainClick = (domain: MenuItem) => {
  if (domain.children?.length) {
    const key = String(domain.key || domain.path)
    menuStore.toggleExpand(key)
  } else {
    navigateTo(domain.path)
  }
}

const isActive = (path: string): boolean => {
  return route.path === path || route.path.startsWith(path + '/')
}

const navigateTo = (path: string) => {
  if (path !== route.path) {
    router.push(path)
  }
}

const isHighlighted = (item: MenuItem): boolean => {
  if (!menuStore.searchQuery.trim()) return false
  return item.label.toLowerCase().includes(menuStore.searchQuery.toLowerCase().trim())
}

// ==========================================
// Search Logic
// ==========================================
const handleSearch = () => {
  if (menuStore.searchQuery.trim()) {
    // Auto-expand all filtered results
    const keysToExpand: string[] = []
    filteredMenuDomains.value.forEach(domain => {
      keysToExpand.push(String(domain.key || domain.path))
    })
    menuStore.expandAll(keysToExpand)
  }
}

const clearSearch = () => {
  menuStore.searchQuery = ''
  // Reset expansion is optional, maybe keep expanded?
  // Let's just collapse non-active ones or restore from initial load logic if we had it.
  // For now, keep current state.
}

const handleSearchKeydown = (e: KeyboardEvent) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    searchInputRef.value?.blur()
    focusState.value.active = true
    focusState.value.domainIndex = 0
    focusState.value.itemIndex = -1 // Start at first domain header
  }
}

// ==========================================
// Keyboard Interaction (Virtual Cursor)
// ==========================================
const isDomainFocused = (dIndex: number) => {
  return focusState.value.active && 
         focusState.value.domainIndex === dIndex && 
         focusState.value.itemIndex === -1
}

const isItemSelected = (dIndex: number, cIndex: number) => {
  return focusState.value.active && 
         focusState.value.domainIndex === dIndex && 
         focusState.value.itemIndex === cIndex
}

const handleGlobalKeydown = (e: KeyboardEvent) => {
  // 1. Global Shortcut: Ctrl+K / Cmd+K to focus search
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    searchInputRef.value?.focus()
    return
  }

  // 2. Ignore if typing in inputs
  const target = e.target as HTMLElement
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName) || target.isContentEditable) {
    return
  }

  // 3. Navigation Logic
  const isNavKey = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Enter', ' '].includes(e.key)
  if (!isNavKey) return

  e.preventDefault()
  focusState.value.active = true

  const currentDomain = filteredMenuDomains.value[focusState.value.domainIndex]
  const currentChildren = currentDomain ? filteredMenuItems(currentDomain) : []
  const isHeaderFocus = focusState.value.itemIndex === -1

  switch (e.key) {
    case 'ArrowDown':
      if (isHeaderFocus) {
        // If on header, check if expanded and has children
        const key = String(currentDomain.key || currentDomain.path)
        if (menuStore.expandedKeys.includes(key) && currentChildren.length > 0) {
          // Go to first child
          focusState.value.itemIndex = 0
        } else {
          // Go to next domain header
          if (focusState.value.domainIndex < filteredMenuDomains.value.length - 1) {
            focusState.value.domainIndex++
          }
        }
      } else {
        // If on item
        if (focusState.value.itemIndex < currentChildren.length - 1) {
          // Next item
          focusState.value.itemIndex++
        } else {
          // Next domain header
          if (focusState.value.domainIndex < filteredMenuDomains.value.length - 1) {
            focusState.value.domainIndex++
            focusState.value.itemIndex = -1
          }
        }
      }
      break

    case 'ArrowUp':
      if (isHeaderFocus) {
        // Previous Domain
        if (focusState.value.domainIndex > 0) {
          focusState.value.domainIndex--
          // Check previous domain state to decide where to land
          const prevDomain = filteredMenuDomains.value[focusState.value.domainIndex]
          const prevKey = String(prevDomain.key || prevDomain.path)
          const prevChildren = filteredMenuItems(prevDomain)
          
          if (menuStore.expandedKeys.includes(prevKey) && prevChildren.length > 0) {
            // Land on last child of previous domain
            focusState.value.itemIndex = prevChildren.length - 1
          } else {
            // Land on header
            focusState.value.itemIndex = -1
          }
        }
      } else {
        // If on item
        if (focusState.value.itemIndex > 0) {
          focusState.value.itemIndex--
        } else {
          // Go up to parent header
          focusState.value.itemIndex = -1
        }
      }
      break

    case 'ArrowRight':
      if (isHeaderFocus) {
        // Expand domain
        const key = String(currentDomain.key || currentDomain.path)
        menuStore.setExpanded(key, true)
      }
      break

    case 'ArrowLeft':
      if (isHeaderFocus) {
        // Collapse domain
        const key = String(currentDomain.key || currentDomain.path)
        menuStore.setExpanded(key, false)
      } else {
        // Go back to parent header
        focusState.value.itemIndex = -1
      }
      break

    case 'Enter':
    case ' ':
      if (isHeaderFocus) {
        handleDomainClick(currentDomain)
      } else {
        const item = currentChildren[focusState.value.itemIndex]
        if (item) navigateTo(item.path)
      }
      break
  }
}

// Lifecycle
onMounted(() => {
  // Initialize expand state based on current route is handled by store logic + current route matching
  // But store only restores from localstorage.
  // We might want to ensure current route is expanded.
  const currentPath = route.path
  ARTDECO_MENU_ENHANCED.forEach(domain => {
    const isInDomain = domain.children?.some(child => currentPath.startsWith(child.path))
    if (isInDomain) {
      menuStore.setExpanded(String(domain.key || domain.path), true)
    }
  })
  
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.tree-menu {
  padding: var(--artdeco-spacing-4);
  font-family: var(--artdeco-font-sans);
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

.menu-root {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-domain {
  margin-bottom: var(--artdeco-spacing-2);
  
  &:last-child {
    margin-bottom: 0;
  }
}

.domain-header {
  width: 100%;
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
  text-align: left;
  outline: none;

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
  
  &.focused {
    box-shadow: 0 0 0 2px var(--artdeco-gold-primary);
    border-color: var(--artdeco-gold-primary);
  }
}

.domain-icon {
  margin-right: var(--artdeco-spacing-3);
  font-size: var(--artdeco-font-size-lg);
  display: flex;
  align-items: center;
}

.domain-label {
  flex: 1;
  font-size: var(--artdeco-font-size-base);
}

.toggle-icon {
  margin-left: var(--artdeco-spacing-3);
  font-size: var(--artdeco-font-size-sm);
  transition: transform 0.2s ease;
  display: flex;
  align-items: center;
}

.domain-items {
  list-style: none;
  padding: 0;
  margin: 0;
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
  text-decoration: none;
  outline: none;

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
    outline: 1px solid var(--artdeco-gold-primary);
  }

  &:last-child {
    margin-bottom: 0;
  }
}

.item-icon {
  margin-right: var(--artdeco-spacing-3);
  font-size: var(--artdeco-font-size-base);
  opacity: 0.8;
  display: flex;
  align-items: center;
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