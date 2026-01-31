<template>
  <transition name="fade">
    <div v-if="isOpen" class="command-palette-overlay" @click.self="close">
      <div class="command-palette">
        <div class="command-header">
          <ArtDecoIcon name="Search" size="sm" class="search-icon" />
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            class="command-input"
            placeholder="搜索命令或菜单..."
            @input="handleSearch"
            @keydown="handleKeydown"
          />
          <div class="shortcut-hint">ESC 关闭</div>
        </div>

        <div class="command-body">
          <div v-if="filteredCommands.length === 0" class="no-results">
            <ArtDecoIcon name="Search" size="lg" class="no-results-icon" />
            <p>未找到匹配项</p>
          </div>

          <div
            v-for="(command, index) in paginatedCommands"
            :key="command.path"
            class="command-item"
            :class="{
              active: index === selectedIndex,
              highlighted: isHighlighted(command)
            }"
            @click="executeCommand(command)"
          >
            <ArtDecoIcon :name="command.icon" size="sm" class="command-icon" />
            <div class="command-info">
              <span class="command-label">{{ command.label }}</span>
              <span class="command-domain">{{ command.domainLabel }}</span>
            </div>
            <ArtDecoIcon name="ArrowRight" size="xs" class="arrow-icon" />
          </div>

          <div v-if="showPagination" class="pagination-controls">
            <button class="pagination-btn" @click="prevPage">
              <ArtDecoIcon name="ChevronLeft" size="xs" />
            </button>
            <span class="pagination-info">{{ currentPage }} / {{ totalPages }}</span>
            <button class="pagination-btn" @click="nextPage">
              <ArtDecoIcon name="ChevronRight" size="xs" />
            </button>
          </div>
        </div>

        <div class="command-footer">
          <div class="keyboard-shortcuts">
            <span class="shortcut-item">
              <kbd>↑↓</kbd> 导航
            </span>
            <span class="shortcut-item">
              <kbd>Enter</kbd> 选择
            </span>
            <span class="shortcut-item">
              <kbd>Ctrl</kbd> + <kbd>K</kbd> 打开
            </span>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import { ARTDECO_MENU_ENHANCED, type MenuItem } from '@/layouts/MenuConfig.enhanced'

interface Command {
  path: string
  label: string
  icon: string
  domainLabel: string
}

const router = useRouter()

const isOpen = ref<boolean>(false)
const searchQuery = ref<string>('')
const searchInputRef = ref<any>(null)
const selectedIndex = ref<number>(0)
const currentPage = ref<number>(1)
const ITEMS_PER_PAGE = 8

const allCommands = computed<Command[]>(() => {
  const commands: Command[] = []
  ARTDECO_MENU_ENHANCED.forEach(domain => {
    if (domain.children) {
      domain.children.forEach(child => {
        commands.push({
          path: child.path,
          label: child.label,
          icon: child.icon,
          domainLabel: domain.label
        })
      })
    }
  })
  return commands
})

const filteredCommands = computed<Command[]>(() => {
  if (!searchQuery.value.trim()) {
    return allCommands.value
  }
  const query = searchQuery.value.toLowerCase().trim()
  return allCommands.value.filter(cmd =>
    cmd.label.toLowerCase().includes(query) ||
    cmd.domainLabel.toLowerCase().includes(query)
  )
})

const totalPages = computed(() => Math.ceil(filteredCommands.value.length / ITEMS_PER_PAGE))

const paginatedCommands = computed<Command[]>(() => {
  const start = (currentPage.value - 1) * ITEMS_PER_PAGE
  const end = start + ITEMS_PER_PAGE
  return filteredCommands.value.slice(start, end)
})

const showPagination = computed(() => totalPages.value > 1)

const handleSearch = () => {
  currentPage.value = 1
  selectedIndex.value = 0
}

const isHighlighted = (command: Command): boolean => {
  if (!searchQuery.value.trim()) {
    return false
  }
  const query = searchQuery.value.toLowerCase().trim()
  return command.label.toLowerCase().includes(query) ||
         command.domainLabel.toLowerCase().includes(query)
}

const handleKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (selectedIndex.value < paginatedCommands.value.length - 1) {
        selectedIndex.value++
      }
      break

    case 'ArrowUp':
      event.preventDefault()
      if (selectedIndex.value > 0) {
        selectedIndex.value--
      }
      break

    case 'Enter':
      event.preventDefault()
      if (selectedIndex.value >= 0 && paginatedCommands.value[selectedIndex.value]) {
        executeCommand(paginatedCommands.value[selectedIndex.value])
      }
      break

    case 'PageDown':
      event.preventDefault()
      nextPage()
      break

    case 'PageUp':
      event.preventDefault()
      prevPage()
      break

    case 'Escape':
      event.preventDefault()
      close()
      break
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    selectedIndex.value = 0
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    selectedIndex.value = 0
  }
}

const executeCommand = (command: Command) => {
  router.push(command.path)
  close()
}

const open = () => {
  isOpen.value = true
  searchQuery.value = ''
  currentPage.value = 1
  selectedIndex.value = 0
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

const close = () => {
  isOpen.value = false
  searchQuery.value = ''
}

const toggle = () => {
  if (isOpen.value) {
    close()
  } else {
    open()
  }
}

const handleGlobalKeydown = (event: KeyboardEvent) => {
  if (event.ctrlKey && event.key === 'k') {
    event.preventDefault()
    toggle()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})

watch(isOpen, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

defineExpose({
  open,
  close,
  toggle
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.command-palette-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  z-index: 9999;
}

.command-palette {
  width: 100%;
  max-width: 640px;
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-primary);
  border-radius: var(--artdeco-radius-lg);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.command-header {
  display: flex;
  align-items: center;
  padding: var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-secondary);
  background: var(--artdeco-bg-primary-light);
}

.search-icon {
  color: var(--artdeco-text-tertiary);
  margin-right: var(--artdeco-spacing-3);
  flex-shrink: 0;
}

.command-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: var(--artdeco-font-size-base);
  color: var(--artdeco-text-primary);
  outline: none;
  padding: 0;

  &::placeholder {
    color: var(--artdeco-text-tertiary);
  }
}

.shortcut-hint {
  font-size: var(--artdeco-font-size-xs);
  color: var(--artdeco-text-tertiary);
  margin-left: var(--artdeco-spacing-3);
  white-space: nowrap;
}

.command-body {
  max-height: 480px;
  overflow-y: auto;
  padding: var(--artdeco-spacing-3);
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--artdeco-spacing-8);
  color: var(--artdeco-text-tertiary);

  .no-results-icon {
    margin-bottom: var(--artdeco-spacing-4);
    opacity: 0.3;
  }

  p {
    font-size: var(--artdeco-font-size-sm);
  }
}

.command-item {
  display: flex;
  align-items: center;
  padding: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-1);
  border-radius: var(--artdeco-radius-md);
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid transparent;

  &:hover {
    background: var(--artdeco-bg-surface-hover);
    border-color: var(--artdeco-border-secondary);
  }

  &.active {
    background: var(--artdeco-bg-primary);
    color: var(--artdeco-text-on-primary);
    border-color: var(--artdeco-border-active);
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
  }

  &.highlighted {
    font-weight: 600;
  }

  &:last-child {
    margin-bottom: 0;
  }
}

.command-icon {
  margin-right: var(--artdeco-spacing-3);
  flex-shrink: 0;
  opacity: 0.8;
}

.command-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-1);
}

.command-label {
  font-size: var(--artdeco-font-size-sm);
  color: var(--artdeco-text-primary);
  font-weight: 500;
}

.command-domain {
  font-size: var(--artdeco-font-size-xs);
  color: var(--artdeco-text-tertiary);
}

.arrow-icon {
  opacity: 0.5;
  margin-left: var(--artdeco-spacing-3);
}

.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-3);
  padding-top: var(--artdeco-spacing-4);
  margin-top: var(--artdeco-spacing-3);
  border-top: 1px solid var(--artdeco-border-secondary);
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--artdeco-spacing-2);
  background: var(--artdeco-bg-surface-hover);
  border: 1px solid var(--artdeco-border-secondary);
  border-radius: var(--artdeco-radius-sm);
  color: var(--artdeco-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--artdeco-bg-primary);
    border-color: var(--artdeco-border-active);
    color: var(--artdeco-text-on-primary);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.pagination-info {
  font-size: var(--artdeco-font-size-sm);
  color: var(--artdeco-text-tertiary);
  min-width: 60px;
  text-align: center;
}

.command-footer {
  display: flex;
  justify-content: center;
  padding: var(--artdeco-spacing-3);
  background: var(--artdeco-bg-primary-light);
  border-top: 1px solid var(--artdeco-border-secondary);
}

.keyboard-shortcuts {
  display: flex;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
  justify-content: center;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  font-size: var(--artdeco-font-size-xs);
  color: var(--artdeco-text-tertiary);
}

kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 6px;
  background: var(--artdeco-bg-surface);
  border: 1px solid var(--artdeco-border-secondary);
  border-radius: var(--artdeco-radius-sm);
  font-size: var(--artdeco-font-size-xs);
  font-family: var(--artdeco-font-family-mono);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

// Fade transition
.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}

// Scrollbar styling
.command-body {
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: var(--artdeco-bg-surface);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--artdeco-border-secondary);
    border-radius: 3px;

    &:hover {
      background: var(--artdeco-border-hover);
    }
  }
}
</style>
