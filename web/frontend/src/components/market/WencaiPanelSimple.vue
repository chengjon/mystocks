<template>
  <div class="wencai-panel">
    <h1>问财筛选功能</h1>
    <p>正在加载...</p>
    <el-button @click="testLoad">测试加载</el-button>
    <div v-if="loaded">
      <p>加载成功！查询数量: {{ queries.length }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { API_ENDPOINTS } from '@/config/api'

const queries = ref([])
const loaded = ref(false)

const testLoad = async () => {
  try {
    ElMessage.info('开始加载查询列表...')
    console.log('API endpoint:', API_ENDPOINTS.wencai.queries)

    const response = await fetch(API_ENDPOINTS.wencai.queries)
    console.log('Response status:', response.status)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    console.log('Response data:', data)

    queries.value = data.queries || []
    loaded.value = true

    ElMessage.success(`成功加载 ${queries.value.length} 个查询`)
  } catch (error) {
    console.error('Load error:', error)
    ElMessage.error('加载失败: ' + error.message)
  }
}

onMounted(() => {
  console.log('WencaiPanelSimple mounted')
  testLoad()
})
</script>

<style scoped>
.wencai-panel {
  padding: 20px;
}
</style>
