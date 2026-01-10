const { test, expect } = require('@playwright/test');

test.describe('Bloomberg Terminal Style Pages', () => {
  test.beforeEach(async ({ page }) => {
    // Set viewport size for desktop testing
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('Market Overview Page', async ({ page }) => {
    console.log('Navigating to Market page...');
    await page.goto('http://localhost:3020/#/market/list');

    // Wait for H1 element to be present
    await page.waitForSelector('h1', { timeout: 10000 });

    // Take screenshot
    await page.screenshot({
      path: '/tmp/market-page.png',
      fullPage: false
    });

    // Check for Bloomberg-style elements
    const h1Elements = await page.$$('h1');
    console.log('H1 elements found:', h1Elements.length);

    // Check for stat cards
    const statCards = await page.$$('.stats-grid .bloomberg-stat-card, .stats-grid > div');
    console.log('Stat cards found:', statCards.length);

    // Verify page has content
    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('MARKET OVERVIEW');
    expect(h1Elements.length).toBeGreaterThanOrEqual(1);
  });

  test('Dashboard Page', async ({ page }) => {
    console.log('Navigating to Dashboard page...');
    await page.goto('http://localhost:3020/#/dashboard');

    // Wait for H1 element to be present
    await page.waitForSelector('h1', { timeout: 10000 });

    // Take screenshot
    await page.screenshot({
      path: '/tmp/dashboard-page.png',
      fullPage: false
    });

    // Check for Bloomberg-style elements
    const h1Elements = await page.$$('h1');
    console.log('H1 elements found:', h1Elements.length);

    // Check for stat cards using a more specific selector
    const statCards = await page.$$('.stats-grid .bloomberg-stat-card, .stats-grid > div');
    console.log('Stat cards found:', statCards.length);

    // Verify page has content
    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('MARKET OVERVIEW');
    expect(h1Elements.length).toBeGreaterThanOrEqual(1);
  });

  test('Trade Management Page', async ({ page }) => {
    console.log('Navigating to Trade Management page...');
    await page.goto('http://localhost:3020/#/trade');

    // Wait for any content to load - check for the container
    await page.waitForSelector('.trade-management-container', { timeout: 10000 });

    // Take screenshot
    await page.screenshot({
      path: '/tmp/trade-management-page.png',
      fullPage: false
    });

    // Check for Bloomberg-style elements
    const h1Elements = await page.$$('h1');
    console.log('H1 elements found:', h1Elements.length);

    // Check for tabs
    const tabs = await page.$$('.bloomberg-tab, .el-tab-pane, .tab');
    console.log('Tabs found:', tabs.length);

    // Verify page has content
    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();

    // Check if container exists
    const container = await page.$('.trade-management-container');
    expect(container).not.toBeNull();
  });

  test('Check for Console Errors', async ({ page }) => {
    const errors = [];
    const warnings = [];

    page.on('console', msg => {
      const text = msg.text();
      if (msg.type() === 'error') {
        // Filter out CSP frame-ancestors warning (browser-specific, not critical)
        if (!text.includes('frame-ancestors') && !text.includes('Content Security Policy')) {
          errors.push(text);
          console.log('❌ Console error:', text);
        }
      }
      if (msg.type() === 'warning') {
        warnings.push(text);
      }
    });

    await page.goto('http://localhost:3020/#/market/list');
    await page.waitForSelector('h1', { timeout: 10000 });

    console.log('Console errors found:', errors.length);
    console.log('Console warnings found:', warnings.length);

    // Log error details for debugging
    if (errors.length > 0) {
      console.log('Error details:', errors);
    }

    // Allow some warnings but check for critical errors
    expect(errors.length).toBe(0);
  });

  test('Diagnose Infinite Loop - Dashboard', async ({ page }) => {
    console.log('🔍 Diagnosing Dashboard page...');
    await page.goto('http://localhost:3020/#/dashboard');
    await page.waitForSelector('h1', { timeout: 10000 });

    // Get page dimensions
    const dimensions = await page.evaluate(() => {
      return {
        scrollHeight: document.documentElement.scrollHeight,
        scrollWidth: document.documentElement.scrollWidth,
        bodyChildren: document.body.children.length,
        h1Count: document.querySelectorAll('h1').length,
        statCardCount: document.querySelectorAll('.bloomberg-stat-card, .stat-card').length
      };
    });

    console.log('📊 Dashboard Dimensions:', JSON.stringify(dimensions, null, 2));

    // Check for duplicates
    if (dimensions.h1Count > 5) {
      console.warn(`⚠️ Too many H1 tags found: ${dimensions.h1Count}`);
    }

    if (dimensions.statCardCount > 10) {
      console.warn(`⚠️ Too many stat cards found: ${dimensions.statCardCount}`);
    }

    // Screenshot for visual inspection
    await page.screenshot({
      path: '/tmp/dashboard-diagnosis.png',
      fullPage: false
    });

    console.log('✅ Diagnosis complete');
  });

  test('Diagnose Infinite Loop - Market', async ({ page }) => {
    console.log('🔍 Diagnosing Market page...');
    await page.goto('http://localhost:3020/#/market/list');
    await page.waitForSelector('h1', { timeout: 10000 });

    // Get page dimensions
    const dimensions = await page.evaluate(() => {
      return {
        scrollHeight: document.documentElement.scrollHeight,
        scrollWidth: document.documentElement.scrollWidth,
        bodyChildren: document.body.children.length,
        h1Count: document.querySelectorAll('h1').length,
        statCardCount: document.querySelectorAll('.bloomberg-stat-card, .stat-card').length
      };
    });

    console.log('📊 Market Dimensions:', JSON.stringify(dimensions, null, 2));

    // Check for duplicates
    if (dimensions.h1Count > 5) {
      console.warn(`⚠️ Too many H1 tags found: ${dimensions.h1Count}`);
    }

    if (dimensions.statCardCount > 10) {
      console.warn(`⚠️ Too many stat cards found: ${dimensions.statCardCount}`);
    }

    // Screenshot for visual inspection
    await page.screenshot({
      path: '/tmp/market-diagnosis.png',
      fullPage: false
    });

    console.log('✅ Diagnosis complete');
  });

  test('Performance Monitoring - Page Load Metrics', async ({ page }) => {
    const pages = [
      { name: 'Dashboard', url: 'http://localhost:3020/#/dashboard' },
      { name: 'Market', url: 'http://localhost:3020/#/market/list' },
      { name: 'Trade Management', url: 'http://localhost:3020/#/trade' }
    ];

    const performanceResults = [];

    for (const pageInfo of pages) {
      console.log(`\n📊 Testing performance for ${pageInfo.name}...`);

      // Clear cache for accurate measurement
      await page.context().clearCookies();
      await page.goto('about:blank');

      const startTime = Date.now();

      // Navigate and wait for page load
      await page.goto(pageInfo.url);

      // Wait for main content to load
      await page.waitForSelector('h1, .trade-management-container', { timeout: 15000 });

      const loadTime = Date.now() - startTime;

      // Get performance metrics
      const metrics = await page.evaluate(() => {
        const perfData = performance.getEntriesByType('navigation')[0];
        return {
          domContentLoaded: Math.round(perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart),
          loadComplete: Math.round(perfData.loadEventEnd - perfData.loadEventStart),
          domInteractive: Math.round(perfData.domInteractive - perfData.fetchStart),
          firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
          firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
        };
      });

      const result = {
        page: pageInfo.name,
        totalLoadTime: loadTime,
        ...metrics
      };

      performanceResults.push(result);

      console.log(`  ⏱️  Total Load Time: ${loadTime}ms`);
      console.log(`  📄 DOM Content Loaded: ${metrics.domContentLoaded}ms`);
      console.log(`  ✅ Load Complete: ${metrics.loadComplete}ms`);
      console.log(`  🎨 DOM Interactive: ${metrics.domInteractive}ms`);
      console.log(`  🖌️  First Paint: ${Math.round(metrics.firstPaint)}ms`);
      console.log(`  📝 First Contentful Paint: ${Math.round(metrics.firstContentfulPaint)}ms`);

      // Performance assertions
      expect(loadTime).toBeLessThan(5000); // Page should load in under 5 seconds
      expect(metrics.domInteractive).toBeLessThan(3000); // DOM should be interactive in under 3 seconds
    }

    // Log summary
    console.log('\n📊 Performance Summary:');
    console.log('─'.repeat(80));
    performanceResults.forEach(result => {
      console.log(`${result.page}:`);
      console.log(`  Total Load: ${result.totalLoadTime}ms`);
      console.log(`  DOM Interactive: ${result.domInteractive}ms`);
    });
    console.log('─'.repeat(80));

    // Calculate average load time
    const avgLoadTime = performanceResults.reduce((sum, r) => sum + r.totalLoadTime, 0) / performanceResults.length;
    console.log(`\n📈 Average Page Load Time: ${Math.round(avgLoadTime)}ms`);

    // Performance expectations
    expect(avgLoadTime).toBeLessThan(4000); // Average should be under 4 seconds
  });
});
