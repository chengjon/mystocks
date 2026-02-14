const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Starting Business Data Verification...');
  const browser = await chromium.launch({ 
    headless: true,
    executablePath: '/root/.cache/ms-playwright/chromium-1200/chrome-linux64/chrome'
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Inject Auth Token
  await page.addInitScript(() => {
    localStorage.setItem('auth_token', 'e2e-test-token-2026');
  });

  // Proxy console messages
  page.on('console', msg => console.log(`🖥️ [Browser Console] ${msg.text()}`));

  const url = process.argv[2] || 'http://localhost:3007/market/realtime';
  console.log(`🌐 Navigating to: ${url}`);

  // Listen for API requests
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      console.log(`📡 [API Call] ${request.method()} ${request.url()}`);
    }
  });

  // Listen for API responses
  page.on('response', async response => {
    if (response.url().includes('/api/v1/market/quotes')) {
      const status = response.status();
      console.log(`✅ [API Response] ${response.url()} - Status: ${status}`);
      if (status === 200) {
          try {
              const data = await response.json();
              console.log('📊 [Data Sample] Found', (data.data?.quotes || []).length, 'quotes');
          } catch (e) {
              console.log('⚠️ [Data Error] Failed to parse JSON');
          }
      }
    }
  });

  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    console.log('⌛ Waiting for data rendering (5s)...');
    await page.waitForTimeout(5000);

    // Check DOM for data
    const pageText = await page.innerText('body');
    const hasDashboardData = pageText.includes('指挥中心') || pageText.includes('上证指数');
    
    console.log(`🏁 [Result] Dashboard Text Present: ${hasDashboardData}`);

    if (hasDashboardData) {
      console.log('🎉 SUCCESS: Dashboard is rendering real content!');
    } else {
      console.log('❌ FAILURE: Dashboard content not found.');
    }

  } catch (error) {
    console.error('❌ Verification Error:', error.message);
  }

  await browser.close();
})();
