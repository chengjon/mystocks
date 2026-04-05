<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">⭐ 自选股管理（分组）</span>
      <span class="badge badge-success">已迁移</span>
    </div>

    <div class="watchlist-section">
      <div class="watchlist-grid">
        <div class="sidebar">
          <WatchlistGroupManager
            ref="groupManagerRef"
            v-model="currentGroupId"
            @group-selected="handleGroupSelected"
            @group-created="handleGroupCreated"
            @group-updated="handleGroupUpdated"
            @group-deleted="handleGroupDeleted"
          />
        </div>

        <div class="main-content">
          <div class="group-stocks">
            <div class="group-stocks-header">
              <h4>{{ currentGroupName }} ({{ currentGroupStocks.length }} 只)</h4>
              <div class="actions">
                <button class="btn btn-sm btn-primary" @click="fetchGroupStocks" :disabled="watchlistLoading">
                  刷新
                </button>
                <button class="btn btn-sm btn-danger" @click="clearCurrentGroup" :disabled="watchlistLoading">
                  清空当前分组
                </button>
              </div>
            </div>

            <div class="table-wrapper" v-loading="watchlistLoading">
              <table class="table">
                <thead>
                  <tr>
                    <th width="100">代码</th>
                    <th width="120">名称</th>
                    <th width="80">市场</th>
                    <th>交易所</th>
                    <th>备注</th>
                    <th width="300">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in currentGroupStocks" :key="index">
                    <td><code>{{ row.symbol }}</code></td>
                    <td>{{ row.displayName ?? row.displayName }}</td>
                    <td>
                      <span
                        class="badge"
                        :class="row.market === 'CN' ? 'badge-success' : 'badge-warning'"
                      >
                        {{ row.market === 'CN' ? 'A股' : 'H股' }}
                      </span>
                    </td>
                    <td>{{ row.exchange }}</td>
                    <td>
                      <input
                        v-model="row.notes"
                        class="input"
                        placeholder="添加备注"
                        @blur="updateNotes(row)"
                      />
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" @click="$emit('get-quote', row)">
                          查看行情
                        </button>
                        <button class="btn btn-sm btn-info" @click="openMovePopover(row)">
                          移动
                        </button>
                        <button class="btn btn-sm btn-danger" @click="removeFromWatchlist(row)">
                          删除
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showMovePopover" class="popover-overlay" @click="closeMovePopover">
      <div class="popover" @click.stop>
        <div class="popover-header">
          <span>移动到</span>
          <button class="popover-close" @click="closeMovePopover">&times;</button>
        </div>
        <div class="popover-content">
          <select v-model="moveToGroupId" class="select">
            <option :value="null">选择目标分组</option>
            <option
              v-for="(group, _idx) in groups.filter(g => g.id !== currentGroupId)"
              :key="group.id"
              :value="group.id"
            >
              {{ group.group_name }}
            </option>
          </select>
          <button class="btn btn-primary move-confirm-btn" @click="moveStock">
            确认移动
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import WatchlistGroupManager from '@/components/watchlist/WatchlistGroupManager.vue'

interface WatchlistGroup {
  id: number
  group_name: string
}

interface WatchlistStock {
  symbol: string
  displayName?: string
  market: string
  exchange: string
  notes?: string
}

interface Props {
  groups: WatchlistGroup[]
}

const _props = defineProps<Props>()

const emit = defineEmits<{
  'get-quote': [stock: WatchlistStock]
  'groups-changed': []
  'api-tested': [feature: string]
}>()

const groupManagerRef = ref<unknown>(null)
const currentGroupId = ref<number | undefined>(undefined)
const currentGroupName = ref('')
const currentGroupStocks = ref<WatchlistStock[]>([])
const watchlistLoading = ref(false)
const moveToGroupId = ref<number | null>(null)
const showMovePopover = ref(false)
const selectedStock = ref<WatchlistStock | null>(null)

const handleGroupSelected = (group: WatchlistGroup): void => {
  currentGroupId.value = group.id
  currentGroupName.value = group.group_name
  fetchGroupStocks()
}

const handleGroupCreated = (): void => emit('groups-changed')
const handleGroupUpdated = (group: WatchlistGroup): void => {
  if (currentGroupId.value === group.id) {
    currentGroupName.value = group.group_name
  }
  emit('groups-changed')
}
const handleGroupDeleted = (): void => emit('groups-changed')

interface ApiErrorResponse {
  response?: {
    data?: {
      detail?: string
    }
  }
  message?: string
}

const fetchGroupStocks = async (): Promise<void> => {
  if (!currentGroupId.value) return
  watchlistLoading.value = true
  try {
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    const response = await axios.get(`${API_BASE}/watchlist/group/${currentGroupId.value}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    currentGroupStocks.value = response.data
    emit('api-tested', 'watchlist')
  } catch (error: unknown) {
    const apiError = error as ApiErrorResponse
    ElMessage.error('获取分组股票失败: ' + (apiError.response?.data?.detail || apiError.message || '未知错误'))
  } finally {
    watchlistLoading.value = false
  }
}

const openMovePopover = (stock: WatchlistStock): void => {
  selectedStock.value = stock
  showMovePopover.value = true
}

const closeMovePopover = (): void => {
  showMovePopover.value = false
  moveToGroupId.value = null
}

const moveStock = async (): Promise<void> => {
  if (!moveToGroupId.value) {
    ElMessage.warning('请选择目标分组')
    return
  }
  if (!selectedStock.value) {
    ElMessage.warning('请选择要移动的股票')
    return
  }
  try {
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    await axios.put(
      `${API_BASE}/watchlist/move`,
      { symbol: selectedStock.value.symbol, from_group_id: currentGroupId.value, to_group_id: moveToGroupId.value },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    ElMessage.success('股票已移动')
    emit('groups-changed')
    fetchGroupStocks()
    closeMovePopover()
  } catch (error: unknown) {
    const apiError = error as ApiErrorResponse
    ElMessage.error('移动失败: ' + (apiError.response?.data?.detail || apiError.message || '未知错误'))
  }
}

const clearCurrentGroup = async (): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      `确定要清空分组 "${currentGroupName.value}" 中的所有股票吗？此操作不可恢复！`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    for (const stock of currentGroupStocks.value) {
      await axios.delete(`${API_BASE}/watchlist/remove/${stock.symbol}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
    }
    ElMessage.success('分组已清空')
    emit('groups-changed')
    fetchGroupStocks()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const apiError = error as ApiErrorResponse
      ElMessage.error('清空失败: ' + (apiError.response?.data?.detail || apiError.message || '未知错误'))
    }
  }
}

const removeFromWatchlist = async (stock: WatchlistStock): Promise<void> => {
  try {
    await ElMessageBox.confirm('确定要从自选股中删除吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    await axios.delete(`${API_BASE}/watchlist/remove/${stock.symbol}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('已从自选股删除')
    emit('groups-changed')
    fetchGroupStocks()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      const apiError = error as ApiErrorResponse
      ElMessage.error('删除失败: ' + (apiError.response?.data?.detail || apiError.message || '未知错误'))
    }
  }
}

const updateNotes = async (stock: WatchlistStock): Promise<void> => {
  try {
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    await axios.put(
      `${API_BASE}/watchlist/notes/${stock.symbol}`,
      { notes: stock.notes },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    ElMessage.success('备注已更新')
  } catch (error: unknown) {
    const apiError = error as ApiErrorResponse
    ElMessage.error('更新失败: ' + (apiError.response?.data?.detail || apiError.message || '未知错误'))
  }
}
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.watchlist-section {
  padding: var(--artdeco-spacing-3) 0;
}

.watchlist-grid {
  display: grid;
  grid-template-columns: calc(var(--artdeco-spacing-20) * 3) minmax(0, 1fr);
  gap: var(--artdeco-spacing-5);
}

.sidebar,
.main-content,
.group-stocks {
  min-height: calc(var(--artdeco-spacing-20) * 6 + var(--artdeco-spacing-5));
}

.group-stocks {
  padding: var(--artdeco-spacing-5);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
}

.group-stocks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-5);
  padding-bottom: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  border-bottom: calc(var(--artdeco-spacing-px) * 2) solid color-mix(in srgb, var(--artdeco-gold-primary) 60%, transparent);

  h4 {
    margin: 0;
    color: var(--artdeco-gold-primary);
    font-size: calc(var(--artdeco-text-base) + var(--artdeco-spacing-px) * 2);
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.actions {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.table-wrapper {
  min-height: calc(var(--artdeco-spacing-20) * 5);
}

.action-buttons {
  display: flex;
  gap: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2));
  flex-wrap: wrap;
}

.input,
.select {
  width: 100%;
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-global);
  color: var(--artdeco-fg-primary);
  transition: border-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:focus {
    outline: none;
    border-color: var(--artdeco-gold-primary);
  }
}

.input {
  padding: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2))
    calc(var(--artdeco-spacing-3) + (var(--artdeco-spacing-px) * 2));
  font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));

  &::placeholder {
    color: var(--artdeco-fg-muted);
  }
}

.select {
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  font-size: var(--artdeco-text-sm);
  cursor: pointer;
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
  width: calc((var(--artdeco-spacing-20) * 2) + var(--artdeco-spacing-10) + var(--artdeco-spacing-5));
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

.move-confirm-btn {
  width: 100%;
  margin-top: var(--artdeco-spacing-3);
}
</style>
