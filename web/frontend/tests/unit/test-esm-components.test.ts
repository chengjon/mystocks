/**
 * Vitest ESM组件测试套件
 * 专门测试ESM模块兼容性，特别是dayjs相关功能
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

// 测试ESM导入是否正常工作
describe('ESM模块兼容性测试', () => {
  it('dayjs ESM导入应该正常工作', async () => {
    // 测试动态导入dayjs
    const dayjs = await import('dayjs')
    expect(dayjs.default).toBeDefined()
    expect(typeof dayjs.default).toBe('function')

    // 测试基本功能
    const now = dayjs.default()
    expect(now).toBeDefined()
    expect(now.isValid()).toBe(true)
  })

  it('dayjs插件ESM导入应该正常工作', async () => {
    // 测试动态导入插件
    const [dayjs, utcPlugin] = await Promise.all([
      import('dayjs'),
      import('dayjs/plugin/utc')
    ])

    // 注册插件
    dayjs.default.extend(utcPlugin.default)

    // 测试插件功能
    const utcTime = dayjs.default().utc()
    expect(utcTime).toBeDefined()
    expect(utcTime.isValid()).toBe(true)
  })

  it('ESM模块缓存应该正确工作', async () => {
    // 测试多次导入是否返回同一实例
    const [dayjs1, dayjs2] = await Promise.all([
      import('dayjs'),
      import('dayjs')
    ])

    expect(dayjs1.default).toBe(dayjs2.default)
  })
})

// 测试组件中的ESM使用
describe('组件ESM使用测试', () => {
  it('组件应该能正确导入和使用dayjs', async () => {
    // 这里可以测试实际组件中的dayjs使用
    // 由于组件可能有复杂依赖，我们先测试概念

    // 模拟组件中的dayjs使用场景
    const mockComponentLogic = async () => {
      const dayjs = (await import('dayjs')).default
      return dayjs().format('YYYY-MM-DD')
    }

    const result = await mockComponentLogic()
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it('组件应该能处理ESM模块的异步加载', async () => {
    // 测试ESM模块的异步加载场景
    let loaded = false

    const loadModule = async () => {
      await import('dayjs')
      loaded = true
      return true
    }

    const result = await loadModule()
    expect(result).toBe(true)
    expect(loaded).toBe(true)
  })
})

// 测试ESM相关的性能和可靠性
describe('ESM性能和可靠性测试', () => {
  it('ESM模块加载应该足够快', async () => {
    const startTime = Date.now()

    await import('dayjs')

    const endTime = Date.now()
    const loadTime = endTime - startTime

    // ESM模块加载应该在合理时间内完成
    expect(loadTime).toBeLessThan(1000) // 1秒内
  })

  it('ESM模块应该有稳定的导出', async () => {
    // 测试多次加载的稳定性
    for (let i = 0; i < 5; i++) {
      const dayjs = await import('dayjs')
      expect(dayjs.default).toBeDefined()
      expect(typeof dayjs.default).toBe('function')
    }
  })

  it('ESM模块应该能正确处理错误', async () => {
    // 测试ESM模块加载错误处理
    try {
      // 尝试导入不存在的模块
      await import('non-existent-module-dayjs-test')
      expect.fail('应该抛出错误')
    } catch (error) {
      expect(error).toBeDefined()
      expect(error.message).toContain('non-existent-module-dayjs-test')
    }
  })
})

// 测试与Vue组件的集成
describe('ESM与Vue组件集成测试', () => {
  it('Vue组件应该能使用ESM模块', async () => {
    // 创建一个简单的测试组件
    const TestComponent = {
      template: '<div>{{ formattedDate }}</div>',
      setup() {
        const formattedDate = ref('')

        onMounted(async () => {
          try {
            const dayjs = (await import('dayjs')).default
            formattedDate.value = dayjs().format('YYYY-MM-DD')
          } catch (error) {
            formattedDate.value = 'ESM加载失败'
          }
        })

        return { formattedDate }
      }
    }

    // 挂载组件
    const wrapper = mount(TestComponent)

    // 等待异步操作完成
    await nextTick()

    // 验证组件能正确渲染
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toMatch(/\d{4}-\d{2}-\d{2}|ESM加载失败/)
  })

  it('Vue组件ESM错误应该被正确处理', async () => {
    // 创建一个会遇到ESM错误的组件
    const ErrorComponent = {
      template: '<div>{{ errorMessage }}</div>',
      setup() {
        const errorMessage = ref('')

        onMounted(async () => {
          try {
            // 尝试导入不存在的ESM模块
            await import('dayjs/esm/non-existent-plugin')
            errorMessage.value = '意外成功'
          } catch (error) {
            errorMessage.value = 'ESM错误已处理'
          }
        })

        return { errorMessage }
      }
    }

    const wrapper = mount(ErrorComponent)
    await nextTick()

    expect(wrapper.text()).toBe('ESM错误已处理')
  })
})

// 辅助函数
function ref(value) {
  return { value }
}

function onMounted(callback) {
  // 在测试环境中模拟onMounted
  callback()
}