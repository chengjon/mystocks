/**
 * E2E 测试助手 - 浏览器兼容性和稳定性工具
 *
 * 提供跨浏览器的等待、选择器、重试机制
 * 用于处理 Firefox/WebKit 的渲染延迟问题
 */

import { Page, BrowserContext } from '@playwright/test'

/**
 * 浏览器配置
 */
export interface BrowserConfig {
  waitAfterLoadState?: number // 额外等待时间 (ms)
  selectTimeout?: number       // 选择器超时 (ms)
  navigationTimeout?: number   // 导航超时 (ms)
}

/**
 * 获取浏览器特定的等待配置
 */
export function getBrowserConfig(browserName: string): BrowserConfig {
  switch (browserName) {
    case 'firefox':
      return {
        waitAfterLoadState: 2000,  // Firefox 需要额外 2 秒
        selectTimeout: 15000,       // Firefox 选择器超时 15s
        navigationTimeout: 40000,   // Firefox 导航超时 40s
      }
    case 'webkit':
      return {
        waitAfterLoadState: 2500,  // WebKit 需要额外 2.5 秒（最慢）
        selectTimeout: 20000,       // WebKit 选择器超时 20s
        navigationTimeout: 45000,   // WebKit 导航超时 45s
      }
    case 'chromium':
    default:
      return {
        waitAfterLoadState: 500,    // Chromium 只需 500ms
        selectTimeout: 10000,       // Chromium 选择器超时 10s
        navigationTimeout: 30000,   // Chromium 导航超时 30s
      }
  }
}

/**
 * 智能页面导航 - 自动处理浏览器延迟
 *
 * @param page Playwright Page 对象
 * @param url 目标 URL
 * @param browserName 浏览器名称
 */
export async function smartGoto(
  page: Page,
  url: string,
  browserName: string = 'chromium'
): Promise<void> {
  const config = getBrowserConfig(browserName)

  try {
    // 带超时的导航
    await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: config.navigationTimeout,
    })

    // 等待网络完全空闲
    await page.waitForLoadState('networkidle')

    // 浏览器特定的额外等待
    if (config.waitAfterLoadState > 0) {
      await page.waitForTimeout(config.waitAfterLoadState)
    }
  } catch (error) {
    throw new Error(`Failed to navigate to ${url}: ${error}`)
  }
}

/**
 * 智能元素等待 - 处理 Firefox/WebKit 的元素可见性问题
 *
 * @param page Playwright Page 对象
 * @param selector CSS 选择器
 * @param browserName 浏览器名称
 */
export async function smartWaitForElement(
  page: Page,
  selector: string,
  browserName: string = 'chromium'
): Promise<void> {
  const config = getBrowserConfig(browserName)

  try {
    // 等待元素在 DOM 中
    await page.waitForSelector(selector, { timeout: config.selectTimeout })

    // 等待元素可见
    const element = page.locator(selector).first()
    await element.waitFor({ state: 'visible', timeout: config.selectTimeout })

    // 浏览器特定延迟
    if (config.waitAfterLoadState > 0) {
      await page.waitForTimeout(500)
    }
  } catch (error) {
    throw new Error(`Element not found or not visible: ${selector}`)
  }
}

/**
 * 智能点击 - 重试机制
 *
 * @param page Playwright Page 对象
 * @param selector CSS 选择器
 * @param browserName 浏览器名称
 * @param maxRetries 最大重试次数
 */
export async function smartClick(
  page: Page,
  selector: string,
  browserName: string = 'chromium',
  maxRetries: number = 3
): Promise<void> {
  let lastError: Error | null = null

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // 等待元素可见
      await smartWaitForElement(page, selector, browserName)

      // 点击元素
      await page.locator(selector).first().click({
        timeout: getBrowserConfig(browserName).selectTimeout,
      })

      return // 成功
    } catch (error) {
      lastError = error as Error

      if (attempt < maxRetries) {
        // 等待后重试
        await page.waitForTimeout(1000)
      }
    }
  }

  throw new Error(`Failed to click ${selector} after ${maxRetries} attempts: ${lastError?.message}`)
}

/**
 * 智能填充 - 处理输入框
 *
 * @param page Playwright Page 对象
 * @param selector CSS 选择器
 * @param text 要填充的文本
 * @param browserName 浏览器名称
 */
export async function smartFill(
  page: Page,
  selector: string,
  text: string,
  browserName: string = 'chromium'
): Promise<void> {
  try {
    await smartWaitForElement(page, selector, browserName)

    const input = page.locator(selector).first()
    await input.fill(text)
  } catch (error) {
    throw new Error(`Failed to fill ${selector}: ${error}`)
  }
}

/**
 * 智能文本等待 - 等待特定文本出现
 *
 * @param page Playwright Page 对象
 * @param text 要等待的文本
 * @param browserName 浏览器名称
 */
export async function smartWaitForText(
  page: Page,
  text: string,
  browserName: string = 'chromium'
): Promise<void> {
  const config = getBrowserConfig(browserName)

  try {
    await page.waitForFunction(
      (searchText) => document.body.innerText.includes(searchText),
      text,
      { timeout: config.selectTimeout }
    )
  } catch (error) {
    throw new Error(`Text not found: ${text}`)
  }
}

/**
 * 设置页面默认超时 - 根据浏览器调整
 *
 * @param page Playwright Page 对象
 * @param browserName 浏览器名称
 */
export function setPageTimeouts(page: Page, browserName: string): void {
  const config = getBrowserConfig(browserName)
  page.setDefaultTimeout(config.selectTimeout)
  page.setDefaultNavigationTimeout(config.navigationTimeout)
}

/**
 * 获取浏览器标识
 *
 * @param context Playwright BrowserContext
 */
export function getBrowserName(context: BrowserContext): string {
  const browser = context.browser()
  return browser?.browserType().name() || 'chromium'
}

/**
 * 重试函数 - 通用重试机制
 *
 * @param fn 要重试的异步函数
 * @param maxRetries 最大重试次数
 * @param delayMs 重试延迟 (ms)
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let lastError: Error | null = null

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error

      if (attempt < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, delayMs))
      }
    }
  }

  throw lastError || new Error('Retry failed')
}
