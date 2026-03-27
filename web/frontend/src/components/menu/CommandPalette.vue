<template>
  <transition name="fade">
    <div v-if="isOpen" class="command-palette-overlay" @click.self="close">
      <div class="command-palette">
        <!-- Search Input -->
        <div class="command-header">
          <ArtDecoIcon name="Search" size="sm" class="search-icon" />
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            class="command-input"
            placeholder="Search pages, actions, or stocks..."
            @keydown="handleKeydown"
            autofocus
          />
          <div class="shortcut-hint">ESC to close</div>
        </div>

        <!-- Results List -->
        <div class="command-body">
          <div v-if="groupedResults.length === 0" class="no-results">
            <ArtDecoIcon name="Search" size="lg" class="no-results-icon" />
            <p>No results found</p>
          </div>

          <div v-else class="results-container">
            <template v-for="(group, gIndex) in groupedResults" :key="group.title">
              <div class="group-header" v-if="group.items.length > 0">
                {{ group.title }}
              </div>
              <div
                v-for="(item, iIndex) in group.items"
                :key="item.id"
                class="command-item"
                :class="{
                  active: isItemSelected(gIndex, iIndex),
                  highlighted: isHighlighted(item)
                }"
                @click="executeCommand(item)"
                @mouseenter="setSelectedIndex(gIndex, iIndex)"
              >
                <ArtDecoIcon :name="item.icon" size="sm" class="command-icon" />
                <div class="command-info">
                  <span class="command-label">{{ item.label }}</span>
                  <span class="command-sublabel" v-if="item.sublabel">{{ item.sublabel }}</span>
                </div>
                <div class="command-shortcut" v-if="item.shortcut">
                  <kbd>{{ item.shortcut }}</kbd>
                </div>
                <ArtDecoIcon name="ArrowRight" size="xs" class="arrow-icon" v-else />
              </div>
            </template>
          </div>
        </div>

        <!-- Footer -->
        <div class="command-footer">
          <div class="keyboard-shortcuts">
            <span class="shortcut-item"><kbd>↑↓</kbd> Navigate</span>
            <span class="shortcut-item"><kbd>Enter</kbd> Select</span>
            <span class="shortcut-item"><kbd>Esc</kbd> Close</span>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMenuStore } from '@/stores/menuStore'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import { ARTDECO_MENU_ENHANCED } from '@/layouts/MenuConfig'

// Types
type CommandType = 'navigation' | 'action' | 'search' | 'external'

interface MenuItem {
  label: string
  path?: string
  icon?: string
  children?: MenuItem[]
}

interface CommandItem {
  id: string
  label: string
  sublabel?: string
  type: CommandType
  icon: string
  handler: () => void
  shortcut?: string
  keywords?: string[]
}

interface CommandGroup {
  title: string
  items: CommandItem[]
}

// State
const isOpen = ref(false)
const searchQuery = ref('')
const searchInputRef = ref<HTMLInputElement | null>(null)
const selectedGroupIndex = ref(0)
const selectedItemIndex = ref(0)

const router = useRouter()
const menuStore = useMenuStore()

// Mock Stock Data (In real app, fetch from API)
const mockStocks = [
  { symbol: 'AAPL', name: 'Apple Inc.' },
  { symbol: 'MSFT', name: 'Microsoft Corp.' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.' },
  { symbol: 'TSLA', name: 'Tesla Inc.' },
  { symbol: 'NVDA', name: 'NVIDIA Corp.' },
]

// Commands Generation
const generateNavigationCommands = (): CommandItem[] => {
  const commands: CommandItem[] = []

  const traverse = (items: MenuItem[], parentLabel = '') => {
    items.forEach(item => {
      if (item.children) {
        traverse(item.children, item.label)
      } else if (item.path) {
        const itemPath = item.path
        commands.push({
          id: `nav-${itemPath}`,
          label: item.label,
          sublabel: parentLabel ? `${parentLabel} > ${item.label}` : 'Navigation',
          type: 'navigation',
          icon: item.icon || 'FileText',
          handler: () => {
            router.push(itemPath)
            close()
          },
          keywords: [item.label, parentLabel, 'page', 'nav']
        })
      }
    })
  }

  traverse(ARTDECO_MENU_ENHANCED as MenuItem[])
  return commands
}

const generateActionCommands = (): CommandItem[] => {
  return [
    {
      id: 'act-toggle-sidebar',
      label: 'Toggle Sidebar',
      sublabel: 'Layout',
      type: 'action',
      icon: 'Sidebar',
      handler: () => {
        menuStore.toggleSidebar()
        close()
      },
      keywords: ['sidebar', 'menu', 'collapse', 'expand']
    },
    {
      id: 'act-toggle-theme', // Placeholder
      label: 'Toggle Theme',
      sublabel: 'Appearance',
      type: 'action',
      icon: 'Moon', // Assuming Moon icon exists
      handler: () => {
        // Implement theme toggle logic here
        console.log('Toggle theme')
        close()
      },
      keywords: ['theme', 'dark', 'light', 'mode']
    },
    {
      id: 'act-logout',
      label: 'Log Out',
      sublabel: 'Account',
      type: 'action',
      icon: 'LogOut',
      handler: () => {
        router.push('/login')
        close()
      },
      keywords: ['logout', 'signout', 'exit']
    }
  ]
}

const generateStockCommands = (query: string): CommandItem[] => {
  if (!query || query.length < 2) return []
  
  const q = query.toLowerCase()
  return mockStocks
    .filter(s => s.symbol.toLowerCase().includes(q) || s.name.toLowerCase().includes(q))
    .slice(0, 5)
    .map(s => ({
      id: `stock-${s.symbol}`,
      label: `${s.symbol} - ${s.name}`,
      sublabel: 'Stock Quote',
      type: 'search',
      icon: 'TrendingUp',
      handler: () => {
        // Navigate to stock detail
        router.push(`/market/stock/${s.symbol}`) // Assuming route
        close()
      },
      keywords: [s.symbol, s.name, 'stock']
    }))
}

// Grouped Results
const groupedResults = computed<CommandGroup[]>(() => {
  const query = searchQuery.value.toLowerCase().trim()
  const navs = generateNavigationCommands()
  const actions = generateActionCommands()
  const stocks = generateStockCommands(query)
  
  let filteredNavs = navs
  let filteredActions = actions
  
  if (query) {
    filteredNavs = navs.filter(cmd => 
      cmd.label.toLowerCase().includes(query) || 
      cmd.keywords?.some(k => k.toLowerCase().includes(query))
    )
    filteredActions = actions.filter(cmd => 
      cmd.label.toLowerCase().includes(query) || 
      cmd.keywords?.some(k => k.toLowerCase().includes(query))
    )
  }
  
  const groups: CommandGroup[] = []
  
  if (stocks.length > 0) {
    groups.push({ title: 'Stocks', items: stocks })
  }
  
  if (filteredNavs.length > 0) {
    groups.push({ title: 'Navigation', items: filteredNavs.slice(0, 8) }) // Limit nav results
  }
  
  if (filteredActions.length > 0) {
    groups.push({ title: 'Actions', items: filteredActions })
  }
  
  return groups
})

// Navigation Logic
const _flatItems = computed(() => {
  return groupedResults.value.flatMap(g => g.items)
})

const isItemSelected = (gIndex: number, iIndex: number) => {
  return selectedGroupIndex.value === gIndex && selectedItemIndex.value === iIndex
}

const setSelectedIndex = (gIndex: number, iIndex: number) => {
  selectedGroupIndex.value = gIndex
  selectedItemIndex.value = iIndex
}

const isHighlighted = (item: CommandItem) => {
  if (!searchQuery.value) return false
  return item.label.toLowerCase().includes(searchQuery.value.toLowerCase())
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    const currentGroup = groupedResults.value[selectedGroupIndex.value]
    if (!currentGroup) return

    if (selectedItemIndex.value < currentGroup.items.length - 1) {
      selectedItemIndex.value++
    } else {
      // Next group
      if (selectedGroupIndex.value < groupedResults.value.length - 1) {
        selectedGroupIndex.value++
        selectedItemIndex.value = 0
      } else {
        // Loop to start
        selectedGroupIndex.value = 0
        selectedItemIndex.value = 0
      }
    }
    // Scroll into view logic could be added here
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (selectedItemIndex.value > 0) {
      selectedItemIndex.value--
    } else {
      // Prev group
      if (selectedGroupIndex.value > 0) {
        selectedGroupIndex.value--
        selectedItemIndex.value = groupedResults.value[selectedGroupIndex.value].items.length - 1
      } else {
        // Loop to end
        selectedGroupIndex.value = groupedResults.value.length - 1
        selectedItemIndex.value = groupedResults.value[selectedGroupIndex.value].items.length - 1
      }
    }
  } else if (e.key === 'Enter') {
    e.preventDefault()
    const currentGroup = groupedResults.value[selectedGroupIndex.value]
    if (currentGroup && currentGroup.items[selectedItemIndex.value]) {
      executeCommand(currentGroup.items[selectedItemIndex.value])
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    close()
  }
}

const executeCommand = (item: CommandItem) => {
  item.handler()
}

// Global Toggle
const open = () => {
  isOpen.value = true
  searchQuery.value = ''
  selectedGroupIndex.value = 0
  selectedItemIndex.value = 0
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

const close = () => {
  isOpen.value = false
}

const toggle = () => {
  isOpen.value ? close() : open()
}

const handleGlobalKeydown = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    toggle()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})

// Watch to reset selection on search
watch(searchQuery, () => {
  selectedGroupIndex.value = 0
  selectedItemIndex.value = 0
})
</script>

<style scoped lang="scss">
@use "./styles/CommandPalette.scss" as *;
</style>
