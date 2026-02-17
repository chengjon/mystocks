import { test, expect } from '@playwright/test';

const FRONTEND_URL = 'http://localhost:3020';

test('Debug Menu Visibility', async ({ page }) => {
  // 1. 注入 Token
  await page.addInitScript(() => {
    localStorage.setItem('auth_token', 'mock-token-debug');
    localStorage.setItem('auth_user', JSON.stringify({
      id: 1, username: 'admin', role: 'admin', permissions: ['*']
    }));
  });

  await page.goto(`${FRONTEND_URL}/dashboard`);
  await page.waitForTimeout(2000); // 等待动画完全结束

  // 2. 截图
  await page.screenshot({ path: 'sidebar-debug-full.png', fullPage: true });
  const sidebar = page.locator('.artdeco-collapsible-sidebar');
  const sidebarStyles = await sidebar.evaluate(el => {
      return {
          bg: window.getComputedStyle(el).backgroundColor,
          color: window.getComputedStyle(el).color
      }
  });
  console.log('🎨 Sidebar 颜色诊断:', sidebarStyles);

  await sidebar.screenshot({ path: 'sidebar-debug-component.png' });
  console.log('📸 截图已保存: sidebar-debug-full.png, sidebar-debug-component.png');

  // 3. 诊断菜单项
  const menuSections = page.locator('.artdeco-nav-section');
  const count = await menuSections.count();
  console.log(`
🔍 检测到 ${count} 个菜单区块`);

  if (count > 0) {
    const firstSection = menuSections.first();
    
    // 获取计算样式
    const styles = await firstSection.evaluate((el) => {
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return {
        opacity: style.opacity,
        visibility: style.visibility,
        display: style.display,
        zIndex: style.zIndex,
        position: style.position,
        height: style.height,
        width: style.width,
        color: style.color,
        backgroundColor: style.backgroundColor,
        rect: {
          top: rect.top,
          left: rect.left,
          width: rect.width,
          height: rect.height
        },
        classList: el.className
      };
    });

    console.log('🧐 第一菜单区块样式诊断:', JSON.stringify(styles, null, 2));

    // 4. 诊断遮挡 (Z-Index Check)
    // 检查 pattern 是否遮挡
    const pattern = page.locator('.artdeco-sidebar-pattern');
    const patternZ = await pattern.evaluate(el => window.getComputedStyle(el).zIndex);
    console.log(`🛡️ 背景纹理 z-index: ${patternZ} (应小于菜单的 ${styles.zIndex})`);
    
    // 5. 检查内部内容
    const navItem = firstSection.locator('.artdeco-nav-item, .artdeco-nav-item-parent').first();
    const navItemStyles = await navItem.evaluate((el) => {
       const style = window.getComputedStyle(el);
       return {
         opacity: style.opacity,
         color: style.color,
         height: style.height,
         innerText: (el as HTMLElement).innerText
       }
    });
    console.log('📝 菜单项内容诊断:', JSON.stringify(navItemStyles, null, 2));
  }
});
