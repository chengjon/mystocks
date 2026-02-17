import { test, expect } from '@playwright/test';
import { ARTDECO_MENU_ITEMS } from '../src/layouts/MenuConfig';

// -----------------------------------------------------------------------------
// 配置
// -----------------------------------------------------------------------------
const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const BASE_URL = `http://localhost:${FRONTEND_PORT}`;

/**
 * 展平菜单树，获取所有待测路径
 */
function getAllPaths(items: any[]): string[] {
  let paths: string[] = [];
  for (const item of items) {
    if (item.path && !item.children) {
      paths.push(item.path);
    }
    if (item.children) {
      paths.push(...getAllPaths(item.children));
    }
  }
  return paths;
}

const allPagePaths = getAllPaths(ARTDECO_MENU_ITEMS);

test.describe('全页面地毯式冒烟测试 (Full Site Crawl)', () => {
  
  test.beforeEach(async ({ page }) => {
    // 注入 Token 绕过登录
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'smoke-test-token');
      localStorage.setItem('auth_user', JSON.stringify({
        id: 1, username: 'admin', role: 'admin', permissions: ['*']
      }));
    });
  });

  // 为每个路径创建一个独立的测试用例
  for (const path of allPagePaths) {
    test(`巡检页面: ${path}`, async ({ page }) => {
      console.log(`正在检查: ${BASE_URL}${path}`);
      
      const response = await page.goto(`${BASE_URL}${path}`, { 
        waitUntil: 'networkidle',
        timeout: 30000 
      });

      // 1. 验证 HTTP 状态 (200 OK)
      expect(response?.status()).toBe(200);

      // 2. 验证是否被拦截回登录页 (如果地址变成了 /login 说明 Token 失效或路由守卫有问题)
      expect(page.url()).not.toContain('/login');

      // 3. 验证基础布局
      const sidebar = page.locator('.artdeco-collapsible-sidebar');
      await expect(sidebar).toBeVisible({ timeout: 5000 });

      const mainContent = page.locator('.artdeco-main');
      await expect(mainContent).toBeVisible();

      // 4. 验证内容渲染 (非白屏)
      // 检查 body 是否有实质性内容 (不仅仅是空白的 div)
      const bodyText = await page.locator('body').innerText();
      expect(bodyText.length).toBeGreaterThan(100); 

      // 5. 截图存档 (可选，用于人工二次确认)
      // await page.screenshot({ path: `tests/screenshots/${path.replace(/\//g, '_')}.png` });
    });
  }
});
