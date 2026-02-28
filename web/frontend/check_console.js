const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const logs = [];
  page.on('console', msg => {
    logs.push({ type: msg.type(), text: msg.text() });
  });

  page.on('pageerror', error => {
    console.log('PAGE ERROR:', error);
  });

  await page.goto('http://localhost:3020/dealing-room');
  await page.waitForTimeout(3000);

  console.log('=== Console Logs ===');
  logs.forEach(log => {
    console.log(`[${log.type}] ${log.text}`);
  });

  await browser.close();
})();
