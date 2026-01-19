/**
 * Toast Manager Unit Tests
 *
 * 测试Toast通知管理器的核心功能
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useToastManager } from '../useToastManager'

describe('useToastManager', () => {
  let toast: ReturnType<typeof useToastManager>

  beforeEach(() => {
    // 清除所有toasts
    toast = useToastManager()
    toast.clearAll()
  })

  afterEach(() => {
    // 清理所有toasts
    toast.clearAll()
  })

  describe('基础功能', () => {
    it('应该初始化为空toasts列表', () => {
      expect(toast.toasts).toHaveLength(0)
    })

    it('应该添加成功toast', () => {
      const id = toast.showSuccess('操作成功')

      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].type).toBe('success')
      expect(toast.toasts[0].message).toBe('操作成功')
      expect(toast.toasts[0].title).toBe('操作成功')
      expect(id).toBeTruthy()
    })

    it('应该添加错误toast', () => {
      const id = toast.showError('操作失败')

      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].type).toBe('error')
      expect(toast.toasts[0].message).toBe('操作失败')
      expect(toast.toasts[0].title).toBe('操作失败')
    })

    it('应该添加警告toast', () => {
      const id = toast.showWarning('注意事项')

      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].type).toBe('warning')
      expect(toast.toasts[0].message).toBe('注意事项')
    })

    it('应该添加信息toast', () => {
      const id = toast.showInfo('提示信息')

      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].type).toBe('info')
      expect(toast.toasts[0].message).toBe('提示信息')
    })
  })

  describe('自定义标题', () => {
    it('应该支持自定义成功toast标题', () => {
      toast.showSuccess('数据已保存', '保存成功')

      expect(toast.toasts[0].title).toBe('保存成功')
      expect(toast.toasts[0].message).toBe('数据已保存')
    })

    it('应该支持自定义错误toast标题', () => {
      toast.showError('网络错误', '连接失败')

      expect(toast.toasts[0].title).toBe('连接失败')
      expect(toast.toasts[0].message).toBe('网络错误')
    })

    it('应该支持自定义警告toast标题', () => {
      toast.showWarning('数据可能过期', '缓存警告')

      expect(toast.toasts[0].title).toBe('缓存警告')
      expect(toast.toasts[0].message).toBe('数据可能过期')
    })

    it('应该支持自定义信息toast标题', () => {
      toast.showInfo('系统维护', '维护通知')

      expect(toast.toasts[0].title).toBe('维护通知')
      expect(toast.toasts[0].message).toBe('系统维护')
    })
  })

  describe('移除功能', () => {
    it('应该移除指定toast', () => {
      const id = toast.showSuccess('测试')

      expect(toast.toasts).toHaveLength(1)

      toast.remove(id)

      expect(toast.toasts).toHaveLength(0)
    })

    it('应该清除所有toasts', () => {
      toast.showSuccess('成功1')
      toast.showError('错误1')
      toast.showWarning('警告1')
      toast.showInfo('信息1')

      expect(toast.toasts).toHaveLength(4)

      toast.clearAll()

      expect(toast.toasts).toHaveLength(0)
    })

    it('移除不存在的ID不应该报错', () => {
      toast.showSuccess('测试')
      expect(toast.toasts).toHaveLength(1)

      // 移除不存在的ID
      toast.remove('non-existent-id')
      expect(toast.toasts).toHaveLength(1) // 不应该影响现有toasts
    })
  })

  describe('通用show方法', () => {
    it('应该支持自定义配置', () => {
      const id = toast.show({
        type: 'error',
        title: '自定义标题',
        message: '自定义消息',
        duration: 10000,
        closable: false,
        position: 'bottom-right'
      })

      const toastItem = toast.toasts[0]
      expect(toastItem.type).toBe('error')
      expect(toastItem.title).toBe('自定义标题')
      expect(toastItem.message).toBe('自定义消息')
      expect(toastItem.duration).toBe(10000)
      expect(toastItem.closable).toBe(false)
    })

    it('应该支持自定义ID', () => {
      const customId = 'my-custom-id'
      toast.show({
        type: 'info',
        message: '测试',
        id: customId
      })

      expect(toast.toasts[0].id).toBe(customId)
    })

    it('相同ID应该替换旧toast', () => {
      const id = 'same-id'

      toast.show({
        type: 'success',
        message: '第一条消息',
        id: id
      })

      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].message).toBe('第一条消息')

      toast.show({
        type: 'error',
        message: '第二条消息',
        id: id
      })

      // 应该替换而不是添加
      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].message).toBe('第二条消息')
      expect(toast.toasts[0].type).toBe('error')
    })
  })

  describe('自动移除', () => {
    vi.useFakeTimers()

    it('应该在duration后自动移除toast', () => {
      const id = toast.show({
        type: 'info',
        message: '测试',
        duration: 1000
      })

      expect(toast.toasts).toHaveLength(1)

      // 快进1000ms
      vi.advanceTimersByTime(1000)

      // 等待下一个tick
      await vi.runAllTimersAsync()

      // Toast应该被移除
      expect(toast.toasts).toHaveLength(0)
    })

    it('duration为0不应该自动移除', () => {
      const id = toast.show({
        type: 'info',
        message: '测试',
        duration: 0
      })

      expect(toast.toasts).toHaveLength(1)

      // 快进10秒
      vi.advanceTimersByTime(10000)

      // Toast应该仍然存在
      expect(toast.toasts).toHaveLength(1)
    })

    afterEach(() => {
      vi.restoreAllMocks()
    })
  })

  describe('默认值', () => {
    it('成功toast默认duration应该是3000ms', () => {
      toast.showSuccess('测试')

      expect(toast.toasts[0].duration).toBe(3000)
    })

    it('错误toast默认duration应该是5000ms', () => {
      toast.showError('测试')

      expect(toast.toasts[0].duration).toBe(5000)
    })

    it('警告toast默认duration应该是4000ms', () => {
      toast.showWarning('测试')

      expect(toast.toasts[0].duration).toBe(4000)
    })

    it('信息toast默认duration应该是3000ms', () => {
      toast.showInfo('测试')

      expect(toast.toasts[0].duration).toBe(3000)
    })

    it('所有toast默认应该是closable', () => {
      toast.showSuccess('测试')

      expect(toast.toasts[0].closable).toBe(true)
    })
  })
})
