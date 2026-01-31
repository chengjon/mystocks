import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    await page.goto('http://localhost:3001/#/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Get full page structure
    const structure = await page.evaluate(() => {
      const result = {
        baseLayout: !!document.querySelector('.base-layout'),
        layoutHeader: !!document.querySelector('.layout-header'),
        layoutSidebar: !!document.querySelector('.layout-sidebar'),
        layoutMain: !!document.querySelector('.layout-main'),
        sidebarToggle: !!document.querySelector('.sidebar-toggle'),
        
        // Count all navigation elements
        allLinks: document.querySelectorAll('a').length,
        allButtons: document.querySelectorAll('button').length,
        
        // Get header content
        headerText: document.querySelector('.layout-header')?.textContent?.trim().substring(0, 100) || '',
        
        // Get sidebar structure
        sidebarChildren: document.querySelector('.layout-sidebar')?.children.length || 0,
        
        // Look for top menu
        topMenu: document.querySelector('[class*="top"], [class*="nav"], [class*="menu"]')?.className || ''
      };
      
      return result;
    });

    console.log('[LAYOUT STRUCTURE]');
    Object.entries(structure).forEach(([key, value]) => {
      console.log('  ' + key + ':', value);
    });

    // Take full page screenshot
    await page.screenshot({ path: 'full-layout.png', fullPage: true });
    console.log('[SCREENSHOT] Saved to full-layout.png');

  } finally {
    await browser.close();
  }
})();
