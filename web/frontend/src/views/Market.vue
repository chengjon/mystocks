<template>
  <div class="market">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>市场行情</span>
          <el-button type="primary" size="small" @click="handleRefresh" :loading="loading">刷新</el-button>
        </div>
      </template>
      <el-empty description="功能开发中..." />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)

const handleRefresh = async () => {
  loading.value = true
  try {
    // TODO: 添加实际的刷新逻辑
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.market {
  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
