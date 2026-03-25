import { defineConfig, devices } from '@playwright/test';
import path from 'path';

const ARTDECO_TOKENS_PATH = path.resolve(__dirname, '../../src/styles/artdeco-tokens.scss');
const ECHARTS_THEME_PATH = path.resolve(__dirname, '../../src/utils/echarts.ts');
const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const FRONTEND_URL = process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`;
const VISUAL_HTML_REPORT_DIR = process.env.VISUAL_HTML_REPORT_DIR || 'playwright-report';
const VISUAL_JSON_REPORT_FILE = process.env.VISUAL_JSON_REPORT_FILE || 'test-results/visual/test-results.json';
const VISUAL_JUNIT_REPORT_FILE = process.env.VISUAL_JUNIT_REPORT_FILE || 'test-results/visual/junit.xml';

export default defineConfig({
  testDir: '..',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: VISUAL_HTML_REPORT_DIR, templatePath: undefined }],
    ['json', { outputFile: VISUAL_JSON_REPORT_FILE }],
    ['junit', { outputFile: VISUAL_JUNIT_REPORT_FILE }]
  ],
  use: {
    baseURL: FRONTEND_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1920, height: 1080 },
    actionTimeout: 30000,
    navigationTimeout: 60000,
    launchOptions: {
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ],
  expect: {
    toHaveScreenshot: {
      maxDiffPixels: 100,
      threshold: 0.2,
      animations: 'disabled'
    }
  },
  snapshotDir: path.resolve(__dirname, '../baselines'),
  snapshotPathTemplate: '{snapshotDir}/{testFilePath}/{arg}{ext}',
  webServer: {
    command: `npm run dev -- --port ${FRONTEND_PORT}`,
    url: FRONTEND_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120000
  },
  timeout: 60000,
  globalTimeout: 900000
});
