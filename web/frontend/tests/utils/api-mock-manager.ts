/**
 * API Mock管理器 - 解决路由处理器优先级问题
 *
 * 核心策略：
 * 1. 统一管理所有API路由处理器
 * 2. 建立清晰的优先级：具体Mock > 通用Mock > 默认处理
 * 3. 避免真实后端依赖
 */

import { test, Page, Route, Request } from '@playwright/test'

export interface MockConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  url: string | RegExp
  status: number
  response?: any
  handler?: (route: Route, request: Request) => Promise<void>
  skipStandardization?: boolean // 跳过API格式校验
}

export class ApiMockManager {
  private mocks: Map<string, MockConfig[]> = new Map()
  private page: Page
  private mockMode: 'all' | 'partial' | 'none' = 'all'

  constructor(page: Page) {
    this.page = page
  }

  /**
   * 设置Mock模式
   * - all: 所有API都使用Mock（推荐用于E2E测试）
   * - partial: 部分API使用Mock，允许真实请求
   * - none: 不使用Mock（仅用于集成测试）
   */
  setMockMode(mode: 'all' | 'partial' | 'none') {
    this.mockMode = mode
  }

  /**
   * 注册API Mock
   */
  registerMock(config: MockConfig) {
    const key = this.getMockKey(config)
    if (!this.mocks.has(key)) {
      this.mocks.set(key, [])
    }
    this.mocks.get(key)!.push(config)
  }

  /**
   * 批量注册Mock
   */
  registerMocks(configs: MockConfig[]) {
    configs.forEach(config => this.registerMock(config))
  }

  /**
   * 应用所有Mock处理器
   * 必须在所有mock注册之后调用
   */
  async applyMocks() {
    // 清除所有现有的路由处理器
    await this.page.unroute('**/*')

    // 按优先级注册路由处理器
    // 1. 具体路径的Mock（最高优先级）
    await this.setupSpecificMocks()

    // 2. 通用路径的Mock（中等优先级）
    await this.setupGenericMocks()

    // 3. 默认处理器（最低优先级）
    await this.setupDefaultHandler()
  }

  /**
   * 设置具体路径的Mock
   */
  private async setupSpecificMocks() {
    // 注册所有具体的API Mock
    for (const [key, configs] of this.mocks) {
      if (key !== '*') { // 跳过通配符配置
        for (const config of configs) {
          await this.page.route(config.url, async (route, request) => {
            await this.handleMock(config, route, request)
          })
        }
      }
    }
  }

  /**
   * 设置通用Mock
   */
  private async setupGenericMocks() {
    const genericConfigs = this.mocks.get('*') || []

    // 处理所有GET请求
    await this.page.route('**/api/**', async (route, request) => {
      const isGet = request.method() === 'GET'
      const hasSpecificMock = await this.hasSpecificMock(request.url())

      if (!hasSpecificMock && genericConfigs.length > 0) {
        // 使用通配符配置
        const config = genericConfigs.find(c => c.method === request.method()) || genericConfigs[0]
        await this.handleMock(config, route, request)
        return
      }

      // 如果没有匹配的Mock，继续到默认处理器
      await route.continue()
    })
  }

  /**
   * 设置默认处理器
   */
  private async setupDefaultHandler() {
    await this.page.route('**/*', async (route, request) => {
      const url = request.url()

      // 跳过非API请求
      if (!url.includes('/api/')) {
        await route.continue()
        return
      }

      if (this.mockMode === 'all') {
        // 所有未Mock的API返回404，避免真实请求
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({
            success: false,
            code: 404,
            data: null,
            message: `API endpoint not mocked: ${request.method()} ${url}`
          })
        })
      } else if (this.mockMode === 'partial') {
        // 部分模式下允许真实请求，但设置超时
        try {
          await Promise.race([
            route.continue(),
            new Promise((_, reject) =>
              setTimeout(() => reject(new Error('Request timeout')), 5000)
            )
          ])
        } catch (error) {
          await route.fulfill({
            status: 408,
            contentType: 'application/json',
            body: JSON.stringify({
              success: false,
              code: 408,
              data: null,
              message: 'Request timeout - backend unavailable'
            })
          })
        }
      } else {
        // none模式直接继续
        await route.continue()
      }
    })
  }

  /**
   * 处理Mock请求
   */
  private async handleMock(config: MockConfig, route: Route, request: Request) {
    if (config.handler) {
      await config.handler(route, request)
    } else {
      let response = config.response

      // 如果响应是函数，调用它
      if (typeof response === 'function') {
        response = response(request)
      }

      // 应用API格式标准
      if (!config.skipStandardization && this.mockMode === 'all') {
        response = this.standardizeResponse(response, config.status)
      }

      await route.fulfill({
        status: config.status,
        contentType: 'application/json',
        body: JSON.stringify(response)
      })
    }
  }

  /**
   * 标准化API响应格式
   */
  private standardizeResponse(data: any, status: number) {
    return {
      success: status >= 200 && status < 300,
      code: status,
      data: data,
      message: status >= 200 && status < 300 ? 'Success' : 'Error'
    }
  }

  /**
   * 检查是否有特定Mock
   */
  private async hasSpecificMock(url: string): Promise<boolean> {
    for (const [key, configs] of this.mocks) {
      if (key !== '*') {
        for (const config of configs) {
          if (typeof config.url === 'string' && url.includes(config.url)) {
            return true
          } else if (config.url instanceof RegExp && config.url.test(url)) {
            return true
          }
        }
      }
    }
    return false
  }

  /**
   * 获取Mock的键
   */
  private getMockKey(config: MockConfig): string {
    if (typeof config.url === 'string') {
      return config.url
    } else if (config.url instanceof RegExp) {
      return config.url.source
    }
    return '*'
  }
}

// 预定义的常用Mock
export const defaultMocks = {
  // 用户认证
  login: {
    method: 'POST' as const,
    url: '/api/user/login',
    status: 200,
    response: {
      token: 'mock-token-123',
      user: {
        id: 1,
        username: 'testuser',
        roles: ['user']
      }
    }
  },

  // 获取用户信息
  userInfo: {
    method: 'GET' as const,
    url: '/api/user/info',
    status: 200,
    response: {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      roles: ['user']
    }
  },

  // 健康检查
  health: {
    method: 'GET' as const,
    url: '/health',
    status: 200,
    response: {
      status: 'healthy',
      timestamp: Date.now()
    },
    skipStandardization: true // 跳过格式标准化
  },

  // 股票列表
  stocks: {
    method: 'GET' as const,
    url: '/api/stocks',
    status: 200,
    response: [
      { symbol: 'AAPL', name: 'Apple Inc.', price: 150.25 },
      { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 2500.50 }
    ]
  },

  // 通用错误Mock
  error: {
    method: 'GET' as const,
    url: '*',
    status: 500,
    response: {
      error: 'Internal Server Error'
    }
  }
}

// 便捷的测试设置函数
export function setupApiMocks(page: Page, mocks: MockConfig[] = []) {
  const manager = new ApiMockManager(page)

  // 注册默认Mock
  manager.registerMocks(Object.values(defaultMocks))

  // 注册自定义Mock
  if (mocks.length > 0) {
    manager.registerMocks(mocks)
  }

  // 应用所有Mock
  return manager.applyMocks()
}
