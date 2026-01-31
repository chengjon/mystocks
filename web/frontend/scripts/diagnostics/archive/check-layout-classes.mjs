import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    await page.goto('http://localhost:3001/#/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const classes = await page.evaluate(() => {
      const result = {};
      
      // Check all expected classes
      const selectors = [
        '.base-layout',
        '.layout-header', 
        '.layout-sidebar',
        '.layout-main',
        '.artdeco-dashboard',
        '.sidebar-toggle'
      ];
      
      selectors.forEach(sel => {
        const el = document.querySelector(sel);
        result[sel] = {
          exists: !!el,
          visible: el ? getComputedStyle(el).display !== 'none' : false
        };
      });
      
      // Get actual body classes
      result.bodyClasses = document.body.className;
      
      // Get app children structure
      const app = document.querySelector('#app');
      if (app) {
        result.appChildren = Array.from(app.children).map(child => ({
          tag: child.tagName,
          className: child.className,
          id: child.id
        }));
      }
      
      return result;
    });

    console.log('[LAYOUT CHECK]');
    Object.entries(classes).forEach(([key, value]) => {
      if (typeof value === 'object') {
        console.log(key + ':', JSON.stringify(value, null, 2));
      } else {
        console.log(key + ':', value);
      }
    });

  } finally {
    await browser.close();
  }
})();
