import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  
  timeout: 30 * 1000,
  expect: {
    threshold: 0.001,
    timeout: 5000,
  },
  
  fullyParallel: true,
  
  retries: process.env.CI ? 2 : 0,
  
  workers: process.env.CI ? 2 : undefined,
  
  reporter: [
    ['html', {
      outputFolder: 'playwright-report',
      open: 'never',
    }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'junit-results.xml' }],
    ['list'],
  ],
  
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3020',
    
    trace: 'on-first-retry',
    
    screenshot: {
      mode: 'only-on-failure',
      fullPage: true,
    },
    
    video: {
      mode: 'retain-on-failure',
      size: { width: 1280, height: 720 },
    },
    
    viewport: { width: 1920, height: 1080 },
    
    ignoreHTTPSErrors: true,
    
    waitUntil: 'domcontentloaded',
    
    actionTimeout: 10000,
    
    navigationTimeout: 30000,
  },
  
  projects: [
    {
      name: 'chromium-desktop',
      use: { ...devices['Desktop Chrome'] },
    },
    
    {
      name: 'chrome-debug',
      use: { 
        ...devices['Desktop Chrome'],
        // 调试模式配置
        launchOptions: {
          headless: false,
          devtools: true,
          slowMo: 1000, // 慢速模式，便于观察
        },
      },
      testMatch: /.*chrome-devtools.*\.spec\.ts$/,
    },
  ],
});