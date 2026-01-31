import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:3001/#/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // Check for .nav-item
    const navItems = await page.locator('.nav-item').count();
    console.log('[.nav-item] Count:', navItems);
    
    // Get text content of nav items
    const navTexts = await page.locator('.nav-item').allTextContents();
    console.log('[.nav-item] Texts:', navTexts.slice(0, 10));
    
    // Check for .sidebar-toggle
    const toggle = await page.locator('.sidebar-toggle').count();
    console.log('[.sidebar-toggle] Count:', toggle);
    
    // Check for .layout-sidebar
    const sidebar = await page.locator('.layout-sidebar').count();
    console.log('[.layout-sidebar] Count:', sidebar);
    
    // Check for Chinese menu labels
    for (const label of ['仪表盘', '市场行情', '股票管理']) {
      const count = await page.locator(`text=${label}`).count();
      console.log(`[text=${label}] Count:`, count);
    }
    
    // Take screenshot
    await page.screenshot({ path: 'menu-structure.png' });
    console.log('[SCREENSHOT] Saved');
    
  } finally {
    await browser.close();
  }
})();
