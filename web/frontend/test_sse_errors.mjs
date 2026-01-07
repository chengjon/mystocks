import { chromium } from 'playwright';

const BASE_URL = 'http://localhost:3020';
const PAGE_URL = '/market/realtime';

async function captureConsoleErrors() {
  console.log('🔍 Capturing console errors for realtime monitoring page...\n');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // Collect all console messages
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push({
      type: msg.type(),
      text: msg.text(),
      location: msg.location()
    });
  });

  // Collect network errors
  const networkErrors = [];
  page.on('response', response => {
    if (response.status() >= 400) {
      networkErrors.push({
        url: response.url(),
        status: response.status(),
        statusText: response.statusText()
      });
    }
  });

  try {
    console.log(`📄 Navigating to: ${BASE_URL}${PAGE_URL}`);
    await page.goto(BASE_URL + PAGE_URL, {
      waitUntil: 'networkidle',
      timeout: 15000
    });

    // Wait to collect errors
    await page.waitForTimeout(3000);

    console.log(`\n📊 Collected ${consoleMessages.length} console messages\n`);
    console.log('=' .repeat(80));

    // Filter for errors and warnings
    const errors = consoleMessages.filter(msg => msg.type === 'error');
    const warnings = consoleMessages.filter(msg => msg.type === 'warning');

    console.log(`\n🔴 ERRORS (${errors.length}):\n`);
    errors.forEach((err, index) => {
      console.log(`[${index + 1}] ${err.text}`);
      if (err.location) {
        console.log(`    Location: ${err.location.url}:${err.location.lineNumber}`);
      }
      console.log('');
    });

    console.log(`\n🟡 WARNINGS (${warnings.length}):\n`);
    warnings.slice(0, 10).forEach((warn, index) => {
      console.log(`[${index + 1}] ${warn.text}`);
      if (warn.location && warn.location.url && !warn.location.url.includes('node_modules')) {
        console.log(`    Location: ${warn.location.url}:${warn.location.lineNumber}`);
      }
      console.log('');
    });

    if (networkErrors.length > 0) {
      console.log(`\n❌ NETWORK ERRORS (${networkErrors.length}):\n`);
      networkErrors.forEach((err, index) => {
        console.log(`[${index + 1}] ${err.status} ${err.statusText}`);
        console.log(`    URL: ${err.url}`);
        console.log('');
      });
    }

    console.log('=' .repeat(80));

  } catch (error) {
    console.error(`❌ Error capturing console: ${error.message}`);
  }

  await browser.close();
  console.log('\n✅ Capture complete!\n');
}

captureConsoleErrors().catch(error => {
  console.error('Test failed:', error);
  process.exit(1);
});
