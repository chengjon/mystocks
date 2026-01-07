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
                    <td>{{ row.display_name }}</td>
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
              v-for="group in groups.filter(g => g.id !== currentGroupId)"
              :key="group.id"
              :value="group.id"
            >
              {{ group.group_name }}
            </option>
          </select>
          <button
            style="width: 100%; margin-top: 10px;"
            @click="moveStock"
          >
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

interface Props {
  groups: any[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'get-quote': [stock: any]
  'groups-changed': []
  'api-tested': [feature: string]
}>()

const groupManagerRef = ref<any>(null)
const currentGroupId = ref<any>(null)
const currentGroupName = ref('')
const currentGroupStocks = ref<any[]>([])
const watchlistLoading = ref(false)
const moveToGroupId = ref<any>(null)
const showMovePopover = ref(false)
const selectedStock = ref<any>(null)

const handleGroupSelected = (group: any) => {
  currentGroupId.value = group.id
  currentGroupName.value = group.group_name
  fetchGroupStocks()
}

const handleGroupCreated = () => emit('groups-changed')
const handleGroupUpdated = (group: any) => {
  if (currentGroupId.value === group.id) {
    currentGroupName.value = group.group_name
  }
  emit('groups-changed')
}
const handleGroupDeleted = () => emit('groups-changed')

const fetchGroupStocks = async () => {
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
  } catch (error: any) {
    ElMessage.error('获取分组股票失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    watchlistLoading.value = false
  }
}

const openMovePopover = (stock: any) => {
  selectedStock.value = stock
  showMovePopover.value = true
}

const closeMovePopover = () => {
  showMovePopover.value = false
  moveToGroupId.value = null
}

const moveStock = async () => {
  if (!moveToGroupId.value) {
    ElMessage.warning('请选择目标分组')
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
  } catch (error: any) {
    ElMessage.error('移动失败: ' + (error.response?.data?.detail || error.message))
  }
}

const clearCurrentGroup = async () => {
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
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const removeFromWatchlist = async (stock: any) => {
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
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const updateNotes = async (stock: any) => {
  try {
    const token = localStorage.getItem('token') || ''
    const API_BASE = '/api'
    await axios.put(
      `${API_BASE}/watchlist/notes/${stock.symbol}`,
      { notes: stock.notes },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    ElMessage.success('备注已更新')
  } catch (error: any) {
    ElMessage.error('更新失败: ' + (error.response?.data?.detail || error.message))
  }
}
</script>

<style scoped lang="scss">

.watchlist-section {
  padding: 10px 0;
}

.watchlist-grid {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 20px;
}

.sidebar {
  min-height: 500px;
}

.main-content {
  min-height: 500px;
}

.group-stocks {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 20px;
  min-height: 500px;
}

.group-stocks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid var(--primary);

  h4 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--primary);
  }
}

.actions {
  display: flex;
  gap: 10px;
}

.table-wrapper {
  min-height: 400px;
}

.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: var(--primary);
  }
}

.select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  background: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: var(--primary);
  }
}

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

  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  width: 220px;
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
    padding: 0;
    line-height: 1;

    &:hover {
      color: var(--text-primary);
    }
  }

  .popover-content {
    padding: 16px;
  }
}
</style>
