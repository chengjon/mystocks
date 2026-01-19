/**
 * Playwright ESM增强测试框架
 * 提供ESM错误监听、诊断机制和页面加载状态监控
 */

import { test as base, Page } from '@playwright/test'

// 扩展测试框架
export const test = base.extend<{
  esmMonitor: ESMMonitor
}>({
  esmMonitor: async ({ page }, use) => {
    const monitor = new ESMMonitor(page)
    await monitor.setup()
    await use(monitor)
    await monitor.cleanup()
  }
})

// ESM错误监听和诊断类
export class ESMMonitor {
  private page: Page
  private errors: string[] = []
  private warnings: string[] = []
  private esmErrors: string[] = []
  private networkRequests: any[] = []
  private networkErrors: any[] = []

  constructor(page: Page) {
    this.page = page
  }

  async setup() {
    // 监听JavaScript错误
    this.page.on('console', msg => {
      const message = `[${msg.type().toUpperCase()}] ${msg.text()}`

      if (msg.type() === 'error') {
        this.errors.push(message)

        // 检测ESM相关错误
        if (this.isESMError(msg.text())) {
          this.esmErrors.push(message)
        }
      } else if (msg.type() === 'warning') {
        this.warnings.push(message)
      }
    })

    // 监听页面错误
    this.page.on('pageerror', error => {
      const errorMsg = `PageError: ${error.message}`
      this.errors.push(errorMsg)

      if (this.isESMError(error.message)) {
        this.esmErrors.push(errorMsg)
      }
    })

    // 监听网络请求
    this.page.on('request', request => {
      this.networkRequests.push({
        url: request.url(),
        method: request.method(),
        timestamp: Date.now(),
        type: this.getRequestType(request.url())
      })
    })

    // 监听网络失败
    this.page.on('requestfailed', request => {
      const failure = request.failure()
      const errorInfo = {
        url: request.url(),
        method: request.method(),
        errorText: failure?.errorText || 'Unknown error',
        timestamp: Date.now(),
        type: this.getRequestType(request.url())
      }

      this.networkErrors.push(errorInfo)
      this.errors.push(`NetworkError: ${request.url()} - ${failure?.errorText}`)
    })

    // 注入页面监控脚本
    await this.page.addInitScript(() => {
      // 全局错误监控
      window.testESMMonitor = {
        esmErrors: [],
        moduleLoadErrors: [],
        scriptLoadErrors: []
      }

      // 监听ESM模块加载错误
      window.addEventListener('error', (event) => {
        const errorMsg = event.message || ''

        // 检测ESM相关错误模式
        if (errorMsg.includes('does not provide an export named') ||
            errorMsg.includes('Cannot resolve module') ||
            errorMsg.includes('ESM import failed') ||
            errorMsg.includes('dayjs.min.js')) {
          window.testESMMonitor.esmErrors.push({
            message: errorMsg,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            timestamp: Date.now()
          })
        }

        // 检测脚本加载错误
        if (errorMsg.includes('Loading module') ||
            errorMsg.includes('Loading chunk') ||
            errorMsg.includes('Failed to load resource')) {
          window.testESMMonitor.scriptLoadErrors.push({
            message: errorMsg,
            timestamp: Date.now()
          })
        }
      })

      // 监听未处理的Promise拒绝
      window.addEventListener('unhandledrejection', (event) => {
        const errorMsg = event.reason?.message || event.reason || 'Unhandled promise rejection'

        if (errorMsg.includes('ESM') || errorMsg.includes('module') ||
            errorMsg.includes('import') || errorMsg.includes('dayjs')) {
          window.testESMMonitor.moduleLoadErrors.push({
            message: errorMsg,
            timestamp: Date.now()
          })
        }
      })
    })
  }

  private isESMError(message: string): boolean {
    const esmErrorPatterns = [
      'does not provide an export named',
      'Cannot resolve module',
      'ESM import failed',
      'dayjs.min.js',
      'Loading module',
      'Loading chunk',
      'Failed to fetch dynamically imported module'
    ]

    return esmErrorPatterns.some(pattern => message.includes(pattern))
  }

  private getRequestType(url: string): string {
    if (url.includes('.js') || url.includes('module')) return 'javascript'
    if (url.includes('.css')) return 'stylesheet'
    if (url.includes('api/') || url.includes('/api')) return 'api'
    if (url.includes('.png') || url.includes('.jpg') || url.includes('.svg')) return 'image'
    return 'other'
  }

  async getPageLoadMetrics() {
    return await this.page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming

      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        totalTime: navigation.loadEventEnd - navigation.fetchStart,
        scriptCount: document.querySelectorAll('script').length,
        cssCount: document.querySelectorAll('link[rel="stylesheet"]').length,
        imageCount: document.querySelectorAll('img').length,
        esmErrors: (window as any).testESMMonitor?.esmErrors || [],
        moduleLoadErrors: (window as any).testESMMonitor?.moduleLoadErrors || [],
        scriptLoadErrors: (window as any).testESMMonitor?.scriptLoadErrors || []
      }
    })
  }

  async getNetworkSummary() {
    const summary = {
      totalRequests: this.networkRequests.length,
      errorCount: this.networkErrors.length,
      byType: {} as Record<string, number>,
      errors: this.networkErrors.slice(0, 10) // 只保留前10个错误
    }

    // 按类型统计请求
    this.networkRequests.forEach(req => {
      summary.byType[req.type] = (summary.byType[req.type] || 0) + 1
    })

    return summary
  }

  async diagnoseESMIssues(): Promise<{
    hasESMErrors: boolean
    criticalErrors: string[]
    recommendations: string[]
    severity: 'low' | 'medium' | 'high' | 'critical'
  }> {
    const pageMetrics = await this.getPageLoadMetrics()
    const networkSummary = await this.getNetworkSummary()

    const criticalErrors: string[] = []
    const recommendations: string[] = []

    // 检查ESM错误
    if (this.esmErrors.length > 0) {
      criticalErrors.push(`发现 ${this.esmErrors.length} 个ESM模块错误`)
      recommendations.push('检查Vite配置中的ESM别名设置')
      recommendations.push('验证dayjs等ESM库的正确导入方式')
    }

    // 检查页面加载问题
    if (pageMetrics.esmErrors.length > 0) {
      criticalErrors.push(`页面级ESM错误: ${pageMetrics.esmErrors.length} 个`)
      recommendations.push('检查浏览器控制台的ESM模块加载错误')
    }

    // 检查网络错误
    const jsErrors = networkSummary.errors.filter(e => e.type === 'javascript')
    if (jsErrors.length > 0) {
      criticalErrors.push(`JavaScript模块加载失败: ${jsErrors.length} 个`)
      recommendations.push('验证ESM模块的CDN路径或本地路径')
    }

    // 确定严重程度
    let severity: 'low' | 'medium' | 'high' | 'critical' = 'low'
    if (criticalErrors.length > 0) {
      if (this.esmErrors.length > 2) {
        severity = 'critical'
      } else if (this.esmErrors.length > 0) {
        severity = 'high'
      } else {
        severity = 'medium'
      }
    }

    return {
      hasESMErrors: this.esmErrors.length > 0 || pageMetrics.esmErrors.length > 0,
      criticalErrors,
      recommendations,
      severity
    }
  }

  getAllErrors() {
    return {
      consoleErrors: this.errors,
      consoleWarnings: this.warnings,
      esmErrors: this.esmErrors,
      networkErrors: this.networkErrors
    }
  }

  async cleanup() {
    // 清理监听器
    this.page.removeAllListeners('console')
    this.page.removeAllListeners('pageerror')
    this.page.removeAllListeners('request')
    this.page.removeAllListeners('requestfailed')
  }
}

// 工具函数
export function createESMTestWrapper(testFunction: (monitor: ESMMonitor) => Promise<void>) {
  return async ({ page, esmMonitor }: { page: Page, esmMonitor: ESMMonitor }) => {
    try {
      await testFunction(esmMonitor)

      // 测试后诊断ESM问题
      const diagnosis = await esmMonitor.diagnoseESMIssues()
      if (diagnosis.hasESMErrors) {
        console.warn('ESM问题诊断:', diagnosis)

        if (diagnosis.severity === 'critical') {
          throw new Error(`Critical ESM errors detected: ${diagnosis.criticalErrors.join(', ')}`)
        }
      }
    } catch (error) {
      // 收集所有错误信息用于调试
      const allErrors = esmMonitor.getAllErrors()
      console.error('Test failed with ESM context:', {
        error: error.message,
        esmErrors: allErrors.esmErrors,
        networkErrors: allErrors.networkErrors
      })
      throw error
    }
  }
}

// 便捷的ESM测试断言
export const esmExpect = {
  noESMErrors: async (monitor: ESMMonitor) => {
    const diagnosis = await monitor.diagnoseESMIssues()
    if (diagnosis.hasESMErrors) {
      throw new Error(`ESM errors detected: ${diagnosis.criticalErrors.join(', ')}`)
    }
  },

  pageLoadsWithin: async (monitor: ESMMonitor, maxTimeMs: number) => {
    const metrics = await monitor.getPageLoadMetrics()
    if (metrics.totalTime > maxTimeMs) {
      throw new Error(`Page load time ${metrics.totalTime}ms exceeds limit ${maxTimeMs}ms`)
    }
  },

  noNetworkErrors: async (monitor: ESMMonitor) => {
    const networkSummary = await monitor.getNetworkSummary()
    if (networkSummary.errorCount > 0) {
      throw new Error(`${networkSummary.errorCount} network errors detected`)
    }
  }
}