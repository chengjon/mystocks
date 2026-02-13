/**
 * MyStocks Full Page Testing Script v2
 * Connects to Chrome via CDP, unregisters service workers,
 * logs in via API, visits every page, captures real errors.
 */
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const playwrightPath = '/opt/claude/mystocks_spec/web/frontend/node_modules/playwright';
const { chromium } = require(playwrightPath);
const { URL } = require('url');

const AUTH_BOOTSTRAP = {
  token: 'e2e-test-token',
  user: {
    id: 1,
    username: 'admin',
    role: 'admin',
    email: 'admin@mystocks.com',
    permissions: []
  }
};

const BASE_URL = 'http://localhost:3020';
const CDP_URL = 'http://localhost:9222';

const ROUTES = [
  '/login',
  '/dashboard',
  '/market/realtime',
  '/market/overview',
  '/market/analysis',
  '/market/industry',
  '/market/technical',
  '/market/fund-flow',
  '/market/etf',
  '/market/concept',
  '/market/auction',
  '/market/chip-race',
  '/market/institution',
  '/market/lhb',
  '/market/sentiment',
  '/market/wencai',
  '/market/tdx-market',
  '/stocks/list',
  '/stocks/screener',
  '/stocks/stock-detail/000001',
  '/stocks/watchlists',
  '/stocks/analysis/industry-concept',
  '/trading/portfolio',
  '/trading/positions',
  '/trading/trade',
  '/trading/history',
  '/trading/risk',
  '/strategy/management',
  '/strategy/backtest',
  '/strategy/signals',
  '/strategy/performance',
  '/strategy/optimization',
  '/strategy/attribution',
  '/strategy/gpu-backtest',
  '/risk/overview',
  '/risk/position',
  '/risk/portfolio',
  '/risk/alerts',
  '/monitoring/dashboard',
  '/monitoring/data-quality',
  '/monitoring/performance',
  '/monitoring/api-health',
  '/monitoring/gpu-monitoring',
  '/system/settings',
  '/system/data-update',
  '/system/announcement',
  '/system/tasks',
  '/system/design',
  '/system/architecture',
  '/system/database-monitor',
  '/market-data/indicators',
  '/market-data/longhubang',
  '/market-data/smart-data-test',
  '/artdeco/test',
  '/artdeco/skeleton-demo',
  '/artdeco/market',
  '/artdeco/market-quotes',
  '/artdeco/analysis',
  '/artdeco/backtest',
  '/artdeco/risk',
  '/artdeco/settings',
  '/artdeco/stock-management',
  '/artdeco/trading',
  '/strategy-hub/strategy-mgmt',
  '/strategy-hub/backtest',
  '/strategy-hub/signals',
  '/strategy-hub/performance',
  '/strategy-hub/optimization',
  '/strategy-hub/attribution',
  '/strategy-hub/gpu-backtest',
  '/strategy-hub/freqtrade-demo',
  '/strategy-hub/openstock-demo',
  '/strategy-hub/pyprofiling-demo',
  '/strategy-hub/stock-analysis-demo',
  '/strategy-hub/tdxpy-demo',
  '/risk-monitor/overview',
  '/risk-monitor/position',
  '/risk-monitor/portfolio',
  '/risk-monitor/alerts',
  '/phase4-dashboard',
  '/strategy-mgmt-phase4',
  '/test',
];

// Known ignorable errors (not real page issues)
const IGNORABLE_PATTERNS = [
  'Failed to load resource: the server responded with a status of 503',
  'Failed to load resource: the server responded with a status of 404',
  'favicon',
  'manifest.json',
  'sw.js',
  '/api/contracts/',
  'net::ERR_CONNECTION_REFUSED',
  'net::ERR_FAILED',
  'ResizeObserver loop',
  'Non-Error promise rejection',
];

function isIgnorable(msg) {
  return IGNORABLE_PATTERNS.some(p => msg.includes(p));
}

async function main() {
  console.log('🔗 Connecting to Chrome via CDP...');

  let browser;
  try {
    browser = await chromium.connectOverCDP(CDP_URL);
    console.log('  ✅ Connected to existing Chrome');
  } catch (e) {
    console.log('  ⚠️ CDP not available, launching Playwright Chromium...');
    browser = await chromium.launch({
      headless: true,
      chromiumSandbox: false,
      args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-setuid-sandbox'],
    });
  }

  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();

  // Preload auth state before app bootstrap
  await context.addInitScript((bootstrap) => {
    localStorage.setItem('token', bootstrap.token);
    localStorage.setItem('auth_token', bootstrap.token);
    localStorage.setItem('user', JSON.stringify(bootstrap.user));
    localStorage.setItem('auth_user', JSON.stringify(bootstrap.user));
  }, AUTH_BOOTSTRAP);

  // Step 0: Unregister all service workers
  console.log('\n📋 Step 0: Unregistering service workers...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(2000);

  const swCount = await page.evaluate(async () => {
    const registrations = await navigator.serviceWorker.getRegistrations();
    for (const reg of registrations) {
      await reg.unregister();
    }
    return registrations.length;
  });
  console.log(`  ✅ Unregistered ${swCount} service worker(s)`);

  // Reload to ensure SW is gone
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);

  // Step 1: Verify authenticated navigation
  console.log('\n📋 Step 1: Verifying authenticated session...');
  try {
    await page.goto(`${BASE_URL}/dashboard`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(1500);

    const currentPath = await page.evaluate(() => window.location.pathname);
    if (currentPath === '/login') {
      throw new Error('Auth bootstrap failed: navigation still redirects to /login');
    }

    console.log(`  ✅ Auth bootstrap verified (current path: ${currentPath})`);
  } catch (e) {
    console.log(`  ❌ Auth verification error: ${e.message}`);
  }

  // Step 2: Visit each page
  const results = { pass: [], fail: [], errors: {} };
  console.log(`\n📋 Step 2: Testing ${ROUTES.length} pages...\n`);

  for (let i = 0; i < ROUTES.length; i++) {
    const route = ROUTES[i];
    const pageErrors = [];
    const consoleErrors = [];

    const onConsoleMsg = (msg) => {
      if (msg.type() === 'error') {
        const text = msg.text();
        if (!isIgnorable(text)) {
          consoleErrors.push(text);
        }
      }
    };
    page.on('console', onConsoleMsg);

    const onPageError = (err) => {
      pageErrors.push(err.message);
    };
    page.on('pageerror', onPageError);

    try {
      const url = `${BASE_URL}${route}`;
      const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(2500);

      const status = response?.status() || 0;
      const title = await page.title();
      const finalUrl = page.url();
      const finalPath = new URL(finalUrl).pathname;
      const redirectedToLogin = route !== '/login' && finalPath === '/login';

      // Check for white screen
      const bodyText = await page.evaluate(() => document.body?.innerText?.trim().length || 0);
      const hasContent = bodyText > 10;

      // Check for Vite error overlay
      const hasViteError = await page.evaluate(() => {
        return !!document.querySelector('vite-error-overlay');
      });

      // Check for Vue runtime errors in the DOM
      const hasVueError = await page.evaluate(() => {
        const el = document.querySelector('.error-boundary, [class*="error"]');
        return el ? el.textContent?.substring(0, 100) : null;
      });

      const hasIssues = !hasContent || hasViteError || status >= 500 || pageErrors.length > 0 || redirectedToLogin;

      const idx = `[${String(i + 1).padStart(2, '0')}/${ROUTES.length}]`;

      if (hasIssues) {
        const issues = [];
        if (!hasContent) issues.push('WHITE_SCREEN');
        if (hasViteError) issues.push('VITE_ERROR');
        if (status >= 500) issues.push(`HTTP_${status}`);
        if (pageErrors.length > 0) issues.push(`PAGE_ERRORS(${pageErrors.length})`);
        if (redirectedToLogin) issues.push('REDIRECTED_TO_LOGIN');
        if (consoleErrors.length > 0) issues.push(`CONSOLE_ERRORS(${consoleErrors.length})`);

        console.log(`${idx} ❌ ${route} — ${issues.join(', ')}`);
        pageErrors.slice(0, 3).forEach(e => console.log(`      💥 ${e.substring(0, 200)}`));
        consoleErrors.slice(0, 2).forEach(e => console.log(`      ⚠️ ${e.substring(0, 200)}`));
        results.fail.push(route);
        results.errors[route] = {
          status,
          finalUrl,
          issues,
          pageErrors: pageErrors.slice(0, 5),
          consoleErrors: consoleErrors.slice(0, 5),
          hasContent,
          hasViteError,
          hasVueError,
          title
        };
      } else if (consoleErrors.length > 0) {
        // Page works but has console errors
        console.log(`${idx} ⚠️ ${route} — OK with ${consoleErrors.length} console warnings (${title})`);
        consoleErrors.slice(0, 2).forEach(e => console.log(`      ⚠️ ${e.substring(0, 150)}`));
        results.pass.push(route);
        results.errors[route] = {
          status,
          finalUrl,
          consoleErrors: consoleErrors.slice(0, 5),
          title,
          severity: 'warning'
        };
      } else {
        console.log(`${idx} ✅ ${route} — OK (${title})`);
        results.pass.push(route);
        results.errors[route] = { status, finalUrl, title };
      }
    } catch (e) {
      const idx = `[${String(i + 1).padStart(2, '0')}/${ROUTES.length}]`;
      console.log(`${idx} ❌ ${route} — TIMEOUT/CRASH: ${e.message.substring(0, 100)}`);
      results.fail.push(route);
      results.errors[route] = { error: e.message.substring(0, 200) };
    }

    page.removeListener('console', onConsoleMsg);
    page.removeListener('pageerror', onPageError);
  }

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`✅ Passed: ${results.pass.length}/${ROUTES.length}`);
  console.log(`❌ Failed: ${results.fail.length}/${ROUTES.length}`);

  if (results.fail.length > 0) {
    console.log('\n❌ Failed pages:');
    results.fail.forEach(r => {
      const info = results.errors[r];
      const detail = info.issues ? info.issues.join(', ') : (info.error || 'unknown');
      console.log(`  • ${r} — ${detail}`);
    });
  }

  // Pages with warnings
  const warnings = Object.entries(results.errors).filter(([_, v]) => v.severity === 'warning');
  if (warnings.length > 0) {
    console.log(`\n⚠️ Pages with console warnings: ${warnings.length}`);
    warnings.forEach(([route, info]) => {
      console.log(`  • ${route} — ${info.consoleErrors?.length || 0} warnings`);
    });
  }

  // Write JSON report
  const reportPath = '/opt/claude/mystocks_spec/scripts/dev/page_test_results.json';
  const fs = await import('fs');
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`\n📄 Detailed report: ${reportPath}`);

  await browser.close();
}

main().catch(e => {
  console.error('Fatal error:', e);
  process.exit(1);
});
