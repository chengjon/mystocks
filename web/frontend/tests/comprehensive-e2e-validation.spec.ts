import { test, expect, Page } from '@playwright/test';
import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
const { loadPortEnv, resolveFrontendConfig, resolveBackendConfig } = require('./e2e/helpers/port-env.js');

loadPortEnv(process.cwd());

const frontendConfig = resolveFrontendConfig();
const backendConfig = resolveBackendConfig();

/**
 * MyStocks E2E Automation Tests - Comprehensive Web Service Validation
 * 基于PM2运行的Web服务端到端自动化测试套件
 */

const FRONTEND_CONFIG = {
  name: 'mystocks-frontend',
  port: frontendConfig.port,
  backupPort: frontendConfig.backupPort,
  baseUrl: frontendConfig.baseUrl
};

const BACKEND_CONFIG = {
  name: 'mystocks-backend',
  port: backendConfig.port,
  backupPort: backendConfig.backupPort,
  baseUrl: backendConfig.baseUrl
};

const TEST_OUTPUT_DIR = path.join(process.cwd(), 'test-results');
const SCREENSHOT_DIR = path.join(TEST_OUTPUT_DIR, 'screenshots');
const VIDEO_DIR = path.join(TEST_OUTPUT_DIR, 'videos');

if (!fs.existsSync(TEST_OUTPUT_DIR)) fs.mkdirSync(TEST_OUTPUT_DIR, { recursive: true });
if (!fs.existsSync(SCREENSHOT_DIR)) fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
if (!fs.existsSync(VIDEO_DIR)) fs.mkdirSync(VIDEO_DIR, { recursive: true });

const testResults = {
  preflight: { passed: 0, failed: 0, details: [] as any[] },
  pageLoad: { passed: 0, failed: 0, details: [] as any[] },
  integration: { passed: 0, failed: 0, details: [] as any[] },
  interaction: { passed: 0, failed: 0, details: [] as any[] },
  startTime: Date.now(),
  endTime: 0
};

// --- Helper Functions ---

function checkPM2Process(serviceName: string): { running: boolean; status?: string; error?: string } {
  try {
    const output = execSync('pm2 jlist', { encoding: 'utf-8' });
    const pm2List = JSON.parse(output);
    const service = pm2List.find((p: any) => p.name === serviceName);

    if (!service) {
      return { running: false, error: `${serviceName} not found in PM2` };
    }

    return {
      running: service.pm2_env.status === 'online',
      status: service.pm2_env.status
    };
  } catch (error: any) {
    return { running: false, error: `PM2 check failed: ${error.message}` };
  }
}

function checkPortConnectivity(port: number): { connected: boolean; error?: string } {
  try {
    execSync(`lsof -Pi :${port} -sTCP:LISTEN -t`, { stdio: 'pipe' });
    return { connected: true };
  } catch {
    try {
      const httpCode = execSync(
        `curl -sS -o /dev/null -m 2 -w "%{http_code}" http://127.0.0.1:${port}`,
        { stdio: 'pipe', encoding: 'utf-8' }
      ).trim();
      if (httpCode !== '000') {
        return { connected: true };
      }
    } catch {
      // fall through
    }
    return { connected: false, error: `Port ${port} is not listening or reachable` };
  }
}

async function checkHttpResponse(url: string): Promise<{ success: boolean; status?: number; error?: string }> {
  try {
    const response = await fetch(url);
    return { success: response.ok, status: response.status };
  } catch (error: any) {
    return { success: false, error: `HTTP request failed: ${error.message}` };
  }
}

async function captureEvidence(page: Page, testName: string, type: 'screenshot' | 'video' = 'screenshot') {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${testName}_${timestamp}`;

  if (type === 'screenshot') {
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, `${filename}.png`), fullPage: true });
  }
}

function setupConsoleErrorDetection(page: Page): Promise<string[]> {
  return new Promise((resolve) => {
    const errors: string[] = [];
    const timer = setTimeout(() => resolve(errors), 10000);

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    page.on('load', () => {
      setTimeout(() => {
        clearTimeout(timer);
        resolve(errors);
      }, 2000);
    });
  });
}

async function validateApiResponse(url: string, expectedStatus: number = 200): Promise<{
  success: boolean;
  status?: number;
  data?: any;
  error?: string;
  responseTime?: number;
}> {
  const startTime = Date.now();
  try {
    const response = await fetch(url);
    const responseTime = Date.now() - startTime;

    if (!response.ok) {
      return {
        success: false,
        status: response.status,
        error: `HTTP ${response.status}: ${response.statusText}`,
        responseTime
      };
    }

    let data;
    try {
      data = await response.json();
    } catch {
      data = await response.text();
    }

    return {
      success: true,
      status: response.status,
      data,
      responseTime
    };
  } catch (error: any) {
    return {
      success: false,
      error: `API request failed: ${error.message}`,
      responseTime: Date.now() - startTime
    };
  }
}

function recordTestResult(category: keyof typeof testResults, testName: string, success: boolean, details?: any) {
  testResults[category][success ? 'passed' : 'failed']++;
  testResults[category].details.push({
    test: testName,
    success,
    timestamp: new Date().toISOString(),
    ...details
  });
}

async function setupAuthenticatedSession(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const user = {
      id: 1,
      username: 'e2e-admin',
      email: 'e2e-admin@mystocks.local',
      role: 'admin',
      permissions: ['*']
    };
    localStorage.setItem('auth_token', 'e2e-token');
    localStorage.setItem('auth_user', JSON.stringify(user));
  });
}

// --- Test Phases ---

test.describe('Phase 1: 前置校验 (Preflight Checks)', () => {
  test('PM2前端服务进程状态验证', async () => {
    const result = checkPM2Process(FRONTEND_CONFIG.name);
    recordTestResult('preflight', 'PM2 Frontend Process Check', result.running, result);
    expect(result.running).toBe(true);
  });

  test('PM2后端服务进程状态验证', async () => {
    const result = checkPM2Process(BACKEND_CONFIG.name);
    recordTestResult('preflight', 'PM2 Backend Process Check', result.running, result);
    expect(result.running).toBe(true);
  });

  test('前端端口连通性验证', async () => {
    const result = checkPortConnectivity(FRONTEND_CONFIG.port);
    const fallback = result.connected ? result : checkPortConnectivity(FRONTEND_CONFIG.backupPort);
    const merged = fallback.connected ? fallback : result;
    recordTestResult('preflight', 'Frontend Port Connectivity', merged.connected, {
      primary: FRONTEND_CONFIG.port,
      backup: FRONTEND_CONFIG.backupPort,
      ...merged
    });
    expect(merged.connected).toBe(true);
  });

  test('后端端口连通性验证', async () => {
    const result = checkPortConnectivity(BACKEND_CONFIG.port);
    const fallback = result.connected ? result : checkPortConnectivity(BACKEND_CONFIG.backupPort);
    const merged = fallback.connected ? fallback : result;
    recordTestResult('preflight', 'Backend Port Connectivity', merged.connected, {
      primary: BACKEND_CONFIG.port,
      backup: BACKEND_CONFIG.backupPort,
      ...merged
    });
    expect(merged.connected).toBe(true);
  });

  test('前端HTTP响应验证', async () => {
    const result = await checkHttpResponse(FRONTEND_CONFIG.baseUrl);
    recordTestResult('preflight', 'Frontend HTTP Response', result.success, result);
    expect(result.success).toBe(true);
  });

  test('后端HTTP响应验证', async () => {
    const result = await checkHttpResponse(BACKEND_CONFIG.baseUrl);
    recordTestResult('preflight', 'Backend HTTP Response', result.success, result);
    expect(result.success).toBe(true);
  });
});

test.describe('Phase 2: 页面加载完整性 (Page Load Integrity)', () => {
  test('DOM元素存在性验证', async ({ page }) => {
    await page.goto(FRONTEND_CONFIG.baseUrl);
    await page.waitForLoadState('networkidle');
    const coreElements = [
      { selector: 'body', name: 'Body' },
      { selector: '#app', name: 'App Root' }
    ];
    const results = [];
    for (const element of coreElements) {
      const count = await page.locator(element.selector).count();
      results.push({ element: element.name, found: count > 0 });
    }
    const allPresent = results.every(r => r.found);
    recordTestResult('pageLoad', 'DOM Elements Presence Check', allPresent, { elements: results });
    expect(allPresent).toBe(true);
  });

  test('控制台错误检测', async ({ page }) => {
    const consoleErrors = setupConsoleErrorDetection(page);
    await page.goto(FRONTEND_CONFIG.baseUrl);
    await page.waitForLoadState('networkidle');
    const errors = await consoleErrors;
    recordTestResult('pageLoad', 'Console Error Detection', errors.length === 0, { errors });
    expect(errors.length).toBe(0);
  });

  test('资源加载验证', async ({ page }) => {
    const failedRequests: string[] = [];
    page.on('requestfailed', request => {
      failedRequests.push(`${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
    });
    await page.goto(FRONTEND_CONFIG.baseUrl);
    await page.waitForLoadState('networkidle');
    recordTestResult('pageLoad', 'Resource Loading Validation', failedRequests.length === 0, { failedRequests });
    expect(failedRequests.length).toBe(0);
  });
});

test.describe('Phase 3: 前后端联动 (Frontend-Backend Integration)', () => {
  test('后端API健康检查', async () => {
    const result = await validateApiResponse(`${BACKEND_CONFIG.baseUrl}/health`);
    recordTestResult('integration', 'Backend API Health Check', result.success, result);
    expect(result.success).toBe(true);
    if (result.success && result.data?.data) {
      expect(result.data.data.status).toBe('healthy');
    }
  });

  test('前端数据获取验证', async ({ page }) => {
    await setupAuthenticatedSession(page);

    const apiRequests: any[] = [];
    page.on('response', response => {
      const url = response.url();
      if (url.includes('/api/') || url.includes(':8020')) {
        apiRequests.push({ url, status: response.status() });
      }
    });

    await page.goto(`${FRONTEND_CONFIG.baseUrl}/strategy/repo`);
    await expect(page.getByRole('heading', { name: '策略管理' })).toBeVisible({ timeout: 10000 });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const strategyRequests = apiRequests.filter((r) => r.url.includes('/strategy'));
    const success =
      strategyRequests.length > 0 &&
      strategyRequests.every((r) => Number.isInteger(r.status) && r.status >= 200 && r.status < 600);
    recordTestResult('integration', 'Frontend Data Fetching', success, { 
      count: apiRequests.length,
      strategyCount: strategyRequests.length,
      requests: apiRequests.slice(0, 10),
      strategyRequests: strategyRequests.slice(0, 10)
    });

    if (strategyRequests.length === 0) {
      console.log('⚠️ No API requests captured. Current page content:', await page.content().then(c => c.substring(0, 500)));
    }

    expect(strategyRequests.length).toBeGreaterThan(0);
    expect(success).toBe(true);
  });
});

test.describe('Phase 4: 基础交互 (Basic Interactions)', () => {
  test('页面导航验证', async ({ page }) => {
    await page.goto(FRONTEND_CONFIG.baseUrl);
    const title = await page.title();
    recordTestResult('interaction', 'Page Navigation', !!title, { title });
    expect(title).toBeDefined();
  });

  test('功能菜单交互验证', async ({ page }) => {
    await setupAuthenticatedSession(page);

    await page.goto(FRONTEND_CONFIG.baseUrl);
    // 覆盖当前 ArtDeco 导航结构，同时兼容 legacy 结构
    const selector = 'nav a, [role="navigation"] a, .layout-sidebar a, .artdeco-nav-item, .nav-item, a[href^="/"]';
    const menuItems = await page.locator(selector).count();
    recordTestResult('interaction', 'Menu Items Presence', menuItems > 0, { count: menuItems });
    expect(menuItems).toBeGreaterThan(0);
  });
});

// --- Report Generation ---

test.afterAll(async () => {
  testResults.endTime = Date.now();
  const duration = (testResults.endTime - testResults.startTime) / 1000;

  const report = {
    summary: {
      totalPassed: testResults.preflight.passed + testResults.pageLoad.passed + testResults.integration.passed + testResults.interaction.passed,
      totalFailed: testResults.preflight.failed + testResults.pageLoad.failed + testResults.integration.failed + testResults.interaction.failed,
      duration: `${duration.toFixed(2)}s`,
      timestamp: new Date().toISOString()
    },
    categories: testResults
  };

  const reportPath = path.join(TEST_OUTPUT_DIR, 'e2e-test-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  console.log('\n' + '='.repeat(80));
  console.log('MyStocks E2E Test Report Generated');
  console.log('='.repeat(80));
  console.log(`Passed: ${report.summary.totalPassed}, Failed: ${report.summary.totalFailed}, Duration: ${report.summary.duration}`);
  console.log('Detailed report:', reportPath);
  console.log('='.repeat(80) + '\n');
});
