const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Capture all console messages
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    console.log('[Console ' + type.toUpperCase() + '] ' + text);
  });
  
  // Capture page errors
  page.on('pageerror', error => {
    console.error('[PAGE ERROR] ' + error.message);
    console.error('Stack: ' + error.stack);
  });
  
  // Capture request failures
  page.on('requestfailed', request => {
    console.error('[REQUEST FAILED] ' + request.url() + ' - ' + request.failure().errorText);
  });
  
  try {
    console.log('Navigating to http://localhost:3020/');
    await page.goto('http://localhost:3020/', { waitUntil: 'networkidle', timeout: 30000 });
    
    console.log('Page loaded!');
    console.log('Page Title: ' + await page.title());
    
    // Wait a bit for Vue to mount
    await page.waitForTimeout(3000);
    
    // Check for #app element
    const appElement = await page.$('#app');
    console.log('#app element exists: ' + !!appElement);
    
    if (appElement) {
      const appHTML = await appElement.innerHTML();
      console.log('#app innerHTML length: ' + appHTML.length + ' characters');
      console.log('#app innerHTML preview: ' + appHTML.substring(0, 500));
    }
    
    // Check for router-view
    const routerView = await page.$('router-view');
    console.log('router-view element exists: ' + !!routerView);
    
    // Check for MainLayout
    const mainLayout = await page.$('.main-layout, .artdeco-dashboard');
    console.log('MainLayout/ArtDecoDashboard element exists: ' + !!mainLayout);
    
    // Take screenshot
    await page.screenshot({ 
      path: '/opt/claude/mystocks_spec/docs/reports/artdeco-dashboard-full-debug.png',
      fullPage: true 
    });
    console.log('Screenshot saved');
    
  } catch (error) {
    console.error('Test failed: ' + error.message);
  } finally {
    await browser.close();
  }
})();
