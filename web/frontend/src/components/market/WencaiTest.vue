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

<style scoped lang="scss">
.test-page {
  padding: var(--artdeco-spacing-10);
  text-align: center;
}

h1 {
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-spacing-5);
  font-family: var(--artdeco-font-heading, var(--font-display));
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

p {
  font-size: var(--artdeco-text-base);
  margin: calc(var(--artdeco-spacing-5) / 2) 0;
  color: var(--artdeco-fg-primary);
}
</style>
