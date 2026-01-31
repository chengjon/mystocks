import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:3001/#/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // Check page title
    const title = await page.title();
    console.log('[PAGE] Title:', title);
    
    // Check for nav items
    const navItems = await page.locator('.nav-item, .menu-item, [class*="nav"], [class*="menu"]').count();
    console.log('[CHECK] Nav items found:', navItems);
    
    // Check for sidebar
    const sidebar = await page.locator('.sidebar, .layout-sidebar, [class*="sidebar"]').count();
    console.log('[CHECK] Sidebar elements found:', sidebar);
    
    // Check main content area
    const mainContent = await page.locator('main, .main-content, [class*="content"]').count();
    console.log('[CHECK] Main content areas:', mainContent);
    
    // Get visible text
    const visibleText = await page.locator('body').innerText();
    console.log('[CHECK] Visible text length:', visibleText.length);
    
    // Check for common dashboard elements
    const hasDashboard = await page.locator('text=Dashboard').count();
    const hasOverview = await page.locator('text=Overview').count();
    console.log('[CHECK] Has "Dashboard":', hasDashboard, 'Has "Overview":', hasOverview);
    
    // Take screenshot
    await page.screenshot({ path: 'dashboard-current.png', fullPage: true });
    console.log('[SCREENSHOT] Saved to dashboard-current.png');
    
  } finally {
    await browser.close();
  }
})();
