# MyStocks API Enhancement Plan
# API增强实施计划

## Phase 1: SSE推送功能实施（优先级：高）

### 实施时间：2-3天

### 目标
为MyStocks系统添加Server-Sent Events（SSE）支持，实现实时推送功能，同时保持现有27个REST API不变。

---

## 实施步骤

### Step 1: 后端SSE端点实现（1天）

#### 1.1 创建SSE工具模块
文件：`/opt/claude/mystocks_spec/mystocks/utils/sse_utils.py`

```python
"""
SSE (Server-Sent Events) 工具模块
提供统一的SSE流生成和管理功能
"""
import json
import asyncio
from typing import AsyncGenerator, Dict, Any
from datetime import datetime


class SSEStream:
    """SSE流生成器基类"""

    @staticmethod
    def format_sse(data: Dict[str, Any], event: str = None) -> str:
        """
        格式化SSE消息

        Args:
            data: 要发送的数据字典
            event: 事件类型（可选）

        Returns:
            格式化的SSE消息字符串
        """
        message = ""
        if event:
            message += f"event: {event}\n"
        message += f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        return message

    @staticmethod
    async def heartbeat(interval: int = 30) -> AsyncGenerator[str, None]:
        """
        SSE心跳生成器

        Args:
            interval: 心跳间隔（秒）
        """
        while True:
            await asyncio.sleep(interval)
            yield SSEStream.format_sse(
                {"type": "heartbeat", "timestamp": datetime.now().isoformat()},
                event="heartbeat"
            )
```

#### 1.2 创建回测进度推送端点
文件：`/opt/claude/mystocks_spec/mystocks/web/backend/api/stream_api.py`

```python
"""
SSE流式API端点
提供实时数据推送功能
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
from utils.sse_utils import SSEStream

router = APIRouter(prefix="/api/stream", tags=["Stream"])


@router.get("/backtest/{task_id}")
async def stream_backtest_progress(task_id: str):
    """
    回测进度实时推送

    Args:
        task_id: 回测任务ID

    Returns:
        SSE流式响应
    """

    async def progress_generator() -> AsyncGenerator[str, None]:
        """生成回测进度事件流"""
        try:
            # TODO: 从database_manager获取实际回测进度
            # 当前为演示实现
            for progress in range(0, 101, 10):
                await asyncio.sleep(1)  # 模拟回测计算

                yield SSEStream.format_sse({
                    "task_id": task_id,
                    "progress": progress,
                    "status": "running" if progress < 100 else "completed",
                    "message": f"回测进度: {progress}%"
                }, event="progress")

            # 发送完成事件
            yield SSEStream.format_sse({
                "task_id": task_id,
                "status": "completed",
                "result_url": f"/api/backtest/results/{task_id}"
            }, event="complete")

        except Exception as e:
            yield SSEStream.format_sse({
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }, event="error")

    return StreamingResponse(
        progress_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用nginx缓冲
        }
    )


@router.get("/alerts")
async def stream_risk_alerts():
    """
    风险告警实时推送

    Returns:
        SSE流式响应
    """

    async def alert_generator() -> AsyncGenerator[str, None]:
        """生成风险告警事件流"""
        try:
            while True:
                # TODO: 从monitoring模块订阅实际告警
                # 当前为演示实现
                await asyncio.sleep(5)

                # 模拟告警数据
                alert = {
                    "timestamp": datetime.now().isoformat(),
                    "level": "warning",
                    "type": "position_risk",
                    "message": "持仓风险超过阈值",
                    "details": {
                        "symbol": "600000.SH",
                        "current_risk": 0.85,
                        "threshold": 0.80
                    }
                }

                yield SSEStream.format_sse(alert, event="alert")

        except asyncio.CancelledError:
            # 客户端断开连接
            pass
        except Exception as e:
            yield SSEStream.format_sse({
                "status": "error",
                "error": str(e)
            }, event="error")

    return StreamingResponse(
        alert_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get("/logs")
async def stream_system_logs(level: str = "INFO"):
    """
    系统日志实时推送（调试用）

    Args:
        level: 日志级别过滤 (DEBUG, INFO, WARNING, ERROR)

    Returns:
        SSE流式响应
    """

    async def log_generator() -> AsyncGenerator[str, None]:
        """生成日志事件流"""
        try:
            # TODO: 集成实际日志系统
            while True:
                await asyncio.sleep(2)

                # 模拟日志数据
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "level": level,
                    "module": "system",
                    "message": "系统运行正常"
                }

                yield SSEStream.format_sse(log_entry, event="log")

        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        log_generator(),
        media_type="text/event-stream"
    )
```

#### 1.3 注册路由
修改文件：`/opt/claude/mystocks_spec/mystocks/web/backend/main.py`

```python
# 在现有导入中添加
from api.stream_api import router as stream_router

# 在app初始化后添加
app.include_router(stream_router)
```

---

### Step 2: 前端SSE客户端集成（1天）

#### 2.1 创建SSE客户端工具
文件：`/opt/claude/mystocks_spec/mystocks/web/frontend/src/utils/sse-client.ts`

```typescript
/**
 * SSE客户端工具
 * 提供类型安全的EventSource封装
 */

export interface SSEOptions {
  onMessage?: (data: any) => void
  onError?: (error: Event) => void
  onOpen?: () => void
  reconnect?: boolean
  reconnectInterval?: number
}

export class SSEClient {
  private eventSource: EventSource | null = null
  private url: string
  private options: SSEOptions
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5

  constructor(url: string, options: SSEOptions = {}) {
    this.url = url
    this.options = {
      reconnect: true,
      reconnectInterval: 3000,
      ...options
    }
  }

  /**
   * 连接SSE流
   */
  connect(): void {
    if (this.eventSource) {
      this.disconnect()
    }

    this.eventSource = new EventSource(this.url)

    this.eventSource.onopen = () => {
      console.log(`[SSE] 连接成功: ${this.url}`)
      this.reconnectAttempts = 0
      this.options.onOpen?.()
    }

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.options.onMessage?.(data)
      } catch (error) {
        console.error('[SSE] 解析消息失败:', error)
      }
    }

    this.eventSource.onerror = (error) => {
      console.error('[SSE] 连接错误:', error)
      this.options.onError?.(error)

      // 自动重连
      if (this.options.reconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        setTimeout(() => {
          console.log(`[SSE] 重连尝试 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)
          this.connect()
        }, this.options.reconnectInterval)
      }
    }
  }

  /**
   * 监听特定事件类型
   */
  addEventListener(event: string, callback: (data: any) => void): void {
    this.eventSource?.addEventListener(event, (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        callback(data)
      } catch (error) {
        console.error(`[SSE] 解析${event}事件失败:`, error)
      }
    })
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
      console.log(`[SSE] 连接已断开: ${this.url}`)
    }
  }

  /**
   * 获取连接状态
   */
  get readyState(): number {
    return this.eventSource?.readyState ?? EventSource.CLOSED
  }
}
```

#### 2.2 创建回测进度监控组件
文件：`/opt/claude/mystocks_spec/mystocks/web/frontend/src/components/BacktestProgress.vue`

```vue
<template>
  <el-card class="backtest-progress">
    <template #header>
      <span>回测进度监控</span>
      <el-tag :type="statusType" size="small" style="float: right">
        {{ statusText }}
      </el-tag>
    </template>

    <el-progress
      :percentage="progress"
      :status="progressStatus"
      :stroke-width="20"
    />

    <div class="progress-info">
      <p>任务ID: {{ taskId }}</p>
      <p>进度: {{ progress }}%</p>
      <p>消息: {{ message }}</p>
    </div>

    <el-button
      v-if="status === 'completed'"
      type="primary"
      @click="viewResults"
    >
      查看回测结果
    </el-button>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { SSEClient } from '@/utils/sse-client'
import { ElMessage } from 'element-plus'

interface Props {
  taskId: string
}

const props = defineProps<Props>()

const progress = ref(0)
const status = ref<'pending' | 'running' | 'completed' | 'error'>('pending')
const message = ref('等待开始...')
let sseClient: SSEClient | null = null

const statusType = computed(() => {
  const typeMap = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    error: 'danger'
  }
  return typeMap[status.value] || 'info'
})

const statusText = computed(() => {
  const textMap = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    error: '失败'
  }
  return textMap[status.value] || '未知'
})

const progressStatus = computed(() => {
  if (status.value === 'error') return 'exception'
  if (status.value === 'completed') return 'success'
  return undefined
})

onMounted(() => {
  // 连接SSE流
  sseClient = new SSEClient(`/api/stream/backtest/${props.taskId}`, {
    onOpen: () => {
      status.value = 'running'
      ElMessage.success('已连接到回测进度流')
    },
    onError: (error) => {
      status.value = 'error'
      message.value = '连接失败，请刷新页面重试'
      ElMessage.error('SSE连接错误')
    }
  })

  // 监听进度事件
  sseClient.addEventListener('progress', (data) => {
    progress.value = data.progress
    status.value = data.status
    message.value = data.message
  })

  // 监听完成事件
  sseClient.addEventListener('complete', (data) => {
    status.value = 'completed'
    message.value = '回测完成！'
    ElMessage.success('回测已完成，可查看结果')
  })

  // 监听错误事件
  sseClient.addEventListener('error', (data) => {
    status.value = 'error'
    message.value = `错误: ${data.error}`
    ElMessage.error(message.value)
  })

  sseClient.connect()
})

onUnmounted(() => {
  sseClient?.disconnect()
})

const viewResults = () => {
  // 跳转到结果页面
  window.location.href = `/backtest/results/${props.taskId}`
}
</script>

<style scoped>
.backtest-progress {
  max-width: 600px;
  margin: 20px auto;
}

.progress-info {
  margin: 20px 0;
  font-size: 14px;
  color: #606266;
}

.progress-info p {
  margin: 8px 0;
}
</style>
```

#### 2.3 创建告警监控组件
文件：`/opt/claude/mystocks_spec/mystocks/web/frontend/src/components/AlertMonitor.vue`

```vue
<template>
  <el-card class="alert-monitor">
    <template #header>
      <span>实时风险告警</span>
      <el-badge :value="unreadCount" :max="99" class="badge">
        <el-icon><Bell /></el-icon>
      </el-badge>
    </template>

    <el-timeline>
      <el-timeline-item
        v-for="alert in alerts"
        :key="alert.id"
        :timestamp="alert.timestamp"
        :type="getAlertType(alert.level)"
      >
        <el-alert
          :title="alert.message"
          :type="getAlertType(alert.level)"
          :closable="false"
          show-icon
        >
          <template #default>
            <pre>{{ JSON.stringify(alert.details, null, 2) }}</pre>
          </template>
        </el-alert>
      </el-timeline-item>
    </el-timeline>

    <el-empty v-if="alerts.length === 0" description="暂无告警" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { SSEClient } from '@/utils/sse-client'
import { ElNotification } from 'element-plus'
import { Bell } from '@element-plus/icons-vue'

interface Alert {
  id: string
  timestamp: string
  level: 'info' | 'warning' | 'error'
  type: string
  message: string
  details: any
}

const alerts = ref<Alert[]>([])
const unreadCount = ref(0)
let sseClient: SSEClient | null = null

const getAlertType = (level: string) => {
  const typeMap: Record<string, any> = {
    info: 'primary',
    warning: 'warning',
    error: 'danger'
  }
  return typeMap[level] || 'info'
}

onMounted(() => {
  sseClient = new SSEClient('/api/stream/alerts')

  sseClient.addEventListener('alert', (data) => {
    const alert: Alert = {
      id: Date.now().toString(),
      ...data
    }

    // 添加到列表（最新在前）
    alerts.value.unshift(alert)

    // 限制列表长度
    if (alerts.value.length > 50) {
      alerts.value = alerts.value.slice(0, 50)
    }

    // 未读计数
    unreadCount.value++

    // 桌面通知
    ElNotification({
      title: '风险告警',
      message: alert.message,
      type: getAlertType(alert.level),
      duration: 5000
    })

    // 播放提示音（可选）
    if (alert.level === 'error') {
      playAlertSound()
    }
  })

  sseClient.connect()
})

onUnmounted(() => {
  sseClient?.disconnect()
})

const playAlertSound = () => {
  // 可选：播放告警提示音
  const audio = new Audio('/alert.mp3')
  audio.play().catch(() => {
    // 浏览器可能阻止自动播放
    console.log('告警提示音播放失败')
  })
}
</script>

<style scoped>
.alert-monitor {
  height: 600px;
  overflow-y: auto;
}

.badge {
  float: right;
  font-size: 20px;
}

pre {
  font-size: 12px;
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}
</style>
```

---

### Step 3: 测试与文档（0.5天）

#### 3.1 创建测试脚本
文件：`/opt/claude/mystocks_spec/mystocks/tests/test_sse_api.py`

```python
"""
SSE API测试脚本
验证SSE端点功能正常
"""
import asyncio
import aiohttp


async def test_backtest_progress_stream():
    """测试回测进度推送"""
    url = "http://localhost:8000/api/stream/backtest/test-task-123"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"连接状态: {response.status}")
            assert response.status == 200

            # 读取前5个事件
            count = 0
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data:'):
                    print(f"收到数据: {line}")
                    count += 1
                    if count >= 5:
                        break

            print("✅ 回测进度推送测试通过")


async def test_alert_stream():
    """测试告警推送"""
    url = "http://localhost:8000/api/stream/alerts"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            assert response.status == 200

            # 读取10秒
            async with asyncio.timeout(10):
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data:'):
                        print(f"收到告警: {line}")

            print("✅ 告警推送测试通过")


if __name__ == "__main__":
    asyncio.run(test_backtest_progress_stream())
    # asyncio.run(test_alert_stream())  # 需要较长时间
```

#### 3.2 更新API文档
在`README.md`中添加：

```markdown
## SSE实时推送API

### 1. 回测进度推送
**端点**: `GET /api/stream/backtest/{task_id}`

**示例**:
```javascript
const eventSource = new EventSource('/api/stream/backtest/my-task-123')

eventSource.addEventListener('progress', (event) => {
  const data = JSON.parse(event.data)
  console.log(`进度: ${data.progress}%`)
})

eventSource.addEventListener('complete', (event) => {
  const data = JSON.parse(event.data)
  console.log('回测完成！结果URL:', data.result_url)
  eventSource.close()
})
```

### 2. 风险告警推送
**端点**: `GET /api/stream/alerts`

**示例**:
```javascript
const eventSource = new EventSource('/api/stream/alerts')

eventSource.addEventListener('alert', (event) => {
  const alert = JSON.parse(event.data)
  if (alert.level === 'error') {
    showNotification(alert.message)
  }
})
```

### 3. 系统日志流
**端点**: `GET /api/stream/logs?level=INFO`

**参数**:
- `level`: 日志级别过滤 (DEBUG, INFO, WARNING, ERROR)
```

---

## Phase 2: 性能优化与监控（可选，3-6个月后）

### 待评估指标
- API响应时间（P50, P95, P99）
- SSE连接数和稳定性
- 数据库查询性能
- 前端渲染性能

### 优化方向
1. **数据库层**：添加索引、查询优化
2. **缓存层**：Redis缓存热点数据（如需要）
3. **CDN**：静态资源加速
4. **负载均衡**：Nginx反向代理（多实例部署）

**原则**：根据实际监控数据决策，避免过早优化

---

## 附录：技术决策记录

### 为什么选择SSE而不是WebSocket？

| 维度 | SSE | WebSocket |
|------|-----|-----------|
| 实现复杂度 | ⭐ (极简) | ⭐⭐⭐ (中等) |
| 浏览器兼容性 | 100% (IE除外) | 100% |
| 自动重连 | ✅ 内置 | ❌ 需手动实现 |
| 调试难度 | ⭐ (DevTools直接查看) | ⭐⭐⭐ (需专用工具) |
| 适用场景 | 单向推送 | 双向交互 |
| 本项目需求匹配 | ✅ 90%场景只需推送 | ⚠️ 双向交互场景少 |

**结论**：SSE完全满足当前需求，WebSocket是过度设计。

### 后续可能的WebSocket应用场景
- 策略实时调试（需要双向交互修改参数）
- 多人协作编辑策略
- 实时聊天客服

当这些需求出现时，再渐进式添加WebSocket端点。

---

## 验收标准

### 功能验收
- [ ] 回测进度推送端点正常工作
- [ ] 告警推送端点正常工作
- [ ] 前端组件正确接收和显示SSE数据
- [ ] 断线自动重连功能正常
- [ ] 错误处理机制完善

### 性能验收
- [ ] SSE连接建立时间 < 500ms
- [ ] 单服务器支持 >100 并发SSE连接
- [ ] 内存占用增长 < 50MB（100连接）

### 文档验收
- [ ] API文档完整（包含示例代码）
- [ ] 前端组件使用文档完整
- [ ] 测试脚本可运行

---

## 参考资料

- [FastAPI StreamingResponse文档](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [MDN EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [SSE规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)
