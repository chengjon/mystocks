import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3020';

// 定义关键页面及其预期可见的元素（证明渲染成功）
const PAGES = [
  { name: 'Dashboard', path: '/dashboard', selector: '.art-deco-card', desc: '仪表盘卡片' },
  { name: 'Market Data', path: '/market/data', selector: '.el-table__body', desc: '行情数据表格' },
  { name: 'Analysis', path: '/analysis/data', selector: '.chart-container', desc: '分析图表' },
  { name: 'Backtest', path: '/strategy/backtest', selector: 'button:has-text("运行回测")', desc: '回测控制按钮' }
];

test.describe('Ralph Wiggum Strict Verification', () => {
  for (const pageCfg of PAGES) {
    test(`Verify ${pageCfg.name} (${pageCfg.path})`, async ({ page }) => {
      const consoleErrors: string[] = [];
      const failedRequests: string[] = [];

      // 1. 捕获控制台错误
      page.on('console', msg => {
        if (msg.type() === 'error') {
          // 忽略一些非致命的样式警告或特定的已知噪音
          const text = msg.text();
          if (!text.includes('deprecated') && !text.includes('HMR')) {
            consoleErrors.push(`[Console] ${text}`);
          }
        }
      });

      // 2. 捕获网络失败
      page.on('response', res => {
        if (res.status() >= 400) {
          failedRequests.push(`[Network] ${res.status()} ${res.url()}`);
        }
      });

      // 3. 访问页面
      console.log(`Navigating to ${pageCfg.name}...`);
      await page.goto(`${BASE_URL}${pageCfg.path}`);

      // 等待网络空闲，确保数据加载完成
      try {
        await page.waitForLoadState('networkidle', { timeout: 5000 });
      } catch (e) {
        console.log(`Network idle timeout on ${pageCfg.name}, continuing check...`);
      }

      // 4. 验证关键元素可见性 (这是判断页面是否"白屏"的核心)
      const element = page.locator(pageCfg.selector).first();
      await expect(element).toBeVisible({ timeout: 10000 });

      // 5. 断言检查
      if (consoleErrors.length > 0) {
        console.log(`\n🔴 Console Errors on ${pageCfg.name}:`);
        consoleErrors.forEach(e => console.log(e));
      }
      expect(consoleErrors, `Found console errors on ${pageCfg.name}`).toEqual([]);
      expect(failedRequests, `Found failed network requests on ${pageCfg.name}`).toEqual([]);
    });
  }
});
