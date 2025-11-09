<template>
  <div class="watchlist-group-manager">
    <!-- 分组列表头部 -->
    <div class="group-header">
      <h3>自选股分组</h3>
      <el-button
        type="primary"
        size="small"
        icon="Plus"
        @click="showCreateDialog"
      >
        新建分组
      </el-button>
    </div>

    <!-- 分组列表 -->
    <el-scrollbar height="500px">
      <div v-loading="loading" class="group-list">
        <div
          v-for="group in groups"
          :key="group.id"
          :class="['group-item', { active: group.id === modelValue }]"
          @click="selectGroup(group)"
        >
          <div class="group-info">
            <span class="group-name">{{ group.group_name }}</span>
            <el-tag v-if="showStockCount" size="small" type="info">
              {{ group.stock_count }}只
            </el-tag>
          </div>
          <div class="group-actions">
            <el-button
              v-if="group.group_name !== '默认分组'"
              size="small"
              icon="Edit"
              link
              @click.stop="showEditDialog(group)"
            />
            <el-button
              v-if="group.group_name !== '默认分组'"
              size="small"
              icon="Delete"
              link
              type="danger"
              @click.stop="confirmDelete(group)"
            />
          </div>
        </div>
      </div>
    </el-scrollbar>

    <!-- 创建/编辑分组对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建分组' : '编辑分组'"
      width="400px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="分组名称">
          <el-input
            v-model="form.group_name"
            placeholder="请输入分组名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// Props
const props = defineProps({
  modelValue: {
    type: Number,
    default: null
  },
  showStockCount: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'group-selected', 'group-created', 'group-updated', 'group-deleted'])

// API配置 - 使用相对路径让Vite代理处理
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
const getToken = () => localStorage.getItem('token')

// 数据
const groups = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('create') // 'create' or 'edit'
const form = ref({
  id: null,
  group_name: ''
})

// 获取分组列表
const fetchGroups = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/watchlist/groups`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    groups.value = response.data

    // 如果还没有选中分组且有分组，自动选中第一个
    if (!props.modelValue && groups.value.length > 0) {
      selectGroup(groups.value[0])
    }
  } catch (error) {
    ElMessage.error('获取分组失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 选择分组
const selectGroup = (group) => {
  emit('update:modelValue', group.id)
  emit('group-selected', group)
}

// 显示创建对话框
const showCreateDialog = () => {
  dialogMode.value = 'create'
  form.value = { id: null, group_name: '' }
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (group) => {
  dialogMode.value = 'edit'
  form.value = { id: group.id, group_name: group.group_name }
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  if (!form.value.group_name?.trim()) {
    ElMessage.warning('请输入分组名称')
    return
  }

  try {
    if (dialogMode.value === 'create') {
      // 创建分组
      const response = await axios.post(
        `${API_BASE}/watchlist/groups`,
        { group_name: form.value.group_name },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      )
      ElMessage.success('分组创建成功')
      emit('group-created', response.data.group)
    } else {
      // 更新分组
      await axios.put(
        `${API_BASE}/watchlist/groups/${form.value.id}`,
        { group_name: form.value.group_name },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      )
      ElMessage.success('分组更新成功')
      emit('group-updated', form.value)
    }

    dialogVisible.value = false
    await fetchGroups()
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 确认删除
const confirmDelete = async (group) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分组 "${group.group_name}" 吗？该分组下的所有股票也会被删除。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteGroup(group)
  } catch (error) {
    // 用户取消
  }
}

// 删除分组
const deleteGroup = async (group) => {
  try {
    await axios.delete(`${API_BASE}/watchlist/groups/${group.id}`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    ElMessage.success('分组删除成功')
    emit('group-deleted', group)

    // 如果删除的是当前选中的分组，切换到第一个分组
    if (props.modelValue === group.id && groups.value.length > 1) {
      const firstGroup = groups.value.find(g => g.id !== group.id)
      if (firstGroup) {
        selectGroup(firstGroup)
      }
    }

    await fetchGroups()
  } catch (error) {
    ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 暴露刷新方法给父组件
defineExpose({
  fetchGroups
})

// 组件挂载时获取分组
onMounted(() => {
  fetchGroups()
})
</script>

<style scoped>
.watchlist-group-manager {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.group-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.group-list {
  padding: 10px;
}

.group-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.group-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
}

.group-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}

.group-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.group-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.group-item.active .group-name {
  color: #409eff;
}

.group-actions {
  display: flex;
  gap: 5px;
  opacity: 0;
  transition: opacity 0.3s;
}

.group-item:hover .group-actions {
  opacity: 1;
}
</style>
