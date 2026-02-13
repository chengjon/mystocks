<template>
  <div class="websocket-config-example">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>WebSocket解耦示例</span>
          <el-tag :type="isConnected ? 'success' : 'info'" size="small">
            {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
        </div>
      </template>

      <!-- 连接状态 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="连接状态">
          <el-tag :type="connectionStateType" size="small">
            {{ connectionStateLabel }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="订阅数量">
          <el-tag type="primary" size="small">
            {{ subscriptionStats.subscribed }} / {{ subscriptionStats.total }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 控制按钮 -->
      <div class="controls">
        <el-space>
          <el-button
            type="primary"
            @click="connect"
            :disabled="isConnected"
          >
            连接WebSocket
          </el-button>
          <el-button
            @click="disconnect"
            :disabled="!isConnected"
          >
            断开连接
          </el-button>
          <el-button
            @click="subscribeToRoute"
            :disabled="!isConnected || !selectedRoute"
          >
            订阅选中路由
          </el-button>
          <el-button
            @click="unsubscribeFromRoute"
            :disabled="!isConnected || !selectedRoute"
          >
            取消订阅
          </el-button>
          <el-button
            type="success"
            @click="subscribeAll"
            :disabled="!isConnected"
          >
            订阅全部路由
          </el-button>
        </el-space>
      </div>

      <!-- 路由选择 -->
      <div class="route-selector">
        <h4>选择路由（仅显示需要WebSocket的路由）:</h4>
        <el-select
          v-model="selectedRoute"
          placeholder="请选择路由"
          style="width: 100%"
          clearable
        >
          <el-option
            v-for="info in allWebSocketRoutes"
            :key="info.routeName"
            :label="info.routeName"
            :value="info.routeName"
          >
            <span style="float: left">{{ info.routeName }}</span>
            <span style="float: right; color: #8492a6; font-size: 13px">
              <el-tag size="small" type="warning">{{ info.channel }}</el-tag>
              <span style="margin-left: 10px">{{ info.description }}</span>
            </span>
          </el-option>
        </el-select>
      </div>

      <!-- 已订阅路由 -->
      <div v-if="subscribedRoutes.length > 0" class="subscribed-routes">
        <h4>已订阅路由:</h4>
        <el-space wrap>
          <el-tag
            v-for="routeName in subscribedRoutes"
            :key="routeName"
            closable
            @close="unsubscribeRoute(routeName)"
          >
            {{ routeName }}
          </el-tag>
        </el-space>
      </div>

      <!-- 消息显示 -->
      <div v-if="lastMessage" class="message-display">
        <h4>最新消息:</h4>
        <el-alert type="info" :closable="false">
          <pre>{{ JSON.stringify(lastMessage, null, 2) }}</pre>
        </el-alert>
      </div>

      <!-- 错误显示 -->
      <div v-if="error" class="error-display">
        <h4>错误信息:</h4>
        <el-alert type="error" :closable="false">
          {{ error }}
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocketWithConfig } from '@/composables/useWebSocketWithConfig'
import type { PageConfig } from '@/config/pageConfig'

// WebSocket功能
const {
  connectionState,
  isConnected,
  lastMessage,
  error,
  subscribedRoutes,
  subscriptionStats,
  getAllWebSocketChannels,
  subscribeByRoute,
  unsubscribeByRoute,
  subscribeAllWebSocketRoutes,
  connect,
  disconnect
} = useWebSocketWithConfig()

// 所有WebSocket路由信息
const allWebSocketRoutes = ref(getAllWebSocketChannels())

// 选中的路由
const selectedRoute = ref<string>('')

// 订阅处理器存储
const unsubscribers = ref<Map<string, () => void>>(new Map())
const unsubscribeAll = ref<(() => void) | null>(null)

/**
 * 连接状态标签类型
 */
const connectionStateType = computed(() => {
  switch (connectionState.value) {
    case 'connected': return 'success'
    case 'connecting': return 'warning'
    case 'error': return 'danger'
    default: return 'info'
  }
})

/**
 * 连接状态标签文本
 */
const connectionStateLabel = computed(() => {
  const labels = {
    disconnected: '已断开',
    connecting: '连接中',
    connected: '已连接',
    error: '错误'
  }
  return labels[connectionState.value] || connectionState.value
})

/**
 * 订阅选中的路由
 */
const subscribeToRoute = () => {
  if (!selectedRoute.value) {
    console.warn('请先选择路由')
    return
  }

  // 检查是否已订阅
  if (unsubscribers.value.has(selectedRoute.value)) {
    console.warn(`路由 ${selectedRoute.value} 已经订阅过了`)
    return
  }

  console.log(`订阅路由: ${selectedRoute.value}`)

  // ✅ 使用统一配置的订阅方法（无硬编码）
  const unsubscribe = subscribeByRoute(selectedRoute.value, handleMessage)

  // 保存取消订阅函数
  unsubscribers.value.set(selectedRoute.value, unsubscribe)
}

/**
 * 取消订阅选中的路由
 */
const unsubscribeFromRoute = () => {
  if (!selectedRoute.value) {
    console.warn('请先选择路由')
    return
  }

  unsubscribeRoute(selectedRoute.value)
}

/**
 * 取消订阅指定路由
 */
const unsubscribeRoute = (routeName: string) => {
  const unsubscribe = unsubscribers.value.get(routeName)

  if (!unsubscribe) {
    console.warn(`路由 ${routeName} 未订阅`)
    return
  }

  console.log(`取消订阅路由: ${routeName}`)

  // 调用取消订阅函数
  unsubscribe()
  unsubscribers.value.delete(routeName)
}

/**
 * 订阅所有WebSocket路由
 */
const subscribeAll = () => {
  console.log('订阅所有WebSocket路由')

  // ✅ 批量订阅所有WebSocket路由（无硬编码）
  const unsubscribe = subscribeAllWebSocketRoutes(handleMessage)

  // 保存取消订阅函数
  unsubscribeAll.value = unsubscribe
}

/**
 * 消息处理函数
 */
const handleMessage = (data: any) => {
  console.log('📨 收到WebSocket消息:', data)

  // 可以在这里添加业务逻辑
  // 例如：更新状态、触发事件等
}

/**
 * 组件挂载时自动连接
 */
onMounted(() => {
  console.log('🚀 WebSocket示例组件已挂载')

  // 自动连接WebSocket
  connect()
})

/**
 * 组件卸载时清理
 */
onUnmounted(() => {
  console.log('🗑️ WebSocket示例组件将卸载')

  // 取消所有订阅
  unsubscribers.value.forEach(unsub => unsub())
  unsubscribers.value.clear()

  // 取消批量订阅
  unsubscribeAll.value?.()

  // 断开连接
  disconnect()
})
</script>

<style scoped>
.websocket-config-example {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.controls {
  margin: 20px 0;
}

.route-selector {
  margin: 20px 0;
}

.route-selector h4 {
  margin-bottom: 10px;
  color: #303133;
}

.channel-badge {
  margin-left: 10px;
}

.description {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.subscribed-routes {
  margin: 20px 0;
}

.subscribed-routes h4 {
  margin-bottom: 10px;
  color: #303133;
}

.message-display,
.error-display {
  margin: 20px 0;
}

.message-display h4,
.error-display h4 {
  margin-bottom: 10px;
  color: #303133;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
