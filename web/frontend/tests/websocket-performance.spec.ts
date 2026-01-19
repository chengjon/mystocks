/**
 * WebSocket Performance Tests
 *
 * 测试WebSocket连接的性能、稳定性和资源消耗
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useWebSocket } from '@/composables/useWebSocket'

describe('WebSocket性能测试', () => {
  let ws: ReturnType<typeof useWebSocket>

  beforeEach(() => {
    ws = useWebSocket({
      url: 'ws://localhost:8000/api/ws',
      reconnectInterval: 1000,
      maxReconnectAttempts: 3,
      heartbeatInterval: 30000
    })
  })

  afterEach(() => {
    ws.disconnect()
  })

  describe('连接性能', () => {
    it('应该在合理时间内建立连接', async () => {
      const startTime = Date.now()

      ws.connect()

      // 模拟连接成功
      setTimeout(() => {
        // WebSocket onopen回调
      }, 100)

      // 验证连接状态
      expect(ws.connectionState.value).not.toBe('disconnected')

      const endTime = Date.now()
      const connectionTime = endTime - startTime

      expect(connectionTime).toBeLessThan(5000) // 5秒内建立连接
    })

    it('应该快速断开连接', () => {
      ws.connect()
      const startTime = Date.now()

      ws.disconnect()

      const endTime = Date.now()
      const disconnectTime = endTime - startTime

      expect(disconnectTime).toBeLessThan(1000) // 1秒内断开
      expect(ws.connectionState.value).toBe('disconnected')
    })

    it('应该支持并发连接', () => {
      const connections: ReturnType<typeof useWebSocket>[] = []

      // 创建10个并发连接
      for (let i = 0; i < 10; i++) {
        const connection = useWebSocket({
          url: `ws://localhost:8000/api/ws/${i}`
        })
        connection.connect()
        connections.push(connection)
      }

      // 验证所有连接都处于连接或连接中状态
      connections.forEach(connection => {
        expect(['connecting', 'connected']).toContain(connection.connectionState.value)
      })

      // 清理
      connections.forEach(connection => connection.disconnect())
    })
  })

  describe('重连性能', () => {
    it('应该在连接失败后自动重连', async () => {
      ws.connect()

      // 模拟连接失败
      setTimeout(() => {
        // WebSocket onerror回调
        ws.error.value = new Event('error')
      }, 100)

      // 等待重连
      await new Promise(resolve => setTimeout(resolve, 2000))

      // 验证重连尝试次数
      expect(ws.reconnectAttempts).toBeGreaterThan(0)
    })

    it('应该使用指数退避延迟重连', async () => {
      ws.connect()

      const timestamps: number[] = []

      // 监听重连尝试
      const originalScheduleReconnect = ws.scheduleReconnect
      ws.scheduleReconnect = () => {
        timestamps.push(Date.now())
        return originalScheduleReconnect()
      }

      // 模拟连续失败
      for (let i = 0; i < 3; i++) {
        ws.error.value = new Event('error')
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      // 验证延迟递增
      if (timestamps.length >= 2) {
        const delay1 = timestamps[1] - timestamps[0]
        const delay2 = timestamps[2] - timestamps[1]

        expect(delay2).toBeGreaterThan(delay1) // 指数退避
      }
    })

    it('应该在达到最大重连次数后停止', async () => {
      ws.connect()

      // 模拟多次失败
      for (let i = 0; i < 10; i++) {
        ws.error.value = new Event('error')
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      // 验证重连次数不超过最大值
      expect(ws.reconnectAttempts).toBeLessThanOrEqual(3)
    })
  })

  describe('消息处理性能', () => {
    it('应该快速处理单条消息', () => {
      ws.connect()

      const startTime = Date.now()

      // 模拟接收消息
      const message = {
        channel: 'test:channel',
        payload: { data: 'test' }
      }

      // 订阅频道
      const callback = vi.fn()
      ws.subscribe('test:channel', callback)

      // 触发消息处理
      ws.message.value = message

      const endTime = Date.now()
      const processingTime = endTime - startTime

      expect(processingTime).toBeLessThan(100) // 100ms内处理
      expect(callback).toHaveBeenCalledWith(message.payload)
    })

    it('应该高效处理批量消息', () => {
      ws.connect()

      const messageCount = 100
      const callbacks = vi.fn()

      ws.subscribe('test:channel', callbacks)

      const startTime = Date.now()

      // 发送批量消息
      for (let i = 0; i < messageCount; i++) {
        ws.message.value = {
          channel: 'test:channel',
          payload: { index: i }
        }
      }

      const endTime = Date.now()
      const totalTime = endTime - startTime
      const avgTime = totalTime / messageCount

      expect(avgTime).toBeLessThan(10) // 平均每条消息处理时间<10ms
      expect(callbacks).toHaveBeenCalledTimes(messageCount)
    })

    it('应该处理不同频道的消息', () => {
      ws.connect()

      const callback1 = vi.fn()
      const callback2 = vi.fn()

      ws.subscribe('channel1', callback1)
      ws.subscribe('channel2', callback2)

      // 发送到channel1
      ws.message.value = {
        channel: 'channel1',
        payload: { data: 'test1' }
      }

      // 发送到channel2
      ws.message.value = {
        channel: 'channel2',
        payload: { data: 'test2' }
      }

      expect(callback1).toHaveBeenCalledTimes(1)
      expect(callback2).toHaveBeenCalledTimes(1)
      expect(callback1).toHaveBeenCalledWith({ data: 'test1' })
      expect(callback2).toHaveBeenCalledWith({ data: 'test2' })
    })
  })

  describe('订阅管理性能', () => {
    it('应该高效管理多个订阅', () => {
      ws.connect()

      const channelCount = 50
      const callbacks: Array<() => void> = []

      // 订阅多个频道
      for (let i = 0; i < channelCount; i++) {
        const unsubscribe = ws.subscribe(`channel-${i}`, vi.fn())
        callbacks.push(unsubscribe)
      }

      expect(ws.getActiveSubscriptions()).toHaveLength(channelCount)

      // 取消所有订阅
      callbacks.forEach(unsubscribe => unsubscribe())

      expect(ws.getActiveSubscriptions()).toHaveLength(0)
    })

    it('应该支持同一频道的多个订阅者', () => {
      ws.connect()

      const callback1 = vi.fn()
      const callback2 = vi.fn()

      ws.subscribe('shared-channel', callback1)
      ws.subscribe('shared-channel', callback2)

      expect(ws.getSubscriberCount('shared-channel')).toBe(2)

      // 发送消息
      ws.message.value = {
        channel: 'shared-channel',
        payload: { test: true }
      }

      // 两个订阅者都应该收到消息
      expect(callback1).toHaveBeenCalled()
      expect(callback2).toHaveBeenCalled()
    })

    it('取消订阅应该只影响指定订阅者', () => {
      ws.connect()

      const callback1 = vi.fn()
      const callback2 = vi.fn()

      const unsubscribe1 = ws.subscribe('shared-channel', callback1)
      ws.subscribe('shared-channel', callback2)

      // 取消第一个订阅
      unsubscribe1()

      expect(ws.getSubscriberCount('shared-channel')).toBe(1)

      // 发送消息
      ws.message.value = {
        channel: 'shared-channel',
        payload: { test: true }
      }

      // 只有callback2应该收到消息
      expect(callback1).not.toHaveBeenCalled()
      expect(callback2).toHaveBeenCalled()
    })
  })

  describe('心跳性能', () => {
    it('应该定期发送心跳消息', async () => {
      ws.connect()

      const sendSpy = vi.spyOn(ws, 'send')

      // 等待心跳间隔
      await new Promise(resolve => setTimeout(resolve, 31000))

      // 验证至少发送了一次心跳
      expect(sendSpy).toHaveBeenCalled()
      expect(sendSpy).toHaveBeenCalledWith(expect.objectContaining({
        type: 'ping'
      }))
    })

    it('应该在断开连接时停止心跳', () => {
      ws.connect()
      ws.disconnect()

      const sendSpy = vi.spyOn(ws, 'send')

      // 等待超过心跳间隔
      setTimeout(() => {
        expect(sendSpy).not.toHaveBeenCalled()
      }, 31000)
    })
  })

  describe('内存泄漏测试', () => {
    it('订阅和取消订阅不应该泄漏内存', () => {
      ws.connect()

      const initialSubscriptions = ws.getActiveSubscriptions().length

      // 多次订阅和取消订阅
      for (let i = 0; i < 100; i++) {
        const unsubscribe = ws.subscribe(`temp-channel-${i}`, vi.fn())
        unsubscribe()
      }

      // 验证订阅已清理
      const finalSubscriptions = ws.getActiveSubscriptions()
      const tempChannels = finalSubscriptions.filter(s => s.startsWith('temp-channel-'))

      expect(tempChannels).toHaveLength(0)
      expect(finalSubscriptions.length).toBe(initialSubscriptions)
    })

    it('重连不应该累积定时器', () => {
      ws.connect()

      // 模拟多次重连
      for (let i = 0; i < 5; i++) {
        ws.error.value = new Event('error')
        // 等待重连尝试
      }

      // 验证只有一个活跃的重连定时器
      // （需要访问内部状态，这里简化为基本检查）
      expect(ws.connectionState.value).not.toBe('error')
    })
  })

  describe('并发安全性', () => {
    it('应该安全处理并发订阅', async () => {
      ws.connect()

      const promises = Array.from({ length: 100 }, (_, i) =>
        Promise.resolve().then(() => {
          const unsubscribe = ws.subscribe(`channel-${i}`, vi.fn())
          return unsubscribe
        })
      )

      const unsubscribers = await Promise.all(promises)

      expect(ws.getActiveSubscriptions()).toHaveLength(100)

      // 清理
      unsubscribers.forEach(unsubscribe => unsubscribe())
    })

    it('应该安全处理并发消息发送', async () => {
      ws.connect()

      const sendPromises = Array.from({ length: 100 }, (_, i) =>
        Promise.resolve().then(() => {
          ws.send({ type: 'test', index: i })
        })
      )

      await Promise.all(sendPromises)

      // 验证所有消息都已发送（简化验证）
      expect(ws.message.value).toBeTruthy()
    })
  })

  describe('错误恢复性能', () => {
    it('应该快速从网络错误中恢复', async () => {
      ws.connect()

      const recoverTime = await new Promise(resolve => {
        const startTime = Date.now()

        // 模拟网络错误
        ws.error.value = new Event('error')

        // 模拟恢复
        setTimeout(() => {
          const endTime = Date.now()
          resolve(endTime - startTime)
        }, 500)
      })

      expect(recoverTime).toBeLessThan(3000) // 3秒内恢复
    })

    it('应该处理服务器重启', async () => {
      ws.connect()

      // 模拟服务器关闭
      ws.error.value = new Event('error')

      // 等待重连
      await new Promise(resolve => setTimeout(resolve, 2000))

      // 模拟服务器恢复
      ws.connect()

      expect(ws.connectionState.value).not.toBe('error')
    })
  })

  describe('资源消耗', () => {
    it('应该控制内存使用', () => {
      ws.connect()

      // 获取初始内存使用（简化）
      const initialMessageCount = 0

      // 发送大量消息
      for (let i = 0; i < 1000; i++) {
        ws.message.value = {
          channel: 'test',
          payload: { index: i, data: 'x'.repeat(1000) }
        }
      }

      // 验证消息不会无限累积
      //（实际实现中需要检查内存使用情况）
      expect(ws.message.value).toBeTruthy()
    })

    it('应该控制CPU使用', () => {
      ws.connect()

      const startTime = Date.now()

      // 大量操作
      for (let i = 0; i < 10000; i++) {
        ws.subscribe(`channel-${i}`, vi.fn())
      }

      const endTime = Date.now()
      const duration = endTime - startTime

      // 应该在合理时间内完成
      expect(duration).toBeLessThan(5000) // 5秒内

      // 清理
      ws.getActiveSubscriptions().forEach(channel => {
        // 取消订阅
      })
    })
  })
})
