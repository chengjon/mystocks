<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="command-palette-overlay"
        @click.self="close"
      >
        <div class="command-palette-container">
          <!-- 搜索输入框 -->
          <div class="search-input-wrapper">
            <span class="search-icon">🔍</span>
            <input
              ref="searchInputRef"
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Type to search..."
              @input="onSearchInput"
              @keydown.down.prevent="onKeyDown"
              @keydown.up.prevent="onKeyUp"
              @keydown.enter.prevent="onEnter"
              @keydown.escape="close"
            />
            <kbd class="escape-hint">ESC</kbd>
          </div>

          <!-- 搜索结果列表 -->
          <div class="results-container">
            <!-- 最近访问 -->
            <div v-if="showRecent && searchQuery === ''" class="result-section">
              <h3 class="section-title">Recent</h3>
              <ul class="result-list">
                <li
                  v-for="(item, index) in recentItems"
                  :key="item.path"
                  class="result-item"
                  :class="{ active: selectedIndex === index }"
                  @click="navigateTo(item.path)"
                  @mouseenter="selectedIndex = index"
                >
                  <span class="result-icon">{{ item.icon }}</span>
                  <span class="result-label">{{ item.label }}</span>
                  <span class="result-path">{{ item.path }}</span>
                </li>
              </ul>
            </div>

            <!-- 搜索结果 -->
            <div v-if="searchQuery !== '' && displayResults.length > 0" class="result-section">
              <h3 class="section-title">
                Results ({{ displayResults.length }})
              </h3>
              <ul class="result-list">
                <li
                  v-for="(item, index) in displayResults"
                  :key="item.path"
                  class="result-item"
                  :class="{ active: selectedIndex === index }"
                  @click="navigateTo(item.path)"
                  @mouseenter="selectedIndex = index"
                >
                  <span class="result-icon">{{ item.icon }}</span>
                  <span class="result-label" v-html="highlightMatch(item.label)"></span>
                  <span class="result-category">{{ item.category }}</span>
                </li>
              </ul>
            </div>

            <!-- 无结果提示 -->
            <div v-if="searchQuery !== '' && displayResults.length === 0" class="no-results">
              <span class="no-results-icon">🔍</span>
              <p>No results found for "{{ searchQuery }}"</p>
            </div>
          </div>

          <!-- 底部提示 -->
          <div class="footer-hints">
            <div class="hint-item">
              <kbd>↑↓</kbd> Navigate
            </div>
            <div class="hint-item">
              <kbd>Enter</kbd> Select
            </div>
            <div class="hint-item">
              <kbd>Esc</kbd> Close
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Fuse, { type FuseResult } from 'fuse.js'

export interface CommandItem {
  path: string
  label: string
  icon: string
  category: string
  keywords?: string[]
}

interface Props {
  items: CommandItem[]
  maxRecent?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxRecent: 5
})

const emit = defineEmits<{
  open: []
  close: []
  navigate: [path: string]
}>()

// Router
const router = useRouter()

// State
const isOpen = ref(false)
const searchQuery = ref('')
const selectedIndex = ref(0)
const searchInputRef = ref<HTMLInputElement>()
const recentItems = ref<CommandItem[]>([])
const searchResults = ref<FuseResult<CommandItem>[]>([])

// 计算属性：提取实际的结果项（避免在模板中访问 item.item）
const displayResults = computed(() => {
  return searchResults.value.map(result => result.item)
})

// Fuse.js配置
const fuse = ref<Fuse<CommandItem>>()

// 初始化Fuse.js搜索引擎
const initFuse = () => {
  fuse.value = new Fuse(props.items, {
    keys: [
      { name: 'label', weight: 2 },
      { name: 'keywords', weight: 1.5 },
      { name: 'category', weight: 1 },
      { name: 'path', weight: 0.5 }
    ],
    threshold: 0.3,
    ignoreLocation: true,
    includeScore: true
  })
}

// 显示最近访问
const showRecent = computed(() => recentItems.value.length > 0)

// 打开Command Palette
const open = () => {
  isOpen.value = true
  searchQuery.value = ''
  selectedIndex.value = 0
  emit('open')
  
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

// 关闭Command Palette
const close = () => {
  isOpen.value = false
  searchQuery.value = ''
  emit('close')
}

// 搜索输入处理
const onSearchInput = () => {
  if (!fuse.value) return
  
  if (searchQuery.value.trim() === '') {
    searchResults.value = []
    selectedIndex.value = 0
    return
  }
  
  const results = fuse.value.search(searchQuery.value)
  searchResults.value = results.slice(0, 8) // 限制显示8个结果
  selectedIndex.value = 0
}

// 键盘导航
const onKeyDown = () => {
  const maxIndex = searchQuery.value === ''
    ? recentItems.value.length - 1
    : displayResults.value.length - 1

  if (selectedIndex.value < maxIndex) {
    selectedIndex.value++
  }
}

const onKeyUp = () => {
  if (selectedIndex.value > 0) {
    selectedIndex.value--
  }
}

// 确认选择
const onEnter = () => {
  const items = searchQuery.value === '' ? recentItems.value : displayResults.value
  const selected = items[selectedIndex.value]

  if (selected) {
    navigateTo(selected.path)
  }
}

// 导航到指定路径
const navigateTo = async (path: string) => {
  await router.push(path)
  addToRecent(path)
  close()
  emit('navigate', path)
}

// 添加到最近访问
const addToRecent = (path: string) => {
  const item = props.items.find(i => i.path === path)
  if (!item) return
  
  // 移除已存在的相同项
  recentItems.value = recentItems.value.filter(i => i.path !== path)
  
  // 添加到开头
  recentItems.value.unshift(item)
  
  // 限制数量
  if (recentItems.value.length > props.maxRecent) {
    recentItems.value = recentItems.value.slice(0, props.maxRecent)
  }
  
  // 保存到localStorage
  saveRecentToStorage()
}

// 高亮匹配文本
const highlightMatch = (text: string): string => {
  if (!searchQuery.value) return text
  
  const regex = new RegExp(`(${searchQuery.value})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

// 从localStorage加载最近访问
const loadRecentFromStorage = () => {
  try {
    const stored = localStorage.getItem('command-palette-recent')
    if (stored) {
      const paths = JSON.parse(stored) as string[]
      recentItems.value = paths
        .map(path => props.items.find(i => i.path === path))
        .filter((item): item is CommandItem => item !== undefined)
        .slice(0, props.maxRecent)
    }
  } catch (error) {
    console.warn('Failed to load recent items:', error)
  }
}

// 保存最近访问到localStorage
const saveRecentToStorage = () => {
  try {
    const paths = recentItems.value.map(i => i.path)
    localStorage.setItem('command-palette-recent', JSON.stringify(paths))
  } catch (error) {
    console.warn('Failed to save recent items:', error)
  }
}

// 全局快捷键处理
const handleGlobalKeydown = (event: KeyboardEvent) => {
  // Ctrl+K 或 Cmd+K
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    isOpen.value ? close() : open()
  }
}

// 监听props.items变化，重新初始化Fuse
watch(() => props.items, () => {
  initFuse()
}, { immediate: true })

// 组件挂载
onMounted(() => {
  initFuse()
  loadRecentFromStorage()
  window.addEventListener('keydown', handleGlobalKeydown)
})

// 组件卸载
onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})

// 暴露方法供父组件调用
defineExpose({
  open,
  close
})
</script>

<style scoped lang="scss">
@import '@/styles/theme-tokens.scss';

.command-palette-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  z-index: var(--z-index-modal, 1000);
}

.command-palette-container {
  width: 90%;
  max-width: 640px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

// ========== 搜索框 ==========
.search-input-wrapper {
  display: flex;
  align-items: center;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  gap: var(--spacing-sm);
}

.search-icon {
  font-size: 20px;
  color: var(--text-secondary);
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: var(--font-size-lg, 18px);
  color: var(--text-primary);
  
  &::placeholder {
    color: var(--text-disabled);
  }
}

.escape-hint {
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
}

// ========== 结果列表 ==========
.results-container {
  max-height: 400px;
  overflow-y: auto;
  @include scrollbar;
}

.result-section {
  padding: var(--spacing-sm) 0;
  
  &:not(:last-child) {
    border-bottom: 1px solid var(--border-color);
  }
}

.section-title {
  padding: 0 var(--spacing-md);
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-xs, 11px);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-disabled);
}

.result-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.result-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  cursor: pointer;
  transition: background 0.15s;
  
  &:hover,
  &.active {
    background: var(--bg-hover);
  }
  
  &.active {
    border-left: 3px solid var(--accent-color);
    padding-left: calc(var(--spacing-md) - 3px);
  }
}

.result-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.result-label {
  flex: 1;
  font-size: var(--font-size-base, 14px);
  color: var(--text-primary);
  
  :deep(mark) {
    background: transparent;
    color: var(--accent-color);
    font-weight: 600;
  }
}

.result-path,
.result-category {
  font-size: var(--font-size-sm, 12px);
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
}

// ========== 无结果提示 ==========
.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-xl);
  color: var(--text-secondary);
  gap: var(--spacing-sm);
}

.no-results-icon {
  font-size: 48px;
  opacity: 0.5;
}

// ========== 底部提示 ==========
.footer-hints {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-sm);
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-color);
}

.hint-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm, 12px);
  color: var(--text-secondary);
  
  kbd {
    padding: 2px 6px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-family: var(--font-family-mono);
    font-size: 11px;
  }
}

// ========== 过渡动画 ==========
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s;
  
  .command-palette-container {
    transition: transform 0.2s, opacity 0.2s;
  }
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  
  .command-palette-container {
    transform: scale(0.95) translateY(-10px);
    opacity: 0;
  }
}

.modal-enter-to,
.modal-leave-from {
  opacity: 1;
  
  .command-palette-container {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}
</style>
