const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  // Capture console logs
  page.on('console', msg => {
    console.log(`[console ${msg.type()}] ${msg.text()}`);
  });

  // Capture page errors
  page.on('pageerror', error => {
    console.error('[page error]', error.message);
  });

  // Capture request failures
  page.on('requestfailed', request => {
    console.error('[request failed]', request.url(), request.failure().errorText);
  });

  await page.goto('http://localhost:3020/dealing-room');
  console.log('=== Page loaded, waiting for Vue app ===');

  // Wait for Vue app to mount
  try {
    await page.waitForSelector('#app', { timeout: 5000 });
    console.log('=== #app found ===');
  } catch (_error) {
    console.log('=== #app NOT found ===');
  }

  // Wait for app to render
  await page.waitForTimeout(3000);

  // Check app inner HTML
  const appHtml = await page.$eval('#app', el => el.innerHTML.substring(0, 500));
  console.log('=== #app inner HTML (first 500 chars): ===');
  console.log(appHtml);

  // Get all elements with class containing 'artdeco'
  const artdecoElements = await page.evaluate(() => {
    const all = document.querySelectorAll('*[class*="artdeco"]');
    return Array.from(all).map(el => ({
      tag: el.tagName,
      class: el.className,
      visible: el.offsetParent !== null
    }));
  });
  console.log('=== ArtDeco elements found:', artdecoElements.length, '===');
  artdecoElements.forEach(el => {
    console.log(`  ${el.tag}.${el.class.split(' ')[0]} - visible: ${el.visible}`);
  });

  // Check if sidebar element exists in DOM at all
  const sidebarExists = await page.evaluate(() => {
    return document.querySelector('.artdeco-sidebar-v3') !== null;
  });
  console.log('=== Sidebar exists in DOM:', sidebarExists, '===');

  if (sidebarExists) {
    const sidebarVisible = await page.evaluate(() => {
      const el = document.querySelector('.artdeco-sidebar-v3');
      return el && el.offsetParent !== null;
    });
    console.log('=== Sidebar visible:', sidebarVisible, '===');

    const sidebarStyles = await page.evaluate(() => {
      const el = document.querySelector('.artdeco-sidebar-v3');
      if (!el) return null;
      const computed = window.getComputedStyle(el);
      return {
        display: computed.display,
        visibility: computed.visibility,
        opacity: computed.opacity,
        width: computed.width,
        height: computed.height
      };
    });
    console.log('=== Sidebar styles:', JSON.stringify(sidebarStyles, null, 2), '===');
  }

  // Take screenshot
  await page.screenshot({ path: 'debug-screenshot2.png', fullPage: true });
  console.log('=== Screenshot saved to debug-screenshot2.png ===');

  await page.waitForTimeout(5000);
  await browser.close();
})();
