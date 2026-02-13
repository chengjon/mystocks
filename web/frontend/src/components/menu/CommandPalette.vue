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
import { ARTDECO_MENU_ENHANCED } from '@/layouts/MenuConfig.enhanced'

// Types
type CommandType = 'navigation' | 'action' | 'search' | 'external'

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
  
  const traverse = (items: any[], parentLabel = '') => {
    items.forEach(item => {
      if (item.children) {
        traverse(item.children, item.label)
      } else {
        commands.push({
          id: `nav-${item.path}`,
          label: item.label,
          sublabel: parentLabel ? `${parentLabel} > ${item.label}` : 'Navigation',
          type: 'navigation',
          icon: item.icon || 'FileText',
          handler: () => {
            router.push(item.path)
            close()
          },
          keywords: [item.label, parentLabel, 'page', 'nav']
        })
      }
    })
  }
  
  traverse(ARTDECO_MENU_ENHANCED)
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
const flatItems = computed(() => {
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
@import '@/styles/artdeco-tokens.scss';

.command-palette-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 15vh;
}

.command-palette {
  width: 100%;
  max-width: 640px;
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-primary);
  border-radius: var(--artdeco-radius-lg);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: 80vh;
}

.command-header {
  display: flex;
  align-items: center;
  padding: var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-subtle);
}

.search-icon {
  color: var(--artdeco-fg-muted);
  margin-right: var(--artdeco-spacing-3);
}

.command-input {
  flex: 1;
  font-size: 16px;
  color: var(--artdeco-fg-primary);
  background: transparent;
  border: none;
  outline: none;
  
  &::placeholder {
    color: var(--artdeco-fg-muted);
  }
}

.shortcut-hint {
  font-size: 12px;
  color: var(--artdeco-fg-muted);
  border: 1px solid var(--artdeco-border-subtle);
  border-radius: 4px;
  padding: 2px 6px;
}

.command-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--artdeco-spacing-2) 0;
}

.no-results {
  padding: var(--artdeco-spacing-8);
  text-align: center;
  color: var(--artdeco-fg-muted);
  
  .no-results-icon {
    margin-bottom: var(--artdeco-spacing-4);
    opacity: 0.5;
  }
}

.group-header {
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--artdeco-fg-muted);
  letter-spacing: 0.05em;
  margin-top: var(--artdeco-spacing-2);
  
  &:first-child {
    margin-top: 0;
  }
}

.command-item {
  display: flex;
  align-items: center;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  cursor: pointer;
  border-left: 2px solid transparent;
  transition: background 0.1s;
  
  &.active {
    background: var(--artdeco-bg-elevated);
    border-left-color: var(--artdeco-gold-primary);
    
    .command-icon {
      color: var(--artdeco-gold-primary);
    }
  }
  
  .command-icon {
    color: var(--artdeco-fg-muted);
    margin-right: var(--artdeco-spacing-3);
  }
  
  .command-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .command-label {
    font-size: 14px;
    color: var(--artdeco-fg-primary);
  }
  
  .command-sublabel {
    font-size: 12px;
    color: var(--artdeco-fg-muted);
  }
  
  .command-shortcut {
    kbd {
      font-family: var(--artdeco-font-mono);
      font-size: 11px;
      padding: 2px 4px;
      background: var(--artdeco-bg-global);
      border: 1px solid var(--artdeco-border-subtle);
      border-radius: 3px;
      color: var(--artdeco-fg-muted);
    }
  }
  
  .arrow-icon {
    color: var(--artdeco-fg-muted);
    opacity: 0.5;
  }
}

.command-footer {
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  background: var(--artdeco-bg-elevated);
  border-top: 1px solid var(--artdeco-border-subtle);
  font-size: 11px;
  color: var(--artdeco-fg-muted);
  display: flex;
  justify-content: flex-end;
}

.keyboard-shortcuts {
  display: flex;
  gap: var(--artdeco-spacing-4);
  
  .shortcut-item {
    display: flex;
    align-items: center;
    gap: 4px;
    
    kbd {
      font-family: var(--artdeco-font-mono);
      background: var(--artdeco-bg-surface);
      border: 1px solid var(--artdeco-border-subtle);
      border-radius: 3px;
      padding: 1px 4px;
      min-width: 18px;
      text-align: center;
    }
  }
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>