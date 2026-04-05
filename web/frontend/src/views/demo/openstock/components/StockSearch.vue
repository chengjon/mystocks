<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">🔍 股票搜索（支持 A 股 + H 股）</span>
      <span class="badge badge-success">已迁移</span>
    </div>

    <div class="search-section">
      <div class="search-form">
        <div class="search-input-group">
          <div class="input-prepend">
            <select v-model="searchMarket" class="market-select">
              <option value="auto">自动</option>
              <option value="cn">A股</option>
              <option value="hk">H股</option>
            </select>
          </div>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="输入股票代码或名称（如：茅台、600000、00700）"
            @keyup.enter="handleSearch"
          />
          <button v-if="searchQuery" class="clear-btn" @click="clearSearch">&times;</button>
        </div>
        <div class="search-actions">
          <button class="btn btn-primary" @click="handleSearch" :disabled="searchLoading">
            <span v-if="searchLoading" class="loading-spinner"></span>
            {{ searchLoading ? '搜索中...' : '搜索' }}
          </button>
          <button class="btn" @click="clearSearch">清空</button>
        </div>
      </div>

      <div v-if="searchResults.length > 0" class="search-results">
        <h3>搜索结果 ({{ searchResults.length }})</h3>
        <table class="table">
          <thead>
            <tr>
              <th width="120">代码</th>
              <th width="150">名称</th>
              <th>交易所</th>
              <th width="100">类型</th>
              <th width="400">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in searchResults" :key="index">
              <td><code>{{ row.symbol }}</code></td>
              <td>{{ row.description }}</td>
              <td>{{ row.exchange }}</td>
              <td>{{ row.type }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn btn-sm btn-primary" @click="$emit('get-quote', row)">
                    获取行情
                  </button>
                  <button class="btn btn-sm btn-info" @click="$emit('get-news', row)">
                    获取新闻
                  </button>
                  <button class="btn btn-sm btn-success" @click="openAddPopover(row)">
                    加入自选
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showAddPopover" class="popover-overlay" @click="closeAddPopover">
      <div class="popover" @click.stop>
        <div class="popover-header">
          <span>加入自选股</span>
          <button class="popover-close" @click="closeAddPopover">&times;</button>
        </div>
        <div class="popover-content">
          <label class="input-label">输入或选择分组:</label>
          <input
            v-model="selectedGroupName"
            type="text"
            class="input"
            placeholder="输入分组名称（不存在则自动创建）"
            list="group-suggestions"
            @input="queryGroupSuggestions"
          />
          <datalist id="group-suggestions">
            <option v-for="group in groupSuggestions" :key="group.id" :value="group.value">
              {{ group.value }} ({{ group.count }}只)
            </option>
          </datalist>
          <button class="btn btn-primary add-confirm-btn" @click="addToWatchlist">
            确认添加
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// Type definitions
interface StockGroup {
  id: number
  group_name: string
  stock_count: number
}

interface SearchResult {
  symbol: string
  name: string
  market: string
  exchange?: string
  [key: string]: unknown
}

interface GroupSuggestion {
  value: string
  count: number
  id: number
}

interface ApiErrorResponse {
  response?: {
    data?: {
      detail?: string
    }
  }
  message?: string
}

interface Props {
  isAuthenticated: boolean
  groups: StockGroup[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'get-quote': [stock: SearchResult]
  'get-news': [stock: SearchResult]
  'api-tested': [feature: string]
}>()

const searchQuery: Ref<string> = ref('')
const searchMarket: Ref<string> = ref('auto')
const searchResults: Ref<SearchResult[]> = ref([])
const searchLoading: Ref<boolean> = ref(false)
const selectedGroupName: Ref<string> = ref('')
const showAddPopover: Ref<boolean> = ref(false)
const selectedStock: Ref<SearchResult | null> = ref(null)
const groupSuggestions: Ref<GroupSuggestion[]> = ref([])

const handleSearch = async (): Promise<void> => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  if (!props.isAuthenticated) {
    ElMessage.warning('请先登录后再使用搜索功能')
    return
  }
  searchLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    const response = await axios.get(`${API_BASE}/stock-search/search`, {
      params: { q: searchQuery.value, market: searchMarket.value },
      headers: { Authorization: `Bearer ${token}` }
    })
    searchResults.value = response.data
    emit('api-tested', 'search')
    ElMessage.success(`找到 ${response.data.length} 条结果`)
  } catch (error: unknown) {
    const apiError = error as ApiErrorResponse
    ElMessage.error('搜索失败: ' + (apiError.response?.data?.detail || apiError.message || '未知错误'))
  } finally {
    searchLoading.value = false
  }
}

const clearSearch = (): void => {
  searchQuery.value = ''
  searchResults.value = []
}

const queryGroupSuggestions = (): void => {
  const suggestions: GroupSuggestion[] = props.groups.map((group: StockGroup): GroupSuggestion => ({
    value: group.group_name,
    count: group.stock_count,
    id: group.id
  }))
  const query = selectedGroupName.value.toLowerCase()
  groupSuggestions.value = query
    ? suggestions.filter((item: GroupSuggestion) => item.value.toLowerCase().includes(query))
    : suggestions
}

const openAddPopover = (stock: SearchResult): void => {
  selectedStock.value = stock
  queryGroupSuggestions()
  showAddPopover.value = true
}

const closeAddPopover = (): void => {
  showAddPopover.value = false
  selectedGroupName.value = ''
}

const addToWatchlist = async () => {
  try {
    const groupName = selectedGroupName.value?.trim() || '默认分组'
    if (!groupName) {
      ElMessage.warning('请输入分组名称')
      return
    }
    if (!selectedStock.value) {
      ElMessage.warning('请先选择要加入自选的股票')
      return
    }
    const stock = selectedStock.value
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    const response = await axios.post(
      `${API_BASE}/watchlist/add`,
      {
        symbol: stock.symbol,
        display_name: stock.description,
        exchange: stock.exchange,
        market: stock.market,
        group_name: groupName
      },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    ElMessage.success(`已添加到分组 "${response.data.group_name}"`)
    closeAddPopover()
    emit('api-tested', 'watchlist')
  } catch (error: unknown) {
    const apiError = error as ApiErrorResponse
    ElMessage.error('添加失败: ' + (apiError.response?.data?.detail || apiError.message))
  }
}
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.search-section {
  padding: var(--artdeco-spacing-3) 0;
}

.search-form {
  display: flex;
  gap: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  align-items: stretch;
}

.search-input-group {
  flex: 1;
  display: flex;
  align-items: stretch;
  overflow: hidden;
  background: var(--artdeco-bg-global);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  transition: border-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:focus-within {
    border-color: var(--artdeco-gold-primary);
  }
}

.input-prepend {
  display: flex;
  align-items: center;
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border-right: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
}

.market-select {
  min-width: var(--artdeco-spacing-10);
  padding: calc(var(--artdeco-spacing-5) / 2) calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  border: none;
  outline: none;
  background: transparent;
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
  cursor: pointer;

  &:focus {
    background: var(--artdeco-bg-elevated);
  }
}

.search-input {
  flex: 1;
  padding: calc(var(--artdeco-spacing-5) / 2) calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  border: none;
  outline: none;
  background: transparent;
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);

  &::placeholder {
    color: var(--artdeco-fg-muted);
  }
}

.clear-btn {
  padding: 0 var(--artdeco-spacing-3);
  border: none;
  background: none;
  color: var(--artdeco-fg-muted);
  font-size: calc(var(--artdeco-text-base) + var(--artdeco-spacing-px) * 2);
  cursor: pointer;
  transition: color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:hover {
    color: var(--artdeco-fg-primary);
  }
}

.search-actions {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.search-results {
  margin-top: var(--artdeco-spacing-5);

  h3 {
    margin-bottom: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
    color: var(--artdeco-gold-primary);
    font-size: var(--artdeco-text-base);
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.action-buttons {
  display: flex;
  gap: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2));
  flex-wrap: wrap;
}

.input {
  width: 100%;
  padding: calc(var(--artdeco-spacing-5) / 2) var(--artdeco-spacing-3);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-global);
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
  transition: border-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:focus {
    outline: none;
    border-color: var(--artdeco-gold-primary);
  }

  &::placeholder {
    color: var(--artdeco-fg-muted);
  }
}

.input-label {
  display: block;
  margin-bottom: var(--artdeco-spacing-2);
  color: var(--artdeco-fg-muted);
  font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
}

.loading-spinner {
  display: inline-block;
  width: var(--artdeco-spacing-4);
  height: var(--artdeco-spacing-4);
  margin-right: var(--artdeco-spacing-2);
  border: calc(var(--artdeco-spacing-px) * 2) solid color-mix(in srgb, var(--artdeco-fg-primary) 30%, transparent);
  border-top-color: var(--artdeco-fg-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.popover-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--artdeco-bg-global) 35%, transparent);
  z-index: 1000;
}

.popover {
  width: calc((var(--artdeco-spacing-20) * 3) + var(--artdeco-spacing-10) + var(--artdeco-spacing-5));
  overflow: hidden;
  background: var(--artdeco-bg-card);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  box-shadow: var(--artdeco-shadow-lg);
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);
  color: var(--artdeco-fg-primary);
  font-weight: var(--artdeco-font-semibold);
}

.popover-close {
  padding: 0;
  border: none;
  background: none;
  color: var(--artdeco-fg-muted);
  cursor: pointer;
  font-size: var(--artdeco-text-lg);
  line-height: var(--artdeco-leading-none);
  transition: color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:hover {
    color: var(--artdeco-fg-primary);
  }
}

.popover-content {
  padding: var(--artdeco-spacing-4);
}

.add-confirm-btn {
  width: 100%;
  margin-top: var(--artdeco-spacing-3);
}
</style>
