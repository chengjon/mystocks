<template>
  <div class="page-config-example">
    <el-card v-if="pageConfig">
      <template #header>
        <div class="card-header">
          <span>{{ pageConfig.description }}</span>
          <el-tag :type="isStandardPage ? 'success' : 'info'" size="small">
            {{ isStandardPage ? '标准页面' : '单体组件' }}
          </el-tag>
        </div>
      </template>

      <div class="config-info">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="路由名称">
            <code>{{ routeName }}</code>
          </el-descriptions-item>
          <el-descriptions-item v-if="isStandardPage" label="API端点">
            <code>{{ standardPageConfig?.apiEndpoint }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="WebSocket频道">
            <el-tag v-if="isStandardPage && standardPageConfig?.wsChannel" type="warning" size="small">
              {{ standardPageConfig.wsChannel }}
            </el-tag>
            <span v-else class="text-muted">不需要</span>
          </el-descriptions-item>
          <el-descriptions-item label="页面类型">
            <el-icon v-if="isStandardPage" color="#67C23A">
              <CircleCheck />
            </el-icon>
            <el-icon v-else color="#909399">
              <CircleClose />
            </el-icon>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="actions">
        <el-button type="primary" @click="loadData" :loading="loading">
          加载数据
        </el-button>
        <el-button v-if="isStandardPage && standardPageConfig?.wsChannel" @click="toggleWebSocket">
          {{ wsConnected ? '断开' : '连接' }} WebSocket
        </el-button>
      </div>

      <div v-if="data" class="data-display">
        <h4>返回数据：</h4>
        <pre>{{ JSON.stringify(data, null, 2) }}</pre>
      </div>

      <div v-if="error" class="error-display">
        <el-alert type="error" :title="error" :closable="false" />
      </div>
    </el-card>

    <el-empty v-else description="未配置的路由" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPageConfig, isRouteName, isStandardConfig, type PageConfig, type StandardPageConfig } from '@/config/pageConfig'
import axios from 'axios'

// 路由相关
const route = useRoute()
const routeName = computed(() => route.name as string)

// 页面配置
const pageConfig = computed(() => getPageConfig(routeName.value))
const isStandardPage = computed(() => pageConfig.value?.type === 'page')
const standardPageConfig = computed((): StandardPageConfig | null =>
  pageConfig.value && isStandardConfig(pageConfig.value) ? pageConfig.value : null
)

// 数据状态
const data = ref<unknown>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const wsConnected = ref(false)

// WebSocket实例（示例）
let wsInstance: WebSocket | null = null

/**
 * 加载数据 - 使用统一配置的API端点
 */
const loadData = async () => {
  if (!pageConfig.value) {
    error.value = '未配置的路由'
    return
  }

  loading.value = true
  error.value = null

  try {
    // ✅ 使用统一配置的API端点（避免硬编码）
    const apiEndpoint = standardPageConfig.value?.apiEndpoint || '/api/default'
    const response = await axios.get(apiEndpoint)
    data.value = response.data

    console.log(`✅ 数据加载成功: ${apiEndpoint}`)
  } catch (err: unknown) {
    error.value = (err as Error).message || '数据加载失败'
    console.error(`❌ 数据加载失败`, err)
  } finally {
    loading.value = false
  }
}

/**
 * 切换WebSocket连接 - 使用统一配置的频道
 */
const toggleWebSocket = () => {
  const wsChannel = isStandardPage.value ? (standardPageConfig.value as StandardPageConfig | null)?.wsChannel : null
  if (!wsChannel) {
    console.warn('当前路由不需要WebSocket连接')
    return
  }

  if (wsConnected.value) {
    // 断开连接
    wsInstance?.close()
    wsInstance = null
    wsConnected.value = false
    console.log('🔇 WebSocket已断开')
  } else {
    // 建立连接（示例URL，实际应从环境变量读取）
    const wsUrl = `ws://localhost:8000/ws/${wsChannel}`
    wsInstance = new WebSocket(wsUrl)

    wsInstance.onopen = () => {
      wsConnected.value = true
      console.log(`✅ WebSocket已连接: ${wsChannel}`)
    }

    wsInstance.onmessage = (event) => {
      const message = JSON.parse(event.data)
      console.log('📨 收到WebSocket消息:', message)
      data.value = message
    }

    wsInstance.onerror = (err) => {
      console.error('❌ WebSocket错误:', err)
    }

    wsInstance.onclose = () => {
      wsConnected.value = false
      console.log('🔇 WebSocket已断开')
    }
  }
}

/**
 * 组件挂载时验证路由
 */
onMounted(() => {
  // ✅ 类型安全的路由验证
  if (!isRouteName(routeName.value)) {
    console.warn(`⚠️ 未配置的路由: ${routeName.value}`)
    error.value = `未配置的路由: ${routeName.value}`
  } else {
    console.log(`✅ 路由配置有效: ${routeName.value}`)
    console.log(`📋 配置信息:`, pageConfig.value)
  }
})

// 组件卸载时清理WebSocket
import { onUnmounted } from 'vue'
onUnmounted(() => {
  wsInstance?.close()
})
</script>

<style scoped>
.page-config-example {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-info {
  margin: 20px 0;
}

.actions {
  margin: 20px 0;
  display: flex;
  gap: 10px;
}

.data-display {
  margin-top: 20px;
}

.data-display h4 {
  margin-bottom: 10px;
  color: #303133;
}

.data-display pre {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 400px;
}

.error-display {
  margin-top: 20px;
}

.text-muted {
  color: #909399;
}

code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #e83e8c;
}
</style>
