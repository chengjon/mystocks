<template>
  <div class="test-page">
    <h1>问财筛选测试页面</h1>
    <p>如果您看到这个页面，说明路由配置正确！</p>
    <p>当前路径: {{ $route.path }}</p>
    <el-button @click="testApi">测试 API</el-button>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'

const testApi = async () => {
  try {
    const response = await fetch('/api/market/wencai/health')
    const data = await response.json()
    ElMessage.success(`API 正常：${JSON.stringify(data)}`)
  } catch (error) {
    ElMessage.error(`API 错误：${error.message}`)
  }
}
</script>

<style scoped>
.test-page {
  padding: 40px;
  text-align: center;
}

h1 {
  color: #409eff;
  margin-bottom: 20px;
}

p {
  font-size: 16px;
  margin: 10px 0;
}
</style>
