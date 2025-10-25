<template>
  <div class="strategy-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>策略列表</span>
          <el-button type="primary" @click="handleCreate">新建策略</el-button>
        </div>
      </template>

      <!-- 筛选区域 -->
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="活跃" value="active" />
            <el-option label="归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadStrategies">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 策略表格 -->
      <el-table
        v-loading="loading"
        :data="strategies"
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="策略名称" width="200" />
        <el-table-column prop="strategy_type" label="类型" width="150">
          <template #default="{ row }">
            <el-tag :type="getStrategyTypeTag(row.strategy_type)">
              {{ getStrategyTypeLabel(row.strategy_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click.stop="handleBacktest(row)">回测</el-button>
            <el-button link type="danger" @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadStrategies"
        @current-change="loadStrategies"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { strategyApi } from '@/api/strategy'

const router = useRouter()

// 数据状态
const loading = ref(false)
const strategies = ref([])

// 筛选表单
const filterForm = reactive({
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 加载策略列表
const loadStrategies = async () => {
  loading.value = true
  try {
    const response = await strategyApi.listStrategies({
      status: filterForm.status,
      page: pagination.page,
      page_size: pagination.pageSize
    })
    strategies.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载策略列表失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilter = () => {
  filterForm.status = ''
  pagination.page = 1
  loadStrategies()
}

// 新建策略
const handleCreate = () => {
  router.push('/strategy/create')
}

// 编辑策略
const handleEdit = (row: any) => {
  router.push(`/strategy/edit/${row.id}`)
}

// 行点击
const handleRowClick = (row: any) => {
  router.push(`/strategy/detail/${row.id}`)
}

// 执行回测
const handleBacktest = (row: any) => {
  router.push({
    path: '/backtest/execute',
    query: { strategy_id: row.id }
  })
}

// 删除策略
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除策略 "${row.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await strategyApi.deleteStrategy(row.id)
    ElMessage.success('删除成功')
    loadStrategies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 获取策略类型标签
const getStrategyTypeTag = (type: string) => {
  const tags: Record<string, string> = {
    model_based: 'success',
    rule_based: 'info',
    hybrid: 'warning'
  }
  return tags[type] || ''
}

const getStrategyTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    model_based: '模型驱动',
    rule_based: '规则驱动',
    hybrid: '混合策略'
  }
  return labels[type] || type
}

// 获取状态标签
const getStatusTag = (status: string) => {
  const tags: Record<string, string> = {
    draft: 'info',
    active: 'success',
    archived: 'danger'
  }
  return tags[status] || ''
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: '草稿',
    active: '活跃',
    archived: '归档'
  }
  return labels[status] || status
}

// 挂载时加载数据
onMounted(() => {
  loadStrategies()
})
</script>

<style scoped lang="scss">
.strategy-list {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .filter-form {
    margin-bottom: 20px;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
