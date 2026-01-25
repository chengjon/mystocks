import { defineConfig, devices } from '@playwright/test';
import path from 'path';

const ARTDECO_TOKENS_PATH = path.resolve(__dirname, '../../src/styles/artdeco-tokens.scss');
const ECHARTS_THEME_PATH = path.resolve(__dirname, '../../src/utils/echarts.ts');

export default defineConfig({
  testDir: '../visual',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report', templatePath: undefined }],
    ['json', { outputFile: 'test-results/visual/test-results.json' }],
    ['junit', { outputFile: 'test-results/visual/junit.xml' }]
  ],
  use: {
    baseURL: 'http://localhost:5173',
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
  snapshotDir: '../visual/baselines',
  snapshotPathTemplate: '{snapshotDir}/{testFilePath}/{arg}{ext}',
  webServer: {
    command: 'npm run dev -- --port 5173',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000
  },
  timeout: 60000,
  globalTimeout: 900000
});
