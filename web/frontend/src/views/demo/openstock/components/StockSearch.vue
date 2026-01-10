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
          <button
            style="width: 100%; margin-top: 12px;"
            @click="addToWatchlist"
          >
            确认添加
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface Props {
  isAuthenticated: boolean
  groups: any[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'get-quote': [stock: any]
  'get-news': [stock: any]
  'api-tested': [feature: string]
}>()

const searchQuery = ref('')
const searchMarket = ref('auto')
const searchResults = ref<any[]>([])
const searchLoading = ref(false)
const selectedGroupName = ref('')
const showAddPopover = ref(false)
const selectedStock = ref<any>(null)
const groupSuggestions = ref<any[]>([])

const handleSearch = async () => {
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
  } catch (error: any) {
    ElMessage.error('搜索失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    searchLoading.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
}

const queryGroupSuggestions = () => {
  const suggestions = props.groups.map((group: any) => ({
    value: group.group_name,
    count: group.stock_count,
    id: group.id
  }))
  const query = selectedGroupName.value.toLowerCase()
  groupSuggestions.value = query
    ? suggestions.filter((item: any) => item.value.toLowerCase().includes(query))
    : suggestions
}

const openAddPopover = (stock: any) => {
  selectedStock.value = stock
  queryGroupSuggestions()
  showAddPopover.value = true
}

const closeAddPopover = () => {
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
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    const response = await axios.post(
      `${API_BASE}/watchlist/add`,
      { symbol: selectedStock.value.symbol, display_name: selectedStock.value.description, exchange: selectedStock.value.exchange, market: selectedStock.value.market, group_name: groupName },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    ElMessage.success(`已添加到分组 "${response.data.group_name}"`)
    closeAddPopover()
    emit('api-tested', 'watchlist')
  } catch (error: any) {
    ElMessage.error('添加失败: ' + (error.response?.data?.detail || error.message))
  }
}
</script>

<style scoped lang="scss">

.search-section {
  padding: 10px 0;
}

.search-form {
  display: flex;
  gap: 15px;
  align-items: stretch;
}

.search-input-group {
  flex: 1;
  display: flex;
  align-items: stretch;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-primary);
  transition: border-color 0.2s;

  &:focus-within {
    border-color: var(--primary);
  }
}

.input-prepend {
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
}

.market-select {
  padding: 10px 14px;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
  min-width: 80px;

  &:focus {
    background: var(--bg-dark);
  }
}

.search-input {
  flex: 1;
  padding: 10px 14px;
  border: none;
  font-size: 14px;
  color: var(--text-primary);
  background: transparent;
  outline: none;

  &::placeholder {
    color: var(--text-muted);
  }
}

.clear-btn {
  padding: 0 12px;
  background: none;
  border: none;
  font-size: 18px;
  color: var(--text-muted);
  cursor: pointer;

  &:hover {
    color: var(--text-primary);
  }
}

.search-actions {
  display: flex;
  gap: 10px;
}

.search-results {
  margin-top: 20px;

  h3 {
    margin-bottom: 15px;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary);
  }
}

.input-label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.popover-content {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  width: 300px;
  overflow: hidden;

  .popover-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-light);
    font-weight: 600;
    color: var(--text-primary);
  }

  .popover-close {
    background: none;
    border: none;
    font-size: 20px;
    color: var(--text-muted);
    cursor: pointer;

    &:hover {
      color: var(--text-primary);
    }
  }

  .popover-content {
    padding: 16px;
  }
}
</style>
