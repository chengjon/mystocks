# WebSocket性能优化和测试指南

## 📋 概述

本文档提供了WebSocket实时更新系统的性能优化策略和测试方法，确保在高并发和大数据量场景下的稳定性和性能。

## 🎯 性能指标

### 目标指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **连接建立时间** | < 5秒 | 从发起连接到连接成功的耗时 |
| **消息处理延迟** | < 100ms | 单条消息从接收到处理完成的耗时 |
| **批量消息平均延迟** | < 10ms | 批量消息的平均处理时间 |
| **重连成功率** | > 95% | 断线重连的成功率 |
| **内存泄漏** | 0 | 长时间运行不应有内存泄漏 |
| **CPU使用率** | < 10% | 正常负载下的CPU使用率 |
| **并发连接数** | > 100 | 支持的并发WebSocket连接数 |
| **心跳间隔** | 30秒 | 默认心跳保活间隔 |

## 🔧 性能优化策略

### 1. 连接优化

#### 1.1 连接池管理

```typescript
// 实现：维护WebSocket连接池，复用连接
class WebSocketPool {
  private connections: Map<string, WebSocket> = new Map()
  private maxConnections = 10

  getConnection(url: string): WebSocket | null {
    return this.connections.get(url) || null
  }

  addConnection(url: string, ws: WebSocket): void {
    if (this.connections.size >= this.maxConnections) {
      // 移除最旧的连接
      const oldestUrl = this.connections.keys().next().value
      this.connections.delete(oldestUrl)
    }

    this.connections.set(url, ws)
  }
}
```

#### 1.2 快速重连机制

```typescript
// 实现：指数退避 + 最大重试次数
const reconnectWithBackoff = (
  maxAttempts: number,
  baseDelay: number
) => {
  let attempts = 0

  const scheduleReconnect = () => {
    if (attempts >= maxAttempts) {
      console.error('Max reconnect attempts reached')
      return
    }

    const delay = Math.min(baseDelay * Math.pow(2, attempts), 5000)

    console.log(`Reconnecting in ${delay}ms (attempt ${attempts + 1}/${maxAttempts})`)

    setTimeout(() => {
      attempts++
      connect()
    }, delay)
  }

  return scheduleReconnect
}
```

### 2. 消息优化

#### 2.1 消息批处理

```typescript
// 实现：批量处理高频消息
class MessageBatcher {
  private messages: any[] = []
  private batchSize = 10
  private batchTimeout = 100 // ms

  addMessage(message: any) {
    this.messages.push(message)

    if (this.messages.length >= this.batchSize) {
      this.flush()
    } else {
      this.scheduleFlush()
    }
  }

  private scheduleFlush() {
    if (this.flushTimeout) return

    this.flushTimeout = setTimeout(() => {
      this.flush()
    }, this.batchTimeout)
  }

  private flush() {
    if (this.messages.length === 0) return

    const batch = this.messages.splice(0, this.messages.length)
    this.processBatch(batch)

    if (this.flushTimeout) {
      clearTimeout(this.flushTimeout)
      this.flushTimeout = null
    }
  }

  private processBatch(batch: any[]) {
    // 批量处理消息
    batch.forEach(msg => {
      this.processMessage(msg)
    })
  }
}
```

#### 2.2 消息队列

```typescript
// 实现：使用队列缓冲消息
class MessageQueue {
  private queue: any[] = []
  private processing = false

  enqueue(message: any) {
    this.queue.push(message)
    this.process()
  }

  private async process() {
    if (this.processing || this.queue.length === 0) return

    this.processing = true

    while (this.queue.length > 0) {
      const message = this.queue.shift()
      await this.processMessage(message)
    }

    this.processing = false
  }
}
```

### 3. 订阅优化

#### 3.1 订阅去重

```typescript
// 实现：避免重复订阅同一频道
class SubscriptionManager {
  private subscriptions: Map<string, Set<Function>> = new Map()

  subscribe(channel: string, callback: Function) {
    if (!this.subscriptions.has(channel)) {
      this.subscriptions.set(channel, new Set())
    }

    const callbacks = this.subscriptions.get(channel)!
    callbacks.add(callback)

    // 返回取消订阅函数
    return () => this.unsubscribe(channel, callback)
  }

  unsubscribe(channel: string, callback: Function) {
    const callbacks = this.subscriptions.get(channel)
    if (callbacks) {
      callbacks.delete(callback)

      // 如果该频道没有订阅者了，清理
      if (callbacks.size === 0) {
        this.subscriptions.delete(channel)
      }
    }
  }

  // 获取活跃订阅列表
  getActiveSubscriptions(): string[] {
    return Array.from(this.subscriptions.keys())
  }

  // 获取指定频道的订阅者数量
  getSubscriberCount(channel: string): number {
    return this.subscriptions.get(channel)?.size || 0
  }
}
```

#### 3.2 订阅缓存

```typescript
// 实现：缓存订阅结果
class SubscriptionCache {
  private cache: Map<string, { data: any; timestamp: number }> = new Map()
  private ttl = 60000 // 60秒

  get(channel: string): any | null {
    const cached = this.cache.get(channel)
    if (cached && Date.now() - cached.timestamp < this.ttl) {
      return cached.data
    }
    return null
  }

  set(channel: string, data: any): void {
    this.cache.set(channel, {
      data,
      timestamp: Date.now()
    })
  }

  clear(channel?: string): void {
    if (channel) {
      this.cache.delete(channel)
    } else {
      this.cache.clear()
    }
  }
}
```

### 4. 内存优化

#### 4.1 消息历史限制

```typescript
// 实现：限制消息历史记录数量
class MessageHistory {
  private history: any[] = []
  private maxSize = 100

  add(message: any) {
    this.history.push(message)

    // 限制历史记录大小
    if (this.history.length > this.maxSize) {
      this.history.shift() // 移除最旧的记录
    }
  }

  getRecent(count: number): any[] {
    return this.history.slice(-count)
  }

  clear() {
    this.history = []
  }
}
```

#### 4.2 定时器清理

```typescript
// 实现：清理未使用的定时器
class TimerManager {
  private timers: Map<string, NodeJS.Timeout> = new Map()

  setInterval(id: string, callback: Function, delay: number) {
    // 清除已存在的同名定时器
    this.clearInterval(id)

    const timer = setInterval(callback, delay)
    this.timers.set(id, timer)
  }

  clearInterval(id: string) {
    const timer = this.timers.get(id)
    if (timer) {
      clearInterval(timer)
      this.timers.delete(id)
    }
  }

  clearAll() {
    this.timers.forEach(timer => clearInterval(timer))
    this.timers.clear()
  }
}
```

### 5. 网络优化

#### 5.1 心跳优化

```typescript
// 实现：动态调整心跳间隔
class HeartbeatManager {
  private heartbeatInterval = 30000 // 默认30秒
  private lastActivity = Date.now()

  adjustHeartbeat() {
    const idleTime = Date.now() - this.lastActivity

    // 如果空闲时间较长，延长心跳间隔
    if (idleTime > 60000) { // 1分钟无活动
      this.heartbeatInterval = 60000 // 延长到60秒
    } else {
      this.heartbeatInterval = 30000 // 恢复默认30秒
    }

    return this.heartbeatInterval
  }

  recordActivity() {
    this.lastActivity = Date.now()
  }
}
```

#### 5.2 压缩传输

```typescript
// 实现：消息压缩（JSON → 压缩格式）
import pako from 'pako'

class MessageCompressor {
  compress(message: any): string {
    const json = JSON.stringify(message)
    const compressed = pako.deflate(json)
    return btoa(String.fromCharCode(...compressed))
  }

  decompress(data: string): any {
    const compressed = atob(data)
    const inflated = pako.inflate(
      new Uint8Array(compressed.split('').map(c => c.charCodeAt(0)))
    )
    return JSON.parse(new TextDecoder().decode(inflated))
  }
}
```

## 🧪 性能测试

### 测试套件

#### 1. 连接性能测试

```typescript
describe('WebSocket连接性能测试', () => {
  it('应该在5秒内建立连接', async () => {
    const ws = useWebSocket()
    const startTime = Date.now()

    ws.connect('ws://localhost:8000/api/ws')

    await waitForConnection(ws)

    const endTime = Date.now()
    const connectionTime = endTime - startTime

    expect(connectionTime).toBeLessThan(5000)
  })

  it('应该支持100个并发连接', async () => {
    const connections = Array.from({ length: 100 }, () => useWebSocket())

    await Promise.all(
      connections.map(ws => ws.connect('ws://localhost:8000/api/ws'))
    )

    const allConnected = connections.every(
      ws => ws.connectionState.value === 'connected'
    )

    expect(allConnected).toBe(true)
  })
})
```

#### 2. 消息吞吐量测试

```typescript
describe('WebSocket消息吞吐量测试', () => {
  it('应该处理1000条消息/秒', async () => {
    const ws = useWebSocket()
    ws.connect('ws://localhost:8000/api/ws')

    const messageCount = 1000
    const processed: any[] = []

    ws.subscribe('test', (data) => {
      processed.push(data)
    })

    const startTime = Date.now()

    for (let i = 0; i < messageCount; i++) {
      ws.send({ type: 'test', index: i })
    }

    await waitFor(() => processed.length === messageCount)

    const endTime = Date.now()
    const duration = endTime - startTime
    const throughput = messageCount / (duration / 1000)

    expect(throughput).toBeGreaterThan(1000) // > 1000 msg/s
  })
})
```

#### 3. 内存泄漏测试

```typescript
describe('WebSocket内存泄漏测试', () => {
  it('长时间运行不应该泄漏内存', async () => {
    const ws = useWebSocket()
    ws.connect('ws://localhost:8000/api/ws')

    const initialMemory = process.memoryUsage().heapUsed

    // 模拟长时间运行（1小时）
    for (let i = 0; i < 3600; i++) {
      // 每秒发送一次消息
      ws.send({ type: 'heartbeat', timestamp: Date.now() })
      await delay(1000)
    }

    const finalMemory = process.memoryUsage().heapUsed
    const memoryGrowth = finalMemory - initialMemory

    // 内存增长应该小于10MB
    expect(memoryGrowth).toBeLessThan(10 * 1024 * 1024)
  })
})
```

#### 4. 稳定性测试

```typescript
describe('WebSocket稳定性测试', () => {
  it('应该从网络错误中恢复', async () => {
    const ws = useWebSocket()
    ws.connect('ws://localhost:8000/api/ws')

    // 模拟网络中断
    ws.error.value = new Event('error')

    // 等待重连
    await waitFor(() => ws.connectionState.value === 'connected')

    expect(ws.connectionState.value).toBe('connected')
  })

  it('应该处理服务器重启', async () => {
    const ws = useWebSocket()
    ws.connect('ws://localhost:8000/api/ws')

    // 模拟服务器关闭
    ws.disconnect()

    // 等待服务器恢复
    await delay(5000)

    // 尝试重连
    ws.connect('ws://localhost:8000/api/ws')

    await waitFor(() => ws.connectionState.value === 'connected')

    expect(ws.connectionState.value).toBe('connected')
  })
})
```

### 测试工具

#### 1. 性能基准测试脚本

```bash
# 安装依赖
npm install --save-dev vitest @vitest/ui

# 运行性能测试
npm run test:performance

# 查看性能报告
npm run test:performance:report
```

#### 2. 负载测试

```typescript
// 使用Artillery进行负载测试
// load-test.yml

config:
  target: "ws://localhost:8000/api/ws"
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 300
      arrivalRate: 100
      name: "Sustained load"

scenarios:
  - name: "WebSocket Load Test"
    engine: ws
    flow:
      - send:
          payload: |
            {
              "type": "ping"
            }
      - think: 1
```

#### 3. 监控工具

```typescript
// 集成Performance API
class WebSocketMonitor {
  private metrics = {
    messagesReceived: 0,
    messagesSent: 0,
    reconnectCount: 0,
    errorCount: 0
  }

  recordMessageReceived() {
    this.metrics.messagesReceived++
  }

  recordMessageSent() {
    this.metrics.messagesSent++
  }

  recordReconnect() {
    this.metrics.reconnectCount++
  }

  recordError() {
    this.metrics.errorCount++
  }

  getMetrics() {
    return {
      ...this.metrics,
      messageRate: this.calculateMessageRate(),
      errorRate: this.calculateErrorRate()
    }
  }

  private calculateMessageRate() {
    // 计算消息速率
    return this.metrics.messagesReceived / (this.getUptime() / 1000)
  }

  private calculateErrorRate() {
    // 计算错误率
    return this.metrics.errorCount / this.metrics.messagesReceived
  }

  private getUptime() {
    // 获取运行时间
    return Date.now() - this.startTime
  }
}
```

## 📊 性能分析

### 1. Chrome DevTools分析

**步骤**：
1. 打开Chrome DevTools (F12)
2. 切换到"Performance"标签
3. 点击"Record"
4. 执行WebSocket操作
5. 停止录制
6. 分析火焰图

**关注指标**：
- JavaScript执行时间
- 布局重排次数
- 内存使用曲线
- 网络请求时间

### 2. Vue DevTools分析

**步骤**：
1. 安装Vue DevTools扩展
2. 切换到"Performance"标签
3. 记录组件性能
4. 分析组件渲染时间

### 3. Node.js Profiling

```bash
# 使用Clinic.js进行性能分析
npm install -g clinic
clinic doctor -- node server.js

# 使用Flamegraphs
npm install -g clinic
clinic flame -- node server.js
```

## 🚀 生产环境优化

### 1. 启用生产模式

```javascript
// vite.config.js
export default defineConfig({
  mode: 'production',
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true
      }
    }
  }
})
```

### 2. CDN加速

```html
<!-- 使用CDN加载WebSocket库 -->
<script src="https://cdn.jsdelivr.net/npm/ws/dist/ws.min.js"></script>
```

### 3. 服务端配置

```nginx
# Nginx WebSocket代理配置
location /api/ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}
```

### 4. 监控和告警

```typescript
// 集成监控系统
class WebSocketAlertManager {
  private thresholds = {
    reconnectRate: 0.1,      // 10%重连率
    errorRate: 0.05,         // 5%错误率
    messageLatency: 1000     // 1秒延迟
  }

  checkMetrics(metrics: any) {
    if (metrics.errorRate > this.thresholds.errorRate) {
      this.sendAlert('High error rate detected')
    }

    if (metrics.messageLatency > this.thresholds.messageLatency) {
      this.sendAlert('High message latency detected')
    }
  }

  private sendAlert(message: string) {
    // 发送告警通知
    console.error('[ALERT]', message)
  }
}
```

## 📚 最佳实践

### 1. 错误处理

```typescript
// 完整的错误处理
ws.subscribe('channel', (data) => {
  try {
    processData(data)
  } catch (error) {
    console.error('[WebSocket] Processing error:', error)
    // 上报错误
    errorReporter.report(error)
    // 继续处理，不中断连接
  }
})
```

### 2. 资源清理

```typescript
// 组件卸载时清理资源
onUnmounted(() => {
  // 取消所有订阅
  subscriptions.forEach(unsub => unsub())

  // 断开WebSocket连接
  ws.disconnect()

  // 清理定时器
  clearTimeout(heartbeatTimer)
  clearTimeout(reconnectTimer)
})
```

### 3. 日志记录

```typescript
// 分级日志记录
const logger = {
  debug: (...args: any[]) => {
    if (import.meta.env.DEV) {
      console.log('[WebSocket:DEBUG]', ...args)
    }
  },
  info: (...args: any[]) => {
    console.info('[WebSocket:INFO]', ...args)
  },
  warn: (...args: any[]) => {
    console.warn('[WebSocket:WARN]', ...args)
  },
  error: (...args: any[]) => {
    console.error('[WebSocket:ERROR]', ...args)
  }
}
```

## 🔗 相关文档

- [WebSocket Composable实现指南](./WEBSOCKET_COMPOSABLE_IMPLEMENTATION_GUIDE.md)
- [ArtDeco菜单数据获取实现指南](./ARTDECO_MENU_DATA_FETCHING_IMPLEMENTATION_GUIDE.md)
- [API映射验证文档](./ARTDECO_MENU_API_MAPPING.md)

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-19
**作者**: Claude Code
**状态**: ✅ 已实现
