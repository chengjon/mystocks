const { chromium } = require('playwright');
const path = require('path');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3020/dealing-room';

const viewports = [
  { name: '1920x1080', width: 1920, height: 1080 },
  { name: '1366x768', width: 1366, height: 768 },
  { name: '768x1024', width: 768, height: 1024 }
];

function approx(num) {
  if (typeof num !== 'number') return null;
  return Math.round(num * 100) / 100;
}

async function collectMetrics(page, viewportName) {
  return page.evaluate((vpName) => {
    const q = (s) => document.querySelector(s);
    const qa = (s) => Array.from(document.querySelectorAll(s));

    const sidebar = q('.artdeco-sidebar-v3');
    const topbar = q('.artdeco-topbar, .artdeco-header, .artdeco-dashboard-header');
    const mainContainer = q('.dashboard-container, .artdeco-main-content, .artdeco-dashboard-content, main');
    const cards = qa('.artdeco-card, .stat-card, .el-card, [class*="card"]');

    const sidebarRect = sidebar?.getBoundingClientRect() || null;
    const topbarRect = topbar?.getBoundingClientRect() || null;
    const mainRect = mainContainer?.getBoundingClientRect() || null;

    let firstTwoCardGap = null;
    if (cards.length >= 2) {
      const a = cards[0].getBoundingClientRect();
      const b = cards[1].getBoundingClientRect();
      if (Math.abs(a.top - b.top) < 5) {
        firstTwoCardGap = Math.max(0, b.left - a.right);
      } else {
        firstTwoCardGap = Math.max(0, b.top - a.bottom);
      }
    }

    const overlappingPairs = [];
    const textOverflowCandidates = qa('h1,h2,h3,h4,h5,p,span,button,a,td,th,div').slice(0, 1500);
    let overflowCount = 0;
    textOverflowCandidates.forEach((el) => {
      if (el.scrollWidth - el.clientWidth > 1 || el.scrollHeight - el.clientHeight > 1) {
        overflowCount += 1;
      }
    });

    const interactive = qa('button, a, [role="button"], input, select, textarea');
    const tinyTargets = interactive.filter((el) => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && (r.width < 32 || r.height < 32);
    }).length;

    const allRects = cards.slice(0, 50).map((el, idx) => ({ idx, r: el.getBoundingClientRect() }));
    for (let i = 0; i < allRects.length; i++) {
      for (let j = i + 1; j < allRects.length; j++) {
        const A = allRects[i].r;
        const B = allRects[j].r;
        const overlap = !(A.right <= B.left || A.left >= B.right || A.bottom <= B.top || A.top >= B.bottom);
        if (overlap) {
          overlappingPairs.push([allRects[i].idx, allRects[j].idx]);
          if (overlappingPairs.length >= 5) break;
        }
      }
      if (overlappingPairs.length >= 5) break;
    }

    const menuSections = qa('.artdeco-nav-section').length;
    const menuLinks = qa('.artdeco-sidebar-v3 a, .artdeco-sidebar-v3 [role="link"]').length;
    const charts = qa('canvas').length;
    const loadingMasksVisible = qa('.el-loading-mask').filter((el) => {
      const st = window.getComputedStyle(el);
      return st.display !== 'none' && st.visibility !== 'hidden' && Number(st.opacity || '1') > 0;
    }).length;

    return {
      viewport: vpName,
      url: location.href,
      title: document.title,
      sidebar: sidebarRect
        ? {
            exists: true,
            width: sidebarRect.width,
            height: sidebarRect.height,
            x: sidebarRect.x,
            y: sidebarRect.y
          }
        : { exists: false },
      topbar: topbarRect
        ? {
            exists: true,
            width: topbarRect.width,
            height: topbarRect.height,
            x: topbarRect.x,
            y: topbarRect.y
          }
        : { exists: false },
      main: mainRect
        ? {
            exists: true,
            width: mainRect.width,
            height: mainRect.height,
            x: mainRect.x,
            y: mainRect.y
          }
        : { exists: false },
      counts: {
        menuSections,
        menuLinks,
        cards: cards.length,
        charts,
        loadingMasksVisible
      },
      spacing: {
        firstTwoCardGap
      },
      visualHealth: {
        overflowCount,
        tinyTargets,
        overlappingPairs
      }
    };
  }, viewportName);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();

  const allResults = [];

  for (const vp of viewports) {
    const page = await context.newPage({ viewport: { width: vp.width, height: vp.height } });

    const consoleErrors = [];
    const requestFailed = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    page.on('requestfailed', (req) => {
      requestFailed.push({ url: req.url(), error: req.failure()?.errorText || 'unknown' });
    });

    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'mock-token-production-test');
      localStorage.setItem(
        'auth_user',
        JSON.stringify({
          id: 1,
          username: 'admin',
          email: 'admin@mystocks.com',
          role: 'admin',
          roles: ['admin'],
          permissions: ['*']
        })
      );
    });

    await page.route('**/api/**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: [], items: [], list: [], rows: [] })
      });
    });

    await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2500);

    const metrics = await collectMetrics(page, vp.name);

    const screenshotPath = path.join('/opt/claude/mystocks_spec/web/frontend', `dealing-room-${vp.name}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    allResults.push({
      viewport: vp,
      metrics,
      consoleErrors,
      requestFailed,
      screenshotPath
    });

    await page.close();
  }

  await browser.close();

  const normalized = allResults.map((r) => ({
    viewport: r.viewport,
    screenshotPath: r.screenshotPath,
    consoleErrors: r.consoleErrors,
    requestFailed: r.requestFailed,
    metrics: {
      ...r.metrics,
      sidebar: r.metrics.sidebar?.exists
        ? {
            ...r.metrics.sidebar,
            width: approx(r.metrics.sidebar.width),
            height: approx(r.metrics.sidebar.height),
            x: approx(r.metrics.sidebar.x),
            y: approx(r.metrics.sidebar.y)
          }
        : r.metrics.sidebar,
      topbar: r.metrics.topbar?.exists
        ? {
            ...r.metrics.topbar,
            width: approx(r.metrics.topbar.width),
            height: approx(r.metrics.topbar.height),
            x: approx(r.metrics.topbar.x),
            y: approx(r.metrics.topbar.y)
          }
        : r.metrics.topbar,
      main: r.metrics.main?.exists
        ? {
            ...r.metrics.main,
            width: approx(r.metrics.main.width),
            height: approx(r.metrics.main.height),
            x: approx(r.metrics.main.x),
            y: approx(r.metrics.main.y)
          }
        : r.metrics.main,
      spacing: {
        firstTwoCardGap: approx(r.metrics.spacing.firstTwoCardGap)
      }
    }
  }));

  console.log(JSON.stringify({ timestamp: new Date().toISOString(), results: normalized }, null, 2));
})();
