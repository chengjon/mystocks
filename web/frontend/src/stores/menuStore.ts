import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'artdeco-menu-expanded'

export const useMenuStore = defineStore('artdeco-menu', () => {
  // State
  const expandedKeys = ref<string[]>([])
  const isSidebarCollapsed = ref(false)
  const searchQuery = ref('')

  // Initialize from storage
  const init = () => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        expandedKeys.value = JSON.parse(stored)
      } catch (e) {
        console.error('Failed to parse menu state', e)
      }
    }
  }

  // Actions
  const toggleExpand = (key: string) => {
    if (expandedKeys.value.includes(key)) {
      expandedKeys.value = expandedKeys.value.filter(k => k !== key)
    } else {
      expandedKeys.value.push(key)
    }
  }

  const setExpanded = (key: string, expanded: boolean) => {
    if (expanded) {
      if (!expandedKeys.value.includes(key)) {
        expandedKeys.value.push(key)
      }
    } else {
      expandedKeys.value = expandedKeys.value.filter(k => k !== key)
    }
  }

  const expandAll = (keys: string[]) => {
    expandedKeys.value = [...new Set([...expandedKeys.value, ...keys])]
  }

  const collapseAll = () => {
    expandedKeys.value = []
  }

  const toggleSidebar = () => {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
  }

  // Watch for changes and persist
  watch(expandedKeys, (newVal) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newVal))
  }, { deep: true })

  // Auto-init
  init()

  return {
    expandedKeys,
    isSidebarCollapsed,
    searchQuery,
    toggleExpand,
    setExpanded,
    expandAll,
    collapseAll,
    toggleSidebar
  }
})
